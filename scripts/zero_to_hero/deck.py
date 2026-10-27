"""Interactive presentation for the From Zero to Hero edition on /products/creator-guide/.

python scripts/zero_to_hero/deck.py  ->  assets/products/zth/deck-copy.js and assets/products/zth/diagrams/*.svg
scripts/build_product_pages.py imports deck_html() for the markup.

One slide per manuscript unit, plus cover, method, course map, the prompt library, the toolkit and the edition slide.
The chapter map (with manuscript pages) is docs/zero-to-hero/PRESENTATION_MAP.md. Diagrams are the book's own SVGs,
drawn per language by diagrams.render() and loaded by assets/brand/zth-deck.js when their slide opens.
"""
import json
import pathlib
import sys
from html import escape as e

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import diagrams  # noqa: E402
from deck_copy import UNITS, UI  # noqa: E402

LANGS = ('ar', 'en', 'ru')
OUT = ROOT / 'assets/products/zth'
# Book diagram per unit (index 0 = unit 01); None = an HTML figure drawn from the unit's own text.
UNIT_FIG = ['episode', 'exposure_stops', 'shot_sizes', 'hard_soft', 'signal_chain', 'axis_180', 'cut_timelines',
            'color_pipeline', 'hook_retention', 'pipeline', 'trust', 'weeks']
HTML_FIGS = {'episode', 'pipeline', 'trust', 'weeks'}
DIAGRAMS = sorted({f for f in UNIT_FIG if f not in HTML_FIGS} | {'prompt_anatomy', 'analytics_funnel'})
EN = {**UI['en'], 'u': UNITS['en']}
SLIDES = ['cover', 'how', 'map'] + [f'u{i:02d}' for i in range(1, 13)] + ['prompts', 'toolkit', 'edition']
N = len(SLIDES)


def get(path):
    v = EN
    for k in path.split('.'):
        v = v[int(k)] if isinstance(v, (list, tuple)) else v[k]
    return v


def t(path, tag='span', cls='', attrs=''):
    c = f' class="{cls}"' if cls else ''
    return f'<{tag}{c} data-t="{path}"{attrs}>{e(get(path))}</{tag}>'


def num(n):
    return f'<span class="zd-num" dir="ltr">{n:02d}</span>'


def slide(n, kind, body, label_path):
    hidden = '' if n == 1 else ' hidden'
    return (f'<article class="zd-slide zd-{kind}" data-slide="{n}" aria-roledescription="slide" '
            f'aria-labelledby="zd{n}-title"{hidden}>{body}</article>')


def h3(n, path):
    return t(path, 'h3', '', f' id="zd{n}-title" tabindex="-1"')


def figure(name, cap_path=None, body=None):
    inner = body if body is not None else f'<div class="zd-svg" data-diagram="{name}" role="presentation"></div>'
    # a book diagram's own title (its alt text, translated) becomes the caption once the SVG is loaded
    extra = t(cap_path, 'span') if cap_path else ('' if body is not None else '<span data-fig-title></span>')
    cap = f'<figcaption>{t("figure", "span", "zd-label")}{extra}</figcaption>'
    return f'<figure class="zd-fig zd-fig-{name}">{inner}{cap}</figure>'


def html_fig(name):
    if name == 'episode':
        return '<ol class="zd-flow zd-flow-v">' + ''.join(f'<li>{num(i + 1)}{t(f"episode.{i}")}</li>' for i in range(4)) + '</ol>'
    if name == 'pipeline':
        return '<ol class="zd-chain">' + ''.join(f'<li>{t(f"pipeline.{i}")}</li>' for i in range(11)) + '</ol>'
    if name == 'trust':
        return '<ul class="zd-tiles">' + ''.join(f'<li>{t(f"trust.{i}.0", "b")}{t(f"trust.{i}.1")}</li>' for i in range(4)) + '</ul>'
    if name == 'weeks':
        return '<ol class="zd-weeks">' + ''.join(f'<li>{t(f"weeks.{i}.0", "b")}{t(f"weeks.{i}.1")}</li>' for i in range(4)) + '</ol>'
    raise KeyError(name)


CAPTIONS = {'episode': 'episodeCap', 'pipeline': 'pipelineCap', 'trust': 'trustCap', 'weeks': 'weeksCap'}


def cover_img(cls, lang='en', size='(max-width: 760px) 60vw, 360px'):
    srcs = ''.join(f' data-src-{l}="/assets/products/cover-v3-{l}.webp"' for l in LANGS)
    return (f'<img class="{cls}" src="/assets/products/cover-v3-{lang}.webp"{srcs} width="1000" height="1420" '
            f'sizes="{size}" alt="{e(EN["deckTitle"])}" loading="lazy">')


def s_cover(n):
    facts = ''.join(f'<li>{t(f"coverFacts.{i}")}</li>' for i in range(4))
    body = (f'<div class="zd-cover-art">{cover_img("zd-cover-img")}</div><div class="zd-copy">'
            f'{t("coverKicker", "p", "zd-kicker")}<h3 id="zd{n}-title" tabindex="-1" class="zd-mark" dir="ltr">FROM ZERO <em>TO HERO</em></h3>'
            f'{t("coverSub", "p", "zd-sub")}{t("coverLead", "p", "zd-lead")}<ul class="zd-facts">{facts}</ul>'
            f'<div class="zd-actions"><button class="btn primary" type="button" data-goto="2">{t("start")}<span aria-hidden="true" class="zd-arrow">→</span></button>'
            f'{t("by", "span", "zd-by")}</div></div>')
    return slide(n, 'cover', body, 'deckTitle')


def s_how(n):
    flow = '<ol class="zd-flow">' + ''.join(f'<li>{num(i + 1)}{t(f"howFlow.{i}")}</li>' for i in range(5)) + '</ol>'
    levels = '<ul class="zd-levels">' + ''.join(f'<li><i aria-hidden="true"></i>{t(f"levels.{i}.0", "b")}{t(f"levels.{i}.1")}</li>' for i in range(3)) + '</ul>'
    body = (f'<div class="zd-copy zd-wide">{t("howKicker", "p", "zd-kicker")}{h3(n, "howTitle")}{t("howLead", "p", "zd-lead")}{flow}{levels}'
            f'<aside class="zd-ex">{t("progress", "p", "zd-label")}{t("progressText", "p")}</aside></div>')
    return slide(n, 'how', body, 'howTitle')


def s_map(n):
    units = ''.join(f'<li><button type="button" data-goto="{i + 4}">{num(i + 1)}<span><small data-t="u.{i}.track">{e(get(f"u.{i}.track"))}</small>'
                    f'{t(f"u.{i}.title", "b")}</span></button></li>' for i in range(12))
    lib = ''.join(f'<li><button type="button" data-goto="{16 if i == 0 else 17}">{t(f"libItems.{i}")}</button></li>' for i in range(9))
    body = (f'<div class="zd-copy zd-wide">{t("mapKicker", "p", "zd-kicker")}{h3(n, "mapTitle")}{t("mapLead", "p", "zd-lead")}'
            f'<ol class="zd-map" data-map>{units}</ol>{t("library", "p", "zd-label zd-lib-label")}<ul class="zd-lib">{lib}</ul></div>')
    return slide(n, 'toc', body, 'mapTitle')


def s_unit(n, i):
    pts = ''.join(f'<li>{t(f"u.{i}.points.{j}.0", "b")}{t(f"u.{i}.points.{j}.1")}</li>' for j in range(3))
    name = UNIT_FIG[i]
    fig = figure(name, CAPTIONS.get(name), html_fig(name)) if name in HTML_FIGS else figure(name)
    ex = 'progress' if i == 11 else 'exercise'
    body = (f'<div class="zd-copy"><p class="zd-kicker">{num(i + 1)}{t("unit")}<span aria-hidden="true"> · </span>{t(f"u.{i}.track")}</p>'
            f'{h3(n, f"u.{i}.title")}{t(f"u.{i}.goal", "p", "zd-lead")}<ol class="zd-points">{pts}</ol>'
            f'<aside class="zd-ex">{t(ex, "p", "zd-label")}{t(f"u.{i}.ex", "p")}</aside></div>{fig}')
    return slide(n, 'unit', body, f'u.{i}.title')


def s_prompts(n):
    pts = ''.join(f'<li>{t(f"promptPoints.{i}")}</li>' for i in range(3))
    card = (f'<div class="zd-prompt">{t("promptCardTitle", "p", "zd-label")}<p class="zd-prompt-text" data-copy-source data-t="promptText">{e(EN["promptText"])}</p>'
            f'<div class="zd-prompt-foot">{t("promptNote", "small")}<button class="btn outline zd-copy-btn" type="button" data-copy>{t("copy", "span", "", " data-copy-label")}</button></div></div>')
    body = (f'<div class="zd-copy">{t("promptKicker", "p", "zd-kicker")}{h3(n, "promptTitle")}{t("promptLead", "p", "zd-lead")}'
            f'<ul class="zd-checks">{pts}</ul>{card}</div>{figure("prompt_anatomy")}')
    return slide(n, 'library', body, 'promptTitle')


def s_toolkit(n):
    tiles = ''.join(f'<li>{t(f"tools.{i}.0", "b")}{t(f"tools.{i}.1")}</li>' for i in range(8))
    body = (f'<div class="zd-copy">{t("toolKicker", "p", "zd-kicker")}{h3(n, "toolTitle")}<ul class="zd-tools">{tiles}</ul></div>'
            f'{figure("analytics_funnel", "toolCap")}')
    return slide(n, 'toolkit', body, 'toolTitle')


def s_edition(n):
    covers = ''.join(f'<img src="/assets/products/cover-v3-{l}.webp" width="1000" height="1420" sizes="160px" alt="" lang="{l}" loading="lazy">' for l in LANGS)
    pts = ''.join(f'<li>{t(f"edPoints.{i}")}</li>' for i in range(3))
    body = (f'<div class="zd-trio" aria-hidden="true">{covers}</div><div class="zd-copy">{t("edKicker", "p", "zd-kicker")}{h3(n, "edTitle")}'
            f'{t("edLead", "p", "zd-lead")}<ul class="zd-checks">{pts}</ul><div class="zd-status">{t("edStatus", "b")}{t("edStatusNote")}</div>'
            f'<div class="zd-actions"><a class="btn primary" href="#purchase">{t("edCta")}<span aria-hidden="true">↗</span></a>'
            f'<a class="btn outline" href="mailto:ali@alialkhuzaee.com?subject=From%20Zero%20to%20Hero">{t("edAsk")}<span aria-hidden="true">↗</span></a></div></div>')
    return slide(n, 'edition', body, 'edTitle')


def deck_html():
    slides = [s_cover(1), s_how(2), s_map(3)] + [s_unit(4 + i, i) for i in range(12)] + [s_prompts(16), s_toolkit(17), s_edition(18)]
    assert len(slides) == N
    return (f'<div class="zd" data-zdeck data-total="{N}"><div class="zd-bar">'
            f'<button class="zd-btn" type="button" data-prev data-t-label="prev" aria-label="{e(EN["prev"])}"><span class="zd-arrow" aria-hidden="true">←</span></button>'
            f'<span class="zd-title" dir="ltr">FROM ZERO <em>TO HERO</em></span>'
            f'<button class="zd-maplink" type="button" data-goto="3">{t("map")}</button>'
            f'<output class="zd-count" dir="ltr" aria-live="polite" data-count>01 / {N}</output>'
            f'<button class="zd-btn" type="button" data-next data-t-label="next" aria-label="{e(EN["next"])}"><span class="zd-arrow" aria-hidden="true">→</span></button>'
            f'</div><div class="zd-progress" aria-hidden="true"><i data-progress></i></div>'
            f'<div class="zd-stage" data-stage>{"".join(slides)}</div>{t("swipe", "p", "zd-hint")}</div>')


def main():
    (OUT / 'diagrams').mkdir(parents=True, exist_ok=True)
    for name in DIAGRAMS:
        for lang in LANGS:
            (OUT / 'diagrams' / f'{name}-{lang}.svg').write_text(diagrams.render(name, lang), encoding='utf-8')
    copy = {l: {**UI[l], 'u': UNITS[l]} for l in LANGS}
    # every language must carry every key the English markup uses
    def shape(v):
        return {k: shape(x) for k, x in v.items()} if isinstance(v, dict) else [shape(x) for x in v] if isinstance(v, (list, tuple)) else None
    for l in LANGS:
        if shape(copy[l]) != shape(copy['en']):
            sys.exit(f'deck copy for {l} does not match the English structure')
    js = ('/* GENERATED by scripts/zero_to_hero/deck.py from deck_copy.py. Do not edit by hand. */\n'
          'window.ZTH_DECK=' + json.dumps(copy, ensure_ascii=False, separators=(',', ':')) + ';\n')
    (OUT / 'deck-copy.js').write_text(js, encoding='utf-8')
    print('wrote', len(DIAGRAMS) * 3, 'diagrams and deck-copy.js', len(js), 'bytes')


if __name__ == '__main__':
    main()
