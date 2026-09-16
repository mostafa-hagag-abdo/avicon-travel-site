"""Remove the Complianz cookie plugin from every page; assets/js/avicon-consent.js takes its place.

    python _dev/remove_complianz.py [--dry-run]

Per page:
- drops the Complianz stylesheets, the inline .cmplz-hidden style, the banner markup, the manage-consent button
  and the three Complianz scripts;
- turns the Complianz-blocked Google Maps iframe into <iframe data-consent-src="..."> (loaded after consent or
  a "Show map" click);
- removes body data-cmplz.
On /cookie-policy-eu/ the manage-consent block becomes a "Change cookie settings" button.
The footer gets a "Cookie settings" link. includes/tracking.php loads avicon-consent.js and reads its consent.
Re-runnable: pages without Complianz leftovers are left unchanged.
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"_dev", ".git", ".github", "database", "avicontravel-backup", "node_modules", "assets"}
dry = "--dry-run" in sys.argv


def end_of_div(s, start):
    depth = 0
    for m in re.finditer(r"<div\b|</div>", s[start:]):
        depth += 1 if m.group().startswith("<div") else -1
        if depth == 0:
            return start + m.end()
    raise ValueError("unbalanced div")


def remove_div(s, marker):
    i = s.find(marker)
    if i < 0:
        return s, 0
    start = i if s.startswith("<div", i) else s.rfind("<div", 0, i + len(marker))
    end = end_of_div(s, start)
    while end < len(s) and s[end] in "\r\n":
        end += 1
    return s[:start] + s[end:], 1


def clean(s):
    n = {}
    s, n["css"] = re.subn(r"[ \t]*<link rel='stylesheet' id='cmplz-(?:general|banner-1-optin)-css'[^>]*/>[ \t]*\r?\n?", "", s)
    s, n["hidden-style"] = re.subn(r"<style>\.cmplz-hidden \{\s*display: none !important;\s*\}</style>", "", s)
    s, n["comment"] = re.subn(r"<!-- Consent Management powered by Complianz[^>]*-->\r?\n?", "", s)
    s, n["banner"] = remove_div(s, '<div id="cmplz-cookiebanner-container">')
    s, n["manage"] = remove_div(s, '<div id="cmplz-manage-consent"')
    s, n["scripts"] = re.subn(
        r'<script[^>]*id="cmplz-cookiebanner-js(?:-extra|-after)?"[^>]*>.*?</script>[ \t]*\r?\n?', "", s, flags=re.S)
    s, n["body"] = re.subn(r"<body data-rsssl=1 data-cmplz=1 ", "<body data-rsssl=1 ", s)

    def map_frame(m):
        tag = m.group(0)
        src = re.search(r'data-src-cmplz="([^"]+)"', tag).group(1)
        tag = re.sub(r'\s(?:data-placeholder-image|data-category|data-service|data-cmplz-target|data-src-cmplz|data-deferlazy)="[^"]*"', "", tag)
        tag = re.sub(r'\sclass="cmplz-[^"]*"', "", tag)
        tag = re.sub(r'\s*src="about:blank"', "", tag)
        return tag.replace("<iframe", f'<iframe data-consent-src="{src}" loading="lazy"', 1)
    s, n["maps"] = re.subn(r"<iframe\b[^>]*data-src-cmplz=\"[^\"]+\"[^>]*>", map_frame, s, flags=re.S)
    s = s.replace('<div class="cmplz-placeholder-parent">', "<div>")
    s, n["footer-link"] = re.subn(
        r'(<p class="avf__copy">© <span id="avf-year">\d{4}</span> Avicon Travel\. All rights reserved\.)(</p>)',
        r'\1 · <a href="#cookie-settings" class="avf__cookie-link">Cookie settings</a>\2', s)
    return s, {k: v for k, v in n.items() if v}


changed = {}
for p in sorted(ROOT.rglob("*.php")):
    rel = p.relative_to(ROOT)
    if rel.parts[0] in SKIP:
        continue
    raw = p.read_bytes().decode("utf-8")
    if "cmplz" not in raw and "avf__copy" not in raw:
        continue
    new, counts = clean(raw)
    if rel.as_posix() == "cookie-policy-eu/index.php":
        new, k = re.subn(
            r'<div id="cmplz-manage-consent-container-nojavascript">.*?</div><div id="cmplz-manage-consent-container" class="cmplz-manage-consent-container"></div>',
            '<p><button type="button" class="avc-settings-btn" data-cookie-settings>Change cookie settings</button></p>', new, flags=re.S)
        new = new.replace('As soon as you click on "Save My Choices", you consent to us using the categories of cookies and plug-ins you selected in the pop-up',
                          'As soon as you click "Accept", you consent to us using analytics cookies and embedded maps')
        if k:
            counts["policy-button"] = k
    if "avf__cookie-link" in new and ".avf__cookie-link" not in new:
        new = new.replace('<p class="avf__copy">', '<style>.avf__cookie-link{color:inherit;text-decoration:underline;text-underline-offset:2px}</style><p class="avf__copy">', 1)
    if new != raw:
        changed[rel.as_posix()] = counts
        if not dry:
            p.write_bytes(new.encode("utf-8"))

tracking = ROOT / "includes/tracking.php"
t = tracking.read_bytes().decode("utf-8")
t_new = t.replace(
    "// GA4 + conversion events. GA only loads after the visitor accepts \"Statistics\" in the\n// Complianz cookie banner.",
    "// GA4 + conversion events. GA only loads after the visitor clicks \"Accept\" in the cookie banner\n// (assets/js/avicon-consent.js).")
t_new = t_new.replace(
    "  function hasConsent() {\n"
    "    if (typeof window.cmplz_has_consent === 'function') return window.cmplz_has_consent('statistics');\n"
    "    return /(?:^|;\\s*)cmplz_statistics=allow/.test(document.cookie);\n"
    "  }",
    "  function hasConsent() {\n"
    "    if (window.aviconConsent) return window.aviconConsent.granted();\n"
    "    return /(?:^|;\\s*)avicon_consent=granted/.test(document.cookie) || /(?:^|;\\s*)cmplz_statistics=allow/.test(document.cookie);\n"
    "  }")
t_new = t_new.replace(
    "  document.addEventListener('cmplz_enable_category', loadGA);\n  document.addEventListener('cmplz_status_change', loadGA);\n",
    "  document.addEventListener('avicon:consent', loadGA);\n")
if 'src="/assets/js/avicon-consent.js' not in t_new:
    t_new = t_new.replace("?>", '?>\n<script src="/assets/js/avicon-consent.js?v=1" defer></script>', 1)
if t_new != t:
    changed["includes/tracking.php"] = {"consent": 1}
    if not dry:
        tracking.write_bytes(t_new.encode("utf-8"))

src_img = ROOT / "assets/plugins/complianz-gdpr/assets/images/placeholders/google-maps-minimal-1280x920.jpg"
dst_img = ROOT / "assets/images/map-placeholder.jpg"
if not dst_img.exists() and not dry:
    dst_img.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src_img, dst_img)

print(f"{'would change' if dry else 'changed'} {len(changed)} files")
totals = {}
for counts in changed.values():
    for k, v in counts.items():
        totals[k] = totals.get(k, 0) + v
print("totals:", totals)
left = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*.php")
        if p.relative_to(ROOT).parts[0] not in SKIP and re.search(r"cmplz-cookiebanner|complianz\.min\.js|data-src-cmplz", p.read_text(encoding="utf-8", errors="ignore"))]
print("pages still carrying the Complianz banner/scripts:", left or "none")
