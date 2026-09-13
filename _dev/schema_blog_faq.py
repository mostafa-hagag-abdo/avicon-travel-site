"""Add a FAQPage node to each blog article's JSON-LD graph, built from the article's visible FAQ section.

    python _dev/schema_blog_faq.py           # write
    python _dev/schema_blog_faq.py --check   # print the parsed questions, write nothing

The FAQ section is the H2 whose text contains "FAQ" or "Frequently Asked Questions", up to the next H2.
Two layouts are read: <h3>question</h3> + answer blocks, or <li><strong>question</strong> answer</li>.
The node goes into the existing <script id="avicon-schema"> graph (any older FAQPage node is replaced),
so re-run it after editing an article's FAQ. Visible content is never touched.
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAG = re.compile(r'(<script type="application/ld\+json" id="avicon-schema">)(.*?)(</script>)', re.S)
check = "--check" in sys.argv


def plain(fragment):
    fragment = re.sub(r"</li>", "; ", fragment)
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()
    t = re.sub(r"\s+([,.;:!?])", r"\1", t)
    return re.sub(r"(;\s*)+$", "", t).strip()


def faq_pairs(s):
    heads = list(re.finditer(r"<h2[^>]*>(.*?)</h2>", s, re.S))
    faq = [m for m in heads if re.search(r"\bFAQs?\b|Frequently Asked Questions", plain(m.group(1)), re.I)]
    if len(faq) != 1:
        raise ValueError(f"{len(faq)} FAQ headings")
    start = faq[0].end()
    nxt = next((m.start() for m in heads if m.start() > start), None)
    end = nxt if nxt is not None else s.find("</article>", start)
    chunk = s[start:end]
    if "<h3" in chunk:
        parts = re.split(r"<h3[^>]*>(.*?)</h3>", chunk, flags=re.S)[1:]
        pairs = [(plain(q), plain(a)) for q, a in zip(parts[::2], parts[1::2])]
    else:
        pairs = []
        for li in re.findall(r"<li\b[^>]*>(.*?)</li>", chunk, re.S):
            m = re.search(r"<strong>(.*?)</strong>(.*)", li, re.S)
            if m:
                pairs.append((plain(m.group(1)), plain(m.group(2))))
    bad = [q for q, a in pairs if not q.endswith("?") or len(a.split()) < 5]
    if len(pairs) < 3 or bad:
        raise ValueError(f"{len(pairs)} pairs, suspicious: {bad}")
    return pairs


total = 0
for p in sorted((ROOT / "blog").glob("*/index.php")):
    raw = p.read_bytes().decode("utf-8")
    url = f"/blog/{p.parent.name}/"
    try:
        pairs = faq_pairs(raw)
    except ValueError as err:
        sys.exit(f"{url}: {err}")
    m = TAG.search(raw)
    if not m:
        sys.exit(f"{url}: no avicon-schema graph")
    data = json.loads(m.group(2))
    canon = f"https://avicontravel.com{url}"
    nodes = [n for n in data["@graph"] if n.get("@type") != "FAQPage"]
    nodes.append({"@type": "FAQPage", "@id": canon + "#faq", "isPartOf": {"@id": canon + "#webpage"},
                  "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                                 for q, a in pairs]})
    data["@graph"] = nodes
    body = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    total += len(pairs)
    print(f"{len(pairs):2} Q  {url}")
    if check:
        for q, a in pairs:
            print(f"     Q: {q}\n     A: {a[:110]}{'…' if len(a) > 110 else ''}")
        continue
    new = raw[:m.start(2)] + body + raw[m.end(2):]
    if new != raw:
        p.write_bytes(new.encode("utf-8"))
print(f"{total} questions {'parsed' if check else 'written'}")
