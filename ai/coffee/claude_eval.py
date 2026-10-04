"""Big-model baseline: the same task, the same tests, sent to the Claude API.
Usage: ANTHROPIC_API_KEY=... python3 claude_eval.py <model> <test.json> <out.json>
Prints accuracy input via score.py separately; here we record latency and token use for cost per 1,000 messages."""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

KEY = os.environ['ANTHROPIC_API_KEY']
PRICE = {'claude-haiku-4-5-20251001': (1.0, 5.0), 'claude-sonnet-5-5': (2.0, 10.0)}   # USD per million tokens (in, out), platform.claude.com pricing, 2026-10-04
SYSTEM = ("You read SMS from coffee farmers in Ermera, Timor-Leste for Dure, an SMS selling service. "
          "Messages are in Tetum or English, often with typos and Indonesian or Portuguese words mixed in. "
          "Return one line of JSON only, with exactly these keys: "
          "lang (\"tet\", \"en\", \"unknown\" for any other language, or null if the message has no words), "
          "crop (\"coffee\", \"other\" or null), kg (number or null), ask (lowest acceptable price in US dollars per kg, number or null), "
          "any (true only if any price is fine), grade (\"A\" good/clean, \"B\" ok/average/some defects, \"C\" bad/mouldy/wet/many black beans, or null), "
          "yn (\"yes\", \"no\" or null). If lang is unknown, set every other field to null/false. "
          "The line 'expect=' says which question the farmer is answering: none, kg, ask (lowest price) or decide (yes/no); "
          "a bare number answers that question.")
FEW = [("none", "hau hakarak fan kafe kilu 60, aat uitoan, 1 dolar 10 sentavu",
        '{"lang":"tet","crop":"coffee","kg":60,"ask":1.1,"any":false,"grade":"C","yn":null}'),
       ("decide", "yes", '{"lang":"en","crop":null,"kg":null,"ask":null,"any":false,"grade":null,"yn":"yes"}')]

def one(model, t):
    msgs = []
    for e, m, a in FEW:
        msgs += [{"role": "user", "content": f"expect={e}\nmsg: {m}"}, {"role": "assistant", "content": a}]
    msgs.append({"role": "user", "content": f"expect={t['expect']}\nmsg: {t['msg']}"})
    body = json.dumps({"model": model, "max_tokens": 1024, "system": SYSTEM, "messages": msgs}).encode()
    for attempt in range(4):
        try:
            t0 = time.time()
            req = urllib.request.Request('https://api.anthropic.com/v1/messages', data=body, headers={
                'x-api-key': KEY, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
            with urllib.request.urlopen(req, timeout=60) as r:
                out = json.loads(r.read())
            ms = (time.time() - t0) * 1000
            txt = ''.join(b.get('text', '') for b in out['content']).strip()
            try: p = json.loads(txt[txt.index('{'): txt.rindex('}') + 1])
            except Exception: p = {}
            return p, ms, out['usage']['input_tokens'], out['usage']['output_tokens']
        except Exception as e:
            time.sleep(2 + attempt * 3)
    return {}, None, 0, 0

if __name__ == '__main__':
    model, tf, of = sys.argv[1], sys.argv[2], sys.argv[3]
    T = json.load(open(tf))
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(lambda t: one(model, t), T))
    json.dump([r[0] for r in res], open(of, 'w'), ensure_ascii=False)
    lat = sorted(r[1] for r in res if r[1]); ti = sum(r[2] for r in res); to = sum(r[3] for r in res)
    pi, po = PRICE[model]
    cost1k = (ti * pi + to * po) / 1e6 / len(T) * 1000
    meta = {'model': model, 'n': len(T), 'median_ms': lat[len(lat) // 2], 'p90_ms': lat[int(len(lat) * .9)],
            'in_tokens_per_msg': ti / len(T), 'out_tokens_per_msg': to / len(T), 'usd_per_1000_msgs': round(cost1k, 3)}
    json.dump(meta, open(of.replace('.json', '.meta.json'), 'w'), indent=1)
    print(json.dumps(meta))
