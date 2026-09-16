"""Round-trip tests for blocks.py on every product page.

    python _dev/cms/test_blocks.py

1. identity: apply(page, extract(page)) returns the page byte-for-byte;
2. edit: for every block, change the data, apply it, and check that extract() of the result returns the new
   data for that block, every other block is unchanged, and the page's <div> balance is intact.
"""
import copy
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blocks  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def pages():
    for sec in ("tours", "nile-cruises", "packages"):
        for p in sorted((ROOT / sec).glob("*/index.php")):
            s = p.read_bytes().decode("utf-8")
            if not s.startswith("<?php header("):
                yield f"{sec}/{p.parent.name}", s


def mutate(key, value):
    v = copy.deepcopy(value)
    if key in ("title", "longform", "tour_package", "crumb"):
        return v + " EDITED" if key != "longform" else v + "<p class=\"section-sub\">Edited paragraph.</p>"
    if key == "badge":
        v["text"] += " EDITED"
    elif key == "chips":
        v[0]["text"] += " EDITED"
        v.append({"icon": "fa-star", "label": v[0]["label"] and "Extra", "text": "New chip"})
    elif key == "gallery":
        v.append({"src": "/assets/uploads/cms/new.webp", "alt": "New photo", "width": "800", "height": "600"})
        v[0]["alt"] += " EDITED"
    elif key == "hero_image":
        v["src"] = "/assets/uploads/cms/hero.webp"
    elif key == "overview":
        v["paragraphs"].append("Second <strong>new</strong> paragraph.")
    elif key == "facts":
        v["cards"][0]["value"] += " EDITED"
        v["extra"]["Best Time"] = "All year"
    elif key == "highlights":
        if v["cards"]:
            v["cards"][0]["value"] += " EDITED"
        else:
            v["items"].append("New highlight")
    elif key == "route":
        v["stops"].append({"icon": "fa-flag", "name": "New stop", "label": "End"})
        v["connectors"].append(v["connectors"][-1] if v["connectors"] else "fa-arrow-right")
    elif key == "pricing":
        if v["kind"] == "table":
            v["rows"][0][1] = "999 USD"
        else:
            v["seasons"][0]["rows"][0][1] = "999 $"
            v["seasons"].append({"icon": "fa-calendar-alt", "label": "New season", "rows": [["Solo", "1 $"]]})
    elif key == "itinerary":
        v["days"].append({"label": f"Day {len(v['days']) + 1}", "title": "New day & more", "html": "<p>New day text.</p>"})
        v["days"][0]["html"] = "<p>Edited first day.</p>"
    elif key in ("included", "excluded"):
        v = v[:-1] + ["New &amp; item"]
    elif key == "faq":
        v["items"].append({"q": "New question?", "a": "<p>New answer.</p>"})
    elif key == "price":
        v["amount"] = "1,234"
    return v


def balance(s):
    return len(re.findall(r"<div\b", s)) - len(re.findall(r"</div>", s))


failures, counts = [], {}
for slug, s in pages():
    data = blocks.extract(s)
    if blocks.apply(s, data) != s:
        failures.append(f"{slug}: identity round-trip changed the page")
    for key in blocks.BLOCKS + ["tour_package", "crumb"]:
        if data.get(key) is None:
            continue
        counts[key] = counts.get(key, 0) + 1
        new = copy.deepcopy(data)
        new[key] = mutate(key, data[key])
        try:
            out = blocks.apply(s, new)
        except Exception as e:  # report and continue
            failures.append(f"{slug}: {key}: apply raised {e!r}")
            continue
        got = blocks.extract(out)
        if got[key] != new[key]:
            failures.append(f"{slug}: {key}: re-extract differs\n   want {json.dumps(new[key])[:300]}\n   got  {json.dumps(got[key])[:300]}")
        for other in blocks.BLOCKS + ["tour_package", "crumb"]:
            if other != key and other not in ("price",) and got.get(other) != data.get(other):
                failures.append(f"{slug}: editing {key} changed {other}")
        if balance(out) != balance(s):
            failures.append(f"{slug}: {key}: div balance {balance(s)} -> {balance(out)}")

print("blocks found on pages:", json.dumps(counts))
print(f"{len(failures)} failure(s)")
for f in failures[:40]:
    print(" -", f)
sys.exit(1 if failures else 0)
