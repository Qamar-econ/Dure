"""Dure photo grader: MobileNetV3-Small (ImageNet weights) + a small trained head, grades A / B / C.

Data: balanced subset of the Pre-Roast Coffee Bean Grading Dataset (MIT; SamruddhK on Hugging Face).
Grade map: dataset A (premium) -> A; B (good) and C (standard) -> B; D (defective) -> C.
Cheap-phone check: every test photo is also scored after being shrunk to ~0.3 MP-equivalent detail,
JPEG-compressed hard and blurred, like an MMS from a basic phone.
Abstain rule: if the top probability is under a threshold chosen on validation data, Dure asks for another photo.
"""
import glob, io, json, os, random, time
import numpy as np, torch, torch.nn as nn
from PIL import Image, ImageFilter
import torchvision.transforms as T
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights

torch.set_num_threads(int(os.environ.get('THREADS', '1'))); torch.manual_seed(0); random.seed(0); np.random.seed(0)
MAP = {'CGA': 'A', 'CGB': 'B', 'CGC': 'B', 'CGD': 'C'}; G = ['A', 'B', 'C']
files = sorted(glob.glob('img/*.jpg'))
items = [(f, G.index(MAP[os.path.basename(f).split('_')[0]])) for f in files]
by = {}
for f, y in items: by.setdefault(os.path.basename(f).split('_')[0], []).append((f, y))
tr, va, te = [], [], []
for k, L in by.items():
    random.shuffle(L); n = len(L); a, b = int(n * .7), int(n * .85)
    tr += L[:a]; va += L[a:b]; te += L[b:]
print({'train': len(tr), 'val': len(va), 'test': len(te)})

W = MobileNet_V3_Small_Weights.IMAGENET1K_V1
net = mobilenet_v3_small(weights=W).eval()
body = nn.Sequential(net.features, net.avgpool, nn.Flatten())
norm = T.Compose([T.ToTensor(), T.Normalize(W.transforms().mean, W.transforms().std)])
aug = T.Compose([T.RandomResizedCrop(224, scale=(.6, 1)), T.RandomHorizontalFlip(), T.RandomVerticalFlip(), T.RandomRotation(25), T.ColorJitter(.25, .25, .2, .03)])
clean = T.Compose([T.Resize(232), T.CenterCrop(224)])

def cheap_phone(im, rng):
    """Shrink to ~0.3 MP-equivalent detail, blur a little, JPEG at low quality."""
    im = clean(im); s = rng.choice([64, 80, 96])
    im = im.resize((s, s), Image.BILINEAR).filter(ImageFilter.GaussianBlur(rng.uniform(0, .8))).resize((224, 224), Image.BILINEAR)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=rng.choice([25, 35, 50])); return Image.open(io.BytesIO(buf.getvalue())).convert('RGB')

@torch.no_grad()
def feats(ims):
    out = []
    for i in range(0, len(ims), 32): out.append(body(torch.stack([norm(x) for x in ims[i:i + 32]])))
    return torch.cat(out)

t0 = time.time(); rng = random.Random(1)
load = lambda f: Image.open(f).convert('RGB')
Xtr, Ytr = [], []
for rep in range(4):          # 4 views per training photo: 2 augmented, 2 augmented + cheap-phone
    ims = [aug(load(f)) if rep < 2 else cheap_phone(aug(load(f)), rng) for f, _ in tr]
    Xtr.append(feats(ims)); Ytr += [y for _, y in tr]
Xtr = torch.cat(Xtr); Ytr = torch.tensor(Ytr)
Xva = feats([clean(load(f)) for f, _ in va]); Yva = torch.tensor([y for _, y in va])
Xte = feats([clean(load(f)) for f, _ in te]); Xte_p = feats([cheap_phone(load(f), rng) for f, _ in te]); Yte = torch.tensor([y for _, y in te])
print(f'features in {time.time() - t0:.0f}s')

head = nn.Sequential(nn.Dropout(.2), nn.Linear(Xtr.shape[1], 3))
opt = torch.optim.AdamW(head.parameters(), lr=2e-3, weight_decay=1e-3); lossf = nn.CrossEntropyLoss()
best, best_state = 0, None
for ep in range(60):
    head.train(); perm = torch.randperm(len(Xtr))
    for i in range(0, len(Xtr), 64):
        j = perm[i:i + 64]; opt.zero_grad(); lossf(head(Xtr[j]), Ytr[j]).backward(); opt.step()
    head.eval(); acc = (head(Xva).argmax(1) == Yva).float().mean().item()
    if acc > best: best, best_state = acc, {k: v.clone() for k, v in head.state_dict().items()}
head.load_state_dict(best_state); head.eval()

def report(X, Y, thr):
    P = torch.softmax(head(X), 1); conf, pred = P.max(1); keep = conf >= thr
    acc = (pred == Y).float().mean().item(); cov = keep.float().mean().item()
    acc_k = (pred[keep] == Y[keep]).float().mean().item() if keep.any() else float('nan')
    cm = [[int(((Y == a) & (pred == b)).sum()) for b in range(3)] for a in range(3)]
    return {'accuracy': round(acc, 3), 'answered': round(cov, 3), 'accuracy_when_answered': round(acc_k, 3), 'confusion_rows_true_cols_pred_ABC': cm}

# abstain threshold: smallest threshold giving >= 90% accuracy on answered validation photos
Pv = torch.softmax(head(Xva), 1); cv, pv = Pv.max(1); thr = 0.0
for t in [x / 100 for x in range(34, 100)]:
    k = cv >= t
    if k.sum() >= 10 and (pv[k] == Yva[k]).float().mean() >= .90: thr = t; break
res = {'n': {'train_photos': len(tr), 'val': len(va), 'test': len(te)}, 'val_best_accuracy': round(best, 3), 'abstain_threshold': thr,
       'test_clean': report(Xte, Yte, thr), 'test_cheap_phone': report(Xte_p, Yte, thr)}
# speed and size
full = nn.Sequential(body, head).eval(); x = norm(clean(load(te[0][0]))).unsqueeze(0)
with torch.no_grad():
    for _ in range(3): full(x)
    t1 = time.time()
    for _ in range(20): full(x)
res['cpu_ms_per_photo_1_thread'] = round((time.time() - t1) / 20 * 1000, 1)
torch.save({'head': head.state_dict(), 'threshold': thr, 'grades': G}, 'grader_head.pt')
torch.save(full.state_dict(), 'grader_full.pt')
res['model_file_mb'] = round(os.path.getsize('grader_full.pt') / 1e6, 1)
json.dump(res, open('photo_results.json', 'w'), indent=1); print(json.dumps(res, indent=1))
