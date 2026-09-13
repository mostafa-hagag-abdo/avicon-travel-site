"""Structured data for the product pages (packages, Nile cruises, day tours).

One JSON-LD graph per product page, built only from what the page itself shows:
Organization + WebSite + WebPage + BreadcrumbList + TouristTrip (itinerary + Offer)
+ FAQPage when the page has an FAQ tab. The Offer takes the visible "Starting Price"
of the booking box, so the markup never disagrees with the page; "on request"
products get no Offer.

Idempotent - re-run after any price / itinerary / FAQ edit:
    python _dev/schema_products.py            # write
    python _dev/schema_products.py --check    # report only, also flags price mismatches
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://avicontravel.com"
ORG_ID, SITE_ID = DOMAIN + "/#organization", DOMAIN + "/#website"
LOGO = "/assets/uploads/2026/05/cropped-cropped-Avicon-Travel-1-1.png.webp"
SAME_AS = ["https://www.instagram.com/avicontravel/",
           "https://www.facebook.com/profile.php?id=61589341120733",
           "https://www.tripadvisor.com/Attraction_Review-g294204-d27707479-Reviews-Avicon_Travel-Aswan_Aswan_Governorate_Nile_River_Valley.html"]
HUBS = {"packages": "Egypt Packages", "nile-cruises": "Egypt Nile Cruises", "tours": "Day Tours"}
# pages whose price is being confirmed with the client: no Offer until it is settled
PRICE_UNDER_REVIEW = set()
TAG = re.compile(r'<script type="application/ld\+json" id="avicon-schema">.*?</script>\r?\n?', re.S)


def text(s):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or ""))).strip()


def grab(rx, s):
    m = re.search(rx, s, re.S | re.I)
    return text(m.group(1)) if m else None


def amount(s):
    m = re.search(r"\$\s?([\d,]+)", s or "")
    return int(m.group(1).replace(",", "")) if m else None


def end_of_div(s, start):
    """Index just past the </div> that closes the <div> starting at `start`."""
    depth = 0
    for m in re.finditer(r"<div\b|</div>", s[start:]):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            return start + m.end()
    raise ValueError("unbalanced <div>")


def faq_pairs(s):
    """Question/answer pairs from the page's FAQ tab (id="faq"), as shown to visitors."""
    i = s.find('id="faq"')
    if i < 0:
        return []
    start = s.rfind("<div", 0, i)
    block = s[start:end_of_div(s, start)]
    return [(text(q), text(a)) for q, a in
            re.findall(r'<div class="day-title"[^>]*>(.*?)</div>.*?<div class="day-content">(.*?)</div>', block, re.S)]


def product(url, s):
    head = s[:s.find("</head>")]
    visible = grab(r'summary-row total"><span>[^<]*</span><span>(.*?)</span>', s)
    hidden = grab(r'id="totalInput" value="([^"]*)"', s)
    return {
        "url": url,
        "name": grab(r"<h1[^>]*>(.*?)</h1>", s),
        "title": re.sub(r"\s*[-|]\s*Avicon Travel\s*$", "", grab(r"<title>(.*?)</title>", head) or ""),
        "description": grab(r'<meta name="description" content="([^"]*)"', head),
        "canonical": grab(r'<link rel="canonical" href="([^"]*)"', head) or DOMAIN + url,
        "image": grab(r'<meta property="og:image" content="([^"]*)"', head),
        "price": amount(visible),
        "price_text": visible or hidden,
        "hidden_price": amount(hidden),
        "itinerary": [text(d) for d in re.findall(r'<div class="day-title">(.*?)</div>', s, re.S)],
        "faq": faq_pairs(s),
    }


def graph(p):
    canon = p["canonical"]
    section = p["url"].strip("/").split("/")[0]
    trip = {
        "@type": "TouristTrip", "@id": canon + "#trip", "name": p["name"] or p["title"],
        "description": p["description"], "url": canon, "image": p["image"],
        "provider": {"@id": ORG_ID},
    }
    if p["itinerary"]:
        trip["itinerary"] = {"@type": "ItemList", "numberOfItems": len(p["itinerary"]),
                             "itemListElement": [{"@type": "ListItem", "position": i, "name": d}
                                                 for i, d in enumerate(p["itinerary"], 1)]}
    if p["price"] and p["url"] not in PRICE_UNDER_REVIEW:
        trip["offers"] = {"@type": "Offer", "price": str(p["price"]), "priceCurrency": "USD",
                          "availability": "https://schema.org/InStock", "url": canon,
                          "description": "Starting price per person", "seller": {"@id": ORG_ID}}
    nodes = [
        {"@type": "Organization", "@id": ORG_ID, "name": "Avicon Travel", "url": DOMAIN + "/",
         "logo": {"@type": "ImageObject", "url": DOMAIN + LOGO}, "email": "info@avicontravel.com",
         "telephone": "+201200555600", "sameAs": SAME_AS},
        {"@type": "WebSite", "@id": SITE_ID, "url": DOMAIN + "/", "name": "Avicon Travel",
         "publisher": {"@id": ORG_ID}, "inLanguage": "en-US"},
        {"@type": "WebPage", "@id": canon + "#webpage", "url": canon, "name": p["title"],
         "description": p["description"], "isPartOf": {"@id": SITE_ID},
         "primaryImageOfPage": {"@type": "ImageObject", "url": p["image"]} if p["image"] else None,
         "breadcrumb": {"@id": canon + "#breadcrumb"}, "mainEntity": {"@id": canon + "#trip"},
         "inLanguage": "en-US"},
        {"@type": "BreadcrumbList", "@id": canon + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
            {"@type": "ListItem", "position": 2, "name": HUBS[section], "item": f"{DOMAIN}/{section}/"},
            {"@type": "ListItem", "position": 3, "name": p["name"] or p["title"], "item": canon}]},
        trip,
    ]
    if p["faq"]:
        nodes.append({"@type": "FAQPage", "@id": canon + "#faq", "isPartOf": {"@id": canon + "#webpage"},
                      "mainEntity": [{"@type": "Question", "name": q,
                                      "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]})
    prune = lambda d: {k: prune(v) if isinstance(v, dict) else v for k, v in d.items() if v not in (None, "", [])}
    return {"@context": "https://schema.org", "@graph": [prune(n) for n in nodes]}


def main(check):
    if not (ROOT / LOGO.lstrip("/")).exists():
        sys.exit(f"logo not found: {LOGO}")
    done, issues, faqs = 0, [], 0
    for section in HUBS:
        for f in sorted((ROOT / section).glob("*/index.php")):
            s = open(f, encoding="utf-8", newline="").read()
            if s.startswith("<?php header('Location:"):
                continue
            url = f"/{section}/{f.parent.name}/"
            p = product(url, s)
            if not p["name"]:
                issues.append(f"{url}: no <h1>")
            if not p["image"]:
                issues.append(f"{url}: no og:image")
            if p["price"] and p["hidden_price"] and p["price"] != p["hidden_price"]:
                issues.append(f"{url}: visible ${p['price']} but booking form sends ${p['hidden_price']}")
            faqs += bool(p["faq"])
            print(f"{url[:64]:64} {('$' + str(p['price'])) if p['price'] else 'on request':>10}  itinerary:{len(p['itinerary'])}  faq:{len(p['faq'])}")
            nl = "\r\n" if "\r\n" in s else "\n"
            tag = ('<script type="application/ld+json" id="avicon-schema">'
                   + json.dumps(graph(p), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
                   + "</script>" + nl)
            new = TAG.sub("", s).replace("</head>", tag + "</head>", 1)
            if not check and new != s:
                open(f, "w", encoding="utf-8", newline="").write(new)
            done += 1
    print(f"\n{done} product pages {'checked' if check else 'written'}; with FAQPage: {faqs}")
    for i in issues:
        print("  !", i)


if __name__ == "__main__":
    main("--check" in sys.argv)
