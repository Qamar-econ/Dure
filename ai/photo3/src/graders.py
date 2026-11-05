"""Dure photo graders in Python: the deployed CLIP grader (ported line by line from site/src/assets/grader_v2.js)
and a ResNet-18 grader with the same structure.

Structure shared by both (= grader_v2.js):
  photo -> 6 views (full, mirror, 4 overlapping quarters) -> centred square -> 224x224 -> backbone (frozen)
  -> 512-d feature, L2-normalised -> 5-class logistic head (A, B, C, N, R) -> softmax -> average over the 6 views
  -> decision: retake if too dark / too blurry (pixel stats of view 0) or p(N) >= 0.5;
               if N wins narrowly, grade anyway with the best of A/B/C/R; R -> 'roasted'; else graded A/B/C.
Training uses the same 6 views as data augmentation (each view is one training row), as the JS comments describe.
"""
import json, os, re
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, '..', 'models')
CLASSES = ['A', 'B', 'C', 'N', 'R']
S = 224
CONFIG = dict(nThr=0.5, darkLuma=25, blurLap=6)


# ---------- views: integer geometry identical to grader_v2.js rects() ----------
def rects(w, h, tta=True):
    cw, ch = w // 2 + w // 8, h // 2 + h // 8
    ox, oy = w // 2 - w // 8, h // 2 - h // 8
    v = [(0, 0, w, h, False), (0, 0, w, h, True)]
    return v + [(0, 0, cw, ch, False), (ox, 0, cw, ch, False), (0, oy, cw, ch, False), (ox, oy, cw, ch, False)] if tta else v[:1]


def view_pixels(im, r):
    """centred square of the view -> 224x224 RGB uint8 (canvas drawImage with high-quality smoothing ~ PIL Lanczos)"""
    x, y, sw, sh, flip = r
    side = min(sw, sh); x0 = x + (sw - side) // 2; y0 = y + (sh - side) // 2
    v = im.crop((x0, y0, x0 + side, y0 + side)).resize((S, S), Image.LANCZOS)
    if flip: v = ImageOps.mirror(v)
    return np.asarray(v, dtype=np.uint8)


def all_views(im):
    im = im.convert('RGB')
    return [view_pixels(im, r) for r in rects(*im.size)]


def pixel_stats(d):
    L = d[..., 0] * .299 + d[..., 1] * .587 + d[..., 2] * .114
    lap = L[:-2, 1:-1] + L[2:, 1:-1] + L[1:-1, :-2] + L[1:-1, 2:] - 4 * L[1:-1, 1:-1]
    return dict(luma=float(L.mean()), lap=float(lap.std()))


# ---------- backbones (frozen) ----------
class Backbone:
    def __init__(self, path, mean, std, out_name, threads=2):
        o = ort.SessionOptions(); o.intra_op_num_threads = threads
        self.sess = ort.InferenceSession(path, o, providers=['CPUExecutionProvider'])
        self.mean = np.array(mean, np.float32)[None, :, None, None]; self.std = np.array(std, np.float32)[None, :, None, None]
        self.out = out_name; self.path = path

    def features(self, views, batch=24):
        """list of 224x224x3 uint8 -> (n, 512) float32"""
        out = []
        for i in range(0, len(views), batch):
            x = np.stack(views[i:i + batch]).astype(np.float32).transpose(0, 3, 1, 2) / 255.0
            x = (x - self.mean) / self.std
            out.append(self.sess.run([self.out], {'pixel_values': x})[0])
        return np.concatenate(out)


def clip_backbone(threads=2):
    return Backbone(os.path.join(MODELS, 'clip_vision_int8.onnx'), [0.48145466, 0.4578275, 0.40821073],
                    [0.26862954, 0.26130258, 0.27577711], 'image_embeds', threads)


def resnet_backbone(int8=False, threads=2):
    f = 'resnet18_feat_int8.onnx' if int8 else 'resnet18_feat_fp32.onnx'
    return Backbone(os.path.join(MODELS, f), [0.485, 0.456, 0.406], [0.229, 0.224, 0.225],
                    '/classifier/classifier.0/Flatten_output_0', threads)


# ---------- head ----------
def l2n(F):
    return F / np.maximum(np.linalg.norm(F, axis=1, keepdims=True), 1e-12)


class Head:
    """softmax(W . e/|e| + b), classes in CLASSES order"""
    def __init__(self, W, b): self.W = np.asarray(W, np.float64); self.b = np.asarray(b, np.float64)

    def probs(self, F):
        z = l2n(F.astype(np.float64)) @ self.W.T + self.b
        z -= z.max(1, keepdims=True); e = np.exp(z); return e / e.sum(1, keepdims=True)

    @staticmethod
    def deployed():
        s = open(os.path.join(HERE, '..', '..', 'dure', 'site', 'src', 'assets', 'grader_v2.js')).read()
        h = json.loads(re.search(r'const HEAD = (\{.*?\});', s, re.S).group(1))
        assert h['classes'] == CLASSES
        return Head(h['W'], h['b'])

    @staticmethod
    def train(F, y, C=1.0, class_weight='balanced'):
        from sklearn.linear_model import LogisticRegression
        m = LogisticRegression(C=C, max_iter=5000, class_weight=class_weight)
        m.fit(l2n(F), y)
        W = np.zeros((5, F.shape[1])); b = np.full(5, -30.0)          # classes absent from training get ~0 prob
        for k, c in enumerate(m.classes_): W[c] = m.coef_[k]; b[c] = m.intercept_[k]
        return Head(W, b)


# ---------- decision (= grader_v2.js grade()) ----------
def decide(p, stats, cfg=CONFIG):
    P = dict(zip(CLASSES, p))
    if stats['luma'] < cfg['darkLuma']: return dict(kind='retake', grade=None, reason='too dark', probs=P)
    if stats['lap'] < cfg['blurLap']: return dict(kind='retake', grade=None, reason='too blurry', probs=P)
    best = CLASSES[int(np.argmax(p))]
    if best == 'N':
        if P['N'] >= cfg['nThr']: return dict(kind='retake', grade=None, reason='no coffee beans recognised', probs=P)
        best = max(['A', 'B', 'C', 'R'], key=lambda c: P[c])
    if best == 'R': return dict(kind='roasted', grade=None, reason='roasted', probs=P)
    return dict(kind='graded', grade=best, reason='grade ' + best, probs=P, conf=P[best])


class Grader:
    def __init__(self, backbone, head): self.bb, self.head = backbone, head

    def grade(self, im):
        V = all_views(im); st = pixel_stats(V[0])
        p = self.head.probs(self.bb.features(V)).mean(0)
        return decide(p, st)
