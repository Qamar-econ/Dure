"""Hybrid reader v2: decide per message, and per field, whether to trust the rules engine or the small model.

Why: with rules engine v2.1 the old hybrid ("rules engine if sure, else model") stopped beating the rules engine alone. The model
is better at English and at declining other languages; the rules engine is better at Tetum. Routing was designed on the
development sets only (tests 1, 2 and 5); tests 3 and 6 were not used to choose it.

Usage: python3 hybrid2.py RULES_DETAIL.json MODEL.json TEST.json [OUT.json] [--policy NAME]
RULES_DETAIL.json comes from `node rules_detail.js OUT TEST`."""
import json, sys

FIELDS = ['lang', 'crop', 'kg', 'ask', 'any', 'grade', 'yn']


def strip(r):
    return {k: v for k, v in r.items() if not k.startswith('_')}


def route_v1(r, m):
    """The 4 Oct hybrid: the rules engine's answer when it is sure, otherwise the model's."""
    return strip(r) if r.get('_sure') else m


def route_v2(r, m):
    """v2: trust each reader where it is strong.
    1. The rules engine is sure -> its answer.
    2. Declining: if the model says the message is in another language and the rules engine did not read it as Tetum, decline.
    3. Tetum: if the rules engine read the message as Tetum and found what the message is about (a crop, kilos, a price, 'any
       price' or a yes/no), keep the rules engine's reading. The model may only fill a missing language.
    4. Otherwise (English, or a message the rules engine could not place) -> the model's answer, but kilos and price come from the
       rules engine when both readers found one and they disagree only by a factor of 10 or 100 (the model's typical number slip)."""
    if r.get('_sure'):
        return strip(r)
    if m.get('lang') == 'unknown' and r.get('lang') != 'tet':
        return {**{f: None for f in FIELDS}, 'lang': 'unknown', 'any': False}
    found = any(r.get(f) not in (None, False) for f in ('crop', 'kg', 'ask', 'any', 'yn'))
    if r.get('lang') == 'tet' and found:
        out = strip(r)
        return out
    out = dict(m) if m else strip(r)
    for f in ('kg', 'ask'):
        a, b = r.get(f), (m or {}).get(f)
        if a is not None and b is not None and a != b and b:
            q = a / b
            if any(abs(q - k) < 1e-6 for k in (10, 100, 0.1, 0.01)):
                out[f] = a
    if out.get('lang') is None and r.get('lang'):
        out['lang'] = r['lang']
    return out


POLICIES = {'v1': route_v1, 'v2': route_v2}


def eq(f, a, b):
    if f in ('kg', 'ask'):
        return (a is None and b is None) or (a is not None and b is not None and abs(float(a) - float(b)) < 1e-6)
    if f == 'any':
        return bool(a) == bool(b)
    return a == b


def ok(t, p):
    l = t['label']
    for f in FIELDS:
        if l['lang'] == 'unknown' and f != 'lang':
            continue
        if f == 'lang' and l['lang'] is None:
            continue
        if not eq(f, l.get(f), p.get(f)):
            return False
    return True


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    pol = sys.argv[sys.argv.index('--policy') + 1] if '--policy' in sys.argv else 'v2'
    args = [a for a in args if a != pol]
    R, M, T = (json.load(open(f)) for f in args[:3])
    H = [POLICIES[pol](r, m) for r, m in zip(R, M)]
    if len(args) > 3:
        json.dump(H, open(args[3], 'w'))
    n = len(T)
    print(f"{pol}: exact {sum(ok(t, h) for t, h in zip(T, H))}/{n} = {sum(ok(t, h) for t, h in zip(T, H)) / n:.0%}"
          f"  | rules alone {sum(ok(t, r) for t, r in zip(T, R))}/{n}  model alone {sum(ok(t, m) for t, m in zip(T, M))}/{n}")
