"""Hybrid reader: use the rules engine's answer when it says it is sure, otherwise the small model's.
Usage: python3 hybrid.py pred_rules_test3.json pred_model_test3.json test3.json"""
import json, sys, subprocess
R, M, T = (json.load(open(f)) for f in sys.argv[1:4])
H = [ {k: v for k, v in r.items() if k != '_sure'} if r.get('_sure') else m for r, m in zip(R, M)]
out = sys.argv[1].replace('pred_rules', 'pred_hybrid'); json.dump(H, open(out, 'w'))
sure = sum(1 for r in R if r.get('_sure')); right_sure = 0
print(f'rules engine sure on {sure}/{len(R)} = {sure/len(R):.0%} of messages -> sent to model: {len(R)-sure}')
print(subprocess.run(['python3', 'score.py', out, sys.argv[3]], capture_output=True, text=True).stdout.strip())
# how often the rules engine is wrong when it says it is sure
import importlib.util
spec = importlib.util.spec_from_file_location('s', 'score.py')
F = ['lang', 'crop', 'kg', 'ask', 'any', 'grade', 'yn']
def eq(f, a, b):
    if f in ('kg', 'ask'): return (a is None and b is None) or (a is not None and b is not None and abs(float(a) - float(b)) < 1e-6)
    if f == 'any': return bool(a) == bool(b)
    return a == b
def ok(t, p):
    l = t['label']
    for f in F:
        if l['lang'] == 'unknown' and f != 'lang': continue
        if f == 'lang' and l['lang'] is None: continue
        if not eq(f, l.get(f), p.get(f)): return False
    return True
ws = sum(1 for t, r in zip(T, R) if r.get('_sure') and not ok(t, r))
print(f'rules engine wrong while sure: {ws}/{sure}')
