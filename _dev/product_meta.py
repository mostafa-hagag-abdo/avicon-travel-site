"""Titles and meta descriptions for the product pages, from _dev/product_meta.json.

`{price}` in a title/description is filled with the page's visible starting price, so
re-running after a price change keeps the snippets honest. Also syncs og:/twitter: tags.
Run schema_products.py afterwards so the WebPage node picks up the new title/description.

    python _dev/product_meta.py --check   # show the final strings and their lengths
    python _dev/product_meta.py           # write
"""
import html, json, re, sys
from pathlib import Path

from schema_products import PRICE_UNDER_REVIEW, ROOT, product

META = json.load(open(Path(__file__).with_name("product_meta.json"), encoding="utf-8"))


def attr(s):
    return html.escape(s, quote=False).replace('"', "&quot;")


def swap(s, rx, value):
    new, n = re.subn(rx, lambda m: m.group(1) + value + m.group(2), s, count=1, flags=re.S | re.I)
    return new, n


def main(check):
    problems, pages = [], []
    for url, m in META.items():
        f = ROOT / url.strip("/") / "index.php"
        s = open(f, encoding="utf-8", newline="").read()
        p = product(url, s)
        price = f"${p['price']:,}" if p["price"] else None
        final = {}
        for key in ("title", "description"):
            if "{price}" in m[key] and (not price or url in PRICE_UNDER_REVIEW):
                problems.append(f"{url}: {key} needs a price the page doesn't settle")
            final[key] = m[key].replace("{price}", price or "")
        t, d = final["title"], final["description"]
        flag = ("" if len(t) <= 60 else " TITLE>60") + ("" if 120 <= len(d) <= 160 else " DESC!")
        print(f"{url}{flag}\n   [{len(t)}] {t}\n   [{len(d)}] {d}")
        if flag:
            problems.append(f"{url}:{flag}")
        for rx, value in [(r"(<title>).*?(</title>)", html.escape(t, quote=False)),
                          (r'(<meta name="description" content=")[^"]*(")', attr(d))]:
            s, n = swap(s, rx, value)
            if n != 1:
                problems.append(f"{url}: {rx[:30]} not found")
        for rx, value in [(r'(<meta property="og:title" content=")[^"]*(")', attr(t)),
                          (r'(<meta name="twitter:title" content=")[^"]*(")', attr(t)),
                          (r'(<meta property="og:description" content=")[^"]*(")', attr(d)),
                          (r'(<meta name="twitter:description" content=")[^"]*(")', attr(d))]:
            s, _ = swap(s, rx, value)
        pages.append((f, s))
    if not check and not problems:  # all-or-nothing
        for f, s in pages:
            open(f, "w", encoding="utf-8", newline="").write(s)
    print(f"\n{len(META)} pages", "checked" if check else "written" if not problems else "NOT written")
    for p in problems:
        print("  !", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
