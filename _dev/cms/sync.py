"""Control panel sync between Supabase (table public.products) and the website's trip pages.

    python _dev/cms/sync.py export [--out FILE]              site -> product records (JSON, no network)
    python _dev/cms/sync.py import                           site -> Supabase: first seed + edits pushed to the repo
    python _dev/cms/sync.py publish --job ID --state FILE    Supabase -> site files (run by publish-content.yml)
    python _dev/cms/sync.py publish --source RECORDS.json    same from a local file (tests; no network)
    python _dev/cms/sync.py save --job ID --state FILE [--commit SHA]   after the push: store what is live now
    python _dev/cms/sync.py finish --job ID --result success|failure|skipped

Network modes read SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY from the environment.

A record is one row of public.products: {slug, section, status, template, sort_order, data, live_data, live_status}.
    data = {"blocks": {...see blocks.py}, "seo": {"title", "description"}, "card": {...see CARD_KEYS}}
`data` is the team's copy, `live_data` what the site had after the last publish/import. Merge rule for every field
(one block, one SEO string, one card field): a change made in the dashboard wins; otherwise a change made in the repo
(e.g. by the daily SEO work) is kept and copied back to the dashboard.

On publish, one trip's change reaches every place that shows it: the trip page (blocks + booking box + lightbox +
og:image), the hub card, the home card, "related" cards on other trips, llms.txt, the search index, sitemap.xml and
_dev/product_meta.json; then product_meta.py and schema_products.py refresh titles and JSON-LD, and health_check.py
must pass. A hidden trip becomes a 301 to its hub (the page is kept in _dev/cms/hidden/ to bring it back).
"""
import copy
import datetime as _dt
import hashlib
import html as _html
import io
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blocks  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DOMAIN = "https://avicontravel.com"
SECTIONS = ("tours", "nile-cruises", "packages")
HOME = "index.php"
STUB = "<?php header('Location:"
HIDDEN = "_dev/cms/hidden"
UPLOADS = "assets/uploads/cms"
META = "_dev/product_meta.json"
CARD_KEYS = ("name", "location", "summary", "duration", "style", "badge", "image", "home")
UNITS = [("blocks", k) for k in blocks.BLOCKS] + [("seo", "title"), ("seo", "description")] + [("card", k) for k in CARD_KEYS]


# ----------------------------------------------------------------------------------------------- files


class Files:
    """Lazy read / write-at-the-end cache, keeping each file's bytes and line endings."""

    def __init__(self, root=ROOT):
        self.root, self.text, self.dirty, self.removed = Path(root), {}, set(), set()

    def exists(self, rel):
        return rel in self.text or (self.root / rel).exists()

    def get(self, rel):
        if rel not in self.text:
            self.text[rel] = (self.root / rel).read_bytes().decode("utf-8")
        return self.text[rel]

    def set(self, rel, s):
        if self.exists(rel) and self.get(rel) == s:
            return
        self.text[rel] = s
        self.dirty.add(rel)

    def remove(self, rel):
        self.removed.add(rel)
        self.dirty.discard(rel)

    def flush(self):
        for rel in sorted(self.dirty):
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(self.text[rel].encode("utf-8"))
        for rel in sorted(self.removed):
            (self.root / rel).unlink(missing_ok=True)
        return sorted(self.dirty | self.removed)


def page_rel(slug):
    return f"{slug}/index.php"


def product_pages(files):
    """slug -> True for every product page that is a real page (not a redirect stub)."""
    out = []
    for sec in SECTIONS:
        for p in sorted((files.root / sec).glob("*/index.php")):
            slug = f"{sec}/{p.parent.name}"
            if not files.get(page_rel(slug)).startswith(STUB):
                out.append(slug)
    return out


# ----------------------------------------------------------------------------------------------- small helpers


def get(d, unit):
    return ((d or {}).get(unit[0]) or {}).get(unit[1])


def put(d, unit, value):
    d.setdefault(unit[0], {})[unit[1]] = copy.deepcopy(value)


def amount(price):
    """Starting price as an int, or None when the page says 'On Request'."""
    if not price or not re.search(r"\d", price.get("amount") or ""):
        return None
    return int(re.sub(r"[^\d]", "", price["amount"]))


def esc_attr(s):
    return (s or "").replace('"', "&quot;")


def set_attr(tag, name, value):
    """Set one attribute on an opening tag, keeping everything else."""
    if value in (None, ""):
        return re.sub(rf'\s{name}="[^"]*"', "", tag)
    if re.search(rf'\s{name}="', tag):
        return re.sub(rf'(\s{name}=")[^"]*(")', lambda m: m.group(1) + esc_attr(value) + m.group(2), tag, count=1)
    return re.sub(r"^<(\w+)", lambda m: f'<{m.group(1)} {name}="{esc_attr(value)}"', tag, count=1)


def set_img(tag, image):
    for a in ("width", "height", "src", "alt"):
        tag = set_attr(tag, a, (image or {}).get(a))
    return tag


def sub_group(frag, rx, value):
    """Replace group 2 of a 3-group regex (first match)."""
    return re.sub(rx, lambda m: m.group(1) + value + m.group(3), frag, count=1, flags=re.S)


def grab(rx, s, default=None):
    m = re.search(rx, s, re.S)
    return m.group(1).strip() if m else default


def cut_line_span(s, a, b):
    """Extend (a, b) to whole lines when the element sits on its own lines, and swallow one blank line."""
    ls = s.rfind("\n", 0, a) + 1
    if s[ls:a].strip() == "":
        a = ls
    le = s.find("\n", b)
    if le != -1 and s[b:le].strip() == "":
        b = le + 1
        nxt = s.find("\n", b)
        if nxt != -1 and s[b:nxt].strip() == "" and s[max(0, a - 2):a].strip() == "":
            b = nxt + 1
    return a, b


# ----------------------------------------------------------------------------------------------- cards (hub + home)

CARD_RX = {
    "badge": r'(<span class="badge[^"]*">)(.*?)(</span>)',
    "location": r'(<span class="(?:location|locations|route)">(?:<i [^>]*></i>\s*)?)(.*?)(</span>)',
    "name": r"(<h3>)(.*?)(</h3>)",
    "summary": r'(<div class="card-body"><h3>.*?</h3><p>)(.*?)(</p>)',
    "duration": r'(<div class="meta-row"><div class="meta"><span>[^<]*</span><strong>)(.*?)(</strong>)',
    "style": r'(<div class="meta-row"><div class="meta">.*?</div><div class="meta"><span>[^<]*</span><strong>)(.*?)(</strong>)',
    "price": r'(<div class="price">(?:<del>.*?</del>)?)(.*?)(</div>)',
}


def card_span(s, slug):
    m = re.search(rf'<a class="(?:tour-card|package-card)" href="/{re.escape(slug)}/">', s)
    return (m.start(), blocks.end_of(s, m.start(), "a")) if m else None


CARD_HREF = r'<a class="(?:tour-card|package-card)" href="/([^"]+)/">'


def card_fields(frag):
    card = {}
    for k in ("name", "location", "summary", "duration", "style", "badge"):
        m = re.search(CARD_RX[k], frag, re.S)
        card[k] = m.group(2).strip() if m else ""
    img = blocks.IMG_RE.search(frag)
    card["image"] = blocks.img_attrs(img.group(0)) if img else None
    return card


def read_card(s, slug):
    span = card_span(s, slug)
    return card_fields(s[span[0]:span[1]]) if span else None


def card_snapshot(s, slug):
    """The card's markup and its neighbours in the same grid, so a hidden trip can come back to the same place."""
    span = card_span(s, slug)
    if not span:
        return None
    found = [(m.group(1), m.start(), blocks.end_of(s, m.start(), "a")) for m in re.finditer(CARD_HREF, s)]
    i = [f[0] for f in found].index(slug)
    after = found[i - 1] if i and "</div>" not in s[found[i - 1][2]:span[0]] else None
    before = found[i + 1] if i + 1 < len(found) and "</div>" not in s[span[1]:found[i + 1][1]] else None
    return {"html": s[span[0]:span[1]], "after": after and after[0], "before": before and before[0]}


def card_price(n, existing):
    if n is None:
        return "On Request"
    return f"${n}/person" if "/person" in (existing or "") else f"${n:,}.00"


def write_card(frag, card, fields, n=None, price=False):
    for k in fields:
        if k == "image":
            m = blocks.IMG_RE.search(frag)
            if m and card.get("image"):
                frag = frag[:m.start()] + set_img(m.group(0), card["image"]) + frag[m.end():]
        elif k in CARD_RX and k != "price" and card.get(k) is not None:
            frag = sub_group(frag, CARD_RX[k], card[k])
    if price:
        old = grab(r'<div class="price">(?:<del>.*?</del>)?(.*?)</div>', frag, "")
        frag = sub_group(frag, CARD_RX["price"], card_price(n, old))
    return frag


def remove_span(files, rel, span):
    s = files.get(rel)
    a, b = cut_line_span(s, *span)
    files.set(rel, s[:a] + s[b:])


def insert_card(files, rel, slug, card, n, after_slugs, snapshot=None, old_card=None):
    """Put the trip's card back where it was (snapshot; only fields that differ from old_card are rewritten),
    or clone a neighbour card (template first) and insert it after it."""
    s = files.get(rel)
    if card_span(s, slug):
        return
    anchor, before = None, False
    if snapshot:
        if snapshot.get("after"):
            anchor = card_span(s, snapshot["after"])
        if not anchor and snapshot.get("before"):
            anchor, before = card_span(s, snapshot["before"]), True
    if not anchor:
        before = False
        anchor = next((card_span(s, o) for o in after_slugs if o and card_span(s, o)), None)
    if not anchor:
        m = list(re.finditer(CARD_HREF, s))
        if not m:
            raise ValueError(f"{rel}: no card to copy for {slug}")
        anchor = (m[-1].start(), blocks.end_of(s, m[-1].start(), "a"))
    if snapshot:
        frag = snapshot["html"]
        old = old_card or card_fields(frag)
        frag = write_card(frag, card, [k for k in CARD_KEYS if k != "home" and card.get(k) != old.get(k)], n, price=True)
    else:
        frag = re.sub(r'href="/[^"]+/"', f'href="/{slug}/"', s[anchor[0]:anchor[1]], count=1)
        frag = write_card(re.sub(r"<del>.*?</del>", "", frag), card, [k for k in CARD_KEYS if k != "home"], n, price=True)
    line_start = s.rfind("\n", 0, anchor[0]) + 1
    indent, nl = s[line_start:anchor[0]], blocks.nl_of(s)
    gap = nl + nl if s[anchor[1]:anchor[1] + 2 * len(nl)] == nl + nl else nl
    if before:
        files.set(rel, s[:anchor[0]] + frag + gap + indent + s[anchor[0]:])
    else:
        files.set(rel, s[:anchor[1]] + gap + indent + frag + s[anchor[1]:])


# ----------------------------------------------------------------------------------------------- related cards

REL_RX = {
    "duration": r'(<span class="related-duration">)(.*?)(</span>)',
    "location": r'(<span class="related-cities">(?:<i [^>]*></i>\s*)?)(.*?)(</span>)',
    "name": r'(<div class="related-title">)(.*?)(</div>)',
    "price": r'(<div class="related-price">)(.*?)(</div>)',
}


def related_spans(s, slug):
    out = []
    for m in re.finditer(rf"<div class=\"related-card\" onclick=\"window.location.href='/{re.escape(slug)}/'\">", s):
        out.append((m.start(), blocks.end_of(s, m.start())))
    return out


def update_related(files, pages, slug, card, fields, n, price):
    for other in pages:
        rel = page_rel(other)
        s = files.get(rel)
        for a, b in reversed(related_spans(s, slug)):
            frag = s[a:b]
            for k in fields:
                if k == "image" and card.get("image"):
                    m = blocks.IMG_RE.search(frag)
                    frag = frag[:m.start()] + set_img(m.group(0), card["image"]) + frag[m.end():] if m else frag
                elif k in REL_RX and k != "price":
                    frag = sub_group(frag, REL_RX[k], card[k])
            if price:
                frag = sub_group(frag, REL_RX["price"], "On Request" if n is None else f"${n:,}<small>/person</small>")
            s = s[:a] + frag + s[b:]
        files.set(rel, s)


def remove_related(files, pages, slug):
    for other in pages:
        rel = page_rel(other)
        for span in reversed(related_spans(files.get(rel), slug)):
            remove_span(files, rel, span)


# ----------------------------------------------------------------------------------------------- llms.txt, search, sitemap, meta


def llms_rx(slug):
    return re.compile(rf"^- \[(.*?)\]\({re.escape(DOMAIN)}/{re.escape(slug)}/\): (.*?) · (from \$[\d,]+ per person|price on request)\. (.*?)(\r?)$", re.M)


def llms_line(slug, card, n):
    price = f"from ${n:,} per person" if n is not None else "price on request"
    return f"- [{_html.unescape(card['name'])}]({DOMAIN}/{slug}/): {_html.unescape(card['duration'])} · {price}. {_html.unescape(card['summary'])}"


LLMS_ITEM = re.compile(rf"^- \[.*?\]\({re.escape(DOMAIN)}/([^)]+)/\): ", re.M)


def previous_in(order, slug):
    return order[order.index(slug) - 1] if slug in order and order.index(slug) else None


def update_llms(files, slug, card, n, remove=False, after=None, line=None):
    rel = "llms.txt"
    if not files.exists(rel):
        return
    s = files.get(rel)
    m = llms_rx(slug).search(s)
    if remove:
        if m:
            end = s.find("\n", m.end())
            files.set(rel, s[:m.start()] + s[end + 1 if end != -1 else m.end():])
        return
    line = line or llms_line(slug, card, n)
    if m:
        files.set(rel, s[:m.start()] + line + m.group(5) + s[m.end():])
        return
    for other in after or []:
        mo = llms_rx(other).search(s) if other else None
        if mo:
            files.set(rel, s[:mo.end()] + blocks.nl_of(s) + line + s[mo.end():])
            return


def hide_snapshot(files, slug, sec, card, n, seo):
    """Everything needed to bring a hidden trip back exactly where it was."""
    snap = {"card": card, "price": n, "seo": seo, "cards": {}}
    for surface in (f"{sec}/index.php", HOME):
        snap["cards"][surface] = card_snapshot(files.get(surface), slug)
    if files.exists("llms.txt"):
        s = files.get("llms.txt")
        m = llms_rx(slug).search(s)
        snap["llms"] = {"line": m.group(0).rstrip("\r") if m else None,
                        "after": previous_in(LLMS_ITEM.findall(s), slug)}
    _, _, entries = search_entries(files)
    urls = [e["u"] for e in entries]
    snap["search"] = {"entry": next((e for e in entries if e["u"] == f"/{slug}/"), None),
                      "after": (previous_in(urls, f"/{slug}/") or "").strip("/") or None}
    locs = re.findall(rf"<loc>{re.escape(DOMAIN)}/(.*?)/?</loc>", files.get("sitemap.xml"))
    snap["sitemap"] = {"after": previous_in(locs, slug)}
    return snap


def search_entries(files):
    s = files.get("search/index.php")
    m = re.search(r"var INDEX = (\[.*?\]);", s, re.S)
    return s, m, json.loads(m.group(1))


def update_search(files, slug, name=None, description=None, remove=False, after=None, entry=None):
    if not files.exists("search/index.php"):
        return
    s, m, entries = search_entries(files)
    url = f"/{slug}/"
    found = [e for e in entries if e["u"] == url]
    if remove:
        entries = [e for e in entries if e["u"] != url]
    elif found:
        for e in found:
            if name is not None:
                e["t"] = _html.unescape(name)
            if description is not None:
                e["d"] = description
    else:
        entry = dict(entry) if entry else {"t": "", "u": url, "d": "", "k": "Tour"}
        if name is not None:
            entry["t"] = _html.unescape(name)
        if description is not None:
            entry["d"] = description
        pos = next((i + 1 for other in (after or []) for i, e in enumerate(entries) if other and e["u"] == f"/{other}/"), len(entries))
        entries.insert(pos, entry)
    files.set("search/index.php", s[:m.start(1)] + json.dumps(entries, ensure_ascii=False) + s[m.end(1):])


def update_sitemap(files, slug, today, remove=False, after=None):
    rel = "sitemap.xml"
    s = files.get(rel)
    rx = re.compile(rf"^([ \t]*)<url><loc>{re.escape(DOMAIN)}/{re.escape(slug)}/</loc><lastmod>[^<]*</lastmod>(.*?)</url>(\r?\n)", re.M)
    m = rx.search(s)
    if remove:
        if m:
            files.set(rel, s[:m.start()] + s[m.end():])
        return
    if m:
        files.set(rel, s[:m.start()] + f"{m.group(1)}<url><loc>{DOMAIN}/{slug}/</loc><lastmod>{today}</lastmod>{m.group(2)}</url>{m.group(3)}" + s[m.end():])
        return
    for other in after or []:
        mo = re.search(rf"^([ \t]*)<url><loc>{re.escape(DOMAIN)}/{re.escape(other)}/</loc>.*?</url>(\r?\n)", s, re.M) if other else None
        if mo:
            line = f"{mo.group(1)}<url><loc>{DOMAIN}/{slug}/</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>{mo.group(2)}"
            files.set(rel, s[:mo.end()] + line + s[mo.end():])
            return
    nl = blocks.nl_of(s)
    files.set(rel, s.replace("</urlset>", f"  <url><loc>{DOMAIN}/{slug}/</loc><lastmod>{today}</lastmod><priority>0.8</priority></url>{nl}</urlset>", 1))


def load_meta(files):
    return json.loads(files.get(META))


def save_meta(files, meta):
    files.set(META, json.dumps(meta, indent=1, ensure_ascii=False) + "\n")


def final_seo(text, n):
    return (text or "").replace("{price}", f"${n:,}" if n is not None else "")


# ----------------------------------------------------------------------------------------------- read the site


def site_record(files, slug, meta=None):
    s = files.get(page_rel(slug))
    b = blocks.extract(s)
    tour_package, crumb = b.pop("tour_package"), b.pop("crumb")
    hub, home = files.get(f"{slug.split('/')[0]}/index.php"), files.get(HOME)
    card = read_card(hub, slug) or read_card(home, slug)
    if not card:
        chips = b.get("chips") or []
        card = {"name": tour_package or b.get("title") or "", "location": "", "summary": "",
                "duration": chips[0]["text"] if chips else "", "style": "", "badge": (b.get("badge") or {}).get("text", ""),
                "image": (b.get("gallery") or [None])[0] or b.get("hero_image")}
    card["home"] = card_span(home, slug) is not None
    meta = load_meta(files) if meta is None else meta
    seo = meta.get(f"/{slug}/") or {"title": _html.unescape(grab(r"<title>(.*?)</title>", s, "")),
                                     "description": _html.unescape(grab(r'<meta name="description" content="([^"]*)"', s, ""))}
    return {"blocks": b, "seo": {"title": seo["title"], "description": seo["description"]}, "card": card}


def export_site(files):
    meta = load_meta(files)
    return {slug: site_record(files, slug, meta) for slug in product_pages(files)}


# ----------------------------------------------------------------------------------------------- merge


def merge(draft, live, page):
    """Dashboard changes win; repo changes to fields the dashboard did not touch are kept."""
    out, conflicts = copy.deepcopy(draft), []
    if page is None or live is None:
        return out, conflicts
    for u in UNITS:
        d, l, p = get(draft, u), get(live, u), get(page, u)
        if d == l and p != l:
            put(out, u, p)
        elif d != l and p != l and p != d:
            conflicts.append(".".join(u))
    return out, conflicts


def derive(data):
    """Fields that repeat other fields: the Quick-facts 'Price' card follows the booking-box price."""
    b = data["blocks"]
    n = amount(b.get("price"))
    extra = (b.get("facts") or {}).get("extra")
    if extra is not None and "Price" in extra:
        extra["Price"] = f"From ${n:,} / person" if n is not None else "On request"
    return data


# ----------------------------------------------------------------------------------------------- images


STORAGE_RX = re.compile(r"https://[a-z0-9]+\.supabase\.co/storage/v1/object/public/site-images/([^\"'\s<>()]+)")


def to_webp(raw, max_width=1600):
    from PIL import Image, ImageOps
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(raw)))
    im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
    if im.width > max_width:
        im = im.resize((max_width, round(im.height * max_width / im.width)), Image.LANCZOS)
    out = io.BytesIO()
    im.save(out, "WEBP", quality=82, method=6)
    return out.getvalue(), im.width, im.height


def localize_images(data, root=ROOT, fetch=None):
    """Copy dashboard uploads (Supabase Storage URLs) into assets/uploads/cms/ as WebP and point the data at them."""
    text = json.dumps(data, ensure_ascii=False)
    found = {m.group(0): m.group(1) for m in STORAGE_RX.finditer(text)}
    if not found:
        return data, []
    fetch = fetch or (lambda url: urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "avicon-cms"}), timeout=60).read())
    sizes, written = {}, []
    for url, path in found.items():
        stem = re.sub(r"[^a-z0-9]+", "-", Path(path).stem.lower()).strip("-")[:60] or "image"
        rel = f"{UPLOADS}/{stem}-{hashlib.sha1(path.encode()).hexdigest()[:8]}.webp"
        dest = Path(root) / rel
        if not dest.exists():
            raw, w, h = to_webp(fetch(url))
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)
            written.append(rel)
        else:
            from PIL import Image
            with Image.open(dest) as im:
                w, h = im.size
        sizes["/" + rel] = (w, h)
        text = text.replace(url, "/" + rel)
    data = json.loads(text)

    def fix(node):
        if isinstance(node, dict):
            if node.get("src") in sizes:
                node["width"], node["height"] = (str(x) for x in sizes[node["src"]])
            for v in node.values():
                fix(v)
        elif isinstance(node, list):
            for v in node:
                fix(v)
    fix(data)
    return data, written


# ----------------------------------------------------------------------------------------------- page extras


def update_page_extras(s, new_blocks, old_blocks, force=False):
    """Lightbox image/count and og:image follow the first gallery (or hero) photo."""
    gal, old_gal = new_blocks.get("gallery"), old_blocks.get("gallery") if old_blocks else None
    main = (gal or [None])[0] or new_blocks.get("hero_image")
    old_main = (old_gal or [None])[0] or (old_blocks or {}).get("hero_image")
    if gal and (force or gal != old_gal):
        lb = blocks.element(s, r'<div class="bk-lb" id="bkLb">')
        if lb:
            frag = s[lb[0]:lb[1]]
            m = blocks.IMG_RE.search(frag)
            if m:
                frag = frag[:m.start()] + set_img(m.group(0), gal[0]) + frag[m.end():]
            frag = re.sub(r'(<div class="bk-lb-count">)\d+ / \d+(</div>)', rf"\g<1>1 / {len(gal)}\g<2>", frag)
            s = s[:lb[0]] + frag + s[lb[1]:]
    if main and main.get("src") and (force or (old_main or {}).get("src") != main["src"]):
        url = main["src"] if main["src"].startswith("http") else DOMAIN + main["src"]
        for rx in (r'(<meta property="og:image" content=")[^"]*(")', r'(<meta property="og:image:secure_url" content=")[^"]*(")',
                   r'(<meta name="twitter:image" content=")[^"]*(")'):
            s = re.sub(rx, lambda m: m.group(1) + url + m.group(2), s, count=1)
        for a in ("width", "height"):
            if main.get(a):
                s = re.sub(rf'(<meta property="og:image:{a}" content=")[^"]*(")', lambda m: m.group(1) + main[a] + m.group(2), s, count=1)
    return s


def write_page(files, slug, data, old):
    """Write blocks into the trip page; `old` is the page's current record (None for a new page)."""
    rel = page_rel(slug)
    s = files.get(rel)
    flat = dict(data["blocks"])
    old_card = (old or {}).get("card") or {}
    if data["card"]["name"] and (old is None or data["card"]["name"] != old_card.get("name")):
        flat["tour_package"] = flat["crumb"] = data["card"]["name"]
    s = blocks.apply(s, flat)
    s = update_page_extras(s, data["blocks"], (old or {}).get("blocks"), force=old is None)
    files.set(rel, s)


# ----------------------------------------------------------------------------------------------- publish


def neighbours(rec):
    return [rec.get("template")] if rec.get("template") else []


def publish_records(records, files, today=None, fetch=None):
    """Apply every record to the site files. Returns (updates for the database, summary)."""
    today = today or _dt.date.today().isoformat()
    pages = product_pages(files)
    site = {slug: site_record(files, slug) for slug in pages}
    meta = load_meta(files)
    meta_before = copy.deepcopy(meta)
    updates, changed, notes = [], [], []

    for rec in sorted(records, key=lambda r: (r.get("sort_order") or 0, r["slug"])):
        slug, sec = rec["slug"], rec["section"]
        rel = page_rel(slug)
        page = site.get(slug)
        have = "published" if page else ("hidden" if files.exists(rel) else None)
        want = rec.get("status") or "hidden"
        draft, uploaded = localize_images(rec["data"], files.root, fetch)
        merged, conflicts = merge(draft, rec.get("live_data"), page)
        merged = derive(merged)
        if conflicts:
            notes.append(f"{slug}: kept the dashboard version of {', '.join(conflicts)} (the site had other edits)")
        touched = False

        if want == "published":
            n = amount(merged["blocks"].get("price"))
            card, hub, url = merged["card"], f"{sec}/index.php", f"/{slug}/"
            if have != "published":
                # new trip, or a hidden trip coming back
                kept, snap = f"{HIDDEN}/{slug}.php", {}
                same_section = [p for p in pages if p.startswith(sec + "/") and p != slug][::-1]
                if files.exists(kept):
                    files.set(rel, files.get(kept))
                    files.remove(kept)
                    if files.exists(f"{HIDDEN}/{slug}.json"):
                        snap = json.loads(files.get(f"{HIDDEN}/{slug}.json"))
                        files.remove(f"{HIDDEN}/{slug}.json")
                    base = site_record_from_text(files, slug)
                    if base and snap.get("card"):
                        base["card"] = {**snap["card"], "home": bool((snap.get("cards") or {}).get(HOME))}
                else:
                    tpl = rec.get("template")
                    if not tpl or tpl not in site:
                        raise ValueError(f"{slug}: choose an existing trip to copy the page layout from")
                    files.set(rel, files.get(page_rel(tpl)).replace(f"/{tpl}/", f"/{slug}/"))
                    base = None
                write_page(files, slug, merged, base)
                cards = snap.get("cards") or {}
                insert_card(files, hub, slug, card, n, neighbours(rec) + same_section, cards.get(hub), snap.get("card"))
                if card.get("home"):
                    insert_card(files, HOME, slug, card, n, neighbours(rec) + same_section, cards.get(HOME), snap.get("card"))
                unchanged = snap.get("card") and all(card.get(k) == snap["card"].get(k) for k in ("name", "duration", "summary")) and n == snap.get("price")
                llms = snap.get("llms") or {}
                update_llms(files, slug, card, n, after=[llms.get("after")] + neighbours(rec) + same_section,
                            line=llms.get("line") if unchanged else None)
                meta[url] = dict(merged["seo"])
                search = snap.get("search") or {}
                keep_entry = search.get("entry") and unchanged and snap.get("seo") == merged["seo"]
                update_search(files, slug, None if keep_entry else card["name"],
                              None if keep_entry else final_seo(merged["seo"]["description"], n),
                              after=[search.get("after")] + neighbours(rec) + same_section, entry=search.get("entry"))
                update_sitemap(files, slug, today, after=[(snap.get("sitemap") or {}).get("after")] + neighbours(rec) + same_section)
                touched = True
            else:
                old = page
                before = files.get(rel)
                write_page(files, slug, merged, old)
                page_changed = files.get(rel) != before
                old_n = amount(old["blocks"].get("price"))
                fields = [k for k in CARD_KEYS if k != "home" and card.get(k) != old["card"].get(k)]
                price_changed = n != old_n
                if fields or price_changed:
                    for surface in (hub, HOME):
                        s = files.get(surface)
                        span = card_span(s, slug)
                        if span:
                            files.set(surface, s[:span[0]] + write_card(s[span[0]:span[1]], card, fields, n, price_changed) + s[span[1]:])
                    update_related(files, pages, slug, card, [f for f in fields if f in ("name", "location", "duration", "image")], n, price_changed)
                    if set(fields) & {"name", "duration", "summary"} or price_changed:
                        update_llms(files, slug, card, n)
                if card.get("home") != old["card"].get("home"):
                    if card.get("home"):
                        insert_card(files, HOME, slug, card, n, neighbours(rec) + [p for p in pages if p.startswith(sec + "/") and p != slug][::-1])
                    elif card_span(files.get(HOME), slug):
                        remove_span(files, HOME, card_span(files.get(HOME), slug))
                seo_changed = merged["seo"] != old["seo"]
                if seo_changed:
                    meta[url] = dict(merged["seo"])
                if "name" in fields or seo_changed or price_changed:
                    update_search(files, slug, card["name"] if "name" in fields else None,
                                  final_seo(merged["seo"]["description"], n) if (seo_changed or price_changed) else None)
                if page_changed or seo_changed:
                    update_sitemap(files, slug, today)
                touched = page_changed or bool(fields) or price_changed or seo_changed or card.get("home") != old["card"].get("home")
        elif have == "published":
            # hide: keep the page for later, redirect to the hub, take the trip out of every list
            files.set(f"{HIDDEN}/{slug}.php", files.get(rel))
            snap = hide_snapshot(files, slug, sec, page["card"], amount(page["blocks"].get("price")), page["seo"])
            files.set(f"{HIDDEN}/{slug}.json", json.dumps(snap, ensure_ascii=False, indent=1) + "\n")
            files.set(rel, f"<?php header('Location: /{sec}/', true, 301); exit;")
            for surface in (f"{sec}/index.php", HOME):
                span = card_span(files.get(surface), slug)
                if span:
                    remove_span(files, surface, span)
            remove_related(files, [p for p in pages if p != slug], slug)
            update_llms(files, slug, merged["card"], None, remove=True)
            update_search(files, slug, remove=True)
            update_sitemap(files, slug, today, remove=True)
            meta.pop(f"/{slug}/", None)
            touched = True

        if touched:
            changed.append(slug)
        live_status = "published" if want == "published" else ("hidden" if have else None)
        updates.append({"slug": slug, "data": merged, "draft_changed": merged != rec["data"],
                        "live_changed": merged != rec.get("live_data") or live_status != rec.get("live_status"),
                        "live_status": live_status, "published": touched, "uploaded": uploaded,
                        "updated_at": rec.get("updated_at")})

    if meta != meta_before:
        save_meta(files, meta)
    return updates, {"changed": changed, "notes": notes}


def site_record_from_text(files, slug):
    try:
        return site_record(files, slug)
    except Exception:  # an old copy that no longer parses: rewrite every block
        return None


def run(cmd):
    print("$", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout[-4000:], r.stderr[-2000:], flush=True)
    return r


def refresh_generated(files):
    """Titles/meta + JSON-LD for all trip pages, then the repo health check. Raises with the reason on failure."""
    for cmd in (["python", "_dev/product_meta.py"], ["python", "_dev/schema_products.py"], ["python", "_dev/health_check.py", "--local"]):
        r = run(cmd)
        if r.returncode != 0:
            tail = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.strip()][-6:]
            raise RuntimeError(f"{Path(cmd[1]).name} failed: " + " | ".join(tail))


# ----------------------------------------------------------------------------------------------- database


class DB:
    def __init__(self):
        self.url = os.environ["SUPABASE_URL"].rstrip("/")
        key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
        self.headers = {"apikey": key, "Content-Type": "application/json"}
        if key.startswith("eyJ"):
            self.headers["Authorization"] = "Bearer " + key

    def call(self, method, path, body=None, prefer="return=representation"):
        req = urllib.request.Request(self.url + path, method=method, headers={**self.headers, "Prefer": prefer},
                                     data=None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8"))
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Supabase {method} {path.split('?')[0]}: {e.code} {e.read()[:300]!r}") from None
        return json.loads(raw) if raw else None

    def products(self):
        return self.call("GET", "/rest/v1/products?select=*&order=sort_order,slug")

    def job(self, job_id, **fields):
        if job_id:
            self.call("PATCH", f"/rest/v1/publish_jobs?id=eq.{int(job_id)}", fields, prefer="return=minimal")


def now():
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def save_updates(db, updates):
    """Store what is live. The team's copy is only overwritten when nobody edited it during the publish."""
    for u in updates:
        if not (u["live_changed"] or u["draft_changed"] or u["published"]):
            continue
        slug = urllib.request.quote(u["slug"], safe="")
        body = {"live_data": u["data"], "live_status": u["live_status"]}
        if u["published"]:
            body["published_at"] = now()
        if u["draft_changed"] and u.get("updated_at"):
            stamp = urllib.request.quote(u["updated_at"], safe="")
            rows = db.call("PATCH", f"/rest/v1/products?slug=eq.{slug}&updated_at=eq.{stamp}", {"data": u["data"]})
            if not rows:
                print(f"  {u['slug']}: edited during publish, the new edits stay unpublished")
        db.call("PATCH", f"/rest/v1/products?slug=eq.{slug}", body, prefer="return=minimal")


# ----------------------------------------------------------------------------------------------- commands


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def cmd_export():
    records = export_site(Files())
    out = json.dumps(records, ensure_ascii=False, indent=1)
    if arg("--out"):
        Path(arg("--out")).write_text(out, encoding="utf-8")
        print(f"{len(records)} trips -> {arg('--out')}")
    else:
        print(out)


def cmd_import():
    """Seed the dashboard from the site, and copy edits that reached the repo (without touching unpublished drafts)."""
    db, files = DB(), Files()
    site = export_site(files)
    rows = {r["slug"]: r for r in db.products()}
    order = {slug: i for i, slug in enumerate(site)}
    new, updated = [], 0
    for slug, page in site.items():
        row = rows.get(slug)
        if not row:
            new.append({"slug": slug, "section": slug.split("/")[0], "status": "published", "data": page,
                        "live_data": page, "live_status": "published", "sort_order": order[slug] * 10})
            continue
        live, draft = row.get("live_data"), row["data"]
        new_draft = copy.deepcopy(draft)
        for u in UNITS:
            if get(draft, u) == get(live, u) and get(page, u) != get(live, u):
                put(new_draft, u, get(page, u))
        body = {}
        if page != live:
            body["live_data"] = page
        if row.get("live_status") != "published":
            body["live_status"] = "published"
        if new_draft != draft:
            body["data"] = new_draft
        if body:
            db.call("PATCH", f"/rest/v1/products?slug=eq.{urllib.request.quote(slug, safe='')}", body, prefer="return=minimal")
            updated += 1
    for i in range(0, len(new), 10):
        db.call("POST", "/rest/v1/products", new[i:i + 10], prefer="return=minimal")
    for slug, row in rows.items():
        if slug not in site and row.get("live_status") == "published" and files.exists(page_rel(slug)):
            db.call("PATCH", f"/rest/v1/products?slug=eq.{urllib.request.quote(slug, safe='')}", {"live_status": "hidden"}, prefer="return=minimal")
    print(f"import: {len(new)} new, {updated} updated, {len(site)} trips on the site")


def cmd_publish():
    job, state = arg("--job"), arg("--state")
    db = None if arg("--source") else DB()
    try:
        if db:
            db.job(job, status="running", run_url=run_url(), message=None)
            records = db.products()
        else:
            records = json.loads(Path(arg("--source")).read_text(encoding="utf-8"))
        files = Files()
        updates, summary = publish_records(records, files)
        written = files.flush()
        if written:
            refresh_generated(files)
        print("changed trips:", ", ".join(summary["changed"]) or "none")
        for n in summary["notes"]:
            print("  note:", n)
        if state:
            Path(state).write_text(json.dumps({"updates": updates, **summary}, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        if db:
            db.job(job, status="failed", message=str(e)[:900], finished_at=now())
        raise


def cmd_save():
    db, st = DB(), json.loads(Path(arg("--state")).read_text(encoding="utf-8"))
    save_updates(db, st["updates"])
    message = "; ".join(st["notes"])[:900] or None
    db.job(arg("--job"), status="deploying" if st["changed"] else "success", changed=st["changed"],
           commit_sha=arg("--commit"), message=message or ("Nothing new to publish" if not st["changed"] else None),
           **({} if st["changed"] else {"finished_at": now()}))


def cmd_finish():
    """--stage build: publishing stopped before the upload; --stage deploy: the upload job's result."""
    result, stage, job = arg("--result"), arg("--stage", "deploy"), arg("--job")
    db = DB()
    rows = db.call("GET", f"/rest/v1/publish_jobs?select=status&id=eq.{int(job)}") if job else []
    if rows and rows[0]["status"] in ("failed", "success"):
        return  # already reported by an earlier step
    if result == "success":
        db.job(job, status="success", finished_at=now())
    elif result == "skipped":
        db.job(job, status="success", finished_at=now(), message="Saved in the repository. The automatic website upload is switched off.")
    elif stage == "build":
        db.job(job, status="failed", finished_at=now(), message="Publishing stopped before the upload, so the website did not change. Press Publish again; if it fails twice, open the run link.")
    else:
        db.job(job, status="failed", finished_at=now(), message="The website upload did not finish. Your changes are saved; press Publish again to retry.")


def run_url():
    if os.environ.get("GITHUB_RUN_ID"):
        return f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    return None


if __name__ == "__main__":
    commands = {"export": cmd_export, "import": cmd_import, "publish": cmd_publish, "save": cmd_save, "finish": cmd_finish}
    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        sys.exit(__doc__)
    commands[sys.argv[1]]()
