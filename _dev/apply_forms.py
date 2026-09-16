"""Point every website form at the Supabase Edge Function instead of Web3Forms.

    python _dev/apply_forms.py https://<project-ref>.supabase.co/functions/v1/<function-name> [--dry-run]

The live function is https://tdpsvcsniftrgnrdyhgi.supabase.co/functions/v1/smooth-worker (source:
_dev/supabase/functions/submit-request/index.ts; Supabase auto-named it smooth-worker when it was deployed).

- replaces the Web3Forms URL (form actions and fetch() calls) with the function URL
- removes the Web3Forms-only hidden inputs (access_key, from_name, redirect)
- adds <input type="hidden" name="form_type" value="..."> to each form: booking, contact, tailor_made, transfer
- updates includes/tracking.php so the GA4 generate_lead event still fires for the new endpoint
Re-runnable: a later run with another function URL swaps the old one. Search forms are left alone.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"_dev", ".git", ".github", "database", "avicontravel-backup", "node_modules"}
OLD_URL = re.compile(r"https://api\.web3forms\.com/submit|https://[a-z0-9]+\.supabase\.co/functions/v1/[a-z0-9_-]+")
HIDDEN = re.compile(r'[ \t]*<input type="hidden" name="(?:access_key|from_name|redirect)"[^>]*>[ \t]*(?:\r?\n)?')
FORM_TAG = re.compile(r"<form\b[^>]*>", re.S)

args = [a for a in sys.argv[1:] if not a.startswith("--")]
dry = "--dry-run" in sys.argv
if len(args) != 1 or not re.fullmatch(r"https://[a-z0-9]+\.supabase\.co/functions/v1/[a-z0-9_-]+", args[0]):
    sys.exit(__doc__)
ENDPOINT = args[0]


def form_type(tag, path):
    if "search" in tag:
        return None
    if 'id="bookingForm"' in tag:
        return "booking"
    if 'id="contactForm"' in tag:
        return "contact"
    if "avi-tm__form" in tag:
        return "tailor_made"
    if 'id="transferForm"' in tag or "car-transportation" in path.as_posix():
        return "transfer"
    return "unknown"


changed, forms, unknown = [], {}, []
for p in sorted(ROOT.rglob("*.php")):
    if p.relative_to(ROOT).parts[0] in SKIP:
        continue
    s = p.read_bytes().decode("utf-8")
    new = s
    if p.as_posix().endswith("includes/tracking.php"):
        new = new.replace(r"/api\.web3forms\.com/", r"/supabase\.co\/functions\/v1\//")
        new = new.replace("/web3forms/.test(", r"/supabase\.co\/functions\/v1\//.test(")
        new = new.replace("transfer forms post straight to Web3Forms", "transfer forms post straight to the form endpoint")
    if OLD_URL.search(new) or "form_type" in new:
        new = OLD_URL.sub(ENDPOINT, new)
        new = HIDDEN.sub("", new)
        out, pos = [], 0
        for m in FORM_TAG.finditer(new):
            kind = form_type(m.group(0), p.relative_to(ROOT))
            out.append(new[pos:m.end()])
            pos = m.end()
            if kind is None:
                continue
            if kind == "unknown":
                unknown.append(f"{p.relative_to(ROOT)}: {m.group(0)[:80]}")
                continue
            forms[kind] = forms.get(kind, 0) + 1
            if 'name="form_type"' in new[m.end():m.end() + 400]:
                continue
            line_start = new.rfind("\n", 0, m.start()) + 1
            indent = re.match(r"[ \t]*", new[line_start:]).group(0) + "  "
            nl = "\r\n" if "\r\n" in new else "\n"
            out.append(f'{nl}{indent}<input type="hidden" name="form_type" value="{kind}">')
        out.append(new[pos:])
        new = "".join(out)
    if new != s:
        changed.append(p.relative_to(ROOT).as_posix())
        if not dry:
            p.write_bytes(new.encode("utf-8"))

print(f"{'would change' if dry else 'changed'} {len(changed)} files; forms: {forms}")
if unknown:
    print("UNKNOWN forms (left without form_type):", *unknown, sep="\n  ")
if not dry:
    left = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*")
            if p.is_file() and p.suffix in {".php", ".js", ".html"} and p.relative_to(ROOT).parts[0] not in SKIP
            and "web3forms" in p.read_text(encoding="utf-8", errors="ignore").lower()]
    print("files still mentioning web3forms:", left or "none")
