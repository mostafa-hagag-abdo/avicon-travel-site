"""Answer-first blog sections (AEO): each listed H2 becomes a question with a 40–60 word direct answer right under it.

Data: blog_answers.json -> {url: {"sections": [{match, h2, answer, replace_first?}], "fixes": [[old, new]]}}
  match          current H2 text (plain); the new h2 text is also accepted, so re-runs work
  replace_first  the existing first <p> under the H2 already answered the question -> replaced, not kept
  answer         plain text; [text](/internal/url/) becomes a link (the article CSS styles it)
Also reads blog_links.json -> {url: [{after, text}]}: a <p class="avp-links"> with tour links goes at the end
of the (sub)section under the heading named in "after" (H2 or H3).
Re-runnable: an existing <p class="avp-answer"> after the H2 is replaced, and old avp-links are removed first. When a page changes, its modified
date is refreshed (visible "Updated …", og:updated_time, article:modified_time, JSON-LD dateModified, sitemap lastmod).
"""
import html, json, re, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads(Path(__file__).with_name("blog_answers.json").read_text(encoding="utf-8"))
TODAY = date.today()
REDIRECT = "<?php header('Location:"


def plain(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def check_link(url):
    page = ROOT / url.strip("/") / "index.php"
    if not url.startswith("/") or not url.endswith("/") or not page.is_file() \
            or page.read_text(encoding="utf-8", errors="ignore").startswith(REDIRECT):
        raise ValueError(f"broken internal link: {url}")


def inline(text):
    out = html.escape(text, quote=False)

    def link(m):
        check_link(m.group(2))
        return f'<a href="{m.group(2)}">{m.group(1)}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, out)


def words(text):
    return len(re.findall(r"[A-Za-z][A-Za-z'’-]*", re.sub(r"\]\([^)]+\)", "]", text)))


sitemap = ROOT / "sitemap.xml"
sm = sitemap.read_bytes().decode("utf-8")
iso = f"{TODAY.isoformat()}T12:00:00+00:00"
LINKS_FILE = Path(__file__).with_name("blog_links.json")
LINKS = json.loads(LINKS_FILE.read_text(encoding="utf-8")) if LINKS_FILE.is_file() else {}
HEAD = re.compile(r"<h([23])[^>]*>(.*?)</h\1>", re.S)

for url in list(DATA) + [u for u in LINKS if u not in DATA]:
    rec = DATA.get(url, {"sections": []})
    path = ROOT / url.strip("/") / "index.php"
    s = path.read_bytes().decode("utf-8")
    before = s
    for old, new in rec.get("fixes", []):
        if s.count(old) == 1:
            s = s.replace(old, new)
        elif new not in s:
            sys.exit(f"fix not found in {url}: {old[:70]}")
    for sec in rec["sections"]:
        n = words(sec["answer"])
        if not 40 <= n <= 60:
            sys.exit(f"{url} '{sec['h2']}': answer has {n} words (want 40-60)")
        hits = [m for m in re.finditer(r"<h2([^>]*)>(.*?)</h2>", s, re.S) if plain(m.group(2)) in (sec["match"], sec["h2"])]
        if len(hits) != 1:
            sys.exit(f"{url}: {len(hits)} H2 matches for '{sec['match']}'")
        m = hits[0]
        after = s[m.end():]
        old_cap = re.match(r'\s*<p class="avp-answer">.*?</p>', after, re.S)
        if old_cap:
            after = after[old_cap.end():]
        elif sec.get("replace_first"):
            first = re.match(r"\s*<p>.*?</p>", after, re.S)
            if not first:
                sys.exit(f"{url}: no paragraph to replace under '{sec['match']}'")
            after = after[first.end():]
        s = (s[:m.start()] + f"<h2{m.group(1)}>{html.escape(sec['h2'], quote=False)}</h2>\n\n\n\n"
             + f'<p class="avp-answer">{inline(sec["answer"])}</p>' + after)
    # Product links (blog_links.json): a <p class="avp-links"> at the end of the (sub)section under "after",
    # i.e. just before the next H2/H3. Old ones are removed first, so edits and re-runs stay clean.
    s = re.sub(r'<p class="avp-links">.*?</p>\s*', "", s, flags=re.S)
    for ln in LINKS.get(url, []):
        hits = [m for m in HEAD.finditer(s) if plain(m.group(2)) == ln["after"]]
        if len(hits) != 1:
            sys.exit(f"{url}: {len(hits)} headings match '{ln['after']}'")
        nxt = re.compile(r"<h[23][\s>]").search(s, hits[0].end())
        pos = nxt.start() if nxt else s.index("</article>", hits[0].end())
        s = s[:pos] + f'<p class="avp-links">{inline(ln["text"])}</p>\n\n\n\n' + s[pos:]
    if s != before:
        s = re.sub(r'(<i class="fas fa-rotate"></i> Updated )[^<]+', lambda m: m.group(1) + f"{TODAY.day} {TODAY:%B %Y}", s)
        s = re.sub(r'(<meta property="(?:og:updated_time|article:modified_time)" content=")[^"]+', lambda m: m.group(1) + iso, s)
        s = re.sub(r'("dateModified"\s*:\s*")[^"]+', lambda m: m.group(1) + iso, s)
        sm = re.sub(rf"(<loc>https://avicontravel\.com{re.escape(url)}</loc><lastmod>)[^<]+", lambda m: m.group(1) + TODAY.isoformat(), sm)
        path.write_bytes(s.encode("utf-8"))
    print(f"{len(rec['sections']):2} answers  {len(LINKS.get(url, [])):2} link paragraphs  {url}{'' if s != before else '  (no change)'}")
sitemap.write_bytes(sm.encode("utf-8"))
