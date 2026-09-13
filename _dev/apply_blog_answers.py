"""Answer-first blog sections (AEO): each listed H2 becomes a question with a 40–60 word direct answer right under it.

Data: blog_answers.json -> {url: {"sections": [{match, h2, answer, replace_first?}], "fixes": [[old, new]]}}
  match          current H2 text (plain); the new h2 text is also accepted, so re-runs work
  replace_first  the existing first <p> under the H2 already answered the question -> replaced, not kept
  answer         plain text; [text](/internal/url/) becomes a link (the article CSS styles it)
Re-runnable: an existing <p class="avp-answer"> after the H2 is replaced. When a page changes, its modified
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
for url, rec in DATA.items():
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
    if s != before:
        s = re.sub(r'(<i class="fas fa-rotate"></i> Updated )[^<]+', lambda m: m.group(1) + f"{TODAY.day} {TODAY:%B %Y}", s)
        s = re.sub(r'(<meta property="(?:og:updated_time|article:modified_time)" content=")[^"]+', lambda m: m.group(1) + iso, s)
        s = re.sub(r'("dateModified"\s*:\s*")[^"]+', lambda m: m.group(1) + iso, s)
        sm = re.sub(rf"(<loc>https://avicontravel\.com{re.escape(url)}</loc><lastmod>)[^<]+", lambda m: m.group(1) + TODAY.isoformat(), sm)
        path.write_bytes(s.encode("utf-8"))
    print(f"{len(rec['sections']):2} answers  {url}{'' if s != before else '  (no change)'}")
sitemap.write_bytes(sm.encode("utf-8"))
