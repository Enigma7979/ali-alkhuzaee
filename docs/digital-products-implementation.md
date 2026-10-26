# Digital Products V1 — inspection and delivery record

## Scope and baseline
- Baseline production: `d012d5146c7721c66977f47a36c15bbe4f7b8a39`.
- Branch: `feature/digital-products-v1`. Separate worktree; cancelled local community code stays on its previous branch and is excluded. No community migration, account, database or deployment took place.
- Existing stack: buildless HTML/CSS/JavaScript, Python static generator, shared JSON EN/AR/RU, `?lang=` URLs. No payment, database or authentication infrastructure exists in production source.
- Live HTTP inspection returned 200 for home and Media Kit with GitHub Pages response identifiers. Hostinger account/server access is not available through connected tools. A Hostinger Mail integration alone cannot inspect hosting or run a backend.
- Preserve current homepage/Media Kit, real social/video links, contact cards, PDF and SEO routes.

## Implementation plan
1. Original educational source in a private publication package; do not commit the complete paid books or full source into this public-facing static repository. Maintain three reviewed editions.
2. Public catalog/product pages and localized 16-section interactive presentation, using only explicitly selected previews rendered from real guide pages. Preserve shared navigation and `?lang=`.
3. Isolated small Django payment/delivery service: no public registration, no community, no subscriptions. Guest checkout, server-side price/language, Stripe signed webhooks and PayPal verified captures/events, idempotent order records, expiring language-bound downloads, outbox/recovery and refunds.
4. Tests, PDF rendering, three-locale QA, safe preview; gate live checkout pending files, tax/legal approval, credentials and provider sandbox verification.
5. Production requires an approved same-origin backend route on existing hosting. Do not merge a storefront that advertises unavailable checkout as working. No hosting migration is authorized.

## Launch blockers known at inspection
- Hostinger runtime/proxy/database and secure environment access unverified. Static GitHub Pages alone cannot run secure payment verification or protect paid files.
- Stripe/PayPal sandbox credentials/webhook IDs unavailable; real provider tests must not be reported as passed.
- Transactional SMTP and provider delivery/DKIM/SPF unverified.
- Seller legal identity, VAT/OSS treatment, final tax-inclusive price and withdrawal/refund policy require owner/professional confirmation before sales.
- PDFs require complete editorial/layout review before launch.

## Legal references for owner review
- EU Your Europe, guarantees and returns: https://europa.eu/youreurope/citizens/consumers/shopping/guarantees-returns/index_en.htm
- EU VAT OSS: https://europa.eu/youreurope/business/finance-and-tax/vat/one-stop-shop/index_en.htm
- EDPB rights: https://www.edpb.europa.eu/sme/be-compliant/respect-individuals-rights_en
Technical implementation is not legal certification. Confirm digital-content early-supply consent/acknowledgement, consumer remedies, receipts, tax evidence/retention and processor agreements before publication.

## Implemented source (not deployed)
- Three 80-page private editorial PDF editions, EN/AR/RU; 35 original practical lessons in ten chapters, 50 original hooks, 30 adaptable prompts with context/examples, 15 official tool profiles and 30 daily actions. Original diagrams, real PDF page previews, bookmarks, hyperlinks, QR and page numbers. All full content stays outside this public repository.
- Public catalog `/products/`, product and 16-section interactive presentation `/products/creator-guide/`, purchase/privacy draft `/products/creator-guide/terms/`. Existing nav/footer extended by one localized link. Shared UI locale system retained.
- Guest checkout backend under `store_service/`, additive order/event/grant/outbox/rate-limit migration; no public user accounts or community. Django admin is operator-only and payment records are read-only.
- Stripe test/live isolation, real SDK signature verification, authoritative paid Session/charge validation; PayPal server capture, retrieved-order/payee/amount validation and remote signature verification.
- Random expiring language-bound tokens, private file release hashes, CSRF-protected downloads, generic lost-link recovery, transactional outbox and refund/dispute revocation. No subscription or live payment activated.

## Executed tests and limitations
- **40 Django tests passed**, including local real Stripe SDK HMAC verification, controlled provider mocks, duplicate/out-of-order events, price/language tampering, refund/reversal revocation, expiry, CSRF, locale/RTL, outbox and recovery. Actual Stripe/PayPal account sandbox purchases are **not run**.
- Django check: no issues; migration consistency: no changes; additive migration exercised on isolated SQLite test DB. PostgreSQL live concurrency/restore tests **not run**.
- Deploy checks: no errors after required environment is supplied; two intentional warnings for HSTS include-subdomains/preload, kept off to avoid unrelated subdomains. No production credentials used.
- Browser: 90 combinations (five pages × three locales × six widths 360/390/430/768/1024/1440); Russian terms headline overflow discovered and fixed. Product page 18 checks passed. All 16 presentation sections checked across three languages at narrow width. Mobile menu opened with direct accessibility click and keyboard; iframe locator click was unreliable in the QA harness.
- PDF: each edition has 80 non-empty pages and bookmark/link structures; all pages rendered for contact-sheet review and representative final pages inspected at full size. Editorial/native-speaker/professional legal review remains recommended before sale; these are review editions, not an already launched product.
- Preview only: `http://terminal.local:4173/products/creator-guide/?lang=en` (and AR/RU). No native Sites project, domain change or hosting migration created.

## Preserved functionality and publication safety
Home and Media Kit sections, portraits, locale selector, Brand Partnerships/Work With Me, published videos, social/contact URLs and existing Media Kit PDF are preserved. Existing robots/sitemap remain unchanged; draft product pages carry noindex and are deliberately not added to production sitemap yet. Canonical/hreflang/OG are prepared for each product route. Remove draft noindex and add the final approved routes to sitemap only at reviewed launch.

## Remaining manual configuration
Confirm Hostinger runtime and same-origin routing, PostgreSQL, private file directory, sandbox keys/webhook IDs, SMTP and verified sender. Approve final book versions and use actual file hashes in private release.json. Confirm legal business identity, VAT/OSS destination treatment, inclusive EUR2.99 pricing, consumer withdrawal/early-delivery wording, refunds, retention, processor agreements and receipt/invoice process. Provider confirmation emails here are not tax invoices. Do not approve launch gates without completing these tasks.

## Future improvements (not V1)
More digital products via a catalog configuration, properly disclosed affiliate resources, optional provider-backed tax automation after professional review and accessible EPUB editions. No community or subscription is planned by this implementation.
