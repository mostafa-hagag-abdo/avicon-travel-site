"""Daily health check for avicontravel.com: the repo and the live site. Exit code 1 when something needs attention.

    python _dev/health_check.py            # repo + live site
    python _dev/health_check.py --local    # repo only, no network

Repo: every JSON-LD block parses; every internal href/src points at a real page or file; redirect stubs point at
real pages; every sitemap URL is a real page. Live: every sitemap URL answers 200 without redirecting, the key files
(robots.txt, llms.txt, IndexNow key) answer 200, and pages changed in the last 3 days show the same <title> live as
in the repo (a mismatch usually means the deploy has not finished or failed).
"""
import html, json, re, subprocess, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://avicontravel.com"
SKIP = {"_dev", ".git", ".github", "database", "avicontravel-backup", "assets", "node_modules"}
REDIRECT = "<?php header('Location:"
UA = {"User-Agent": "AviconHealthCheck/1.0 (+https://avicontravel.com/)"}
problems, notes = [], []


def rel_url(p):
    r = p.parent.relative_to(ROOT).as_posix()
    return "/" if r == "." else f"/{r}/"


def page_files():
    for p in sorted(ROOT.rglob("index.php")):
        if p.relative_to(ROOT).parts[0] not in SKIP:
            yield p


def target_exists(path):
    path = path.split("#")[0].split("?")[0]
    if not path or path == "/":
        return True
    local = ROOT / path.lstrip("/")
    if path.endswith("/"):
        return (local / "index.php").is_file() or (local / "index.html").is_file()
    return local.is_file() or (local / "index.php").is_file()


def title_of(s):
    m = re.search(r"<title>(.*?)</title>", s, re.S)
    return html.unescape(m.group(1)).strip() if m else None


# ---------- repo ----------
pages, redirects, titles = {}, {}, {}
for p in page_files():
    s = p.read_text(encoding="utf-8", errors="replace")
    u = rel_url(p)
    if s.startswith(REDIRECT):
        redirects[u] = re.search(r"Location:\s*([^'\"]+)", s).group(1).strip()
        continue
    pages[u] = s
for inc in sorted((ROOT / "includes").glob("*.php")):
    pages[f"(include) {inc.name}"] = inc.read_text(encoding="utf-8", errors="replace")

ld_blocks = 0
for u, s in pages.items():
    for body in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', s, re.S):
        ld_blocks += 1
        try:
            json.loads(body)
        except ValueError as e:
            problems.append(f"broken JSON-LD on {u}: {e}")
    bad = set()
    for attr, link in re.findall(r'\b(href|src)="(/[^"]*)"', s):
        if link.startswith("//") or "<?" in link:
            continue
        if not target_exists(html.unescape(link)):
            bad.add(link)
    for link in sorted(bad):
        problems.append(f"broken internal link on {u}: {link}")
    if not u.startswith("(include)"):
        t = title_of(s)
        if t:
            titles.setdefault(t, []).append(u)

for u, target in redirects.items():
    if target.startswith("/") and not target_exists(target):
        problems.append(f"redirect {u} -> {target} points at a missing page")

for t, us in titles.items():
    if len(us) > 1:
        notes.append(f"same <title> on {len(us)} pages: {', '.join(us[:4])}")

sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
locs = re.findall(r"<loc>(.*?)</loc>", sitemap)
for loc in locs:
    path = loc.replace(SITE, "") or "/"
    if path in redirects:
        problems.append(f"sitemap lists a redirect: {path}")
    elif path not in pages and not target_exists(path):
        problems.append(f"sitemap lists a missing page: {path}")
indexable = {u for u, s in pages.items() if not u.startswith("(include)") and "noindex" not in s[:20000]}
missing = sorted(u for u in indexable if f"{SITE}{u}" not in locs and u not in ("/404/",))
for u in missing:
    notes.append(f"indexable page not in sitemap: {u}")

print(f"repo: {len([u for u in pages if not u.startswith('(include)')])} pages, {len(redirects)} redirect stubs, "
      f"{ld_blocks} JSON-LD blocks, {len(locs)} sitemap URLs")

# ---------- live ----------
if "--local" not in sys.argv:
    def fetch(url):
        t0 = time.time()
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8", errors="replace")
                return url, r.status, r.geturl(), body, time.time() - t0
        except urllib.error.HTTPError as e:
            return url, e.code, url, "", time.time() - t0
        except Exception as e:  # network trouble is reported, not raised
            return url, None, url, str(e), time.time() - t0

    stamp = f"hc={int(time.time())}"
    with ThreadPoolExecutor(8) as pool:
        results = list(pool.map(fetch, [f"{loc}{'&' if '?' in loc else '?'}{stamp}" for loc in locs]))
    slow = []
    for url, status, final, body, dt in results:
        clean = url.split("?")[0]
        if status != 200:
            problems.append(f"live {clean} answered {status or body[:80]}")
        elif final.split("?")[0] != clean:
            problems.append(f"live {clean} redirects to {final}")
        if dt > 3:
            slow.append(f"{clean} ({dt:.1f}s)")
    if slow:
        notes.append("slow pages (>3s): " + ", ".join(slow[:6]))
    key = next((f.name for f in ROOT.glob("*.txt") if re.fullmatch(r"[0-9a-f]{32}\.txt", f.name)), None)
    for f in ["robots.txt", "llms.txt", "sitemap.xml"] + ([key] if key else []):
        _, status, _, _, _ = fetch(f"{SITE}/{f}?{stamp}")
        if status != 200:
            problems.append(f"live /{f} answered {status}")
    changed = subprocess.run(["git", "-C", str(ROOT), "log", "--since=3.days", "--name-only", "--format="],
                             capture_output=True, text=True).stdout.split()
    checked = 0
    for f in sorted(set(c for c in changed if c.endswith("index.php"))):
        u = "/" + f[:-len("index.php")] if f != "index.php" else "/"
        if u not in pages:
            continue
        local_t = title_of(pages[u])
        _, status, _, body, _ = fetch(f"{SITE}{u}?{stamp}")
        checked += 1
        if status == 200 and title_of(body) != local_t:
            problems.append(f"not live yet? {u}: live title differs from the repo")
    ok = sum(1 for r in results if r[1] == 200)
    print(f"live: {ok}/{len(locs)} sitemap URLs answer 200; {checked} recently changed pages compared with the repo")

for n in notes:
    print("  note:", n)
for pr in problems:
    print("  PROBLEM:", pr)
print("RESULT:", "OK" if not problems else f"{len(problems)} problem(s)")
sys.exit(1 if problems else 0)
