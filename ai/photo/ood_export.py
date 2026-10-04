"""Novelty guard + ONNX export for the Dure photo grader.

Why: on real coffee photos unlike the training set (Wikimedia Commons), the grader answered with
near-total confidence and was mostly wrong. Confidence alone can't catch that, so the exported model
also returns a novelty score: the share of a photo's features that the training photos can't explain
(1 - variance captured by the top 32 principal components of the training features).
Threshold: the 98th percentile of validation photos. Above it, Dure refuses to grade.

Outputs: grader.onnx (inputs: image; outputs: probs, novelty), ood.json, demo_photos.json
"""
import base64, glob, io, json, os, random
import numpy as np, torch, torch.nn as nn
from PIL import Image
import torchvision.transforms as T
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights

torch.set_num_threads(int(os.environ.get('THREADS', '1'))); torch.manual_seed(0); random.seed(0); np.random.seed(0)
MAP = {'CGA': 'A', 'CGB': 'B', 'CGC': 'B', 'CGD': 'C'}; G = ['A', 'B', 'C']; K = 32
files = sorted(glob.glob('img/*.jpg'))
by = {}
for f in files: by.setdefault(os.path.basename(f).split('_')[0], []).append((f, G.index(MAP[os.path.basename(f).split('_')[0]])))
tr, va, te = [], [], []
for k, L in by.items():           # same split as train_photo.py (same seed, same order)
    random.shuffle(L); n = len(L); a, b = int(n * .7), int(n * .85)
    tr += L[:a]; va += L[a:b]; te += L[b:]

W = MobileNet_V3_Small_Weights.IMAGENET1K_V1
net = mobilenet_v3_small(weights=W).eval()
body = nn.Sequential(net.features, net.avgpool, nn.Flatten())
head = nn.Sequential(nn.Dropout(.2), nn.Linear(576, 3)); ck = torch.load('grader_head.pt'); head.load_state_dict(ck['head']); head.eval()
norm = T.Compose([T.ToTensor(), T.Normalize(W.transforms().mean, W.transforms().std)]); clean = T.Compose([T.Resize(232), T.CenterCrop(224)])
load = lambda f: clean(Image.open(f).convert('RGB'))

@torch.no_grad()
def feats(ims):
    return torch.cat([body(torch.stack([norm(x) for x in ims[i:i + 32]])) for i in range(0, len(ims), 32)])

Xtr = feats([load(f) for f, _ in tr]); Xva = feats([load(f) for f, _ in va]); Xte = feats([load(f) for f, _ in te])
mu = Xtr.mean(0); U, S, V = torch.linalg.svd(Xtr - mu, full_matrices=False); P = V[:K].T.contiguous()   # 576 x K

class Guarded(nn.Module):
    def __init__(s):
        super().__init__(); s.body, s.head = body, head
        s.register_buffer('mu', mu); s.register_buffer('P', P)
    def forward(s, image):
        f = s.body(image); c = f - s.mu; r = c - (c @ s.P) @ s.P.T
        return torch.softmax(s.head(f), 1), (r.pow(2).sum(1) / c.pow(2).sum(1).clamp_min(1e-6))

g = Guarded().eval()
with torch.no_grad():
    nov = lambda X: (lambda c: ((c - (c @ P) @ P.T).pow(2).sum(1) / c.pow(2).sum(1)))(X - mu)
    thr = float(np.percentile(nov(Xva).numpy(), 98)); te_ref = float((nov(Xte) > thr).float().mean())
    com = sorted(glob.glob('commons/*.jpg')); Xc = feats([load(f) for f in com]); nc = nov(Xc).numpy()
torch.onnx.export(g, torch.randn(1, 3, 224, 224), 'grader.onnx', input_names=['image'], output_names=['probs', 'novelty'],
                  dynamic_axes={'image': {0: 'n'}}, opset_version=17, dynamo=False)
res = {'pca_components': K, 'novelty_threshold': round(thr, 4), 'test_refused_share': round(te_ref, 3),
       'commons_refused': f'{int((nc > thr).sum())}/{len(com)}', 'commons': {os.path.basename(f): round(float(v), 3) for f, v in zip(com, nc)},
       'onnx_mb': round(os.path.getsize('grader.onnx') / 1e6, 2)}
# refresh the cached results the demo shows when the model can't load (same preprocessing as the browser)
import onnxruntime as ort
sess = ort.InferenceSession('grader.onnx'); dp = json.load(open('demo_photos.json'))
import re
key = lambda x: re.sub(r'[^a-z0-9]', '', os.path.splitext(x)[0].lower().replace('jpg', ''))[:36]
def find(src):
    for f in glob.glob('img/*.jpg') + glob.glob('commons/*.jpg'):
        if key(os.path.basename(f)) == key(src): return f
for k, v in dp.items():
    if k.startswith('_'): continue
    f = find(v['src'])
    if not f: print('missing source for', k, v['src']); continue
    p, n = sess.run(None, {'image': norm(load(f)).unsqueeze(0).numpy()})
    v['probs'] = [round(float(x), 3) for x in p[0]]; v['novelty'] = round(float(n[0]), 3)
    print(k, f, v['probs'], v['novelty'], 'REFUSED' if n[0] > thr else 'graded')
dp['_threshold'] = {'novelty': round(thr, 4), 'confidence': 0.6}
json.dump(dp, open('demo_photos.json', 'w'))
json.dump(res, open('ood.json', 'w'), indent=1); print(json.dumps(res, indent=1))
