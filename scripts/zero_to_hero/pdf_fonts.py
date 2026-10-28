"""Web fonts prepared for a PDF whose text copies and extracts correctly.

Variable fonts (IBM Plex Sans, Manrope, Geologica) are pinned to each @font-face weight: Chromium embeds a
variable font as a Type 3 font, which many readers extract as garbage (Russian came out as "Íîñ óâå...").

Chromium writes each glyph's text from the font's cmap. IBM Plex Sans Arabic and Alexandria map their ligature
glyphs to Arabic presentation forms (U+FB50-FDFF, U+FE70-FEFF), so copied or extracted text came out as
"يف" for "في" and "الكامريا" for "الكاميرا". This drops those cmap entries and every ligature except the
mandatory lam-alef. Shapes are unchanged; a few optional ligatures (فى، بر، تى) are drawn as their two letters.
Some extractors (poppler/pdftotext) still reverse lam-alef ("اإل"); that is the reader's limitation.

css(url) returns the Google Fonts stylesheet with every font inlined as a static, cleaned woff2 data URI (cached).
"""
import base64, hashlib, io, re, sys, urllib.request
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
def is_pres(c): return 0xFB50 <= c <= 0xFDFF or 0xFE70 <= c <= 0xFEFF
def lam_glyphs(f):
    best = f.getBestCmap(); lam = {best.get(c) for c in (0x0644, 0xFEDD, 0xFEDE, 0xFEDF, 0xFEE0)} - {None}
    lam |= {g for g in f.getGlyphOrder() if 'lam' in g.lower() or g.startswith('uni0644')}
    alef = {best.get(c) for c in (0x0622, 0x0623, 0x0625, 0x0627, 0x0671, 0xFE81, 0xFE82, 0xFE83, 0xFE84, 0xFE87, 0xFE88, 0xFE8D, 0xFE8E)} - {None}
    alef |= {g for g in f.getGlyphOrder() if 'alef' in g.lower() and 'maksura' not in g.lower()}
    return lam, alef
def clean(data, weight=None):
    f = TTFont(io.BytesIO(data))
    if 'fvar' in f:
        axes = {a.axisTag: (weight if a.axisTag == 'wght' and weight else a.defaultValue) for a in f['fvar'].axes}
        f = instancer.instantiateVariableFont(f, axes)
    lam, alef = lam_glyphs(f)
    if 'GSUB' in f:
        feats = f['GSUB'].table.FeatureList.FeatureRecord
        rlig = {i for fr in feats if fr.FeatureTag in ('rlig', 'liga', 'dlig', 'clig') for i in fr.Feature.LookupListIndex}
        for i in rlig:
            l = f['GSUB'].table.LookupList.Lookup[i]
            for st in l.SubTable:
                s = st.ExtSubTable if l.LookupType == 7 else st
                if getattr(s, 'LookupType', 4) == 4 and hasattr(s, 'ligatures'):
                    s.ligatures = {k: kept for k, v in s.ligatures.items() if k in lam
                                    for kept in [[lg for lg in v if lg.Component and lg.Component[0] in alef]] if kept}
    for t in f['cmap'].tables:
        for c in [c for c in t.cmap if is_pres(c)]: del t.cmap[c]
    out = io.BytesIO(); f.flavor = 'woff2'; f.save(out); return out.getvalue()
CACHE = Path.home() / '.cache' / 'zero_to_hero_fonts'


def css(url):
    cached = CACHE / (hashlib.sha256(url.encode()).hexdigest()[:16] + '.css')
    if cached.exists():
        return cached.read_text()
    out = clean_css(url); CACHE.mkdir(parents=True, exist_ok=True); cached.write_text(out)
    return out


def clean_css(url):
    def face(m):
        block = m.group(0); w = re.search(r'font-weight:\s*(\d+)', block)
        return re.sub(r'url\((https://fonts\.gstatic\.com/[^)]+)\)', lambda u: 'url(data:font/woff2;base64,' + base64.b64encode(
            clean(get(u.group(1)), int(w.group(1)) if w else None)).decode() + ')', block)
    return re.sub(r'@font-face\s*\{[^}]*\}', face, get(url).decode())


if __name__ == '__main__':
    sys.stdout.write(css(sys.argv[1]))
