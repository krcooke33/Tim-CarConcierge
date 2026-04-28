#!/usr/bin/env python3
"""
Export all public-site copy as a single .docx file for a non-technical
copywriter to edit outside Replit.

Pages covered (in nav order):
  HOME            — index.html
  ABOUT           — about/index.html
  HOW IT WORKS    — process/index.html
  GALLERY         — gallery/index.html
  CONTACT         — contact/index.html
  CONTACT THANKS  — contact/thanks/index.html
  404             — 404.html

Internal-only pages (brand-exploration, business-plan, competitor-research,
components, conversation-guide, mood-board, site-brief) are excluded.

Each editable block is preceded by a short canonical block-ID label in the
form  PAGE · Section · Slot  (for example, "HOME · Hero · H1" or
"PROCESS · FAQ · Q3"). Section headers add a larger chapter divider for
readability. All copy is emitted verbatim — no case transformations.

Output: copy-export.docx in the project root.
"""

from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.shared import Pt, RGBColor


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "copy-export.docx"

OXBLOOD = RGBColor(0x6E, 0x1F, 0x1F)
INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x66, 0x66, 0x66)


# ─────────────────────────────────────────────────────────────────────────────
# Loading + DOM helpers
# ─────────────────────────────────────────────────────────────────────────────


def load(rel_path: str) -> BeautifulSoup:
    with (PROJECT_ROOT / rel_path).open("r", encoding="utf-8") as f:
        return BeautifulSoup(f.read(), "html.parser")


def add_inline_runs(paragraph, node, italic_inherited: bool = False, bold_inherited: bool = False):
    """
    Walk a BeautifulSoup node and add runs to the paragraph, preserving
    italic (<em>, <i>) and bold (<strong>, <b>) at the run level. The
    .brand-amp span renders as a literal "&". <br> becomes a line break.
    Anchors and other inline tags render as their text content.
    """
    for child in node.children:
        if isinstance(child, NavigableString):
            text = str(child)
            if not text:
                continue
            run = paragraph.add_run(text)
            run.italic = italic_inherited
            run.bold = bold_inherited
        elif isinstance(child, Tag):
            name = child.name.lower()
            if name == "br":
                paragraph.add_run("\n")
                continue
            classes = child.get("class", []) or []

            italic_now = italic_inherited or name in ("em", "i")
            bold_now = bold_inherited or name in ("strong", "b")

            if "brand-amp" in classes:
                run = paragraph.add_run("&")
                run.italic = italic_now
                run.bold = bold_now
                continue

            add_inline_runs(paragraph, child, italic_now, bold_now)


def collapse_whitespace_runs(paragraph):
    """Collapse multi-whitespace within and across runs of a paragraph and
    trim leading/trailing whitespace, while preserving per-run italic/bold."""
    prev_space = True  # treat start as whitespace → trims leading
    new_texts = []
    for r in paragraph.runs:
        out_chars = []
        for ch in r.text:
            if ch.isspace():
                if not prev_space:
                    out_chars.append(" ")
                prev_space = True
            else:
                out_chars.append(ch)
                prev_space = False
        new_texts.append("".join(out_chars))
    for i in range(len(new_texts) - 1, -1, -1):
        if new_texts[i]:
            new_texts[i] = new_texts[i].rstrip()
            break
    for r, t in zip(paragraph.runs, new_texts):
        r.text = t


# ─────────────────────────────────────────────────────────────────────────────
# Block-ID + paragraph emitters
# ─────────────────────────────────────────────────────────────────────────────


def chapter_label(doc, page: str, section: str):
    """Larger chapter divider. Page + section, no slot. For navigation."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"{page}  ·  {section}")
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = OXBLOOD
    return p


def block_id(doc, page: str, section: str, slot: str):
    """Small grey canonical block-ID label preceding an editable block."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(f"{page} · {section} · {slot}")
    run.font.size = Pt(8)
    run.font.color.rgb = MUTED
    run.font.bold = True
    return p


def add_copy_paragraph(doc, html_node, *, style: str = "body"):
    """
    Emit a paragraph from a BeautifulSoup node. NEVER transforms case or
    text — copy is verbatim. Style only adjusts visual presentation
    (size, color, indent). Italic emphasis comes from <em>/<i> in the
    source HTML, not from the style.
    """
    p = doc.add_paragraph()

    if html_node is not None:
        add_inline_runs(p, html_node)
        collapse_whitespace_runs(p)

    if not p.runs or all(not r.text for r in p.runs):
        p._element.getparent().remove(p._element)
        return None

    pf = p.paragraph_format

    if style == "h1":
        for r in p.runs:
            r.font.size = Pt(20)
            r.font.bold = True
            r.font.color.rgb = INK
        pf.space_before = Pt(2)
        pf.space_after = Pt(8)
    elif style == "h2":
        for r in p.runs:
            r.font.size = Pt(15)
            r.font.bold = True
            r.font.color.rgb = INK
        pf.space_before = Pt(2)
        pf.space_after = Pt(6)
    elif style == "h3":
        for r in p.runs:
            r.font.size = Pt(12)
            r.font.bold = True
            r.font.color.rgb = INK
        pf.space_before = Pt(2)
        pf.space_after = Pt(4)
    elif style == "kicker":
        # NO uppercase transform — copy is verbatim. Visual cue is color
        # only (oxblood matches site CSS for kickers).
        for r in p.runs:
            r.font.size = Pt(10)
            r.font.bold = True
            r.font.color.rgb = OXBLOOD
        pf.space_before = Pt(2)
        pf.space_after = Pt(2)
    elif style == "lede":
        for r in p.runs:
            r.font.size = Pt(12)
            r.font.color.rgb = INK
        pf.space_before = Pt(2)
        pf.space_after = Pt(6)
    elif style == "caption":
        for r in p.runs:
            r.font.size = Pt(9)
            r.font.color.rgb = MUTED
        pf.space_before = Pt(0)
        pf.space_after = Pt(4)
    elif style == "quote":
        # Indent + size only. Italic emphasis comes from <em> in source HTML.
        for r in p.runs:
            r.font.size = Pt(11)
            r.font.color.rgb = INK
        pf.left_indent = Pt(18)
        pf.space_before = Pt(2)
        pf.space_after = Pt(4)
    else:  # body
        for r in p.runs:
            r.font.size = Pt(11)
            r.font.color.rgb = INK
        pf.space_before = Pt(2)
        pf.space_after = Pt(6)

    return p


def add_text_paragraph(doc, text: str, *, style: str = "body"):
    """Convenience: emit a paragraph from a plain string (verbatim)."""
    if not text:
        return None
    soup = BeautifulSoup(f"<root>{text}</root>", "html.parser")
    return add_copy_paragraph(doc, soup.root, style=style)


def emit(doc, page: str, section: str, slot: str, html_node, *, style: str = "body"):
    """Emit a canonical block ID label followed by the editable block."""
    if html_node is None:
        return
    block_id(doc, page, section, slot)
    add_copy_paragraph(doc, html_node, style=style)


def emit_text(doc, page: str, section: str, slot: str, text: str, *, style: str = "body"):
    """Emit a canonical block ID label followed by a plain-text block."""
    if not text:
        return
    block_id(doc, page, section, slot)
    add_text_paragraph(doc, text, style=style)


# ─────────────────────────────────────────────────────────────────────────────
# Shared sections (metadata, nav, footer, alts)
# ─────────────────────────────────────────────────────────────────────────────


def emit_page_meta(doc, soup: BeautifulSoup, page: str):
    S = "Page metadata"
    chapter_label(doc, page, S)

    title = soup.find("title")
    if title:
        emit(doc, page, S, "Browser title", title, style="body")

    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        emit_text(doc, page, S, "Meta description", meta_desc["content"], style="body")

    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content"):
        emit_text(doc, page, S, "Social-share title", og_title["content"], style="body")

    og_desc = soup.find("meta", attrs={"property": "og:description"})
    if og_desc and og_desc.get("content"):
        emit_text(doc, page, S, "Social-share description", og_desc["content"], style="body")


def emit_alts(doc, soup: BeautifulSoup, page: str):
    S = "Image alt text"
    alts = []
    for img in soup.find_all("img"):
        alt = (img.get("alt") or "").strip()
        if alt:
            alts.append(alt)
    if not alts:
        return
    chapter_label(doc, page, S)
    for i, a in enumerate(alts, 1):
        emit_text(doc, page, S, f"Alt {i}", a, style="body")


def emit_nav_block(doc, soup: BeautifulSoup, page: str):
    nav = soup.find("nav", class_="site-nav")
    if not nav:
        return
    S = "Site navigation (same on every page)"
    chapter_label(doc, page, S)

    wordmark = nav.find(class_="nav-wordmark")
    if wordmark:
        emit(doc, page, S, "Wordmark (top-left)", wordmark, style="body")

    links_ul = nav.find("ul", class_="nav-links")
    if links_ul:
        labels = [li.get_text(" ", strip=True) for li in links_ul.find_all("li")]
        emit_text(doc, page, S, "Nav link labels", " · ".join(labels), style="body")


def emit_footer_block(doc, soup: BeautifulSoup, page: str):
    footer = soup.find("footer", class_="site-footer")
    if not footer:
        return
    S = "Site footer (same on every page)"
    chapter_label(doc, page, S)

    byline = footer.find(class_="footer-byline")
    if byline:
        emit(doc, page, S, "Byline", byline, style="body")

    nums = footer.select(".year-mark .num")
    connector = footer.select_one(".year-mark .connector")
    if nums and connector:
        years = f"'{nums[0].get_text(strip=True)} {connector.get_text(strip=True)} '{nums[1].get_text(strip=True)}"
        emit_text(doc, page, S, "Era mark (lockup)", years, style="body")

    links_ul = footer.select_one(".footer-links ul")
    if links_ul:
        labels = [li.get_text(" ", strip=True) for li in links_ul.find_all("li")]
        emit_text(doc, page, S, "Footer nav labels", " · ".join(labels), style="body")

    email_link = footer.select_one(".footer-email")
    if email_link:
        emit(doc, page, S, "Email link label", email_link, style="body")

    lineage = footer.select_one(".footer-lineage")
    if lineage and lineage.find("p"):
        emit(doc, page, S, "Lineage line", lineage.find("p"), style="body")

    bottom_left = footer.select_one(".footer-bottom-left")
    bottom_right = footer.select_one(".footer-bottom-right")
    if bottom_left:
        emit(doc, page, S, "Footer bottom — copyright", bottom_left, style="body")
    if bottom_right:
        emit(doc, page, S, "Footer bottom — region + era", bottom_right, style="body")


# ─────────────────────────────────────────────────────────────────────────────
# Per-page extractors
# ─────────────────────────────────────────────────────────────────────────────


def emit_home(doc, soup: BeautifulSoup):
    P = "HOME"

    emit_page_meta(doc, soup, P)
    emit_nav_block(doc, soup, P)

    # Hero
    S = "Hero"
    chapter_label(doc, P, S)
    hero = soup.find("header", class_="hero")
    emit(doc, P, S, "Wordmark", hero.select_one(".hero-wordmark"), style="body")
    emit(doc, P, S, "H1", hero.select_one("h1"), style="h1")
    emit(doc, P, S, "Tagline", hero.select_one(".hero-tagline"), style="lede")
    emit(doc, P, S, "CTA button", hero.select_one(".btn"), style="body")
    emit_text(doc, P, S, "Era mark (decal)", "'66  '99", style="body")

    # The problem
    S = "Section 1 — The problem"
    chapter_label(doc, P, S)
    prob = soup.find("section", class_="home-problem")
    if prob:
        emit(doc, P, S, "H2", prob.find("h2"), style="h2")
        lede = prob.find("p", class_="lede")
        emit(doc, P, S, "Lede", lede, style="lede")
        body_ps = [p for p in prob.find_all("p") if "lede" not in (p.get("class") or [])]
        for i, p in enumerate(body_ps, 1):
            emit(doc, P, S, f"Body {i}", p, style="body")

    # What we do
    S = "Section 2 — What The & Garage does"
    chapter_label(doc, P, S)
    wwd = soup.find("section", class_="what-we-do")
    if wwd:
        emit(doc, P, S, "H2", wwd.find("h2"), style="h2")
        emit(doc, P, S, "Lede", wwd.find("p", class_="lede"), style="lede")
        for card in wwd.select(".service-card"):
            num_el = card.select_one(".card-num")
            num = num_el.get_text(strip=True) if num_el else ""
            emit(doc, P, S, f"Card {num} · H3", card.find("h3"), style="h3")
            emit(doc, P, S, f"Card {num} · Body", card.find("p"), style="body")
        emit(doc, P, S, "CTA button", wwd.select_one(".what-we-do-cta .btn"), style="body")

    # Tim signature
    S = "Section 3 — Meet Tim signature"
    chapter_label(doc, P, S)
    sig = soup.find("section", class_="home-tim-signature")
    if sig:
        emit(doc, P, S, "Kicker", sig.find(class_="kicker"), style="kicker")
        emit(doc, P, S, "Signature body", sig.find(class_="signature-body"), style="body")
        emit(doc, P, S, "CTA button", sig.find("a", class_="btn"), style="body")

    # Quotes
    S = "Section 4 — Testimonials"
    chapter_label(doc, P, S)
    quotes = soup.find("section", class_="home-quotes")
    if quotes:
        emit(doc, P, S, "H2", quotes.find("h2"), style="h2")
        for i, card in enumerate(quotes.select(".quote-card"), 1):
            emit(doc, P, S, f"Testimonial {i} · Quote", card.find("blockquote"), style="quote")
            cite = card.find("cite")
            if cite:
                name = cite.find(class_="name")
                city = cite.find(class_="city")
                car = cite.find(class_="car")
                if name:
                    emit_text(doc, P, S, f"Testimonial {i} · Name", name.get_text(strip=True), style="body")
                if city:
                    emit_text(doc, P, S, f"Testimonial {i} · City", city.get_text(strip=True), style="body")
                if car:
                    emit_text(doc, P, S, f"Testimonial {i} · Car", car.get_text(strip=True), style="body")

    # Gallery teaser
    S = "Section 5 — Gallery teaser"
    chapter_label(doc, P, S)
    teaser = soup.find("section", class_="home-gallery-teaser")
    if teaser:
        emit(doc, P, S, "H2", teaser.find("h2"), style="h2")
        for i, card in enumerate(teaser.select(".gallery-card"), 1):
            emit(doc, P, S, f"Card {i} · Title", card.find(class_="car-title"), style="h3")
            emit(doc, P, S, f"Card {i} · Spotted", card.find(class_="spotted"), style="caption")
            emit(doc, P, S, f"Card {i} · Note", card.find(class_="note"), style="body")
        emit(doc, P, S, "Bottom link", teaser.select_one(".gallery-teaser-link"), style="body")

    # Final CTA
    S = "Section 6 — Final CTA"
    chapter_label(doc, P, S)
    final = soup.find("section", class_="final-cta")
    if final:
        emit(doc, P, S, "Quiet line", final.find(class_="final-cta-quiet"), style="quote")
        emit(doc, P, S, "Lead line", final.find(class_="final-cta-lead"), style="quote")
        emit(doc, P, S, "CTA button", final.find("a", class_="btn"), style="body")

    emit_alts(doc, soup, P)
    emit_footer_block(doc, soup, P)


def emit_about(doc, soup: BeautifulSoup):
    P = "ABOUT"

    emit_page_meta(doc, soup, P)

    # Hero
    S = "Hero"
    chapter_label(doc, P, S)
    hero = soup.select_one(".hero.hero-about")
    if hero:
        emit(doc, P, S, "Kicker", hero.find(class_="kicker"), style="kicker")
        emit(doc, P, S, "H1", hero.find("h1"), style="h1")

    # Story
    S = "The Story"
    chapter_label(doc, P, S)
    story = soup.select_one(".story-body")
    if story:
        for i, p in enumerate(story.find_all("p"), 1):
            slot = f"Paragraph {i}"
            if "story-close" in (p.get("class") or []):
                slot = f"Paragraph {i} (closing)"
            emit(doc, P, S, slot, p, style="body")

    # Past cars
    S = "Past cars timeline"
    chapter_label(doc, P, S)
    past = soup.select_one(".past-cars")
    if past:
        emit(doc, P, S, "Kicker", past.find(class_="kicker"), style="kicker")
        emit(doc, P, S, "H2", past.find("h2"), style="h2")
        emit(doc, P, S, "Lede", past.find(class_="lede"), style="lede")
        for item in past.select(".timeline-item"):
            year_el = item.find(class_="timeline-year")
            year = year_el.get_text(strip=True) if year_el else ""
            emit(doc, P, S, f"{year} · Title", item.find(class_="timeline-title"), style="h3")
            emit(doc, P, S, f"{year} · Note", item.find(class_="timeline-note"), style="body")
        emit(doc, P, S, "Coda line", past.select_one(".timeline-coda"), style="quote")

    # Currently driving
    S = "Currently driving"
    chapter_label(doc, P, S)
    cur = soup.select_one(".currently-driving")
    if cur:
        emit(doc, P, S, "Kicker", cur.find(class_="kicker"), style="kicker")
        emit(doc, P, S, "H2", cur.find("h2"), style="h2")
        for i, card in enumerate(cur.select(".car-card"), 1):
            emit(doc, P, S, f"Car {i} · Title", card.find(class_="car-title"), style="h3")
            for_sale = card.find(class_="for-sale")
            if for_sale:
                emit(doc, P, S, f"Car {i} · Badge", for_sale, style="body")
            emit(doc, P, S, f"Car {i} · Caption", card.find(class_="car-caption"), style="body")

    # Illustrations
    S = "From the sketchbook (illustrations)"
    chapter_label(doc, P, S)
    ill = soup.select_one(".illustrations")
    if ill:
        emit(doc, P, S, "Kicker", ill.find(class_="kicker"), style="kicker")
        emit(doc, P, S, "H2", ill.find("h2"), style="h2")
        emit(doc, P, S, "Lede", ill.find(class_="lede"), style="lede")
        for i, card in enumerate(ill.select(".illustration-card"), 1):
            cap = card.find("figcaption")
            emit(doc, P, S, f"Illustration {i} · Caption", cap, style="body")

    # Final CTA
    S = "Final CTA"
    chapter_label(doc, P, S)
    final = soup.select_one(".final-cta")
    if final:
        emit(doc, P, S, "Quiet line", final.find(class_="final-cta-quiet"), style="quote")
        emit(doc, P, S, "CTA button", final.find("a", class_="btn"), style="body")

    emit_alts(doc, soup, P)


def emit_process(doc, soup: BeautifulSoup):
    P = "PROCESS"

    emit_page_meta(doc, soup, P)

    # Hero
    S = "Hero"
    chapter_label(doc, P, S)
    hero = soup.select_one(".hero.hero-process")
    if hero:
        emit(doc, P, S, "Kicker", hero.find(class_="kicker"), style="kicker")
        emit(doc, P, S, "H1", hero.find("h1"), style="h1")
        emit(doc, P, S, "Lede", hero.find(class_="hero-lede"), style="lede")
        anchors = hero.select(".hero-anchor-nav .btn")
        for i, a in enumerate(anchors, 1):
            emit_text(doc, P, S, f"Anchor button {i}", a.get_text(" ", strip=True), style="body")

    # Buying
    S = "Buying — six-step timeline"
    chapter_label(doc, P, S)
    buying = soup.select_one("#buying")
    if buying:
        emit(doc, P, S, "Kicker", buying.find(class_="kicker"), style="kicker")
        emit(doc, P, S, "H2", buying.find("h2"), style="h2")
        emit(doc, P, S, "Lede", buying.find(class_="lede"), style="lede")
        for step in buying.select(".timeline-step"):
            circle = step.find(class_="step-circle")
            num = circle.get_text(strip=True) if circle else ""
            emit(doc, P, S, f"Step {num} · Name", step.find(class_="step-name"), style="h3")
            emit(doc, P, S, f"Step {num} · Marker", step.find(class_="step-marker"), style="caption")
            emit(doc, P, S, f"Step {num} · Body", step.find(class_="step-body"), style="body")

    # Selling
    S = "Selling — three-step inverse arc"
    chapter_label(doc, P, S)
    selling = soup.select_one("#selling")
    if selling:
        emit(doc, P, S, "Kicker", selling.find(class_="kicker"), style="kicker")
        emit(doc, P, S, "H2", selling.find("h2"), style="h2")
        emit(doc, P, S, "Lede", selling.find(class_="lede"), style="lede")
        emit(doc, P, S, "Intro paragraph", selling.find(class_="sell-arc-intro"), style="body")
        for step in selling.select(".sell-step"):
            num_el = step.find(class_="sell-num")
            num = num_el.get_text(strip=True) if num_el else ""
            emit(doc, P, S, f"Step {num} · Name", step.find(class_="step-name"), style="h3")
            emit(doc, P, S, f"Step {num} · Marker", step.find(class_="step-marker"), style="caption")
            emit(doc, P, S, f"Step {num} · Body", step.find(class_="step-body"), style="body")

    # Pricing
    S = "Pricing"
    chapter_label(doc, P, S)
    pricing = soup.select_one(".process-pricing")
    if pricing:
        emit(doc, P, S, "Kicker", pricing.find(class_="kicker"), style="kicker")
        emit(doc, P, S, "H2", pricing.find("h2"), style="h2")
        body = pricing.find(class_="pricing-body")
        if body:
            for i, p in enumerate(body.find_all("p", recursive=False), 1):
                cls = p.get("class") or []
                if "pricing-teaser" in cls:
                    emit(doc, P, S, "Teaser line", p, style="quote")
                else:
                    emit(doc, P, S, f"Body {i}", p, style="body")

    # FAQ
    S = "FAQ"
    chapter_label(doc, P, S)
    faq = soup.select_one(".process-faq")
    if faq:
        emit(doc, P, S, "Kicker", faq.find(class_="kicker"), style="kicker")
        emit(doc, P, S, "H2", faq.find("h2"), style="h2")
        for i, item in enumerate(faq.select(".faq-item"), 1):
            q = item.select_one(".faq-q-text")
            a_inner = item.select_one(".faq-a-inner")
            emit(doc, P, S, f"Q{i}", q, style="h3")
            if a_inner:
                a_paras = a_inner.find_all("p")
                if len(a_paras) == 1:
                    emit(doc, P, S, f"A{i}", a_paras[0], style="body")
                else:
                    for j, p in enumerate(a_paras, 1):
                        emit(doc, P, S, f"A{i} · Paragraph {j}", p, style="body")

    # Final CTA
    S = "Final CTA"
    chapter_label(doc, P, S)
    final = soup.select_one(".final-cta")
    if final:
        emit(doc, P, S, "Lead line", final.find(class_="final-cta-line"), style="lede")
        emit(doc, P, S, "CTA button", final.find("a", class_="btn"), style="body")

    emit_alts(doc, soup, P)


def emit_gallery(doc, soup: BeautifulSoup):
    P = "GALLERY"

    emit_page_meta(doc, soup, P)

    # Hero
    S = "Hero"
    chapter_label(doc, P, S)
    hero = soup.select_one(".gallery-hero")
    if hero:
        emit(doc, P, S, "Kicker", hero.find(class_="kicker"), style="kicker")
        emit(doc, P, S, "H1", hero.find("h1"), style="h1")
        emit(doc, P, S, "Lede", hero.find(class_="gallery-hero-lede"), style="lede")

    # Cards
    S = "Gallery cards"
    chapter_label(doc, P, S)
    grid = soup.select_one(".gallery-grid")
    if grid:
        for i, card in enumerate(grid.select(".gallery-card"), 1):
            emit(doc, P, S, f"Card {i} · Title", card.find(class_="car-title"), style="h3")
            emit(doc, P, S, f"Card {i} · Spotted", card.find(class_="spotted"), style="caption")
            emit(doc, P, S, f"Card {i} · Note", card.find(class_="note"), style="body")

    # Final CTA
    S = "Final CTA"
    chapter_label(doc, P, S)
    final = soup.select_one(".final-cta")
    if final:
        emit(doc, P, S, "Kicker", final.find(class_="final-cta-kicker"), style="kicker")
        emit(doc, P, S, "Lead line", final.find(class_="final-cta-lead"), style="lede")
        emit(doc, P, S, "CTA button", final.find("a", class_="btn"), style="body")

    emit_alts(doc, soup, P)


def emit_contact(doc, soup: BeautifulSoup):
    P = "CONTACT"

    emit_page_meta(doc, soup, P)

    # Hero
    S = "Hero"
    chapter_label(doc, P, S)
    hero = soup.select_one(".contact-hero")
    if hero:
        emit(doc, P, S, "Kicker", hero.find(class_="kicker"), style="kicker")
        emit(doc, P, S, "H1", hero.find("h1"), style="h1")
        emit(doc, P, S, "Lede", hero.find(class_="contact-hero-lede"), style="lede")

    # What happens next
    S = "What happens next"
    chapter_label(doc, P, S)
    wn = soup.select_one(".what-next")
    if wn:
        emit(doc, P, S, "Kicker", wn.find(class_="kicker"), style="kicker")
        for step in wn.select(".next-step"):
            num_el = step.find(class_="num")
            num = num_el.get_text(strip=True) if num_el else ""
            emit(doc, P, S, f"Step {num} · Body", step.find(class_="body"), style="body")
        emit(doc, P, S, "Coda line", wn.find(class_="next-coda"), style="quote")

    # Form
    S = "Intake form"
    chapter_label(doc, P, S)
    form = soup.find("form", class_="contact-form")
    if form:
        for field in form.select(".form-field"):
            label = field.find("label")
            label_text = label.get_text(" ", strip=True) if label else "field"
            slot_base = f"Field — {label_text}"
            emit(doc, P, S, f"{slot_base} · Label", label, style="body")
            hint = field.find(class_="form-hint")
            if hint:
                emit(doc, P, S, f"{slot_base} · Hint", hint, style="caption")
            select = field.find("select")
            if select:
                opts = [opt.get_text(strip=True) for opt in select.find_all("option") if opt.get_text(strip=True)]
                emit_text(doc, P, S, f"{slot_base} · Dropdown options", "  ·  ".join(opts), style="body")
        emit(doc, P, S, "Submit button", form.select_one(".form-actions .btn"), style="body")
        emit(doc, P, S, "Below-button microcopy", form.select_one(".form-actions .form-meta"), style="quote")

    fallback = soup.select_one(".email-fallback")
    if fallback:
        emit(doc, P, S, "Email fallback line", fallback, style="body")

    emit_alts(doc, soup, P)


def emit_thanks(doc, soup: BeautifulSoup):
    P = "THANKS"

    emit_page_meta(doc, soup, P)

    # Hero
    S = "Hero (confirmation)"
    chapter_label(doc, P, S)
    hero = soup.select_one(".thanks-hero")
    if hero:
        emit(doc, P, S, "Kicker", hero.find(class_="kicker"), style="kicker")
        emit(doc, P, S, "H1", hero.find("h1"), style="h1")
        emit(doc, P, S, "Lede", hero.find(class_="thanks-hero-lede"), style="lede")
        actions = hero.select_one(".thanks-actions")
        if actions:
            emit(doc, P, S, "Primary button", actions.find("a", class_="btn"), style="body")
            emit(doc, P, S, "Secondary link", actions.find(class_="thanks-secondary-link"), style="body")

    # While you wait
    S = "While you wait"
    chapter_label(doc, P, S)
    wyw = soup.select_one(".while-you-wait")
    if wyw:
        emit(doc, P, S, "Kicker", wyw.find(class_="kicker"), style="kicker")
        emit(doc, P, S, "H2", wyw.find("h2"), style="h2")
        for i, card in enumerate(wyw.select(".while-you-wait-card"), 1):
            emit(doc, P, S, f"Card {i} · Title", card.find("h3"), style="h3")
            emit(doc, P, S, f"Card {i} · Description", card.find("p"), style="body")

    emit_alts(doc, soup, P)


def emit_404(doc, soup: BeautifulSoup):
    P = "404"

    emit_page_meta(doc, soup, P)

    # Hero
    S = "Hero (lost-page)"
    chapter_label(doc, P, S)
    hero = soup.select_one(".notfound-hero")
    if hero:
        emit(doc, P, S, "Kicker", hero.find(class_="kicker"), style="kicker")
        emit(doc, P, S, "H1", hero.find("h1"), style="h1")
        emit(doc, P, S, "Lede (with inline links)", hero.find(class_="notfound-hero-lede"), style="lede")
        emit(doc, P, S, "CTA button", hero.find("a", class_="btn"), style="body")

    # Try one of these instead
    S = "Try one of these instead"
    chapter_label(doc, P, S)
    wyw = soup.select_one(".while-you-wait")
    if wyw:
        emit(doc, P, S, "Kicker", wyw.find(class_="kicker"), style="kicker")
        emit(doc, P, S, "H2", wyw.find("h2"), style="h2")
        for i, card in enumerate(wyw.select(".while-you-wait-card"), 1):
            emit(doc, P, S, f"Card {i} · Title", card.find("h3"), style="h3")
            emit(doc, P, S, f"Card {i} · Description", card.find("p"), style="body")

    emit_alts(doc, soup, P)


# ─────────────────────────────────────────────────────────────────────────────
# Cover page + assemble
# ─────────────────────────────────────────────────────────────────────────────


def add_page_break(doc):
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)


def add_cover(doc):
    # Title
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("The & Garage")
    r.font.size = Pt(28)
    r.font.bold = True
    r.font.color.rgb = INK
    p.paragraph_format.space_before = Pt(60)

    # Subtitle
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Site copy export")
    r.font.size = Pt(16)
    r.font.color.rgb = OXBLOOD
    r.font.bold = True

    # Tag line
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("For copy review and editing — outside Replit")
    r.font.size = Pt(11)
    r.font.color.rgb = MUTED
    r.italic = True
    p.paragraph_format.space_after = Pt(36)

    # Short body intro — this is editable workflow guidance, brief.
    intro = (
        "This document contains every piece of editable copy on the public "
        "site, in nav order: Home, About Tim, How it works, Gallery, "
        "Contact, the Contact thank-you page, and the 404 page. Each "
        "editable block is preceded by a short ID label in the form  "
        "PAGE · Section · Slot  (for example, \"HOME · Hero · H1\" or "
        "\"PROCESS · FAQ · Q3\"). Edit the copy below each label; do not "
        "edit the labels themselves."
    )
    add_text_paragraph(doc, intro, style="body")

    # Footnotes-style separator + tone notes block — small, indented, set
    # apart from the body so the editor can see at a glance these are
    # guidance, not text to edit.
    sep = doc.add_paragraph()
    sep.paragraph_format.space_before = Pt(24)
    sep_run = sep.add_run("— Tone notes (do not edit) —")
    sep_run.font.size = Pt(8)
    sep_run.font.bold = True
    sep_run.font.color.rgb = MUTED
    sep.alignment = WD_ALIGN_PARAGRAPH.CENTER

    notes_lines = [
        "Year ranges always read \"to\" (e.g., 1966 to 1999). Never use a dash for a year range.",
        "The brand wordmark renders the ampersand as a feature glyph; writing it as \"&\" in this document is fine.",
        "Italic is reserved for emotional emphasis only — usually a single word or short phrase. Where you see an italic word in a sentence, keep the italic on the same word, or move the italic onto whichever word now carries the emphasis.",
        "Em dashes (—) are stylistic; en dashes (–) are not used.",
        "Image alt text is read by screen readers and indexed by search engines. Keep alts factual and short.",
    ]
    for line in notes_lines:
        n = doc.add_paragraph()
        n.paragraph_format.left_indent = Pt(36)
        n.paragraph_format.right_indent = Pt(36)
        n.paragraph_format.space_after = Pt(2)
        marker = n.add_run("•  ")
        marker.font.size = Pt(8)
        marker.font.color.rgb = MUTED
        body_run = n.add_run(line)
        body_run.font.size = Pt(8)
        body_run.italic = True
        body_run.font.color.rgb = MUTED

    add_page_break(doc)


def main():
    pages = [
        ("index.html", emit_home),
        ("about/index.html", emit_about),
        ("process/index.html", emit_process),
        ("gallery/index.html", emit_gallery),
        ("contact/index.html", emit_contact),
        ("contact/thanks/index.html", emit_thanks),
        ("404.html", emit_404),
    ]

    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Georgia"
    style.font.size = Pt(11)

    add_cover(doc)

    for i, (rel, fn) in enumerate(pages):
        soup = load(rel)
        fn(doc, soup)
        if i < len(pages) - 1:
            add_page_break(doc)

    doc.save(str(OUTPUT_PATH))
    print(f"Wrote {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
