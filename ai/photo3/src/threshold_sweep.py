"""For the chosen improved head: which real coffee photos are refused, and how p(N) threshold trades refusal vs acceptance."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import improve as im
from graders import decide, CONFIG
w, ck, cg = 20, 1.0, 3.0
P_real = {}
for rid, g in im.REAL:
    hk, hg = im.train_heads(rid, w, ck, cg)
    for v in ('clean', 'phone'): P_real[(rid, v)] = im.probs5(hk, hg, im.ix[(rid, v)])
hk, hg = im.train_heads(None, w, ck, cg)
test = [i for i in np.where(im.split == 'test')[0] if im.rows[i]['id'] not in im.real_ids]
P_test = {i: im.probs5(hk, hg, i) for i in test}
for thr in (0.4, 0.5, 0.6, 0.7):
    cfg = dict(CONFIG, nThr=thr); line = []
    for v in ('clean', 'phone'):
        acc = np.mean([decide(P_real[(rid, v)], im.rows[im.ix[(rid, v)]], cfg)['kind'] == 'graded' for rid, _ in im.REAL])
        N = [i for i in test if im.lab[i] == 'N' and im.var[i] == v and im.rows[i]['id'].startswith('commons')]
        ref = np.mean([decide(P_test[i], im.rows[i], cfg)['kind'] == 'retake' for i in N])
        line.append(f'{v}: coffee graded {acc:.2f} / no-coffee refused {ref:.2f}')
    print(f'nThr={thr}:', ' | '.join(line))
print('\nreal coffee photos not graded (clean, nThr 0.5):')
for rid, g in im.REAL:
    d = decide(P_real[(rid, 'clean')], im.rows[im.ix[(rid, 'clean')]])
    if d['kind'] != 'graded': print(' ', rid[:70], g, d['kind'], d['reason'], {k: round(float(x), 2) for k, x in d['probs'].items()})
