"""Build train/test images and cache 6-view features for every backbone.

Splits (seeded, no overlap):
  bean crops   : 70% train / 30% test, per dataset grade -> train piles only use train crops, test piles only test crops
  piles        : 300 per grade for training (900, as v2), 80 per grade for testing
  R (roasted)  : reviewed Commons photos, 70/30 per search query
  N (no beans) : reviewed Commons photos 70/30 per query + empty synthetic backgrounds (60 train / 20 test)
  G (real green/parchment coffee, Commons): test only -> should come out 'graded' (no grade labels exist)
Every test image is also scored after cheap_phone() degradation.
"""
import json, os, sys, time
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from compose import load_crops, pile, empty_background, cheap_phone
from graders import all_views, pixel_stats, clip_backbone, resnet_backbone

W = os.path.join(os.path.dirname(__file__), '..'); D = os.path.join(W, 'data'); OUT = os.path.join(D, 'feats'); os.makedirs(OUT, exist_ok=True)
IMG = os.path.join(D, 'images'); os.makedirs(IMG, exist_ok=True)
rng = np.random.default_rng(42)
PART = sys.argv[1] if len(sys.argv) > 1 else 'all'      # 'synthetic' (piles, empty backgrounds, seen photos) | 'commons' | 'all'

# ---------- crops split ----------
crops = load_crops(os.path.join(D, 'crops')); tr_c, te_c = {}, {}
for g, L in crops.items():
    L = list(L); rng.shuffle(L); k = int(len(L) * .7); tr_c[g], te_c[g] = L[:k], L[k:]
print({g: (len(tr_c[g]), len(te_c[g])) for g in crops})

# ---------- reviewed Commons sets ----------
SUF = '2' if PART == 'commons2' else ''
meta = json.load(open(os.path.join(D, 'commons', f'meta{SUF}.json'))) if PART != 'synthetic' else {}
review = json.load(open(os.path.join(D, 'commons', f'review{SUF}.json'))) if PART != 'synthetic' else {}      # {path: 'R'|'G'|'N'|'drop'} after looking at contact sheets
items = []   # (id, split, label, kind_expected, loader)
def add(id_, split, label, loader): items.append((id_, split, label, loader))

by_q = {}
for k, m in meta.items():
    lab = review.get(k, m['set'])
    if lab == 'drop' or not os.path.exists(os.path.join(D, 'commons', k)): continue
    by_q.setdefault((lab, m['query']), []).append(k)
for (lab, q), L in sorted(by_q.items()):
    L = sorted(L); rng.shuffle(L); k = int(round(len(L) * .7))
    for i, f in enumerate(L):
        split = 'test' if lab == 'G' else ('train' if i < k else 'test')
        add('commons/' + f, split, lab, (lambda f=f: Image.open(os.path.join(D, 'commons', f)).convert('RGB')))

cache = {}
if PART in ('commons', 'commons2'): items_commons = list(items)
def piler(g, cr, seed): return lambda: pile(g, cr, np.random.default_rng(seed), cache)
for g in 'ABC':
    for i in range(300): add(f'pile/train/{g}{i:03d}', 'train', g, piler(g, tr_c, 1000 * ord(g) + i))
    for i in range(80): add(f'pile/test/{g}{i:03d}', 'test', g, piler(g, te_c, 500000 + 1000 * ord(g) + i))
for i in range(60): add(f'empty/train/{i:03d}', 'train', 'N', (lambda s=i: empty_background(np.random.default_rng(70000 + s))))
for i in range(20): add(f'empty/test/{i:03d}', 'test', 'N', (lambda s=i: empty_background(np.random.default_rng(80000 + s))))

# real photos the deployed model may have seen (repo commons + demo samples): reported separately
for f in sorted(os.listdir(os.path.join(W, '..', 'dure', 'ai', 'photo', 'commons'))):
    if f.endswith('.jpg'): add('seen/' + f, 'seen', 'G', (lambda f=f: Image.open(os.path.join(W, '..', 'dure', 'ai', 'photo', 'commons', f)).convert('RGB')))
for g in 'ABC':
    add(f'seen/sample_{g}', 'seen', g, (lambda g=g: Image.open(os.path.join(W, '..', 'dure', 'site', 'src', 'assets', 'samples', f'sample_{g}.jpg')).convert('RGB')))

if PART in ('commons', 'commons2'): items = items_commons
print('items', {s: sum(1 for x in items if x[1] == s) for s in ('train', 'test', 'seen')})

# ---------- views (+ cheap-phone copies for test/seen) ----------
rows = []   # (id, split, label, variant, views, stats)
t0 = time.time()
for n, (id_, split, lab, ld) in enumerate(items):
    im = ld()
    if id_.startswith('pile/test') and n % 20 == 0: im.save(os.path.join(IMG, id_.replace('/', '_') + '.jpg'), quality=85)
    variants = [('clean', im)] + ([('phone', cheap_phone(im, np.random.default_rng(hash(id_) % 2**32)))] if split != 'train' else [])
    for var, x in variants:
        V = all_views(x); rows.append((id_, split, lab, var, V, pixel_stats(V[0])))
print(f'views for {len(rows)} images in {time.time() - t0:.0f}s')

meta_rows = [dict(id=r[0], split=r[1], label=r[2], variant=r[3], **r[5]) for r in rows]
json.dump(meta_rows, open(os.path.join(OUT, f'{PART}_rows.json'), 'w'))
allv = [v for r in rows for v in r[4]]
for name, mk in [('resnet18_fp32', lambda: resnet_backbone(False)), ('resnet18_int8', lambda: resnet_backbone(True)), ('clip_int8', clip_backbone)]:
    t0 = time.time(); bb = mk(); F = bb.features(allv)
    np.save(os.path.join(OUT, f'{PART}_{name}.npy'), F.reshape(len(rows), 6, -1).astype(np.float32))
    print(f'{name}: {F.shape} in {time.time() - t0:.0f}s ({(time.time() - t0) / len(allv) * 1000:.1f} ms/view)', flush=True)
