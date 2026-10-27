"""fit.py PAGES_DIR OUT_DIR STATE.json: after a build, bisect each page's data-fit between a value that fits and one that overflows.

Run build.py, then fit.py, and repeat until it prints "pending 0". data-fit="0.9" on a <section class="pg"> zooms that page's content to 90 %;
the floor is 0.8. Regenerating the library pages (gen_library.py) drops their data-fit, so re-run this afterwards.
"""
import json, re, sys
from pathlib import Path
pages, out, st = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
rep = json.loads((out / 'render-report.json').read_text())['book']['overflow']
over = {x['page'] for x in rep if x['issue'] in ('frame overflow', 'escapes frame')}
used = {x['page']: x['used'] for x in rep if x['issue'] == 'fit'}
S = json.loads(st.read_text()) if st.exists() else {}
n = 1; todo = 0
for f in sorted(pages.glob('*.html')):
    parts = re.split(r'(<section class="pg" [^>]*>)', f.read_text()); changed = False
    for i in range(1, len(parts), 2):
        n += 1; k = str(n)
        tag = parts[i]; m = re.search(r' data-fit="([\d.]+)"', tag); cur = float(m.group(1)) if m else 1.0
        s = S.get(k)
        if s is None:
            if n in over: s = {'ok': 0.8, 'bad': cur}
            elif n in used and used[n] < 0.93 and cur < 1: s = {'ok': cur, 'bad': 1.01}
            else: continue
        elif n in over: s['bad'] = cur
        else: s['ok'] = cur
        S[k] = s
        if s['bad'] - s['ok'] <= 0.015: new = s['ok']
        else: new = round((s['ok'] + s['bad']) / 2, 2); todo += 1
        if new == cur: continue
        tag = re.sub(r' data-fit="[\d.]+"', '', tag)
        parts[i] = tag if new >= 1 else tag[:-1] + f' data-fit="{new}">'
        changed = True; print(n, f.name, cur, '->', new, s)
    if changed: f.write_text(''.join(parts))
st.write_text(json.dumps(S)); print('pending', todo)
