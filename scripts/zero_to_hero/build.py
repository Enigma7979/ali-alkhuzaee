"""Build From Zero to Hero review proofs: cover concepts and the full Arabic edition.

python scripts/zero_to_hero/build.py PAGES_DIR OUT_DIR

PAGES_DIR holds the manuscript pages (*.html). The repository is public, so the paid manuscript lives in the
private project folder (/mnt/project-files/creator-guide-private/zero-to-hero/pages), not in this repo.

Writes (all labelled as review proofs; nothing here touches the live product):
  OUT_DIR/covers/covers-concepts.pdf + PNGs of every cover (A/B/C × ar/en/ru) and the back cover
  OUT_DIR/proof/ZeroToHero_AR_full_review.pdf + p##.png per page, and ZeroToHero_AR_prompts.md (copyable prompts)
  OUT_DIR/diagrams/*.svg (editable vector sources)
Each <section class="pg"> in a page file becomes one B5 page.
`{{fig:name}}` inserts a diagram from diagrams.py; `{{page:id}}` the page number of the section with that data-id. Rendering uses Chromium through Playwright for Node,
and fonts load from Google Fonts (network required).
"""
import json, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diagrams, covers

FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Alexandria:wght@400;500;600;700;800'
         '&family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500'
         '&family=Manrope:wght@400;500;600;700;800&family=Geologica:wght@400;600;700'
         '&family=Noto+Sans+Math&family=Noto+Sans+Symbols+2&display=swap" rel="stylesheet">')
BOOK = 'FROM ZERO TO HERO'
# Printed on every text page until Ali approves the edition for sale.
PROOFMARK = 'نسخة مراجعة · قبل الاعتماد'
BOOK_PDF = 'ZeroToHero_AR_full_review.pdf'


def head(title, extra_css=''):
    css = (HERE / 'design.css').read_text() + covers.CSS + extra_css
    return (f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>{title}</title>'
            f'<meta name="author" content="Ali Alkhuzaee"><meta name="description" content="{title}">{FONTS}<style>{css}</style></head><body>')


def fill(html):
    return re.sub(r'\{\{fig:(\w+)\}\}', lambda m: diagrams.ALL[m.group(1)](), html)


PAGES = HERE / 'pages'


def sections():
    for f in sorted(PAGES.glob('*.html')):
        src = re.sub(r'<!--.*?-->', '', f.read_text(), flags=re.S)
        for m in re.finditer(r'<section class="pg"([^>]*)>(.*?)</section>', src, re.S):
            attrs = dict(re.findall(r'data-(\w+)="([^"]*)"', m.group(1)))
            yield attrs, m.group(2)


def book_html(title='From Zero to Hero — Arabic edition (review)'):
    secs = list(sections())
    # Page numbers for {{page:id}} references (the table of contents): the cover is page 1.
    nums = {a['id']: n for n, (a, _) in enumerate(secs, 2) if 'id' in a}
    page_ref = lambda html: re.sub(r'\{\{page:([\w-]+)\}\}', lambda m: str(nums[m.group(1)]), html)
    pages = [covers.cover('A', 'ar')]
    for n, (attrs, body) in enumerate(secs, 2):
        body = page_ref(body)
        side = 'odd' if n % 2 else 'even'
        anchor = f' id="{attrs["id"]}"' if 'id' in attrs else ''
        if attrs.get('kind') == 'dark':
            pages.append(f'<div class="page dark {side}"{anchor}>{fill(body)}<div class="folio">{n}</div></div>')
            continue
        run = attrs.get('run', '')
        rh = f'<div class="runhead"><span>{run}</span><span class="mark">{BOOK}</span></div>' if side == 'even' else \
             f'<div class="runhead"><span class="mark">{BOOK}</span><span>{run}</span></div>'
        if attrs.get('kind') == 'plain':
            rh = ''
        pages.append(f'<div class="page {side}"{anchor}>{rh}<div class="frame">{fill(body)}</div>'
                     f'<div class="proofmark">{PROOFMARK}</div><div class="folio">{n}</div></div>')
    pages.append(covers.back_cover())
    return head(title) + ''.join(pages) + '</body></html>'


def covers_html():
    pages = [covers.cover(c, l) for c in 'ABC' for l in ('ar', 'en', 'ru')] + [covers.back_cover()]
    return head('From Zero to Hero — cover concepts (review)') + ''.join(pages) + '</body></html>'


def render(html, pdf, png_dir, scale='1.5'):
    png_dir.mkdir(parents=True, exist_ok=True)
    src = png_dir.parent / (pdf.stem + '.html')
    src.write_text(html)
    r = subprocess.run(['node', str(HERE / 'render.mjs'), str(src), str(pdf), str(png_dir), scale], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)
    return json.loads(r.stdout.strip().splitlines()[-1])


def main(pages, out):
    global PAGES
    PAGES, out = Path(pages), Path(out)
    (out / 'diagrams').mkdir(parents=True, exist_ok=True)
    for k, f in diagrams.ALL.items():
        (out / 'diagrams' / f'{k}.svg').write_text(f())
    rep = {'covers': render(covers_html(), out / 'covers' / 'ZeroToHero_cover-concepts_review.pdf', out / 'covers' / 'png', '1'),
           'book': render(book_html(), out / 'proof' / BOOK_PDF, out / 'proof' / 'png', '1.5')}
    # Copyable companion: PDF text extraction can reverse lam-alef pairs, so prompts also ship as plain UTF-8 text.
    prompts = []
    for attrs, body in sections():
        for m in re.finditer(r'<div class="bar"><span>(.*?)</span><span class="id">(.*?)</span>.*?<pre>(.*?)</pre>', body, re.S):
            prompts.append(f'## {m.group(2)} · {m.group(1)}\n\n' + re.sub(r'<[^>]+>', '', m.group(3)).strip() + '\n')
    (out / 'proof' / 'ZeroToHero_AR_prompts.md').write_text('# From Zero to Hero · قوالب البرومبت\n\n' + '\n'.join(prompts))
    (out / 'render-report.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    print(json.dumps({k: {'pages': v['pages'], 'overflow': len(v['overflow'])} for k, v in rep.items()}))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
