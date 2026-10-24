"""Rebuild the English media kit: python scripts/build_media_kit_pdf.py"""
from pathlib import Path
import json
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'media-kit/data.json').read_text())
OUT=ROOT/'media-kit/Ali-Alkhuzaee-Media-Kit.pdf'
for name,file in [('Inter','DejaVuSans.ttf'),('InterBold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
W,H=595.28,841.89
C=canvas.Canvas(str(OUT),pagesize=(W,H));C.setTitle('Ali Alkhuzaee | Media Kit & Brand Partnerships');C.setAuthor('Ali Alkhuzaee');C.setSubject('AI, technology and multilingual creator partnerships')
BG='#08090b';PANEL='#111722';MUTED='#a2aabd';WHITE='#f3f3f4';BLUE='#8eb9ff'
def optimized_image(path):
 im=Image.open(path).convert('RGB');im.thumbnail((700,700));buffer=BytesIO();im.save(buffer,format='JPEG',quality=88,optimize=True);buffer.seek(0);return ImageReader(buffer)
def text(x,y,t,size=10,color=WHITE,bold=False):C.setFillColor(HexColor(color));C.setFont('InterBold' if bold else 'Inter',size);C.drawString(x,y,t)
def para(x,y,t,width=490,size=10,leading=17,color=MUTED):
 words=t.split();line=''
 for word in words:
  next=(line+' '+word).strip()
  if pdfmetrics.stringWidth(next,'Inter',size)>width:
   text(x,y,line,size,color);y-=leading;line=word
  else:line=next
 if line:text(x,y,line,size,color)
 return y-leading

def bg(n):
 C.setFillColor(HexColor(BG));C.rect(0,0,W,H,fill=1,stroke=0)
 C.setStrokeColor(HexColor('#273247'));C.line(42,793,W-42,793);text(42,810,'Ali Alkhuzaee',11);text(405,810,'MEDIA KIT / 2026',8,BLUE)
 C.line(42,45,W-42,45);text(42,28,'alialkhuzaee.com',8,MUTED);C.linkURL('https://alialkhuzaee.com',(42,20,180,40),relative=0);text(W-68,28,f'0{n}',8,MUTED)
def label(y,t):text(42,y,t,8,BLUE)
def card(x,y,w,h):C.setFillColor(HexColor(PANEL));C.roundRect(x,y,w,h,12,fill=1,stroke=0)
def link(x,y,t,url,size=9):text(x,y,t,size,BLUE);C.linkURL(url,(x,y-3,x+pdfmetrics.stringWidth(t,'Inter',size),y+12),relative=0)
bg(1);label(756,'BRAND PARTNERSHIPS')
text(42,715,'Partner with',29);text(42,673,'Ali Alkhuzaee',32,BLUE,True)
text(42,643,'AI & Tech Creator',12);text(42,622,'Founder of Study UA Plus',10,MUTED)
C.drawImage(optimized_image(ROOT/'ali-alkhuzaee.jpeg'),390,615,160,160,mask='auto',preserveAspectRatio=True)
y=para(42,580,'Make useful technology part of everyday life.',size=17,leading=24,color=WHITE)
y=para(42,y-10,'Connect your brand with an Arabic-speaking audience interested in AI, technology and productivity through practical, engaging creator-led content. Clear explanations bring useful tools, workflows and emerging technologies into everyday context.',size=10,leading=17)
label(454,'WHY PARTNER WITH ALI?')
items=[('A focused niche','AI, technology, productivity and automation.'),('Clear Arabic storytelling','Complex features connected to everyday needs.'),('Short-form creative','Relatable problems and practical applications.'),('Technical perspective','A PhD in Computer Engineering and hands-on automation projects.')]
for i,(title,body) in enumerate(items):
 x=42+(i%2)*260;y=425-(i//2)*86;card(x,y-60,249,75);text(x+15,y-6,title,10,WHITE,True);para(x+15,y-25,body,218,9,14)
label(238,'MULTILINGUAL CREATOR & INTERNATIONAL PERSPECTIVE')
para(42,214,'Fluent in Arabic, English, Russian and Ukrainian, Ali can develop content and brand partnerships in all four languages. His perspective is shaped by approximately 18 years of study and visits in Ukraine and five years of living in Belgium.',size=10,leading=17)
para(42,131,'For SaaS and AI brands: multilingual campaigns can be tailored to the product, language and creative brief. Each partnership can be shaped around the brand objectives, creative format and intended language.',size=9,leading=15)
C.showPage();bg(2);label(756,'COLLABORATION FORMATS');text(42,720,'A format that fits your product.',24)
formats=['Sponsored Reels & Short-form Videos','AI Tool Reviews & Demonstrations','Product Integrations','Brand Partnerships','Educational Technology Campaigns','Long-term Brand Ambassadorships','Multilingual Campaigns']
for i,f in enumerate(formats):text(42,685-i*23,f'{i+1:02}   {f}',10)
label(493,'SELECTED PUBLISHED CONTENT')
for i,v in enumerate(DATA['work']):
 x=42+i*174;im=optimized_image(ROOT/'assets/media-kit'/f'{v["id"]}.webp');# preserve the full original frame
 C.drawImage(im,x,303,156,174,preserveAspectRatio=True,anchor='c',mask='auto')
 title=v['title']['en'];para(x,286,title,155,9,13,color=WHITE);link(x,252,'Watch on YouTube',v['url'],8)
label(215,'EXPLORE THE CHANNELS')
for i,(name,url) in enumerate(DATA['platforms'].items()):link(42+(i%3)*174,190-(i//3)*22,name+'  /',url,9)
C.setStrokeColor(HexColor('#273247'));C.line(42,146,W-42,146)
text(42,122,'Let’s collaborate.',19,WHITE,True)
para(42,101,'Share your product, campaign objective, timeline and proposed budget.',490,9,14)
link(42,64,'ali@alialkhuzaee.com','mailto:ali@alialkhuzaee.com?subject=Brand%20Partnership%20Inquiry%20%E2%80%94%20Ali%20Alkhuzaee',11)
C.save();print(OUT)
