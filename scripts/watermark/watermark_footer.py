"""Version 2 (recommended): a small footer line with the buyer's details on every page.

=== الإعدادات: غيّر هذه الأسطر الستة فقط ===
"""
INPUT_PDF = "ZeroToHero_AR.pdf"           # ملف الكتاب الأصلي (لا يتغيّر)
OUTPUT_PDF = "ZeroToHero_AR_licensed.pdf"  # الملف الجديد الذي ترسله للمشتري
BUYER_NAME = "اسم المشتري"
BUYER_EMAIL = "buyer@example.com"
ORDER_REF = "A1B2C3D4"                    # رقم الطلب (اختياري، اتركه "" إن لم يوجد)
BOOK_LANGUAGE = "ar"                      # لغة الكتاب: "ar" أو "en" أو "ru"
# ================================================

import html, re, sys
from pathlib import Path
import pymupdf                      # pip install PyMuPDF
from fontTools.ttLib import TTFont  # pip install fonttools

HERE = Path(__file__).resolve().parent
# Fonts: a "fonts" folder next to this script, or the store's copy inside the repository.
FONTS = next(p for p in (HERE / "fonts", HERE.parent.parent / "store_service" / "orders" / "fonts") if p.exists())
ARABIC = re.compile("[؀-ۿݐ-ݿࢠ-ࣿ]")
LICENSED = {"ar": "مرخّصة لـ:", "en": "Licensed to:", "ru": "Лицензия для:"}
CSS = ("@font-face{font-family:plex;src:url(IBMPlexSans-Regular.ttf)}"
       "@font-face{font-family:plexar;src:url(IBMPlexSansArabic-Regular.ttf)}"
       "*{font-family:plex;margin:0;padding:0}.ar{font-family:plexar}")


def run(text):
    """One piece of text, in the Arabic font when it contains Arabic letters."""
    cls = ' class="ar"' if ARABIC.search(text) else ""
    return f"<bdi{cls}>{html.escape(text)}</bdi>"


def arabic_tounicode():
    """Text map for every glyph of the Arabic font, so copied Arabic stays real Arabic letters.

    PyMuPDF only maps the font's basic letters; the joined forms it draws (initial, medial, final,
    lam-alef) get the text of the letters they replace.
    """
    f = TTFont(FONTS / "IBMPlexSansArabic-Regular.ttf")
    gid = f.getReverseGlyphMap()
    text = {g: chr(c) for c, g in sorted(f.getBestCmap().items(), reverse=True)}
    subs = []
    for lookup in f["GSUB"].table.LookupList.Lookup:
        for st in lookup.SubTable:
            st = st.ExtSubTable if lookup.LookupType == 7 else st
            if hasattr(st, "mapping"):
                subs += [((a,), b) for a, b in st.mapping.items()]
            if hasattr(st, "ligatures"):
                subs += [((first, *lg.Component), lg.LigGlyph) for first, ligs in st.ligatures.items() for lg in ligs]
    changed = True
    while changed:
        changed = False
        for parts, out in subs:
            if out not in text and all(p in text for p in parts):
                text[out] = "".join(text[p] for p in parts)
                changed = True
    rows = ["<%04x> <%s>" % (gid[g], "".join("%04x" % ord(ch) for ch in u)) for g, u in text.items() if g in gid]
    body = "".join("%d beginbfchar\n%s\nendbfchar\n" % (len(rows[i:i + 100]), "\n".join(rows[i:i + 100]))
                   for i in range(0, len(rows), 100))
    return ("/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n"
            "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n"
            "/CMapName /Adobe-Identity-UCS def\n/CMapType 2 def\n1 begincodespacerange\n<0000> <FFFF>\n"
            "endcodespacerange\n" + body + "endcmap\nCMapName currentdict /CMap defineresource pop\nend\nend\n").encode()


def main():
    doc = pymupdf.open(INPUT_PDF)
    archive = pymupdf.Archive(str(FONTS))
    rtl = BOOK_LANGUAGE == "ar"
    label = LICENSED[BOOK_LANGUAGE]
    parts = ["© Ali Alkhuzaee · alialkhuzaee.com", "—", label, BUYER_NAME, "·", BUYER_EMAIL] + (["·", ORDER_REF] if ORDER_REF else [])
    line = " ".join(run(p) for p in parts)
    style = "direction:rtl;text-align:right" if rtl else "text-align:left"

    # The footer is laid out once on a blank page of the same size, then placed on every page.
    # The book's own text and fonts are not touched.
    marks = {}
    for page in doc:
        size = (page.rect.width, page.rect.height)
        if size not in marks:
            mark = pymupdf.open()
            w, h = size
            m = mark.new_page(width=w, height=h)
            # 8 px (6 pt), grey, in the strip under the page numbers: 47 pt side margins, 6 pt from the bottom.
            m.insert_htmlbox(pymupdf.Rect(47, h - 20, w - 47, h - 6),
                             f'<div style="{style}"><span style="font-size:6pt;color:#6b7380">{line}</span></div>',
                             css=CSS, archive=archive, opacity=0.85, scale_low=0)
            marks[size] = mark
        page.show_pdf_page(page.rect, marks[size], 0)

    # Hidden copy of the buyer's details in the file's properties.
    meta = doc.metadata or {}
    meta["subject"] = f"Licensed to {BUYER_NAME} <{BUYER_EMAIL}> {ORDER_REF}".strip()
    doc.set_metadata(meta)

    for x in range(1, doc.xref_length()):
        if doc.xref_get_key(x, "BaseFont")[1].replace("#20", " ") == "/IBM Plex Sans Arabic Regular":
            kind, ref = doc.xref_get_key(x, "ToUnicode")
            if kind == "xref":
                doc.update_stream(int(ref.split()[0]), arabic_tounicode())

    doc.save(OUTPUT_PDF, garbage=1, deflate=True)
    print("Done:", OUTPUT_PDF, f"({doc.page_count} pages)")


if __name__ == "__main__":
    if not Path(INPUT_PDF).exists():
        sys.exit(f"File not found: {INPUT_PDF}  (put the PDF in the same folder, or write its full path)")
    main()
