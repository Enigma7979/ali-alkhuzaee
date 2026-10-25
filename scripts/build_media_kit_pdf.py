"""Build the standalone English Media Kit from the current verified website content."""
from pathlib import Path
from io import BytesIO
import json
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'media-kit/data.json').read_text())
HOME=json.loads((ROOT/'assets/translations.json').read_text())['en']
COPY=json.loads((ROOT/'media-kit/translations.json').read_text())['en']
OUT=ROOT/'media-kit/Ali-Alkhuzaee-Media-Kit.pdf'
for n,f in [('Regular','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(n,'/usr/share/fonts/truetype/dejavu/'+f))
W,H=595.28,841.89
C=canvas.Canvas(str(OUT),pagesize=(W,H));C.setTitle('Ali Alkhuzaee | Media Kit & Brand Partnerships');C.setAuthor('Ali Alkhuzaee');C.setSubject('AI, technology, SaaS and multilingual creator partnerships');C.setKeywords('Ali Alkhuzaee, AI, automation, Arabic, English, Russian, Ukrainian, Belgium, Ukraine')
INK='#15233c';BLUE='#2563eb';MUTED='#53647c';NAVY='#111d35';PAPER='#f8fafc';CYAN='#86dcff'
def txt(x,y,t,size=10,color=INK,bold=False):
 C.setFillColor(HexColor(color));C.setFont('Bold' if bold else 'Regular',size);C.drawString(x,y,t)
def para(x,y,t,width=505,size=10,leading=16,color=MUTED,bold=False):
 font='Bold' if bold else 'Regular';line=''
 for w in t.split():
  test=(line+' '+w).strip()
  if pdfmetrics.stringWidth(test,font,size)>width and line:txt(x,y,line,size,color,bold);y-=leading;line=w
  else:line=test
 if line:txt(x,y,line,size,color,bold)
 return y-leading

def image(path,x,y,w,h):
 im=Image.open(path).convert('RGBA');bg=Image.new('RGBA',im.size,'#f8fafc');bg.alpha_composite(im);im=bg.convert('RGB');im.thumbnail((900,900));b=BytesIO();im.save(b,format='JPEG',quality=92,optimize=True);b.seek(0);C.drawImage(ImageReader(b),x,y,w,h,preserveAspectRatio=True,anchor='c')
def rect(x,y,w,h,color,r=0):
 C.setFillColor(HexColor(color));C.roundRect(x,y,w,h,r,stroke=0,fill=1)
def rule(y,color='#d7dfeb'):C.setStrokeColor(HexColor(color));C.line(40,y,W-40,y)
def link(x,y,label,url,size=9,color=BLUE):
 txt(x,y,label,size,color);C.linkURL(url,(x,y-3,x+pdfmetrics.stringWidth(label,'Regular',size),y+12),relative=0)
def bg(page):
 rect(0,0,W,H,PAPER);txt(40,806,'ALI ALKHUZAEE',10,INK,True);txt(398,806,'MEDIA KIT / 2026',8,BLUE,True);rule(791)
 rule(39);link(40,23,'alialkhuzaee.com','https://alialkhuzaee.com',8);txt(W-57,23,f'0{page}',8,MUTED)
def label(y,s):txt(40,y,s,8,BLUE,True)
bg(1);label(755,'AI & TECHNOLOGY CREATOR')
txt(40,715,'Technology,',31,INK,True);txt(40,675,'made human.',31,BLUE,True)
txt(40,642,'Ali Alkhuzaee',18,INK,True)
para(40,620,'AI & Tech Creator | N8N Automation Engineer',300,9,14)
para(40,599,'PhD in Computer Engineering',300,9,14)
para(40,579,'Founder & CEO of Study UA Plus',300,9,14)
image(ROOT/'assets/portraits/ali-partnership-900.webp',363,565,190,190)
rect(40,448,515,97,NAVY,12)
txt(57,523,'Partner with Ali Alkhuzaee',15,'#ffffff',True)
para(57,499,COPY['intro'],480,9,15,'#c9d9ef')
label(416,'WHY PARTNER WITH ALI?')
for i,(title,body) in enumerate(COPY['whyCards']):
 x=40+(i%2)*265;y=389-(i//2)*78
 para(x,y,title,245,10,14,INK,True);para(x,y-21,body,245,8.6,13)
rule(226);label(204,'MULTILINGUAL CREATOR / INTERNATIONAL PERSPECTIVE')
para(40,181,'Arabic. English. Russian. Ukrainian.',505,13,18,INK,True)
para(40,153,HOME['globalText'],505,9,14)
para(40,109,HOME['globalHistory'],505,8.5,14)
para(40,66,HOME['location'],505,8,12,BLUE,True)
C.showPage();bg(2)
label(755,'BRAND PARTNERSHIPS')
txt(40,720,'Useful products. Clear stories.',24,INK,True)
para(40,695,'Campaigns for AI, SaaS, technology, automation and creator-tool brands.',505,9,15)
for i,(title,desc) in enumerate(COPY['formats']):
 x=40+(i%2)*266;y=659-(i//2)*35
 txt(x,y,f'{i+1:02}',8,BLUE,True);para(x+22,y,title,229,8.7,12,INK,True)
rule(516);label(494,'SELECTED PUBLISHED CONTENT')
for i,v in enumerate(DATA['work']):
 x=40+i*176;image(ROOT/'assets/media-kit'/f'{v["id"]}.webp',x,350,162,128)
 para(x,333,v['title']['en'],160,9,13,INK,True);link(x,293,'Watch on YouTube',v['url'],8)
label(255,'EXPLORE THE CHANNELS')
for i,(name,url) in enumerate(DATA['platforms'].items()):link(40+(i%3)*176,230-(i//3)*22,name+'  /',url,9)
rect(40,63,515,119,NAVY,12)
txt(57,159,'Let’s build something worth watching.',16,'#ffffff',True)
para(57,137,'Share your product, campaign objective, timeline and proposed budget.',480,8.7,14,'#c9d9ef')
link(57,108,'ali@alialkhuzaee.com','mailto:ali@alialkhuzaee.com?subject=Brand%20Partnership%20Inquiry%20%E2%80%94%20Ali%20Alkhuzaee',13,CYAN)
link(57,82,'Belgium: +32 467 68 52 50','tel:+32467685250',8,'#d9e7fa');link(318,82,'Ukraine: +380 63 717 17 71','tel:+380637171771',8,'#d9e7fa')
C.save();print(OUT)
