# The & Garage

A classic car acquisition concierge service website for Tim Young. Static HTML + CSS + minimal JS — no frameworks, no build tools.

## Project Overview

- **Site**: The & Garage — classic car acquisition concierge (1966 to 1999 era)
- **Operator**: Tim Young
- **Stack**: Static HTML, CSS3, minimal vanilla JS
- **Fonts**: Fraunces (serif headings) + DM Sans (body)
- **Colors**: `--ink-dark: #131426`, `--cream: #f7f3ec`, `--oxblood: #6e2828`, `--warm: #c57b3c`

## Pages (V1 — per BRIEF.md)

- Home
- About Tim
- How it works
- Gallery
- Contact

## Running the Project

Served via Python's built-in HTTP server on port 5000:

```
python3 -m http.server 5000 --bind 0.0.0.0
```

## Shared Components

Both the nav and footer are defined in `index.html` and must be copied consistently to every page:

- **Nav** (`<nav class="site-nav">`) — fixed dark bar, wordmark left, 4 links right, hamburger at <760px
- **Footer** (`<footer class="site-footer">`) — 3-column dark footer (brand | links+email | lineage), bottom copyright bar
- **Mobile toggle** — wired in `js/site.js`; toggling `.is-open` on `#nav-drawer` and `.nav-open` on `#site-nav`

## Key Files

- `BRIEF.md` — Canonical site specification (read before making changes)
- `index.html` — Component test page (to be rebuilt as Home); contains nav + footer partials
- `css/components.css` — All reusable component styles including `.site-nav` and `.site-footer`
- `js/site.js` — Mobile hamburger toggle
- `site-brief.html` — Styled HTML version of the brief for human review
- `img/` — Assets: `gallery/` (27 scouting photos), `hero/`, `tim/`, `mood/`

## Constraints (from BRIEF.md §10)

- No frameworks (React, Vue, etc.)
- No build tools (Vite, Webpack, Tailwind)
- No custom form handling — use Airtable embeds
- Always write year ranges as "1966 to 1999" (never dashes)
- Tim is the protagonist on every page
