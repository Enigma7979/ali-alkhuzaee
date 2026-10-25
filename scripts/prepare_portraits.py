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
