"""End-to-end test of sync.py publish on a throw-away copy of the repo (never run it in the real checkout).

    git worktree add ../avicon-sync-test HEAD
    python ../avicon-sync-test/_dev/cms/test_sync.py

1. identity: publishing the site's own records changes no file;
2. edits: price, card name/summary, gallery photo, SEO title, "show on home" off, a hidden trip, a new trip copied
   from a template, a repo-side edit merged with a dashboard edit -> generated files pass health_check, and exporting
   the site again returns exactly the published data;
3. un-hide: the hidden trip comes back byte-identical.
"""
import copy
import io
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sync  # noqa: E402

ROOT = sync.ROOT
if (ROOT / ".git").is_dir():
    sys.exit("refusing to run in the main checkout: use a git worktree")

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)
        print("  FAIL", msg)


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout


def records_from_site():
    site = sync.export_site(sync.Files())
    return [{"slug": s, "section": s.split("/")[0], "status": "published", "template": None, "sort_order": i,
             "data": copy.deepcopy(d), "live_data": copy.deepcopy(d), "live_status": "published"} for i, (s, d) in enumerate(site.items())]


def publish(records, fetch=None):
    files = sync.Files()
    updates, summary = sync.publish_records(records, files, today="2026-09-16", fetch=fetch)
    written = files.flush()
    return updates, summary, written


# ---------------------------------------------------------------- 1. identity
print("1. identity")
recs = records_from_site()
updates, summary, written = publish(recs)
check(not written, f"identity publish wrote files: {written}")
check(not summary["changed"], f"identity publish changed trips: {summary['changed']}")

# ---------------------------------------------------------------- 2. edits
print("2. edits")
by = {r["slug"]: r for r in recs}
BAL, RAS, CRU, NEW = "tours/luxor-hot-air-balloon", "tours/ras-mohammed-snorkeling", "nile-cruises/ms-tulip-nile-cruise", "tours/luxor-balloon-and-west-bank"

# fake Storage download: a generated JPEG
from PIL import Image  # noqa: E402
buf = io.BytesIO()
Image.new("RGB", (2400, 1600), (200, 120, 40)).save(buf, "JPEG")
fake = {"n": 0}


def fetch(url):
    fake["n"] += 1
    return buf.getvalue()


STORAGE = "https://tdpsvcsniftrgnrdyhgi.supabase.co/storage/v1/object/public/site-images/uploads/Balloon%20Sunrise.JPG"

b = by[BAL]["data"]
b["blocks"]["price"]["amount"] = "105"
b["card"]["name"] = "Luxor Sunrise Hot Air Balloon"
b["card"]["summary"] = "Sunrise balloon flight over Luxor's West Bank with hotel pickup."
b["blocks"]["gallery"].append({"src": STORAGE, "alt": "Balloons over the West Bank", "width": "", "height": ""})
b["seo"]["title"] = "Luxor Hot Air Balloon Ride at Sunrise | From {price}"
b["blocks"]["faq"]["items"].append({"q": "Can children fly?", "a": "<p>Yes, from age 6 with an adult.</p>"})

c = by[CRU]["data"]
c["card"]["home"] = False
c["blocks"]["price"]["amount"] = "820"

by[RAS]["status"] = "hidden"

new_data = copy.deepcopy(by[BAL]["data"])
new_data["blocks"]["title"] = "Luxor Balloon &amp; West Bank Day"
new_data["blocks"]["price"]["amount"] = "140"
new_data["card"].update({"name": "Luxor Balloon &amp; West Bank Day", "home": True, "summary": "Balloon at sunrise, then the Valley of the Kings."})
new_data["seo"] = {"title": "Luxor Balloon & West Bank Day Tour | From {price}",
                   "description": "Start with a sunrise hot air balloon flight over Luxor, then visit the Valley of the Kings, Hatshepsut Temple and the Colossi. From {price} per person."}
new_data["blocks"]["gallery"] = [{"src": STORAGE, "alt": "Luxor balloons", "width": "", "height": ""}]
recs.append({"slug": NEW, "section": "tours", "status": "published", "template": BAL, "sort_order": 999,
             "data": new_data, "live_data": None, "live_status": None})

# a repo-side edit on another trip, plus a dashboard edit of a different field of the same trip
GIZA = "tours/giza-pyramids-saqqara-tour"
repo_faq_q = "Is the Saqqara tour suitable for families?"
site_now = sync.site_record(sync.Files(), GIZA)
site_now["blocks"]["faq"]["items"].append({"q": repo_faq_q, "a": "<p>Yes.</p>"})
f = sync.Files()
f.set(sync.page_rel(GIZA), sync.blocks.apply(f.get(sync.page_rel(GIZA)), site_now["blocks"]))
f.flush()
by[GIZA]["data"]["blocks"]["price"]["amount"] = "55"

updates, summary, written = publish(recs, fetch)
print("   changed:", summary["changed"], "notes:", summary["notes"])
check(set(summary["changed"]) == {BAL, CRU, RAS, NEW, GIZA}, f"changed trips {summary['changed']}")
check(fake["n"] == 1, f"image downloaded {fake['n']} times (same URL twice should download once)")

r = sync.run(["python", "_dev/product_meta.py"])
check(r.returncode == 0, "product_meta.py failed")
r = sync.run(["python", "_dev/schema_products.py"])
check(r.returncode == 0, "schema_products.py failed")
r = sync.run(["python", "_dev/health_check.py", "--local"])
check(r.returncode == 0, "health_check failed")

files = sync.Files()
home, hub, llms, sitemap = (files.get(x) for x in ("index.php", "tours/index.php", "llms.txt", "sitemap.xml"))
search = files.get("search/index.php")
bal = files.get(sync.page_rel(BAL))
check("<h3>Luxor Sunrise Hot Air Balloon</h3>" in home and "<h3>Luxor Sunrise Hot Air Balloon</h3>" in hub, "card name on home + hub")
check('<div class="price">$105.00</div>' in hub, "hub price $105.00")
check("Sunrise balloon flight over Luxor's West Bank" in hub, "hub summary")
check("from $105 per person" in llms and "[Luxor Sunrise Hot Air Balloon]" in llms, "llms line")
check('"t": "Luxor Sunrise Hot Air Balloon"' in search, "search title")
check("From $105 / person" in bal and "From $105 / person" in bal.split('class="summary-row total"')[1][:200], "facts + summary price")
check('value="Luxor Sunrise Hot Air Balloon"' in bal, "tour_package follows the card name")
check("<title>Luxor Hot Air Balloon Ride at Sunrise | From $105</title>" in bal, "SEO title with price")
check("1 / 4" in bal, "lightbox count")
check('"price":"105"' in bal, "JSON-LD offer price")
related = [p for p in sync.product_pages(files) if "window.location.href='/tours/luxor-hot-air-balloon/'" in files.get(sync.page_rel(p))]
check(related and all("$105<small>/person</small>" in files.get(sync.page_rel(p)) for p in related), "related cards price")
check('href="/nile-cruises/ms-tulip-nile-cruise/"' not in home, "cruise removed from home")
check("$820/person" in files.get("nile-cruises/index.php"), "cruise hub price")
check(files.get(sync.page_rel(RAS)) == "<?php header('Location: /tours/', true, 301); exit;", "hidden trip is a redirect")
check((ROOT / sync.HIDDEN / f"{RAS}.php").exists(), "hidden page kept")
check("ras-mohammed-snorkeling" not in hub + llms + sitemap + search, "hidden trip removed from hub/llms/sitemap/search")
check(not any("window.location.href='/tours/ras-mohammed-snorkeling/'" in files.get(sync.page_rel(p)) for p in sync.product_pages(files)), "hidden trip removed from related cards")
check(f'href="/{NEW}/"' in hub and f'href="/{NEW}/"' in home, "new trip card on hub + home")
check(f"{sync.DOMAIN}/{NEW}/" in sitemap and f"{sync.DOMAIN}/{NEW}/" in llms and f'"/{NEW}/"' in search, "new trip in sitemap/llms/search")
newp = files.get(sync.page_rel(NEW))
check(f'<link rel="canonical" href="{sync.DOMAIN}/{NEW}/"' in newp and "luxor-hot-air-balloon/\"" not in newp.split("</head>")[0], "new page canonical")
check("/assets/uploads/cms/balloon-20sunrise-" in newp and 'width="1600" height="1067"' in newp, "uploaded image localized and sized")
check(f'og:image" content="{sync.DOMAIN}/assets/uploads/cms/' in newp, "new page og:image")
giza = files.get(sync.page_rel(GIZA))
check(repo_faq_q in giza and "From $55 / person" in giza, "repo FAQ edit kept + dashboard price applied")
merged_giza = next(u for u in updates if u["slug"] == GIZA)["data"]
check(any(i["q"] == repo_faq_q for i in merged_giza["blocks"]["faq"]["items"]), "repo edit copied back to the dashboard data")

# exporting the site again gives the published data
site = sync.export_site(sync.Files())
for u in updates:
    if u["live_status"] == "published":
        got = site.get(u["slug"])
        if got != u["data"]:
            diff = [".".join(x) for x in sync.UNITS if sync.get(got, x) != sync.get(u["data"], x)]
            check(False, f"{u['slug']}: site differs from published data in {diff}")

# ---------------------------------------------------------------- 3. publish again = no change; then un-hide
print("3. republish + un-hide")
recs2 = []
for rec in recs:
    u = next(x for x in updates if x["slug"] == rec["slug"])
    recs2.append({**rec, "data": copy.deepcopy(u["data"]), "live_data": copy.deepcopy(u["data"]), "live_status": u["live_status"]})
_, summary2, written2 = publish(recs2)
check(not written2, f"second publish wrote {written2}")
next(r for r in recs2 if r["slug"] == RAS)["status"] = "published"
_, summary3, written3 = publish(recs2)
orig = subprocess.run(["git", "show", f"HEAD:{RAS}/index.php"], cwd=ROOT, capture_output=True).stdout.decode("utf-8")
check((ROOT / RAS / "index.php").read_bytes().decode("utf-8") == orig, "un-hidden page is byte-identical")
check('href="/tours/ras-mohammed-snorkeling/"' in sync.Files().get("tours/index.php"), "un-hidden card back on hub")
check(not (ROOT / sync.HIDDEN / f"{RAS}.php").exists(), "hidden copy removed after un-hide")

print(f"\n{len(failures)} failure(s)")
print(git("status", "--short")[:3000])
sys.exit(1 if failures else 0)
