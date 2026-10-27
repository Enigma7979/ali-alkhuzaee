"""Build the standalone English Media Kit PDF from the current verified website content, in the book identity
(From Zero to Hero palette via scripts/build_brand_css.py; portrait = the standing photograph, half-body crop).

python scripts/build_media_kit_pdf.py   -> media-kit/Ali-Alkhuzaee-Media-Kit.pdf (two A4 pages, printed with Chromium)
Metrics stay out of the PDF until dated, sourced data is approved in media-kit/data.json.
"""
from pathlib import Path
from html import escape as e
import json,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'media-kit/data.json').read_text())
HOME=json.loads((ROOT/'assets/translations.json').read_text())['en']
COPY=json.loads((ROOT/'media-kit/translations.json').read_text())['en']
OUT=ROOT/'media-kit/Ali-Alkhuzaee-Media-Kit.pdf'
MAIL='mailto:ali@alialkhuzaee.com?subject=Brand%20Partnership%20Inquiry%20%E2%80%94%20Ali%20Alkhuzaee'
FONTS='https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=Manrope:wght@300;400;500;600;700;800&family=IBM+Plex+Sans+Arabic:wght@600&family=Noto+Sans+Math&family=Noto+Sans+Symbols+2&display=block'
JPG=Path(tempfile.gettempdir())/'media-kit-jpg'
def uri(rel,bg=None):
 # Chromium embeds JPEG as-is but re-encodes WebP losslessly, so photos go in as JPEG to keep the PDF small.
 # A cutout (RGBA) is flattened onto `bg` first; JPEG has no alpha.
 from PIL import Image
 src=ROOT/rel;dst=JPG/(src.stem+'.jpg');JPG.mkdir(exist_ok=True)
 im=Image.open(src)
 if bg and im.mode=='RGBA':
  base=Image.new('RGBA',im.size,bg);base.alpha_composite(im);im=base
 im.convert('RGB').save(dst,quality=88,optimize=True);return dst.as_uri()
CSS='''
@page{size:A4;margin:0}
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;font:400 9.4pt/1.55 Manrope,sans-serif;color:#eef3ff;background:#060b18}
h1,h2,h3,p{margin:0}
h1,h2,h3{font-family:Geologica,sans-serif;font-weight:600;letter-spacing:-.02em}
a{color:inherit;text-decoration:none}
.page{position:relative;width:210mm;height:297mm;overflow:hidden;break-after:page;padding:14mm 15mm 16mm}
.page:last-child{break-after:auto}
.dark{background:radial-gradient(120% 70% at 85% 8%,#16306f 0,rgba(22,48,111,0) 55%),radial-gradient(60% 50% at 0 100%,rgba(141,128,255,.16),transparent 70%),#060b18}
.paper{background:#f2f4f9;color:#0c1630}
.top{display:flex;justify-content:space-between;align-items:center;padding-bottom:5mm;border-bottom:.3mm solid rgba(150,178,255,.25);font:600 7.5pt/1 Geologica;letter-spacing:.14em}
.paper .top{border-color:#d8deea}
.brand{display:flex;align-items:center;gap:2.6mm}
.mark{width:8mm;height:8mm;border-radius:2.4mm;display:grid;place-items:center;background:linear-gradient(145deg,#3563f5,#8d80ff);color:#fff;font-size:10pt;letter-spacing:0}
.top .tag{font:500 6.8pt "JetBrains Mono";color:#56d9ff;letter-spacing:.16em}
.paper .top .tag{color:#2f56e0}
.foot{position:absolute;left:15mm;right:15mm;bottom:7mm;display:flex;justify-content:space-between;font:500 6.5pt "JetBrains Mono";letter-spacing:.12em;color:#8593b5}
.label{font:500 6.8pt/1.4 "JetBrains Mono";letter-spacing:.16em;text-transform:uppercase;color:#56d9ff;margin-bottom:2.5mm}
.paper .label{color:#2f56e0}
.hero{display:grid;grid-template-columns:1.2fr .8fr;gap:7mm;align-items:center;margin-top:7mm}
.hero h1{font-size:30pt;line-height:1.02}
.hero h1 em{display:block;font-style:normal;font-weight:300;color:#56d9ff}
.lead{font:500 12pt/1.4 Geologica;margin:4mm 0 3mm}
.intro{color:#b3c0dc}
.pills{display:flex;flex-wrap:wrap;gap:2mm;margin-top:4mm}
.pills span{padding:1.2mm 3.2mm;border-radius:9mm;border:.3mm solid rgba(150,178,255,.35);font-size:7.6pt;background:rgba(86,217,255,.06)}
.vf{position:relative;aspect-ratio:5/6;border-radius:5mm;overflow:hidden;border:.3mm solid rgba(150,178,255,.35);background:#000;box-shadow:0 10mm 30mm rgba(0,0,0,.5)}
.vf img{width:100%;height:100%;object-fit:cover;object-position:50% 30%}
.vf::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,transparent 55%,rgba(6,11,24,.85))}
.vf i{position:absolute;z-index:2;width:6mm;height:6mm;border:.5mm solid rgba(238,243,255,.8)}
.vf .tl{top:4mm;left:4mm;border-right:0;border-bottom:0;border-top-left-radius:2mm}.vf .tr{top:4mm;right:4mm;border-left:0;border-bottom:0;border-top-right-radius:2mm}
.vf .bl{bottom:4mm;left:4mm;border-right:0;border-top:0;border-bottom-left-radius:2mm}.vf .br{bottom:4mm;right:4mm;border-left:0;border-top:0;border-bottom-right-radius:2mm}
.chip{position:absolute;z-index:2;top:5.5mm;font:500 6pt/1 "JetBrains Mono";letter-spacing:.08em;padding:1.4mm 2.4mm;border-radius:9mm;background:rgba(6,11,24,.65);border:.3mm solid rgba(150,178,255,.35)}
.chip.rec{left:12mm}.chip.rec::before{content:"";display:inline-block;width:1.6mm;height:1.6mm;border-radius:50%;background:#ff5d6c;margin-right:1.4mm}
.chip.fmt{right:12mm;color:#56d9ff}
.vf figcaption{position:absolute;z-index:2;left:6mm;right:6mm;bottom:6mm;display:grid;gap:.6mm}
.vf figcaption b{font:600 7.5pt Geologica;letter-spacing:.14em}
.vf figcaption span{font-size:7pt;color:#b3c0dc}
.facts{display:grid;grid-template-columns:repeat(3,1fr);gap:.3mm;margin-top:6mm;border-radius:3.5mm;overflow:hidden;background:rgba(150,178,255,.2);border:.3mm solid rgba(150,178,255,.2)}
.facts div{background:#0b1636;padding:2.6mm 3.4mm}
.facts dt{font:500 5.8pt "JetBrains Mono";letter-spacing:.1em;text-transform:uppercase;color:#8593b5;margin-bottom:.6mm}
.facts dd{margin:0;font-weight:600;font-size:8pt}
h2{font-size:15pt;line-height:1.15;margin-bottom:3mm}
h2 em{font-style:normal;font-weight:300;color:#56d9ff}
.paper h2 em{color:#2f56e0}
.block{margin-top:5mm}
.why{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm}
.card{border-radius:3.5mm;border:.3mm solid rgba(150,178,255,.2);background:linear-gradient(180deg,rgba(17,33,75,.8),rgba(10,20,48,.7));padding:3.6mm}
.card b{display:block;font:500 6.4pt "JetBrains Mono";color:#56d9ff;margin-bottom:2.4mm}
.card h3{font-size:8.8pt;line-height:1.3;margin-bottom:1.6mm}
.card p{font-size:7.4pt;line-height:1.45;color:#b3c0dc}
.paper .card{background:#fff;border-color:#d8deea}
.paper .card b{color:#2f56e0}
.paper .card p{color:#4a5774}
.intl{display:grid;grid-template-columns:1.15fr .85fr;gap:7mm;align-items:center}
.intl p{color:#b3c0dc;font-size:8.4pt}
.intl .loc{color:#eef3ff;font-weight:600;margin-top:2mm}
.langs{display:grid;grid-template-columns:repeat(3,1fr);gap:2.4mm}
.langs div{aspect-ratio:1/1;border-radius:3.5mm;border:.3mm solid rgba(150,178,255,.3);background:radial-gradient(80% 60% at 50% 20%,rgba(86,217,255,.18),transparent 70%),rgba(6,11,24,.6);padding:3mm;display:flex;flex-direction:column;justify-content:space-between}
.langs span{font:600 16pt Geologica;color:#56d9ff}
.langs strong{font-size:7.6pt}
.formats{display:grid;grid-template-columns:repeat(3,1fr);gap:2.6mm}
.formats .card{padding:2.2mm 3.4mm}.formats .card b{margin-bottom:1.2mm}.formats .card h3{margin-bottom:.6mm}
.formats .card:last-child{grid-column:1/-1}
.work{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm}
.short .th{position:relative;aspect-ratio:4/3;border-radius:3.5mm;overflow:hidden;background:#0b1530;border:.3mm solid #d8deea}
.short .th img{width:100%;height:100%;object-fit:cover}
.short .th span{position:absolute;left:2.4mm;bottom:2.4mm;font:500 5.6pt "JetBrains Mono";letter-spacing:.08em;color:#fff;padding:1mm 2mm;border-radius:9mm;background:rgba(6,11,24,.6)}
.short small{display:block;margin-top:2.4mm;font:500 5.8pt "JetBrains Mono";letter-spacing:.1em;text-transform:uppercase;color:#2f56e0}
.short h3{font-size:8.6pt;line-height:1.35;margin:.8mm 0}
.short a{font-size:7.2pt;font-weight:700;color:#2f56e0}
.channels{display:grid;grid-template-columns:repeat(3,1fr);gap:2.4mm}
.channels a{display:flex;justify-content:space-between;padding:1.8mm 3.4mm;border-radius:3mm;background:#fff;border:.3mm solid #d8deea;font-weight:700;font-size:8pt}
.channels a span{color:#2f56e0}
.contact{margin-top:5mm;border-radius:5mm;padding:5mm 7mm;color:#eef3ff;background:radial-gradient(70% 90% at 90% 50%,rgba(141,128,255,.35),transparent 70%),linear-gradient(120deg,#1d3fb8,#2f56e0 60%,#3a3fd0)}
.contact h2{color:#fff;margin-bottom:2mm}
.contact p{color:#dde6ff;font-size:8.4pt}
.contact .mail{display:inline-block;margin-top:3mm;font:600 14pt Geologica;color:#fff}
.contact .phones{display:flex;gap:8mm;margin-top:3mm;font-size:8.4pt;color:#dde6ff}
'''
# Book identity: map the v2 colours with the same table as the website, swap fonts, then the PDF-specific overrides.
import sys;sys.path.insert(0,str(ROOT/'scripts'))
from build_brand_css import remap_colours
CSS=remap_colours(CSS,'media kit pdf').replace('"JetBrains Mono"','"IBM Plex Mono"').replace('Geologica','Manrope')+'''
body{background:#101827;color:#f8f7f3;font-family:Manrope,"Noto Sans Math","Noto Sans Symbols 2",sans-serif}
.dark{background:radial-gradient(90% 60% at 85% 10%,#16263e 0,rgba(22,38,62,0) 62%),#101827}
.dark::before{content:"";position:absolute;width:190mm;height:190mm;right:-70mm;top:-30mm;background:url("IRIS") center/contain no-repeat;pointer-events:none}
.dark>:not(.foot){position:relative}
.formats .card h3{font-size:8.2pt}.work{gap:3.4mm}
.paper{background:#f8f7f3;color:#101827}
.mark{border-radius:50%;background:#16263e;border:.5mm solid #e3a86b;color:#f8f7f3}
.top .tag,.label{color:#e3a86b}
.paper .top .tag,.paper .label,.paper .card b,.short small,.short a,.channels a span,.paper h2 em{color:#8a4f1c}
.label{display:flex;align-items:center;gap:2.4mm}.label::before{content:"";width:6mm;height:.5mm;background:currentColor}
h1,h2,h3{font-weight:700}
.hero h1 em,h2 em{color:#e3a86b}
.pills span,.chip{border-radius:1mm}
.vf{border-radius:3mm;background:radial-gradient(60% 46% at 50% 30%,rgba(227,168,107,.3),transparent 72%),#1e2d49;box-shadow:none;border-color:rgba(248,247,243,.18)}
.vf img{object-fit:cover;object-position:50% 0}
.facts,.card,.langs div,.short .th,.channels a{border-radius:1.6mm}
.facts div{background:#16263e}
.card{background:rgba(22,38,62,.7);border-color:rgba(248,247,243,.13)}
.paper .card{box-shadow:inset 0 .6mm 0 #e3a86b}
.langs div{background:rgba(22,38,62,.7)}
.contact{border-radius:2mm;background:#16263e;border-top:.8mm solid #e3a86b}
.contact p,.contact .phones{color:#d5dce6}
.langs span{font-family:Manrope,"IBM Plex Sans Arabic",sans-serif}
.channels a span,.mail,.short a{font-family:Manrope,"Noto Sans Math","Noto Sans Symbols 2",sans-serif}
.foot{color:#9fb0c6}.paper .foot{color:#526174}
'''.replace('IRIS',"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='-100 -100 200 200'%3E%3Cg fill='none' stroke='%23F8F7F3' stroke-opacity='.08'%3E%3Ccircle r='96'/%3E%3Ccircle r='80'/%3E%3Ccircle r='62'/%3E%3Ccircle r='44'/%3E%3C/g%3E%3Cpath d='M-62 0A62 62 0 0 1 0-62' fill='none' stroke='%23E3A86B' stroke-opacity='.6' stroke-width='1.2'/%3E%3C/svg%3E")
def page(cls,tag,body,n):
 return f'<section class="page {cls}"><div class="top"><span class="brand"><span class="mark">A</span>ALI ALKHUZAEE</span><span class="tag">{e(tag)}</span></div>{body}<div class="foot"><a href="https://alialkhuzaee.com">ALIALKHUZAEE.COM</a><span>0{n} / 02</span></div></section>'
def build_html():
 facts=[('Content focus',HOME['factFocusV']),('Format',HOME['factFormatV']),('Content language',HOME['factLangV']),('Works in','AR · EN · RU'),('Based in',HOME['basedShort']),('Main channels','YouTube · Instagram · TikTok')]
 p1=('<div class="hero"><div><p class="label">'+e(COPY['eyebrow'])+'</p><h1>'+e(COPY['hero'])+'<em>'+e(COPY['name'])+'</em></h1><p class="lead">'+e(COPY['lead'])+'</p><p class="intro">'+e(COPY['intro'])+'</p>'
  '<div class="pills">'+''.join(f'<span>{e(COPY[k])}</span>' for k in ('pill1','pill2','pill3'))+'</div></div>'
  f'<figure class="vf" style="margin:0"><img src="{uri("assets/portraits/ali-standing-half-533.webp",(30,45,73,255))}" alt=""><i class="tl"></i><i class="tr"></i><i class="bl"></i><i class="br"></i><span class="chip rec">REC</span><span class="chip fmt">9:16 · VERTICAL</span><figcaption><b>ALI ALKHUZAEE</b><span>AI &amp; Tech Creator · N8N Automation Engineer</span><span>{e(HOME["credential"])} · {e(HOME["founder"])}</span></figcaption></figure></div>'
  '<dl class="facts">'+''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k,v in facts)+'</dl>'
  '<div class="block"><p class="label">'+e(COPY['whyLabel'])+'</p><h2>'+e(COPY['why'])+'</h2><div class="why">'+''.join(f'<div class="card"><b>{i+1:02d}</b><h3>{e(t)}</h3><p>{e(d)}</p></div>' for i,(t,d) in enumerate(COPY['whyCards']))+'</div></div>'
  '<div class="block intl"><div><p class="label">'+e(COPY['internationalLabel'])+'</p><h2>'+e(HOME['globalTitle'])+' <em>'+e(HOME['internationalAccent'])+'</em></h2><p>'+e(HOME['globalText'])+'</p><p style="margin-top:2mm">'+e(HOME['globalHistory'])+'</p><p class="loc">'+e(HOME['location'])+'</p></div>'
  '<div class="langs">'+''.join(f'<div><span>{m}</span><strong>{e(n)}</strong></div>' for m,n in zip(['ع','En','Ру'],HOME['languages']))+'</div></div>')
 shorts=''.join(f'<div class="short"><div class="th"><img src="{uri("assets/media-kit/"+v["id"]+".webp")}" alt=""><span>YOUTUBE SHORTS</span></div><small>{e(HOME["workTopics"][i])}</small><h3>{e(v["title"]["en"])}</h3><a href="{e(v["url"])}">Watch on YouTube ↗</a></div>' for i,v in enumerate(DATA['work']))
 p2=('<div class="block" style="margin-top:7mm"><p class="label">'+e(COPY['formatsLabel'])+'</p><h2>'+e(COPY['formatsTitle'])+'</h2><div class="formats">'+''.join(f'<div class="card"><b>{i+1:02d}</b><h3>{e(t)}</h3><p>{e(d)}</p></div>' for i,(t,d) in enumerate(COPY['formats']))+'</div></div>'
  '<div class="block"><p class="label">'+e(COPY['workLabel'])+'</p><div class="work">'+shorts+'</div></div>'
  '<div class="block"><p class="label">'+e(COPY['socialLabel'])+'</p><div class="channels">'+''.join(f'<a href="{e(u)}">{e(n)}<span>↗</span></a>' for n,u in DATA['platforms'].items())+'</div></div>'
  '<div class="contact"><h2>'+e(HOME['contactTitle'])+' '+e(HOME['contactAccent'])+'</h2><p>'+e(COPY['contactText'])+'</p><a class="mail" href="'+MAIL+'">ali@alialkhuzaee.com ↗</a>'
  '<div class="phones"><a href="tel:+32467685250">Belgium: +32 467 68 52 50</a><a href="tel:+380637171771">Ukraine: +380 63 717 17 71</a></div></div>')
 return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Ali Alkhuzaee | Media Kit &amp; Brand Partnerships</title>'
  f'<meta name="author" content="Ali Alkhuzaee"><link rel="stylesheet" href="{FONTS}"><style>{CSS}</style></head><body>'
  +page('dark','MEDIA KIT / 2026',p1,1)+page('paper','BRAND PARTNERSHIPS',p2,2)+'</body></html>')
RENDER_JS='''const {chromium}=require('playwright');(async()=>{const [src,pdf]=process.argv.slice(2);const b=await chromium.launch();const p=await b.newPage();
await p.goto(src,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);
const overflow=await p.evaluate(()=>[...document.querySelectorAll('.page')].map((s,i)=>s.scrollHeight>s.clientHeight+2?i+1:0).filter(Boolean));
await p.pdf({path:pdf,preferCSSPageSize:true,printBackground:true,tagged:true});console.log(JSON.stringify({overflow}));await b.close()})();'''
def main():
 with tempfile.TemporaryDirectory() as tmp:
  html=Path(tmp)/'media-kit.html';html.write_text(build_html());js=Path(tmp)/'render.js';js.write_text(RENDER_JS)
  res=subprocess.run(['node',str(js),html.as_uri(),str(OUT)],check=True,capture_output=True,text=True)
 print(OUT,res.stdout.strip())
if __name__=='__main__':main()
