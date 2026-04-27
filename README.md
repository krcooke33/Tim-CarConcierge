# The & Garage

An acquisition concierge for enthusiasts buying classic and modern-classic cars from 1966 to 1999. End-to-end service: intake → search → vet → negotiate → transport → handoff. Tim Young, operator. Sibling brand to [The & Network](https://timyoungtalent.com/).

This repo holds the brand strategy, brand exploration, mood board, and the spec for the V1 website.

---

## For developers / Replit AI

**Start here:** [`BRIEF.md`](./BRIEF.md) — the full site specification. Read it in full before generating code.

The styled HTML version of the brief lives at [`site-brief.html`](./site-brief.html) for human review; `BRIEF.md` is the canonical text source.

### Quick spec summary

- **Stack:** Static HTML + CSS + minimal JS. **No frameworks.** No build tools.
- **Pages (V1):** 5 — Home · About Tim · How it works · Gallery · Start a conversation
- **Hosting:** GitHub Pages (existing) or Replit Deploy.
- **Forms:** Airtable embed (no custom form handling).
- **Domain:** `andgarage.com` (assumed — confirm).
- **Era:** 1966 to 1999. Always written as "to" — never em-dash, hyphen, or slash.
- **Brand non-negotiables:** see BRIEF.md §04.

### Repo structure

```
Tim-CarConcierge/
├── README.md                 (this file)
├── BRIEF.md                  (canonical site spec — for AI agents)
├── site-brief.html           (styled brief — for human review)
├── business-plan.html        (strategic plan)
├── conversation-guide.html   (POV / network outreach guide)
├── competitor-research.html  (competitive scan)
├── brand-exploration.html    (brand iteration history)
├── mood-board.html           (visual mood + photography direction)
├── index.html                (placeholder home page — to be rebuilt per BRIEF.md)
└── img/
    ├── hero/                 (home + about page heroes)
    ├── tim/                  (Tim's portrait + current cars)
    ├── gallery/              (27 cars in the wild)
    └── mood/                 (mood board references — NOT for site use)
```

### Build approach

The site is being built by Kendra in Replit with Replit's AI agent. Pattern: small chunks, confirmation gates between steps. Each chunk references specific BRIEF.md sections by number. The agent should:

1. Read `BRIEF.md` in full before any code.
2. Build foundations first (file structure, CSS tokens, components) — see §04 and §07.
3. Build pages section by section, each per its §06 sub-brief.
4. Use real copy from §08 verbatim — never paraphrase.
5. Pause at each chunk for human review.

### Hands-off files (do not modify)

These are internal working documents for Tim and Kendra. The agent should **not** modify, delete, or rebuild them. They are reference material the spec is drawn from.

- `BRIEF.md` (the spec — read, don't edit)
- `README.md` (this file — read, don't edit)
- `business-plan.html`
- `conversation-guide.html`
- `competitor-research.html`
- `brand-exploration.html`
- `mood-board.html`
- `site-brief.html`

The agent's job is to **create or replace** the V1 site files per BRIEF.md:

- `index.html` (will be rebuilt as the V1 home page — current placeholder is a working-docs landing page)
- `about/index.html`, `process/index.html`, `gallery/index.html`, `contact/index.html`
- `404.html`
- `css/tokens.css`, `css/base.css`, `css/components.css`
- `js/site.js`

---

## For Tim & Kendra

**Working docs in this repo (already complete):**

- [Business plan](./business-plan.html) — positioning, pricing, year-one roadmap
- [POV conversation guide](./conversation-guide.html) — talking points for network outreach
- [Competitor research](./competitor-research.html) — four-player landscape scan
- [Brand exploration](./brand-exploration.html) — & Garage brand iteration
- [Mood board](./mood-board.html) — palette, type, photography direction
- [Site brief](./site-brief.html) — what we're building (V1 spec)

**Status:** Brief complete. Photography in place (Tim's portrait, 3 current cars, 27 gallery scouting items, 2 hero images). Next step: begin V1 build in Replit.

**Open items before launch:**

- Confirm domain (`andgarage.com` or alternative)
- Set up Airtable form for Contact page (Tim, ~15 min)
- Gather 3 – 5 quotes from past matches (Tim, ongoing — see template provided)
- Compress hero images (currently large — ~5MB) to ~300 – 500KB before final commit
- Fill placeholder copy in gallery cards (location + Tim's note per card)

**Phase 2 backlog** (don't build now): Instagram embed, newsletter, journal/blog, Airtable-driven gallery feed. See BRIEF.md §11 – 12.

---

*Private · internal · not for distribution. © 2026 The & Garage.*
