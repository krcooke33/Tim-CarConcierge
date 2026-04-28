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

Output: copy-export.docx in the project root.
"""

from __future__ import annotations

import os
import sys
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


def load(rel_path: str) -> BeautifulSoup:
    with (PROJECT_ROOT / rel_path).open("r", encoding="utf-8") as f:
        return BeautifulSoup(f.read(), "html.parser")


def normalize_text(s: str) -> str:
    """Collapse whitespace; the entity decoding is already done by BS4."""
    if s is None:
        return ""
    return " ".join(s.split())


def add_inline_runs(paragraph, node, italic_inherited: bool = False, bold_inherited: bool = False):
    """
    Walk a BeautifulSoup node and add runs to the paragraph, preserving
    italic (<em>, <i>) and bold (<strong>, <b>). The .brand-amp span renders
    as a literal "&". Anchors render as their text content. Decorative
    spans (.faq-icon, .arrow with hidden glyphs) keep their text content
    only when meaningful.
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
    """Collapse multiple whitespace within / between runs of a paragraph."""
    text = "".join(r.text for r in paragraph.runs)
    collapsed = " ".join(text.split())
    if text == collapsed:
        return
    # Rebuild runs, preserving italic/bold per char isn't worth it — instead,
    # walk runs and rewrite each run's text by mapping.
    # Simple approach: rewrite first run = collapsed, drop the rest.
    # But that loses italic spans. So we do a smarter mapping: walk runs and
    # collapse only if the global collapse changes total length minimally
    # (multiple spaces → one). We rewrite each run by replacing internal
    # multi-whitespace with single space, and trim leading/trailing per global
    # position.
    # Implementation: walk runs left-to-right, track whether previous char was
    # space. For each run, build a new text where consecutive whitespace
    # collapses (across run boundaries) and leading/trailing of overall string
    # is trimmed.
    prev_space = True  # treat start of paragraph as if preceded by space → trims leading
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
    # Trim trailing whitespace from final non-empty run
    for i in range(len(new_texts) - 1, -1, -1):
        if new_texts[i]:
            new_texts[i] = new_texts[i].rstrip()
            break
    for r, t in zip(paragraph.runs, new_texts):
        r.text = t


def section_label(doc, page_label: str, section: str, slot: str = ""):
    """
    Add a small grey label like:
        HOME · Hero · Headline (H1)
    """
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(2)
    parts = [page_label, section]
    if slot:
        parts.append(slot)
    text = "  ·  ".join(parts).upper()
    run = p.add_run(text)
    run.font.size = Pt(8)
    run.font.color.rgb = MUTED
    run.font.bold = True
    return p


def add_copy_paragraph(doc, html_node, *, style: str = "body", placeholder: str = ""):
    """
    Add a copy paragraph extracted from html_node (or a literal placeholder
    if html_node is None and placeholder is provided).

    Styles:
      body      — default
      h1        — site H1
      h2        — site H2
      h3        — site H3
      kicker    — small all-caps
      lede      — slightly larger body
      caption   — smaller muted
      quote     — italic blockquote-ish
      meta      — small grey (used for meta description, alt text, etc.)
    """
    p = doc.add_paragraph()

    if html_node is not None:
        add_inline_runs(p, html_node)
        collapse_whitespace_runs(p)
    elif placeholder:
        p.add_run(placeholder)

    if not p.runs or all(not r.text for r in p.runs):
        # Drop empty paragraph
        para_el = p._element
        para_el.getparent().remove(para_el)
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
        for r in p.runs:
            r.font.size = Pt(9)
            r.font.bold = True
            r.font.color.rgb = OXBLOOD
            r.text = r.text.upper()
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
        # Do NOT force italic here — preserve the selective <em> emphasis
        # already captured at the run level by add_inline_runs(). Use only
        # indentation and color to give the paragraph a quote feel.
        for r in p.runs:
            r.font.size = Pt(11)
            r.font.color.rgb = INK
        pf.left_indent = Pt(18)
        pf.space_before = Pt(2)
        pf.space_after = Pt(4)
    elif style == "meta":
        for r in p.runs:
            r.font.size = Pt(9)
            r.font.color.rgb = MUTED
        pf.space_before = Pt(0)
        pf.space_after = Pt(2)
    else:  # body
        for r in p.runs:
            r.font.size = Pt(11)
            r.font.color.rgb = INK
        pf.space_before = Pt(2)
        pf.space_after = Pt(6)

    return p


def add_text_paragraph(doc, text: str, *, style: str = "body"):
    """Convenience: add a paragraph from a plain string."""
    if not text:
        return None
    soup = BeautifulSoup(f"<root>{text}</root>", "html.parser")
    return add_copy_paragraph(doc, soup.root, style=style)


# ─────────────────────────────────────────────────────────────────────────────
# Page-by-page extractors
# Each extractor receives the loaded BeautifulSoup, the doc, and the page
# label. They emit labeled sections in reading order.
# ─────────────────────────────────────────────────────────────────────────────


def add_page_meta(doc, soup: BeautifulSoup, page_label: str):
    """Title, meta description, OG title/description for the page."""
    section_label(doc, page_label, "Page metadata", "Browser tab + share previews")

    title = soup.find("title")
    if title:
        add_text_paragraph(doc, "Browser title: ", style="caption")
        add_copy_paragraph(doc, title, style="body")

    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and meta_desc.get("content"):
        add_text_paragraph(doc, "Meta description (search-engine summary): ", style="caption")
        add_text_paragraph(doc, meta_desc["content"], style="body")

    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content"):
        add_text_paragraph(doc, "Social-share title: ", style="caption")
        add_text_paragraph(doc, og_title["content"], style="body")

    og_desc = soup.find("meta", attrs={"property": "og:description"})
    if og_desc and og_desc.get("content"):
        add_text_paragraph(doc, "Social-share description: ", style="caption")
        add_text_paragraph(doc, og_desc["content"], style="body")


def emit_alts(doc, soup: BeautifulSoup, page_label: str):
    """Collect every non-empty <img alt=""> on the page, list them at the end."""
    alts = []
    for img in soup.find_all("img"):
        alt = (img.get("alt") or "").strip()
        if alt:
            alts.append(alt)
    if not alts:
        return
    section_label(doc, page_label, "Image alt text", "Read by screen readers + search engines")
    for a in alts:
        add_text_paragraph(doc, "• " + a, style="caption")


def emit_footer(doc, soup: BeautifulSoup, page_label: str):
    """Footer microcopy — same on every page; emit once on the first page only."""
    footer = soup.find("footer", class_="site-footer")
    if not footer:
        return
    section_label(doc, page_label, "Site footer", "Same on every page")

    byline = footer.find(class_="footer-byline")
    if byline:
        add_text_paragraph(doc, "Byline: ", style="caption")
        add_copy_paragraph(doc, byline, style="body")

    year_mark_nums = footer.select(".year-mark .num")
    connector = footer.select_one(".year-mark .connector")
    if year_mark_nums and connector:
        years = f"'{year_mark_nums[0].get_text(strip=True)} {connector.get_text(strip=True)} '{year_mark_nums[1].get_text(strip=True)}"
        add_text_paragraph(doc, "Era mark (lockup): ", style="caption")
        add_text_paragraph(doc, years, style="body")

    links_ul = footer.select_one(".footer-links ul")
    if links_ul:
        add_text_paragraph(doc, "Footer nav labels: ", style="caption")
        labels = [li.get_text(" ", strip=True) for li in links_ul.find_all("li")]
        add_text_paragraph(doc, " · ".join(labels), style="body")

    email_link = footer.select_one(".footer-email")
    if email_link:
        add_text_paragraph(doc, "Email link label: ", style="caption")
        add_copy_paragraph(doc, email_link, style="body")

    lineage = footer.select_one(".footer-lineage")
    if lineage:
        add_text_paragraph(doc, "Lineage line: ", style="caption")
        add_copy_paragraph(doc, lineage.find("p"), style="body")

    bottom_left = footer.select_one(".footer-bottom-left")
    bottom_right = footer.select_one(".footer-bottom-right")
    if bottom_left:
        add_text_paragraph(doc, "Footer bottom left (copyright): ", style="caption")
        add_copy_paragraph(doc, bottom_left, style="body")
    if bottom_right:
        add_text_paragraph(doc, "Footer bottom right (region + era): ", style="caption")
        add_copy_paragraph(doc, bottom_right, style="body")


def emit_nav(doc, soup: BeautifulSoup, page_label: str):
    """Site nav labels — same on every page; emit once on the first page only."""
    nav = soup.find("nav", class_="site-nav")
    if not nav:
        return
    section_label(doc, page_label, "Site navigation", "Same on every page")

    wordmark = nav.find(class_="nav-wordmark")
    if wordmark:
        add_text_paragraph(doc, "Wordmark (top-left): ", style="caption")
        add_copy_paragraph(doc, wordmark, style="body")

    links_ul = nav.find("ul", class_="nav-links")
    if links_ul:
        add_text_paragraph(doc, "Nav link labels: ", style="caption")
        labels = [li.get_text(" ", strip=True) for li in links_ul.find_all("li")]
        add_text_paragraph(doc, " · ".join(labels), style="body")


# ─── HOME ────────────────────────────────────────────────────────────────────


def emit_home(doc, soup: BeautifulSoup):
    P = "Home"

    add_page_meta(doc, soup, P)
    emit_nav(doc, soup, P)

    # Hero
    section_label(doc, P, "Hero", "Top of page over a black-and-white photo")
    hero = soup.find("header", class_="hero")
    wm = hero.select_one(".hero-wordmark")
    h1 = hero.select_one("h1")
    tagline = hero.select_one(".hero-tagline")
    btn = hero.select_one(".btn")
    if wm:
        add_text_paragraph(doc, "Wordmark: ", style="caption")
        add_copy_paragraph(doc, wm, style="body")
    if h1:
        add_text_paragraph(doc, "Headline (H1): ", style="caption")
        add_copy_paragraph(doc, h1, style="h1")
    if tagline:
        add_text_paragraph(doc, "Tagline: ", style="caption")
        add_copy_paragraph(doc, tagline, style="lede")
    if btn:
        add_text_paragraph(doc, "Button label: ", style="caption")
        add_copy_paragraph(doc, btn, style="body")
    add_text_paragraph(doc, "Era mark (decal): ", style="caption")
    add_text_paragraph(doc, "'66  '99", style="body")

    # The problem
    section_label(doc, P, "Section 1 — The problem")
    prob = soup.find("section", class_="home-problem")
    if prob:
        h2 = prob.find("h2")
        lede = prob.find("p", class_="lede")
        body_ps = [p for p in prob.find_all("p") if "lede" not in (p.get("class") or [])]
        if h2:
            add_text_paragraph(doc, "Headline (H2): ", style="caption")
            add_copy_paragraph(doc, h2, style="h2")
        if lede:
            add_text_paragraph(doc, "Lede: ", style="caption")
            add_copy_paragraph(doc, lede, style="lede")
        for i, p in enumerate(body_ps, 1):
            add_text_paragraph(doc, f"Body paragraph {i}: ", style="caption")
            add_copy_paragraph(doc, p, style="body")

    # What we do
    section_label(doc, P, "Section 2 — What The & Garage does")
    wwd = soup.find("section", class_="what-we-do")
    if wwd:
        add_text_paragraph(doc, "Headline (H2): ", style="caption")
        add_copy_paragraph(doc, wwd.find("h2"), style="h2")
        lede = wwd.find("p", class_="lede")
        if lede:
            add_text_paragraph(doc, "Lede: ", style="caption")
            add_copy_paragraph(doc, lede, style="lede")
        for card in wwd.select(".service-card"):
            num = card.select_one(".card-num")
            h3 = card.find("h3")
            body = card.find("p")
            label = f"Card {num.get_text(strip=True) if num else ''}"
            add_text_paragraph(doc, label, style="caption")
            if h3:
                add_copy_paragraph(doc, h3, style="h3")
            if body:
                add_copy_paragraph(doc, body, style="body")
        cta_btn = wwd.select_one(".what-we-do-cta .btn")
        if cta_btn:
            add_text_paragraph(doc, "Button label: ", style="caption")
            add_copy_paragraph(doc, cta_btn, style="body")

    # Tim signature
    section_label(doc, P, "Section 3 — Meet Tim (signature)")
    sig = soup.find("section", class_="home-tim-signature")
    if sig:
        kicker = sig.find(class_="kicker")
        body = sig.find(class_="signature-body")
        btn = sig.find("a", class_="btn")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if body:
            add_text_paragraph(doc, "Signature body: ", style="caption")
            add_copy_paragraph(doc, body, style="body")
        if btn:
            add_text_paragraph(doc, "Button label: ", style="caption")
            add_copy_paragraph(doc, btn, style="body")

    # Quotes
    section_label(doc, P, "Section 4 — Testimonials")
    quotes = soup.find("section", class_="home-quotes")
    if quotes:
        add_text_paragraph(doc, "Headline (H2): ", style="caption")
        add_copy_paragraph(doc, quotes.find("h2"), style="h2")
        for i, card in enumerate(quotes.select(".quote-card"), 1):
            add_text_paragraph(doc, f"Testimonial {i} — quote: ", style="caption")
            bq = card.find("blockquote")
            if bq:
                add_copy_paragraph(doc, bq, style="quote")
            cite = card.find("cite")
            if cite:
                name = cite.find(class_="name")
                city = cite.find(class_="city")
                car = cite.find(class_="car")
                add_text_paragraph(doc, f"Testimonial {i} — attribution: ", style="caption")
                if name:
                    add_text_paragraph(doc, "Name: " + name.get_text(strip=True), style="body")
                if city:
                    add_text_paragraph(doc, "City: " + city.get_text(strip=True), style="body")
                if car:
                    add_text_paragraph(doc, "Car: " + car.get_text(strip=True), style="body")

    # Gallery teaser
    section_label(doc, P, "Section 5 — Gallery teaser")
    teaser = soup.find("section", class_="home-gallery-teaser")
    if teaser:
        add_text_paragraph(doc, "Headline (H2): ", style="caption")
        add_copy_paragraph(doc, teaser.find("h2"), style="h2")
        for i, card in enumerate(teaser.select(".gallery-card"), 1):
            title = card.find(class_="car-title")
            spotted = card.find(class_="spotted")
            note = card.find(class_="note")
            add_text_paragraph(doc, f"Card {i} — car title: ", style="caption")
            if title:
                add_copy_paragraph(doc, title, style="h3")
            if spotted:
                add_text_paragraph(doc, f"Card {i} — location + month: ", style="caption")
                add_copy_paragraph(doc, spotted, style="caption")
            if note:
                add_text_paragraph(doc, f"Card {i} — note: ", style="caption")
                add_copy_paragraph(doc, note, style="body")
        teaser_link = teaser.select_one(".gallery-teaser-link")
        if teaser_link:
            add_text_paragraph(doc, "Bottom link label: ", style="caption")
            add_copy_paragraph(doc, teaser_link, style="body")

    # Final CTA
    section_label(doc, P, "Section 6 — Final call to action")
    final = soup.find("section", class_="final-cta")
    if final:
        quiet = final.find(class_="final-cta-quiet")
        lead = final.find(class_="final-cta-lead")
        btn = final.find("a", class_="btn")
        if quiet:
            add_text_paragraph(doc, "Quiet line (italic): ", style="caption")
            add_copy_paragraph(doc, quiet, style="quote")
        if lead:
            add_text_paragraph(doc, "Lead line (italic): ", style="caption")
            add_copy_paragraph(doc, lead, style="quote")
        if btn:
            add_text_paragraph(doc, "Button label: ", style="caption")
            add_copy_paragraph(doc, btn, style="body")

    emit_alts(doc, soup, P)
    emit_footer(doc, soup, P)


# ─── ABOUT ──────────────────────────────────────────────────────────────────


def emit_about(doc, soup: BeautifulSoup):
    P = "About Tim"

    add_page_meta(doc, soup, P)

    # Hero
    section_label(doc, P, "Hero", "Tim's portrait")
    hero = soup.select_one(".hero.hero-about")
    if hero:
        kicker = hero.find(class_="kicker")
        h1 = hero.find("h1")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if h1:
            add_text_paragraph(doc, "Headline (H1): ", style="caption")
            add_copy_paragraph(doc, h1, style="h1")

    # Story
    section_label(doc, P, "The Story", "Seven paragraphs, in reading order")
    story = soup.select_one(".story-body")
    if story:
        for i, p in enumerate(story.find_all("p"), 1):
            label = f"Paragraph {i}"
            if "story-close" in (p.get("class") or []):
                label += " (closing — italic)"
            add_text_paragraph(doc, label + ":", style="caption")
            add_copy_paragraph(doc, p, style="body")

    # Past cars
    section_label(doc, P, "Past cars timeline")
    past = soup.select_one(".past-cars")
    if past:
        kicker = past.find(class_="kicker")
        h2 = past.find("h2")
        lede = past.find(class_="lede")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if h2:
            add_text_paragraph(doc, "Headline (H2): ", style="caption")
            add_copy_paragraph(doc, h2, style="h2")
        if lede:
            add_text_paragraph(doc, "Lede: ", style="caption")
            add_copy_paragraph(doc, lede, style="lede")
        for item in past.select(".timeline-item"):
            year = item.find(class_="timeline-year")
            title = item.find(class_="timeline-title")
            note = item.find(class_="timeline-note")
            label = f"Year {year.get_text(strip=True) if year else ''}"
            add_text_paragraph(doc, label + " — title:", style="caption")
            if title:
                add_copy_paragraph(doc, title, style="h3")
            add_text_paragraph(doc, label + " — note:", style="caption")
            if note:
                add_copy_paragraph(doc, note, style="body")
        coda = past.select_one(".timeline-coda")
        if coda:
            add_text_paragraph(doc, "Coda (italic line): ", style="caption")
            add_copy_paragraph(doc, coda, style="quote")

    # Currently driving
    section_label(doc, P, "Currently driving")
    cur = soup.select_one(".currently-driving")
    if cur:
        kicker = cur.find(class_="kicker")
        h2 = cur.find("h2")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if h2:
            add_text_paragraph(doc, "Headline (H2): ", style="caption")
            add_copy_paragraph(doc, h2, style="h2")
        for i, card in enumerate(cur.select(".car-card"), 1):
            for_sale = card.find(class_="for-sale")
            title = card.find(class_="car-title")
            cap = card.find(class_="car-caption")
            add_text_paragraph(doc, f"Car {i} — title:", style="caption")
            if title:
                add_copy_paragraph(doc, title, style="h3")
            if for_sale:
                add_text_paragraph(doc, f"Car {i} — badge:", style="caption")
                add_copy_paragraph(doc, for_sale, style="body")
            add_text_paragraph(doc, f"Car {i} — caption:", style="caption")
            if cap:
                add_copy_paragraph(doc, cap, style="body")

    # Illustrations
    section_label(doc, P, "From the sketchbook (illustrations)")
    ill = soup.select_one(".illustrations")
    if ill:
        kicker = ill.find(class_="kicker")
        h2 = ill.find("h2")
        lede = ill.find(class_="lede")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if h2:
            add_text_paragraph(doc, "Headline (H2): ", style="caption")
            add_copy_paragraph(doc, h2, style="h2")
        if lede:
            add_text_paragraph(doc, "Lede: ", style="caption")
            add_copy_paragraph(doc, lede, style="lede")
        for i, card in enumerate(ill.select(".illustration-card"), 1):
            cap = card.find("figcaption")
            add_text_paragraph(doc, f"Illustration {i} — caption:", style="caption")
            if cap:
                add_copy_paragraph(doc, cap, style="body")

    # Final CTA
    section_label(doc, P, "Final call to action")
    final = soup.select_one(".final-cta")
    if final:
        quiet = final.find(class_="final-cta-quiet")
        btn = final.find("a", class_="btn")
        if quiet:
            add_text_paragraph(doc, "Quiet line (italic): ", style="caption")
            add_copy_paragraph(doc, quiet, style="quote")
        if btn:
            add_text_paragraph(doc, "Button label: ", style="caption")
            add_copy_paragraph(doc, btn, style="body")

    emit_alts(doc, soup, P)


# ─── PROCESS ────────────────────────────────────────────────────────────────


def emit_process(doc, soup: BeautifulSoup):
    P = "How it works"

    add_page_meta(doc, soup, P)

    # Hero
    section_label(doc, P, "Hero", "Image variant — Plymouth Barracuda")
    hero = soup.select_one(".hero.hero-process")
    if hero:
        kicker = hero.find(class_="kicker")
        h1 = hero.find("h1")
        lede = hero.find(class_="hero-lede")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if h1:
            add_text_paragraph(doc, "Headline (H1): ", style="caption")
            add_copy_paragraph(doc, h1, style="h1")
        if lede:
            add_text_paragraph(doc, "Lede: ", style="caption")
            add_copy_paragraph(doc, lede, style="lede")
        anchors = hero.select(".hero-anchor-nav .btn")
        for i, a in enumerate(anchors, 1):
            add_text_paragraph(doc, f"Anchor button {i}:", style="caption")
            text = a.get_text(" ", strip=True).replace("→", "→")
            add_text_paragraph(doc, text, style="body")

    # Buying
    section_label(doc, P, "Buying — six-step timeline")
    buying = soup.select_one("#buying")
    if buying:
        kicker = buying.find(class_="kicker")
        h2 = buying.find("h2")
        lede = buying.find(class_="lede")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if h2:
            add_text_paragraph(doc, "Headline (H2): ", style="caption")
            add_copy_paragraph(doc, h2, style="h2")
        if lede:
            add_text_paragraph(doc, "Lede: ", style="caption")
            add_copy_paragraph(doc, lede, style="lede")
        for step in buying.select(".timeline-step"):
            circle = step.find(class_="step-circle")
            name = step.find(class_="step-name")
            marker = step.find(class_="step-marker")
            body = step.find(class_="step-body")
            num = circle.get_text(strip=True) if circle else ""
            add_text_paragraph(doc, f"Step {num} — name:", style="caption")
            if name:
                add_copy_paragraph(doc, name, style="h3")
            if marker:
                add_text_paragraph(doc, f"Step {num} — timeline marker:", style="caption")
                add_copy_paragraph(doc, marker, style="caption")
            if body:
                add_text_paragraph(doc, f"Step {num} — body:", style="caption")
                add_copy_paragraph(doc, body, style="body")

    # Selling
    section_label(doc, P, "Selling — three-step inverse arc")
    selling = soup.select_one("#selling")
    if selling:
        kicker = selling.find(class_="kicker")
        h2 = selling.find("h2")
        lede = selling.find(class_="lede")
        intro = selling.find(class_="sell-arc-intro")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if h2:
            add_text_paragraph(doc, "Headline (H2): ", style="caption")
            add_copy_paragraph(doc, h2, style="h2")
        if lede:
            add_text_paragraph(doc, "Lede: ", style="caption")
            add_copy_paragraph(doc, lede, style="lede")
        if intro:
            add_text_paragraph(doc, "Intro paragraph: ", style="caption")
            add_copy_paragraph(doc, intro, style="body")
        for step in selling.select(".sell-step"):
            num_el = step.find(class_="sell-num")
            name = step.find(class_="step-name")
            marker = step.find(class_="step-marker")
            body = step.find(class_="step-body")
            num = num_el.get_text(strip=True) if num_el else ""
            add_text_paragraph(doc, f"Step {num} — name:", style="caption")
            if name:
                add_copy_paragraph(doc, name, style="h3")
            if marker:
                add_text_paragraph(doc, f"Step {num} — timeline marker:", style="caption")
                add_copy_paragraph(doc, marker, style="caption")
            if body:
                add_text_paragraph(doc, f"Step {num} — body:", style="caption")
                add_copy_paragraph(doc, body, style="body")

    # Pricing
    section_label(doc, P, "Pricing")
    pricing = soup.select_one(".process-pricing")
    if pricing:
        kicker = pricing.find(class_="kicker")
        h2 = pricing.find("h2")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if h2:
            add_text_paragraph(doc, "Headline (H2): ", style="caption")
            add_copy_paragraph(doc, h2, style="h2")
        body = pricing.find(class_="pricing-body")
        if body:
            for i, p in enumerate(body.find_all("p", recursive=False), 1):
                cls = p.get("class") or []
                label = f"Body paragraph {i}"
                if "pricing-teaser" in cls:
                    label = f"Teaser line (italic, paragraph {i})"
                add_text_paragraph(doc, label + ":", style="caption")
                style = "quote" if "pricing-teaser" in cls else "body"
                add_copy_paragraph(doc, p, style=style)

    # FAQ
    section_label(doc, P, "FAQ")
    faq = soup.select_one(".process-faq")
    if faq:
        kicker = faq.find(class_="kicker")
        h2 = faq.find("h2")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if h2:
            add_text_paragraph(doc, "Headline (H2): ", style="caption")
            add_copy_paragraph(doc, h2, style="h2")
        for i, item in enumerate(faq.select(".faq-item"), 1):
            q = item.select_one(".faq-q-text")
            a = item.select_one(".faq-a-inner")
            add_text_paragraph(doc, f"FAQ {i} — question:", style="caption")
            if q:
                add_copy_paragraph(doc, q, style="h3")
            add_text_paragraph(doc, f"FAQ {i} — answer:", style="caption")
            if a:
                for p in a.find_all("p"):
                    add_copy_paragraph(doc, p, style="body")

    # Final CTA
    section_label(doc, P, "Final call to action")
    final = soup.select_one(".final-cta")
    if final:
        line = final.find(class_="final-cta-line")
        btn = final.find("a", class_="btn")
        if line:
            add_text_paragraph(doc, "Lead line: ", style="caption")
            add_copy_paragraph(doc, line, style="lede")
        if btn:
            add_text_paragraph(doc, "Button label: ", style="caption")
            add_copy_paragraph(doc, btn, style="body")

    emit_alts(doc, soup, P)


# ─── GALLERY ────────────────────────────────────────────────────────────────


def emit_gallery(doc, soup: BeautifulSoup):
    P = "Gallery"

    add_page_meta(doc, soup, P)

    # Hero
    section_label(doc, P, "Hero", "Typographic, dark")
    hero = soup.select_one(".gallery-hero")
    if hero:
        kicker = hero.find(class_="kicker")
        h1 = hero.find("h1")
        lede = hero.find(class_="gallery-hero-lede")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if h1:
            add_text_paragraph(doc, "Headline (H1): ", style="caption")
            add_copy_paragraph(doc, h1, style="h1")
        if lede:
            add_text_paragraph(doc, "Lede: ", style="caption")
            add_copy_paragraph(doc, lede, style="lede")

    # Cards
    section_label(doc, P, "Gallery cards", "One block per spotted car, in display order")
    grid = soup.select_one(".gallery-grid")
    if grid:
        for i, card in enumerate(grid.select(".gallery-card"), 1):
            title = card.find(class_="car-title")
            spotted = card.find(class_="spotted")
            note = card.find(class_="note")
            add_text_paragraph(doc, f"Card {i} — car title:", style="caption")
            if title:
                add_copy_paragraph(doc, title, style="h3")
            if spotted:
                add_text_paragraph(doc, f"Card {i} — location + month:", style="caption")
                add_copy_paragraph(doc, spotted, style="caption")
            if note:
                add_text_paragraph(doc, f"Card {i} — note:", style="caption")
                add_copy_paragraph(doc, note, style="body")

    # Final CTA
    section_label(doc, P, "Final call to action")
    final = soup.select_one(".final-cta")
    if final:
        kicker = final.find(class_="final-cta-kicker")
        lead = final.find(class_="final-cta-lead")
        btn = final.find("a", class_="btn")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if lead:
            add_text_paragraph(doc, "Lead line: ", style="caption")
            add_copy_paragraph(doc, lead, style="lede")
        if btn:
            add_text_paragraph(doc, "Button label: ", style="caption")
            add_copy_paragraph(doc, btn, style="body")

    emit_alts(doc, soup, P)


# ─── CONTACT ────────────────────────────────────────────────────────────────


def emit_contact(doc, soup: BeautifulSoup):
    P = "Contact"

    add_page_meta(doc, soup, P)

    # Hero
    section_label(doc, P, "Hero", "Typographic, dark")
    hero = soup.select_one(".contact-hero")
    if hero:
        kicker = hero.find(class_="kicker")
        h1 = hero.find("h1")
        lede = hero.find(class_="contact-hero-lede")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if h1:
            add_text_paragraph(doc, "Headline (H1): ", style="caption")
            add_copy_paragraph(doc, h1, style="h1")
        if lede:
            add_text_paragraph(doc, "Lede: ", style="caption")
            add_copy_paragraph(doc, lede, style="lede")

    # What happens next
    section_label(doc, P, "What happens next", "Three numbered steps")
    wn = soup.select_one(".what-next")
    if wn:
        kicker = wn.find(class_="kicker")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        for step in wn.select(".next-step"):
            num_el = step.find(class_="num")
            body = step.find(class_="body")
            num = num_el.get_text(strip=True) if num_el else ""
            add_text_paragraph(doc, f"Step {num}:", style="caption")
            if body:
                add_copy_paragraph(doc, body, style="body")
        coda = wn.find(class_="next-coda")
        if coda:
            add_text_paragraph(doc, "Coda (italic line): ", style="caption")
            add_copy_paragraph(doc, coda, style="quote")

    # Form
    section_label(doc, P, "Intake form labels")
    form = soup.find("form", class_="contact-form")
    if form:
        for field in form.select(".form-field"):
            label = field.find("label")
            hint = field.find(class_="form-hint")
            if label:
                add_text_paragraph(doc, "Field label: ", style="caption")
                add_copy_paragraph(doc, label, style="body")
            if hint:
                add_text_paragraph(doc, "Field hint: ", style="caption")
                add_copy_paragraph(doc, hint, style="caption")
            select = field.find("select")
            if select:
                add_text_paragraph(doc, "Dropdown options:", style="caption")
                for opt in select.find_all("option"):
                    val = opt.get_text(strip=True)
                    if val:
                        add_text_paragraph(doc, "• " + val, style="body")
        btn = form.select_one(".form-actions .btn")
        meta = form.select_one(".form-actions .form-meta")
        if btn:
            add_text_paragraph(doc, "Submit button label: ", style="caption")
            add_copy_paragraph(doc, btn, style="body")
        if meta:
            add_text_paragraph(doc, "Below-button microcopy (italic): ", style="caption")
            add_copy_paragraph(doc, meta, style="quote")

    fallback = soup.select_one(".email-fallback")
    if fallback:
        add_text_paragraph(doc, "Email fallback line: ", style="caption")
        add_copy_paragraph(doc, fallback, style="body")

    emit_alts(doc, soup, P)


# ─── CONTACT THANKS ─────────────────────────────────────────────────────────


def emit_thanks(doc, soup: BeautifulSoup):
    P = "Contact — thank you"

    add_page_meta(doc, soup, P)

    section_label(doc, P, "Hero", "Confirmation page, dark")
    hero = soup.select_one(".thanks-hero")
    if hero:
        kicker = hero.find(class_="kicker")
        h1 = hero.find("h1")
        lede = hero.find(class_="thanks-hero-lede")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if h1:
            add_text_paragraph(doc, "Headline (H1): ", style="caption")
            add_copy_paragraph(doc, h1, style="h1")
        if lede:
            add_text_paragraph(doc, "Lede: ", style="caption")
            add_copy_paragraph(doc, lede, style="lede")
        actions = hero.select_one(".thanks-actions")
        if actions:
            btn = actions.find("a", class_="btn")
            secondary = actions.find(class_="thanks-secondary-link")
            if btn:
                add_text_paragraph(doc, "Primary button label: ", style="caption")
                add_copy_paragraph(doc, btn, style="body")
            if secondary:
                add_text_paragraph(doc, "Secondary link label: ", style="caption")
                add_copy_paragraph(doc, secondary, style="body")

    section_label(doc, P, "While you wait", "Three curated link cards")
    wyw = soup.select_one(".while-you-wait")
    if wyw:
        kicker = wyw.find(class_="kicker")
        h2 = wyw.find("h2")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if h2:
            add_text_paragraph(doc, "Headline (H2): ", style="caption")
            add_copy_paragraph(doc, h2, style="h2")
        for i, card in enumerate(wyw.select(".while-you-wait-card"), 1):
            h3 = card.find("h3")
            p = card.find("p")
            add_text_paragraph(doc, f"Card {i} — title:", style="caption")
            if h3:
                add_copy_paragraph(doc, h3, style="h3")
            add_text_paragraph(doc, f"Card {i} — description:", style="caption")
            if p:
                add_copy_paragraph(doc, p, style="body")

    emit_alts(doc, soup, P)


# ─── 404 ────────────────────────────────────────────────────────────────────


def emit_404(doc, soup: BeautifulSoup):
    P = "404 — wrong turn"

    add_page_meta(doc, soup, P)

    section_label(doc, P, "Hero", "Lost-page screen, dark")
    hero = soup.select_one(".notfound-hero")
    if hero:
        kicker = hero.find(class_="kicker")
        h1 = hero.find("h1")
        lede = hero.find(class_="notfound-hero-lede")
        btn = hero.find("a", class_="btn")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if h1:
            add_text_paragraph(doc, "Headline (H1): ", style="caption")
            add_copy_paragraph(doc, h1, style="h1")
        if lede:
            add_text_paragraph(doc, "Lede (with inline links — keep the link words): ", style="caption")
            add_copy_paragraph(doc, lede, style="lede")
        if btn:
            add_text_paragraph(doc, "Button label: ", style="caption")
            add_copy_paragraph(doc, btn, style="body")

    section_label(doc, P, "Try one of these instead", "Three rescue link cards")
    wyw = soup.select_one(".while-you-wait")
    if wyw:
        kicker = wyw.find(class_="kicker")
        h2 = wyw.find("h2")
        if kicker:
            add_text_paragraph(doc, "Kicker: ", style="caption")
            add_copy_paragraph(doc, kicker, style="kicker")
        if h2:
            add_text_paragraph(doc, "Headline (H2): ", style="caption")
            add_copy_paragraph(doc, h2, style="h2")
        for i, card in enumerate(wyw.select(".while-you-wait-card"), 1):
            h3 = card.find("h3")
            p = card.find("p")
            add_text_paragraph(doc, f"Card {i} — title:", style="caption")
            if h3:
                add_copy_paragraph(doc, h3, style="h3")
            add_text_paragraph(doc, f"Card {i} — description:", style="caption")
            if p:
                add_copy_paragraph(doc, p, style="body")

    emit_alts(doc, soup, P)


# ─────────────────────────────────────────────────────────────────────────────
# Cover page + assemble
# ─────────────────────────────────────────────────────────────────────────────


def add_page_break(doc):
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)


def add_cover(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("The & Garage")
    r.font.size = Pt(28)
    r.font.bold = True
    r.font.color.rgb = INK
    p.paragraph_format.space_before = Pt(60)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Site copy export")
    r.font.size = Pt(16)
    r.font.color.rgb = OXBLOOD
    r.font.bold = True

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("For copy review and editing — outside Replit")
    r.font.size = Pt(11)
    r.font.color.rgb = MUTED
    r.italic = True
    p.paragraph_format.space_after = Pt(36)

    intro = (
        "This document contains every piece of editable copy on the public "
        "site, in nav order: Home, About Tim, How it works, Gallery, "
        "Contact, the Contact thank-you page, and the 404 page. Each block "
        "is labeled with its page, section, and slot (for example, "
        "\"HOME · HERO · Headline (H1)\")."
    )
    add_text_paragraph(doc, intro, style="body")

    notes = (
        "House conventions (please preserve when you edit): year ranges "
        "always read \"to\" (1966 to 1999), never with a dash. The brand "
        "wordmark renders the ampersand visually as a feature glyph — "
        "writing it as \"&\" in this doc is fine. Italic is reserved for "
        "emotional emphasis only, so where you see italic in a sentence, "
        "leave the italic on the same word or replace it with the word that "
        "carries the emphasis. Em dashes (—) are stylistic; en dashes (–) "
        "are not used."
    )
    add_text_paragraph(doc, notes, style="body")

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

    # Default font
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
