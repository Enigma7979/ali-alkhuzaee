# Premium Visual Design Specification — From Zero to Hero

This is an implementation specification, not a vague inspiration board. Follow alongside CLAUDE_REBUILD_BRIEF_AR.md. Design the Arabic master first. Do not change production checkout or live downloads.

## Art direction
Editorial cinematic + premium technical field manual, not a generic AI ebook, not a neon cyberpunk brochure. Balanced sophistication, warmth and legibility. Build a cohesive design system before bulk layout. Use high-quality original diagrams and real instructional utility, not decorative stock photos.

## Proposed palette (adjust only with documented visual rationale)
- Midnight ink #101827 (primary dark headings and cover)
- Deep navy #16263E (secondary backgrounds)
- Electric cyan #25C5D9 (technical accents, use sparingly)
- Warm copper #E3A86B (selected emphasis)
- Ivory #F8F7F3 (paper/background)
- Slate #526174 (body secondary)
- White #FFFFFF
- Critical/warning #B54C43 (limited semantics only)
Ensure WCAG AA contrast for all small text; don't use cyan on white for body copy. Mostly light interior pages with intentional dark chapter openers; do not flood every page with dark backgrounds.

## Typography
- Arabic: IBM Plex Sans Arabic for body, Alexandria for display/headings; verify licenses and correct shaping/embedding. Use available licensed fonts or explicitly document replacements.
- English: Manrope or similarly licensed neutral sans; Russian: Geologica or licensed Cyrillic-capable alternative.
- Body 10.5–11.5 pt minimum for printed A4/B5-equivalent; line height 1.45–1.65. Headings 24–32 pt chapter, 16–20 pt section, 12–14 pt subheading; adjust based on proof. Captions >= 9 pt. Avoid tiny dense pages.
- Arabic true RTL: punctuation, numbers, English product names, prompt code, hyperlinks, tables and mixed-language paragraphs must be individually inspected. Preserve copy-paste of prompts.

## Cover & front matter
Create 3 genuinely distinct premium cover concepts (not trivial recolors) and render mockups for approval. Cover must clearly communicate 'From Zero to Hero', Arabic subtitle and creator identity 'Ali Alkhuzaee'; use custom geometric/cinematic graphic composition, not stock portraits or AI-generated fake author photos. Strong hierarchy and thumbnail legibility. Include front cover, spine only if print specs justify it, back cover with credible benefit statement, no unsupported promises or fake testimonials. Copyright, edition/date, scope, contents and how-to-use pages.

## Page system
Establish A4 or B5 trim based on legibility; consistent margins, baseline/grid, page folios, running heads, chapter numbers, icons, callouts, table styles, example cards, source notes and footnotes. Use meaningful white space, avoid widows/orphans and lonely headings. Design chapter openers, concept spreads, step-by-step tutorials, visual comparisons, exercises, prompt cards, checklists, troubleshooting matrices, and capstone projects. Use internal links, clickable TOC, PDF bookmarks and working URLs.

## Original instructional visuals
Produce diagrams as editable SVG or vector: exposure triangle and motion blur; 24/25/30/60 fps usage; Kelvin color-temperature comparisons; hard vs soft light and source size; key/fill/rim lighting with top-down placement; inverse-square law with real-world caveats; audio signal chain, mic placement and room reflections; 180-degree rule, shot sizes, camera movement; match cut/cut-on-action timelines; color-correction vs grading; hook/retention timeline; prompt anatomy and iteration loop; analytics and business funnel. Captions must explain why each image matters. Never copy other creators' frames or use fake before/after claims. Maintain asset provenance/license ledger.

## Production QA / acceptance
Create 6-10 representative spreads first and render at print and phone size. Audit visually before generating the entire book. Export press-quality PDF and optimized digital PDF, both with embedded fonts, searchable selectable Arabic text, bookmarks, hyperlinks, accessibility metadata and consistent page numbers. Programmatically check missing images, overflowing elements, links, font embedding, color contrast where possible, and render-review EVERY page. Provide contact sheets and QA report. Deliver source files and assets in repository; don't publish before user approval.

## Do not silently fabricate
If source PDF isn't in repository, ask for attachment. Don't claim a full book is complete if content is missing. Report exact delivered chapters, diagrams, tests and outstanding issues.
