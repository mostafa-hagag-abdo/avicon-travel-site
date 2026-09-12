"""Lighter images for every page.

1. Every PNG/JPG the pages load that is over 100 KB gets a WebP sibling
   (`name.png` -> `name.png.webp`, the naming WordPress already used here), at most
   1600 px wide, quality 80. The original stays on disk: og:image, schema and old
   backlinks keep pointing at it.
2. References in src / data-src / srcset / url() switch to the WebP. <meta> tags and
   JSON-LD are left alone.
3. Every <img> after the first one on a page gets loading="lazy" (the first is usually
   the hero; images already in view load straight away anyway). This also stops the
   seasonal popup from downloading its two big photos on every page view.

Idempotent - re-run after adding pages or images:
    python _dev/optimize_images.py            # dry run
    python _dev/optimize_images.py --apply
"""
import re, sys
from pathlib import Path
from urllib.parse import unquote

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MIN_BYTES, MAX_W, QUALITY = 100_000, 1600, 80
HOST = "https://avicontravel.com"
REF = re.compile(r"""((?:src|data-src)=["'])([^"']+)(["'])|(srcset=["'])([^"']+)(["'])|(url\(['"]?)([^'")]+)(['"]?\))""", re.I)
IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)


def pages():
    for p in ROOT.rglob("*.php"):
        rel = p.relative_to(ROOT)
        if {"assets", "_dev"} & set(rel.parts) or rel.as_posix() == "includes/header.php":
            continue
        s = open(p, encoding="utf-8", newline="").read()
        if not s.startswith("<?php header('Location:"):
            yield p, s


def local(url):
    u = unquote(url.strip().split(" ")[0].split("?")[0].replace(HOST, ""))
    return u if u.startswith("/assets/uploads/") and u.lower().endswith((".png", ".jpg", ".jpeg")) else None


def urls_in(s):
    for m in REF.finditer(s):
        if m.group(2):
            yield m.group(2)
        elif m.group(5):
            yield from (part.strip().split(" ")[0] for part in m.group(5).split(","))
        else:
            yield m.group(8)


def convert(u, apply):
    src = ROOT / u.lstrip("/")
    dst = src.with_name(src.name + ".webp")
    if not src.is_file() or src.stat().st_size < MIN_BYTES:
        return None
    if dst.is_file():
        return u + ".webp", src.stat().st_size, dst.stat().st_size
    im = Image.open(src)
    im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") and "transparency" in im.info or im.mode == "RGBA" else "RGB")
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    tmp = dst.with_suffix(".tmp")
    im.save(tmp, "WEBP", quality=QUALITY, method=6)
    size = tmp.stat().st_size
    if size > src.stat().st_size * 0.8:          # not worth it
        tmp.unlink()
        return None
    if apply:
        tmp.replace(dst)
    else:
        tmp.unlink()
    return u + ".webp", src.stat().st_size, size


def main(apply):
    all_pages = list(pages())
    wanted = sorted({l for _, s in all_pages for l in map(local, urls_in(s)) if l})
    mapping, before, after = {}, 0, 0
    for u in wanted:
        r = convert(u, apply)
        if r:
            mapping[u] = r[0]
            before += r[1]
            after += r[2]
    print(f"{len(wanted)} PNG/JPG referenced; converting {len(mapping)}: {before/1e6:.1f} MB -> {after/1e6:.1f} MB")

    def swap(url):
        l = local(url)
        if l in mapping:
            return url.replace(l, mapping[l]) if l in url else HOST + mapping[l]
        return url

    def sub(m):
        if m.group(2):
            return m.group(1) + swap(m.group(2)) + m.group(3)
        if m.group(5):
            parts = [p.strip() for p in m.group(5).split(",")]
            return m.group(4) + ", ".join(" ".join([swap(p.split(" ")[0])] + p.split(" ")[1:]) for p in parts) + m.group(6)
        return m.group(7) + swap(m.group(8)) + m.group(9)

    refs = lazy = changed = 0
    firsts = {}
    for p, s in all_pages:
        new = REF.sub(sub, s)
        refs += sum(1 for a, b in zip(re.findall(r"uploads/[^\"' )]+", s), re.findall(r"uploads/[^\"' )]+", new)) if a != b)
        # the seasonal popup is hidden until it opens: its images are never "the hero"
        pop = re.search(r'<div class="avi-seasonal-pop".*?</div>\s*</div>\s*</div>', new, re.S)
        out, last, first_seen = [], 0, False
        for m in IMG_TAG.finditer(new):
            tag = m.group(0)
            in_popup = bool(pop and pop.start() <= m.start() < pop.end())
            if not first_seen and not in_popup:
                first_seen = True
                key = "home" if p.parent == ROOT else p.parent.name
                firsts[key] = re.search(r'src="([^"]+)"', tag).group(1) if 'src="' in tag else tag[:60]
            elif "loading=" not in tag:
                out.append(new[last:m.start()] + tag.replace("<img", '<img loading="lazy"', 1))
                last = m.end()
                lazy += 1
        new = "".join(out) + new[last:]
        if new != s:
            changed += 1
            if apply:
                open(p, "w", encoding="utf-8", newline="").write(new)
    print(f"references switched to WebP: {refs}; loading=lazy added: {lazy}; files changed: {changed}")
    for k in ("home", "7-days-cairo-hurghada-holiday", "ms-tulip-nile-cruise", "luxor-hot-air-balloon",
              "cairo-travel-guide-pyramids-museums-bazaars", "packages", "about"):
        if k in firsts:
            print(f"   first <img> kept eager on {k}: {firsts[k][:90]}")
    missing = [l for _, s in (pages() if apply else []) for l in (local(u) for u in urls_in(s)) if l and not (ROOT / l.lstrip('/')).is_file()]
    missing += [m for m in mapping.values() if apply and not (ROOT / m.lstrip("/")).is_file()]
    if apply:
        print("broken references after rewrite:", missing[:5] or "none")
    print("written" if apply else "dry run - nothing written")


if __name__ == "__main__":
    main("--apply" in sys.argv)
