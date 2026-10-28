"""Build From Zero to Hero: cover concepts and the full book in Arabic, English or Russian.

python scripts/zero_to_hero/build.py PAGES_DIR OUT_DIR [ar|en|ru]

PAGES_DIR holds the manuscript pages (*.html). The repository is public, so the paid manuscript lives in the
private project folder (/mnt/project-files/creator-guide-private/zero-to-hero/pages), not in this repo.

PAGES_DIR holds one language; the English and Russian manuscripts are translations of the Arabic master.
Writes (nothing here touches the live product):
  OUT_DIR/covers/covers-concepts.pdf + PNGs of every cover (A/B/C × ar/en/ru) and the back cover
  OUT_DIR/proof/ZeroToHero_<LANG>.pdf + p###.png per page, and ZeroToHero_<LANG>_prompts.md (copyable prompts)
  OUT_DIR/diagrams/*.svg (editable vector sources)
Each <section class="pg"> in a page file becomes one B5 page.
`{{fig:name}}` inserts a diagram from diagrams.py; `{{page:id}}` the page number of the section with that data-id. Rendering uses Chromium through Playwright for Node,
and fonts load from Google Fonts (network required).
"""
import json, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pdf_fonts, diagrams, covers

# Every face is inlined as a static, cleaned font (pdf_fonts.py) so text copied from the PDF reads correctly.
FONTS = ('https://fonts.googleapis.com/css2?family=Alexandria:wght@400;500;600;700;800'
         '&family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500'
         '&family=Manrope:wght@400;500;600;700;800&family=Geologica:wght@400;600;700'
         '&family=Noto+Sans+Math&family=Noto+Sans+Symbols+2&display=swap')
BOOK = 'FROM ZERO TO HERO'
LANG = 'ar'
TITLES = {'ar': 'From Zero to Hero — Arabic edition', 'en': 'From Zero to Hero — English edition', 'ru': 'From Zero to Hero — Russian edition'}
PROMPTS_TITLE = {'ar': 'قوالب البرومبت', 'en': 'Prompt templates', 'ru': 'Шаблоны промптов'}
# English and Russian: Latin/Cyrillic faces of the same identity, mirrored binding and left-aligned blocks.
LTR_CSS = """
html[dir=ltr]{--ar:"IBM Plex Sans","Noto Sans Math","Noto Sans Symbols 2",sans-serif;--ar-display:Geologica,"IBM Plex Sans","Noto Sans Math","Noto Sans Symbols 2",sans-serif}
html[dir=ltr] body{font-size:9.7pt;line-height:1.5}
html[dir=ltr] .lead{font-size:10.8pt;line-height:1.5}
html[dir=ltr] .small,html[dir=ltr] figcaption,html[dir=ltr] .hook,html[dir=ltr] .legend div{font-size:8.7pt;line-height:1.42}
html[dir=ltr] .callout{font-size:9.2pt;line-height:1.46}
html[dir=ltr] table.data{font-size:8.6pt;line-height:1.34}
html[dir=ltr] table.data td{padding:1.3mm 1.8mm}
html[dir=ltr] ul.check{font-size:9.1pt}
html[dir=ltr] ul.check.cols{row-gap:0}
html[dir=ltr] h2{font-size:15.5pt;line-height:1.25}
html[dir=ltr] h3{font-size:11.6pt}
html[dir=ltr] .prompt pre{line-height:1.5}
html[dir=ltr] .prompt.sm pre{font-size:8.3pt;line-height:1.42}
html[dir=ltr] .prompt.sm .pv{line-height:1.35}
html[dir=ltr] .prompt pre{direction:ltr;text-align:left}
html[dir=ltr] .opener .unit,html[dir=ltr] .opener .bignum{text-align:left}
html[dir=ltr] .opener .art{transform:scaleX(-1)}
html[dir=ltr] .page.odd .folio{flex-direction:row}
html[dir=ltr] .page.even .folio{flex-direction:row-reverse}
html[lang=en] .hook q{quotes:"“" "”"}
html[dir=ltr] .hook q{font-size:9.8pt;line-height:1.4}
"""


def book_pdf(lang=None):
    return f'ZeroToHero_{(lang or LANG).upper()}.pdf'


def head(title, extra_css='', lang='ar'):
    css = (HERE / 'design.css').read_text() + covers.CSS + extra_css + ('' if lang == 'ar' else LTR_CSS)
    return (f'<!doctype html><html lang="{lang}" dir="{'rtl' if lang == 'ar' else 'ltr'}"><head><meta charset="utf-8"><title>{title}</title>'
            f'<meta name="author" content="Ali Alkhuzaee"><meta name="description" content="{title}"><style>{pdf_fonts.css(FONTS)}</style><style>{css}</style></head><body>')


def fill(html):
    return re.sub(r'\{\{fig:(\w+)\}\}', lambda m: diagrams.render(m.group(1), LANG), html)


PAGES = HERE / 'pages'


def sections():
    for f in sorted(PAGES.glob('*.html')):
        src = re.sub(r'<!--.*?-->', '', f.read_text(), flags=re.S)
        for m in re.finditer(r'<section class="pg"([^>]*)>(.*?)</section>', src, re.S):
            attrs = dict(re.findall(r'data-(\w+)="([^"]*)"', m.group(1)))
            yield attrs, m.group(2)


def book_html():
    rtl = LANG == 'ar'
    secs = list(sections())
    # Page numbers for {{page:id}} references (the table of contents): the cover is page 1.
    nums = {a['id']: n for n, (a, _) in enumerate(secs, 2) if 'id' in a}
    page_ref = lambda html: re.sub(r'\{\{page:([\w-]+)\}\}', lambda m: str(nums[m.group(1)]), html)
    pages = [covers.cover('A', LANG)]
    for n, (attrs, body) in enumerate(secs, 2):
        body = page_ref(body)
        # 'odd'/'even' name the page geometry of the Arabic book: 'even' is a right-hand page. In a left-to-right
        # book the odd pages are the right-hand ones.
        side = 'odd' if (n % 2 == 1) == rtl else 'even'
        anchor = f' id="{attrs["id"]}"' if 'id' in attrs else ''
        if attrs.get('kind') == 'dark':
            pages.append(f'<div class="page dark {side}"{anchor}>{fill(body)}<div class="folio">{n}</div></div>')
            continue
        run = attrs.get('run', '')
        # The running head sits on the outer edge of the page.
        rh = f'<div class="runhead"><span>{run}</span><span class="mark">{BOOK}</span></div>' if (side == 'even') == rtl else \
             f'<div class="runhead"><span class="mark">{BOOK}</span><span>{run}</span></div>'
        if attrs.get('kind') == 'plain':
            rh = ''
        # data-fit="0.94" scales one page's content down slightly, for translations that run longer than the Arabic.
        fit = f' data-fit style="--fit:{attrs["fit"]}"' if 'fit' in attrs else ''
        pages.append(f'<div class="page {side}"{anchor}>{rh}<div class="frame"{fit}>{fill(body)}</div><div class="folio">{n}</div></div>')
    pages.append(covers.back_cover(LANG))
    return head(TITLES[LANG], lang=LANG) + ''.join(pages) + '</body></html>'


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


def main(pages, out, lang='ar'):
    global PAGES, LANG
    PAGES, out, LANG = Path(pages), Path(out), lang
    (out / 'diagrams').mkdir(parents=True, exist_ok=True)
    for k, f in diagrams.ALL.items():
        (out / 'diagrams' / f'{k}.svg').write_text(diagrams.render(k, LANG))
    rep = {'covers': render(covers_html(), out / 'covers' / 'ZeroToHero_cover-concepts_review.pdf', out / 'covers' / 'png', '1'),
           'book': render(book_html(), out / 'proof' / book_pdf(), out / 'proof' / 'png', '1.5')}
    # Copyable companion: PDF text extraction can reverse lam-alef pairs, so prompts also ship as plain UTF-8 text.
    prompts = []
    for attrs, body in sections():
        for m in re.finditer(r'<div class="bar"><span>(.*?)</span><span class="id">(.*?)</span>.*?<pre>(.*?)</pre>', body, re.S):
            prompts.append(f'## {m.group(2)} · {m.group(1)}\n\n' + re.sub(r'<[^>]+>', '', m.group(3)).strip() + '\n')
    (out / 'proof' / f'ZeroToHero_{LANG.upper()}_prompts.md').write_text(f'# From Zero to Hero · {PROMPTS_TITLE[LANG]}\n\n' + '\n'.join(prompts))
    (out / 'render-report.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    print(json.dumps({k: {'pages': v['pages'], 'overflow': len(v['overflow'])} for k, v in rep.items()}))


if __name__ == '__main__':
    main(*sys.argv[1:4])
