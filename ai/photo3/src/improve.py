"""Improved CLIP head for Dure, built on the lessons of the ResNet-18 vs CLIP experiment.

Lessons -> changes
  1. Real photos matter more than the backbone   -> real green/parchment photos in training, upweighted (w_real),
                                                     clean + cheap-phone copy of each
  2. The shipped head lets 27% of look-alikes through (peanuts, kidney beans, cocoa ...)
                                                  -> ~330 reviewed real 'not coffee' photos incl. those look-alikes
  3. A synthetic-heavy 5-class head calls real beans 'not coffee'
                                                  -> split the decision: a KIND head (coffee / N / R) trained on every real
                                                     coffee photo (graded or not) and a GRADE head (A/B/C) trained on piles +
                                                     graded real photos. Output stays the same 5 numbers:
                                                     p(A)=p(coffee)p(A|coffee), ... , p(N), p(R)  -> same decide() rules.
Backbone, 6 views, preprocessing and decision rules are unchanged (same 89 MB model file).

Evaluation (no photo is ever scored by a head that saw it):
  real coffee photos: leave-one-photo-out (both its clean and phone copies left out)
  no-coffee / roasted / synthetic piles: the held-out test split, head trained on the train split + all real photos
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from graders import CLASSES, Head, decide, l2n

W = os.path.join(os.path.dirname(__file__), '..'); FD = os.path.join(W, 'data', 'feats'); RD = os.path.join(W, 'results')
PARTS = [p for p in ('synthetic', 'commons', 'commons2') if os.path.exists(os.path.join(FD, f'{p}_rows.json'))]
rows = [r for p in PARTS for r in json.load(open(os.path.join(FD, f'{p}_rows.json')))]
X = np.concatenate([np.load(os.path.join(FD, f'{p}_clip_int8.npy')) for p in PARTS])
split = np.array([r['split'] for r in rows]); var = np.array([r['variant'] for r in rows]); lab = np.array([r['label'] for r in rows])
ix = {(r['id'], r['variant']): i for i, r in enumerate(rows)}

grades = {}
for f in ('real_grades.json', 'real_grades2.json', 'real_grades_samples.json'):
    if os.path.exists(os.path.join(W, 'data', f)): grades.update(json.load(open(os.path.join(W, 'data', f))))
def row_id(k):
    if k.startswith('sample:'): return 'seen/sample_' + k[7:]              # the demo's three sample photos
    return 'seen/' + os.path.basename(k) if '/ai/photo/commons/' in k else 'commons/' + k.split('data/commons/', 1)[1]
REAL = [(row_id(k), g) for k, g in grades.items() if (row_id(k), 'clean') in ix]
real_ids = {rid for rid, _ in REAL}
print('parts', PARTS, '| real coffee photos', len(REAL), '| graded', sum(1 for _, g in REAL if g), {g: sum(1 for _, x in REAL if x == g) for g in 'ABC'})

# base training rows (synthetic piles, empty backgrounds, R and N train split) -- real coffee photos are added per fold
base = np.where((split == 'train'))[0]
KIND = {'A': 0, 'B': 0, 'C': 0, 'N': 1, 'R': 2}

def train_heads(exclude=None, w_real=10, C_kind=3.0, C_grade=3.0):
    rr = [(rid, g) for rid, g in REAL if rid != exclude]
    ri = [ix[(rid, v)] for rid, _ in rr for v in ('clean', 'phone')]
    rg = [g for _, g in rr for v in ('clean', 'phone')]
    # kind head: coffee(0) / N(1) / R(2)
    ki = np.concatenate([base, np.tile(ri, w_real)]).astype(int)
    ky = np.concatenate([[KIND[l] for l in lab[base]], np.zeros(len(ri) * w_real, int)])
    hk = Head.train(X[ki].reshape(-1, X.shape[2]), np.repeat(ky, 6), C=C_kind)
    # grade head: A/B/C from piles + graded real photos
    gi_base = base[np.isin(lab[base], ['A', 'B', 'C'])]
    gri = [i for i, g in zip(ri, rg) if g]; gry = [g for g in rg if g]
    gi = np.concatenate([gi_base, np.tile(gri, w_real)]).astype(int)
    gy = np.array(['ABC'.index(l) for l in lab[gi_base]] + ['ABC'.index(g) for g in gry] * w_real)
    hg = Head.train(X[gi].reshape(-1, X.shape[2]), np.repeat(gy, 6), C=C_grade)
    return hk, hg

def probs5(hk, hg, i):
    """per view: p5 = [pk0*pgA, pk0*pgB, pk0*pgC, pkN, pkR], then mean over the 6 views (exactly what grader_v2.js does)"""
    pk = hk.probs(X[i])[:, :3]; pg = hg.probs(X[i])[:, :3]
    pk = pk / pk.sum(1, keepdims=True); pg = pg / pg.sum(1, keepdims=True)
    return np.stack([pk[:, 0] * pg[:, 0], pk[:, 0] * pg[:, 1], pk[:, 0] * pg[:, 2], pk[:, 1], pk[:, 2]], 1).mean(0)

def evaluate(w_real, C_kind, C_grade, verbose=False):
    out = {}
    # real coffee photos: leave one photo out
    real_dec = {v: [] for v in ('clean', 'phone')}
    for rid, g in REAL:
        hk, hg = train_heads(rid, w_real, C_kind, C_grade)
        for v in ('clean', 'phone'):
            i = ix[(rid, v)]; real_dec[v].append((g, decide(probs5(hk, hg, i), rows[i])))
    hk, hg = train_heads(None, w_real, C_kind, C_grade)
    for v in ('clean', 'phone'):
        d = real_dec[v]; gd = [(g, x) for g, x in d if g]
        test = np.where((split == 'test') & (var == v))[0]
        dec = {i: decide(probs5(hk, hg, i), rows[i]) for i in test if rows[i]['id'] not in real_ids}
        N = [i for i in dec if lab[i] == 'N']; Nr = [i for i in N if rows[i]['id'].startswith('commons')]
        R = [i for i in dec if lab[i] == 'R']; P = [i for i in dec if rows[i]['id'].startswith('pile/')]
        out[v] = dict(
            real_coffee_graded=round(np.mean([x['kind'] == 'graded' for _, x in d]), 3), n_real=len(d),
            real_grade_exact=round(np.mean([x['grade'] == g for g, x in gd]), 3), n_real_graded=len(gd),
            real_confusion={g: {c: sum(1 for gg, x in gd if gg == g and (x['grade'] or x['kind']) == c) for c in ['A', 'B', 'C', 'retake', 'roasted']} for g in 'ABC'},
            no_coffee_refused=round(np.mean([dec[i]['kind'] == 'retake' for i in N]), 3), no_coffee_real_refused=round(np.mean([dec[i]['kind'] == 'retake' for i in Nr]), 3), n_no_coffee_real=len(Nr),
            roasted=round(np.mean([dec[i]['kind'] == 'roasted' for i in R]), 3), n_roasted=len(R),
            piles_exact=round(np.mean([dec[i]['grade'] == lab[i] for i in P]), 3))
    return out, (hk, hg)

def deployed_eval():
    h = Head.deployed(); out = {}
    for v in ('clean', 'phone'):
        d = [(g, decide(h.probs(X[ix[(rid, v)]]).mean(0), rows[ix[(rid, v)]])) for rid, g in REAL]; gd = [(g, x) for g, x in d if g]
        test = np.where((split == 'test') & (var == v))[0]
        dec = {i: decide(h.probs(X[i]).mean(0), rows[i]) for i in test if rows[i]['id'] not in real_ids}
        N = [i for i in dec if lab[i] == 'N']; Nr = [i for i in N if rows[i]['id'].startswith('commons')]
        R = [i for i in dec if lab[i] == 'R']; P = [i for i in dec if rows[i]['id'].startswith('pile/')]
        out[v] = dict(real_coffee_graded=round(np.mean([x['kind'] == 'graded' for _, x in d]), 3), n_real=len(d),
                      real_grade_exact=round(np.mean([x['grade'] == g for g, x in gd]), 3), n_real_graded=len(gd),
                      real_confusion={g: {c: sum(1 for gg, x in gd if gg == g and (x['grade'] or x['kind']) == c) for c in ['A', 'B', 'C', 'retake', 'roasted']} for g in 'ABC'},
                      no_coffee_refused=round(np.mean([dec[i]['kind'] == 'retake' for i in N]), 3), no_coffee_real_refused=round(np.mean([dec[i]['kind'] == 'retake' for i in Nr]), 3), n_no_coffee_real=len(Nr),
                      roasted=round(np.mean([dec[i]['kind'] == 'roasted' for i in R]), 3), n_roasted=len(R),
                      piles_exact=round(np.mean([dec[i]['grade'] == lab[i] for i in P]), 3))
    return out

def show(name, o):
    for v in ('clean', 'phone'):
        q = o[v]
        print(f"  {name[:34]:34} {v:5} real: coffee->graded {q['real_coffee_graded']:.2f} (n={q['n_real']}) grade {q['real_grade_exact']:.2f} (n={q['n_real_graded']}) | "
              f"no-coffee refused {q['no_coffee_real_refused']:.2f} (real n={q['n_no_coffee_real']}) | roasted {q['roasted']:.2f} (n={q['n_roasted']}) | piles {q['piles_exact']:.2f}", flush=True)

if __name__ == '__main__':
    res = {'deployed': deployed_eval()}; show('deployed (as shipped)', res['deployed'])
    grid = [(w, ck, cg) for w in (5, 20) for ck in (1.0, 3.0) for cg in (1.0, 3.0)]
    for w, ck, cg in grid:
        o, _ = evaluate(w, ck, cg); res[f'w{w}_Ck{ck}_Cg{cg}'] = o; show(f'improved w={w} Ck={ck} Cg={cg}', o)
    json.dump(res, open(os.path.join(RD, f'improve_grid_{"_".join(PARTS)}.json'), 'w'), indent=1)
