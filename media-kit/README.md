# Media Kit maintenance

This is part of the existing static GitHub Pages website. Publish the repository root from `main`; `/media-kit/index.html` allows direct visits and refreshes at `/media-kit/` without SPA rewrites. Do not deploy the local `dist/` preview or change CNAME.

## Content and languages

- `index.html`: English fallback content, links, SEO and structured data.
- `translations.json`: Arabic, English, French and Russian interface copy.
- Professional content and campaign languages are Arabic, English and Russian. Interface languages remain Arabic, English, French and Russian; the language lists are independent.
- `data.json`: selected content, platform references and dated metrics. Keep platform links in the HTML, JSON-LD and PDF in sync when updating.
- Preserve the existing Snapchat URL unless Ali confirms a replacement.

## Audience insights

The `metrics` array is intentionally empty until current platform analytics are supplied. The audience section stays hidden. Add only approved, dated data with `label`, `value`, `asOf` and `source`; records missing any of these are not displayed. `label` can be a string or an object with `en`, `ar`, `fr`, `ru` translations. Record a public source or a non-sensitive evidence description; do not commit private analytics exports. A label can identify a platform, average views, reach, engagement or a documented audience geography. Do not infer audience distribution from Ali's spoken languages or residence.

## English PDF

Install Python dependencies `reportlab` and `Pillow`, with DejaVu Sans fonts available at `/usr/share/fonts/truetype/dejavu/`, then run:

```sh
python scripts/build_media_kit_pdf.py
```

The generator uses the original site portrait, local thumbnails and verified channel links from `data.json`. Update editorial PDF copy in the generator and review both rendered pages after rebuilding. The current PDF intentionally omits unsupplied statistics and prices.

## Validation before publishing

Check both pages in all four languages at phone, tablet and desktop widths; confirm the primary contact cards are visible without expansion and only Other Messaging Apps is collapsible; test Arabic RTL, language persistence, mail links, thumbnail/video links, PDF downloads and direct-page refreshes. Preserve every existing homepage section and link. Confirm robots/sitemap remain accessible, and verify the live page and PDF after GitHub Pages deployment completes.

## Rollback

The branch `backup/pre-media-kit-2026-10-25` preserves the production source before this change. Revert the Media Kit merge commit for a normal Git-based rollback without rewriting history.
