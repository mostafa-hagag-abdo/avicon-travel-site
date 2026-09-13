"""Append the long-form guide copy from product_longform.json to the end of each product page's Overview tab.

Re-runnable: an existing <div class="av-longform"> block is replaced, not duplicated.
Body items: a string is a paragraph, a list is a bulleted list. Inline markup: **bold** and [text](/internal/url/).
Run schema_products.py afterwards only if other page facts changed (this block is not part of the schema).
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((Path(__file__).with_name("product_longform.json")).read_text(encoding="utf-8"))
LINK_STYLE = "color:var(--primary-light);font-weight:600;text-decoration:underline;text-underline-offset:3px"
UL_STYLE = "padding-left: 20px; color: var(--text-muted); font-size: 13px; line-height: 1.7; margin-bottom: 18px;"
REDIRECT = "<?php header('Location:"


def end_of_div(s, start):
    depth = 0
    for m in re.finditer(r"<div\b|</div>", s[start:]):
        depth += 1 if m.group().startswith("<div") else -1
        if depth == 0:
            return start + m.end()
    raise ValueError("unbalanced div")


def check_link(url):
    if not url.startswith("/") or not url.endswith("/"):
        raise ValueError(f"link must be an internal /path/: {url}")
    page = ROOT / url.strip("/") / "index.php"
    if not page.is_file() or page.read_text(encoding="utf-8", errors="ignore").startswith(REDIRECT):
        raise ValueError(f"broken internal link: {url}")


def inline(text):
    out = html.escape(text, quote=False)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)

    def link(m):
        check_link(m.group(2))
        return f'<a href="{m.group(2)}" style="{LINK_STYLE}">{m.group(1)}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, out)


def render(sections, nl):
    pad = " " * 10
    lines = [f'{pad}<div class="av-longform">']
    for i, sec in enumerate(sections):
        top = 32 if i == 0 else 24
        lines.append(f'{pad}  <h3 class="section-title" style="font-size:17px;margin-top:{top}px">{inline(sec["h"])}</h3>')
        for item in sec["body"]:
            if isinstance(item, list):
                lines.append(f'{pad}  <ul style="{UL_STYLE}">')
                lines += [f"{pad}    <li>{inline(li)}</li>" for li in item]
                lines.append(f"{pad}  </ul>")
            else:
                lines.append(f'{pad}  <p class="section-sub">{inline(item)}</p>')
    lines.append(f"{pad}</div>")
    return nl.join(lines) + nl


def words(sections):
    text = " ".join(" ".join(x if isinstance(x, str) else " ".join(x) for x in [s["h"]] + s["body"]) for s in sections)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text).replace("**", "")
    return len(re.findall(r"[A-Za-z][A-Za-z'’-]*", text))


for url, rec in DATA.items():
    path = ROOT / url.strip("/") / "index.php"
    s = path.read_bytes().decode("utf-8")
    nl = "\r\n" if "\r\n" in s else "\n"
    m = re.search(r'<div class="tab-panel[^"]*" id="overview">', s)
    if not m:
        sys.exit(f"no overview panel: {url}")
    end = end_of_div(s, m.start())
    panel = s[m.start():end]
    old = panel.find('<div class="av-longform">')
    if old >= 0:
        line_start = panel.rfind("\n", 0, old) + 1
        block_end = end_of_div(panel, old)
        if panel[block_end:block_end + len(nl)] == nl:
            block_end += len(nl)
        panel = panel[:line_start] + panel[block_end:]
    close = panel.rfind("</div>")
    close_line = panel.rfind("\n", 0, close) + 1
    panel = panel[:close_line] + render(rec["sections"], nl) + panel[close_line:]
    s = s[:m.start()] + panel + s[end:]
    path.write_bytes(s.encode("utf-8"))
    print(f"{words(rec['sections']):4} words  {url}")
