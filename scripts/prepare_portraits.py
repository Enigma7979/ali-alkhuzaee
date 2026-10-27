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
# Half-body Media Kit portrait (book identity, Oct 2026): the standing hero photograph with its reviewed alpha mask,
# cropped to head-to-jacket-hem and resized only. No retouching, no generated pixels; replaces the pointing photo.
alpha=Image.open(ROOT/'masks'/'hero-alpha.png').convert('L')
standing=Image.open(ROOT/'originals'/'hero-original.png').convert('RGBA').resize(alpha.size,Image.Resampling.LANCZOS)
standing.putalpha(alpha)
s=alpha.size[0]/1600
half=standing.crop(tuple(round(v*s) for v in (470,0,1150,850)))
# The mask is 1254 px, so the crop is 533 x 666 at full resolution; 400 is the small size. Thumbnail never upscales.
for width in [400,half.size[0]]:
 derivative=half.copy();derivative.thumbnail((width,width*2));derivative.save(ROOT/f'ali-standing-half-{width}.webp','WEBP',quality=90,method=6)
# Social card for the Media Kit (og:image): the same standing photograph on its own white background, cropped only.
Image.open(ROOT/'originals'/'hero-original.png').convert('RGB').crop((40,0,1560,800)).resize((1200,632),Image.Resampling.LANCZOS).save(ROOT/'ali-standing-og.jpg',quality=88,optimize=True,progressive=True)
