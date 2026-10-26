"""Render the v2 Creator Guide cover (design-preview/cover/cover.html) to assets/products/cover-v2-{ar,en,ru}.webp.

Needs a local server on the repository root, e.g. python -m http.server 4173, and Playwright for Node.
python scripts/render_guide_cover.py [BASE_URL]
"""
from pathlib import Path
import subprocess,sys,tempfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
BASE=sys.argv[1] if len(sys.argv)>1 else 'http://localhost:4173'
JS='''const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1400,height:1960}});
for(const l of ['ar','en','ru']){await p.goto(process.argv[2]+'/design-preview/cover/cover.html?lang='+l,{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);await p.screenshot({path:process.argv[3]+'/'+l+'.png'})}
await b.close()})();'''
with tempfile.TemporaryDirectory() as tmp:
 script=Path(tmp)/'render.js';script.write_text(JS)
 subprocess.run(['node',str(script),BASE,tmp],check=True)
 for l in ('ar','en','ru'):
  Image.open(Path(tmp)/f'{l}.png').convert('RGB').resize((1000,1400),Image.LANCZOS).save(ROOT/f'assets/products/cover-v2-{l}.webp','WEBP',quality=86,method=6)
print('rendered 3 covers')
