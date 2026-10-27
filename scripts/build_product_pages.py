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
 h=base.head(False).replace('<script src="/assets/site.js?v=v2-1" defer></script>','<script src="/assets/site.js?v=v2-1" defer></script><script src="/assets/products/store.js?v=3" defer></script><link rel="stylesheet" href="/assets/v3/guide.css?v=3"><link rel="stylesheet" href="/assets/v3/deck.css?v=3"><link rel="stylesheet" href="/assets/v3/store.css?v=3"><link rel="stylesheet" href="/assets/brand/zth-deck.css?v=1">')
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
 h=h.replace('<body id="top" data-page="product">',f'<body id="top" data-page="product" data-product-route="{path}">')
 return h+base.nav(False)
# Sample pages of the From Zero to Hero Arabic proof (scripts/zero_to_hero/site_assets.py PREVIEW_PAGES)
PAGES=list(zth_assets.PREVIEW_PAGES)
def cover(cls='book-stage'):
 # The From Zero to Hero cover (concept A) follows the page language (zth-deck.js swaps data-src-{lang}).
 return f'<figure class="{cls}"><img src="/assets/products/cover-v3-en.webp" data-src-ar="/assets/products/cover-v3-ar.webp" data-src-en="/assets/products/cover-v3-en.webp" data-src-ru="/assets/products/cover-v3-ru.webp" width="1000" height="1420" alt="{e(c["productTitle"])}" data-alt="productTitle"></figure>'
def deck():
 # The From Zero to Hero presentation: one slide per book unit (scripts/zero_to_hero/deck.py).
 return zth_deck.deck_html()
def previews():return '<section class="section paper" id="pages"><div class="shell"><div class="section-heading">'+t('previewTitle','h2')+t('previewNote','p','section-intro')+'</div><div class="book-previews">'+''.join(f'<a href="/assets/products/preview-v3-{p}-lg.webp" data-preview-link="{p}" target="_blank" rel="noopener"><img src="/assets/products/preview-v3-{p}.webp" data-preview="{p}" lang="ar" width="540" height="767" loading="lazy" alt="{e(c["previewAlt"])}"></a>' for p in PAGES)+'</div></div></section>'
def purchase():
 # Coming soon: no price or checkout until Ali opens sales and activates payments.
 return '<section class="section navy" id="purchase"><div class="shell purchase-grid"><div class="purchase-copy">'+t('buyCta','h2')+t('editionNotice','p')+t('oneTime','p','fineprint')+'</div><div class="purchase-box">'+t('comingSoon','p','product-price')+t('comingSoonNote','p','checkout-status')+btn('legalLabel','/products/creator-guide/terms/','text')+'</div></div></section>'
SCRIPTS='<script src="/assets/products/zth/deck-copy.js?v=1"></script><script src="/assets/brand/zth-deck.js?v=1"></script>'
def build():
 catalog=header('/products/',c['navProducts']+' | Ali Alkhuzaee',c['catalogIntro'])+'<main id="main"><section class="hero product-hero"><div class="shell"><div class="hero-content">'+t('navProducts','p','eyebrow')+t('catalogTitle','h1')+t('catalogIntro','p','hero-intro')+'</div><article class="catalog-card"><a href="/products/creator-guide/" data-language-route>'+cover('catalog-cover')+'</a><div>'+t('productTitle','h2')+t('productIntro','p')+t('comingSoon','p','price-small')+t('comingSoonNote','p','fineprint')+'<div class="hero-buttons">'+btn('viewProduct','/products/creator-guide/')+'</div></div></article></div></section></main>'+base.footer()+SCRIPTS+'</body></html>'
 product=header('/products/creator-guide/',c['productTitle']+' | Ali Alkhuzaee',c['productIntro'])+'<main id="main"><section class="hero product-hero"><div class="shell hero-layout"><div class="hero-content">'+t('productEyebrow','p','eyebrow')+t('productTitle','h1')+t('productIntro','p','hero-intro')+'<div class="hero-buttons">'+btn('presentationCta','#presentation')+btn('buyCta','#purchase','outline')+'</div>'+t('oneTime','p','fineprint')+'</div>'+cover()+'</div></section><section class="section deck-section" id="presentation"><div class="shell"><div class="section-heading">'+t('presentationLabel','p','eyebrow')+'<div class="heading-row">'+t('presentationTitle','h2')+t('presentationIntro','p','section-intro')+'</div></div>'+deck()+'</div></section><section class="section navy" id="inside"><div class="shell"><div class="section-heading">'+t('inside','h2')+t('insideIntro','p','section-intro')+'</div><ol class="chapter-grid">'+''.join(f'<li><b class="mono">{i+1:02d}</b><span data-array="chapters.{i}">{e(x)}</span></li>' for i,x in enumerate(c['chapters']))+'</ol></div></section>'+previews()+purchase()+'</main>'+base.footer()+SCRIPTS+'</body></html>'
 terms=header('/products/creator-guide/terms/',c['legalLabel']+' | Ali Alkhuzaee',c['legalIntro'])+'<main id="main"><section class="section paper"><div class="shell legal-copy">'+t('legalLabel','h1')+t('legalIntro','p','hero-intro')+''.join(t(k,'p') for k in ['taxTerms','deliveryTerms','refundTerms','privacyTerms'])+btn('backProduct','/products/creator-guide/','outline')+'<p><a href="mailto:ali@alialkhuzaee.com">ali@alialkhuzaee.com</a></p></div></section></main>'+base.footer()+'</body></html>'
 for path,html in [('products/index.html',catalog),('products/creator-guide/index.html',product),('products/creator-guide/terms/index.html',terms)]:
  p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(html+'\n')
if __name__=='__main__':build()
