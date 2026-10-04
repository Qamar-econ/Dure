"""Dure daily brief writer.

A model reads the facts table (facts.json, built from the register by facts.js) and writes the brief.
It decides what matters; it may only use numbers that are in the table.
A validator then checks every sentence: each number must appear in the table, village names must be real,
and no sentence may claim a cause (the register shows where and when, not why). A failed sentence is dropped;
if the headline fails or too little survives, the sheet falls back to the template brief.

  python3 brief.py qwen     # Qwen2.5-1.5B-Instruct on CPU (Apache-2.0), the one Dure ships
  python3 brief.py claude   # Claude Haiku 4.5 as a comparison (needs ANTHROPIC_API_KEY in the environment)
"""
import json, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
F = json.load(open(os.environ.get('FINDINGS') or os.path.join(HERE, 'findings.json')))
FIND = {f['id']: f for f in F['findings']}; VILLAGES = F['villages']

SYSTEM = """You write the 06:00 daily brief for an agriculture ministry officer about a coffee farmers' pool in Letefoho, Timor-Leste.
Code has already ranked the findings from the register, most unusual first. Write them up plainly for an officer who has two minutes.

Rules:
- The headline is about the first finding. Put findings about the same village together.
- Every sentence lists the ids of the findings it uses in "cite". Use only numbers from those findings, copied exactly. Do not compute new numbers.
- Say which way things moved correctly: a share that went from 10% to 70% rose.
- Do not explain causes in the headline, "changed" or "prices". Never write "because", "due to", "caused", "led to".
- Do not advise farmers. "review" holds questions an extension officer could look into, each starting with "Whether", with no numbers, citing the findings they follow from.
- Plain English, short sentences. No words like "significant", "alarming", "indicating".
- Keep it short: at most 4 items in changed, 2 in prices, 3 in review.
- Reply with JSON only, with the keys headline, changed, prices, review, as in the example.

Example, for a different pool:
FINDINGS: F7: Hera, week 3: photos flagged insect damage 40% (week 1: 5%; the other four villages in week 3: 6%) | F9: Hera, week 3: 22 kg per offer, -30% against week 1 (31 kg) | F2: Last auction (9 Mar): the lot cleared at $1.10/kg, against $1.12 at the first auction (2 Mar)
{"headline": {"text": "Hera: insect damage on 40% of photos in week 3, against 5% in week 1 and 6% in the other villages.", "cite": ["F7"]},
 "changed": [{"text": "Hera's farms offered 22 kg each in week 3, 30% less than in week 1.", "cite": ["F9"]}],
 "prices": [{"text": "The last lot cleared at $1.10/kg, against $1.12 at the first auction.", "cite": ["F2"]}],
 "review": [{"text": "Whether an extension visit to Hera this week could check the coffee for insect damage?", "cite": ["F7"]}]}
"""

CAUSAL = re.compile(r"\b(because|due to|caused|causing|led to|leads to|result of|as a result|owing to|thanks to)\b", re.I)
ADVICE = re.compile(r"\b(should|must|need to|have to|recommend)\b", re.I)
MEASURES = {r'\bmou?ld\w*|\bblack\b': ['mould'], r'\binsect\w*': ['insect'], r'\bdr(y|ying|ied)\b': ['drying'], r'\bgrade c\b': ['grade c'],
            r'\bs(at|it|itting) out\b': ['sat out'], r'\bvolume|\bkg\b|\bless coffee': ['kg per offer']}
NUM = re.compile(r"(?<![A-Za-z0-9-])-?\$?\d+(?:[.,]\d+)?")


def numbers(s):
    out = []
    for m in NUM.finditer(s.replace('F', ' F') if False else re.sub(r'\bF\d+\b', '', s)):
        try: out.append(float(m.group().replace('$', '').replace(',', '.')))
        except ValueError: pass
    return out


def check(text, cite, review=False):
    bad = []
    if not isinstance(text, str) or not text.strip(): return ['empty']
    if re.search(r'one sentence|the most important change, its village|Whether \.\.\.', text): return ['copied the instructions instead of writing']
    if CAUSAL.search(text) and not review: bad.append(f'claims a cause ("{CAUSAL.search(text).group()}")')
    if review:
        if numbers(re.sub(r'\bweek \d\b', '', text)): bad.append('numbers in a review question')
        if ADVICE.search(text): bad.append(f'gives advice ("{ADVICE.search(text).group()}")')
        if not text.strip().lower().startswith('whether'): bad.append('not phrased as a question for an expert')
        for v in re.findall(r'\b[A-Z][a-z]{3,}\b', text):
            if v.endswith(('u', 'o', 'ai', 'au')) and v not in VILLAGES + ['Letefoho', 'Ermera']: bad.append(f'unknown place {v}')
        cite = [c for c in (cite or []) if isinstance(c, str) and c in FIND]
        if not cite: bad.append('cites no finding')
        src = ' '.join(FIND[c]['text'].lower() for c in cite)
        for word, keys in MEASURES.items():   # a question about drying must follow from a drying finding, and so on
            if re.search(word, text, re.I) and not any(k in src for k in keys): bad.append(f'asks about "{re.search(word, text, re.I).group()}" but cites no finding about it')
        vs = {FIND[c]['village'] for c in cite} - {None}
        for v in VILLAGES:
            if v in text and v not in vs: bad.append(f'names {v} without citing a {v} finding')
        for v in vs:
            if v not in text: bad.append(f'cites a {v} finding but asks about somewhere else')
        return bad
    cite = [c for c in (cite or []) if isinstance(c, str)]
    unknown = [c for c in cite if c not in FIND]
    if unknown: bad.append(f'cites findings that do not exist ({", ".join(unknown)})')
    if not cite: bad.append('cites no finding')
    allowed = [abs(float(n)) for c in cite if c in FIND for n in FIND[c]['nums']]
    for n in numbers(text):
        if not any(abs(abs(n) - a) < 0.006 for a in allowed): bad.append(f'number {n:g} is not in the findings it cites')
    dirs = {FIND[c].get('dir', 0) for c in cite if c in FIND} - {0}
    if dirs == {1} and re.search(r'\b(drop|dropped|fell|fall|falls|down|decrease|decreased|lower|less|fewer|declin\w*)\b', text, re.I): bad.append('says it fell; the finding rose')
    if dirs == {-1} and re.search(r'\b(rose|rise|rises|up|increase|increased|higher|jump\w*)\b', text, re.I): bad.append('says it rose; the finding fell')
    if re.search(r'\b(significant\w*|alarming|indicat\w*|dramatic\w*)\b', text, re.I): bad.append('judgement word')
    # grade prices: a sentence about one grade may not quote another grade's price
    gp = {}
    for c in cite:
        if c in FIND:
            for g, v in re.findall(r'\b([ABC]) \$(\d+\.\d+)', FIND[c]['text']): gp[g] = float(v)
    named = set(re.findall(r'\bgrade ([ABC])\b', text, re.I))
    if gp and len(named) == 1:
        g0 = named.pop().upper()
        for n in numbers(text):
            for g, v in gp.items():
                if g != g0 and abs(n - v) < .006 and abs(n - gp.get(g0, -1)) > .006: bad.append(f'${n:.2f} is the grade {g} price, not grade {g0}')
    vs = {FIND[c]['village'] for c in cite if c in FIND} - {None}
    for v in VILLAGES:
        if v in text and v not in vs: bad.append(f'names {v} without citing a {v} finding')
    for v in re.findall(r'\b[A-Z][a-z]{3,}\b', text):
        if v.endswith(('u', 'o', 'ai', 'au')) and v not in VILLAGES + ['Letefoho', 'Ermera']: bad.append(f'unknown place {v}')
    return bad


def validate(b):
    rep = {'checked': 0, 'kept': 0, 'numbers_checked': 0, 'dropped': []}
    def keep(item, where, review=False):
        if review and isinstance(item, str): text, cite = item, []
        elif review: text, cite = (item or {}).get('text', ''), (item or {}).get('cite', [])
        else: text, cite = (item or {}).get('text', ''), (item or {}).get('cite', [])
        rep['checked'] += 1; rep['numbers_checked'] += len(numbers(text or ''))
        p = check(text, cite, review)
        if p: rep['dropped'].append({'where': where, 'text': text, 'why': p}); return None
        rep['kept'] += 1
        vs = sorted({FIND[c]['village'] for c in cite if c in FIND} - {None})
        return {'text': text, 'cite': cite} if review else {'text': text, 'cite': cite, 'village': vs[0] if len(vs) == 1 else None}
    out = {'headline': keep(b.get('headline'), 'headline') if isinstance(b.get('headline'), dict) else None}
    for k in ('changed', 'prices'):
        out[k] = [x for x in (keep(i, k) for i in (b.get(k) or []) if isinstance(i, dict)) if x]
    seen = set(); revs = []
    for i in (b.get('review') or [])[:6]:
        k = json.dumps(i, sort_keys=True)
        if k not in seen: seen.add(k); revs.append(i)
    out['review'] = [x for x in (keep(i, 'review', True) for i in revs if isinstance(i, (str, dict))) if x][:3]
    out['headline_text'] = out['headline']['text'] if out['headline'] else None
    rep['usable'] = bool(out['headline']) and len(out['changed']) >= 1 and len(out['review']) >= 1
    # coverage: the three most unusual village findings must reach the officer. If the model left one out, code adds it as written.
    cited = {c for x in [out['headline']] + out['changed'] if x for c in x['cite']}
    top = sorted([f for f in F['findings'] if f['village']], key=lambda f: -f['score'])[:3]
    rep['added_by_code'] = 0
    for f in top:
        if f['id'] not in cited:
            out['changed'].append({'text': f['text'] + '.', 'cite': [f['id']], 'village': f['village'], 'by': 'code'}); rep['added_by_code'] += 1
    return out, rep


def parse_json(t):
    t = re.sub(r'^```(?:json)?|```$', '', t.strip(), flags=re.M).strip()
    t = t[t.find('{'):]
    try: return json.loads(t[:t.rfind('}') + 1])
    except ValueError: pass
    # cut off mid-list (the model ran out of tokens or started repeating): keep every complete item, close the brackets
    for end in [m.end() for m in re.finditer(r'\}', t)][::-1]:
        for tail in (']}', '}', ']}]}'):
            try: return json.loads(t[:end] + tail)
            except ValueError: continue
    raise ValueError('no JSON object found')


def run_qwen():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_num_threads(int(os.environ.get('THREADS', '2')))
    path = os.path.join(HERE, 'qwen15')
    tok = AutoTokenizer.from_pretrained(path); m = AutoModelForCausalLM.from_pretrained(path, dtype=torch.bfloat16).eval()
    msgs = [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': F['text']}]
    ids = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors='pt')
    att = torch.ones_like(ids)
    t0 = time.time()
    with torch.no_grad(): out = m.generate(ids, attention_mask=att, max_new_tokens=600, do_sample=False, repetition_penalty=1.05)
    text = tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True)
    n_out = out.shape[1] - ids.shape[1]
    return text, {'model': 'Qwen2.5-1.5B-Instruct (Apache-2.0), bf16, CPU', 'seconds': round(time.time() - t0), 'tokens_in': ids.shape[1], 'tokens_out': int(n_out), 'cost_usd': 0}


def run_gguf(size):
    """4-bit GGUF through llama.cpp: the way it would run on a pickup-hub laptop."""
    from llama_cpp import Llama
    path = os.path.join(HERE, 'gguf', f'qwen2.5-{size}-instruct-q4_k_m.gguf')
    m = Llama(model_path=path, n_ctx=4096, n_threads=int(os.environ.get('THREADS', '1')), seed=0, verbose=False)
    t0 = time.time()
    r = m.create_chat_completion(messages=[{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': F['text']}],
                                 temperature=0, max_tokens=800, repeat_penalty=1.0, response_format={'type': 'json_object'})
    u = r['usage']
    return r['choices'][0]['message']['content'], {'model': f'Qwen2.5-{size.upper()}-Instruct (Apache-2.0), 4-bit GGUF, llama.cpp, CPU', 'file_mb': round(os.path.getsize(path) / 1e6),
            'seconds': round(time.time() - t0), 'tokens_in': u['prompt_tokens'], 'tokens_out': u['completion_tokens'], 'cost_usd': 0}


def run_claude(model='claude-haiku-4-5-20251001'):
    import urllib.request
    body = json.dumps({'model': model, 'max_tokens': 1200, 'system': SYSTEM, 'messages': [{'role': 'user', 'content': F['text']}]}).encode()
    req = urllib.request.Request('https://api.anthropic.com/v1/messages', data=body, headers={
        'x-api-key': os.environ['ANTHROPIC_API_KEY'], 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
    t0 = time.time(); r = json.load(urllib.request.urlopen(req, timeout=90))
    text = ''.join(b['text'] for b in r['content'] if b['type'] == 'text'); u = r['usage']
    cost = u['input_tokens'] * 1e-6 + u['output_tokens'] * 5e-6   # Haiku 4.5: $1 / $5 per million tokens
    return text, {'model': model, 'seconds': round(time.time() - t0), 'tokens_in': u['input_tokens'], 'tokens_out': u['output_tokens'], 'cost_usd': round(cost, 4)}


def revalidate(which):
    """Re-run only the checker on a saved model output (after the checker changes; the model is not called again)."""
    tag = os.environ.get('TAG', ''); p = os.path.join(HERE, f'brief_{which}{tag}.json'); res = json.load(open(p))
    out, rep = validate(parse_json(open(os.path.join(HERE, f'raw_{which}{tag}.txt')).read()))
    res.update(validation=rep, brief=out, findings=F['findings']); json.dump(res, open(p, 'w'), indent=1, ensure_ascii=False); return res


if __name__ == '__main__' and len(sys.argv) > 2 and sys.argv[2] == '--recheck':
    r = revalidate(sys.argv[1]); print(json.dumps(r['validation'], indent=1)); sys.exit()
if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'qwen'
    text, meta = run_qwen() if which == 'qwen' else run_gguf(which) if which in ('1.5b', '3b') else run_claude()
    open(os.path.join(HERE, f'raw_{which}{os.environ.get("TAG", "")}.txt'), 'w').write(text)
    try: b = parse_json(text)
    except Exception as e: b = {}; meta['parse_error'] = str(e)
    out, rep = validate(b)
    res = {'hash': F['hash'], 'written_at': 'Monday 27 July 2026, 06:00', 'findings': F['findings'], 'meta': meta, 'validation': rep, 'brief': out}
    json.dump(res, open(os.path.join(HERE, f'brief_{which}{os.environ.get("TAG", "")}.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(res, indent=1, ensure_ascii=False))
