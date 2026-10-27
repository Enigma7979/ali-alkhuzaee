# From Zero to Hero — same-product rebrand map (old → new)

Rule: `products/creator-guide/SAME_PRODUCT_REBRAND_RULES.md`. "From Zero to Hero" is the new edition of the
existing product **From Zero to AI-Powered Content Creation**. One product, one route, one checkout, three languages.

**Status (2026-10-27, review branch `feature/digital-products-v1`): applied on the branch, not live.** Rows 1–9 and 12
are applied on the branch (row 12 by replacing the old deck runtime; `assets/v2/guide.js` itself is kept for the old
edition). Row 10 (private PDFs) waits for the final approved PDFs; row 11 is unchanged ("coming soon", payments off).
Nothing reaches the live site until Ali approves a merge to `main`.

## Stays the same (must not change)

| Item | Value | Where |
|---|---|---|
| Product id | `creator-guide` | `store_service/orders/models.py` (default), `payments.py` metadata, `fulfillment.py` metadata check |
| Route / canonical | `/products/creator-guide/` (+ `?lang=en|ar|ru`) | `products/creator-guide/index.html`, `sitemap.xml`, hreflang links |
| Terms page | `/products/creator-guide/terms/` | unchanged |
| Language selector | en / ar / ru | `assets/products/store.js` `localize()` |
| Checkout flow | one Stripe Checkout session per order, EUR, per-language edition | `store_service/orders/payments.py` (price untouched; payments stay off) |
| Fulfilment | private manifest `release.json`, `status: approved` gate, per-language edition path | `store_service/orders/fulfillment.py`, `PRIVATE_PDF_MANIFEST` |
| Existing purchasers | keep access; their download resolves through the same manifest | manifest edition paths are swapped in place, not duplicated |

## Changes after approval

| # | Old | New | File(s) |
|---|---|---|---|
| 1 | Title EN "From Zero to AI-Powered Content Creation" | "From Zero to Hero" + subtitle "The practical guide to content and video creation" | `assets/products/translations.json` → `en.productTitle`; `assets/products/guide-copy.js`; `products/index.html` (2×); `products/creator-guide/index.html` `<title>`, `og:title` |
| 2 | Title AR «من الصفر إلى صناعة المحتوى بالذكاء الاصطناعي» | «From Zero to Hero» + «الدليل العملي لصناعة المحتوى والفيديو» (Arabic title wording: Ali to confirm) | same files, `ar.*` |
| 3 | Title RU «С нуля до создания контента с помощью ИИ» | «From Zero to Hero» + «Практическое руководство по созданию контента и видео» | same files, `ru.*` |
| 4 | Meta description (phone, AI ideas, small business) | Describe the completed curriculum only (camera, light, sound, story, editing, AI workflow, analytics) | `products/creator-guide/index.html` `description`, `og:description` |
| 5 | Covers `assets/products/cover-v2-{en,ar,ru}.webp` | Chosen concept (A/B/C) per language, same filenames or a new `cover-v3-*` with references updated | `products/*.html`, `store.js` |
| 6 | Previews `assets/products/preview-v2-{lang}-{1,3,5,24}.webp` | Pages from the approved final PDF (no sample-only pages) | `store.js` builds `preview-v2-LANG-N.webp`; update pattern + `data-preview` numbers together |
| 7 | `og:image` `preview-v2-en-1.webp` | new EN cover | `products/creator-guide/index.html` |
| 8 | Stripe line item name `Creator Guide / LANG` | `From Zero to Hero / LANG` (display only; metadata `product: creator-guide` unchanged) | `store_service/orders/payments.py` |
| 9 | Email subject "Your Creator Guide — private download" (+ AR/RU) | "From Zero to Hero — your private download" (+ AR/RU) | `assets/products/translations.json` `emailSubject` |
| 10 | Private PDFs `Creator_Guide_v2_{EN,AR,RU}.pdf` | `ZeroToHero_{EN,AR,RU}.pdf` in the same private root; manifest `editions.LANG.path` swapped; keep old files until purchasers are confirmed working | server `PRIVATE_PDF_ROOT`, `release.json` |
| 11 | "coming soon" state on the live page | unchanged until Ali approves publication | `products/creator-guide/index.html` |
| 12 | `assets/v2/guide.js` "Creator Guide" label | new title | `assets/v2/guide.js` |

Build tooling for the old edition (`scripts/build_creator_guide*.py`, `render_guide_cover.py`, `guide_preview_copy.py`,
`prepare_guide_photos.py`, `design-preview/`) is kept, not deleted, so the old edition can still be rebuilt.

## Smoke tests to run on the review branch before asking for merge

1. `/products/creator-guide/?lang=en|ar|ru` renders title, cover, previews; Arabic is RTL; no 404s in the network log.
2. No second product card on `/products/`; only one checkout button.
3. `store_service` tests (`python manage.py test orders`) pass; metadata still says `product: creator-guide`.
4. Fulfilment with a test manifest returns the new PDF for each language and refuses an unapproved manifest.
5. Canonical, hreflang, `og:*` and `sitemap.xml` point to the same URL as before.
