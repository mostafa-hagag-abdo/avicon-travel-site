"""Tell Bing/Yandex (IndexNow) about new or changed URLs - run AFTER the change is live.

    python _dev/indexnow_ping.py                  # every URL in sitemap.xml
    python _dev/indexnow_ping.py /packages/ /blog/some-post/

The key file (<32 hex>.txt) sits in the site root and must be reachable at
https://avicontravel.com/<key>.txt before the first ping.
"""
import json, re, sys, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "avicontravel.com"

key = next((f.stem for f in ROOT.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}", f.stem)), None)
if not key:
    sys.exit("no IndexNow key file in the site root")

if len(sys.argv) > 1:
    urls = [f"https://{HOST}{p if p.startswith('/') else '/' + p}" for p in sys.argv[1:]]
else:
    urls = re.findall(r"<loc>(.*?)</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))

body = json.dumps({"host": HOST, "key": key, "keyLocation": f"https://{HOST}/{key}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8"})
with urllib.request.urlopen(req, timeout=30) as r:
    print(r.status, f"- submitted {len(urls)} URLs")  # 200/202 = accepted
