# From Zero to Hero — design system and proof pipeline

New edition of the existing Creator Guide product (see `REBRAND_MAP.md`). Arabic master; full English and Russian
translations of the same book (one product, three PDFs). Specs: `products/creator-guide/CLAUDE_REBUILD_BRIEF_AR.md`,
`PREMIUM_VISUAL_DESIGN_SPEC.md`, `SAME_PRODUCT_REBRAND_RULES.md`.

## Where things live

| What | Where | Why |
|---|---|---|
| Design tokens + components | `scripts/zero_to_hero/design.css` | shared by every page |
| Original diagrams (code) | `scripts/zero_to_hero/diagrams.py` | values computed, not drawn by eye |
| Diagrams (editable SVG export) | `docs/zero-to-hero/diagrams/*.svg` | open in Illustrator/Figma/Inkscape |
| Cover concepts | `scripts/zero_to_hero/covers.py` | 3 concepts × ar/en/ru + back cover |
| Build / render / QA | `build.py`, `render.mjs`, `qa.py` | Chromium via Playwright for Node |
| **Manuscript pages** | `/mnt/project-files/creator-guide-private/zero-to-hero/pages{,-en,-ru}/*.html` (private) | the repo is public; paid text stays private |
| Proofs and final PDFs | `/mnt/project-files/creator-guide-private/zero-to-hero/final-YYYY-MM-DD/{ar,en,ru}/` (private) | never in this repo |

`scripts/` and `docs/` are excluded from GitHub Pages by `_config.yml`, so nothing here is published by a merge.

## Build

```
python scripts/zero_to_hero/build.py /mnt/project-files/creator-guide-private/zero-to-hero/pages OUT/ar ar
python scripts/zero_to_hero/build.py /mnt/project-files/creator-guide-private/zero-to-hero/pages-en OUT/en en
python scripts/zero_to_hero/build.py /mnt/project-files/creator-guide-private/zero-to-hero/pages-ru OUT/ru ru
python scripts/zero_to_hero/qa.py OUT/ar ar   # and en, ru
```

English and Russian run longer than Arabic, so a few pages carry `data-fit` (content zoom, floor 0.8).
`fit.py PAGES OUT STATE.json` sets those values after a build; repeat build + fit until it prints `pending 0`.
LTR typography overrides live in `build.py` (`LTR_CSS`), diagram labels in `diagram_i18n.json`.

Needs network for Google Fonts. Writes the proof PDF, cover PDF, per-page PNGs, RTL spread sheets, phone previews,
`ZeroToHero_{AR,EN,RU}_prompts.md` (copyable prompts) and `qa-report.json`.

Page source format: each `<section class="pg" data-run="running head" data-id="anchor">` is one B5 page;
`data-kind="dark"` for a chapter opener, `data-kind="plain"` for no running head. `{{fig:name}}` inserts a diagram; `{{page:id}}` becomes the page number of the section with that `data-id` (used by the contents pages).
The 60-prompt and 40-hook library pages are generated from private data by `creator-guide-private/zero-to-hero/data/gen_library.py PAGES_DIR`.
The build fails loudly in QA if any element escapes its page frame.

## Design system

**Trim and grid.** B5 176 × 250 mm, chosen over A4 because one page fits a phone screen at fit-width and still prints
well. Text frame 142 × 210 mm. RTL binding: even pages on the right of a spread, odd on the left; inner margin 19 mm,
outer 15 mm, top 19 mm, bottom 21 mm. Folio at the outer bottom corner with a copper rule; running head = unit · title.

**Colour.** Spec palette: ink `#101827`, navy `#16263E`, cyan `#25C5D9`, copper `#E3A86B`, ivory `#F8F7F3`,
slate `#526174`, warn `#B54C43`. Two documented additions, because brand cyan (1.95:1) and copper fail WCAG AA as
small text on ivory: **cyan-ink `#0B6E7C`** (5.5:1) and **copper-ink `#8A4F1C`** (6.1:1) for labels and kickers. Brand
cyan and copper stay for fills, rules and dark pages. Light interior pages; dark only for chapter openers and covers.

**Type.** Arabic body IBM Plex Sans Arabic 10.5 pt / 1.65; display Alexandria (chapter 27 pt, section 17.5 pt,
sub 12.5 pt); Latin Manrope; Russian Geologica; mono IBM Plex Mono; Noto Sans Math + Noto Sans Symbols 2 as glyph
fallbacks (← ≈ ∝ ◆ ✓). All SIL OFL 1.1. No letter-spacing on Arabic (it breaks joining). Captions ≥ 9 pt.
Numbers, ranges and formulas inside Arabic are isolated (`<span class="num">`, or U+2066/U+2069 in SVG) so they
read left-to-right.

**Components.** kicker + tag, lead, figure card with "why it matters" caption, callouts (technical note / field tip /
common myth), data table, troubleshooting matrix, numbered tutorial with "why" lines, exercise card (levels, time,
materials, deliverable, success criterion), checklist, prompt card (copyable text, variables, sample output,
failure modes, verification), hook card (type, line, first visual proof), chapter opener, TOC with internal links.
Anything drawn rather than tested carries the "illustrative" label or says so in its caption.

## Website (same identity)

| What | Where |
|---|---|
| Shared tokens (book palette, type, radii) | `assets/brand/tokens.css` — `scripts/build_brand_css.py` fails if `design.css` drifts from it |
| Site CSS in the book identity | `assets/v3/*.css`, generated from `assets/v2/*.css` + `assets/brand/book.css` by `python scripts/build_brand_css.py` |
| Cover A per language, preview pages | `python scripts/zero_to_hero/site_assets.py [OUT/proof/png]` → `assets/products/cover-v3-*.webp`, `preview-v3-*.webp` |
| Presentation | copy `deck_copy.py`, markup/diagrams `deck.py` → `assets/products/zth/`; runtime `assets/brand/zth-deck.{js,css}`; map `PRESENTATION_MAP.md` |
| Diagram labels in EN/RU | `diagram_i18n.json`; `diagrams.render(name, lang)` |

Then `python scripts/build_site.py`, `python scripts/build_product_pages.py`, `python scripts/build_media_kit_pdf.py`.
