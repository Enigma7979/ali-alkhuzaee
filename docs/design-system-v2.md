# Design system v2 — "Studio after dark"

Status: **Stage B review samples only.** Nothing here is linked from the live site. The full redesign starts only after Ali approves this direction.

- Review page (branch): `design-preview/index.html` (noindex, not in sitemap, not linked from navigation)
- Styles and runtime: `assets/v2/ds.css`, `assets/v2/ds.js` (no framework, ~10 KB JS unminified)
- Copy: `scripts/build_design_preview.py` reuses the approved EN/AR/RU wording from `assets/translations.json`, `media-kit/translations.json`, `assets/products/translations.json` and `media-kit/data.json`; only new UI strings are defined there.
- Offline package and sandboxed review page: `python scripts/build_design_preview.py OFFLINE.html ARTIFACT.html`

## Direction

A creator's studio at night: midnight surfaces lit by one cool key light, with the vertical 9:16 frame as the recurring motif (hero viewfinder, Shorts cards, presentation). Light "paper" sections carry reading-heavy content so the site does not become one long dark page.

## Tokens

| Role | Token | Value |
|---|---|---|
| Base background | `--night` | `#060b18` |
| Raised dark surface | `--navy` / `--deep` | `#0a1430` / `#11214b` |
| Primary action | `--electric` | `#3563f5` (white text 4.9:1) |
| Highlight, focus ring on dark | `--cyan` | `#56d9ff` |
| Restrained accent | `--violet` | `#8d80ff` |
| Text on dark | `--ink`, `--ink-2`, `--ink-3` | `#eef3ff`, `#b3c0dc`, `#8593b5` |
| Light section | `--paper`, `--paper-ink`, `--paper-2` | `#f2f4f9`, `#0c1630`, `#4a5774` |
| Status | `--ok`, `--warn`, `--rec` | green, amber (pending data), recording red |

Contrast (computed, WCAG 2): `--ink-2` on `--night` 10.8:1; `--ink-3` on `--night` 6.4:1; `--paper-2` on `--paper` 6.6:1; white on `--electric` 4.9:1; `--electric-2` labels on `--paper` 5.4:1.

## Typography

| Role | Latin / Cyrillic | Arabic |
|---|---|---|
| Display | Geologica 300/500/600 | Alexandria 500/600/700 |
| Body | Manrope 400–700 | IBM Plex Sans Arabic 400–700 |
| Utility (labels, specs, timecodes) | JetBrains Mono 500 | Body face (no letter-spacing) |

Scale: hero `clamp(2.75rem, 6.4vw, 6rem)`, H2 `clamp(2rem, 4.2vw, 3.75rem)`, H3 `clamp(1.25rem, 1.8vw, 1.6rem)`, lead `~1.1–1.3rem`, body 16px, label 0.72rem. Arabic headings get taller line-height (1.25–1.4) and no negative tracking. Russian hero size steps down to fit longer words.

For production, load the Arabic families only on `?lang=ar` and the Latin display face only on EN/RU to keep requests small.

## Spacing, radius, layout

- Side gutter `max(16px, safe-area)`; content shell 1240 px.
- Section padding `clamp(72px, 9vw, 120px)`.
- Radius: 10 px (inputs, notes), 18 px (cards, frames), 28 px (hero frame, presentation shell). Buttons are pills.
- Breakpoints: 1100 px (metric grid 5→3), 900 px (two-column layouts stack), 640 px (phone: Shorts become a swipe row, single-column lists), 360 px (legend single column).

## Components

- **Buttons:** primary (electric fill), ghost (outline). Disabled state is visibly muted and `disabled`, used for checkout until it opens.
- **Viewfinder frame:** 9:16, corner marks, rule-of-thirds grid, REC and format chips. Uses Ali's supplied portrait cut-out (original pixels).
- **Short card:** 9:16 frame, play control, topic, title, description, "Open on YouTube" link. Click-to-play loads `youtube-nocookie.com` only after a tap; without JavaScript, or in sandboxed previews, it opens YouTube. A titled fallback shows when the thumbnail cannot load.
- **Fact grid:** label/value pairs for the Media Kit.
- **Metric tile:** shows a value only with date and source; otherwise a dashed tile with "Awaiting verified export".
- **Product buy box:** price, one-time note, edition choice, disabled checkout with status.
- **Presentation shell:** bar with previous/next, live counter, progress, swipe and arrow keys (reversed in RTL), section list.
- **Lighting plot:** top-view illustration with numbered markers and an HTML legend; budget tiers dim what a tier does not include. Clearly labelled as an illustration.

## Motion

One load sequence on the hero (staggered rise, 0.9 s). Short card hover zoom, button lift, slide entrance. No loops except three REC blinks. `prefers-reduced-motion` removes all animation and transitions (tested).

## RTL / LTR

`dir` is set per language. Layout uses logical properties (`inset-inline-*`, `margin-inline`, `padding-inline-start`). Directional arrows flip in RTL. Phone numbers, emails, handles, prices and counters are forced LTR. Presentation keys and swipes follow reading direction.

## Images and licensing

| Asset | Source | Status |
|---|---|---|
| `assets/portraits/ali-hero-690.webp` | Ali's supplied photo, existing alpha mask | Owner photo, approved in PR #7 |
| `assets/portraits/ali-kit-dark-{520,900}.webp` | Ali's supplied `pointing-dark-original.jpeg`, resized only | Owner photo |
| `assets/media-kit/XrUiMpdjRwE.webp`, `q6BLhS16MwU.webp` | YouTube thumbnails of Ali's own Shorts | Owner content |
| New Short thumbnail | Loaded from `i.ytimg.com/vi/6m0NC1etQIU/hqdefault.jpg` at runtime | Owner content; not stored locally (YouTube unreachable from the build environment) |
| `assets/products/cover-{ar,en,ru}.webp` | Cropped from the real page-1 previews | Owner's guide |
| Lighting plot | Original SVG drawn for this project | Original illustration, labelled |

No stock photos, generated faces or third-party images are used. No image-generation tool was available, so studio, lighting and product photography in the full presentation need either Ali's own photos (recommended: shoot his real desk setup) or clearly labelled original illustrations.
