"""Build web derivatives of the licensed Creator Guide photos and the new Short's local cover.

python scripts/prepare_guide_photos.py SOURCE_DIR
  SOURCE_DIR holds the original 1800px JPEGs (a-1-…jpg … h-2-…jpg), LICENSES.json and 6m0NC1etQIU-oar2.jpg.
  Writes assets/presentation/photos/<name>-{1600,900}.webp, assets/presentation/photos/LICENSES.json
  and assets/media-kit/6m0NC1etQIU.webp (720x1280, the YouTube oar2 frame).
"""
from pathlib import Path
import json,shutil,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/presentation/photos'

def main():
 src=Path(sys.argv[1]);OUT.mkdir(parents=True,exist_ok=True)
 licenses=json.loads((src/'LICENSES.json').read_text())
 for entry in licenses:
  im=Image.open(src/entry['file']).convert('RGB');stem=Path(entry['file']).stem
  for w in (1600,900):
   r=im.resize((w,round(im.height*w/im.width)),Image.LANCZOS)
   r.save(OUT/f'{stem}-{w}.webp','WEBP',quality=74 if w==1600 else 72,method=6)
 shutil.copyfile(src/'LICENSES.json',OUT/'LICENSES.json')
 cover=Image.open(src/'6m0NC1etQIU-oar2.jpg').convert('RGB')
 cover.resize((720,1280),Image.LANCZOS).save(ROOT/'assets/media-kit/6m0NC1etQIU.webp','WEBP',quality=80,method=6)
 print(len(licenses),'photos')

if __name__=='__main__':main()
