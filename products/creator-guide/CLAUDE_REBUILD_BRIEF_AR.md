# From Zero to Hero — Claude Code Production Brief (Arabic master)

## Goal
Rebuild the Arabic creator course into a commercially credible, technically verified, visually original, practical educational book. The current 38-page PDF is a **draft manuscript**, not a finished commercial book. Do not market or publish it as complete.

## Inputs
- User-provided file: `From_Zero_to_Hero_AR_Expanded_Manuscript_v2.pdf` (38 pages). The user will place this binary PDF in `products/creator-guide/source/` or provide it directly in the Claude Code session.
- Existing PDFs and web product assets in this repository: audit and preserve them.
- Existing branch: `feature/digital-products-v1`; existing PR #8. Do not overwrite published products or change checkout until approved.

## Execution plan — do not stop at planning
1. Inventory all source PDFs, assets, fonts, build scripts, preview/deck, and product routes; produce an audit of missing depth, errors, weak illustrations, and inaccurate claims.
2. Build a **source-controlled book manuscript** (Markdown/MDX/structured data) so text is editable, not trapped in a PDF. Extract Arabic manuscript carefully and validate RTL, equations, and code prompts. Keep versioned sources.
3. Expand chapters to include: exposure triangle, fps/shutter/motion blur, white balance and color science, focal lengths/composition, hard vs soft light, inverse-square-law caveats, lighting direction/ratios, microphone selection, acoustics, gain staging, EQ/compression/noise reduction, scripting/storytelling, hooks/retention, shot lists, editing, sound design, color correction vs grading, AI workflows and prompt engineering, content analytics, ethical marketing, monetization and business systems.
4. Preserve and improve **60 editable prompt templates** and **40 hooks** in the supplied draft; add realistic input variables, sample outputs, failure cases, and verification steps. Include 15/30/60s scripts, practical projects for beginner/intermediate/advanced, and rubrics.
5. Create original instructional illustrations (not generic stock): exposure triangle and shutter examples; lighting diagrams with placement and Kelvin comparisons; microphone polar patterns and signal chain; shot composition/180-degree rule; cut-on-action and match cut timelines; color workflow; analytics funnel; before/after case studies. Use SVG diagrams or original licensed assets with documented provenance, captions and alt text. No copied YouTube frames or copyrighted illustrations without permission.
6. Design a premium, accessible Arabic RTL PDF with clickable TOC, stable pagination, readable Arabic typography, embedded fonts, print-friendly charts, consistent page grid, source notes, diagrams, exercise pages and editable prompts. Generate proof pages and inspect every page for overflow, clipping, font shaping, RTL ordering, image quality and contrast.
7. Create QA checks for technical accuracy, factual sources, accessibility, links, prompt copyability, RTL rendering and file size. Record source citations and date-sensitive tool guidance. Flag uncertain claims rather than fabricate.
8. Only after Arabic master approval, adapt and independently proofread English and Russian editions; don't machine-translate without QA. Update the free preview and product pages to accurately reflect final content; preserve existing purchase functionality and routes.
9. Build final artifacts in a review-only directory, plus changelog, source bibliography, license ledger, QA report and a preview link. Do not merge, deploy or replace live paid downloads until user approval.

## Acceptance criteria
- Deep, tested, actionable teaching for beginner/intermediate/advanced readers; no page-count padding.
- Each major skill: why, when, exact steps, troubleshooting, example, exercise, checklist, source references.
- All visual examples original or properly licensed; no fake comparisons.
- Arabic RTL proofed; downloadable PDF and editable source; accessible preview; no broken assets.
- Evidence-backed claims and clear distinction between research and original examples.

## Working method
Implement in batches and commit tangible changes. If source PDF isn't present, report the missing file and proceed with repository audit and build pipeline; do not invent its content. Ask only for blockers, not routine approvals. Do not claim completion until all QA gates pass.
