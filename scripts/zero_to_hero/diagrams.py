"""Original instructional diagrams for From Zero to Hero, drawn as editable SVG.

Every function returns a standalone <svg> string. Physical values (stops, angles, falloff, polar patterns)
are computed here rather than drawn by eye, so the figures stay correct when edited.
Full-width figures use a 600-unit viewBox (≈142 mm in the book, 1 unit ≈ 0.24 mm); half-width ones use 290.
"""
import json, math, pathlib, re
from html import escape

INK, NAVY, CYAN, COPPER, IVORY, SLATE, WHITE, WARN = '#101827', '#16263E', '#25C5D9', '#E3A86B', '#F8F7F3', '#526174', '#FFFFFF', '#B54C43'
CYAN_INK, COPPER_INK, MIST, RULE, PAPER2 = '#0B6E7C', '#8A4F1C', '#9FB0C6', '#D8DBE0', '#EFEDE6'
AR_RE = re.compile('[؀-ۿ]')
AR, LAT = "'IBM Plex Sans Arabic','Noto Sans Math','Noto Sans Symbols 2',sans-serif", "Manrope,'IBM Plex Sans Arabic','Noto Sans Math','Noto Sans Symbols 2',sans-serif"


# Language of the labels. The book is drawn in Arabic; the website presentation also needs English and Russian.
# Translations live in diagram_i18n.json keyed by the Arabic label; a missing one fails loudly.
LANG = 'ar'
I18N = json.loads((pathlib.Path(__file__).with_name('diagram_i18n.json')).read_text(encoding='utf-8'))


def tr(s):
    if LANG == 'ar' or not AR_RE.search(s):
        return s
    if s not in I18N:
        raise KeyError(f'diagram label has no {LANG} translation: {s!r}')
    return I18N[s][LANG]


def render(name, lang='ar'):
    """Draw one diagram in the given language."""
    global LANG
    prev, LANG = LANG, lang
    try:
        return ALL[name]()
    finally:
        LANG = prev


def T(x, y, s, size=13, w=500, fill=INK, align='center', font=None, extra=''):
    """Text in physical alignment terms (left/center/right), correct for both Arabic (RTL) and Latin runs."""
    s = tr(s)
    rtl = bool(AR_RE.search(s))
    anchor = {'center': 'middle', 'right': 'start' if rtl else 'end', 'left': 'end' if rtl else 'start'}[align]
    fam = font or (AR if rtl else LAT)
    d = f' direction="{'rtl' if rtl else 'ltr'}"'
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}"{d} {extra}>{escape(s)}</text>'


def ltr(s):
    """Isolate a left-to-right run (numbers, ranges, formulas) inside Arabic text."""
    return '\u2066' + s + '\u2069'


def svg(w, h, body, label):
    label = tr(label)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}">'
            f'<title>{escape(label)}</title>{body}</svg>')


def arrow_defs(color=INK, id='ah'):
    return f'<defs><marker id="{id}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker></defs>'


# ---------------------------------------------------------------- exposure
def exposure_stops():
    rows = [
        ('فتحة العدسة', 'Aperture · f-number', ['f/16', 'f/11', 'f/8', 'f/5.6', 'f/4', 'f/2.8', 'f/2', 'f/1.4'], 'عمق مجال أعمق', 'عمق مجال ضحل'),
        ('زمن الغالق', 'Shutter · seconds', ['1/4000', '1/2000', '1/1000', '1/500', '1/250', '1/125', '1/60', '1/30'], 'حركة متجمدة', 'طمس حركة أكثر'),
        ('حساسية ISO', 'ISO · gain', ['100', '200', '400', '800', '1600', '3200', '6400', '12800'], 'ضجيج أقل ومدى أوسع', 'ضجيج أوضح'),
    ]
    W, x0, x1 = 600, 30, 430
    b = [arrow_defs(COPPER_INK, 'ex')]
    b.append('<defs><linearGradient id="lightg" x1="0" x2="1"><stop offset="0" stop-color="#1b2433"/><stop offset="1" stop-color="#FFF4E2"/></linearGradient></defs>')
    b.append(f'<rect x="{x0}" y="14" width="{x1-x0}" height="14" rx="3" fill="url(#lightg)"/>')
    b.append(T(x0, 46, 'أقل ضوءًا', 11.5, 600, SLATE, 'left'))
    b.append(T(x1, 46, 'أكثر ضوءًا', 11.5, 600, SLATE, 'right'))
    for i, (ar, en, vals, lo, hi) in enumerate(rows):
        y = 92 + i * 84
        b.append(T(590, y - 4, ar, 14, 700, INK, 'right'))
        b.append(T(590, y + 14, en, 10.5, 600, SLATE, 'right'))
        b.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{RULE}" stroke-width="2"/>')
        step = (x1 - x0) / (len(vals) - 1)
        for j, v in enumerate(vals):
            x = x0 + j * step
            b.append(f'<circle cx="{x:.1f}" cy="{y}" r="6.5" fill="{WHITE}" stroke="{INK}" stroke-width="1.6"/>')
            b.append(f'<circle cx="{x:.1f}" cy="{y}" r="{1.2 + j*0.55:.1f}" fill="{INK}"/>')
            b.append(T(x, y - 14, v, 10.5, 700, INK))
        b.append(T(x0, y + 26, lo, 11, 500, SLATE, 'left'))
        b.append(T(x1, y + 26, hi, 11, 500, SLATE, 'right'))
    # one-stop bracket
    xa, xb, yb = x0 + 4 * (x1 - x0) / 7, x0 + 5 * (x1 - x0) / 7, 312
    b.append(f'<path d="M{xa:.1f},{yb-8} v8 h{xb-xa:.1f} v-8" fill="none" stroke="{COPPER_INK}" stroke-width="1.4"/>')
    b.append(T((xa + xb) / 2, yb + 16, 'خطوة واحدة = ضعف الضوء أو نصفه', 11.5, 700, COPPER_INK))
    return svg(W, 336, ''.join(b), 'سلالم الستوب الثلاثة: الفتحة والغالق وISO، وكل خطوة تضاعف الضوء أو تنصفه')


def shutter_angle():
    W, H = 600, 250
    b = []
    cases = [(360, '1/25'), (180, '1/50'), (90, '1/100'), (45, '1/200')]
    for i, (ang, sp) in enumerate(cases):
        cx, cy, r = 527 - i * 142, 70, 40
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{NAVY}"/>')
        if ang >= 360:
            b.append(f'<circle cx="{cx}" cy="{cy}" r="{r-3}" fill="#FFF4E2"/>')
        else:
            a = math.radians(ang)
            x2, y2 = cx + (r - 3) * math.sin(a), cy - (r - 3) * math.cos(a)
            large = 1 if ang > 180 else 0
            b.append(f'<path d="M{cx},{cy} L{cx},{cy-r+3} A{r-3},{r-3} 0 {large} 1 {x2:.1f},{y2:.1f} Z" fill="#FFF4E2"/>')
        b.append(f'<rect x="{cx-20}" y="{cy+r+6}" width="40" height="18" rx="9" fill="{COPPER if ang == 180 else PAPER2}"/>')
        b.append(T(cx, cy + r + 19, f'{ang}°', 11.5, 800, INK))
        b.append(T(cx, 146, f'غالق {ltr(sp)} ث', 12.5, 700, INK))
        # motion streak: blur length proportional to exposure time
        L = 6 + 60 * ang / 360
        y = 176
        b.append(f'<defs><linearGradient id="st{i}" x1="0" x2="1"><stop offset="0" stop-color="{INK}" stop-opacity="0"/><stop offset="1" stop-color="{INK}" stop-opacity=".85"/></linearGradient></defs>')
        b.append(f'<rect x="{cx-L/2-2:.1f}" y="{y-9}" width="{L:.1f}" height="18" rx="9" fill="url(#st{i})"/>')
        b.append(f'<circle cx="{cx+L/2-2:.1f}" cy="{y}" r="9" fill="{INK}"/>')
        b.append(T(cx, 208, ['طمس قوي', 'طمس طبيعي', 'حركة أحدّ', 'حركة متقطعة'][i], 11.5, 500, SLATE))
        if ang == 180:
            b.append(f'<rect x="{cx-66}" y="20" width="132" height="200" rx="8" fill="none" stroke="{COPPER}" stroke-width="1.6" stroke-dasharray="4 4"/>')
            b.append(T(cx, 15, 'نقطة البداية المعتادة', 11, 700, COPPER_INK))
    b.append(f'<rect x="0" y="222" width="{W}" height="28" rx="5" fill="{PAPER2}"/>')
    b.append(T(590, 241, 'عند 25 إطارًا في الثانية، زاوية 180° تعني:', 12, 600, INK, 'right'))
    b.append(T(12, 241, 'shutter = 1 ÷ (2 × 25) = 1/50 s', 12, 700, COPPER_INK, 'left'))
    return svg(W, H, ''.join(b), 'زاوية الغالق عند 25 إطارًا في الثانية وأثرها في طمس الحركة')


def flicker():
    W, H = 600, 236
    x0, x1, y0, yb = 40, 580, 30, 160  # 0..30 ms
    sx = (x1 - x0) / 30
    b = [arrow_defs(SLATE, 'fl')]
    pts = []
    for k in range(0, 301):
        t = k / 10
        v = abs(math.sin(2 * math.pi * 50 * t / 1000))
        pts.append(f'{x0 + t*sx:.1f},{yb - v*(yb-y0-10):.1f}')
    # exposure windows
    def win(t0, dur, color, lbl, y):
        b.append(f'<rect x="{x0+t0*sx:.1f}" y="{y0}" width="{dur*sx:.1f}" height="{yb-y0}" fill="{color}" opacity=".16"/>')
        b.append(f'<path d="M{x0+t0*sx:.1f},{y} h{dur*sx:.1f}" stroke="{color}" stroke-width="3"/>')
        b.append(T(x0 + (t0 + dur / 2) * sx, y - 7, lbl, 11, 700, color))
    win(1.5, 10, CYAN_INK, f'{ltr("1/100")} ث = دورة كاملة', 26)
    win(14.5, 6.25, WARN, f'{ltr("1/160")} ث: جزء', 26)
    win(23.0, 6.25, WARN, f'{ltr("1/160")} ث: جزء آخر', 26)
    b.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{COPPER_INK}" stroke-width="2.2"/>')
    b.append(f'<line x1="{x0}" y1="{yb}" x2="{x1+8}" y2="{yb}" stroke="{SLATE}" stroke-width="1.2" marker-end="url(#fl)"/>')
    for ms in range(0, 31, 5):
        b.append(f'<line x1="{x0+ms*sx:.1f}" y1="{yb}" x2="{x0+ms*sx:.1f}" y2="{yb+5}" stroke="{SLATE}"/>')
        b.append(T(x0 + ms * sx, yb + 18, f'{ms} ms', 10, 600, SLATE))
    b.append(T(300, 202, 'شدة ضوء يعمل على تيار 50 هرتز تنبض 100 مرة في الثانية (منحنى توضيحي لمصباح شديد الوميض)', 11.5, 500, INK))
    b.append(T(300, 222, f'زمن تعريض يساوي مضاعفات {ltr("1/100")} ث يجمع كمية الضوء نفسها في كل إطار؛ غيره قد يُظهر وميضًا أو أشرطة', 11.5, 600, INK))
    return svg(W, H, ''.join(b), 'لماذا يسبب زمن غالق غير متوافق مع تردد الكهرباء وميضًا في الفيديو')


# ---------------------------------------------------------------- lighting
def _shadow_panel(ox, title, src_len, src_x, note):
    """Side view: source (vertical segment) -> opaque card -> wall. Shadow edges from exact ray geometry."""
    b = []
    cy, wall_x = 120, ox + 250
    obj_x, ot, ob = ox + 150, 95, 135
    st, sb = cy - src_len / 2, cy + src_len / 2
    def hit(sy, oy):
        return sy + (oy - sy) * (wall_x - src_x) / (obj_x - src_x)
    up0, up1 = hit(sb, ot), hit(st, ot)   # upper penumbra
    lo0, lo1 = hit(sb, ob), hit(st, ob)   # lower penumbra
    gid = f'g{ox}'
    b.append(f'<defs><linearGradient id="{gid}u" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK}" stop-opacity=".08"/><stop offset="1" stop-color="{INK}" stop-opacity=".85"/></linearGradient>'
             f'<linearGradient id="{gid}l" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK}" stop-opacity=".85"/><stop offset="1" stop-color="{INK}" stop-opacity=".08"/></linearGradient></defs>')
    b.append(f'<rect x="{wall_x}" y="20" width="14" height="210" fill="{PAPER2}" stroke="{RULE}"/>')
    b.append(f'<rect x="{wall_x}" y="{up0:.1f}" width="14" height="{up1-up0:.1f}" fill="url(#{gid}u)"/>')
    b.append(f'<rect x="{wall_x}" y="{up1:.1f}" width="14" height="{lo0-up1:.1f}" fill="{INK}" opacity=".88"/>')
    b.append(f'<rect x="{wall_x}" y="{lo0:.1f}" width="14" height="{lo1-lo0:.1f}" fill="url(#{gid}l)"/>')
    for sy, oy in ((st, ot), (sb, ot), (st, ob), (sb, ob)):
        b.append(f'<line x1="{src_x}" y1="{sy:.1f}" x2="{wall_x}" y2="{hit(sy, oy):.1f}" stroke="{COPPER}" stroke-width="1" stroke-dasharray="3 3"/>')
    b.append(f'<rect x="{src_x-5}" y="{st:.1f}" width="10" height="{src_len}" rx="3" fill="#FFF4E2" stroke="{COPPER_INK}" stroke-width="1.6"/>')
    b.append(f'<rect x="{obj_x-3}" y="{ot}" width="6" height="{ob-ot}" fill="{NAVY}"/>')
    b.append(T(ox + 130, 16, title, 12.5, 700, INK))
    b.append(T(wall_x - 6, 246, 'شبه ظل ' + ('عريض' if lo1 - lo0 > 30 else 'ضيق'), 11, 700, COPPER_INK, 'right'))
    b.append(T(src_x, cy + src_len / 2 + 18, 'المصدر', 10.5, 600, SLATE))
    b.append(T(obj_x, ob + 16, 'جسم', 10.5, 600, SLATE))
    b.append(T(ox + 130, 268, note, 11, 500, SLATE))
    return ''.join(b)


def hard_soft():
    body = _shadow_panel(310, 'مصدر صغير وبعيد ← حافة حادة', 10, 340, 'الانتقال من الضوء إلى الظل سريع') + \
           _shadow_panel(10, 'مصدر كبير وقريب ← حافة ناعمة', 60, 70, 'منطقة شبه الظل أعرض، فيبدو الظل أنعم') + \
           f'<line x1="300" y1="20" x2="300" y2="270" stroke="{RULE}"/>' + \
           f'<rect x="420" y="282" width="12" height="12" fill="{INK}" opacity=".88"/>' + T(414, 292, 'ظل كامل Umbra', 10.5, 600, INK, 'right') + \
           f'<rect x="230" y="282" width="12" height="12" fill="url(#g10u)"/>' + T(224, 292, 'شبه ظل Penumbra', 10.5, 600, INK, 'right')
    return svg(600, 300, body, 'مقارنة هندسية بين مصدر ضوء صغير بعيد ومصدر كبير قريب وأثرهما في عرض شبه الظل')


def lighting_plan():
    W, H = 600, 424
    b = [arrow_defs(SLATE, 'lp')]
    sx, sy = 300, 196
    def beam(x, y, ang, spread, length, color, op):
        a1, a2 = math.radians(ang - spread), math.radians(ang + spread)
        return (f'<path d="M{x},{y} L{x+length*math.cos(a1):.1f},{y+length*math.sin(a1):.1f} '
                f'L{x+length*math.cos(a2):.1f},{y+length*math.sin(a2):.1f} Z" fill="{color}" opacity="{op}"/>')
    def fixture(x, y, ang, w, label, sub, color, lx, ly, align):
        dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        px, py = -dy, dx
        p = [(x + px * w / 2, y + py * w / 2), (x - px * w / 2, y - py * w / 2), (x - px * w / 2 - dx * 14, y - py * w / 2 - dy * 14), (x + px * w / 2 - dx * 14, y + py * w / 2 - dy * 14)]
        s = f'<polygon points="{" ".join(f"{a:.1f},{c:.1f}" for a, c in p)}" fill="{color}" stroke="{INK}" stroke-width="1.4"/>'
        s += T(lx, ly, label, 12.5, 700, INK, align) + T(lx, ly + 16, sub, 10.5, 500, SLATE, align)
        return s
    # background wall
    b.append(f'<rect x="60" y="18" width="480" height="12" fill="{PAPER2}" stroke="{RULE}"/>')
    b.append(T(300, 50, 'الخلفية', 11, 600, SLATE))
    b.append(f'<line x1="566" y1="30" x2="566" y2="{sy-24}" stroke="{SLATE}" marker-start="url(#lp)" marker-end="url(#lp)"/>')
    b.append(T(560, 110, 'مسافة', 10.5, 600, SLATE, 'right'))
    b.append(T(560, 124, 'تفصل الظل', 10.5, 600, SLATE, 'right'))
    b.append(T(560, 138, 'عن الخلفية', 10.5, 600, SLATE, 'right'))
    # key at camera-left 45°, fill camera-right, rim behind
    kx, ky = sx - 125, sy + 125
    fx, fy = sx + 150, sy + 90
    rx, ry = sx + 110, sy - 120
    b.append(beam(kx, ky, -45, 22, 190, COPPER, .22))
    b.append(beam(fx, fy, math.degrees(math.atan2(sy - fy, sx - fx)), 20, 175, CYAN, .14))
    b.append(beam(rx, ry, math.degrees(math.atan2(sy - ry, sx - rx)), 10, 150, '#FFF4E2', .9))
    # subject
    b.append(f'<circle cx="{sx}" cy="{sy}" r="24" fill="{NAVY}"/><path d="M{sx-7},{sy+21} L{sx},{sy+34} L{sx+7},{sy+21} Z" fill="{NAVY}"/>')
    b.append(T(sx + 34, sy - 6, 'الشخص', 12.5, 700, INK, 'left'))
    # camera
    cx, cy = sx, sy + 150
    b.append(f'<rect x="{cx-18}" y="{cy}" width="36" height="22" rx="3" fill="{INK}"/><path d="M{cx-9},{cy} L{cx-14},{cy-14} L{cx+14},{cy-14} L{cx+9},{cy} Z" fill="{INK}"/>')
    b.append(T(cx, cy + 38, 'الكاميرا', 12, 700, INK))
    b.append(f'<line x1="{sx}" y1="{sy+28}" x2="{cx}" y2="{cy-16}" stroke="{SLATE}" stroke-dasharray="3 4"/>')
    # 45° angle arc between camera axis and key direction
    r = 62
    b.append(f'<path d="M{sx},{sy+r} A{r},{r} 0 0 1 {sx - r*math.sin(math.radians(45)):.1f},{sy + r*math.cos(math.radians(45)):.1f}" fill="none" stroke="{COPPER_INK}" stroke-width="1.6"/>')
    b.append(T(sx - 30, sy + 78, '≈45°', 11.5, 800, COPPER_INK))
    b.append(fixture(kx, ky, -45, 58, 'الضوء الرئيسي Key', 'مصدر كبير، أعلى من العين قليلًا', '#FFF4E2', kx - 40, ky + 44, 'center'))
    b.append(fixture(fx, fy, math.degrees(math.atan2(sy - fy, sx - fx)), 50, 'التعبئة Fill', 'عاكس أو ضوء أضعف بـ 1–2 ستوب', '#E6F6F8', fx + 4, fy + 46, 'center'))
    b.append(fixture(rx, ry, math.degrees(math.atan2(sy - ry, sx - rx)), 26, 'ضوء الحافة Rim', 'خلف الشخص، يفصل الكتف والشعر', '#FFF4E2', rx - 30, ry - 6, 'right'))
    return svg(W, H, ''.join(b), 'مخطط علوي لإضاءة ثلاثية: رئيسي بزاوية 45 درجة، وتعبئة، وضوء حافة، ومسافة عن الخلفية')


def inverse_square():
    W, H = 600, 300
    x0, x1, y0, y1 = 70, 470, 24, 236
    dmin, dmax, vmax = 0.4, 4.0, 300
    X = lambda d: x0 + (d - dmin) / (dmax - dmin) * (x1 - x0)
    Y = lambda v: y1 - min(v, vmax) / vmax * (y1 - y0)
    b = [arrow_defs(SLATE, 'is')]
    for v in (0, 50, 100, 200, 300):
        b.append(f'<line x1="{x0}" y1="{Y(v):.1f}" x2="{x1}" y2="{Y(v):.1f}" stroke="{RULE}" stroke-width="{1.4 if v==0 else .8}"/>')
        b.append(T(x0 - 8, Y(v) + 4, f'{v}%', 10, 600, SLATE, 'right'))
    for d in (0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4):
        b.append(T(X(d), y1 + 16, f'{d:g} m', 10, 600, SLATE))
    r = 0.3  # 60 cm round softbox
    pt = ' '.join(f'{X(d):.1f},{Y(100/d**2):.1f}' for d in [dmin + i * 0.01 for i in range(int((dmax - dmin) / 0.01) + 1)] if 100 / d**2 <= vmax * 1.02)
    disk = ' '.join(f'{X(d):.1f},{Y(100/(d**2 + r**2)):.1f}' for d in [dmin + i * 0.01 for i in range(int((dmax - dmin) / 0.01) + 1)])
    b.append(f'<polyline points="{pt}" fill="none" stroke="{INK}" stroke-width="2.4"/>')
    b.append(f'<polyline points="{disk}" fill="none" stroke="{COPPER_INK}" stroke-width="2.2" stroke-dasharray="6 4"/>')
    for d, lbl in ((1, 'المرجع ' + ltr('100%')), (1.41, '−1 EV'), (2, '−2 EV'), (2.83, '−3 EV'), (4, '−4 EV')):
        v = 100 / d**2
        b.append(f'<circle cx="{X(d):.1f}" cy="{Y(v):.1f}" r="4.5" fill="{WHITE}" stroke="{INK}" stroke-width="1.8"/>')
        b.append(T(X(d) + 6, Y(v) - 10, lbl, 10.5, 700, INK, 'left'))
    b.append(T((x0 + x1) / 2, y1 + 36, 'المسافة بين المصدر والشخص', 11, 600, SLATE))
    lx = 490
    b.append(f'<line x1="{lx}" y1="44" x2="{lx+26}" y2="44" stroke="{INK}" stroke-width="2.4"/>')
    b.append(T(596, 48, 'مصدر نقطي:', 11, 700, INK, 'right'))
    b.append(T(596, 64, 'الإضاءة ∝ 1 ÷ المسافة²', 10.5, 500, SLATE, 'right'))
    b.append(f'<line x1="{lx}" y1="96" x2="{lx+26}" y2="96" stroke="{COPPER_INK}" stroke-width="2.2" stroke-dasharray="6 4"/>')
    b.append(T(596, 100, 'سوفت بوكس دائري', 11, 700, COPPER_INK, 'right'))
    b.append(T(596, 116, 'قطره 60 سم (محسوب)', 10.5, 500, SLATE, 'right'))
    b.append(T(596, 150, 'الفرق كبير قرب', 10.5, 600, INK, 'right'))
    b.append(T(596, 165, 'المصدر الكبير ويختفي', 10.5, 600, INK, 'right'))
    b.append(T(596, 180, 'تقريبًا بعد نحو', 10.5, 600, INK, 'right'))
    b.append(T(596, 195, '5 أضعاف قطره', 10.5, 600, INK, 'right'))
    return svg(W, H, ''.join(b), 'منحنى قانون التربيع العكسي لمصدر نقطي مقارنة بسوفت بوكس قطره 60 سم')


def kelvin():
    W, H = 600, 256
    stops = [(1800, '#FF7E00'), (2700, '#FFA757'), (3200, '#FFBB78'), (4000, '#FFD1A3'), (5000, '#FFE4CE'), (5600, '#FFEEDE'), (6500, '#FFF9FD'), (8000, '#E3E9FF'), (10000, '#CCDBFF')]
    k0, k1, x0, x1 = 1800, 10000, 20, 580
    X = lambda k: x0 + (k - k0) / (k1 - k0) * (x1 - x0)
    g = ''.join(f'<stop offset="{(k-k0)/(k1-k0):.3f}" stop-color="{c}"/>' for k, c in stops)
    b = [f'<defs><linearGradient id="kg" x1="0" x2="1">{g}</linearGradient></defs>',
         f'<rect x="{x0}" y="40" width="{x1-x0}" height="30" rx="5" fill="url(#kg)" stroke="{RULE}"/>']
    marks = [(1900, 'شمعة', '≈1900K'), (3200, 'مصباح تنغستن', '≈3200K'), (5600, 'ضوء نهار مرجعي', '≈5600K'), (6500, 'سماء ملبدة', '≈6500K'), (8500, 'ظل في يوم مشمس', '7500–9000K+')]
    for i, (k, lbl, val) in enumerate(marks):
        x = X(k)
        b.append(f'<line x1="{x:.1f}" y1="36" x2="{x:.1f}" y2="76" stroke="{INK}" stroke-width="1.4"/>')
        dy = 0 if i % 2 == 0 else 30
        b.append(f'<line x1="{x:.1f}" y1="76" x2="{x:.1f}" y2="{80+dy}" stroke="{RULE}"/>')
        b.append(T(x, 92 + dy, lbl, 11, 700, INK, 'left' if i == 0 else 'center'))
        b.append(T(x, 106 + dy, val, 10, 600, SLATE, 'left' if i == 0 else 'center'))
    b.append(T(x0, 26, 'أدفأ (برتقالي)', 11, 600, COPPER_INK, 'left'))
    b.append(T(x1, 26, 'أبرد (أزرق)', 11, 600, CYAN_INK, 'right'))
    # same grey card lit by ~5600K daylight, three camera WB settings
    cards = [('#B9C7E6', 'ضبط الكاميرا 3200K', 'الصورة تميل للأزرق'), ('#C8C8C6', 'ضبط الكاميرا 5600K', 'رمادي محايد'), ('#E2C49C', 'ضبط الكاميرا 8000K', 'الصورة تميل للبرتقالي')]
    for i, (c, a, s) in enumerate(cards):
        x = 412 - i * 196
        b.append(f'<rect x="{x}" y="148" width="168" height="52" rx="6" fill="{c}" stroke="{RULE}"/>')
        b.append(f'<rect x="{x+12}" y="160" width="28" height="28" rx="3" fill="{WHITE}" opacity=".55"/>')
        b.append(T(x + 160, 170, a, 11, 700, INK, 'right'))
        b.append(T(x + 160, 188, s, 10.5, 500, INK, 'right'))
    b.append(T(300, 228, 'البطاقات: بطاقة رمادية واحدة تحت ضوء نهار تقريبًا 5600K، وثلاثة إعدادات لتوازن الأبيض (محاكاة توضيحية)', 11, 500, SLATE))
    b.append(T(300, 247, 'القاعدة: إذا ضبطت الكاميرا على رقم أقل من حرارة الضوء الفعلية تميل الصورة للأزرق، وأعلى منها تميل للبرتقالي', 11, 600, INK))
    return svg(W, H, ''.join(b), 'مقياس حرارة اللون بالكلفن وأثر ضبط توازن الأبيض على بطاقة رمادية')


# ---------------------------------------------------------------- audio
def polar_patterns():
    W, H = 600, 230
    pats = [('شامل الاتجاه', 'Omni', 1.0, 'لا يرفض الجوانب'), ('قلبي', 'Cardioid', 0.5, 'أقل التقاط عند 180°'),
            ('فوق القلبي', 'Supercardioid', 0.366, 'أقل التقاط ≈ 126°'), ('ثنائي الاتجاه', 'Figure-8', 0.0, 'أقل التقاط عند 90°')]
    b = []
    for i, (ar, en, a, null) in enumerate(pats):
        cx, cy, R = 527 - i * 151, 98, 56
        for rr in (0.5, 1.0):
            b.append(f'<circle cx="{cx}" cy="{cy}" r="{R*rr}" fill="none" stroke="{RULE}" stroke-width="{1 if rr==1 else .7}"/>')
        b.append(f'<line x1="{cx}" y1="{cy-R-6}" x2="{cx}" y2="{cy+R+6}" stroke="{RULE}" stroke-width=".7"/><line x1="{cx-R-6}" y1="{cy}" x2="{cx+R+6}" y2="{cy}" stroke="{RULE}" stroke-width=".7"/>')
        front, rear = [], []
        for k in range(0, 361):
            th = math.radians(k)
            v = a + (1 - a) * math.cos(th)
            x, y = cx + R * abs(v) * math.sin(th), cy - R * abs(v) * math.cos(th)
            (front if v >= 0 else rear).append((k, f'{x:.1f},{y:.1f}'))
        def runs(seq):
            out, cur, last = [], [], None
            for k, p in seq:
                if last is not None and k != last + 1:
                    out.append(cur); cur = []
                cur.append(p); last = k
            if cur: out.append(cur)
            return out
        for r_ in runs(front):
            b.append(f'<polyline points="{" ".join(r_)}" fill="none" stroke="{CYAN_INK}" stroke-width="2.4"/>')
        for r_ in runs(rear):
            b.append(f'<polyline points="{" ".join(r_)}" fill="none" stroke="{COPPER_INK}" stroke-width="1.8" stroke-dasharray="4 3"/>')
        b.append(f'<rect x="{cx-4}" y="{cy-12}" width="8" height="20" rx="4" fill="{INK}"/>')
        b.append(T(cx, cy - R - 12, '0° الأمام', 10, 600, SLATE))
        b.append(T(cx, 182, ar, 12.5, 700, INK))
        b.append(T(cx, 197, en, 10.5, 600, SLATE))
        b.append(T(cx, 214, null, 10.5, 600, COPPER_INK))
    return svg(W, H, ''.join(b), 'أنماط التقاط الميكروفون محسوبة: شامل، قلبي، فوق القلبي، ثنائي الاتجاه')


def signal_chain():
    W, H = 600, 312
    b = [arrow_defs(INK, 'sc')]
    row1 = [('مصدر الصوت', 'الفم والأداء'), ('الغرفة', 'صدى وضجيج'), ('الميكروفون', 'النوع والمسافة'), ('الكسب Gain', 'مستوى الإدخال'), ('التسجيل', 'WAV · 24-bit')]
    row2 = [('تنظيف محافظ', 'ضجيج ثابت فقط'), ('High-pass', 'حوالي 80 Hz للكلام'), ('EQ تصحيحي', 'خفض قبل الرفع'), ('ضغط Compressor', '2:1 إلى 4:1 كبداية'), ('مستوى التسليم', 'LUFS وTrue Peak')]
    # The chain runs in reading direction: right to left in Arabic, mirrored for English and Russian.
    m = LANG != 'ar'
    fx = (lambda x, w=0: W - x - w) if m else (lambda x, w=0: x)
    def row(items, y, title, color):
        bw, gap = 102, 10
        b.append(T(fx(584), y - 12, title, 11.5, 700, color, 'left' if m else 'right'))
        for i, (a, s) in enumerate(items):
            x = fx(584 - (i + 1) * bw - i * gap, bw)
            b.append(f'<rect x="{x:.1f}" y="{y}" width="{bw}" height="54" rx="6" fill="{WHITE}" stroke="{color}" stroke-width="1.6"/>')
            b.append(T(x + bw / 2, y + 23, a, 11.5, 700, INK))
            b.append(T(x + bw / 2, y + 41, s, 9.6, 500, SLATE))
            if i:
                x1, x2 = (x - gap + 1, x - 1.5) if m else (x + bw + gap - 1, x + bw + 1.5)
                b.append(f'<line x1="{x1:.1f}" y1="{y+27}" x2="{x2:.1f}" y2="{y+27}" stroke="{INK}" stroke-width="1.4" marker-end="url(#sc)"/>')
        return 584 - len(items) * bw - (len(items) - 1) * gap
    endx = row(row1, 30, 'أثناء التسجيل: ما لا يمكن إصلاحه لاحقًا بسهولة', NAVY)
    row(row2, 138, 'بعد التسجيل: معالجة بالترتيب وباعتدال', COPPER_INK)
    b.append(f'<path d="M{fx(endx+51):.1f},84 v16 H{fx(594)} V165 H{fx(587)}" fill="none" stroke="{INK}" stroke-width="1.4" marker-end="url(#sc)"/>')
    # level meter (LTR by convention: dBFS scales run to 0 on the right)
    y, x0, x1 = 244, 40, 560
    X = lambda db: x0 + (db + 48) / 48 * (x1 - x0)
    b.append(f'<rect x="{x0}" y="{y}" width="{x1-x0}" height="16" rx="3" fill="{PAPER2}"/>')
    b.append(f'<rect x="{X(-18):.1f}" y="{y}" width="{X(-6)-X(-18):.1f}" height="16" fill="{CYAN}" opacity=".55"/>')
    b.append(f'<rect x="{X(-6):.1f}" y="{y}" width="{X(-1)-X(-6):.1f}" height="16" fill="{COPPER}" opacity=".7"/>')
    b.append(f'<rect x="{X(-1):.1f}" y="{y}" width="{X(0)-X(-1):.1f}" height="16" fill="{WARN}"/>')
    for db in (-48, -36, -24, -18, -12, -6, 0):
        b.append(f'<line x1="{X(db):.1f}" y1="{y+16}" x2="{X(db):.1f}" y2="{y+21}" stroke="{SLATE}"/>')
        b.append(T(X(db), y + 33, f'{db} dBFS'.replace('-', '−'), 9.6, 600, SLATE))
    b.append(T((X(-18) + X(-6)) / 2, y - 7, 'ذروات الكلام هنا', 10.5, 700, CYAN_INK))
    b.append(T(X(0), y - 7, 'قص لا يُصلح', 10.5, 700, WARN, 'right'))
    b.append(T(300, 305, 'مقياس الذروة في برنامج التسجيل: نطاق انطلاق شائع للكلام، وليس رقمًا إلزاميًا لكل جهاز', 10.5, 500, SLATE))
    return svg(W, H, ''.join(b), 'سلسلة الإشارة الصوتية من الفم إلى ملف التسليم، ومقياس المستوى المقترح أثناء التسجيل')


# ---------------------------------------------------------------- story & editing
def axis_180():
    W, H = 290, 268
    b = []
    ax, ay, bx, by = 200, 112, 90, 112
    b.append(f'<path d="M0,112 L290,112 L290,268 L0,268 Z" fill="{CYAN}" opacity=".09"/>')
    b.append(f'<line x1="0" y1="112" x2="290" y2="112" stroke="{COPPER_INK}" stroke-width="1.8" stroke-dasharray="7 5"/>')
    b.append(T(286, 104, 'محور الحوار (الخط)', 10.5, 700, COPPER_INK, 'right'))
    for x, y, n in ((ax, ay, 'أ'), (bx, by, 'ب')):
        b.append(f'<circle cx="{x}" cy="{y}" r="15" fill="{NAVY}"/>')
        b.append(T(x, y + 5, n, 12, 700, WHITE))
    def cam(x, y, ang, lbl, ok):
        col = INK if ok else WARN
        s = f'<g transform="translate({x},{y}) rotate({ang})"><rect x="-11" y="-8" width="22" height="16" rx="2" fill="{col}"/><path d="M11,-5 L21,-10 L21,10 L11,5 Z" fill="{col}"/></g>'
        return s + T(x, y + (30 if y > 112 else -20), lbl, 10.5, 700, col)
    b.append(cam(70, 196, -55, '1', True))
    b.append(cam(222, 196, -125, '2', True))
    b.append(cam(145, 214, -90, 'واسعة', True))
    b.append(cam(150, 40, 90, '3 ✕ يعبر الخط', False))
    b.append(T(145, 262, 'الكاميرات 1 و2 تحافظ على اتجاه النظر', 10.5, 600, CYAN_INK))
    return svg(W, H, ''.join(b), 'قاعدة 180 درجة: الكاميرات في جهة واحدة من محور الحوار')


def shot_sizes():
    W, H = 290, 300
    b = []
    fx = 205
    # simple original figure
    b.append(f'<circle cx="{fx}" cy="52" r="20" fill="{NAVY}"/>')
    b.append(f'<path d="M{fx-9},70 h18 v10 h-18 z" fill="{NAVY}"/>')
    b.append(f'<path d="M{fx-38},86 Q{fx},74 {fx+38},86 L{fx+34},170 L{fx-34},170 Z" fill="{NAVY}"/>')
    b.append(f'<path d="M{fx-30},170 h26 l-2,108 h-20 z M{fx+4},170 h26 l-4,108 h-20 z" fill="{NAVY}"/>')
    b.append(f'<circle cx="{fx-7}" cy="49" r="2.2" fill="{IVORY}"/><circle cx="{fx+7}" cy="49" r="2.2" fill="{IVORY}"/>')
    sizes = [(58, 'ECU', 'قريبة جدًا: العينان'), (82, 'CU', 'قريبة: الوجه'), (118, 'MCU', 'متوسطة قريبة: الصدر'),
             (160, 'MS', 'متوسطة: الخصر'), (226, 'MLS', 'متوسطة واسعة: الركبتان'), (290, 'WS', 'واسعة: الجسم والمكان')]
    for y, en, ar in sizes:
        b.append(f'<line x1="{fx-58}" y1="{y}" x2="{fx+62}" y2="{y}" stroke="{COPPER_INK}" stroke-width="1.3" stroke-dasharray="4 3"/>')
        b.append(T(fx - 64, y + 4, en, 10.5, 800, COPPER_INK, 'right'))
        b.append(T(110, y + 4, ar, 11, 600, INK, 'right'))
    b.append(T(110, 14, 'الحافة السفلية للإطار ←', 10.5, 600, SLATE, 'right'))
    return svg(W, H, ''.join(b), 'أحجام اللقطات من القريبة جدًا إلى الواسعة بحسب موضع الحافة السفلية للإطار')


def cut_timelines():
    W, H = 600, 330
    b = [arrow_defs(SLATE, 'ct')]
    x0, x1 = 120, 590
    rows = [('قطع مباشر', 'Straight cut', 0, 0), ('J-cut', 'صوت ب يسبق صورتها', -70, 0), ('L-cut', 'صوت أ يستمر فوق صورة ب', 0, 70)]
    cut = 355
    for i, (t, s, a_off, l_off) in enumerate(rows):
        y = 18 + i * 74
        b.append(T(108, y + 18, t, 12, 800, INK, 'right'))
        if tr(s) != tr(t):  # in English the gloss would repeat the title
            b.append(T(108, y + 35, s, 10, 500, SLATE, 'right'))
        b.append(f'<rect x="{x0+8}" y="{y+4}" width="{cut-x0-8}" height="20" rx="3" fill="{NAVY}"/><rect x="{cut}" y="{y+4}" width="{x1-cut}" height="20" rx="3" fill="{COPPER}"/>')
        ac = cut + a_off + l_off
        b.append(f'<rect x="{x0+8}" y="{y+32}" width="{ac-x0-8}" height="18" rx="3" fill="{NAVY}" opacity=".55"/><rect x="{ac}" y="{y+32}" width="{x1-ac}" height="18" rx="3" fill="{COPPER}" opacity=".6"/>')
        b.append(T(x0 + 20, y + 18, 'صورة أ', 10, 700, WHITE, 'left'))
        b.append(T(x1 - 10, y + 18, 'صورة ب', 10, 700, INK, 'right'))
        if ac != cut:
            b.append(f'<line x1="{cut}" y1="{y}" x2="{cut}" y2="{y+54}" stroke="{INK}" stroke-width="1.2" stroke-dasharray="2 2"/>')
    # cut on action
    y = 240
    b.append(T(108, y + 18, 'Cut on action', 11.5, 800, INK, 'right'))
    b.append(T(108, y + 35, 'القطع داخل الحركة', 10, 500, SLATE, 'right'))
    b.append(f'<rect x="{x0+8}" y="{y+4}" width="{cut-x0-8}" height="20" rx="3" fill="{NAVY}"/><rect x="{cut}" y="{y+4}" width="{x1-cut}" height="20" rx="3" fill="{COPPER}"/>')
    b.append(T(x0 + 20, y + 18, 'واسعة: اليد تمسك المقبض', 10, 700, WHITE, 'left'))
    b.append(T(x1 - 10, y + 18, 'قريبة: الباب ينفتح', 10, 700, INK, 'right'))
    b.append(f'<rect x="{cut-62}" y="{y+30}" width="124" height="14" rx="7" fill="{CYAN}" opacity=".5"/>')
    b.append(T(cut, y + 41, 'الحركة نفسها مستمرة', 10, 700, INK))
    b.append(f'<line x1="{cut}" y1="{y}" x2="{cut}" y2="{y+28}" stroke="{WARN}" stroke-width="2.4"/>')
    b.append(f'<line x1="{x0+8}" y1="{H-12}" x2="{x1}" y2="{H-12}" stroke="{SLATE}" stroke-width="1.2" marker-end="url(#ct)"/>')
    b.append(T(x1, H - 18, 'الشريط العلوي: الصورة · السفلي: الصوت · الزمن يتجه من اليسار إلى اليمين كما في برامج المونتاج', 10, 600, SLATE, 'right'))
    return svg(W, H, ''.join(b), 'مقارنة على الخط الزمني بين القطع المباشر وJ-cut وL-cut والقطع داخل الحركة')


def color_pipeline():
    W, H = 600, 210
    b = [arrow_defs(INK, 'cp')]
    nodes = [('المصدر', 'Rec.709 أو Log', PAPER2), ('1 التعريض', 'السواد والبياض', WHITE), ('2 توازن الأبيض', 'رمادي محايد', WHITE),
             ('3 مطابقة', 'اللقطات معًا', WHITE), ('4 تعديل ثانوي', 'البشرة، السماء', '#FFF4E2'), ('5 المظهر', 'Look إبداعي', '#FFF4E2'), ('التسليم', 'Rec.709 · 2.4', PAPER2)]
    bw, gap, x = 74, 10, 8
    for i, (a, s, f) in enumerate(nodes):
        b.append(f'<rect x="{x}" y="70" width="{bw}" height="58" rx="7" fill="{f}" stroke="{INK}" stroke-width="1.3"/>')
        b.append(T(x + bw / 2, 95, a, 10.8, 700, INK))
        b.append(T(x + bw / 2, 113, s, 9.4, 500, SLATE))
        if i:
            b.append(f'<line x1="{x-gap+1}" y1="99" x2="{x-1.5}" y2="99" stroke="{INK}" stroke-width="1.3" marker-end="url(#cp)"/>')
        x += bw + gap
    xa, xb = 8 + bw + gap, 8 + 4 * (bw + gap) - gap
    b.append(f'<path d="M{xa},58 v-10 H{xb} v10" fill="none" stroke="{CYAN_INK}" stroke-width="1.6"/>')
    b.append(T((xa + xb) / 2, 38, 'تصحيح تقني Color correction: يجعل اللقطات صحيحة ومتسقة', 11, 700, CYAN_INK))
    xc, xd = 8 + 4 * (bw + gap), 8 + 6 * (bw + gap) - gap
    b.append(f'<path d="M{xc},140 v10 H{xd} v-10" fill="none" stroke="{COPPER_INK}" stroke-width="1.6"/>')
    b.append(T((xc + xd) / 2, 168, 'تلوين إبداعي Grading', 11, 700, COPPER_INK))
    b.append(T((xc + xd) / 2, 184, 'يخدم الشعور والقصة', 10.5, 500, COPPER_INK))
    b.append(T(8, 196, 'ترتيب العقد يُقرأ من اليسار إلى اليمين كما في DaVinci Resolve', 10, 600, SLATE, 'left'))
    return svg(W, H, ''.join(b), 'ترتيب التصحيح التقني ثم التلوين الإبداعي في سلسلة عقد')


# ---------------------------------------------------------------- growth & systems
def hook_retention():
    W, H = 600, 270
    x0, x1, y0, y1 = 40, 586, 96, 214
    X = lambda s: x0 + s / 30 * (x1 - x0)
    b = [arrow_defs(SLATE, 'hr')]
    beats = [(0, 1.5, 'صورة', COPPER), (1.5, 3, 'وعد', '#F0C9A0'), (3, 8, 'سياق المشكلة', '#CFE9EE'), (8, 15, 'الدليل', CYAN), (15, 25, 'الحل خطوة خطوة', '#CFE9EE'), (25, 30, 'خلاصة + دعوة', '#F0C9A0')]
    for a, z, l, c in beats:
        b.append(f'<rect x="{X(a):.1f}" y="44" width="{X(z)-X(a)-2:.1f}" height="30" rx="4" fill="{c}"/>')
        b.append(T((X(a) + X(z)) / 2, 64, l, 10.5 if z - a > 2 else 9.4, 700, INK))
    b.append(T(X(0), 32, f'أول {ltr("1.5")} ثانية: حركة أو نتيجة مرئية', 10.5, 700, COPPER_INK, 'left'))
    b.append(T(X(30), 32, 'تقسيم مقترح لريل 30 ثانية', 10.5, 700, INK, 'right'))
    for v in (0, 50, 100):
        y = y1 - v / 100 * (y1 - y0)
        b.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{RULE}" stroke-width=".8"/>')
        b.append(T(x0 - 6, y + 4, f'{v}%', 9.5, 600, SLATE, 'right'))
    curve = [(0, 100), (1.5, 88), (3, 74), (5, 64), (8, 52), (8.5, 51), (12, 48), (15, 46), (18, 44), (22, 39), (25, 37), (30, 31)]
    pts = ' '.join(f'{X(s):.1f},{y1-v/100*(y1-y0):.1f}' for s, v in curve)
    b.append(f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="2.2"/>')
    for s, v, l in ((3, 74, 'هبوط حاد إن تأخر الوعد'), (22, 39, 'هبوط إن تكررت الفكرة')):
        y = y1 - v / 100 * (y1 - y0)
        b.append(f'<circle cx="{X(s):.1f}" cy="{y:.1f}" r="4" fill="{WARN}"/>')
        b.append(T(X(s) + 8, y - 8, l, 10.5, 700, WARN, 'left'))
    for s in range(0, 31, 5):
        b.append(T(X(s), y1 + 16, f'{s}s', 9.5, 600, SLATE))
    b.append(T(300, 252, 'منحنى احتفاظ توضيحي مرسوم لشرح طريقة القراءة — ليس بيانات من منصة أو حسابًا حقيقيًا', 10.5, 600, COPPER_INK))
    return svg(W, H, ''.join(b), 'تقسيم زمني مقترح لريل مدته 30 ثانية ومنحنى احتفاظ توضيحي')


def prompt_anatomy():
    W, H = 600, 290
    b = [arrow_defs(INK, 'pa')]
    parts = [('R', 'الدور', 'محرر ريلز تعليمي يكتب بعربية بسيطة', NAVY), ('C', 'السياق', 'الجمهور، المادة المصورة، ما ثبت وما لم يثبت', '#24405F'),
             ('T', 'المهمة', 'فعل واحد واضح: اكتب 3 افتتاحيات', '#2E5778'), ('F', 'الشكل', 'جدول: النص | اللقطة | الدليل', '#356D8C'), ('Q', 'معيار الجودة', 'لا أرقام غير موجودة في المدخلات', COPPER_INK)]
    for i, (k, a, s, c) in enumerate(parts):
        y = 18 + i * 52
        b.append(f'<rect x="300" y="{y}" width="292" height="44" rx="6" fill="{c}"/>')
        b.append(f'<text x="572" y="{y+30}" font-family="{LAT}" font-size="20" font-weight="800" fill="{COPPER if c!=COPPER_INK else IVORY}" text-anchor="middle">{k}</text>')
        b.append(T(548, y + 19, a, 12, 700, WHITE, 'right'))
        b.append(T(548, y + 36, s, 10, 500, '#DCE3EC', 'right'))
    cx, cy, r = 140, 150, 80
    steps = ['اكتب', 'اختبر', 'قيّم', 'عدّل', 'سجّل']
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{RULE}" stroke-width="10"/>')
    for i, s in enumerate(steps):
        a = math.radians(-90 + i * 72)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        a2 = math.radians(-90 + i * 72 + 52)
        b.append(f'<path d="M{cx + r*math.cos(a + .32):.1f},{cy + r*math.sin(a + .32):.1f} A{r},{r} 0 0 1 {cx + r*math.cos(a2):.1f},{cy + r*math.sin(a2):.1f}" fill="none" stroke="{INK}" stroke-width="1.6" marker-end="url(#pa)"/>')
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="{IVORY}" stroke="{INK}" stroke-width="1.6"/>')
        b.append(f'<text x="{x:.1f}" y="{y+5:.1f}" font-family="{LAT}" font-size="13" font-weight="800" fill="{INK}" text-anchor="middle">{i+1}</text>')
        if i == 0: b.append(T(x, y - 22, s, 11.5, 700, INK))
        elif i in (2, 3): b.append(T(x, y + 34, s, 11.5, 700, INK))
        elif i == 1: b.append(T(x + 21, y + 5, s, 11.5, 700, INK, 'left'))
        else: b.append(T(x - 21, y + 5, s, 11.5, 700, INK, 'right'))
    b.append(T(cx, cy - 4, 'حلقة', 13, 700, INK))
    b.append(T(cx, cy + 14, 'التحسين', 13, 700, INK))
    return svg(W, H, ''.join(b), 'تشريح البرومبت بصيغة R-C-T-F-Q وحلقة تحسينه')


def analytics_funnel():
    W, H = 600, 320
    stages = [('الظهور', 'Impressions / Reach', 'هل وصل الفيديو إلى أحد؟', 'الموضوع، الغلاف، توقيت النشر'),
              ('بدء المشاهدة', 'Plays · أول 3 ثوانٍ', 'هل أوقفت البداية التمرير؟', 'الصورة الأولى والجملة الأولى'),
              ('الاحتفاظ', 'Avg. watch · Retention', 'هل وفى الفيديو بالوعد؟', 'موضع الدليل وطول المقدمة'),
              ('التفاعل المفيد', 'Saves · Shares', 'هل كانت المعلومة قابلة للاستخدام؟', 'خطوات أوضح، ملخص، مثال'),
              ('العلاقة', 'Profile visits · Follows', 'هل يريد المشاهد المزيد منك؟', 'سلسلة واضحة ووعد الحساب'),
              ('العمل', 'Clicks · Leads · Sales', 'هل العرض مناسب لهذا الجمهور؟', 'صفحة صادقة ودعوة واحدة')]
    b = []
    cx = 300
    b.append(T(560, 16, 'ماذا يخبرك؟', 11, 700, CYAN_INK, 'right'))
    b.append(T(40, 16, 'ماذا تجرّب؟', 11, 700, COPPER_INK, 'left'))
    for i, (a, en, q, t) in enumerate(stages):
        y = 26 + i * 48
        w0, w1 = 276 - i * 24, 276 - (i + 1) * 24
        shade = ['#16263E', '#1D3150', '#243D61', '#2C4A73', '#355785', '#3F6597'][i]
        b.append(f'<path d="M{cx-w0/2},{y} L{cx+w0/2},{y} L{cx+w1/2},{y+42} L{cx-w1/2},{y+42} Z" fill="{shade}"/>')
        b.append(T(cx, y + 19, a, 12, 700, WHITE))
        b.append(T(cx, y + 34, en, 9.4, 600, '#C9D4E3'))
        b.append(T(590, y + 26, q, 10.5, 600, INK, 'right'))
        b.append(T(10, y + 26, t, 10.5, 500, SLATE, 'left'))
    return svg(W, H, ''.join(b), 'قمع تحليل المحتوى من الظهور إلى العمل، مع سؤال كل مرحلة وما يمكن تجربته')


ALL = {k: v for k, v in globals().items() if callable(v) and k not in ('T', 'svg', 'arrow_defs', 'escape', 'ltr', 'tr', 'render') and not k.startswith('_')}


# ---------------------------------------------------------------- chapter opener art (decorative, dark pages)
def opener_exposure():
    b = []
    cx, cy = 110, 300
    for i, r in enumerate((430, 360, 290, 220)):
        b.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{COPPER if i == 0 else "#FFFFFF"}" stroke-opacity="{.5 if i == 0 else .06 + i*.02}" stroke-width="{2 if i == 0 else 1.2}"/>')
    n, r = 9, 150
    v = [(cx + r * math.cos(math.radians(12 + i * 40)), cy + r * math.sin(math.radians(12 + i * 40))) for i in range(n)]
    b.append(f'<polygon points="{" ".join(f"{x:.0f},{y:.0f}" for x, y in v)}" fill="none" stroke="{CYAN}" stroke-opacity=".7" stroke-width="2"/>')
    for i in range(n):
        x, y = v[i]; a = math.radians(12 + i * 40 + 70)
        b.append(f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x + 300*math.cos(a):.0f}" y2="{y + 300*math.sin(a):.0f}" stroke="#FFFFFF" stroke-opacity=".12"/>')
    return f'<svg class="art" viewBox="0 0 600 850" preserveAspectRatio="xMidYMid slice" aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%">{"".join(b)}</svg>'


def opener_light():
    b = []
    kx, ky = 70, 170
    for f in (1, 1.41, 2, 2.83, 4):
        r = 120 * f
        b.append(f'<circle cx="{kx}" cy="{ky}" r="{r:.0f}" fill="none" stroke="{COPPER}" stroke-opacity="{.55 if f == 1 else .18}" stroke-width="1.6" stroke-dasharray="{"0" if f == 1 else "6 6"}"/>')
    b.append(f'<path d="M{kx},{ky} L520,600 L380,700 Z" fill="#FFF4E2" fill-opacity=".06"/>')
    b.append(f'<rect x="{kx-40}" y="{ky-10}" width="80" height="20" rx="4" transform="rotate(-50 {kx} {ky})" fill="#FFF4E2" fill-opacity=".85"/>')
    return f'<svg class="art" viewBox="0 0 600 850" preserveAspectRatio="xMidYMid slice" aria-hidden="true" style="position:absolute;inset:0;width:100%;height:100%">{"".join(b)}</svg>'


ALL.update(opener_exposure=opener_exposure, opener_light=opener_light)
