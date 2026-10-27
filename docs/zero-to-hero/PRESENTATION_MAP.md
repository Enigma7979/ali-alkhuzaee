# From Zero to Hero — presentation ↔ curriculum map (verified)

Source checked: Ali's Arabic manuscript **Zero_to_Hero_Arabic_V2.pdf** (38 pages, October 2026), the only complete
curriculum that exists today, plus the Batch 1 designed sample pages (28 pp) for the diagrams. Page numbers are the
manuscript's printed folios. The presentation replaces the old 16-slide deck of the previous edition
(`design-preview/guide.html`, kept for the old edition's build); none of the old chapter descriptions are reused.

**When the final book PDF exists, re-check every row against it** (titles, counts, the diagrams used per unit) and
update `scripts/zero_to_hero/deck_copy.py`, then run `python scripts/zero_to_hero/deck.py`.

| Slide | Content | Manuscript | Book figure on the slide |
|---|---|---|---|
| 01 | Cover: title, subtitle, 12 units / 60 prompts / 40 hooks, three languages | p. 1, TOC p. 2 | Cover concept A (chosen by Ali) |
| 02 | Method: goal → idea → apply → exercise → review; three levels; progress check | p. 2 "كيف تستخدم هذا الإصدار؟", progress line on every unit page | — |
| 03 | Course map: 12 units (clickable) + library list | TOC p. 2, sections 13–22 | — |
| 04 | Unit 01 · الأساس · من الفكرة إلى مشروع محتوى واضح | p. 3 | Episode map (from the unit text) |
| 05 | Unit 02 · التصوير · التعريض والتحكم في الكاميرا | p. 4 | `exposure_stops` |
| 06 | Unit 03 · التصوير · العدسات والتكوين وحركة الكاميرا | p. 5 | `shot_sizes` |
| 07 | Unit 04 · الإضاءة · هندسة الإضاءة: من نافذة إلى استوديو | p. 6 | `hard_soft` |
| 08 | Unit 05 · الصوت · الصوت: تشخيص المشكلة قبل المعالجة | p. 7 | `signal_chain` |
| 09 | Unit 06 · القصة · السرد البصري والتخطيط | p. 8 | `axis_180` |
| 10 | Unit 07 · المونتاج · فن القطع والانتقالات | p. 9 | `cut_timelines` |
| 11 | Unit 08 · المونتاج · المونتاج في DaVinci Resolve | p. 10 | `color_pipeline` |
| 12 | Unit 09 · النمو · كتابة الريلز والاحتفاظ بالمشاهد | p. 11 | `hook_retention` (labelled illustrative) |
| 13 | Unit 10 · الأنظمة · الذكاء الاصطناعي داخل سير العمل | p. 12 | 11-step workflow (from the unit text) |
| 14 | Unit 11 · الأعمال · العلامة الشخصية والمنتج الرقمي | p. 13 | Four trust questions (from the unit text) |
| 15 | Unit 12 · التطبيق · مشروع التخرج وخطة 30 يومًا (+ test card, pre-publish checklist) | pp. 14–15 | Four-week plan (from the unit text) |
| 16 | Library: prompt engineering, R-C-T-F-Q, 60 templates, sample prompt 01 (copyable) | §13 pp. 16–17, §14 pp. 18–23 | `prompt_anatomy` |
| 17 | Toolkit: 40 hooks, 5 Reel scripts, weekly plan, DaVinci 8 steps, analytics, automation, projects + 100-point rubric, troubleshooting | §15 p. 24, §16 p. 29, §17 p. 31, §18 p. 32, §19 p. 33, §20 p. 34, §21 p. 35, §22 p. 36 | `analytics_funnel` |
| 18 | Edition: one product in three languages, Arabic first; status "coming soon", no price | SAME_PRODUCT_REBRAND_RULES.md | Covers A in AR/EN/RU |

## Counts quoted on the slides (counted in the manuscript)

| Claim | Where counted |
|---|---|
| 12 units | TOC p. 2, unit pages 3–14 |
| 60 prompt templates | §14, last item "برومبت · 60" |
| 40 hook examples | §15 heading "40 مثالًا" and items "مثال · 01…40" |
| 5 Reel scripts (15, 30, 45, 60, 60 s) | §16 headings |
| DaVinci in 8 steps | §18, steps 1–8 |
| 100-point rubric | §21 "سلم التقييم 100 نقطة" |

## Left out on purpose

- §23 "خطة تطوير الكتاب للإصدار التجاري" (the internal development plan) and the sources page: not customer content.
  §23 also lists companion files (storyboard, shot list, prompt log, analytics tracker) that are **planned, not made**;
  the presentation does not promise them.
- No page count, price, follower numbers, results, testimonials or partner logos.
- Photos: none. The old deck's licensed stock photos and the pointing portrait are not used.

## Languages

Arabic is the master copy (from the manuscript); English and Russian are translations in `deck_copy.py`. Diagram
labels are translated in `scripts/zero_to_hero/diagram_i18n.json` (a missing label fails the build); the audio
signal chain is mirrored for left-to-right reading. Arabic RTL; English and Russian LTR.
