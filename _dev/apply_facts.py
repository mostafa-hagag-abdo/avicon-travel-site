"""Add four answer-ready cards to each product page's first quick-facts grid: Price, Pickup, Included, Best Time.

Price comes from the page's own booking box ("From $X / person", or "On request"), so it never disagrees with
the page. Pickup, Included and Best Time come from product_facts.json. Re-runnable: cards marked "qf-extra"
are removed and re-added.
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads(Path(__file__).with_name("product_facts.json").read_text(encoding="utf-8"))
CARDS = [("fa-tag", "Price", "price"), ("fa-location-dot", "Pickup", "pickup"),
         ("fa-circle-check", "Included", "included"), ("fa-sun", "Best Time", "best")]


def end_of_div(s, start):
    depth = 0
    for m in re.finditer(r"<div\b|</div>", s[start:]):
        depth += 1 if m.group().startswith("<div") else -1
        if depth == 0:
            return start + m.end()
    raise ValueError("unbalanced div")


def price(s):
    m = re.search(r'class="price-amount">(.*?)</div>', s, re.S)
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", m.group(1)))).strip() if m else ""
    n = re.search(r"\d[\d,]*", t)
    return f"From ${int(n.group().replace(',', '')):,} / person" if n else "On request"


for url, rec in DATA.items():
    path = ROOT / url.strip("/") / "index.php"
    s = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in s else "\n"
    m = re.search(r'<div class="quick-facts">', s)
    if not m:
        sys.exit(f"no quick-facts grid: {url}")
    end = end_of_div(s, m.start())
    grid = s[m.start():end]
    for old in reversed([c for c in re.finditer(r'<div class="fact-card qf-extra">', grid)]):
        stop = end_of_div(grid, old.start())
        line = grid.rfind("\n", 0, old.start()) + 1
        grid = grid[:line] + grid[grid.find("\n", stop) + 1:]
    pad = re.search(r"\n([ \t]*)<div class=\"fact-card", grid).group(1)
    vals = dict(rec, price=price(s))
    block = "".join(
        f'{pad}<div class="fact-card qf-extra">{nl}'
        f'{pad}  <div class="fact-icon"><i class="fas {icon}"></i></div>{nl}'
        f'{pad}  <div class="fact-label">{label}</div>{nl}'
        f'{pad}  <div class="fact-value">{html.escape(vals[key], quote=False)}</div>{nl}'
        f'{pad}</div>{nl}' for icon, label, key in CARDS)
    close = grid.rfind("</div>")
    close_line = grid.rfind("\n", 0, close) + 1
    grid = grid[:close_line] + block + grid[close_line:]
    new = s[:m.start()] + grid + s[end:]
    if new != s:
        path.write_bytes(new.encode("utf-8"))
    print(f"{vals['price']:>22}  {url}")
