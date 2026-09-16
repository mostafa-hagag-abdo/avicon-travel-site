"""Read and write the editable parts of a product page (tours, nile-cruises, packages).

    data = extract(html)          # -> dict of blocks (see BLOCKS)
    html = apply(html, data)      # re-renders only the blocks whose data differ from the page

A block that is unchanged keeps its original bytes, so apply(html, extract(html)) == html for every page.
A changed block is rendered in the site's multi-line markup at the block's original indentation.
Text fields hold HTML exactly as it appears inside the element (entities kept), so the editor
round-trips them untouched; rich fields (paragraphs, itinerary days, FAQ answers, long-form) hold inner HTML.
"""
import html as _html
import re

# ----------------------------------------------------------------------------------------------- helpers


def end_of(s, start, tag="div"):
    """Index just after the element that opens at `start` (balanced on `tag`)."""
    depth = 0
    for m in re.finditer(rf"<{tag}\b|</{tag}>", s[start:]):
        depth += 1 if m.group().startswith("<" + tag) else -1
        if depth == 0:
            return start + m.end()
    raise ValueError(f"unbalanced <{tag}> at {start}")


def element(s, pattern, tag="div", pos=0, end=None):
    """(start, end) of the first element whose opening tag matches `pattern`, searching s[pos:end]."""
    m = re.compile(pattern).search(s, pos, len(s) if end is None else end)
    if not m:
        return None
    return m.start(), end_of(s, m.start(), tag)


def inner(s, span):
    """(start, end) of the content inside the element at span."""
    open_end = s.index(">", span[0]) + 1
    close_start = s.rindex("</", span[0], span[1])
    return open_end, close_start


def indent_at(s, pos):
    line_start = s.rfind("\n", 0, pos) + 1
    return re.match(r"[ \t]*", s[line_start:]).group(0)


def nl_of(s):
    return "\r\n" if "\r\n" in s else "\n"


def icon_of(fragment):
    m = re.search(r'<i class="(?:fas|fab|far) (fa-[a-z0-9-]+)[^"]*"', fragment)
    return m.group(1) if m else ""


def text_of(fragment, cls, tag="div"):
    m = re.search(rf'<{tag} class="{cls}"[^>]*>(.*?)</{tag}>', fragment, re.S)
    return m.group(1).strip() if m else ""


def elements(frag, cls):
    """Yield (fragment, match) for every <div> whose class attribute matches the regex `cls` exactly."""
    for m in re.finditer(rf'<div class="({cls})"[^>]*>', frag):
        yield frag[m.start():end_of(frag, m.start())], m


def plain(fragment):
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


# ----------------------------------------------------------------------------------------------- regions


def main_region(s):
    span = element(s, r'<div class="main-content">')
    return span


def panel(s, pid):
    m = re.search(rf'<div class="tab-panel[^"]*" id="{pid}">', s)
    return (m.start(), end_of(s, m.start())) if m else None


# ----------------------------------------------------------------------------------------------- blocks
# Each block: find(s) -> (start, end) | None ; parse(fragment) -> data ; render(data, indent, nl) -> fragment


class Block:
    key = ""

    def find(self, s):
        raise NotImplementedError

    def parse(self, frag):
        raise NotImplementedError

    def render(self, data, ind, nl):
        raise NotImplementedError


class Title(Block):
    """The H1 (inner HTML)."""
    key = "title"

    def find(self, s):
        m = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
        return (m.start(1), m.end(1)) if m else None

    def parse(self, frag):
        return frag.strip()

    def render(self, data, ind, nl):
        return data


class Badge(Block):
    key = "badge"

    def find(self, s):
        m = re.search(r'<div class="(?:bk-badge|hero-badge)">(.*?)</div>', s, re.S)
        return (m.start(1), m.end(1)) if m else None

    def parse(self, frag):
        return {"icon": icon_of(frag), "text": re.sub(r"^\s*<i[^>]*></i>\s*", "", frag).strip()}

    def render(self, data, ind, nl):
        return (f'<i class="fas {data["icon"]}"></i> ' if data.get("icon") else "") + data["text"]


class Chips(Block):
    """bk-chips (most pages) or the hero-meta items of the tour-hero layout."""
    key = "chips"

    def find(self, s):
        span = element(s, r'<div class="bk-chips">') or element(s, r'<div class="hero-meta">')
        return span

    def parse(self, frag):
        if frag.startswith('<div class="bk-chips">'):
            return [{"icon": icon_of(c), "label": "", "text": re.sub(r"^\s*<i[^>]*></i>\s*", "", c).strip()}
                    for c in re.findall(r'<span class="bk-chip">(.*?)</span>', frag, re.S)]
        items = []
        for m in re.finditer(r'<div class="hero-meta-item">(.*?)</div>\s*</div>', frag, re.S):
            label = re.search(r"<span>(.*?)</span>", m.group(1), re.S)
            value = re.search(r"<strong>(.*?)</strong>", m.group(1), re.S)
            items.append({"icon": icon_of(m.group(1)), "label": label.group(1).strip() if label else "",
                          "text": value.group(1).strip() if value else ""})
        return items

    def render(self, data, ind, nl):
        if any(c.get("label") for c in data):
            rows = [f'{ind}  <div class="hero-meta-item">{nl}{ind}    <i class="fas {c["icon"]}"></i>{nl}'
                    f'{ind}    <div><span>{c["label"]}</span><strong>{c["text"]}</strong></div>{nl}{ind}  </div>'
                    for c in data]
            return f'<div class="hero-meta">{nl}' + nl.join(rows) + f"{nl}{ind}</div>"
        rows = [f'{ind}  <span class="bk-chip"><i class="fas {c["icon"]}"></i> {c["text"]}</span>' for c in data]
        return f'<div class="bk-chips">{nl}' + nl.join(rows) + f"{nl}{ind}</div>"


IMG_RE = re.compile(r"<img\b([^>]*)>", re.S)


def img_attrs(tag):
    get = lambda a: (re.search(rf'\s{a}="([^"]*)"', tag) or [None, ""])[1]
    return {"src": get("src"), "alt": get("alt"), "width": get("width"), "height": get("height")}


class Gallery(Block):
    """Hero photos of the bk-hero layout: bk-main + bk-tile images (the tour-hero layout uses HeroImage)."""
    key = "gallery"

    def find(self, s):
        return element(s, r'<div class="bk-gallery bk-container">')

    def parse(self, frag):
        return [img_attrs(m.group(0)) for m in IMG_RE.finditer(frag)]

    def render(self, data, ind, nl):
        def img(d, lazy):
            size = f'width="{d["width"]}" height="{d["height"]}" ' if d.get("width") and d.get("height") else ""
            return f'<img {size}{"loading=\"lazy\" " if lazy else ""}decoding="async" src="{d["src"]}" alt="{d["alt"]}">'
        rows = [f'{ind}  <div class="bk-main" data-bk-lb="1">{img(data[0], False)}</div>'] if data else []
        rows += [f'{ind}    <div class="bk-tile" data-bk-lb="1">{img(d, True)}</div>' for d in data[1:]]
        return f'<div class="bk-gallery bk-container">{nl}' + nl.join(rows) + f"{nl}{ind}</div>"


class HeroImage(Block):
    """tour-hero layout only: the one hero <img> (kept separate so the overlay markup is untouched)."""
    key = "hero_image"

    def find(self, s):
        span = element(s, r'<div class="hero-image">')
        if not span:
            return None
        m = IMG_RE.search(s, span[0], span[1])
        return (m.start(), m.end()) if m else None

    def parse(self, frag):
        return img_attrs(frag)

    def render(self, data, ind, nl):
        size = f'width="{data["width"]}" height="{data["height"]}" ' if data.get("width") and data.get("height") else ""
        return f'<img {size}decoding="async" src="{data["src"]}" alt="{data["alt"]}">'


class OverviewIntro(Block):
    """Overview heading + the section-sub paragraphs right under it."""
    key = "overview"

    def find(self, s):
        p = panel(s, "overview")
        if not p:
            return None
        m = re.compile(r'<h2 class="section-title">.*?</h2>(?:\s*<p class="section-sub">.*?</p>)*', re.S).search(s, p[0], p[1])
        return (m.start(), m.end()) if m else None

    def parse(self, frag):
        return {"heading": re.search(r"<h2[^>]*>(.*?)</h2>", frag, re.S).group(1).strip(),
                "paragraphs": [x.strip() for x in re.findall(r'<p class="section-sub">(.*?)</p>', frag, re.S)]}

    def render(self, data, ind, nl):
        out = [f'<h2 class="section-title">{data["heading"]}</h2>']
        out += [f'{ind}<p class="section-sub">{p}</p>' for p in data["paragraphs"]]
        return nl.join(out)


def fact_cards(frag, extra):
    cards = []
    for body, m in elements(frag, r"fact-card(?: qf-extra)?"):
        if m.group(1).endswith("qf-extra") != extra:
            continue
        cards.append({"icon": icon_of(body), "label": text_of(body, "fact-label"), "value": text_of(body, "fact-value")})
    return cards


def render_cards(cards, ind, nl, extra=False):
    cls = "fact-card qf-extra" if extra else "fact-card"
    return nl.join(
        f'{ind}<div class="{cls}">{nl}{ind}  <div class="fact-icon"><i class="fas {c["icon"]}"></i></div>{nl}'
        f'{ind}  <div class="fact-label">{c["label"]}</div>{nl}{ind}  <div class="fact-value">{c["value"]}</div>{nl}{ind}</div>'
        for c in cards)


class Facts(Block):
    """The first quick-facts grid in the overview: base cards + the four qf-extra cards (Price, Pickup, Included, Best Time)."""
    key = "facts"

    def find(self, s):
        p = panel(s, "overview")
        return element(s, r'<div class="quick-facts">', pos=p[0], end=p[1]) if p else None

    def parse(self, frag):
        extra = fact_cards(frag, True)
        return {"cards": fact_cards(frag, False), "extra": {c["label"]: c["value"] for c in extra}}

    def render(self, data, ind, nl):
        extra = [{"icon": icon, "label": label, "value": data["extra"][label]}
                 for icon, label in (("fa-tag", "Price"), ("fa-location-dot", "Pickup"), ("fa-circle-check", "Included"), ("fa-sun", "Best Time"))
                 if data["extra"].get(label)]
        body = render_cards(data["cards"], ind + "  ", nl)
        if extra:
            body += nl + render_cards(extra, ind + "  ", nl, extra=True)
        return f'<div class="quick-facts">{nl}{body}{nl}{ind}</div>'


class Highlights(Block):
    """'… Highlights' heading with either a bullet list (tours/packages) or a card grid (cruises)."""
    key = "highlights"

    def find(self, s):
        p = panel(s, "overview")
        if not p:
            return None
        m = re.compile(r'<h3 class="section-title"[^>]*>[^<]*Highlights</h3>\s*').search(s, p[0], p[1])
        if not m:
            return None
        after = m.end()
        if s.startswith("<ul", after):
            return m.start(), end_of(s, after, "ul")
        if s.startswith('<div class="quick-facts">', after):
            return m.start(), end_of(s, after)
        return None

    def parse(self, frag):
        heading = re.search(r"<h3[^>]*>(.*?)</h3>", frag, re.S).group(1).strip()
        style = re.search(r"<h3[^>]*style=\"([^\"]*)\"", frag).group(1)
        if '<div class="quick-facts">' in frag:
            return {"heading": heading, "style": style, "cards": fact_cards(frag, False), "items": []}
        ul_style = (re.search(r'<ul style="([^"]*)"', frag) or [None, ""])[1]
        return {"heading": heading, "style": style, "ul_style": ul_style, "cards": [],
                "items": [x.strip() for x in re.findall(r"<li>(.*?)</li>", frag, re.S)]}

    def render(self, data, ind, nl):
        head = f'<h3 class="section-title" style="{data.get("style") or "font-size:17px;margin-top:24px"}">{data["heading"]}</h3>'
        if data.get("cards"):
            return f'{head}{nl}{ind}<div class="quick-facts">{nl}{render_cards(data["cards"], ind + "  ", nl)}{nl}{ind}</div>'
        ul_style = data.get("ul_style") or "padding-left: 20px; color: var(--text-muted); font-size: 13px; line-height: 1.7; margin-bottom: 24px;"
        items = nl.join(f"{ind}  <li>{x}</li>" for x in data["items"])
        return f'{head}{nl}{ind}<ul style="{ul_style}">{nl}{items}{nl}{ind}</ul>'


class Route(Block):
    key = "route"

    def find(self, s):
        p = panel(s, "overview")
        if not p:
            return None
        m = re.compile(r'<h3 class="section-title"[^>]*>[^<]*Route</h3>\s*<div class="route-section">').search(s, p[0], p[1])
        if not m:
            return None
        return m.start(), end_of(s, s.index('<div class="route-section">', m.start()))

    def parse(self, frag):
        heading = re.search(r"<h3[^>]*>(.*?)</h3>", frag, re.S).group(1).strip()
        style = re.search(r"<h3[^>]*style=\"([^\"]*)\"", frag).group(1)
        stops, lines = [], []
        for body, m in elements(frag, r"route-stop|route-line"):
            if m.group(1) == "route-line":
                lines.append(icon_of(body))
            else:
                stops.append({"icon": icon_of(body), "name": text_of(body, "route-stop-name"), "label": text_of(body, "route-stop-num")})
        return {"heading": heading, "style": style, "stops": stops, "connectors": lines}

    def render(self, data, ind, nl):
        i2, i3, i4 = ind + "  ", ind + "    ", ind + "      "
        parts = []
        connectors = list(data.get("connectors") or [])
        for n, st in enumerate(data["stops"]):
            if n:
                # a new stop reuses the previous connector icon (ship, car, arrow…)
                icon = connectors[n - 1] if n - 1 < len(connectors) else (connectors[-1] if connectors else "fa-arrow-right")
                parts.append(f'{i4}<div class="route-line"><i class="fas {icon or "fa-arrow-right"}"></i></div>')
            parts.append(f'{i4}<div class="route-stop">{nl}{i4}  <div class="route-stop-icon"><i class="fas {st["icon"]}"></i></div>{nl}'
                         f'{i4}  <div class="route-stop-name">{st["name"]}</div>{nl}{i4}  <div class="route-stop-num">{st["label"]}</div>{nl}{i4}</div>')
        return (f'<h3 class="section-title" style="{data.get("style") or "font-size:17px;margin-top:20px"}">{data["heading"]}</h3>{nl}'
                f'{ind}<div class="route-section">{nl}{i2}<div class="route-bar">{nl}{i3}<div class="route-track">{nl}'
                + nl.join(parts) + f"{nl}{i3}</div>{nl}{i2}</div>{nl}{ind}</div>")


class Pricing(Block):
    """Price table: gold-pricing seasons (most pages) or the tour-prices-box table."""
    key = "pricing"

    def find(self, s):
        p = panel(s, "overview")
        if not p:
            return None
        return element(s, r'<div class="gold-pricing">', pos=p[0], end=p[1]) or element(s, r'<div class="tour-prices-box">', pos=p[0], end=p[1])

    def parse(self, frag):
        if frag.startswith('<div class="tour-prices-box">'):
            title = re.search(r'<div class="tour-prices-title">.*?<span>(.*?)</span>', frag, re.S).group(1).strip()
            head = [x.strip() for x in re.findall(r"<th>(.*?)</th>", frag, re.S)]
            body = re.search(r"<tbody>(.*?)</tbody>", frag, re.S).group(1)
            rows = [[c.strip() for c in re.findall(r"<td>(.*?)</td>", r, re.S)] for r in re.findall(r"<tr>(.*?)</tr>", body, re.S)]
            return {"kind": "table", "title": title, "columns": head, "rows": rows, "seasons": []}
        title = re.search(r'<div class="gold-pricing-header">.*?</span>\s*<span>(.*?)</span>', frag, re.S).group(1).strip()
        seasons = []
        for body, _ in elements(frag, "gold-season"):
            head = re.search(r'<div class="gold-season-date">(.*?)</div>', body, re.S).group(1)
            seasons.append({"icon": icon_of(head),
                            "label": re.search(r"<span>(.*?)</span>", head, re.S).group(1).strip(),
                            "rows": [[k.strip(), v.strip()] for k, v in re.findall(
                                r'<div class="gold-price-row"><span>(.*?)</span><strong>(.*?)</strong></div>', body, re.S)]})
        return {"kind": "seasons", "title": title, "seasons": seasons, "columns": [], "rows": []}

    def render(self, data, ind, nl):
        i2, i3, i4, i5 = (ind + "  " * n for n in (1, 2, 3, 4))
        if data.get("kind") == "table":
            head = nl.join(f"{i5}<th>{c}</th>" for c in data["columns"])
            rows = nl.join(f"{i4}<tr>{nl}" + nl.join(f"{i5}<td>{c}</td>" for c in r) + f"{nl}{i4}</tr>" for r in data["rows"])
            return (f'<div class="tour-prices-box">{nl}{i2}<div class="tour-prices-title">{nl}{i3}<i class="fas fa-sack-dollar"></i>{nl}'
                    f'{i3}<span>{data["title"]}</span>{nl}{i2}</div>{nl}{nl}{i2}<table class="tour-prices-table">{nl}{i3}<thead>{nl}{i4}<tr>{nl}'
                    f'{head}{nl}{i4}</tr>{nl}{i3}</thead>{nl}{i3}<tbody>{nl}{rows}{nl}{i3}</tbody>{nl}{i2}</table>{nl}{ind}</div>')
        seasons = []
        for se in data["seasons"]:
            rows = nl.join(f'{i5}<div class="gold-price-row"><span>{k}</span><strong>{v}</strong></div>' for k, v in se["rows"])
            seasons.append(f'{i3}<div class="gold-season">{nl}{i4}<div class="gold-season-date"><i class="fas {se.get("icon") or "fa-tags"}"></i>'
                           f'<span>{se["label"]}</span></div>{nl}{i4}<div class="gold-price-card">{nl}{rows}{nl}{i4}</div>{nl}{i3}</div>')
        return (f'<div class="gold-pricing">{nl}{i2}<div class="gold-pricing-header">{nl}{i3}<span class="gold-pricing-icon"><i class="fas fa-tags"></i></span>{nl}'
                f'{i3}<span>{data["title"]}</span>{nl}{i2}</div>{nl}{i2}<div class="gold-pricing-grid">{nl}{nl}'
                + nl.join(seasons) + f"{nl}{i2}</div>{nl}{ind}</div>")


class Longform(Block):
    """The long-form guide copy at the end of the overview (inner HTML, may be absent)."""
    key = "longform"

    def find(self, s):
        span = element(s, r'<div class="av-longform">')
        return inner(s, span) if span else None

    def parse(self, frag):
        return frag

    def render(self, data, ind, nl):
        return data


class Itinerary(Block):
    key = "itinerary"

    def find(self, s):
        return panel(s, "itinerary")

    def parse(self, frag):
        heading = re.search(r'<h2 class="section-title">(.*?)</h2>', frag, re.S)
        intro = re.search(r'<p class="section-sub">(.*?)</p>', frag, re.S)
        days = []
        for m in re.finditer(r'<div class="day-item[^"]*">', frag):
            item = frag[m.start():end_of(frag, m.start())]
            title = re.search(r'<div class="day-title">(?:<span>(.*?)</span>)?\s*(.*?)</div>', item, re.S)
            content_span = element(item, r'<div class="day-content">')
            content = item[inner(item, content_span)[0]:inner(item, content_span)[1]].strip() if content_span else ""
            days.append({"label": (title.group(1) or "").strip() if title else "", "title": title.group(2).strip() if title else "",
                         "html": content})
        return {"heading": heading.group(1).strip() if heading else "", "intro": intro.group(1).strip() if intro else "", "days": days}

    def render(self, data, ind, nl):
        i2, i3, i4, i5 = (ind + "  " * n for n in (1, 2, 3, 4))
        days = []
        for n, d in enumerate(data["days"], 1):
            label = f"<span>{d['label']}</span> " if d.get("label") else ""
            body = nl.join(f"{i5}{line.strip()}" for line in re.split(r"(?<=</p>)\s*(?=<)", d["html"].strip()) if line.strip())
            days.append(f'{i3}<div class="day-item{" open" if n == 1 else ""}">{nl}{i4}<div class="day-marker">{n}</div>{nl}'
                        f'{i4}<div class="day-header">{nl}{i5}<div class="day-title">{label}{d["title"]}</div>{nl}'
                        f'{i5}<i class="fas fa-chevron-down day-toggle"></i>{nl}{i4}</div>{nl}{i4}<div class="day-content">{nl}{body}{nl}{i4}</div>{nl}{i3}</div>')
        intro = f'{i2}<p class="section-sub">{data["intro"]}</p>{nl}' if data.get("intro") else ""
        return (f'<div class="tab-panel" id="itinerary">{nl}{i2}<h2 class="section-title">{data["heading"]}</h2>{nl}{intro}{nl}'
                f'{i2}<div class="timeline">{nl}{nl}' + nl.join(days) + f"{nl}{nl}{i2}</div>{nl}{ind}</div>")


class TicketItems(Block):
    """Included / excluded lists (the ticket-items of each ticket) plus the stub counts."""

    def __init__(self, which):
        self.which = which
        self.key = which

    def find(self, s):
        p = panel(s, "inclusions")
        if not p:
            return None
        return element(s, rf'<div class="ticket {self.which}">', pos=p[0], end=p[1])

    def parse(self, frag):
        return [x.strip() for x in re.findall(r'<div class="ticket-item-text">(.*?)</div>', frag, re.S)]

    def apply_to(self, frag, items, nl):
        """Replace the stub count and the ticket-items block inside the existing ticket markup."""
        icon = "fa-check" if self.which == "included" else "fa-xmark"
        frag = re.sub(r'(<div class="stub-count">)\d+ ITEMS?(</div>)', rf"\g<1>{len(items)} ITEMS\g<2>", frag, count=1)
        span = element(frag, r'<div class="ticket-items">')
        ind = indent_at(frag, span[0])
        rows = nl.join(f'{ind}  <div class="ticket-item"><div class="ticket-item-icon"><i class="fas {icon}"></i></div>'
                       f'<div class="ticket-item-text">{x}</div></div>' for x in items)
        return frag[:span[0]] + f'<div class="ticket-items">{nl}{rows}{nl}{ind}</div>' + frag[span[1]:]


class Faq(Block):
    key = "faq"

    def find(self, s):
        return panel(s, "faq")

    def parse(self, frag):
        heading = re.search(r'<h2 class="section-title">(.*?)</h2>', frag, re.S)
        intro = re.search(r'<p class="section-sub">(.*?)</p>', frag, re.S)
        items = []
        for m in re.finditer(r'<div class="day-item[^"]*">', frag):
            item = frag[m.start():end_of(frag, m.start())]
            q = re.search(r'<div class="day-title"[^>]*>(.*?)</div>', item, re.S)
            content_span = element(item, r'<div class="day-content">')
            a = item[inner(item, content_span)[0]:inner(item, content_span)[1]].strip() if content_span else ""
            items.append({"q": q.group(1).strip() if q else "", "a": a})
        return {"heading": heading.group(1).strip() if heading else "", "intro": intro.group(1).strip() if intro else "", "items": items}

    def render(self, data, ind, nl):
        i2, i3, i4, i5 = (ind + "  " * n for n in (1, 2, 3, 4))
        items = []
        for n, it in enumerate(data["items"], 1):
            items.append(f'{i3}<div class="day-item{" open" if n == 1 else ""}">{nl}{i4}<div class="day-header" style="cursor:pointer">{nl}'
                         f'{i5}<div class="day-title" style="font-size:14px">{it["q"]}</div>{nl}{i5}<i class="fas fa-chevron-down day-toggle"></i>{nl}'
                         f'{i4}</div>{nl}{i4}<div class="day-content">{nl}{i5}{it["a"].strip()}{nl}{i4}</div>{nl}{i3}</div>')
        intro = f'{i2}<p class="section-sub">{data["intro"]}</p>{nl}' if data.get("intro") else ""
        return (f'<div class="tab-panel" id="faq">{nl}{i2}<h2 class="section-title">{data["heading"]}</h2>{nl}{intro}'
                f'{i2}<div class="timeline">{nl}' + nl.join(items) + f"{nl}{i2}</div>{nl}{ind}</div>")


class SidebarPrice(Block):
    """Booking box price: label, amount (text between the <small> tags) and the note under it."""
    key = "price"

    def find(self, s):
        return element(s, r'<div class="price-header">')

    def parse(self, frag):
        amount = re.search(r'<div class="price-amount"(?: style="([^"]*)")?>(?:<small>(.*?)</small>)?(.*?)(?:<small>(.*?)</small>)?</div>', frag, re.S)
        return {"label": text_of(frag, "price-label"), "currency": (amount.group(2) or "").strip(), "amount": amount.group(3).strip(),
                "per": (amount.group(4) or "").strip(), "note": text_of(frag, "price-per"), "style": amount.group(1) or ""}

    def render(self, data, ind, nl):
        numeric = bool(re.search(r"\d", data["amount"]))
        amount = (f"<small>{data['currency']}</small>" if data.get("currency") and numeric else "") + data["amount"] + \
                 (f"<small>{data['per']}</small>" if data.get("per") and numeric else "")
        style = data.get("style") if data.get("style") else ("" if numeric else "font-size:30px")
        style_attr = f' style="{style}"' if style else ""
        return (f'<div class="price-header">{nl}{ind}  <div class="price-label">{data["label"]}</div>{nl}'
                f'{ind}  <div class="price-amount"{style_attr}>{amount}</div>{nl}{ind}  <div class="price-per">{data["note"]}</div>{nl}{ind}</div>')


SIMPLE = [Title(), Badge(), Chips(), Gallery(), HeroImage(), OverviewIntro(), Facts(), Highlights(), Route(), Pricing(),
          Longform(), Itinerary(), Faq(), SidebarPrice()]
TICKETS = [TicketItems("included"), TicketItems("excluded")]
BLOCKS = [b.key for b in SIMPLE] + [t.key for t in TICKETS]


def extract(s):
    data = {}
    for b in SIMPLE + TICKETS:
        span = b.find(s)
        data[b.key] = b.parse(s[span[0]:span[1]]) if span else None
    data["tour_package"] = (re.search(r'<input type="hidden" name="tour_package" value="([^"]*)"', s) or [None, None])[1]
    data["crumb"] = (re.search(r'<nav class="bk-crumb">.*?<b>(.*?)</b></nav>', s, re.S) or [None, None])[1]
    return data


def price_text(price):
    """'From $95 / person' style text from the sidebar price, used by the summary row and estimate."""
    cur = _html.unescape(price.get("currency") or "$")
    return f"From {cur}{price['amount']}"


def apply(s, data):
    """Write data into the page. Only blocks whose data differ are re-rendered."""
    nl = nl_of(s)
    old = extract(s)
    # Work from the end of the page backwards so earlier spans stay valid.
    edits = []
    for b in SIMPLE:
        new = data.get(b.key)
        if new is None or new == old.get(b.key):
            continue
        span = b.find(s)
        if not span:
            raise ValueError(f"block '{b.key}' is not on this page")
        edits.append((span, b.render(new, indent_at(s, span[0]), nl)))
    for t in TICKETS:
        new = data.get(t.key)
        if new is None or new == old.get(t.key):
            continue
        span = t.find(s)
        edits.append((span, t.apply_to(s[span[0]:span[1]], new, nl)))
    edits.sort(key=lambda e: e[0][0], reverse=True)
    for (a, b_), text in edits:
        s = s[:a] + text + s[b_:]
    # Values that repeat the price or the name elsewhere in the booking box.
    if data.get("price") and data["price"] != old.get("price"):
        p = data["price"]
        per = " / person" if "person" in (p.get("per") or "") else ""
        on_request = not re.search(r"\d", p["amount"])
        summary = "On request" if on_request else f"{price_text(p)}{per}"
        s = re.sub(r'(<div class="summary-row total"><span>[^<]*</span><span>)[^<]*(</span></div>)', rf"\g<1>{summary}\g<2>", s, count=1)
        estimate = "Price on request" if on_request else f"Starting {price_text(p)} Per Person"
        s = re.sub(r'(<input type="hidden" name="estimated_total" id="totalInput" value=")[^"]*(")', rf"\g<1>{estimate}\g<2>", s, count=1)
    if data.get("tour_package") and data["tour_package"] != old.get("tour_package"):
        name = data["tour_package"]
        s = re.sub(r'(<input type="hidden" name="tour_package" value=")[^"]*(")', rf"\g<1>{name}\g<2>", s, count=1)
        s = re.sub(r'(<input type="hidden" name="subject" value="New Booking - )[^"]*(")', rf"\g<1>{name}\g<2>", s, count=1)
    if data.get("crumb") and data["crumb"] != old.get("crumb"):
        s = re.sub(r'(<nav class="bk-crumb">.*?<b>)(.*?)(</b></nav>)', lambda m: m.group(1) + data["crumb"] + m.group(3), s, count=1, flags=re.S)
    return s
