#!/usr/bin/env python3
"""Build the website CSS (assets/v3/) in the From Zero to Hero book identity.

The v2 stylesheets stay untouched so the live site keeps working; v3 is generated from them:
  1. assets/brand/tokens.css (book palette, type, radii) goes first in site.css,
  2. every v2 token is re-pointed at a book token,
  3. every literal v2 colour is mapped to its book equivalent (unknown colours fail the build),
  4. assets/brand/book.css (editorial motifs and component overrides) is appended.
The script also checks that the book's own design.css still carries the token values, so the site and the
book cannot drift apart silently.

Usage: python scripts/build_brand_css.py
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = {
    'site.css': ROOT / 'assets/v2/site.css',
    'guide.css': ROOT / 'assets/v2/guide.css',
    'deck.css': ROOT / 'assets/v2/deck.css',
    'store.css': ROOT / 'assets/products/store.css',
}
OUT = ROOT / 'assets/v3'
TOKENS = ROOT / 'assets/brand/tokens.css'
BOOK = ROOT / 'assets/brand/book.css'
BOOK_DESIGN = ROOT / 'scripts/zero_to_hero/design.css'

# v2 token -> book token
TOKEN_MAP = {
    '--night': 'var(--b-ink)', '--navy': 'var(--b-navy)', '--deep': 'var(--b-navy-2)', '--glass': 'rgba(22,38,62,.62)',
    '--electric': 'var(--b-copper)', '--electric-2': 'var(--b-copper-ink)', '--cyan': 'var(--b-copper)',
    '--violet': 'var(--b-cyan)', '--ink': 'var(--b-ivory)', '--ink-2': 'var(--b-haze)', '--ink-3': 'var(--b-mist)',
    '--line': 'rgba(248,247,243,.13)', '--line-2': 'rgba(227,168,107,.34)', '--paper': 'var(--b-ivory)',
    '--paper-card': 'var(--b-white)', '--paper-ink': 'var(--b-ink)', '--paper-2': 'var(--b-slate)',
    '--paper-line': 'var(--b-rule)', '--rec': '#E0675C',
    '--f-display': 'var(--b-f-lat)', '--f-body': 'var(--b-f-lat)', '--f-mono': 'var(--b-f-mono)',
    '--r-s': 'var(--b-r-s)', '--r-m': 'var(--b-r-m)', '--r-l': 'var(--b-r-l)',
}

# literal colour -> book colour (rgb triplets keep their alpha)
RGB_MAP = {
    (5, 10, 23): (12, 19, 32), (6, 11, 24): (16, 24, 39), (10, 20, 48): (22, 38, 62), (12, 22, 48): (16, 24, 39),
    (17, 33, 75): (30, 45, 73), (22, 48, 111): (36, 55, 90), (16, 30, 66): (22, 38, 62),
    (53, 99, 245): (227, 168, 107), (61, 107, 255): (227, 168, 107), (86, 217, 255): (227, 168, 107),
    (141, 128, 255): (37, 197, 217), (150, 178, 255): (248, 247, 243), (238, 243, 255): (248, 247, 243),
    (255, 93, 108): (224, 103, 92), (255, 139, 150): (236, 140, 130),
    (255, 255, 255): (255, 255, 255), (0, 0, 0): (0, 0, 0),
}
HEX_MAP = {
    '#050a17': '#0c1320', '#070d1f': '#111a2b', '#060c1d': '#0f1726', '#060b18': '#101827', '#071027': '#13203a',
    '#0a1430': '#16263e', '#0c1630': '#101827', '#11214b': '#1e2d49', '#16306f': '#24375a', '#0f1f49': '#1a2a45',
    '#0d1a36': '#142236', '#0b1636': '#152540', '#0b1530': '#142338', '#1b2c63': '#24375a',
    '#3563f5': '#e3a86b', '#2f56e0': '#d4975a', '#1d3fb8': '#b97d44', '#3a3fd0': '#8a4f1c',
    '#56d9ff': '#e3a86b', '#56d9ff55': '#e3a86b55', '#c9f3ff': '#f3dcc2', '#8d80ff': '#25c5d9',
    '#eef3ff': '#f8f7f3', '#b3c0dc': '#d5dce6', '#8593b5': '#9fb0c6', '#d3dcf2': '#d5dce6', '#dde6ff': '#e8ebef',
    '#c9d4ee': '#c9ced6', '#b9c5dc': '#c9ced6', '#f2f4f9': '#f8f7f3', '#d8deea': '#d8dbe0', '#4a5774': '#526174',
    '#ff5d6c': '#e0675c', '#ff8b96': '#ec8c82', '#fff': '#fff', '#000': '#000',
}
BOOK_VALUES = {'--ink': '#101827', '--navy': '#16263E', '--cyan': '#25C5D9', '--copper': '#E3A86B',
               '--ivory': '#F8F7F3', '--slate': '#526174', '--warn': '#B54C43', '--cyan-ink': '#0B6E7C',
               '--copper-ink': '#8A4F1C', '--mist': '#9FB0C6'}


def check_book():
    css = BOOK_DESIGN.read_text()
    tokens = TOKENS.read_text()
    bad = []
    for name, value in BOOK_VALUES.items():
        if not re.search(re.escape(name) + r':' + re.escape(value) + r'[;}]', css, re.I):
            bad.append(f'design.css {name} != {value}')
        if not re.search(r'--b-' + re.escape(name[2:]) + r':' + re.escape(value) + r'[;}]', tokens, re.I):
            bad.append(f'tokens.css --b-{name[2:]} != {value}')
    if bad:
        sys.exit('book/site token drift:\n  ' + '\n  '.join(bad))


def remap_colours(css, name):
    unknown = set()

    def rgb(m):
        key = tuple(int(x) for x in m.group(2).replace(' ', '').split(','))
        if key not in RGB_MAP:
            unknown.add(m.group(0))
            return m.group(0)
        return f'{m.group(1)}({",".join(map(str, RGB_MAP[key]))}{m.group(3)})'

    css = re.sub(r'(rgba?)\((\d+\s*,\s*\d+\s*,\s*\d+)([^)]*)\)', rgb, css)

    def hexc(m):
        h = m.group(0).lower()
        if h not in HEX_MAP:
            unknown.add(h)
            return h
        return HEX_MAP[h]

    css = re.sub(r'#[0-9a-fA-F]{3,8}\b', hexc, css)
    if unknown:
        sys.exit(f'{name}: unmapped colours {sorted(unknown)}')
    return css


def remap_root(css):
    def root(m):
        body = m.group(1)
        for tok, val in TOKEN_MAP.items():
            body, n = re.subn(re.escape(tok) + r':[^;]*;', f'{tok}:{val};', body, count=1)
            if not n:
                sys.exit(f'site.css :root has no {tok}')
        return ':root{' + body + '}'

    css, n = re.subn(r':root\{(.*?)\}', root, css, count=1, flags=re.S)
    if not n:
        sys.exit('site.css has no :root')
    # Arabic keeps the book's Alexandria/Plex pairing; Russian uses Geologica like the book's RU edition.
    css = css.replace('html[lang=ar]{--f-display:"Alexandria","IBM Plex Sans Arabic",system-ui,sans-serif;'
                      '--f-body:"IBM Plex Sans Arabic",system-ui,sans-serif}',
                      'html[lang=ar]{--f-display:var(--b-f-ar-display);--f-body:var(--b-f-ar)}\n'
                      'html[lang=ru]{--f-display:var(--b-f-ru)}')
    return css


def main():
    check_book()
    OUT.mkdir(exist_ok=True)
    head = '/* GENERATED by scripts/build_brand_css.py from {src}. Edit the source, tokens.css or book.css, then rebuild. */\n'
    for name, src in SRC.items():
        css = src.read_text()
        css = remap_colours(css, name)
        if name == 'site.css':
            css = remap_root(css)
        if name == 'site.css':
            css = TOKENS.read_text() + '\n' + css + '\n' + BOOK.read_text()
        (OUT / name).write_text(head.format(src=src.relative_to(ROOT)) + css)
        print('wrote', (OUT / name).relative_to(ROOT), len(css))


if __name__ == '__main__':
    main()
