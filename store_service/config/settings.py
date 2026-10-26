import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
BASE_DIR=Path(__file__).resolve().parent.parent
ROOT=BASE_DIR.parent
DEBUG=os.getenv('STORE_DEBUG','0')=='1'
SECRET_KEY=os.getenv('DJANGO_SECRET_KEY','dev-only-change-me') if DEBUG else os.environ['DJANGO_SECRET_KEY']
ALLOWED_HOSTS=os.getenv('ALLOWED_HOSTS','localhost,127.0.0.1,testserver').split(',')
PUBLIC_ORIGIN=os.getenv('PUBLIC_ORIGIN','http://127.0.0.1:8000' if DEBUG else 'https://alialkhuzaee.com').rstrip('/')
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','orders']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','orders.middleware.Locale','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware','orders.middleware.Security']
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages','orders.copy.context']}}]
WSGI_APPLICATION='config.wsgi.application'
if os.getenv('PGHOST'):
 DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':os.environ['PGDATABASE'],'USER':os.environ['PGUSER'],'PASSWORD':os.environ['PGPASSWORD'],'HOST':os.environ['PGHOST'],'PORT':os.getenv('PGPORT','5432'),'OPTIONS':{'sslmode':os.getenv('PGSSLMODE','require')}}}
else:
 if not DEBUG:raise ImproperlyConfigured('PostgreSQL is required for live concurrent checkout.')
 DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'development.sqlite3'}}
LANGUAGES=[('en','English'),('ar','العربية'),('ru','Русский')]
LANGUAGE_CODE='en';USE_I18N=True;USE_TZ=True;TIME_ZONE='UTC'
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':14}}]
STATIC_URL='/store-static/';STATIC_ROOT=BASE_DIR/'static-collected'
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
SESSION_COOKIE_NAME='ali_store_session';SESSION_COOKIE_PATH='/store/';SESSION_COOKIE_HTTPONLY=True;SESSION_COOKIE_SAMESITE='Lax';SESSION_COOKIE_SECURE=not DEBUG;SESSION_COOKIE_AGE=3600
CSRF_COOKIE_NAME='ali_store_csrf';CSRF_COOKIE_PATH='/store/';CSRF_COOKIE_HTTPONLY=True;CSRF_COOKIE_SECURE=not DEBUG
CSRF_TRUSTED_ORIGINS=[PUBLIC_ORIGIN]
SECURE_SSL_REDIRECT=not DEBUG;SECURE_HSTS_SECONDS=31536000 if not DEBUG else 0;SECURE_HSTS_INCLUDE_SUBDOMAINS=False;SECURE_HSTS_PRELOAD=False;SECURE_CONTENT_TYPE_NOSNIFF=True;X_FRAME_OPTIONS='DENY'
if os.getenv('TRUST_TLS_PROXY')=='1':SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')
EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST=os.getenv('EMAIL_HOST','');EMAIL_PORT=int(os.getenv('EMAIL_PORT','587'));EMAIL_USE_TLS=True;EMAIL_HOST_USER=os.getenv('EMAIL_HOST_USER','');EMAIL_HOST_PASSWORD=os.getenv('EMAIL_HOST_PASSWORD','');EMAIL_TIMEOUT=15
DEFAULT_FROM_EMAIL=os.getenv('DEFAULT_FROM_EMAIL','ali@alialkhuzaee.com')
PAYMENT_MODE=os.getenv('PAYMENT_MODE','test')
if PAYMENT_MODE not in ('test','live'):raise ImproperlyConfigured('Unknown payment mode.')
CHECKOUT_ENABLED=os.getenv('CHECKOUT_ENABLED','0')=='1'
LEGAL_APPROVED=os.getenv('LEGAL_APPROVED','0')=='1';TAX_APPROVED=os.getenv('TAX_APPROVED','0')=='1';PROVIDER_TESTS_APPROVED=os.getenv('PROVIDER_TESTS_APPROVED','0')=='1'
PDF_ROOT=Path(os.getenv('PRIVATE_PDF_ROOT',str(BASE_DIR/'private-files'))).resolve()
if PDF_ROOT.is_relative_to(ROOT):
 if not DEBUG:raise ImproperlyConfigured('PRIVATE_PDF_ROOT must be outside the public document root and repository.')
PDF_MANIFEST=Path(os.getenv('PRIVATE_PDF_MANIFEST',str(PDF_ROOT/'release.json')))
STRIPE_SECRET_KEY=os.getenv('STRIPE_SECRET_KEY','');STRIPE_WEBHOOK_SECRET=os.getenv('STRIPE_WEBHOOK_SECRET','')
PAYPAL_CLIENT_ID=os.getenv('PAYPAL_CLIENT_ID','');PAYPAL_CLIENT_SECRET=os.getenv('PAYPAL_CLIENT_SECRET','');PAYPAL_WEBHOOK_ID=os.getenv('PAYPAL_WEBHOOK_ID','');PAYPAL_MERCHANT_ID=os.getenv('PAYPAL_MERCHANT_ID','')
PAYPAL_ORIGIN='https://api-m.paypal.com' if PAYMENT_MODE=='live' else 'https://api-m.sandbox.paypal.com'
# All-in EUR 2.99; no unapproved VAT calculator. Owner must approve gross tax treatment and receipts before live mode.
PRICE_CENTS=299;CURRENCY='EUR';DOWNLOAD_MAX_AGE=7*86400
DATA_UPLOAD_MAX_MEMORY_SIZE=1024*1024;DATA_UPLOAD_MAX_NUMBER_FIELDS=25
if CHECKOUT_ENABLED and PAYMENT_MODE=='live':
 if not all((LEGAL_APPROVED,TAX_APPROVED,PROVIDER_TESTS_APPROVED,EMAIL_HOST,STRIPE_SECRET_KEY.startswith('sk_live_'),STRIPE_WEBHOOK_SECRET,PAYPAL_CLIENT_ID,PAYPAL_CLIENT_SECRET,PAYPAL_WEBHOOK_ID,PAYPAL_MERCHANT_ID)):
  raise ImproperlyConfigured('Live launch gates are not satisfied.')
if PAYMENT_MODE=='test' and STRIPE_SECRET_KEY and not STRIPE_SECRET_KEY.startswith('sk_test_'):raise ImproperlyConfigured('Test mode cannot use a live Stripe key.')
