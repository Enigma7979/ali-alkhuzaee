"""Verify private editions and generate explicitly selected public previews."""
from pathlib import Path
from pypdf import PdfReader
from PIL import Image,ImageDraw
import sys,json,subprocess
root=Path(__file__).resolve().parents[1];private=Path(sys.argv[1]).resolve();qa=private/'qa';qa.mkdir(exist_ok=True)
results=[]
for lang in ['en','ar','ru']:
 pdf=private/f'Creator_Guide_{lang.upper()}.pdf';manifest=json.loads((private/f'manifest-{lang}.json').read_text());r=PdfReader(pdf)
 assert len(r.pages)==manifest['expected_pages']==80
 assert all(len(p.extract_text().strip())>80 for p in r.pages)
 assert len(r.outline)>=10
 assert len(r.pages[2].get('/Annots',[]))==10
 for item in r.outline:
  if isinstance(item,dict):assert 0<=r.get_destination_page_number(item)<len(r.pages)
 subprocess.run(['pdftoppm','-scale-to','500','-jpeg','-jpegopt','quality=75',str(pdf),str(qa/lang)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
 paths=sorted(qa.glob(lang+'-*.jpg'));paths=paths[:80];sheet=Image.new('RGB',(8*160,10*235),'#cbd5e1');d=ImageDraw.Draw(sheet)
 for i,p in enumerate(paths):
  im=Image.open(p);im.thumbnail((150,212));x=(i%8)*160+5;y=(i//8)*235+18;sheet.paste(im,(x,y));d.text((x,y-15),str(i+1),fill='black')
 sheet.save(qa/f'contact-{lang}.jpg')
 selected={1:1,6:manifest['chapters']['2'],16:manifest['chapters']['5'],62:manifest['chapters']['10']+2}
 for key,page in selected.items():
  prefix=qa/f'preview-{lang}-{key}'
  subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-scale-to','1200','-png','-singlefile',str(pdf),str(prefix)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
  Image.open(str(prefix)+'.png').save(root/'assets/products'/f'preview-{lang}-{key}.webp',quality=86)
 results.append({'language':lang,'pages':len(r.pages),'annotations':sum(len(p.get('/Annots',[])) for p in r.pages),'previews':selected})
print(json.dumps(results,indent=2))
