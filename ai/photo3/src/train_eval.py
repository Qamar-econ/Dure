"""Train the 5-class heads (same recipe for every backbone) and compare against the deployed CLIP grader.

Recipe (identical for CLIP and ResNet-18):
  features of the 6 views of each training image = 6 training rows (the v2 augmentation), L2-normalised,
  multinomial logistic regression, class-balanced; C picked by 5-fold CV grouped by image (score = 6-view-averaged
  5-class accuracy). Prediction = mean of the 6 views' probabilities -> graders.decide() (same rules as grader_v2.js).
"""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from graders import CLASSES, Head, decide, l2n

W = os.path.join(os.path.dirname(__file__), '..'); F = os.path.join(W, 'data', 'feats'); R = os.path.join(W, 'results'); os.makedirs(R, exist_ok=True)
PARTS = [p for p in ('synthetic', 'commons') if os.path.exists(os.path.join(F, f'{p}_rows.json'))]
rows = [r for p in PARTS for r in json.load(open(os.path.join(F, f'{p}_rows.json')))]
lab = np.array([CLASSES.index(r['label']) if r['label'] in CLASSES else -1 for r in rows])
split = np.array([r['split'] for r in rows]); var = np.array([r['variant'] for r in rows])

def wilson(k, n, z=1.96):
    if n == 0: return (float('nan'),) * 2
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(c - h, 3), round(c + h, 3)

def fit(X6, y, Cs=(0.3, 1, 3, 10, 30)):
    """X6: (n, 6, d). Grouped CV over images for C, then refit on all."""
    from sklearn.model_selection import StratifiedKFold
    n = len(y); best = None
    for C in Cs:
        acc = []
        for tr, va in StratifiedKFold(5, shuffle=True, random_state=0).split(np.zeros(n), y):
            h = Head.train(X6[tr].reshape(-1, X6.shape[2]), np.repeat(y[tr], 6), C=C)
            p = h.probs(X6[va].reshape(-1, X6.shape[2])).reshape(len(va), 6, 5).mean(1)
            acc.append((p.argmax(1) == y[va]).mean())
        m = float(np.mean(acc)); print(f'    C={C:<5} cv acc {m:.3f}', flush=True)
        if best is None or m > best[1]: best = (C, m)
    return Head.train(X6.reshape(-1, X6.shape[2]), np.repeat(y, 6), C=best[0]), best

def evaluate(head, X6):
    P = head.probs(X6.reshape(-1, X6.shape[2])).reshape(len(X6), 6, 5).mean(1)
    return P, [decide(P[i], rows[i]) for i in range(len(rows))]

def summarise(dec, P):
    out = {}
    for v in ('clean', 'phone'):
        m = (split == 'test') & (var == v)
        pile = m & np.array([r['id'].startswith('pile/') for r in rows])
        cm = {g: {k: 0 for k in ['A', 'B', 'C', 'retake', 'roasted']} for g in 'ABC'}
        for i in np.where(pile)[0]:
            d = dec[i]; cm[rows[i]['label']][d['grade'] or d['kind']] += 1
        n = int(pile.sum()); ok = sum(cm[g][g] for g in 'ABC'); ans = sum(cm[g][k] for g in 'ABC' for k in 'ABC')
        argmax_ok = int(sum(CLASSES[P[i].argmax()] == rows[i]['label'] for i in np.where(pile)[0]))
        sel = lambda f: [i for i in np.where(m)[0] if f(rows[i])]
        Ri = sel(lambda r: r['label'] == 'R'); Ni = sel(lambda r: r['label'] == 'N'); Ni_c = sel(lambda r: r['label'] == 'N' and r['id'].startswith('commons'))
        Gi = sel(lambda r: r['label'] == 'G')
        out[v] = dict(
            piles=dict(n=n, exact=round(ok / n, 3), exact_ci=wilson(ok, n), answered=round(ans / n, 3),
                       acc_when_answered=round(ok / max(ans, 1), 3), argmax_5class=round(argmax_ok / n, 3), confusion=cm),
            roasted=dict(n=len(Ri), said_roasted=round(np.mean([dec[i]['kind'] == 'roasted' for i in Ri]), 3) if Ri else None),
            no_coffee=dict(n=len(Ni), refused=round(np.mean([dec[i]['kind'] == 'retake' for i in Ni]), 3) if Ni else None,
                           n_real_photos=len(Ni_c), refused_real_photos=round(np.mean([dec[i]['kind'] == 'retake' for i in Ni_c]), 3) if Ni_c else None),
            real_green=dict(n=len(Gi), graded=round(np.mean([dec[i]['kind'] == 'graded' for i in Gi]), 3) if Gi else None,
                            kinds={k: int(sum(dec[i]['kind'] == k for i in Gi)) for k in ('graded', 'roasted', 'retake')},
                            grades={g: int(sum(dec[i]['grade'] == g for i in Gi)) for g in 'ABC'}))
    return out

if __name__ == '__main__':
    tr = split == 'train'; y = lab[tr]
    print('train images', int(tr.sum()), {c: int((y == k).sum()) for k, c in enumerate(CLASSES)})
    results, heads = {}, {}
    feats = {n: np.concatenate([np.load(os.path.join(F, f'{p}_{n}.npy')) for p in PARTS]) for n in ('clip_int8', 'resnet18_fp32', 'resnet18_int8')}
    runs = [('CLIP int8, deployed head (as shipped)', 'clip_int8', 'deployed'),
            ('CLIP int8, head retrained here', 'clip_int8', 'train'),
            ('ResNet-18 fp32, head trained here', 'resnet18_fp32', 'train'),
            ('ResNet-18 int8, head trained here', 'resnet18_int8', 'train')]
    for name, fn, how in runs:
        X = feats[fn]; print(name, flush=True)
        if how == 'deployed': head, cv = Head.deployed(), None
        else: head, cv = fit(X[tr], y)
        P, dec = evaluate(head, X); heads[name] = head
        results[name] = dict(backbone=fn, cv=cv, **summarise(dec, P),
                             seen=[dict(id=rows[i]['id'], variant=rows[i]['variant'], kind=dec[i]['kind'], grade=dec[i]['grade'],
                                        probs={k: round(float(v), 3) for k, v in dec[i]['probs'].items()}) for i in np.where(split == 'seen')[0]])
        if how == 'train':
            json.dump({'classes': CLASSES, 'W': np.round(head.W, 6).tolist(), 'b': np.round(head.b, 6).tolist(), 'C': cv[0]},
                      open(os.path.join(R, f'head_{fn}.json'), 'w'))
    json.dump(results, open(os.path.join(R, 'results.json'), 'w'), indent=1)
    for name, r in results.items():
        c, p = r['clean'], r['phone']
        print(f"\n== {name}  (cv {r['cv']})")
        for v in ('clean', 'phone'):
            q = r[v]
            print(f"  {v:5} piles exact {q['piles']['exact']:.3f} {q['piles']['exact_ci']} answered {q['piles']['answered']:.3f} acc|ans {q['piles']['acc_when_answered']:.3f}"
                  f" | roasted->R {q['roasted']['said_roasted']} (n={q['roasted']['n']}) | no-coffee refused {q['no_coffee']['refused']} (real {q['no_coffee']['refused_real_photos']}, n={q['no_coffee']['n_real_photos']})"
                  f" | real green graded {q['real_green']['graded']} (n={q['real_green']['n']}) {q['real_green']['kinds']}")
