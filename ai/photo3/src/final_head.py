"""Train the final improved head on ALL data (train + test splits + every real coffee photo) with the chosen settings,
save it, and score the three demo samples with the exact per-view arithmetic the JS will use."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import improve as im
from graders import Head, decide, clip_backbone, all_views, pixel_stats
W_REAL, CK, CG = 20, 1.0, 3.0
# use every non-real row as training data now (evaluation is done)
im.base = np.array([i for i in range(len(im.rows)) if im.rows[i]['variant'] == 'clean' and im.rows[i]['split'] in ('train', 'test') and im.rows[i]['id'] not in im.real_ids])
hk, hg = im.train_heads(None, W_REAL, CK, CG)
out = {'classes': ['A', 'B', 'C', 'N', 'R'],
       'kind': {'classes': ['coffee', 'N', 'R'], 'W': np.round(hk.W[:3], 6).tolist(), 'b': np.round(hk.b[:3], 6).tolist()},
       'grade': {'classes': ['A', 'B', 'C'], 'W': np.round(hg.W[:3], 6).tolist(), 'b': np.round(hg.b[:3], 6).tolist()},
       'settings': {'w_real': W_REAL, 'C_kind': CK, 'C_grade': CG}}
json.dump(out, open(os.path.join(im.RD, 'head_v3.json'), 'w'))
print('train rows', len(im.base), 'kind W', np.array(out['kind']['W']).shape, 'grade W', np.array(out['grade']['W']).shape)
from PIL import Image
bb = clip_backbone(); HK = Head(out['kind']['W'], out['kind']['b']); HG = Head(out['grade']['W'], out['grade']['b'])
for g in 'ABC':
    img = Image.open(f'/home/claude/dure/site/src/assets/samples/sample_{g}.jpg'); V = all_views(img); F = bb.features(V)
    pk = HK.probs(F); pg = HG.probs(F)
    p = np.stack([pk[:, 0] * pg[:, 0], pk[:, 0] * pg[:, 1], pk[:, 0] * pg[:, 2], pk[:, 1], pk[:, 2]], 1).mean(0)
    d = decide(p, pixel_stats(V[0])); print(g, d['kind'], d['grade'], {k: round(float(v), 3) for k, v in d['probs'].items()})
