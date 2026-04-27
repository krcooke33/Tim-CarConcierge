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

## Key Files

- `BRIEF.md` — Canonical site specification (read before making changes)
- `index.html` — Current working docs landing page (to be rebuilt as Home)
- `site-brief.html` — Styled HTML version of the brief for human review
- `img/` — Assets: `gallery/` (27 scouting photos), `hero/`, `tim/`, `mood/`

## Constraints (from BRIEF.md §10)

- No frameworks (React, Vue, etc.)
- No build tools (Vite, Webpack, Tailwind)
- No custom form handling — use Airtable embeds
- Always write year ranges as "1966 to 1999" (never dashes)
- Tim is the protagonist on every page
