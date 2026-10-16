"""Train Dure's on-device intent reader: a fastText-style model (hashed word and character n-grams -> averaged
embedding -> softmax over 8 topics), written in numpy. Exports int8 weights for the browser to site/src/assets/intent.json.
The same features are computed in the demo (demo_map.html, intentFeats), so Python and JavaScript agree."""
import json, re, numpy as np, sys
B, D, LAB = 1 << 14, 32, ['sell', 'why', 'forecast', 'buyers', 'weather', 'quality', 'pool', 'other']

def norm(t):
    t = t.lower().replace('’', "'").replace('´', "'")
    t = re.sub(r"[^a-z0-9à-ÿ' ]+", ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

def fnv(s):
    h = 0x811c9dc5
    for ch in s:
        h ^= ord(ch); h = (h * 0x01000193) & 0xffffffff
    return h

def feats(t):
    w = norm(t).split()
    f = ['w:' + x for x in w] + ['b:' + a + '_' + b for a, b in zip(w, w[1:])]
    for x in w:
        x = '<' + x + '>'
        for n in (3, 4, 5):
            f += ['c:' + x[i:i+n] for i in range(len(x) - n + 1)]
    return [fnv(s) % B for s in f] or [0]

def load(p):
    if p.endswith('.jsonl'): return [(d['text'], d['label']) for d in map(json.loads, open(p, encoding='utf-8'))]
    return [tuple(x) for x in json.load(open(p, encoding='utf-8'))]

def train(data, epochs=30, lr=.4, seed=0, keep=.75):
    rng = np.random.default_rng(seed)
    E = (rng.standard_normal((B, D)) * .05).astype(np.float32); W = np.zeros((D, len(LAB)), np.float32); b = np.zeros(len(LAB), np.float32)
    X = [np.array(feats(t)) for t, _ in data]; Y = np.array([LAB.index(l) for _, l in data])
    for ep in range(epochs):
        a = lr * (1 - ep / epochs)
        for i in rng.permutation(len(X)):
            ids = X[i]; k = ids[rng.random(len(ids)) < keep]; ids = k if len(k) else ids   # feature dropout: robust to unseen wording
            h = E[ids].mean(0); z = h @ W + b; p = np.exp(z - z.max()); p /= p.sum()
            g = p.copy(); g[Y[i]] -= 1
            gh = W @ g; W -= a * np.outer(h, g); b -= a * g; np.subtract.at(E, ids, a * gh / len(ids))
    used = np.zeros(B, bool)
    for ids in X: used[ids] = True
    E[~used] = 0   # features never seen in training carry no signal; zero them instead of keeping random noise
    return E, W, b

def predict(m, t):
    E, W, b = m; z = E[feats(t)].mean(0) @ W + b; p = np.exp(z - z.max()); p /= p.sum(); return LAB[int(p.argmax())], float(p.max())

if __name__ == '__main__':
    tr, te = load('train.jsonl'), load('test.json') + load('test2.json') + load('test3.json') + load('test4.json')
    m = train(tr)
    ok = sum(predict(m, t)[0] == l for t, l in te)
    print(f'test: {ok}/{len(te)} = {ok/len(te):.0%}')
    for t, l in te:
        p, c = predict(m, t)
        if p != l: print(f'  miss: {t!r} want {l}, got {p} ({c:.2f})')
    E, W, b = m
    q = lambda a: (np.clip(np.round(a / (np.abs(a).max() / 127)), -127, 127).astype(np.int8), float(np.abs(a).max() / 127))
    import base64
    Eq, es = q(E); Wq, ws = q(W)
    out = {'B': B, 'D': D, 'labels': LAB, 'es': es, 'ws': ws, 'b': [round(float(x), 5) for x in b],
           'E': base64.b64encode(Eq.tobytes()).decode(), 'W': base64.b64encode(Wq.tobytes()).decode(), 'test': f'{ok}/{len(te)}'}
    # check the quantised model gives the same answers
    mq = (Eq.astype(np.float32) * es, Wq.astype(np.float32) * ws, b)
    okq = sum(predict(mq, t)[0] == l for t, l in te); print(f'int8: {okq}/{len(te)}')
    json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else '../../site/src/assets/intent.json', 'w'))
