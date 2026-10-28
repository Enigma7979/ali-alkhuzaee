"""Public website assets for the From Zero to Hero edition: the chosen cover (concept A, Aperture) per language.

python scripts/zero_to_hero/site_assets.py [FINAL_DIR]
  -> assets/products/cover-v3-{ar,en,ru}.webp (1000 x 1420)
  -> with FINAL_DIR (holding build.py output per language, FINAL_DIR/{ar,en,ru}/proof/png):
     preview-v3-{lang}-N.webp (540 wide) and preview-v3-{lang}-N-lg.webp (full) for the pages in PREVIEW_PAGES.
     Only these few pages are public; the manuscript stays private.
Needs network for Google Fonts.
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import build, covers  # noqa: E402

OUT = ROOT / 'assets/products'
LANGS = ('ar', 'en', 'ru')
# cover, contents, three-point lighting plan (unit 04), prompts 01-05, hooks 01-10, the 30-day plan (unit 12).
# Page numbers of the final edition; all three languages share the same pagination.
PREVIEW_PAGES = (1, 4, 25, 73, 86, 66)


def main():
    html = build.head('From Zero to Hero — covers') + ''.join(covers.cover('A', l) for l in LANGS) + '</body></html>'
    with tempfile.TemporaryDirectory() as tmp:
        src = pathlib.Path(tmp) / 'covers.html'
        src.write_text(html, encoding='utf-8')
        env = dict(os.environ, NODE_PATH=os.environ.get('NODE_PATH', '/usr/local/lib/node_modules_global'))
        res = subprocess.run(['node', str(HERE / 'render.mjs'), str(src), '-', tmp, '2'], check=True, capture_output=True, text=True, env=env)
        report = json.loads(res.stdout)
        if report['overflow']:
            sys.exit(f'cover overflow: {report["overflow"]}')
        for i, lang in enumerate(LANGS, 1):
            im = Image.open(pathlib.Path(tmp) / f'p{i:03d}.png').convert('RGB').resize((1000, 1420), Image.Resampling.LANCZOS)
            im.save(OUT / f'cover-v3-{lang}.webp', 'WEBP', quality=90, method=6)
            print('wrote', (OUT / f'cover-v3-{lang}.webp').relative_to(ROOT))


def previews(final_dir):
    for lang in LANGS:
        for n in PREVIEW_PAGES:
            im = Image.open(pathlib.Path(final_dir) / lang / 'proof' / 'png' / f'p{n:03d}.png').convert('RGB')
            im.resize((540, 767), Image.Resampling.LANCZOS).save(OUT / f'preview-v3-{lang}-{n}.webp', 'WEBP', quality=88, method=6)
            im.save(OUT / f'preview-v3-{lang}-{n}-lg.webp', 'WEBP', quality=86, method=6)
            print('wrote preview', lang, n)


if __name__ == '__main__':
    main()
    if len(sys.argv) > 1:
        previews(sys.argv[1])
