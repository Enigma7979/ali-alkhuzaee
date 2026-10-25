# Premium creator redesign — preview review

Status: preview only. Do not merge or deploy until Ali explicitly approves the final preview.

## Audit

- Production baseline: `f449d5833b3ebeca87602530f77dde70673fdab6` (PR #6).
- Existing application is buildless static HTML/CSS/JavaScript, with `/` and `/media-kit/` served directly. No React, frontend package dependencies, forms, authentication or server integrations were present.
- Production HTTPS responses and prior deployment evidence identify GitHub Pages as the serving path. The owner has a Hostinger account; no Hostinger, DNS, TLS, CNAME or Pages settings were changed.
- Home used inline CSS and four embedded translation objects; Media Kit used separate CSS/JS/translation/data files. The redesign retains static architecture, extracts shared styling/runtime and adds a small Python generator for consistent English HTML fallbacks.
- Existing PDF was English only. No AR/RU/FR PDF downloads existed.
- Actual original site portrait, six Media Kit platform URLs, Facebook/GitHub/Notion/project links, three real YouTube Shorts and both phone numbers were identified and retained. Snapchat is unchanged.
- Audience metrics are empty and demographics unavailable. No numerical counters, sponsor logos, testimonials, prices or audience-geography claims were invented. Add dated/source-backed metrics to `media-kit/data.json` when available; the section remains hidden until then.
- The primary concept was reviewed from its source repository, read-only, because its public URL required ChatGPT sign-in. Its layouts/data were not copied. Other references informed editorial hierarchy and partnership positioning only.

## Implemented design

- Larger typography, off-white surfaces, deep navy sections, electric blue and cyan highlights.
- Original standing portrait in the homepage Hero; original pointing portrait in Media Kit, placed towards the partnership copy.
- CSS perspective orbits/sphere, subtle pointer depth on fine-pointer desktop devices, reveal transitions and hover treatments. No Three.js/GSAP runtime or autoplay embeds added.
- System reduced-motion preference disables animations, transitions, pointer depth and reveal gating. No animation library or 3D model download blocks content.
- Photos retain original RGB subject pixels. Image editing was used only to extract alpha masks; derivatives combine those masks with the original photograph pixels. No generated face/body pixels are used. Original four uploads and extraction masks are retained in `assets/portraits/`.
- Visible phone cards, business-email priority, text country labels without flags. Other Messaging Apps is a small native disclosure in the Ukraine card.
- English/Arabic/Russian UI only, RTL for Arabic. Four *communication capabilities* (Arabic/English/Russian/Ukrainian) remain distinct from the three website locales.
- Professional standalone English PDF refreshed with matching design, original pointing portrait, real selected content, four communication languages and essential contacts.

## Language migration and SEO

French URLs found in the old public source/sitemap:

- `https://alialkhuzaee.com/?lang=fr`
- `https://alialkhuzaee.com/media-kit/?lang=fr`

Public search returned no matching indexed results; this does not prove they were never indexed. No Search Console access was available.

The preview maps unsupported `lang` values (including old stored French) to English, updates the visible URL with History replacement, and emits EN/AR/RU/x-default hreflang and consistent canonical/OG URLs. Existing paths and fragments remain valid. French is removed from runtime dictionaries, selector, work-title data, sitemap and alternates.

**HTTP 301 limitation:** GitHub Pages cannot configure query-parameter-based response redirects from repository files. JavaScript fallback is not an HTTP 301. A true permanent redirect requires an existing edge/server rule after checking the domain's actual routing. No provider settings were changed or alternative hosting added. Before final release, the owner can approve publishing with the safe canonical/client fallback, or arrange a 301 rule with the current serving provider. Never claim that a 301 has been implemented by adding `_redirects` or `.htaccess` to a GitHub Pages repository.

Desired server/edge mapping: match path `/` or `/media-kit/` AND query `lang=fr`, return 301 to the same path with `lang=en`; preserve other non-language query parameters. Do not redirect all French-speaking visitors by browser language.

## Rebuild

```sh
python scripts/prepare_portraits.py
python scripts/build_site.py
python scripts/build_media_kit_pdf.py
```

Portrait/PDF rebuild requires Pillow/reportlab and DejaVu fonts, as before. Browser runtime needs no package installation.

## Preservation

- `/media-kit/` direct access and reload; standalone PDF URL.
- `#about`, `#projects`, `#connect`, `#contact` fragments; added `#work`, `#expertise`, `#international`.
- Brand Partnerships nav, Work With Me Hero CTA and footer Media Kit link.
- Business email, correct call/WhatsApp targets, social/project URLs and selected published videos.
- Belgium/Ukraine identity, PhD, Study UA Plus, international history.
- CNAME, robots.txt, deployment settings and unrelated systems untouched.

## Verification

- Both pages × EN/AR/RU × 360/390/430/768/1024/1440 CSS pixels: 36 browser layout cases, no horizontal overflow, one H1, exactly three locale options, two direct phone cards, Arabic RTL.
- Mobile navigation opened/closed with expected ARIA state; Escape closes it. Other Messaging Apps opens using keyboard Enter.
- English PDF text, actual link annotations and both rendered pages checked.
- All internal assets/fragment targets, phone/mail/video targets, metadata and locale dictionaries checked before source handoff.
- No Core Web Vitals field data or Lighthouse score is claimed. Performance provisions: optimized responsive WebP portraits, lazy local thumbnails, no media autoplay, no heavyweight 3D runtime, deferred shared JS, content available in static HTML.

## Pending review inputs

- Ali's explicit final-preview approval is required before main merge/production deployment.
- Current platform analytics, if desired for the audience section; absent metrics remain hidden.
- Real HTTP 301 handling for legacy French query URLs requires provider-level configuration or an explicitly accepted fallback.

## Preview download limitation

The regenerated PDF opens and renders correctly as a local standalone file, with verified link annotations. The preview browser did not emit a download event when using its download button, and the browser download helper also timed out. This is not reported as a successful end-to-end download test. Retest the button on the approved hosted release before declaring production complete. The reviewed PDF is provided separately for approval.

## Modified or added files

- `assets/contact-options.css`
- `assets/portraits/ali-hero-420.webp`
- `assets/portraits/ali-hero-690.webp`
- `assets/portraits/ali-partnership-480.webp`
- `assets/portraits/ali-partnership-900.webp`
- `assets/portraits/masks/hero-alpha.png`
- `assets/portraits/masks/partnership-alpha.png`
- `assets/portraits/originals/full-length-original.jpeg`
- `assets/portraits/originals/hero-original.png`
- `assets/portraits/originals/partnership-original.jpeg`
- `assets/portraits/originals/pointing-dark-original.jpeg`
- `assets/site.css`
- `assets/site.js`
- `assets/translations.json`
- `docs/redesign-review.md`
- `index.html`
- `media-kit/Ali-Alkhuzaee-Media-Kit.pdf`
- `media-kit/README.md`
- `media-kit/app.js`
- `media-kit/data.json`
- `media-kit/index.html`
- `media-kit/style.css`
- `media-kit/translations.json`
- `scripts/build_media_kit_pdf.py`
- `scripts/build_site.py`
- `scripts/prepare_portraits.py`
- `sitemap.xml`

## Image extraction provenance

The built-in image editing tool was used in background-extraction mode. The effective brief for each portrait was: remove only the white background into true transparent alpha; preserve exact face, body, pose, hand/finger, hair, skin texture, suit colors and framing; no redraw, generated face, retouching or relighting. The generated RGB output is deliberately not used. `scripts/prepare_portraits.py` combines only the reviewed alpha masks with the original photograph RGB pixels. The original supplied photographs remain preserved separately.

## Review screenshots

- `docs/previews/home-desktop.jpg`
- `docs/previews/home-mobile-ar.jpg`
- `docs/previews/media-kit-desktop.jpg`
- `docs/previews/media-kit-mobile.jpg`
