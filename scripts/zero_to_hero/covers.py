"""Three cover concepts for From Zero to Hero, each in Arabic, English and Russian, plus the Arabic back cover.

Art is original vector geometry (SVG); all words are live HTML text so they stay selectable and editable.
A: "Aperture"  — dark editorial, an iris built from exact blade geometry.
B: "Timeline"  — light Swiss layout, an editing timeline that fills up from 0:00 to the playhead.
C: "Light plan" — deep navy technical plan: key light, falloff rings (inverse-square), camera and Kelvin strip.
"""
import math
from diagrams import INK, NAVY, CYAN, COPPER, IVORY, SLATE, WHITE, COPPER_INK, MIST

COPY = {
    'ar': dict(dir='rtl', sub='الدليل العملي لصناعة المحتوى والفيديو',
               line='من الكاميرا والإضاءة والصوت إلى السرد والمونتاج وسير عمل الذكاء الاصطناعي والنمو',
               author='علي الخزاعي', ed='إصدار جديد موسّع · 2026', font='var(--ar)', disp='var(--ar-display)'),
    'en': dict(dir='ltr', sub='The practical guide to content and video creation',
               line='From camera, light and sound to story, editing, AI workflows and growth',
               author='Ali Alkhuzaee', ed='New expanded edition · 2026', font='var(--lat)', disp='var(--lat)'),
    'ru': dict(dir='ltr', sub='Практическое руководство по созданию контента и видео',
               line='От камеры, света и звука к сюжету, монтажу, ИИ‑процессам и росту',
               author='Али Альхузаи', ed='Новое расширенное издание · 2026', font='Geologica,var(--lat)', disp='Geologica,var(--lat)'),
}
W, H = 1760, 2500  # 0.1 mm units on a 176 × 250 mm cover

CSS = '''
.cover{position:relative;width:176mm;height:250mm;overflow:hidden}
.cover svg.art{position:absolute;inset:0;width:100%;height:100%}
.cover .txt{position:absolute;inset:0;padding:16mm 15mm 15mm;display:flex;flex-direction:column}
.cover .mark{font:800 41pt/0.92 var(--lat);letter-spacing:-.01em;direction:ltr;text-transform:uppercase}
.cover .mark em{font-style:normal}
.cover .sub{font-weight:600;font-size:15pt;line-height:1.4;margin-top:4.5mm;text-wrap:balance}
.cover .line{font-size:9.6pt;line-height:1.55;margin-top:2.4mm;max-width:118mm;opacity:.86;text-wrap:balance}
.cover .author{font-weight:700;font-size:12pt}
.cover .ed{font-size:8.6pt;opacity:.8}
.cover .foot{display:flex;justify-content:space-between;align-items:flex-end;gap:6mm}
.cover .brand{font:700 7pt/1 var(--lat);letter-spacing:.28em;direction:ltr}
'''


def _iris(cx, cy, R, r, n=8, rot=10):
    """Camera iris: an n-gon opening of radius r; each blade edge continues tangentially to the housing circle."""
    out = []
    verts = [(cx + r * math.cos(math.radians(rot + i * 360 / n)), cy + r * math.sin(math.radians(rot + i * 360 / n))) for i in range(n)]
    out.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in verts)}" fill="#0B1220"/>')
    for i in range(n):
        x1, y1 = verts[i]; x2, y2 = verts[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1; L = math.hypot(dx, dy); dx, dy = dx / L, dy / L
        # extend edge beyond x2 until it meets the housing circle
        fx, fy = x2 - cx, y2 - cy
        bq = 2 * (fx * dx + fy * dy); cq = fx * fx + fy * fy - R * R
        t = (-bq + math.sqrt(bq * bq - 4 * cq)) / 2
        ex, ey = x2 + dx * t, y2 + dy * t
        gx1, gy1, gx2, gy2 = x1, y1, cx + R * math.cos(a_mid := math.atan2((y1 + ey) / 2 - cy, (x1 + ex) / 2 - cx)), cy + R * math.sin(a_mid)
        # blade = edge + arc segment back along the housing
        a_end = math.atan2(ey - cy, ex - cx); a_start = math.atan2(y1 - cy, x1 - cx)
        sx, sy = cx + R * math.cos(a_start), cy + R * math.sin(a_start)
        out.append(f'<defs><linearGradient id="bl{i}" gradientUnits="userSpaceOnUse" x1="{gx1:.0f}" y1="{gy1:.0f}" x2="{gx2:.0f}" y2="{gy2:.0f}">'
                   f'<stop offset="0" stop-color="#3A4E72"/><stop offset=".45" stop-color="#1E2D49"/><stop offset="1" stop-color="#131D31"/></linearGradient></defs>')
        out.append(f'<path d="M{x1:.1f},{y1:.1f} L{ex:.1f},{ey:.1f} A{R},{R} 0 0 0 {sx:.1f},{sy:.1f} Z" fill="url(#bl{i})" stroke="#0B1220" stroke-width="4"/>')
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{COPPER}" stroke-width="2.5" stroke-opacity=".8"/>')
    return ''.join(out)


def art_a():
    b = [f'<rect width="{W}" height="{H}" fill="{INK}"/>',
         '<defs><radialGradient id="glow" cx=".5" cy=".38" r=".6"><stop offset="0" stop-color="#22365A" stop-opacity=".9"/><stop offset="1" stop-color="#101827" stop-opacity="0"/></radialGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#glow)"/>']
    for x in range(0, W + 1, 110):
        b.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#FFFFFF" stroke-opacity=".035"/>')
    for y in range(0, H + 1, 110):
        b.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#FFFFFF" stroke-opacity=".035"/>')
    cx, cy, R = 900, 860, 560
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{R+70}" fill="none" stroke="{COPPER}" stroke-opacity=".35" stroke-width="2"/>')
    for k in range(0, 360, 6):  # focus ring knurl
        a = math.radians(k); L = 26 if k % 30 == 0 else 12
        b.append(f'<line x1="{cx+(R+70)*math.cos(a):.1f}" y1="{cy+(R+70)*math.sin(a):.1f}" x2="{cx+(R+70+L)*math.cos(a):.1f}" y2="{cy+(R+70+L)*math.sin(a):.1f}" stroke="{COPPER}" stroke-opacity=".5" stroke-width="2"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#0E1626"/>')
    b.append(_iris(cx, cy, R, 215, n=9))
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{COPPER}" stroke-width="5"/>')
    b.append(f'<path d="M{cx+R+120},{cy} A{R+120},{R+120} 0 0 0 {cx+(R+120)*math.cos(math.radians(-58)):.1f},{cy+(R+120)*math.sin(math.radians(-58)):.1f}" fill="none" stroke="{CYAN}" stroke-width="7" stroke-linecap="round"/>')
    # viewfinder corners and readout
    for x, y, sx, sy in ((150, 150, 1, 1), (W - 150, 150, -1, 1), (150, 1560, 1, -1), (W - 150, 1560, -1, -1)):
        b.append(f'<path d="M{x},{y+sy*90} V{y} H{x+sx*90}" fill="none" stroke="{IVORY}" stroke-opacity=".55" stroke-width="4"/>')
    b.append(f'<text x="{W/2}" y="1600" font-family="IBM Plex Mono,Noto Sans Symbols 2,monospace" font-size="30" fill="{MIST}" text-anchor="middle" letter-spacing="6">25p · 1/50 · f/2.8 · ISO 200 · 5600K</text>')
    b.append(f'<circle cx="215" cy="215" r="13" fill="#E5484D"/><text x="245" y="226" font-family="IBM Plex Mono,Noto Sans Symbols 2,monospace" font-size="30" fill="{IVORY}" fill-opacity=".7">REC 00:00:00:00</text>')
    return ''.join(b)


def art_b():
    b = [f'<rect width="{W}" height="{H}" fill="{IVORY}"/>']
    # timeline band
    y0 = 1260
    b.append(f'<rect x="0" y="{y0-70}" width="{W}" height="560" fill="#EFEDE6"/>')
    for k in range(0, 41):
        x = 120 + k * 38
        h = 34 if k % 5 == 0 else 16
        b.append(f'<line x1="{x}" y1="{y0-70}" x2="{x}" y2="{y0-70+h}" stroke="{SLATE}" stroke-width="2"/>')
    b.append(f'<text x="120" y="{y0-110}" font-family="IBM Plex Mono,Noto Sans Symbols 2,monospace" font-size="30" fill="{SLATE}">00:00:00:00</text>')
    tracks = [('V2', 0.55), ('V1', 0.95), ('A1', 0.9), ('A2', 0.45)]
    import random
    rnd = random.Random(7)
    colors = {'V2': CYAN, 'V1': NAVY, 'A1': COPPER, 'A2': '#C9CED6'}
    for t, (name, dens) in enumerate(tracks):
        y = y0 + t * 110
        b.append(f'<text x="70" y="{y+58}" font-family="IBM Plex Mono,Noto Sans Symbols 2,monospace" font-size="28" fill="{SLATE}">{name}</text>')
        x = 130
        while x < 1640:
            prog = (x - 130) / 1510  # timeline fills up: sparse at 0:00, dense near the playhead
            gap = 120 * (1 - prog) + 8
            w = 60 + rnd.random() * 220 * (0.4 + prog)
            if rnd.random() < dens * (0.35 + 0.65 * prog):
                ww = min(w, 1640 - x)
                b.append(f'<rect x="{x:.0f}" y="{y+16}" width="{ww:.0f}" height="78" rx="10" fill="{colors[name]}" fill-opacity="{0.35 + 0.65*prog:.2f}"/>')
                if name.startswith('A'):
                    for wx in range(int(x) + 10, int(x + ww) - 10, 12):
                        hh = 8 + 26 * abs(math.sin(wx * 0.07)) * (0.5 + prog)
                        b.append(f'<line x1="{wx}" y1="{y+55-hh:.0f}" x2="{wx}" y2="{y+55+hh:.0f}" stroke="{INK}" stroke-opacity=".35" stroke-width="3"/>')
            x += w + gap
    px = 1500
    b.append(f'<line x1="{px}" y1="{y0-150}" x2="{px}" y2="{y0+470}" stroke="{COPPER_INK}" stroke-width="6"/>')
    b.append(f'<path d="M{px-26},{y0-150} h52 l-26,34 z" fill="{COPPER_INK}"/>')
    # giant outline zero
    b.append(f'<text x="40" y="2460" font-family="Manrope" font-weight="800" font-size="1000" fill="none" stroke="{INK}" stroke-opacity=".09" stroke-width="5" text-anchor="start">0</text>')
    return ''.join(b)


def art_c():
    b = [f'<rect width="{W}" height="{H}" fill="{NAVY}"/>']
    for x in range(0, W + 1, 55):
        b.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#FFFFFF" stroke-opacity="{.07 if x % 275 == 0 else .025}"/>')
    for y in range(0, H + 1, 55):
        b.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#FFFFFF" stroke-opacity="{.07 if y % 275 == 0 else .025}"/>')
    sx, sy = 1020, 1330         # subject
    kx, ky = 600, 1650          # key light
    d0 = math.hypot(sx - kx, sy - ky)
    for f, lbl in ((0.5, '400%'), (1, '100%'), (1.41, '50%'), (2, '25%')):  # isolux rings around the key
        r = d0 * f
        b.append(f'<circle cx="{kx}" cy="{ky}" r="{r:.0f}" fill="none" stroke="{COPPER}" stroke-opacity="{.75 if f == 1 else .3}" stroke-width="{4 if f == 1 else 2.5}" stroke-dasharray="{"0" if f == 1 else "14 12"}"/>')
        b.append(f'<text x="{kx + r*math.cos(math.radians(-62)) + 14:.0f}" y="{ky + r*math.sin(math.radians(-62)):.0f}" font-family="IBM Plex Mono,Noto Sans Symbols 2,monospace" font-size="28" fill="{COPPER}" fill-opacity=".85">{lbl}</text>')
    ang = math.atan2(sy - ky, sx - kx)
    a1, a2 = ang - math.radians(24), ang + math.radians(24)
    b.append(f'<path d="M{kx},{ky} L{kx+900*math.cos(a1):.0f},{ky+900*math.sin(a1):.0f} L{kx+900*math.cos(a2):.0f},{ky+900*math.sin(a2):.0f} Z" fill="#FFF4E2" fill-opacity=".10"/>')
    # softbox
    px, py = -math.sin(ang), math.cos(ang)
    pts = [(kx + px * 150, ky + py * 150), (kx - px * 150, ky - py * 150), (kx - px * 150 - math.cos(ang) * 40, ky - py * 150 - math.sin(ang) * 40), (kx + px * 150 - math.cos(ang) * 40, ky + py * 150 - math.sin(ang) * 40)]
    b.append(f'<polygon points="{" ".join(f"{x:.0f},{y:.0f}" for x, y in pts)}" fill="#FFF4E2" stroke="{IVORY}" stroke-width="4"/>')
    # subject, camera, rim
    b.append(f'<circle cx="{sx}" cy="{sy}" r="74" fill="none" stroke="{IVORY}" stroke-width="5"/><path d="M{sx-22},{sy+70} L{sx},{sy+112} L{sx+22},{sy+70}" fill="none" stroke="{IVORY}" stroke-width="5"/>')
    cx, cy = sx, sy + 440
    b.append(f'<rect x="{cx-60}" y="{cy}" width="120" height="74" rx="8" fill="none" stroke="{CYAN}" stroke-width="5"/><path d="M{cx-30},{cy} L{cx-48},{cy-48} L{cx+48},{cy-48} L{cx+30},{cy}" fill="none" stroke="{CYAN}" stroke-width="5"/>')
    b.append(f'<line x1="{sx}" y1="{sy+120}" x2="{cx}" y2="{cy-60}" stroke="{CYAN}" stroke-width="3" stroke-dasharray="12 12"/>')
    b.append(f'<rect x="{sx+300}" y="{sy-380}" width="70" height="160" rx="8" transform="rotate(35 {sx+335} {sy-300})" fill="none" stroke="{IVORY}" stroke-width="4"/>')
    b.append(f'<path d="M{sx},{sy} m0,-230 a230,230 0 0 0 -{230*math.sin(math.radians(45)):.0f},{230-230*math.cos(math.radians(45)):.0f}" fill="none" stroke="{IVORY}" stroke-opacity=".5" stroke-width="3"/>')
    b.append(f'<text x="{kx-40}" y="{ky+150}" font-family="IBM Plex Mono,Noto Sans Symbols 2,monospace" font-size="30" fill="{IVORY}" fill-opacity=".8" text-anchor="middle">KEY · 5600K</text>')
    b.append(f'<text x="{cx}" y="{cy+130}" font-family="IBM Plex Mono,Noto Sans Symbols 2,monospace" font-size="30" fill="{CYAN}" text-anchor="middle">CAM A · 35mm</text>')
    # kelvin strip
    g = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in ((0, '#FF8A1F'), (.18, '#FFB46B'), (.45, '#FFE4CE'), (.6, '#FFF4EA'), (.78, '#E3E9FF'), (1, '#BFD3FF')))
    b.append(f'<defs><linearGradient id="kc" x1="0" x2="1">{g}</linearGradient></defs><rect x="150" y="2060" width="{W-300}" height="16" rx="8" fill="url(#kc)"/>')
    for k, lbl in ((0, '2000K'), (.33, '3200K'), (.6, '5600K'), (1, '10000K')):
        b.append(f'<text x="{150 + k*(W-300):.0f}" y="2120" font-family="IBM Plex Mono,Noto Sans Symbols 2,monospace" font-size="26" fill="{MIST}" text-anchor="{"start" if k == 0 else "end" if k == 1 else "middle"}">{lbl}</text>')
    return ''.join(b)


def cover(concept, lang):
    c = COPY[lang]
    art = {'A': art_a, 'B': art_b, 'C': art_c}[concept]()
    fg, accent, line = {'A': (IVORY, COPPER, '#C9D3E0'), 'B': (INK, COPPER_INK, SLATE), 'C': (WHITE, COPPER, '#C9D4E3')}[concept]
    align = 'right' if c['dir'] == 'rtl' else 'left'
    mark = '<em>FROM ZERO</em><br><em style="color:%s">TO HERO</em>' % accent
    sub = f'<div class="sub" style="font-family:{c["disp"]}">{c["sub"]}</div><div class="line" style="color:{line}">{c["line"]}</div>'
    foot = (f'<div class="foot" style="direction:{c["dir"]}"><div><div class="author" style="font-family:{c["disp"]}">{c["author"]}</div>'
            f'<div class="ed" style="font-family:{c["font"]}">{c["ed"]}</div></div><div class="brand" style="color:{accent}">ALIALKHUZAEE.COM</div></div>')
    if concept == 'A':
        body = f'<div style="margin-top:auto"></div><div style="text-align:{align}"><div class="mark" style="text-align:{align}">{mark}</div>{sub}</div><div style="height:9mm"></div>{foot}'
    elif concept == 'B':
        body = (f'<div class="brand" style="color:{accent};text-align:{align}">ALI ALKHUZAEE · CREATOR EDUCATION</div>'
                f'<div style="margin-top:14mm;text-align:{align}"><div class="mark" style="font-size:50pt">{mark}</div>{sub}</div><div style="margin-top:auto"></div>{foot}')
    else:
        body = (f'<div style="text-align:{align}"><div class="mark" style="font-size:46pt">{mark}</div>{sub}</div><div style="margin-top:auto"></div>{foot}')
    return (f'<div class="page cover" lang="{lang}" dir="{c["dir"]}"><svg class="art" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" style="direction:ltr">{art}</svg>'
            f'<div class="txt" style="color:{fg};font-family:{c["font"]};text-align:{align}">{body}</div></div>')


def back_cover():
    """Arabic back cover in concept A's language. Claims are limited to what the finished book will contain."""
    art = f'<rect width="{W}" height="{H}" fill="{INK}"/>' + ''.join(
        f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="#FFFFFF" stroke-opacity=".035"/>' for x in range(0, W + 1, 110))
    return f'''<div class="page cover" lang="ar" dir="rtl"><svg class="art" viewBox="0 0 {W} {H}" aria-hidden="true">{art}</svg>
<div class="txt" style="color:{IVORY};padding:20mm 17mm 16mm">
 <div class="brand" style="color:{COPPER};text-align:right">FROM ZERO TO HERO</div>
 <p style="font:600 17pt/1.5 var(--ar-display);margin:7mm 0 5mm">صوّر وسجّل وحرّر وانشر بفهم، لا بإعدادات محفوظة.</p>
 <p style="font-size:10.5pt;line-height:1.75;color:#D5DCE6;margin:0 0 6mm">كتاب عملي بالعربية لصانع المحتوى المبتدئ والمتوسط وصاحب المشروع الصغير. كل مهارة فيه تبدأ بالسبب، ثم الخطوات، ثم تمرين يمكنك قياس نتيجته، ثم قائمة فحص قبل النشر.</p>
 <div style="display:grid;grid-template-columns:1fr 1fr;gap:3mm 7mm;font-size:9.6pt;line-height:1.55;color:#E6EAF0">
  <div><b style="color:{COPPER}">التصوير</b><br>التعريض، الغالق والإطارات، العدسات والتكوين.</div>
  <div><b style="color:{COPPER}">الإضاءة</b><br>حجم المصدر، الاتجاه، النسب، حرارة اللون.</div>
  <div><b style="color:{COPPER}">الصوت</b><br>اختيار الميكروفون، الغرفة، الكسب، المعالجة.</div>
  <div><b style="color:{COPPER}">السرد والمونتاج</b><br>الافتتاحية، قائمة اللقطات، القطع، التلوين.</div>
  <div><b style="color:{COPPER}">الذكاء الاصطناعي</b><br>برومبتات قابلة للتعديل مع طرق تحقق.</div>
  <div><b style="color:{COPPER}">النمو والأعمال</b><br>قراءة الأرقام بحذر ومنتج رقمي صادق.</div>
 </div>
 <div style="margin-top:7mm;border-top:.25mm solid rgba(248,247,243,.25);padding-top:4mm;font-size:9.4pt;line-height:1.65;color:#C9D3E0">
  <b style="color:{IVORY}">ما لا يعدك به هذا الكتاب:</b> لا أرقام مشاهدات مضمونة، ولا «إعدادات سحرية»، ولا شهادات مختلقة. الأمثلة المرسومة توضيحية، وأسعار الأدوات وخططها تتغير، لذلك تحمل تاريخ تحقق.
 </div>
 <div style="margin-top:auto" class="foot"><div><div class="author" style="font-family:var(--ar-display)">علي الخزاعي</div><div class="ed">إصدار جديد موسّع من «من الصفر إلى صناعة المحتوى بالذكاء الاصطناعي»</div></div><div class="brand" style="color:{COPPER}">ALIALKHUZAEE.COM</div></div>
</div></div>'''
