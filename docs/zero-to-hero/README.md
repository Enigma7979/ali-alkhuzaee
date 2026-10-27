# From Zero to Hero — design system and proof pipeline

New edition of the existing Creator Guide product (see `REBRAND_MAP.md`). Arabic master first; English and Russian
follow after approval. Specs: `products/creator-guide/CLAUDE_REBUILD_BRIEF_AR.md`,
`PREMIUM_VISUAL_DESIGN_SPEC.md`, `SAME_PRODUCT_REBRAND_RULES.md`.

## Where things live

| What | Where | Why |
|---|---|---|
| Design tokens + components | `scripts/zero_to_hero/design.css` | shared by every page |
| Original diagrams (code) | `scripts/zero_to_hero/diagrams.py` | values computed, not drawn by eye |
| Diagrams (editable SVG export) | `docs/zero-to-hero/diagrams/*.svg` | open in Illustrator/Figma/Inkscape |
| Cover concepts | `scripts/zero_to_hero/covers.py` | 3 concepts × ar/en/ru + back cover |
| Build / render / QA | `build.py`, `render.mjs`, `qa.py` | Chromium via Playwright for Node |
| **Manuscript pages** | `/mnt/project-files/creator-guide-private/zero-to-hero/pages/*.html` (private) | the repo is public; paid text stays private |
| Proofs | `/mnt/project-files/creator-guide-private/zero-to-hero/proofs-YYYY-MM-DD/` (private) | review only |

`scripts/` and `docs/` are excluded from GitHub Pages by `_config.yml`, so nothing here is published by a merge.

## Build

```
python scripts/zero_to_hero/build.py /mnt/project-files/creator-guide-private/zero-to-hero/pages OUT
python scripts/zero_to_hero/qa.py OUT
```

Needs network for Google Fonts. Writes the proof PDF, cover PDF, per-page PNGs, RTL spread sheets, phone previews,
`ZeroToHero_AR_prompts_sample.md` (copyable prompts) and `qa-report.json`.

Page source format: each `<section class="pg" data-run="running head" data-id="anchor">` is one B5 page;
`data-kind="dark"` for a chapter opener, `data-kind="plain"` for no running head. `{{fig:name}}` inserts a diagram.
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
