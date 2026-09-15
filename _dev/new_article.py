"""Scaffold a new /blog/ article with the same structure as the existing 12: full head (meta, Open Graph,
Twitter Card, JSON-LD Organization/WebSite/WebPage/BreadcrumbList/BlogPosting), hero image, article body,
a "You May Also Like" related-cards section, and a root-level 301 stub. Also wires the article into
sitemap.xml, the /blog/ listing grid and llms.txt.

Clones an existing article (DONOR below) and only rewrites what differs -- header/footer/scripts/cookie
banner stay byte-identical to whatever the donor currently has, so any future shared-shell edit keeps
applying the next time this is run against a fresh donor. A few WordPress/Elementor internals (the
elementor-post-* CSS ids, the "post" JS config object) are cosmetic leftovers that don't need to be
unique per page and are left untouched; the body postid-NNNNN class and the gtranslate widget's
data-gt-orig-url ARE rewritten since the second one is a real link the widget uses.

Spec file (_dev/articles/<slug>.json):
    {
      "slug": "abu-simbel-sun-festival-2026",
      "title": "...",                     <title>, og:title, twitter:title, <h1>
      "meta_description": "...",          50-160 chars; used for description/og:description/twitter:description
      "category": "Destination Guides",   breadcrumb + card label; any text works, doesn't need to match an
                                           existing one
      "published": "2026-09-16",          YYYY-MM-DD
      "modified": "2026-09-16",           optional, defaults to "published"
      "read_minutes": 7,
      "keywords": "Abu Simbel sun festival",   optional, short phrase for the BlogPosting schema node
      "image": {
        "path": "/assets/uploads/2026/09/Abu-Simbel-Sun-Festival.png",   the ORIGINAL upload; must already
                                                                          exist on disk. Left as-is in <img
                                                                          src>, og:image and JSON-LD, same as
                                                                          a freshly written page -- run
                                                                          optimize_images.py afterward to get
                                                                          the .webp sibling and lazy-loading
        "width": 1448, "height": 1086, "alt": "..."
      },
      "body_html": "...full inner HTML of <article class=\"avp-body\">...",
      "related": ["slug-a", "slug-b", "slug-c"]   1-3 existing /blog/ slugs; their title, image, category,
                                                    published date and read time are read live off their own
                                                    pages, so they can't go stale
    }

    python _dev/new_article.py _dev/articles/<slug>.json           # write
    python _dev/new_article.py _dev/articles/<slug>.json --check   # validate only, write nothing

After writing: run schema_blog_faq.py if body_html has a visible FAQ section, optimize_images.py for the
new hero image, then health_check.py.
"""
import html, json, re, sys, zlib
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"
DONOR = BLOG / "aswan-egypt-guide-temples-nubian-villages-sunsets" / "index.php"
SITE = "https://avicontravel.com"
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
check = "--check" in sys.argv


def esc(s):
    return html.escape(s, quote=True)


def parse_date(s, field):
    try:
        y, m, d = (int(x) for x in s.split("-"))
        return date(y, m, d)
    except Exception:
        sys.exit(f"bad {field}: {s!r} (want YYYY-MM-DD)")


def display_full(d):
    return f"{d.day} {d:%B} {d.year}"


def display_short(d):
    return f"{d.day} {d.strftime('%B')[:3]}, {d.year}"


def iso(d):
    return f"{d.isoformat()}T12:00:00+00:00"


def load_spec(path):
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    for field in ("slug", "title", "meta_description", "category", "published", "read_minutes", "image", "body_html", "related"):
        if field not in spec:
            sys.exit(f"spec missing '{field}'")
    if not SLUG_RE.match(spec["slug"]):
        sys.exit(f"bad slug: {spec['slug']!r} (lowercase letters, digits, hyphens)")
    if not 50 <= len(spec["meta_description"]) <= 160:
        sys.exit(f"meta_description is {len(spec['meta_description'])} chars (want 50-160)")
    if not 1 <= len(spec["related"]) <= 3:
        sys.exit("related must list 1-3 slugs")
    img = spec["image"]
    for field in ("path", "width", "height", "alt"):
        if field not in img:
            sys.exit(f"image missing '{field}'")
    if not (ROOT / img["path"].lstrip("/")).is_file():
        sys.exit(f"image not found on disk: {img['path']} (upload it first)")
    if "<article" in spec["body_html"] or "</html" in spec["body_html"]:
        sys.exit("body_html must be the INNER content of <article class=\"avp-body\">, not the whole page")
    return spec


def article_summary(slug):
    path = BLOG / slug / "index.php"
    if not path.is_file():
        sys.exit(f"related slug not found under /blog/: {slug}")
    s = path.read_bytes().decode("utf-8")
    h1 = re.search(r"<h1>(.*?)</h1>", s, re.S)
    badge = re.search(r'<div class="avp-badge"><i[^>]*></i>\s*(.*?)</div>', s, re.S)
    fig = re.search(r'<figure class="avp-figure">(<img\b[^>]*>)', s)
    date_span = re.search(r'fa-calendar"></i>\s*([^<]+)</span>', s)
    read_span = re.search(r'fa-clock"></i>\s*(\d+)\s*min', s)
    if not (h1 and badge and fig and date_span and read_span):
        sys.exit(f"couldn't read summary off /blog/{slug}/ (unexpected markup)")
    img_tag = fig.group(1)
    src = re.search(r'src="([^"]+)"', img_tag).group(1)
    alt = re.search(r'alt="([^"]*)"', img_tag)
    w = re.search(r'width="(\d+)"', img_tag)
    h = re.search(r'height="(\d+)"', img_tag)
    return {
        "slug": slug, "title": html.unescape(h1.group(1)).strip(), "category": badge.group(1).strip(),
        "src": src, "alt": html.unescape(alt.group(1)) if alt else "",
        "width": w.group(1) if w else "1448", "height": h.group(1) if h else "1086",
        "date": date_span.group(1).strip(), "read": read_span.group(1),
    }


def build_head_block(spec, canon, img_url, pub_iso, mod_iso):
    title, desc = spec["title"], spec["meta_description"]
    return f"""<!-- Search Engine Optimization by Rank Math PRO - https://rankmath.com/ -->
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}"/>
<meta name="robots" content="index, follow, max-snippet:-1, max-video-preview:-1, max-image-preview:large"/>
<link rel="canonical" href="{canon}" />
<meta property="og:locale" content="en_US" />
<meta property="og:type" content="article" />
<meta property="og:title" content="{esc(title)}" />
<meta property="og:description" content="{esc(desc)}" />
<meta property="og:url" content="{canon}" />
<meta property="og:site_name" content="Avicon Travel" />
<meta property="article:section" content="{esc(spec['category'])}" />
<meta property="og:updated_time" content="{mod_iso}" />
<meta property="og:image" content="{img_url}" />
<meta property="og:image:secure_url" content="{img_url}" />
<meta property="og:image:width" content="{spec['image']['width']}" />
<meta property="og:image:height" content="{spec['image']['height']}" />
<meta property="og:image:alt" content="{esc(spec['image']['alt'])}" />
<meta property="og:image:type" content="image/png" />
<meta property="article:published_time" content="{pub_iso}" />
<meta property="article:modified_time" content="{mod_iso}" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{esc(title)}" />
<meta name="twitter:description" content="{esc(desc)}" />
<meta name="twitter:image" content="{img_url}" />
<meta name="twitter:label1" content="Written by" />
<meta name="twitter:data1" content="avicontravel@gmail.com" />
<meta name="twitter:label2" content="Time to read" />
<meta name="twitter:data2" content="{spec['read_minutes']} minutes" />

<!-- /Rank Math WordPress SEO plugin -->"""


def build_schema(spec, canon, img_url, pub_iso, mod_iso):
    title, desc = spec["title"], spec["meta_description"]
    blog_posting = {
        "@type": "BlogPosting", "@id": f"{canon}#article", "headline": title, "description": desc,
        "image": img_url, "datePublished": pub_iso, "dateModified": mod_iso,
        "articleSection": spec["category"],
    }
    if spec.get("keywords"):
        blog_posting["keywords"] = spec["keywords"]
    blog_posting.update({
        "author": {"@id": f"{SITE}/#organization"}, "publisher": {"@id": f"{SITE}/#organization"},
        "mainEntityOfPage": {"@id": f"{canon}#webpage"}, "inLanguage": "en-US",
    })
    graph = [
        {"@type": "Organization", "@id": f"{SITE}/#organization", "name": "Avicon Travel", "url": f"{SITE}/",
         "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/uploads/2026/05/cropped-Avicon-Travel-1-1.png.webp"},
         "email": "info@avicontravel.com", "telephone": "+201200555600",
         "sameAs": ["https://www.instagram.com/avicontravel/", "https://www.facebook.com/profile.php?id=61589341120733",
                    "https://www.tripadvisor.com/Attraction_Review-g294204-d27707479-Reviews-Avicon_Travel-Aswan_Aswan_Governorate_Nile_River_Valley.html"]},
        {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/", "name": "Avicon Travel",
         "publisher": {"@id": f"{SITE}/#organization"}, "inLanguage": "en-US"},
        {"@type": "WebPage", "@id": f"{canon}#webpage", "url": canon, "name": title, "description": desc,
         "isPartOf": {"@id": f"{SITE}/#website"}, "about": {"@id": f"{SITE}/#organization"},
         "primaryImageOfPage": {"@type": "ImageObject", "url": img_url},
         "datePublished": pub_iso, "dateModified": mod_iso,
         "breadcrumb": {"@id": f"{canon}#breadcrumb"}, "inLanguage": "en-US"},
        {"@type": "BreadcrumbList", "@id": f"{canon}#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": title, "item": canon}]},
        blog_posting,
    ]
    body = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    return body.replace("</", "<\\/")


def build_related_cards(related):
    cards = []
    for r in related:
        cards.append(
            f'      <a class="avp-rel-card" href="/blog/{r["slug"]}/">\n'
            f'        <div class="avp-rel-img"><span>{esc(r["category"])}</span>'
            f'<img width="{r["width"]}" height="{r["height"]}" loading="lazy" decoding="async" '
            f'src="{r["src"]}" alt="{esc(r["title"])}" onerror="this.style.display=\'none\'"></div>\n'
            f'        <div class="avp-rel-body">\n'
            f'          <h3>{esc(r["title"])}</h3>\n'
            f'          <div class="avp-rel-meta">Read Article <small>{r["date"]} · {r["read"]} min</small></div>\n'
            f'        </div>\n'
            f'      </a>'
        )
    return (
        '<div class="avp-related" style="background:#F4F8FC;margin-top:56px;padding:56px 20px 30px"><div class="avp-related-inner">\n'
        '    <h2>You May Also Like</h2>\n'
        '    <p class="sub">More guides and tips for your Egypt trip</p>\n'
        '    <div class="avp-rel-grid">\n' + "\n".join(cards) + "\n    </div>\n"
        "  </div></div>\n</section>"
    )


def build_blog_card(spec, slug, pub_display_short):
    img = spec["image"]
    return (
        '<div class="col-lg-4 col-md-6 wow animate fadeInDown" data-wow-delay="200ms" data-wow-duration="1500ms">\n'
        '                                <div class="blog-card2 three">\n'
        '                                    <div class="blog-img-wrap">\n'
        f'                                                                                    <a href="/blog/{slug}/" class="blog-img">\n'
        f'                                                <img loading="lazy" decoding="async" width="650" height="400" src="{img["path"]}" '
        f'class="attachment-card-thumb size-card-thumb wp-post-image" alt="{esc(img["alt"])}" />                                            </a>\n'
        '                                                                            </div>\n'
        '                                    <div class="blog-content">\n'
        f'                                                                                                                            {esc(spec["category"])}\n'
        f'                                                                                <h4><a href="/blog/{slug}/">{esc(spec["title"])}</a></h4>\n'
        '                                        <ul class="blog-meta">\n'
        f'                                            <li>{pub_display_short}</li>\n'
        f'                                                                                        <li>{spec["read_minutes"]} Min reads</li>\n'
        '                                        </ul>\n'
        '                                    </div>\n'
        '                                </div>\n'
        '                            </div>'
    )


def main():
    if len(sys.argv) < 2 or sys.argv[1].startswith("--"):
        sys.exit(__doc__.strip().splitlines()[-3])
    spec = load_spec(sys.argv[1])
    slug = spec["slug"]
    target = BLOG / slug / "index.php"
    if target.is_file():
        sys.exit(f"already exists: blog/{slug}/index.php")
    if not DONOR.is_file():
        sys.exit(f"donor article missing: {DONOR}")

    published = parse_date(spec["published"], "published")
    modified = parse_date(spec.get("modified", spec["published"]), "modified")
    canon = f"{SITE}/blog/{slug}/"
    img_url = f"{SITE}{spec['image']['path']}"
    pub_iso, mod_iso = iso(published), iso(modified)
    related = [article_summary(s) for s in spec["related"]]

    donor = DONOR.read_bytes().decode("utf-8")

    head_re = re.compile(
        r"<!-- Search Engine Optimization by Rank Math PRO - https://rankmath\.com/ -->.*?"
        r"<!-- /Rank Math WordPress SEO plugin -->", re.S)
    if not head_re.search(donor):
        sys.exit("donor: Rank Math head block not found")
    page = head_re.sub(lambda m: build_head_block(spec, canon, img_url, pub_iso, mod_iso), donor, count=1)

    schema_re = re.compile(r'(<script type="application/ld\+json" id="avicon-schema">).*?(</script>)', re.S)
    page = schema_re.sub(lambda m: m.group(1) + build_schema(spec, canon, img_url, pub_iso, mod_iso) + m.group(2), page, count=1)

    page = re.sub(r"postid-\d+", f"postid-{zlib.crc32(slug.encode()) % 90000 + 10000}", page, count=1)
    page = re.sub(r'data-gt-orig-url="[^"]*"', f'data-gt-orig-url="/blog/{slug}/"', page, count=1)

    head_section_re = re.compile(r'<header class="avp-head">.*?</figure>', re.S)
    if not head_section_re.search(page):
        sys.exit("donor: article header/figure block not found")
    img = spec["image"]
    new_header = (
        '<header class="avp-head">\n'
        f'    <nav class="avp-crumb"><a href="/">Home</a><span>›</span><a href="/blog/">Blog</a>'
        f'<span>›</span><a href="/blog/">{esc(spec["category"])}</a></nav>\n'
        f'    <div class="avp-badge"><i class="fas fa-folder-open"></i> {esc(spec["category"])}</div>\n'
        f'    <h1>{esc(spec["title"])}</h1>\n'
        '    <div class="avp-meta">\n'
        f'      <span><i class="fas fa-calendar"></i> {display_full(published)}</span>\n'
        + (f'      <span><i class="fas fa-rotate"></i> Updated {display_full(modified)}</span>\n' if modified != published else "")
        + f'      <span><i class="fas fa-clock"></i> {spec["read_minutes"]} min read</span>\n'
        '    </div>\n'
        '  </header>\n'
        f'  <figure class="avp-figure"><img width="{img["width"]}" height="{img["height"]}" decoding="async" '
        f'src="{img["path"]}" alt="{esc(spec["title"])}"></figure>'
    )
    page = head_section_re.sub(new_header, page, count=1)

    body_re = re.compile(r'(<article class="avp-body">).*?(</article>)', re.S)
    if not body_re.search(page):
        sys.exit("donor: <article class=\"avp-body\"> block not found")
    page = body_re.sub(lambda m: m.group(1) + spec["body_html"] + m.group(2), page, count=1)

    related_re = re.compile(r'<div class="avp-related".*?</section>', re.S)
    if not related_re.search(page):
        sys.exit("donor: related-cards section not found")
    page = related_re.sub(build_related_cards(related), page, count=1)

    if check:
        print(f"OK (--check): blog/{slug}/index.php would be written, {len(page)} bytes; "
              f"{len(related)} related card(s); sitemap + blog/index.php + llms.txt would be updated")
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(page.encode("utf-8"))

    stub = ROOT / slug / "index.php"
    stub.parent.mkdir(parents=True, exist_ok=True)
    stub.write_text(f"<?php header('Location: /blog/{slug}/', true, 301); exit;", encoding="utf-8", newline="")

    sitemap_path = ROOT / "sitemap.xml"
    sm = sitemap_path.read_bytes().decode("utf-8")
    new_url = f'  <url><loc>{canon}</loc><lastmod>{published.isoformat()}</lastmod><priority>0.7</priority></url>\n'
    lines = sm.splitlines(keepends=True)
    insert_at = len(lines)
    for i, line in enumerate(lines):
        m = re.search(r"<loc>(https://avicontravel\.com/blog/[^<]+)</loc>", line)
        if m and m.group(1) > canon:
            insert_at = i
            break
        if m:
            insert_at = i + 1
    lines.insert(insert_at, new_url)
    sitemap_path.write_bytes("".join(lines).encode("utf-8"))

    blog_index = BLOG / "index.php"
    bi = blog_index.read_bytes().decode("utf-8")
    grid_re = re.compile(r'(<div class="row g-4 mb-40">\s*)(<div class="col-lg-4)')
    if not grid_re.search(bi):
        sys.exit("blog/index.php: card grid not found")
    card = build_blog_card(spec, slug, display_short(published))
    bi = grid_re.sub(lambda m: m.group(1) + card + "\n                                                    " + m.group(2), bi, count=1)
    blog_index.write_bytes(bi.encode("utf-8"))

    llms_path = ROOT / "llms.txt"
    llms = llms_path.read_bytes().decode("utf-8")
    section = re.search(r"## Travel guides\n\n(.*?)(\n## |\Z)", llms, re.S)
    if not section:
        sys.exit("llms.txt: 'Travel guides' section not found")
    entry = f"- [{spec['title']}]({canon}): {spec['meta_description']}"
    entries = [ln for ln in section.group(1).splitlines() if ln.strip()]
    entries.append(entry)
    entries.sort(key=lambda ln: re.search(r"\[([^\]]+)\]", ln).group(1).lower())
    llms = llms[:section.start(1)] + "\n".join(entries) + llms[section.end(1):]
    llms_path.write_bytes(llms.encode("utf-8"))

    print(f"wrote blog/{slug}/index.php + {slug}/index.php (301 stub)")
    print(f"sitemap.xml, blog/index.php and llms.txt updated for {canon}")
    print("next: run schema_blog_faq.py if the body has a visible FAQ, optimize_images.py for the hero image, then health_check.py")


if __name__ == "__main__":
    main()
