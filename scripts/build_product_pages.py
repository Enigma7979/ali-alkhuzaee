"""Public storefront only. Never packages complete paid editions."""
from pathlib import Path
import importlib.util,json,sys
from html import escape as e
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('base',ROOT/'scripts/build_site.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
sys.path.insert(0,str(ROOT/'scripts/zero_to_hero'));import deck as zth_deck,site_assets as zth_assets
COPY=json.loads((ROOT/'assets/products/translations.json').read_text());c=COPY['en']
def t(k,tag='span',cls=''):return f'<{tag} class="{cls}" data-i18n="{k}">{e(c[k])}</{tag}>'
def btn(k,url,kind='primary'):return f'<a class="btn {kind}" href="{url}" data-language-route>{t(k)}<span aria-hidden="true">↗</span></a>'
def header(path,title,desc):
 h=base.head(False).replace('<script src="/assets/site.js?v=v2-1" defer></script>','<script src="/assets/site.js?v=v2-3" defer></script><script src="/assets/products/store.js?v=4" defer></script><link rel="stylesheet" href="/assets/v3/guide.css?v=3"><link rel="stylesheet" href="/assets/v3/deck.css?v=3"><link rel="stylesheet" href="/assets/v3/store.css?v=4"><link rel="stylesheet" href="/assets/brand/zth-deck.css?v=1">')
 h=h.replace('data-page="home"','data-page="product"').replace('https://alialkhuzaee.com/?lang=','https://alialkhuzaee.com'+path+'?lang=')
 # Accurate page-specific metadata; shared runtime localizes it.
 import re
 h=re.sub(r'<title>.*?</title>','<title>'+e(title)+'</title>',h)
 h=re.sub(r'<link rel="canonical"[^>]+>',f'<link rel="canonical" href="https://alialkhuzaee.com{path}">',h)
 h=h.replace('<head>','<head><meta name="robots" content="noindex,nofollow">')
 h=re.sub(r'<meta property="og:title"[^>]+>', '<meta property="og:title" content="'+e(title)+'">',h)
 h=re.sub(r'<meta property="og:description"[^>]+>', '<meta property="og:description" content="'+e(desc)+'">',h)
 h=re.sub(r'<meta property="og:url"[^>]+>', '<meta property="og:url" content="https://alialkhuzaee.com'+path+'">',h)
 h=re.sub(r'<meta property="og:image"[^>]+>', '<meta property="og:image" content="https://alialkhuzaee.com/assets/products/cover-v3-en.webp">',h)
 h=h.replace('hreflang="x-default" href="https://alialkhuzaee.com/"','hreflang="x-default" href="https://alialkhuzaee.com'+path+'"')
 h=h.replace('<meta name="description" content="'+e(base.HOME['seoHome'])+'">','<meta name="description" content="'+e(desc)+'">')
 h=h.replace('<body id="top" data-page="product">',f'<body id="top" data-page="product" data-product-route="{path}" data-store-origin="{STORE_ORIGIN}">')
 return h+base.nav(False)
# Sample pages of the final From Zero to Hero edition (scripts/zero_to_hero/site_assets.py PREVIEW_PAGES)
PAGES=list(zth_assets.PREVIEW_PAGES)
# Origin of store_service (Railway), e.g. https://store.alialkhuzaee.com. Empty until the store is live: the buy button stays closed.
STORE_ORIGIN=''
def cover(cls='book-stage'):
 # The From Zero to Hero cover (concept A) follows the page language (zth-deck.js swaps data-src-{lang}).
 return f'<figure class="{cls}"><img src="/assets/products/cover-v3-en.webp" data-src-ar="/assets/products/cover-v3-ar.webp" data-src-en="/assets/products/cover-v3-en.webp" data-src-ru="/assets/products/cover-v3-ru.webp" width="1000" height="1420" alt="{e(c["productTitle"])}" data-alt="productTitle"></figure>'
def deck():
 # The From Zero to Hero presentation: one slide per book unit (scripts/zero_to_hero/deck.py).
 return zth_deck.deck_html()
def previews():
 # Sample pages of the final edition in the page language (zth-deck.js swaps data-src-{lang} / data-href-{lang}).
 def page(i,p):
  src=' '.join(f'data-src-{l}="/assets/products/preview-v3-{l}-{p}.webp"' for l in ('ar','en','ru'))
  href=' '.join(f'data-href-{l}="/assets/products/preview-v3-{l}-{p}-lg.webp"' for l in ('ar','en','ru'))
  return f'<figure><a href="/assets/products/preview-v3-en-{p}-lg.webp" {href} data-preview-link="{p}" target="_blank" rel="noopener"><img src="/assets/products/preview-v3-en-{p}.webp" {src} data-preview="{p}" width="540" height="767" loading="lazy" alt="{e(c["previewAlt"])}" data-alt="previewAlt"></a><figcaption data-array="lpPreviewCaps.{i}">{e(c["lpPreviewCaps"][i])}</figcaption></figure>'
 return '<section class="section paper" id="pages"><div class="shell"><div class="section-heading">'+t('previewTitle','h2')+t('previewNote','p','section-intro')+'</div><div class="book-previews">'+''.join(page(i,p) for i,p in enumerate(PAGES))+'</div></div></section>'
INSTAGRAM='https://www.instagram.com/alialkhuzaee_startups'
INTEREST={'ar':('From Zero to Hero — أريد الكتاب عند الإطلاق','مرحباً علي، أريد كتاب From Zero to Hero عند الإطلاق. لغتي المفضلة: العربية'),'en':('From Zero to Hero — I want the book at launch','Hi Ali, I want From Zero to Hero when it launches. My preferred language: English'),'ru':('From Zero to Hero — хочу книгу при запуске','Здравствуйте, Али! Хочу книгу From Zero to Hero при запуске. Предпочитаемый язык: русский')}
def interest(kind='outline'):
 # Waitlist by email: no data is stored on the site; each request arrives in Ali's inbox (zth-deck.js swaps data-href-{lang}).
 from urllib.parse import quote
 href={l:'mailto:ali@alialkhuzaee.com?subject='+quote(a)+'&body='+quote(b) for l,(a,b) in INTEREST.items()}
 return f'<a class="btn {kind}" href="{e(href["en"])}" '+' '.join(f'data-href-{l}="{e(h)}"' for l,h in href.items())+'>'+t('lpInterestCta')+'<span aria-hidden="true">✉</span></a>'
def follow(kind='primary'):
 return f'<a class="btn {kind}" href="{INSTAGRAM}" target="_blank" rel="noopener noreferrer">'+t('lpFollowIg')+'<span aria-hidden="true">↗</span></a>'
def items(key,tag='li'):
 return ''.join(f'<{tag} data-array="{key}.{i}">{e(x)}</{tag}>' for i,x in enumerate(c[key]))
def purchase():
 # Coming soon: the price Ali approved is shown, but there is no checkout until he opens sales and activates payments.
 offer='<ul class="check-list">'+items('lpOffer')+'</ul>'
 guarantee='<div class="guarantee">'+t('lpGuaranteeTitle','h3')+t('lpGuaranteeText','p')+'</div>'
 return '<section class="section navy" id="purchase"><div class="shell purchase-grid"><div class="purchase-copy">'+t('lpOfferTitle','h2')+offer+t('editionNotice','p')+guarantee+'</div><div class="purchase-box">'+t('lpPriceLabel','p','fineprint')+t('lpPrice','p','product-price')+t('lpPriceNote','p','fineprint')+t('comingSoon','p','soon-badge')+t('comingSoonNote','p','checkout-status')+t('lpFollowTitle','h3')+follow()+interest()+t('lpInterestNote','p','fineprint')+btn('legalLabel','/products/creator-guide/terms/','text')+'</div></div></section>'
def landing():
 # Sales sections of the product page (copy approved by Ali on 2026-10-28; keys lp* in assets/products/translations.json).
 problem='<section class="section paper" id="problem"><div class="shell narrow">'+t('lpProblemTitle','h2')+'<ul class="pain-list">'+items('lpProblems')+'</ul>'+t('lpProblemClose','p','lead-close')+'</div></section>'
 rows=''.join(f'<tr><td data-array="lpCompare.{i}.0">{e(a)}</td><td data-array="lpCompare.{i}.1">{e(b)}</td></tr>' for i,(a,b) in enumerate(c['lpCompare']))
 solution='<section class="section navy" id="solution"><div class="shell narrow">'+t('lpSolutionTitle','h2')+t('lpSolutionText','p','section-intro')+t('lpSolutionMethod','p','method-line')+t('lpCompareTitle','h3','compare-title')+'<div class="compare-wrap"><table class="compare"><thead><tr><th data-array="lpCompareHead.0">'+e(c['lpCompareHead'][0])+'</th><th data-array="lpCompareHead.1">'+e(c['lpCompareHead'][1])+'</th></tr></thead><tbody>'+rows+'</tbody></table></div></div></section>'
 return problem+solution
def inside():
 value=''.join(f'<li><b data-array="lpInside.{i}.0">{e(a)}</b><span data-array="lpInside.{i}.1">{e(b)}</span></li>' for i,(a,b) in enumerate(c['lpInside']))
 return '<section class="section paper" id="inside"><div class="shell"><div class="section-heading">'+t('lpInsideTitle','h2')+t('insideIntro','p','section-intro')+'</div><ul class="value-list">'+value+'</ul><ol class="chapter-grid">'+''.join(f'<li><b class="mono">{i+1:02d}</b><span data-array="chapters.{i}">{e(x)}</span></li>' for i,x in enumerate(c['chapters']))+'</ol></div></section>'
def audience():
 return '<section class="section navy" id="audience"><div class="shell audience-grid"><div class="audience-card yes">'+t('lpForTitle','h3')+'<ul class="check-list">'+items('lpFor')+'</ul></div><div class="audience-card no">'+t('lpNotForTitle','h3')+'<ul class="cross-list">'+items('lpNotFor')+'</ul></div></div></section>'
def about():
 return '<section class="section paper" id="author"><div class="shell author-grid"><img src="/assets/portraits/ali-standing-half-400.webp" width="400" height="'+str(AUTHOR_H)+'" loading="lazy" alt="Ali Alkhuzaee" data-alt="portraitAlt"><div>'+t('lpAboutTitle','h2')+t('lpAboutText','p','section-intro')+'</div></div></section>'
def faq():
 qa=''.join(f'<details><summary data-array="lpFaq.{i}.0">{e(q)}</summary><p data-array="lpFaq.{i}.1">{e(a)}</p></details>' for i,(q,a) in enumerate(c['lpFaq']))
 return '<section class="section paper" id="faq"><div class="shell narrow">'+t('lpFaqTitle','h2')+'<div class="faq-list">'+qa+'</div><div class="hero-buttons">'+follow()+interest()+'</div></div></section>'
from PIL import Image
AUTHOR_H=Image.open(ROOT/'assets/portraits/ali-standing-half-400.webp').height
SCRIPTS='<script src="/assets/products/zth/deck-copy.js?v=1"></script><script src="/assets/brand/zth-deck.js?v=2"></script>'
def build():
 catalog=header('/products/',c['navProducts']+' | Ali Alkhuzaee',c['catalogIntro'])+'<main id="main"><section class="hero product-hero"><div class="shell"><div class="hero-content">'+t('navProducts','p','eyebrow')+t('catalogTitle','h1')+t('catalogIntro','p','hero-intro')+'</div><article class="catalog-card"><a href="/products/creator-guide/" data-language-route>'+cover('catalog-cover')+'</a><div>'+t('productTitle','h2')+t('productIntro','p')+t('comingSoon','p','price-small')+t('comingSoonNote','p','fineprint')+'<div class="hero-buttons">'+btn('viewProduct','/products/creator-guide/')+'</div></div></article></div></section></main>'+base.footer()+SCRIPTS+'</body></html>'
 product=header('/products/creator-guide/',c['productTitle']+' | Ali Alkhuzaee',c['productIntro'])+'<main id="main"><section class="hero product-hero"><div class="shell hero-layout"><div class="hero-content">'+t('lpBadge','p','eyebrow')+t('lpTitle','h1')+t('lpSub','p','hero-intro')+'<div class="hero-buttons">'+btn('lpFollowCta','#purchase')+btn('lpPagesCta','#pages','outline')+'</div>'+t('lpTrust','p','fineprint')+'</div>'+cover()+'</div></section>'+landing()+inside()+'<section class="section deck-section" id="presentation"><div class="shell"><div class="section-heading">'+t('presentationLabel','p','eyebrow')+'<div class="heading-row">'+t('presentationTitle','h2')+t('presentationIntro','p','section-intro')+'</div></div>'+deck()+'</div></section>'+previews()+audience()+about()+purchase()+faq()+'</main>'+base.footer()+SCRIPTS+'</body></html>'
 terms=header('/products/creator-guide/terms/',c['legalLabel']+' | Ali Alkhuzaee',c['legalIntro'])+'<main id="main"><section class="section paper"><div class="shell legal-copy">'+t('legalLabel','h1')+t('legalIntro','p','hero-intro')+''.join(t(k,'p') for k in ['taxTerms','deliveryTerms','refundTerms','privacyTerms'])+btn('backProduct','/products/creator-guide/','outline')+'<p><a href="mailto:ali@alialkhuzaee.com">ali@alialkhuzaee.com</a></p></div></section></main>'+base.footer()+'</body></html>'
 for path,html in [('products/index.html',catalog),('products/creator-guide/index.html',product),('products/creator-guide/terms/index.html',terms)]:
  p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(html+'\n')
if __name__=='__main__':build()
