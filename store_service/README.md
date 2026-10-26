# Guest checkout and private PDF delivery

This service is implemented for review and **not deployed**. Production is still the original static site. Do not publish this directory as static files. No community, public account registration, subscription or payment credentials are included.

## Infrastructure decision required

The observed domain serves GitHub Pages. That platform cannot run this Python service, verify webhooks or protect paid PDFs. Hostinger resources have not been inspected because no hosting administration connection is available. Confirm an existing Hostinger runtime with Python 3.12+, a process supervisor/reverse proxy and PostgreSQL before choosing this deployment. Shared hosting without that runtime will require a separately approved compatible backend decision. No hosting migration has been performed or assumed.

Preferred same-origin mount: route `/store/` to this service, `/store-static/` to collected Django admin static assets, and keep existing static pages/assets on their current serving path. The existing homepage/Media Kit must remain intact. Do not expose a new domain or change DNS without approval.

## Development

```
python -m venv .venv
.venv/bin/pip install -r requirements.txt
STORE_DEBUG=1 .venv/bin/python manage.py migrate
STORE_DEBUG=1 .venv/bin/python manage.py test orders
```

SQLite is development/test only. Test database migrations were actually run by Django's test runner. PostgreSQL migration/concurrency testing has **not** been performed yet.

## Configuration and launch gates

Copy variable NAMES from `.env.example` into the hosting secret manager. The app does not automatically read `.env`; the supervisor must inject environment variables. Never paste private keys into chat or a GitHub issue. Production needs a strong random `DJANGO_SECRET_KEY`, PostgreSQL credentials, HTTPS origin/allowed hosts and transactional SMTP. Keep `PAYMENT_MODE=test` and `CHECKOUT_ENABLED=0` initially.

The PDF directory must be outside both repository and public document root. Install only three approved PDF files in it. A private `release.json` must contain:

```json
{"status":"approved","editions":{"en":{"file":"Creator_Guide_EN.pdf","sha256":"ACTUAL_SHA256"},"ar":{"file":"Creator_Guide_AR.pdf","sha256":"ACTUAL_SHA256"},"ru":{"file":"Creator_Guide_RU.pdf","sha256":"ACTUAL_SHA256"}}}
```

Replace hash descriptions with actual file hashes. The source package is presently marked `editorial-review`, not approved. Never change that status merely to bypass the launch gate.

`ready()` requires valid release files and all provider settings. `CHECKOUT_ENABLED=1` exposes checkout only after that test. Live mode additionally refuses startup without `LEGAL_APPROVED=1`, `TAX_APPROVED=1`, `PROVIDER_TESTS_APPROVED=1`, SMTP and live provider settings. These are review attestations, not automated evidence of tax/legal compliance.

## Provider configuration

Stripe: create a test secret and signed webhook endpoint for `/store/webhooks/stripe/`. Subscribe to `checkout.session.completed`, `checkout.session.async_payment_succeeded`, `checkout.session.expired`, `charge.refunded`, `charge.dispute.created`. Checkout is a single EUR2.99 card payment, server priced; the server retrieves the Session and expanded settled charge before fulfilment. Metadata binds order/product/language. Refund and dispute events revoke links. Do not use test events to fulfil live orders.

PayPal: configure a sandbox REST application, merchant ID and webhook ID for `/store/webhooks/paypal/`. Subscribe to `PAYMENT.CAPTURE.COMPLETED`, `PAYMENT.CAPTURE.REFUNDED`, `PAYMENT.CAPTURE.REVERSED`. Browser approval is followed by a CSRF-protected capture POST; only the verified server response/retrieved completed order can fulfil. Webhooks are verified with PayPal's signature-verification API. Capture amount, payee, custom/invoice ID and currency must match.

No real Stripe or PayPal sandbox transaction has been executed: credentials are not available. All current provider tests use controlled mocks and are explicitly not certification of the live integration. Before launch, test successful/failed/cancelled checkout, duplicate and out-of-order events, lost capture responses, refunds/reversals, disputes and emails in each language against the real sandboxes.

## Delivery and email worker

Only SHA256 hashes of random 256-bit bearer download tokens are used for download lookup. A private email outbox retains the link until dispatch. Links last seven days, bind the immutable order language and stop working after refund/dispute. GET shows a confirmation page; CSRF-protected POST streams only that edition. There is no public file URL. A copied link remains a bearer credential until expiry; do not describe it as impossible to share.

Run `python manage.py send_order_emails` from a private scheduled worker each minute. It sends only to paid order addresses. Failed sends retry (up to eight attempts); inspect failures without logging message bodies/tokens. Exactly-once SMTP transmission cannot be guaranteed if a process crashes after SMTP accepts a message but before the DB commits. Payment fulfilment and initial email-job creation are idempotent. Recovery is generic, rate-limited and at most one new email per order per UTC day.

Run `python manage.py cleanup_rate_buckets` hourly. Operationally confirm retention periods and delete/anonymize customer records according to the approved policy and tax retention obligations; no arbitrary production-order deletion job is enabled.

## Administration and refunds

Provision an administrator with `python manage.py createsuperuser` directly in the server console, using a strong unique credential. No owner credentials are seeded or hardcoded. `/store/admin/` is staff-only; order/event/grant/mail records are read-only to prevent manual payment grants. Use the provider dashboard for refunds after the owner's approval; signed events revoke access. Automated refund initiation and tax invoicing are not implemented. Payment confirmation email is not a VAT invoice.

## Reverse proxy and security

- Gunicorn binds loopback only. Use a dedicated unprivileged service account, restrictive PDF/secret permissions and least-privilege database role.
- Proxy only `/store/`; preserve all unrelated routes. Proxy must strip incoming forwarding headers and set its own TLS/client identity. Enable `TRUST_TLS_PROXY=1` only with that verified arrangement.
- Resolve client IP from trusted ingress, not arbitrary `X-Forwarded-For`; application rate limits deliberately use `REMOTE_ADDR`. A misconfigured proxy could group all customers into one bucket.
- Disable/redact access logs for `/store/download/` paths and do not log request bodies, Stripe signatures, PayPal headers or SMTP contents. Add ingress abuse controls for webhook endpoints without blocking genuine provider retries.
- HTTPS, HttpOnly/SameSite cookies, CSRF for customer actions, CSP, frame denial, no-referrer/no-store/noindex are enabled. Webhook endpoints alone are CSRF exempt because provider signatures authenticate them.
- Deploy check reports two intentional warnings: HSTS subdomain scope and preload are off to avoid altering security for unrelated subdomains.
- Back up encrypted PostgreSQL and private approved PDFs; test restoring in staging. Set monitoring for webhook errors, outbox failures, disk capacity and backups.

## Rollback

Keep existing Pages publication at baseline `d012d5146c7721c66977f47a36c15bbe4f7b8a39` until reviewed. Backup ref `backup/pre-digital-products-v1` preserves it. Additive order migrations only; no production migration has run. Before any eventual release, snapshot the DB and static tree. To stop sales, set `CHECKOUT_ENABLED=0`; keep signed webhooks and existing downloads running so pending orders and customers are not abandoned. Restore prior static publication if needed. Never drop orders or reverse migrations with production data merely to roll back the storefront.
