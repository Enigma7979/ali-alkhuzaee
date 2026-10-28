"""Plain-text (Markdown) edition of a built book, taken from the build HTML instead of the PDF.

python scripts/zero_to_hero/text_edition.py OUT_DIR [ar|en|ru]   (after build.py)
  -> OUT_DIR/proof/ZeroToHero_{LANG}_text.md

Text pulled out of a PDF depends on the reader (some reverse Arabic lam-alef), so proofreading and
copying work from this file. Diagrams become their captions; running heads, folios and covers are dropped.
"""
import html
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import markdownify

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402


def page_md(page):
    for el in page.select('svg, style, script, .runhead, .folio, .art, .bignum, .dots, .spacer, .sw'):
        el.decompose()
    for pre in page.select('pre'):  # keep prompt text verbatim as a fenced block
        pre.replace_with(BeautifulSoup(f'<p>```</p><p>{"<br>".join(html.escape(l) for l in pre.get_text().splitlines())}</p><p>```</p>', 'html.parser'))
    src = re.sub(r'</(span|div|figcaption)>', r'</\1> ', str(page))  # stripped wrappers would glue words together
    src = re.sub(r'</(b|strong)>(?=\w)', r'</\1> ', src)
    src = src.replace('<span class="why">', '<br><span class="why">')
    md = markdownify(src, heading_style='ATX', bullets='-', strip=['a', 'span', 'div', 'figure', 'section'])
    md = re.sub(r'[ \t]+\n', '\n', md)
    return re.sub(r'\n{3,}', '\n\n', md).strip()


def main(out, lang='ar'):
    out = Path(out) / 'proof'
    soup = BeautifulSoup((out / build.book_pdf(lang).replace('.pdf', '.html')).read_text(encoding='utf-8'), 'html.parser')
    parts = [f'# {build.TITLES[lang]}']
    for n, page in enumerate(soup.select('div.page'), 1):
        if 'cover' in page.get('class', []):
            continue
        body = page_md(page)
        if body:
            parts.append(f'<!-- page {n} -->\n\n{body}')
    dst = out / build.book_pdf(lang).replace('.pdf', '_text.md')
    dst.write_text('\n\n'.join(parts) + '\n', encoding='utf-8')
    print('wrote', dst, dst.stat().st_size // 1024, 'KB')


if __name__ == '__main__':
    main(*sys.argv[1:3])
