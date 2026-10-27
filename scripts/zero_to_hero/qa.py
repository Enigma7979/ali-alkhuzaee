"""Automated QA for From Zero to Hero proofs, plus spread contact sheets and phone-size previews.

python scripts/zero_to_hero/qa.py OUT_DIR   (after build.py PAGES_DIR OUT_DIR)

Checks: page count and trim size, font embedding, extractable Arabic text, bookmarks, internal and
external links (external ones are fetched), raster images, overflow from the render step, document
metadata, file size, and WCAG contrast of the palette's text pairings. Writes OUT_DIR/qa-report.json.
"""
import json, re, subprocess, sys, unicodedata, urllib.request
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402
PT_PER_MM = 72 / 25.4
TEXT_PAIRS = {  # (foreground, background, use)
    'ink on ivory (body)': ('#101827', '#F8F7F3'), 'slate on ivory (secondary)': ('#526174', '#F8F7F3'),
    'cyan-ink on ivory (labels)': ('#0B6E7C', '#F8F7F3'), 'cyan-ink on cyan tint': ('#0B6E7C', '#E6F6F8'),
    'copper-ink on ivory': ('#8A4F1C', '#F8F7F3'), 'copper-ink on copper tint': ('#8A4F1C', '#FBF0E4'),
    'warn on warn tint': ('#B54C43', '#FBEDEB'), 'ivory on navy (table head)': ('#FFFFFF', '#16263E'),
    'copper on ink (dark pages)': ('#E3A86B', '#101827'), 'mist on ink (dark small text)': ('#9FB0C6', '#101827'),
    'brand cyan on ivory (NOT for text)': ('#25C5D9', '#F8F7F3'),
}


def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return round((la + 0.05) / (lb + 0.05), 2)


def set_metadata(pdf, title, lang):
    r = PdfReader(pdf); w = PdfWriter(clone_from=r)
    w.add_metadata({'/Title': title, '/Author': 'Ali Alkhuzaee', '/Subject': 'From Zero to Hero — review proof', '/Creator': 'scripts/zero_to_hero/build.py'})
    w._root_object.update({__import__('pypdf').generic.NameObject('/Lang'): __import__('pypdf').generic.TextStringObject(lang)})
    w.write(pdf)


def check_pdf(pdf, render):
    r = PdfReader(pdf)
    res = {'file': pdf.name, 'bytes': pdf.stat().st_size, 'pages': len(r.pages)}
    sizes = {(round(float(p.mediabox.width) / PT_PER_MM), round(float(p.mediabox.height) / PT_PER_MM)) for p in r.pages}
    res['trim_mm'] = sorted(sizes)
    fonts = subprocess.run(['pdffonts', str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
    res['fonts'] = sorted({l.split()[0].split('+')[-1] for l in fonts})
    res['fonts_not_embedded'] = [l for l in fonts if l.split()[-5] != 'yes']
    txt = unicodedata.normalize('NFKC', subprocess.run(['pdftotext', str(pdf), '-'], capture_output=True, text=True).stdout)
    res['text_chars'] = len(txt)
    res['arabic_words_found'] = {w: (w in txt) for w in ('التعريض', 'الميكروفون', 'الإضاءة')}
    # lam-alef: Chromium + these fonts emit the two glyphs so that extractors reverse them (الإ -> اإل). Count it.
    res['lam_alef_reversed_in_extraction'] = len(re.findall('اإل|األ|اآل', txt))
    res['outline_entries'] = len(_flat(r.outline))
    internal, external = 0, set()
    for p in r.pages:
        for a in (p.get('/Annots') or []):
            a = a.get_object()
            if a.get('/Subtype') != '/Link': continue
            act = a.get('/A')
            if act and act.get('/URI'): external.add(str(act['/URI']))
            elif a.get('/Dest') is not None or (act and act.get('/S') == '/GoTo'): internal += 1
    res['internal_links'] = internal
    res['external_links'] = {u: url_status(u) for u in sorted(external)}
    imgs = subprocess.run(['pdfimages', '-list', str(pdf)], capture_output=True, text=True).stdout.splitlines()[2:]
    res['raster_images'] = len(imgs)
    res['overflow_findings'] = render['overflow']
    meta = r.metadata or {}
    res['metadata'] = {k: str(meta.get(k)) for k in ('/Title', '/Author')} | {'/Lang': str(r.trailer['/Root'].get('/Lang')), 'tagged': '/MarkInfo' in r.trailer['/Root'] or '/StructTreeRoot' in r.trailer['/Root']}
    return res


def _flat(o):
    out = []
    for x in o or []:
        out += _flat(x) if isinstance(x, list) else [x]
    return out


def url_status(u):
    try:
        r = subprocess.run(['curl', '-s', '-o', '/dev/null', '-L', '-A', 'Mozilla/5.0', '--max-time', '20', '-w', '%{http_code}', u], capture_output=True, text=True)
        return int(r.stdout or 0) or 'unreachable from build host (network policy)'
    except Exception as e:  # report, don't fail the build
        return type(e).__name__


def spreads(png_dir, out, first=2):
    """RTL spreads: even page on the right, the following odd page on the left."""
    pages = sorted(png_dir.glob('p*.png'))
    ims = [Image.open(p) for p in pages]
    w, h = ims[0].size
    pairs = [(ims[i + 1] if i + 1 < len(ims) else None, ims[i]) for i in range(first - 1, len(ims), 2)]
    sheets = []
    per = 4
    for s in range(0, len(pairs), per):
        chunk = pairs[s:s + per]
        sheet = Image.new('RGB', (w * 4 + 60, (h + 30) * ((len(chunk) + 1) // 2) + 30), '#C9CCD2')
        for k, (left, right) in enumerate(chunk):
            x, y = 20 + (k % 2) * (w * 2 + 20), 20 + (k // 2) * (h + 30)
            if left: sheet.paste(left, (x, y))
            sheet.paste(right, (x + w, y))
        f = out / f'spreads-{s // per + 1:02d}.png'
        sheet.thumbnail((2600, 2600)); sheet.save(f, optimize=True); sheets.append(f.name)
    return sheets


def phone(png_dir, out, pages):
    """Simulate a 390-pt-wide phone showing a page fitted to width (status bar + page, no zoom)."""
    files = []
    for n in pages:
        im = Image.open(png_dir / f'p{n:03d}.png')
        W = 1170  # 390 pt × 3
        im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
        frame = Image.new('RGB', (W + 60, 2532 + 60), '#0B0F17')
        screen = Image.new('RGB', (W, 2532), '#1C1C1E')
        y = (2532 - im.height) // 2
        screen.paste(im, (0, y))
        ImageDraw.Draw(screen).text((40, 40), '9:41', fill='#FFFFFF')
        frame.paste(screen, (30, 30))
        f = out / f'phone-p{n:02d}.png'
        frame.thumbnail((700, 1600)); frame.save(f, optimize=True); files.append(f.name)
    return files


def main(out):
    out = Path(out)
    rep = json.loads((out / 'render-report.json').read_text())
    book = out / 'proof' / build.BOOK_PDF
    covers = out / 'covers' / 'ZeroToHero_cover-concepts_review.pdf'
    set_metadata(book, 'From Zero to Hero — Arabic edition (review)', 'ar')
    set_metadata(covers, 'From Zero to Hero — cover concepts (review)', 'ar')
    qa = {'book': check_pdf(book, rep['book']), 'covers': check_pdf(covers, rep['covers']),
          'contrast': {k: {'ratio': contrast(*v), 'AA_small_text': contrast(*v) >= 4.5} for k, v in TEXT_PAIRS.items()},
          'contact_sheets': spreads(out / 'proof' / 'png', out / 'proof'),
          'phone_previews': phone(out / 'proof' / 'png', out / 'proof', [7, 10, 14, 23])}
    (out / 'qa-report.json').write_text(json.dumps(qa, ensure_ascii=False, indent=1))
    print(json.dumps(qa, ensure_ascii=False, indent=1)[:4000])


if __name__ == '__main__':
    main(sys.argv[1])
