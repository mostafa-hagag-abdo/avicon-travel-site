"""width/height on every <img>, so the browser reserves the space before the image arrives
(no layout jump - Core Web Vitals CLS). Mostly matters now that images below the hero are lazy.

The numbers are the file's real pixel size (read with Pillow). A zero-specificity rule in
<head>, `:where(img[width][height]){height:auto}`, stops the height attribute from ever
stretching an image: any CSS that sizes an image still wins, and images CSS only gives a
width to keep their shape from the attribute ratio.

Idempotent - re-run after adding images:
    python _dev/image_dimensions.py            # dry run
    python _dev/image_dimensions.py --apply
"""
import re, sys
from pathlib import Path
from urllib.parse import unquote

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMG = re.compile(r"<img\b[^>]*>", re.I)
RULE = '<style id="avicon-img-ratio">:where(img[width][height]){height:auto}</style>'
_cache = {}


def dims(src):
    u = unquote(src.split("?")[0].replace("https://avicontravel.com", ""))
    if not u.startswith("/assets/") or u.lower().endswith(".svg"):
        return None
    if u not in _cache:
        f = ROOT / u.lstrip("/")
        try:
            with Image.open(f) as im:
                _cache[u] = im.size
        except Exception:
            _cache[u] = None
    return _cache[u]


def main(apply):
    added = skipped = files = 0
    for p in ROOT.rglob("*.php"):
        rel = p.relative_to(ROOT)
        if {"assets", "_dev"} & set(rel.parts):
            continue
        s = open(p, encoding="utf-8", newline="").read()
        if s.startswith("<?php header('Location:"):
            continue

        def sub(m):
            nonlocal added, skipped
            tag = m.group(0)
            if re.search(r"\swidth=", tag) and re.search(r"\sheight=", tag):
                return tag
            src = re.search(r"""\ssrc=["']([^"']+)""", tag)
            d = dims(src.group(1)) if src else None
            if not d or re.search(r"\s(width|height)=", tag):   # unknown size, or only one of the two set: leave it
                skipped += 1
                return tag
            added += 1
            return tag.replace("<img", f'<img width="{d[0]}" height="{d[1]}"', 1)

        new = IMG.sub(sub, s)
        if "</head>" in new and 'id="avicon-img-ratio"' not in new:
            new = new.replace("</head>", RULE + "\n</head>", 1)
        if new != s:
            files += 1
            if apply:
                open(p, "w", encoding="utf-8", newline="").write(new)
    print(f"width/height added to {added} <img>; left alone {skipped} (svg/remote/partial); files changed {files}")
    print("written" if apply else "dry run - nothing written")


if __name__ == "__main__":
    main("--apply" in sys.argv)
