"""Move inline <style> blocks that repeat across pages into cached CSS files.

A block that appears, byte-for-byte, on 2+ pages and is at least 2 KB is written once to
assets/css/shared/<name>.<hash>.css and every copy is replaced, in place, by a <link> -
same position, so the cascade order does not change. The hash is part of the file name,
so an edited block gets a new file and browsers never serve a stale one.

To change shared CSS later, edit the file in assets/css/shared/ (and bump the name's
hash or add ?v=) - the pages no longer carry a copy.

    python _dev/extract_shared_css.py            # dry run
    python _dev/extract_shared_css.py --apply
"""
import hashlib, re, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "css" / "shared"
MIN_BYTES, MIN_PAGES = 2000, 2
STYLE = re.compile(r"<style\b[^>]*>(.*?)</style>", re.S | re.I)
NAMES = [("/* ── TOKENS ── */ .avf", "footer"), (".avi-seasonal-pop", "popup"), ("Booking-style hero (bk-*)", "bk-hero"),
         ("Article v2", "article"), (":root{--wp--preset", "wp-global"), (".wp-block-audio", "wp-block-library"),
         ("@import url('https://fonts.googleapis.com/css2?family=Playfair", "cruise"), (":root{ --primary:#1A3A6E", "product")]


def norm(css):
    return css.replace("\r\n", "\n").strip()


def name_for(css):
    flat = re.sub(r"\s+", " ", css[:200])
    return next((n for key, n in NAMES if key in flat), "block")


def main(apply):
    pages = []
    for p in ROOT.rglob("*.php"):
        rel = p.relative_to(ROOT)
        if {"assets", "_dev", "includes"} & set(rel.parts):
            continue
        s = open(p, encoding="utf-8", newline="").read()
        if not s.startswith("<?php header('Location:"):
            pages.append((p, s))
    seen = defaultdict(set)
    for p, s in pages:
        for m in STYLE.finditer(s):
            seen[norm(m.group(1))].add(p)
    shared = {css: hashlib.md5(css.encode()).hexdigest()[:10] for css, ps in seen.items()
              if len(ps) >= MIN_PAGES and len(css.encode()) >= MIN_BYTES}
    problems = []
    files = {}
    for css, h in shared.items():
        rel_urls = [u for u in re.findall(r"url\(\s*['\"]?([^'\")]+)", css) if not re.match(r"(/|https?:|data:)", u)]
        if rel_urls:
            problems.append(f"{h}: relative url() {rel_urls[:2]}")
        files[css] = f"/assets/css/shared/{name_for(css)}.{h}.css"
    saved = sum(len(css.encode()) * (len(seen[css]) - 1) for css in shared)
    print(f"{len(shared)} shared blocks -> files; bytes no longer repeated in pages: {saved/1e6:.2f} MB")
    for css, f in sorted(files.items(), key=lambda x: -len(x[0]) * len(seen[x[0]])):
        print(f"   {len(css.encode())//1024:3} KB x {len(seen[css]):2} pages  {f}")

    changed = 0
    for p, s in pages:
        def sub(m):
            f = files.get(norm(m.group(1)))
            return f"<link rel='stylesheet' href='{f}' type='text/css' media='all' />" if f else m.group(0)
        new = STYLE.sub(sub, s)
        if new != s:
            changed += 1
            if apply and not problems:
                open(p, "w", encoding="utf-8", newline="").write(new)
    if apply and not problems:
        OUT.mkdir(parents=True, exist_ok=True)
        for css, f in files.items():
            (ROOT / f.lstrip("/")).write_text(css + "\n", encoding="utf-8", newline="\n")
    print(f"pages changed: {changed}")
    for pr in problems:
        print("  !", pr)
    print("written" if apply and not problems else "dry run - nothing written")


if __name__ == "__main__":
    main("--apply" in sys.argv)
