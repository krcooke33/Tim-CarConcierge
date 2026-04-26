# Mood Board Image Slots

Drop image files into this folder using the filenames below. The mood board page (`mood-board.html`) expects images at exactly these paths.

**File format:** `.jpg` preferred (smaller); `.png` or `.webp` will also work but you'd need to update the `data-img` attribute in the HTML.
**Size:** ~1200–2000px on the long edge is plenty. Compress with TinyPNG or similar before committing — keeps the repo light and the deploy fast.

---

## Photographic mood (Feel section)

The 6 cards under "What it looks like." Sun-faded romance, cars + people + open road.

| Filename | What goes here |
|---|---|
| `feel-01.jpg` | A car on a country road, golden hour. Cinematic. |
| `feel-02.jpg` | A couple in or beside a classic — the lifestyle, not the catalogue. |
| `feel-03.jpg` | A car at rest somewhere atmospheric — desert, gates, fall leaves. |
| `feel-04.jpg` | A wood-rim wheel with a hand on it. The most intimate detail. |
| `feel-05.jpg` | A dashboard with patina — gauges, wood, polished metal. |
| `feel-06.jpg` | A sunlit interior — leather warm, the wheel waiting. |

## Image treatments — three columns

The Drive / Arrival / Detail grid showing the photographer's eye across three subjects.

### Drive — the freedom
| Filename | What goes here |
|---|---|
| `drive-01.jpg` | Car on a country road, low light or golden hour. |
| `drive-02.jpg` | A hand on a wood wheel, in motion. Windscreen sun-flare. |
| `drive-03.jpg` | A car kicking up dust on an empty highway. Cinematic. |

### Arrival — the companion
| Filename | What goes here |
|---|---|
| `arrival-01.jpg` | A couple beside a convertible — desert, mountain, or beach. |
| `arrival-02.jpg` | A car parked alone in a beautiful place — gate, cliff, or field. |
| `arrival-03.jpg` | A driver leaning, looking — the moment after the drive. |

### Detail — the beauty
| Filename | What goes here |
|---|---|
| `detail-01.jpg` | Wood-rim wheel, hand resting. Petrolicious-style. |
| `detail-02.jpg` | Gauge cluster — Veglia, Smiths, Jaeger. Cream-on-black. |
| `detail-03.jpg` | Polished gear knob, sun-warmed leather, the small considered things. |

## Adjacent inspiration

Reference shots from brands that share the air. Just a few each — these are pinning notes, not curated portfolios.

| Filename | What goes here |
|---|---|
| `inspiration-petrolicious.jpg` | A reference shot from Petrolicious — film-grain interior, wood-wheel, sun-warmed. |
| `inspiration-singer.jpg` | Singer Vehicle Design hero photography — dark backgrounds, cinematic light. |
| `inspiration-hodinkee.jpg` | Hodinkee editorial layout or warm photography — adjacent enthusiast voice. |
| `inspiration-magnus.jpg` | Magnus Walker / Outlaw Porsche aesthetic — patina, ownership, romance. |

## Putting it together

| Filename | What goes here |
|---|---|
| `mock-hero.jpg` | The big hero mock background. A workshop, dashboard, or open-road shot strong enough to carry headline type over it. |

## Optional — material textures

The CSS swatches in the materials section are placeholders. To push them harder, drop real texture photos in:

| Filename | What goes here |
|---|---|
| `texture-leather.jpg` | A close crop of sun-warmed leather, oxblood-deep. |
| `texture-paint.jpg` | A faded paint surface, sun-bleached. |
| `texture-paper.jpg` | Aged paper or vintage manual page. |
| `texture-wood.jpg` | A wood-rim wheel close-up. |
| `texture-chrome.jpg` | Patina'd chrome — bumper, badge, gear knob. |
| `texture-asphalt.jpg` | Open road tarmac. |

Note: the HTML doesn't reference these by default — they'd require small edits to swap CSS gradients for real photos. Tell me when you want to push the materials section that direction.

---

## Two ways to add images

**Quick (per-session preview):** open `mood-board.html` in your browser and click any slot. The file picker opens, and the image previews instantly. Won't persist after a refresh, won't deploy to GitHub.

**Permanent:** save files into this folder with the matching filenames, commit, push. The deployed site picks them up automatically. Hard-refresh the browser if cached.

## Mapping the images you've already collected

Suggested matches based on your collection so far:

- *Mustang couple "this type of love"* → `feel-01.jpg` (typography overlay sets the tone)
- *Black GTO at dusk, urban* → `drive-01.jpg`
- *Red muscle car at sunset* → `mock-hero.jpg` (strong hero candidate)
- *Couple in convertible with scarf* → `arrival-01.jpg` or `feel-02.jpg`
- *Red Mustang at fall gates* → `feel-03.jpg`
- *Red Camaro on highway* → `drive-03.jpg`
- *Woman with hood up, mountain* → use sparingly — leans more workshop than mood
- *Mercedes 350SL desert couple* → `arrival-01.jpg` or `mock-hero.jpg`
- *"I'm tired, boss" BMW* → not a primary mood image but good as a voice/tone reference
- *Wood steering wheel detail (Petrolicious)* → `detail-01.jpg`
- *Veglia gauge + gear shifter (Petrolicious)* → `detail-02.jpg`
- *Woman in red dress with cyan Beetle* → `arrival-02.jpg`
- *White Bronco with rainbow stripes* → `drive-02.jpg`
