"""Reproduce optimized cutouts using original photograph pixels and reviewed extraction masks.
No generated face/subject pixels are used. Originals and alpha masks are preserved.
"""
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]/'assets/portraits'
for kind,original,widths in [('hero','hero-original.png',[420,690]),('partnership','partnership-original.jpeg',[480,900])]:
 alpha=Image.open(ROOT/'masks'/f'{kind}-alpha.png').convert('L')
 image=Image.open(ROOT/'originals'/original).convert('RGBA').resize(alpha.size,Image.Resampling.LANCZOS)
 image.putalpha(alpha)
 if kind=='hero':image=image.crop(alpha.point(lambda x:255 if x>20 else 0).getbbox())
 for width in widths:
  derivative=image.copy();derivative.thumbnail((width,1600 if kind=='hero' else width))
  derivative.save(ROOT/f'ali-{kind}-{width}.webp','WEBP',quality=90 if kind=='hero' else 92,method=6)
# Dark Media Kit portrait (design system v2): natural pixels of the supplied dark-background photo, resized only.
dark=Image.open(ROOT/'originals'/'pointing-dark-original.jpeg').convert('RGB')
for width in [520,900]:
 derivative=dark.copy();derivative.thumbnail((width,width));derivative.save(ROOT/f'ali-kit-dark-{width}.webp','WEBP',quality=86,method=6)
# Guide covers for v2 product layouts: the cover area cropped from the real page-1 previews.
PRODUCTS=ROOT.parent/'products'
for lang in ['ar','en','ru']:
 Image.open(PRODUCTS/f'preview-{lang}-1.webp').convert('RGB').crop((72,67,773,1051)).save(PRODUCTS/f'cover-{lang}.webp','WEBP',quality=88,method=6)
