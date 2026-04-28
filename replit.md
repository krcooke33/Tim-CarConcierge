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
- ~~Gallery~~ — dedicated page hidden as of task #55. The home page's "Cars I'm seeing right now" teaser is kept as a display-only showcase (cards rendered as `<article>`, not links; "See the full gallery →" foot link removed). Re-enable the dedicated page by: restoring the Gallery `<li>` in the top nav and footer of every page, converting the home teaser cards back from `<article class="gallery-card">` to `<a class="gallery-card" href="/gallery/">` and restoring the `gallery-teaser-foot` link, restoring the "Cars in the wild" card in the `while-you-wait` grids on `contact/thanks/index.html` and `404.html`, and removing the `noindex,nofollow` meta from `gallery/index.html`.
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
- `img/` — Assets: `gallery/` (27 scouting photos), `hero/`, `tim/` (current cars + portrait, plus `tim/past/` for the About-page timeline and `tim/illustrations/` for the About-page sketchbook grid), `mood/`, `texture/` (e.g. `grain.png` — the tiled film-grain overlay used on dark surfaces)
- `img_original/` — Source-of-truth high-resolution photos. Web-optimized versions in `img/` are generated from these.
- `scripts/resize-images.sh` — Re-runs the image pipeline (`magick -auto-orient` → strip metadata → resize → q82 progressive JPEG). Run this whenever a source photo is added or replaced in `img_original/gallery/`. **Always uses `-auto-orient` BEFORE stripping EXIF** — without that step, photos with EXIF orientation flags render rotated in the browser once metadata is gone (the bug that hit `mercedes-450sl.jpg` in Task #13 / formalized in Task #29).

## Constraints (from BRIEF.md §10)

- No frameworks (React, Vue, etc.)
- No build tools (Vite, Webpack, Tailwind)
- No custom backend. Contact intake is a real HTML form
  (`contact/index.html`) that POSTs to **Web3Forms**
  (`https://api.web3forms.com/submit`), a free hosted relay that emails
  every submission to Tim's inbox — works for visitors who only use
  webmail and have no native mail handler. On success `js/site.js`
  redirects to `/contact/thanks/`. A hidden `website` honeypot field
  filters bot spam. The `access_key` is Tim's real Web3Forms key; if
  it's ever reset to the `YOUR-WEB3FORMS-ACCESS-KEY-HERE` placeholder
  the JS auto-falls back to a `mailto:tim@theandgarage.com` handoff so
  the form keeps working. BRIEF.md §06.5 originally specified an
  Airtable embed; this was swapped to mailto in task #12, to
  Web3Forms in task #28, and Tim's real key was wired in via task
  #42 so the funnel works end-to-end for every visitor.
- Always write year ranges as "1966 to 1999" (never dashes)
- Tim is the protagonist on every page
