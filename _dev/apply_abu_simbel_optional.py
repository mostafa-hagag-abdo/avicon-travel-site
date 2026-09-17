"""Abu Simbel is an optional extra on the two "Include Abu Simbel" cruises (owner, 2026-09-17).

The two cruise pages said the Abu Simbel excursion was part of the package. The owner confirmed it is an
optional extra from $90 per person, and that travelers who skip it have a free morning on board. This
rewrites the visible copy that claimed otherwise:

  - both cruise pages: product name, hero badge, breadcrumb, H1, intro, route stop, highlight card,
    the Abu Simbel day, the Included / Excluded lists and their item counts
  - the product name wherever else it appears (cards on the home page, /nile-cruises/, /packages/,
    related cards on other cruise pages, image alts, the booking form's hidden fields)
  - the card descriptions on the three listing pages, the /search/ index and llms.txt
  - one copy-paste error on the 4-night page: its itinerary blurb described a 4-day Aswan-to-Luxor trip

Texts in _dev/product_meta.json, product_facts.json, product_faq.json and product_longform.json are
applied by their own tools, and the Sun Festival article by new_article.py. Run afterwards:

    python _dev/apply_abu_simbel_optional.py
    python _dev/product_meta.py && python _dev/apply_facts.py && python _dev/apply_faq.py
    python _dev/apply_longform.py && python _dev/new_article.py _dev/articles/abu-simbel-sun-festival-2026.json
    python _dev/schema_products.py && python _dev/schema_blog_faq.py && python _dev/health_check.py --local

Re-runnable: an edit that is already in place is skipped.
"""
import sys

P3 = 'nile-cruises/3-nights-nile-cruise-from-aswan-including-abu-simbel/index.php'
P4 = 'nile-cruises/4-nights-nile-cruise-from-luxor-including-abu-simbel/index.php'
HUBS = ['index.php', 'nile-cruises/index.php', 'packages/index.php']

NAMES = [
    ('3 Nights Nile River Cruise from Aswan Include Abu Simbel',
     '3 Nights Nile River Cruise from Aswan with Optional Abu Simbel'),
    ('4 Nights Nile River Cruise from Luxor Include Abu Simbel',
     '4 Nights Nile River Cruise from Luxor with Optional Abu Simbel'),
    # /search/ index uses slightly different titles
    ('3 Nights Nile Cruise from Aswan Including Abu Simbel',
     '3 Nights Nile Cruise from Aswan with Optional Abu Simbel'),
    ('4 Nights Nile Cruise from Luxor Including Abu Simbel',
     '4 Nights Nile Cruise from Luxor with Optional Abu Simbel'),
]

ITEM = ('<div class="ticket-item"><div class="ticket-item-icon"><i class="fas fa-%s"></i></div>'
        '<div class="ticket-item-text">%s</div></div>')
EXTRA = ITEM % ('xmark', 'Abu Simbel excursion - optional, from $90 per person')

EDITS = [
    # ---------------- 3-night cruise from Aswan ----------------
    (P3, '<div class="bk-badge"><i class="fas fa-star"></i> Nile Cruise with Abu Simbel</div>',
         '<div class="bk-badge"><i class="fas fa-star"></i> Nile Cruise with Optional Abu Simbel</div>'),
    (P3, 'Enjoy a 3-night Nile cruise from Aswan to Luxor including Abu Simbel, combining Aswan sightseeing, '
         'the great rock-cut temples of Ramses II, Kom Ombo, Edfu, and the major monuments of Luxor in one '
         'compact Upper Egypt journey.',
         'Enjoy a 3-night Nile cruise from Aswan to Luxor combining Aswan sightseeing, Kom Ombo, Edfu, and the '
         'major monuments of Luxor in one compact Upper Egypt journey. The great rock-cut temples of Abu Simbel '
         'can be added as an optional excursion from $90 per person.'),
    (P3, '<div class="route-stop-name">Abu Simbel</div><div class="route-stop-num">Stop 2</div>',
         '<div class="route-stop-name">Abu Simbel (optional)</div><div class="route-stop-num">Stop 2</div>'),
    (P3, '<div class="fact-label">Abu Simbel</div><div class="fact-value">Ramses II Temples</div>',
         '<div class="fact-label">Abu Simbel</div><div class="fact-value">Ramses II (optional)</div>'),
    (P3, '<span>Day 2</span> Abu Simbel Temples & Sail to Kom Ombo',
         '<span>Day 2</span> Sail to Kom Ombo (Abu Simbel optional)'),
    (P3, '<p>Start early with breakfast boxes, then travel by private air-conditioned vehicle to Abu Simbel to '
         'explore the colossal temples of Ramses II and Queen Nefertari. Return to the cruise for lunch and '
         'dinner while sailing. Meals: breakfast, lunch, and dinner.</p>',
         '<p>Optional extra, from $90 per person: start early with breakfast boxes, then travel by private '
         'air-conditioned vehicle to Abu Simbel to explore the colossal temples of Ramses II and Queen '
         'Nefertari, and return to the cruise for lunch. If you skip it, you have a free morning on board in '
         'Aswan. The ship then sails on towards Kom Ombo, with lunch and dinner served on board. Meals: '
         'breakfast, lunch, and dinner.</p>'),
    (P3, '<div class="stub-label">Included</div><div class="stub-count">8 ITEMS</div>',
         '<div class="stub-label">Included</div><div class="stub-count">7 ITEMS</div>'),
    (P3, ITEM % ('check', 'Abu Simbel excursion by private air-conditioned vehicle'), ''),
    (P3, '<div class="stub-label">Excluded</div><div class="stub-count">3 ITEMS</div>',
         '<div class="stub-label">Excluded</div><div class="stub-count">4 ITEMS</div>'),
    (P3, ITEM % ('xmark', 'Any extras not mentioned in the program'),
         EXTRA + '\n                    ' + ITEM % ('xmark', 'Any extras not mentioned in the program')),

    # ---------------- 4-night cruise from Luxor ----------------
    (P4, '<div class="bk-badge"><i class="fas fa-star"></i> Nile Cruise with Abu Simbel</div>',
         '<div class="bk-badge"><i class="fas fa-star"></i> Nile Cruise with Optional Abu Simbel</div>'),
    (P4, 'Take a 4-night Nile cruise from Luxor to Aswan including Abu Simbel, combining Luxor East and West '
         'Bank sightseeing, Edfu, Kom Ombo, the colossal temples of Abu Simbel, and Aswan highlights in one '
         'full-board cruise journey.',
         'Take a 4-night Nile cruise from Luxor to Aswan combining Luxor East and West Bank sightseeing, Edfu, '
         'Kom Ombo, and Aswan highlights in one full-board cruise journey. The colossal temples of Abu Simbel '
         'can be added as an optional excursion from $90 per person.'),
    (P4, '<div class="route-stop-name">Abu Simbel</div><div class="route-stop-num">Stop 4</div>',
         '<div class="route-stop-name">Abu Simbel (optional)</div><div class="route-stop-num">Stop 4</div>'),
    (P4, '<div class="fact-label">Abu Simbel</div><div class="fact-value">Ramses II Temples</div>',
         '<div class="fact-label">Abu Simbel</div><div class="fact-value">Ramses II (optional)</div>'),
    (P4, '<span>Day 4</span> Abu Simbel Temples',
         '<span>Day 4</span> Abu Simbel Temples (optional)'),
    (P4, '<p>Start early with breakfast boxes and travel by modern air-conditioned vehicle to Abu Simbel. Visit '
         'the two great rock-cut temples of Ramses II and Queen Nefertari, then return to the cruise for lunch '
         'and overnight. Meals: breakfast, lunch, and dinner.</p>',
         '<p>Optional extra, from $90 per person: start early with breakfast boxes and travel by modern '
         'air-conditioned vehicle to Abu Simbel, visit the two great rock-cut temples of Ramses II and Queen '
         'Nefertari, then return to the cruise for lunch and overnight. If you skip it, you have a free morning '
         'on board in Aswan. Meals: breakfast, lunch, and dinner.</p>'),
    (P4, ITEM % ('check', 'Nile cruise excursions and Abu Simbel trip as mentioned in the itinerary'),
         ITEM % ('check', 'Nile cruise excursions as mentioned in the itinerary')),
    (P4, '<div class="stub-label">Excluded</div><div class="stub-count">3 ITEMS</div>',
         '<div class="stub-label">Excluded</div><div class="stub-count">4 ITEMS</div>'),
    (P4, ITEM % ('xmark', 'Any extras not mentioned in the program'),
         EXTRA + '\n                    ' + ITEM % ('xmark', 'Any extras not mentioned in the program')),
    # copy-paste leftover: this is a 5-day Luxor-to-Aswan cruise
    (P4, 'A compact 4-day Nile program from Aswan to Luxor with guided temple visits, onboard meals, and cruise '
         'accommodation.',
         'A 5-day Nile program from Luxor to Aswan with guided temple visits, onboard meals, and cruise '
         'accommodation.'),

    # ---------------- card descriptions on the listing pages ----------------
    ('index.php', 'Classic Aswan to Luxor Nile cruise with Abu Simbel, Kom Ombo, Edfu, and Luxor highlights.',
                  'Classic Aswan to Luxor Nile cruise with Kom Ombo, Edfu, and Luxor highlights, plus optional Abu Simbel.'),
    ('index.php', 'Luxor to Aswan cruise package with temples, West Bank sightseeing, and Abu Simbel included.',
                  'Luxor to Aswan cruise package with temples, West Bank sightseeing, and optional Abu Simbel.'),
    ('nile-cruises/index.php', 'Classic Aswan to Luxor Nile cruise with Abu Simbel, Kom Ombo, Edfu, and Luxor highlights.',
                               'Classic Aswan to Luxor Nile cruise with Kom Ombo, Edfu, and Luxor highlights, plus optional Abu Simbel.'),
    ('nile-cruises/index.php', 'Luxor to Aswan Nile cruise with temples, West Bank sightseeing, and Abu Simbel included.',
                               'Luxor to Aswan Nile cruise with temples, West Bank sightseeing, and optional Abu Simbel.'),
    ('packages/index.php', 'Classic Aswan to Luxor Nile cruise package with Abu Simbel, Kom Ombo, Edfu, and Luxor highlights.',
                           'Classic Aswan to Luxor Nile cruise package with Kom Ombo, Edfu, and Luxor highlights, plus optional Abu Simbel.'),
    ('packages/index.php', 'Luxor to Aswan Nile cruise package with temples, West Bank sightseeing, and Abu Simbel included.',
                           'Luxor to Aswan Nile cruise package with temples, West Bank sightseeing, and optional Abu Simbel.'),

    # ---------------- /search/ index snippets ----------------
    ('search/index.php',
     'Enjoy a 3-night Nile cruise from Aswan to Luxor including Abu Simbel, combining Aswan sightseeing, the great rock-cut temples of Ramses II, Kom Ombo, Edfu,',
     'Enjoy a 3-night Nile cruise from Aswan to Luxor combining Aswan sightseeing, Kom Ombo, Edfu, and the major monuments of Luxor. Abu Simbel is optional,'),
    ('search/index.php',
     'Take a 4-night Nile cruise from Luxor to Aswan including Abu Simbel, combining Luxor East and West Bank sightseeing, Edfu, Kom Ombo, the colossal temples of',
     'Take a 4-night Nile cruise from Luxor to Aswan combining Luxor East and West Bank sightseeing, Edfu, Kom Ombo, and Aswan highlights. Abu Simbel is optional,'),

    # ---------------- llms.txt ----------------
    ('llms.txt', 'from $500 per person. Classic Aswan to Luxor Nile cruise package with Abu Simbel, Kom Ombo, Edfu, and Luxor highlights.',
                 'from $500 per person. Classic Aswan to Luxor Nile cruise package with Kom Ombo, Edfu and Luxor highlights; Abu Simbel optional from $90.'),
    ('llms.txt', 'from $560 per person. Luxor to Aswan Nile cruise package with temples, West Bank sightseeing, and Abu Simbel included.',
                 'from $560 per person. Luxor to Aswan Nile cruise package with temples and West Bank sightseeing; Abu Simbel optional from $90.'),
]

FILES_FOR_NAMES = [P3, P4, 'index.php', 'nile-cruises/index.php', 'packages/index.php', 'search/index.php',
                   'llms.txt', 'blog/abu-simbel-sun-festival-2026/index.php',
                   'nile-cruises/4-days-dahabiya-nile-cruise-from-aswan-to-luxor/index.php',
                   'nile-cruises/4-days-off-the-beaten-path-nile-river-cruise-for-repeat-visitors/index.php',
                   'nile-cruises/5-days-dahabiya-nile-cruise-from-luxor-to-aswan/index.php',
                   'nile-cruises/5-days-hidden-treasures-nile-cruise-for-returning-visitors/index.php',
                   'nile-cruises/5-days-nile-river-cruise-from-luxor-to-aswan/index.php']


def main(check):
    texts, changed = {}, 0

    def load(f):
        if f not in texts:
            texts[f] = open(f, 'rb').read().decode('utf-8')
        return texts[f]

    for f, old, new in EDITS:
        s = load(f)
        if old not in s and (new in s if new else True):
            print('  = already done:', f, '|', (old[:60] if old else ''))
            continue
        n = s.count(old)
        if n != 1:
            print('::error:: %s occurrences in %s for %r' % (n, f, old[:70]))
            return 1
        texts[f] = s.replace(old, new)
        changed += 1

    for f in FILES_FOR_NAMES:
        s = load(f)
        for old, new in NAMES:
            if old in s:
                texts[f] = texts[f].replace(old, new)
                changed += 1

    for f, s in sorted(texts.items()):
        cur = open(f, 'rb').read().decode('utf-8')
        if s != cur:
            print('%s %s' % ('would write' if check else 'wrote', f))
            if not check:
                open(f, 'wb').write(s.encode('utf-8'))
    print('%d edits' % changed)
    return 0


if __name__ == '__main__':
    sys.exit(main('--check' in sys.argv))
