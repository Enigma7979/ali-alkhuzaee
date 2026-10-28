"""Per-buyer stamping of the delivered PDF with PyMuPDF.

The book's own fonts and text layer are never rewritten: the stamp is added as new content on top of
each page, with its own embedded IBM Plex fonts (SIL OFL, see fonts/). The Arabic font is the cleaned
build from scripts/zero_to_hero/pdf_fonts.py (no presentation-form cmap entries), so the stamped Arabic
copies and extracts as normal Arabic letters.
"""
import html,re
from datetime import date
from functools import cache
from pathlib import Path
import pymupdf
from fontTools.ttLib import TTFont

FONTS=Path(__file__).resolve().parent/'fonts'
ARCHIVE=pymupdf.Archive(str(FONTS))
CSS=('@font-face{font-family:plex;src:url(IBMPlexSans-Regular.ttf)}'
 '@font-face{font-family:plexar;src:url(IBMPlexSansArabic-Regular.ttf)}'
 '*{font-family:plex;margin:0;padding:0}.ar{font-family:plexar}')
ARABIC=re.compile('[؀-ۿݐ-ݿࢠ-ࣿ]')
OWNER={'en':'© Ali Alkhuzaee · Study UA Plus · alialkhuzaee.com','ar':'© علي الخزاعي · Study UA Plus · alialkhuzaee.com','ru':'© Али Альхузаи · Study UA Plus · alialkhuzaee.com'}
LICENSED={'en':'Licensed to','ar':'مرخّصة لـ','ru':'Лицензия для'}
ORDER={'en':'Order','ar':'الطلب','ru':'Заказ'}
# Personal licence block for the empty top half of page 2 (the copyright page).
LICENCE={
 'en':('LICENCE FOR THIS COPY','This PDF copy was sold to the person named above for their personal use only. You may keep it on your own devices and print it for yourself. You may not share, forward, upload, resell or publish the book or any part of it. The prompts and checklists may be used in your own work. Each copy carries its buyer\'s details, so a shared copy can be traced to its order.'),
 'ar':('ترخيص هذه النسخة','بيعت نسخة PDF هذه للشخص المذكور أعلاه لاستخدامه الشخصي فقط. يمكنك حفظها على أجهزتك وطباعتها لنفسك. لا يُسمح بمشاركة الكتاب أو أي جزء منه أو إرساله أو رفعه أو إعادة بيعه أو نشره. يمكنك استخدام البرومبتات وقوائم الفحص في عملك. تحمل كل نسخة بيانات مشتريها، لذلك يمكن تتبّع أي نسخة منشورة إلى طلبها.'),
 'ru':('ЛИЦЕНЗИЯ НА ЭТОТ ЭКЗЕМПЛЯР','Этот экземпляр PDF продан указанному выше лицу только для личного использования. Вы можете хранить его на своих устройствах и распечатать для себя. Запрещается передавать, пересылать, выкладывать, перепродавать или публиковать книгу или её части. Промпты и чек-листы можно использовать в своей работе. Каждый экземпляр содержит данные покупателя, поэтому распространённую копию можно связать с её заказом.'),
}

@cache
def arabic_tounicode():
 """ToUnicode CMap for every glyph of the Arabic font, joined forms and lam-alef included.

 MuPDF writes the CMap from the font's cmap only, so the positional forms it shapes (initial,
 medial, final lam and so on) would copy as garbage. Each glyph produced by a GSUB single or
 ligature substitution gets the text of the glyphs it replaced.
 """
 f=TTFont(FONTS/'IBMPlexSansArabic-Regular.ttf');gid=f.getReverseGlyphMap()
 text={g:chr(c) for c,g in sorted(f.getBestCmap().items(),reverse=True)}
 subs=[]
 for lookup in f['GSUB'].table.LookupList.Lookup:
  for st in lookup.SubTable:
   st=st.ExtSubTable if lookup.LookupType==7 else st
   if hasattr(st,'mapping'):subs+=[((a,),b) for a,b in st.mapping.items()]
   if hasattr(st,'ligatures'):subs+=[((first,*lg.Component),lg.LigGlyph) for first,ligs in st.ligatures.items() for lg in ligs]
 changed=True
 while changed:
  changed=False
  for parts,out in subs:
   if out not in text and all(p in text for p in parts):text[out]=''.join(text[p] for p in parts);changed=True
 rows=['<%04x> <%s>'%(gid[g],''.join('%04x'%ord(ch) for ch in u)) for g,u in text.items() if g in gid]
 body=''.join('%d beginbfchar\n%s\nendbfchar\n'%(len(rows[i:i+100]),'\n'.join(rows[i:i+100])) for i in range(0,len(rows),100))
 return ('/CIDInit /ProcSet findresource begin\n12 dict begin\nbegincmap\n/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def\n'
  '/CMapName /Adobe-Identity-UCS def\n/CMapType 2 def\n1 begincodespacerange\n<0000> <FFFF>\nendcodespacerange\n'+body+
  'endcmap\nCMapName currentdict /CMap defineresource pop\nend\nend\n').encode()

def fix_arabic_text(doc):
 # Only the stamp's own Arabic font (not subset, so no "ABCDEF+" prefix); the book's fonts are left alone.
 for x in range(1,doc.xref_length()):
  if doc.xref_get_key(x,'BaseFont')[1].replace('#20',' ')=='/IBM Plex Sans Arabic Regular':
   kind,ref=doc.xref_get_key(x,'ToUnicode')
   if kind=='xref':doc.update_stream(int(ref.split()[0]),arabic_tounicode())

def t(text):
 # MuPDF uses the first font of a family list for a whole run, so Arabic runs get the Arabic font explicitly.
 return '<bdi class="ar">'+html.escape(text)+'</bdi>' if ARABIC.search(text) else '<bdi>'+html.escape(text)+'</bdi>'

def _box(page,rect,body,rtl,opacity=1,scale_low=1):
 style='direction:rtl;text-align:right' if rtl else 'text-align:left'
 spare,_=page.insert_htmlbox(rect,'<div style="'+style+'">'+body+'</div>',css=CSS,archive=ARCHIVE,opacity=opacity,scale_low=scale_low)
 if spare<0:raise ValueError('Stamp text does not fit')

def _mark(width,height,rect,body,rtl,**kw):
 # Laid out once on its own page and placed on every page, so the fonts are embedded once.
 mark=pymupdf.open();_box(mark.new_page(width=width,height=height),rect,body,rtl,**kw);return mark

def footer_mark(language,name,email,ref,size):
 # One small line under the page number band (body text and page numbers end above y=685 on a 709 pt page).
 w,h=size;line=t(OWNER[language])+' — '+t(LICENSED[language]+':')+' '+t(name)+' · '+t(email)+' · '+t(ORDER[language])+' '+t(ref)
 return _mark(w,h,pymupdf.Rect(47,h-20,w-47,h-6),'<span style="font-size:6pt;color:#6b7380">'+line+'</span>',language=='ar',opacity=0.85)

def diagonal_mark(language,name,email,size):
 # A long strip, placed on every page turned by 45 degrees: light grey at about 12% opacity,
 # 40 pt unless a long name needs a smaller size to stay on one line.
 w=min(size)*2**0.5*0.8;h=70
 plain=LICENSED[language]+': '+name+' - '+email
 font=pymupdf.Font(fontfile=str(FONTS/('IBMPlexSansArabic-Regular.ttf' if ARABIC.search(plain) else 'IBMPlexSans-Regular.ttf')))
 pt=min(40,w*0.92/max(font.text_length(plain,fontsize=1),1))
 label=t(LICENSED[language]+':')+' '+t(name)+' - '+t(email)
 mark=_mark(w,h,pymupdf.Rect(0,0,w,h),'<p style="text-align:center;white-space:nowrap;font-size:%.1fpt;color:#808080">'%pt+label+'</p>',language=='ar',opacity=0.12,scale_low=0)
 side=(w+h)/2**0.5;cx,cy=size[0]/2,size[1]/2
 return mark,pymupdf.Rect(cx-side/2,cy-side/2,cx+side/2,cy+side/2)

def licence_block(page,language,name,email,ref,sold_on):
 title,text=LICENCE[language];r=page.rect
 body=('<p style="font-size:7.5pt;letter-spacing:'+('0' if language=='ar' else '1.5pt')+';color:#9a4a12">'+t(title)+'</p>'
  '<p style="font-size:12pt;color:#1d2533;margin-top:6pt">'+t(name)+'</p>'
  '<p style="font-size:9pt;color:#4b5565;margin-top:2pt">'+t(email)+' · '+t(ORDER[language])+' '+t(ref)+' · '+t(sold_on)+'</p>'
  '<p style="font-size:8pt;line-height:1.5;color:#4b5565;margin-top:8pt">'+t(text)+'</p>')
 _box(page,pymupdf.Rect(47,64,r.width-47,330),body,language=='ar')

def stamp(source,language,name,email,ref,style='footer',sold_on=None):
 """Return the stamped PDF as bytes. source: path or bytes. style: 'footer' (default) or 'diagonal'."""
 if language not in OWNER or style not in ('footer','diagonal'):raise ValueError('Invalid language or style')
 name=' '.join((name or '').split())[:80] or email
 sold_on=sold_on or date.today().isoformat()
 doc=pymupdf.open(stream=source) if isinstance(source,(bytes,bytearray)) else pymupdf.open(source)
 marks={}
 for i,page in enumerate(doc):
  size=(page.rect.width,page.rect.height)
  if size not in marks:marks[size]=diagonal_mark(language,name,email,size) if style=='diagonal' else (footer_mark(language,name,email,ref,size),page.rect)
  mark,where=marks[size]
  page.show_pdf_page(where,mark,0,rotate=45 if style=='diagonal' else 0)
  doc.xref_set_key(page.xref,'AAK_Order',pymupdf.get_pdf_str(ref))
  if i==1:licence_block(page,language,name,email,ref,sold_on)
 # Hidden copies of the order reference: document info, catalog and every page object.
 meta=doc.metadata or {}
 meta.update({'subject':'Licensed to '+name+' <'+email+'> · order '+ref,'keywords':'licensed-copy order:'+ref})
 doc.set_metadata(meta)
 doc.xref_set_key(doc.pdf_catalog(),'AAK_License',pymupdf.get_pdf_str(ref+' '+email))
 fix_arabic_text(doc)
 out=doc.tobytes(garbage=1,deflate=True);doc.close()
 return out
