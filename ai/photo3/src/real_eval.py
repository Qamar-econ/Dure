"""Second protocol, closer to v2: real labelled photos are part of training, scored leave-one-photo-out (as in the README).

Real photos (41): 31 reviewed Commons green/parchment photos + the 10 Commons photos kept in the repo (ai/photo/commons).
Grades below are mine, by eye, following the README criteria (black/mouldy beans, insect holes, broken beans,
uneven colour); photos too far away to grade are 'kind only' (must come out as coffee = graded, grade not scored).
Training for each fold = synthetic piles + roasted + no-coffee (train split) + every labelled real photo except the held-out one.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from graders import CLASSES, Head, decide
import train_eval as te

W = os.path.join(os.path.dirname(__file__), '..')
keys = json.load(open(os.path.join(W, 'data', 'real_keys.json')))
GRADE = {}
for g, idx in {'A': [0, 1, 14, 22, 23, 24, 26, 34, 36, 37], 'B': [4, 9, 11, 17, 27], 'C': [13, 15, 32, 35, 38, 39, 40]}.items():
    for i in idx: GRADE[i] = g

def row_id(k):
    return 'seen/' + os.path.basename(k) if '/ai/photo/commons/' in k else 'commons/' + k.split('data/commons/', 1)[1]
rows, split, var = te.rows, te.split, te.var
ix = {(r['id'], r['variant']): i for i, r in enumerate(rows)}
real = [(i, k, GRADE.get(i)) for i, k in enumerate(keys)]
labelled = [(i, k, g) for i, k, g in real if g]
kind_only = [(i, k, g) for i, k, g in real if not g]
print('real photos', len(real), 'labelled', len(labelled), {g: sum(1 for x in labelled if x[2] == g) for g in 'ABC'}, 'kind only', len(kind_only))

tr = np.where(split == 'train')[0]; y_tr = te.lab[tr]
Cbest = {}
for l in open(os.path.join(W, 'train_eval.log')):
    pass
res = json.load(open(os.path.join(W, 'results', 'results.json')))
for name, r in res.items():
    if r['cv']: Cbest[r['backbone']] = r['cv'][0]

REAL_W = int(os.environ.get('REAL_W', '1'))      # repeat real labelled photos this many times in training (1 = plain)
def fit(X, extra_idx, extra_y, C):
    extra_idx = np.tile(extra_idx, REAL_W); extra_y = np.tile(extra_y, REAL_W)
    Xa = np.concatenate([X[tr], X[extra_idx]]); ya = np.concatenate([y_tr, extra_y])
    return Head.train(Xa.reshape(-1, Xa.shape[2]), np.repeat(ya, 6), C=C)

def probs(head, X, i): return head.probs(X[i]).mean(0)

out = {}
feats = te.feats if hasattr(te, 'feats') else None
F = {n: np.concatenate([np.load(os.path.join(te.F, f'{p}_{n}.npy')) for p in te.PARTS]) for n in ('clip_int8', 'resnet18_fp32', 'resnet18_int8')}
models = ([('CLIP int8, deployed head (as shipped)', 'clip_int8', None)] if REAL_W == 1 else []) + [('CLIP int8, head retrained here', 'clip_int8', 'train'),
          ('ResNet-18 fp32, head trained here', 'resnet18_fp32', 'train'), ('ResNet-18 int8, head trained here', 'resnet18_int8', 'train')]
for name, fn, how in models:
    X = F[fn]; o = {}
    for v in ('clean', 'phone'):
        lab_ix = np.array([ix[(row_id(k), 'clean')] for _, k, _ in labelled])     # training always uses the clean photo
        lab_y = np.array([CLASSES.index(g) for _, _, g in labelled])
        # leave-one-photo-out on labelled real photos
        dec = []
        for j, (i, k, g) in enumerate(labelled):
            h = Head.deployed() if how is None else fit(X, np.delete(lab_ix, j), np.delete(lab_y, j), Cbest[fn])
            t = ix[(row_id(k), v)]; dec.append((g, decide(probs(h, X, t), rows[t])))
        # kind-only photos + synthetic/R/N tests with a head trained on all labelled real photos
        h = Head.deployed() if how is None else fit(X, lab_ix, lab_y, Cbest[fn])
        kd = [decide(probs(h, X, ix[(row_id(k), v)]), rows[ix[(row_id(k), v)]]) for _, k, _ in kind_only]
        P = h.probs(X.reshape(-1, X.shape[2])).reshape(len(X), 6, 5).mean(1)
        allde = [decide(P[i], rows[i]) for i in range(len(rows))]
        syn = te.summarise(allde, P)[v]
        n = len(dec); ok = sum(d['grade'] == g for g, d in dec); graded = sum(d['kind'] == 'graded' for _, d in dec)
        cm = {g: {c: sum(1 for gg, d in dec if gg == g and (d['grade'] or d['kind']) == c) for c in ['A', 'B', 'C', 'retake', 'roasted']} for g in 'ABC'}
        o[v] = dict(real_lopo=dict(n=n, exact=round(ok / n, 3), exact_ci=te.wilson(ok, n), graded=round(graded / n, 3), confusion=cm),
                    real_kind_only=dict(n=len(kd), graded=round(np.mean([d['kind'] == 'graded' for d in kd]), 3),
                                        kinds={c: sum(d['kind'] == c for d in kd) for c in ('graded', 'roasted', 'retake')}),
                    synthetic_piles=syn['piles'], roasted=syn['roasted'], no_coffee=syn['no_coffee'])
    out[name] = o
    print(f'\n== {name}')
    for v in ('clean', 'phone'):
        q = o[v]
        print(f"  {v:5} REAL lopo exact {q['real_lopo']['exact']:.3f} {q['real_lopo']['exact_ci']} graded {q['real_lopo']['graded']:.2f} | kind-only graded {q['real_kind_only']['graded']:.2f} {q['real_kind_only']['kinds']}"
              f" | piles {q['synthetic_piles']['exact']:.3f} | roasted {q['roasted']['said_roasted']} | no-coffee refused {q['no_coffee']['refused']} (real {q['no_coffee']['refused_real_photos']})")
        print('        confusion', q['real_lopo']['confusion'])
json.dump(out, open(os.path.join(W, 'results', f'results_real_w{REAL_W}.json'), 'w'), indent=1)
