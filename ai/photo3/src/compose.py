"""Synthetic coffee piles: real bean cut-outs (MIT dataset) scattered on procedural tarp / sack / concrete / bamboo-mat
backgrounds. Reconstruction of the lost v2 recipe ("crops composed into synthetic piles on tarp, sack and concrete").

Pile grade from its bean mix (dataset grades: CGA premium, CGB good, CGC standard, CGD defective):
  A: CGA only (up to 10% CGB), no CGD
  B: mostly CGB/CGC (CGA allowed), CGD 0-8%
  C: CGD 25-60%, rest CGB/CGC
Also: empty backgrounds (no beans) for the N class, and cheap_phone() degradation for tests.
"""
import io, os, random
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw

def _noise(h, w, scale, rng):
    """smooth value noise in [0,1]"""
    sh, sw = max(2, h // scale), max(2, w // scale)
    n = Image.fromarray((rng.random((sh, sw)) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(n, np.float32) / 255

def background(kind, w, h, rng):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    if kind == 'tarp':
        base = np.array(rng.choice([[40, 90, 170], [30, 120, 80], [210, 110, 40], [150, 150, 150], [60, 60, 160]]), np.float32)
        p = rng.uniform(3, 6); weave = 0.06 * (np.sin(x * 2 * np.pi / p) * np.sin(y * 2 * np.pi / p))
        folds = 0.18 * (_noise(h, w, rng.integers(60, 160), rng) - .5)
        img = base[None, None] * (1 + weave + folds)[..., None]
    elif kind == 'sack':
        base = np.array([rng.uniform(150, 195), rng.uniform(120, 160), rng.uniform(75, 110)], np.float32)
        p = rng.uniform(5, 9); weave = 0.14 * (np.abs(np.sin(x * np.pi / p)) * np.abs(np.sin(y * np.pi / p)) - .4)
        fib = 0.10 * (_noise(h, w, 3, rng) - .5); img = base[None, None] * (1 + weave + fib + 0.1 * (_noise(h, w, 80, rng) - .5))[..., None]
    elif kind == 'concrete':
        g = rng.uniform(110, 175); base = np.array([g, g * rng.uniform(.96, 1.02), g * rng.uniform(.9, 1.0)], np.float32)
        t = 0.10 * (_noise(h, w, 2, rng) - .5) + 0.12 * (_noise(h, w, 40, rng) - .5) + 0.08 * (_noise(h, w, 200, rng) - .5)
        img = base[None, None] * (1 + t)[..., None]
        for _ in range(rng.integers(50, 300)):   # speckles
            cx, cy = rng.integers(0, w), rng.integers(0, h); img[max(0, cy - 1):cy + 2, max(0, cx - 1):cx + 2] *= rng.uniform(.6, 1.2)
    else:  # bamboo mat (woven drying tray)
        base = np.array([rng.uniform(170, 210), rng.uniform(140, 175), rng.uniform(90, 120)], np.float32)
        p = rng.uniform(14, 26); a = np.floor(x / p) + np.floor(y / p)
        stripe = np.where(a % 2 == 0, np.sin(y * np.pi / p * 6), np.sin(x * np.pi / p * 6)) * 0.05
        img = base[None, None] * (1 + stripe + 0.08 * (_noise(h, w, 4, rng) - .5) - 0.12 * (np.minimum((x % p), (y % p)) < 1.2))[..., None]
    # light: gradient + vignette
    gx, gy = rng.uniform(-.25, .25), rng.uniform(-.25, .25)
    light = 1 + gx * (x / w - .5) + gy * (y / h - .5) - rng.uniform(0, .25) * (((x / w - .5) ** 2 + (y / h - .5) ** 2) * 2)
    return Image.fromarray(np.clip(img * light[..., None], 0, 255).astype(np.uint8))

def load_crops(d):
    by = {}
    for f in sorted(os.listdir(d)):
        if f.endswith('.png'): by.setdefault(f[:3], []).append(os.path.join(d, f))
    return by

MIX = {  # grade -> function(rng) -> dict of dataset-grade shares
    'A': lambda r: {'CGA': 1 - (b := r.uniform(0, .1)), 'CGB': b},
    'B': lambda r: (lambda d, a: {'CGA': a, 'CGB': (1 - a - d) * (s := r.uniform(.3, .7)), 'CGC': (1 - a - d) * (1 - s), 'CGD': d})(r.uniform(0, .08), r.uniform(0, .2)),
    'C': lambda r: (lambda d: {'CGB': (1 - d) * (s := r.uniform(.2, .8)), 'CGC': (1 - d) * (1 - s), 'CGD': d})(r.uniform(.25, .6)),
}

def pile(grade, crops, rng, cache):
    """one synthetic photo of a pile of the given grade; crops = {CGA: [paths], ...} (only this split's beans)"""
    W, H = [(1024, 768), (900, 900), (768, 1024), (1200, 900)][rng.integers(4)]
    im = background(rng.choice(['tarp', 'sack', 'concrete', 'mat'], p=[.3, .3, .25, .15]), W, H, rng).convert('RGBA')
    n = int(rng.integers(35, 140)); mix = MIX[grade](rng); keys = list(mix); pr = np.array([mix[k] for k in keys]); pr /= pr.sum()
    bean_len = rng.uniform(.06, .12) * min(W, H)
    # cluster centre (piles are rarely uniform)
    cx, cy, spread = rng.uniform(.35, .65) * W, rng.uniform(.35, .65) * H, rng.uniform(.25, .6)
    shadow = Image.new('RGBA', im.size, (0, 0, 0, 0)); layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
    for _ in range(n):
        g = keys[rng.choice(len(keys), p=pr)]; f = crops[g][rng.integers(len(crops[g]))]
        b = cache.get(f) or cache.setdefault(f, Image.open(f).convert('RGBA'))
        s = bean_len * rng.uniform(.85, 1.15) / max(b.size)
        bb = b.resize((max(4, int(b.size[0] * s)), max(4, int(b.size[1] * s))), Image.LANCZOS).rotate(rng.uniform(0, 360), expand=True, resample=Image.BICUBIC)
        px = int(np.clip(rng.normal(cx, spread * W / 2.5), 0, W - bb.size[0])); py = int(np.clip(rng.normal(cy, spread * H / 2.5), 0, H - bb.size[1]))
        sh = Image.new('RGBA', bb.size, (0, 0, 0, 0)); sh.putalpha(bb.split()[3].point(lambda a: int(a * .45)))
        shadow.alpha_composite(sh, (px + int(bean_len * .06), py + int(bean_len * .08)))
        layer.alpha_composite(bb, (px, py))
    im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(bean_len * .06)))
    im.alpha_composite(layer)
    out = im.convert('RGB')
    out = ImageEnhance.Brightness(out).enhance(rng.uniform(.8, 1.15))
    out = ImageEnhance.Color(out).enhance(rng.uniform(.85, 1.15))
    tint = np.array([rng.uniform(.94, 1.06), 1, rng.uniform(.9, 1.08)])
    out = Image.fromarray(np.clip(np.asarray(out, np.float32) * tint, 0, 255).astype(np.uint8))
    if rng.random() < .4: out = out.filter(ImageFilter.GaussianBlur(rng.uniform(.3, 1.0)))
    buf = io.BytesIO(); out.save(buf, 'JPEG', quality=int(rng.integers(70, 95))); return Image.open(io.BytesIO(buf.getvalue())).convert('RGB')

def empty_background(rng):
    W, H = [(1024, 768), (900, 900)][rng.integers(2)]
    return background(rng.choice(['tarp', 'sack', 'concrete', 'mat']), W, H, rng)

def cheap_phone(im, rng):
    """basic camera phone MMS: long side 480-640 px, slight blur, hard JPEG"""
    im = im.convert('RGB'); L = int(rng.choice([480, 560, 640])); s = L / max(im.size)
    if s < 1: im = im.resize((max(1, int(im.size[0] * s)), max(1, int(im.size[1] * s))), Image.BILINEAR)
    im = im.filter(ImageFilter.GaussianBlur(rng.uniform(0, .8)))
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=int(rng.choice([25, 35, 50]))); return Image.open(io.BytesIO(buf.getvalue())).convert('RGB')
