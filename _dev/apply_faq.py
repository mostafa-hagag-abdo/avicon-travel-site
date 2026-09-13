"""Add an FAQ tab to product pages from _dev/product_faq.json.

The tab and panel reuse the markup the day-tour pages already use for their FAQ
(.tab / .tab-panel / .day-item accordion), so each page's own script switches and
opens them - no new CSS or JS. Pages that already have an FAQ tab are left alone.
Run schema_products.py afterwards so the FAQPage markup picks the questions up.

    python _dev/apply_faq.py            # dry run
    python _dev/apply_faq.py --apply
"""
import html, json, re, sys
from pathlib import Path

from schema_products import ROOT, end_of_div

FAQ = json.load(open(Path(__file__).with_name("product_faq.json"), encoding="utf-8"))
TAB = '<div class="tab" data-tab="faq"><i class="fas fa-circle-question"></i> FAQ</div>'
INC_TAB = re.compile(r'<div class="tab[^"]*" data-tab="inclusions">.*?</div>', re.S)
INC_PANEL = re.compile(r'<div class="tab-panel[^"]*" id="inclusions">')


def clean(t):
    return html.escape(t.replace(" - ", " — "), quote=False)


def panel(faq, nl, ind):
    items = [f'{ind}    <div class="day-item{" open" if i == 0 else ""}"><div class="day-header" style="cursor:pointer">'
             f'<div class="day-title" style="font-size:14px">{clean(q)}</div><i class="fas fa-chevron-down day-toggle"></i></div>'
             f'<div class="day-content"><p>{clean(a)}</p></div></div>' for i, (q, a) in enumerate(faq)]
    return nl.join(["", f'{ind}<div class="tab-panel" id="faq">',
                    f'{ind}  <h2 class="section-title">Frequently Asked Questions</h2>',
                    f'{ind}  <p class="section-sub">Quick answers about this trip. For anything else, message us on WhatsApp — we reply fast.</p>',
                    f'{ind}  <div class="timeline">', *items, f'{ind}  </div>', f'{ind}</div>'])


def main(apply):
    done, skipped, problems = [], [], []
    for url, rec in FAQ.items():
        f = ROOT / url.strip("/") / "index.php"
        s = open(f, encoding="utf-8", newline="").read()
        if 'id="faq"' in s:
            skipped.append(url)
            continue
        tabs, panels = INC_TAB.findall(s), list(INC_PANEL.finditer(s))
        if len(tabs) != 1 or len(panels) != 1:
            problems.append(f"{url}: inclusions tab x{len(tabs)}, panel x{len(panels)}")
            continue
        nl = "\r\n" if "\r\n" in s else "\n"
        start = panels[0].start()
        ind = s[s.rfind("\n", 0, start) + 1:start]
        end = end_of_div(s, start)
        new = s[:end] + panel(rec["faq"], nl, ind if not ind.strip() else "") + s[end:]
        new = new.replace(tabs[0], tabs[0] + TAB, 1)
        if new.count('id="faq"') != 1 or new.count('data-tab="faq"') != 1:
            problems.append(f"{url}: faq inserted wrongly")
            continue
        done.append((f, new, len(rec["faq"])))
    print(f"FAQ tab to add: {len(done)} pages, {sum(n for *_, n in done)} questions; already had one: {len(skipped)}")
    for pr in problems:
        print("  !", pr)
    if apply and not problems:
        for f, new, _ in done:
            open(f, "w", encoding="utf-8", newline="").write(new)
        print("written")
    else:
        print("dry run - nothing written" if not problems else "NOT written")


if __name__ == "__main__":
    main("--apply" in sys.argv)
