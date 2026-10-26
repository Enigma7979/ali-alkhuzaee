"""Build the private Creator Guide PDFs in the v2 "Studio after dark" design.

python scripts/build_creator_guide_v2.py PRIVATE_SOURCE_DIR PRIVATE_OUTPUT_DIR [en ar ru]

Reads the same private content.py as build_creator_guide.py and reuses its EN/AR/RU edition strings.
Licensed photography comes from assets/presentation/photos (credits in LICENSES.json).
Renders with Chromium through Playwright for Node (`npm i playwright` and `npx playwright install chromium`
where it is not already available). Fonts load from Google Fonts, so rendering needs a network connection.
Never write complete paid books into the public website tree.
"""
from pathlib import Path
from html import escape as e
import ast,importlib.util,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
PHOTOS=ROOT/'assets/presentation/photos'

def load_editions():
 """Read the edition strings (T, plain dict(...) literals) from build_creator_guide.py without running that script."""
 tree=ast.parse((ROOT/'scripts/build_creator_guide.py').read_text())
 for node in tree.body:
  if isinstance(node,ast.Assign) and getattr(node.targets[0],'id',None)=='T':
   return eval(compile(ast.Expression(node.value),'build_creator_guide.py','eval'),{'__builtins__':{},'dict':dict})
 raise SystemExit('Edition strings not found in build_creator_guide.py')

T=load_editions()
EXTRA={
 'en':dict(chapter='Chapter',contents='Contents',credits='Photography',creditsText='Photographs are used under the Unsplash and Pexels licenses. They show example setups, not Ali’s own studio unless stated.',day='Day',page='Page',hook='Hook'),
 'ar':dict(chapter='الفصل',contents='المحتويات',credits='الصور',creditsText='الصور مستخدمة وفق ترخيص Unsplash وPexels، وتعرض أمثلة على التجهيزات وليست استوديو علي الشخصي ما لم يُذكر ذلك.',day='اليوم',page='صفحة',hook='افتتاحية'),
 'ru':dict(chapter='Глава',contents='Содержание',credits='Фотографии',creditsText='Фотографии используются по лицензиям Unsplash и Pexels. Это примеры студий, а не личная студия Али, если не указано иное.',day='День',page='Стр.',hook='Хук')}
# One licensed photo per chapter opener, and one per lesson illustration type.
CHAPTER_PHOTOS=['b-1-phone-ring-light','a-2-camera-mic-desk-setup','c-1-octabox-studio','f-1-tabletop-softbox-setup','d-1-purple-desk-boom-mic','h-2-editor-dark-room','d-2-rgb-laptop-setup','h-1-editing-dark-desk','f-2-cosmetics-shoot-bw','c-2-softboxes-silhouette']
ART_PHOTOS={'studio':'a-2-camera-mic-desk-setup','lighting':'c-1-octabox-studio','audio':'e-1-boom-arm-mic','product':'f-1-tabletop-softbox-setup','comparison':'f-2-cosmetics-shoot-bw','budget':'b-2-phones-tripod-ring-lights','workflow':'h-1-editing-dark-desk','frame':'b-1-phone-ring-light','hook':'d-1-purple-desk-boom-mic','prompt':'d-2-rgb-laptop-setup','timeline':'h-2-editor-dark-room','plan':'c-2-softboxes-silhouette'}
ARABIC_FOLIO='letter-spacing:0;font-family:"IBM Plex Sans Arabic";font-size:7pt'  # tracking breaks Arabic joining
FALLBACK=['a-1-dark-creator-studio','b-2-phones-tripod-ring-lights','c-2-softboxes-silhouette','d-2-rgb-laptop-setup']

def photo(name,w=1600):return (PHOTOS/f'{name}-{w}.webp').as_uri()

CSS='''
@page{size:176mm 250mm;margin:19mm 17mm 21mm;
 @bottom-left{font:500 6.5pt "JetBrains Mono",monospace;letter-spacing:.12em;color:#8593b5;vertical-align:top;padding-top:5mm}
 @bottom-right{content:counter(page);font:600 7pt "JetBrains Mono",monospace;color:#2f56e0;vertical-align:top;padding-top:5mm}}
@page bleed{margin:0;@bottom-left{content:none}@bottom-right{content:none}}
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;font:400 10pt/1.6 Manrope,sans-serif;color:#0c1630;background:#fff}
html[lang=ar] body{font-family:"IBM Plex Sans Arabic",sans-serif;line-height:1.85}
.page{page:bleed;position:relative;width:176mm;height:250mm;overflow:hidden;break-before:page;padding:0}
.page:first-child{break-before:auto}
.flow{break-before:page}
.panel,.exercise,.photo,.hook,.prompt,.day,.card,.steps li,.toc a,.tool-head{break-inside:avoid}
h2,h3{break-after:avoid}
h1,h2,h3,h4{font-family:Geologica,sans-serif;margin:0}
html[lang=ar] :is(h1,h2,h3,h4){font-family:Alexandria,sans-serif;letter-spacing:0!important}
h2{font-size:22pt;line-height:1.15;letter-spacing:-.02em;margin:2mm 0 5mm;color:#060b18}
html[lang=ar] h2{line-height:1.45}
h3{font-size:10.5pt;color:#2f56e0;margin:5mm 0 2mm}
p{margin:0 0 3mm}
.eyebrow{font:600 7pt "JetBrains Mono",monospace;letter-spacing:.16em;text-transform:uppercase;color:#2f56e0;margin:0}
html[lang=ar] .eyebrow{font:600 8.5pt "IBM Plex Sans Arabic";letter-spacing:0}
.folio{position:absolute;bottom:9mm;inset-inline:17mm;display:flex;justify-content:space-between;font:500 6.5pt "JetBrains Mono",monospace;letter-spacing:.12em;color:#8593b5;border-top:.3mm solid #d8deea;padding-top:2.5mm}
.folio b{color:#2f56e0}
.dark{background:#060b18;color:#eef3ff}
.dark h2{color:#fff}
.dark .folio{border-color:rgba(150,178,255,.25);color:#8593b5}
.bleed{position:absolute;inset:0}
.bleed img{width:100%;height:100%;object-fit:cover;display:block}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(6,11,24,.55) 0%,rgba(6,11,24,.15) 35%,rgba(6,11,24,.86) 70%,#060b18 100%)}
.vf i{position:absolute;width:12mm;height:12mm;border:0 solid rgba(238,243,255,.85)}
.vf i:nth-child(1){top:9mm;left:9mm;border-top-width:.6mm;border-left-width:.6mm}
.vf i:nth-child(2){top:9mm;right:9mm;border-top-width:.6mm;border-right-width:.6mm}
.vf i:nth-child(3){bottom:9mm;left:9mm;border-bottom-width:.6mm;border-left-width:.6mm}
.vf i:nth-child(4){bottom:9mm;right:9mm;border-bottom-width:.6mm;border-right-width:.6mm}
/* cover */
.cover .top{position:absolute;top:17mm;inset-inline:18mm;display:flex;justify-content:space-between;direction:ltr;font:600 7pt "JetBrains Mono";letter-spacing:.18em}
.cover .rec::before{content:"";display:inline-block;width:2.4mm;height:2.4mm;border-radius:50%;background:#ff5d6c;margin-right:2mm;vertical-align:-.2mm}
.cover .badge{color:#56d9ff;border:.3mm solid rgba(86,217,255,.6);padding:1mm 3mm;border-radius:9mm}
.cover .copy{position:absolute;inset-inline:18mm;bottom:58mm}
.cover .eyebrow{color:#56d9ff;font-size:8pt;margin-bottom:5mm}
html[lang=ar] .cover .eyebrow{font-size:10pt}
.cover h1{font:800 31pt/1.05 Geologica;letter-spacing:-.035em;color:#fff}
html[lang=ar] .cover h1{font:800 31pt/1.4 Alexandria}
html[lang=ru] .cover h1{font-size:27pt}
.cover h1 em{font-style:normal;display:block;color:#56d9ff;background:linear-gradient(90deg,#56d9ff,#8d80ff);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;padding-bottom:.15em;margin-bottom:-.15em}
.cover .sub{margin-top:5mm;font-size:10.5pt;color:#c9d4ee;max-width:120mm}
.cover .bar{position:absolute;inset-inline:18mm;bottom:22mm;display:flex;justify-content:space-between;align-items:center;border-top:.3mm solid rgba(150,178,255,.3);padding-top:6mm}
.author{display:flex;align-items:center;gap:4mm}
.author img{width:16mm;height:16mm;border-radius:50%;object-fit:cover;object-position:50% 18%;border:.6mm solid #56d9ff}
.author b{display:block;font:700 12pt Geologica;color:#fff}
html[lang=ar] .author b{font-family:Alexandria}
.author span{font-size:7.5pt;color:#b3c0dc}
.cover .ed{text-align:end;font-weight:600;font-size:8.5pt}
.cover .ed small{display:block;font:500 6pt "JetBrains Mono";letter-spacing:.14em;color:#56d9ff;direction:ltr}
/* chapter opener */
.opener .num{position:absolute;inset-inline:17mm;bottom:70mm;font:300 70pt/1 Geologica;color:rgba(86,217,255,.9);letter-spacing:-.04em}
.opener .ttl{position:absolute;inset-inline:17mm;bottom:28mm}
.opener h2{font-size:30pt;color:#fff;margin:3mm 0 0}
html[lang=ar] .opener h2{line-height:1.4}
.opener .eyebrow{color:#56d9ff}
.opener .credit,.photo .credit{font-size:6pt;color:rgba(238,243,255,.7)}
.opener .credit{position:absolute;inset-inline-end:17mm;bottom:12mm}
/* lessons */
.photo{position:relative;margin:3mm 0 5mm;height:52mm;border-radius:4mm;overflow:hidden;background:#060b18}
.photo img{width:100%;height:100%;object-fit:cover;display:block}
.photo .credit{position:absolute;inset-inline-end:3mm;bottom:2mm;text-shadow:0 0 3mm rgba(0,0,0,.8)}
.lead{font-size:11pt;color:#28344f}
.steps{list-style:none;margin:0 0 4mm;padding:0;counter-reset:s}
.steps li{counter-increment:s;display:grid;grid-template-columns:8mm 1fr;gap:2mm;margin-bottom:1.8mm}
.steps li::before{content:counter(s,decimal-leading-zero);font:600 7.5pt/1.9 "JetBrains Mono";color:#2f56e0}
.panel{background:#eef3ff;border-inline-start:1mm solid #3563f5;border-radius:2mm;padding:3.5mm 4.5mm;margin:3mm 0}
.panel h3,.exercise h3{margin:0 0 1mm;font-size:9pt}
.exercise{background:#0a1430;color:#eef3ff;border-radius:3mm;padding:4mm 5mm;margin:3mm 0;position:relative;overflow:hidden}
.exercise::after{content:"";position:absolute;inset:auto -10mm -14mm auto;width:40mm;height:40mm;border-radius:50%;background:radial-gradient(circle,rgba(141,128,255,.35),transparent 70%)}
.exercise h3{color:#56d9ff}
.exercise p{margin:0}
/* hooks */
.hook{display:grid;grid-template-columns:10mm 1fr;gap:3mm;padding:3.2mm 0;border-bottom:.3mm solid #d8deea;font-size:10.5pt;break-inside:avoid}
.hook b{font:600 9pt "JetBrains Mono";color:#2f56e0}
/* tools */
.tool-head{display:flex;align-items:center;gap:4mm;margin:2mm 0 4mm}
.mark{width:13mm;height:13mm;border-radius:3.5mm;display:grid;place-items:center;font:700 15pt Geologica;color:#fff;background:linear-gradient(135deg,#3563f5,#8d80ff)}
.tool-head h2{margin:0}
.url{font:500 7.5pt "JetBrains Mono";color:#2f56e0;direction:ltr;text-align:left;overflow-wrap:anywhere}
.card{border:.3mm solid #d8deea;border-radius:3mm;padding:3.5mm 4.5mm;margin-bottom:3mm}
.card h3{margin-top:0}
/* prompts */
.prompt{border:.3mm solid #c9d5f5;border-radius:3.5mm;padding:5mm;margin:0 0 5mm;background:linear-gradient(180deg,#f7f9ff,#fff);break-inside:avoid}
.prompt h3{margin:0 0 2mm}
.prompt .task{font:500 9.5pt/1.65 "JetBrains Mono";color:#0c1630}
html[lang=ar] .prompt .task{font:500 10.5pt/1.9 "IBM Plex Sans Arabic"}
.fine{font-size:7.2pt;color:#5b6886}
.notes{height:14mm;border-bottom:.3mm dashed #b9c5dc}
/* plan */
.day{display:grid;grid-template-columns:16mm 1fr 6mm;gap:3mm;align-items:start;padding:3.5mm 0;border-bottom:.3mm solid #d8deea}
.day b{font:600 8pt "JetBrains Mono";color:#2f56e0}
.day .box{width:5mm;height:5mm;border:.4mm solid #3563f5;border-radius:1mm}
/* toc */
.toc a{display:grid;grid-template-columns:12mm 1fr 10mm;gap:3mm;align-items:center;padding:3.4mm 0;border-bottom:.3mm solid #d8deea;color:#0c1630;text-decoration:none;font-weight:600}
.toc a span:first-child{font:600 8pt "JetBrains Mono";color:#2f56e0}
.toc a span:last-child{font:500 8pt "JetBrains Mono";color:#5b6886;text-align:end}
.toc .thumb{display:none}
.credits li{font-size:7.5pt;margin-bottom:1.2mm}
a{color:#2f56e0;text-decoration:none}
.qr{width:24mm;height:24mm}
'''

def build(out,lang,m,licenses,fonts_href,chapter_page=None):
 c={**T[lang],**EXTRA[lang]};pages=[];chapter_page=chapter_page or {}
 by=lambda name:licenses.get(name,{})
 def credit(name):
  l=by(name);return f'<span class="credit">{e(c["credits"])}: {e(l.get("photographer_name",""))} / {e(l.get("source_site",""))}</span>' if l else ''
 def sheet(body,cls='',ident=''):
  # Photo pages (cover, chapter openers) are fixed full-bleed sheets; text pages flow across as many pages as they need.
  kind='page' if 'dark' in cls else 'flow'
  pages.append(f'<section class="{kind} {cls}"'+(f' id="{ident}"' if ident else '')+f'>{body}</section>')
 # Cover: the same composition as the website cover (design-preview/cover/cover.html).
 t1,t2={'ar':('من الصفر إلى صناعة المحتوى','بالذكاء الاصطناعي'),'en':('From Zero to','AI-Powered Content Creation'),'ru':('С нуля до создания контента','с помощью ИИ')}[lang]
 sheet(f'<div class="bleed"><img src="{photo("a-1-dark-creator-studio")}" alt=""></div><div class="shade"></div><div class="vf"><i></i><i></i><i></i><i></i></div>'
  f'<div class="top"><span class="rec">REC</span><span class="badge">9:16 · AI</span></div>'
  f'<div class="copy"><p class="eyebrow">{e(c["guide"])}</p><h1>{e(t1)}<em>{e(t2)}</em></h1><p class="sub">{e(c["subtitle"])}</p></div>'
  f'<div class="bar"><div class="author"><img src="{(ROOT/"assets/portraits/ali-kit-dark-520.webp").as_uri()}" alt=""><div><b>{"علي الخزاعي" if lang=="ar" else "Ali Alkhuzaee"}</b><span>{e(c["about"].split(" · ")[1])}</span></div></div><div class="ed">{e(c["edition"])}<small>ALIALKHUZAEE.COM</small></div></div>','dark cover')
 sheet(f'<p class="eyebrow">ALI ALKHUZAEE</p><h2>{e(c["guide"])}</h2><p class="lead">{e(c["intro"])}</p><div class="panel">{e(c["how"])}</div><h3>© 2026 Ali Alkhuzaee</h3><p class="fine">{e(c["legal"])}</p><p class="fine">{e(c["about"])}</p><p class="fine">{e(c["review"])}</p>')
 toc_index=len(pages);pages.append('TOC')
 used=0
 def lesson_photo(art):
  nonlocal used
  name=ART_PHOTOS.get(art) or FALLBACK[used%len(FALLBACK)];used+=1;return name
 current=None
 for idx,item in enumerate(m.lessons):
  ch=item['ch']
  if ch!=current:
   current=ch;name=CHAPTER_PHOTOS[(ch-1)%len(CHAPTER_PHOTOS)]
   sheet(f'<div class="bleed"><img src="{photo(name)}" alt=""></div><div class="shade"></div><div class="vf"><i></i><i></i><i></i><i></i></div><div class="num">{ch:02d}</div><div class="ttl"><p class="eyebrow">{e(c["chapter"])} {ch:02d}</p><h2>{e(c["chapters"][ch-1])}</h2></div>{credit(name)}','dark opener',f'ch{ch}')
  name=lesson_photo(item.get('art',''))
  body=(f'<p class="eyebrow">{ch:02d} / {e(c["chapters"][ch-1])}</p><h2>{e(item["title"][lang])}</h2><p class="lead">{e(item["core"][lang])}</p>'
   f'<div class="photo"><img src="{photo(name,900)}" alt="">{credit(name)}</div>'
   f'<h3>{e(c["steps"])}</h3><ol class="steps">'+''.join(f'<li>{e(s.strip())}</li>' for s in item['steps'][lang].split('|'))+'</ol>'
   f'<div class="panel"><h3>{e(c["example"])}</h3><p>{e(item["example"][lang])}</p></div><div class="exercise"><h3>{e(c["exercise"])}</h3><p>{e(item["exercise"][lang])}</p></div>')
  sheet(body)
  last=idx==len(m.lessons)-1 or m.lessons[idx+1]['ch']!=ch
  if last and ch==5:
   for start in range(0,len(m.hooks),10):
    sheet(f'<p class="eyebrow">05 / {e(c["chapters"][4])}</p><h2>{e(c["hooks"])}</h2>'+''.join(f'<div class="hook"><b>{i+1:02d}</b><span>{e(h[lang])}</span></div>' for i,h in enumerate(m.hooks[start:start+10],start)))
  if last and ch==6:
   for i,t in enumerate(m.tools):
    body=f'<p class="eyebrow">06 / {e(c["tools"])} · {i+1:02d}</p><div class="tool-head"><span class="mark">{e(t["name"][:1])}</span><h2>{e(t["name"])}</h2></div><p class="lead">{e(t["role"][lang])}</p><p class="url"><a href="{e(t["url"])}">{e(t["url"])}</a></p>'
    for key in ('access','rights','task'):body+=f'<div class="card"><h3>{e(c[key])}</h3><p>{e(t[key][lang])}</p></div>'
    body+=f'<p class="fine">{e(c["verified"])}: {e(m.VERIFIED)}</p><p class="url"><a href="{e(t["source"])}">{e(c["source"])}: {e(t["source"])}</a></p>'
    sheet(body)
  if last and ch==7:
   for start in range(0,len(m.prompts),2):
    body=f'<p class="eyebrow">07 / {e(c["chapters"][6])}</p><h2>{e(c["prompts"])}</h2><p class="fine">{e(c["promptRule"])}</p>'
    for i,p in enumerate(m.prompts[start:start+2],start):body+=f'<div class="prompt"><h3>{i+1:02d} / {e(p["title"][lang])}</h3><p class="task">{e(p["task"][lang])}</p><p class="fine">{e(c["promptExample"])}: {e(p["example"][lang])}</p><p class="fine">{e(c["promptCheck"])}</p></div>'
    sheet(body+f'<h3>{e(c["notes"])}</h3><div class="notes"></div>')
  if last and ch==10:
   for start in range(0,len(m.days),6):
    sheet(f'<p class="eyebrow">10 / {e(c["chapters"][9])}</p><h2>{e(c["plan"])}</h2>'+''.join(f'<div class="day"><b>{e(c["day"])} {i+1:02d}</b><p>{e(d[lang])}</p><span class="box"></span></div>' for i,d in enumerate(m.days[start:start+6],start)))
 pages[toc_index]=f'<section class="flow"><p class="eyebrow">{e(c["guide"])}</p><h2>{e(c["toc"])}</h2><nav class="toc">'+''.join(f'<a href="#ch{i}"><span>{i:02d}</span><span>{e(t)}</span><span>{chapter_page.get(i,"")}</span></a>' for i,t in enumerate(c['chapters'],1))+'</nav></section>'
 import qrcode
 qr=out/f'qr-{lang}.png';qrcode.make('https://alialkhuzaee.com').save(qr)
 used_photos=sorted({n for n in CHAPTER_PHOTOS+list(ART_PHOTOS.values())+FALLBACK+['a-1-dark-creator-studio'] if n in licenses})
 sheet(f'<p class="eyebrow">ALI ALKHUZAEE</p><h2>{e(c["refTitle"])}</h2><p>{e(c["refText"])}</p><div class="panel"><p>{e(c["location"])}</p><p>{e(c["about"])}</p></div><p><a href="mailto:ali@alialkhuzaee.com">ali@alialkhuzaee.com</a> · <a href="https://alialkhuzaee.com">alialkhuzaee.com</a></p><img class="qr" src="{qr.as_uri()}" alt="">'
  f'<h3>{e(c["credits"])}</h3><p class="fine">{e(c["creditsText"])}</p><ul class="credits fine">'+''.join(f'<li>{e(licenses[n]["photographer_name"])} / {e(licenses[n]["source_site"])} — <span dir="ltr">{e(licenses[n]["photo_page_url"])}</span></li>' for n in used_photos)+'</ul>')
 html=(f'<!doctype html><html lang="{lang}" dir="{"rtl" if lang=="ar" else "ltr"}"><head><meta charset="utf-8"><title>{e(c["title"])}</title><meta name="author" content="Ali Alkhuzaee">'
  f'<link rel="stylesheet" href="{fonts_href}"><style>{CSS}@page{{@bottom-left{{content:"ALI ALKHUZAEE · {e(c["guide"])}";{ARABIC_FOLIO if lang=="ar" else ""}}}}}</style></head><body>'+''.join(pages)+'</body></html>')
 src=out/f'Creator_Guide_v2_{lang.upper()}.html';src.write_text(html)
 return src

RENDER_JS='''const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
for(const [src,pdf] of JSON.parse(process.argv[2])){await p.goto(src,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);
 const overflow=await p.evaluate(()=>[...document.querySelectorAll('.page')].map((s,i)=>s.scrollHeight>s.clientHeight+2?i+1:0).filter(Boolean));
 await p.pdf({path:pdf,preferCSSPageSize:true,printBackground:true,outline:true,tagged:true});console.log(JSON.stringify({pdf,overflow}))}
await b.close()})();'''
FONTS='https://fonts.googleapis.com/css2?family=Alexandria:wght@300;400;600;700;800&family=Geologica:wght@300;400;600;700;800&family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&family=Manrope:wght@400;500;600;700&display=block'

def render(jobs):
 with tempfile.TemporaryDirectory() as tmp:
  js=Path(tmp)/'render.js';js.write_text(RENDER_JS)
  res=subprocess.run(['node',str(js),json.dumps(jobs)],check=True,capture_output=True,text=True)
 return {r['pdf']:r for r in map(json.loads,res.stdout.splitlines())}

def chapter_pages(pdf):
 """Page numbers of the chapter openers, read from the PDF's named destinations (#ch1 … #ch10)."""
 from pypdf import PdfReader
 r=PdfReader(pdf);found={}
 for name,dest in r.named_destinations.items():
  key=str(name).lstrip('/')
  if key.startswith('ch') and key[2:].isdigit():found[int(key[2:])]=r.get_destination_page_number(dest)+1
 return found,len(r.pages)

def main():
 if len(sys.argv)<3:raise SystemExit(__doc__)
 source=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve()
 if out.is_relative_to(ROOT):raise SystemExit('Paid editions must be built outside the public repository.')
 out.mkdir(parents=True,exist_ok=True)
 spec=importlib.util.spec_from_file_location('guide_content',source/'content.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 licenses={Path(x['file']).stem:x for x in json.loads((PHOTOS/'LICENSES.json').read_text())}
 langs=sys.argv[3:] or ['en','ar','ru']
 pdfs={lang:str(out/f'Creator_Guide_v2_{lang.upper()}.pdf') for lang in langs}
 # Pass 1 finds where each chapter lands; pass 2 prints those numbers in the contents page (same digit count, so nothing reflows).
 render([[build(out,lang,m,licenses,FONTS).as_uri(),pdfs[lang]] for lang in langs])
 found={lang:chapter_pages(pdfs[lang])[0] for lang in langs}
 res=render([[build(out,lang,m,licenses,FONTS,{k:f'{v:02d}' for k,v in found[lang].items()}).as_uri(),pdfs[lang]] for lang in langs])
 for lang in langs:
  final,count=chapter_pages(pdfs[lang])
  manifest={'language':lang,'design':'v2','pages':count,'chapters':final,'toc_matches':final==found[lang],'overflowing_photo_pages':res[pdfs[lang]]['overflow'],'hooks':len(m.hooks),'prompts':len(m.prompts),'tools':len(m.tools),'status':'editorial-review','verified_on':m.VERIFIED}
  (out/f'manifest-v2-{lang}.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False));print(Path(pdfs[lang]).name,json.dumps(manifest,ensure_ascii=False))

if __name__=='__main__':main()
