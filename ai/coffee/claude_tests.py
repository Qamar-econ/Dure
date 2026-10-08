"""Ask Claude to write SMS a coffee farmer in Ermera might send, without showing it
our generator or our test set. The result is a second, more independent test set
(still synthetic: written by a model, not by farmers). Labels are reviewed by hand
afterwards (see review notes in test2_review.md). The API key comes from $ANTHROPIC_API_KEY only."""
import json, os, urllib.request

KEY = os.environ['ANTHROPIC_API_KEY']
PROMPT = r"""You are helping build a test set for an SMS service used by smallholder coffee farmers in Ermera, Timor-Leste.
Farmers sell dried parchment coffee through a pooled weekly auction. Every Monday at 06:30 they get prices per kg
(grade A 1.40-1.48, B 1.22-1.30, C 0.94-1.02 US dollars). The service asks them: what are you selling, how many kg,
and the lowest price per kg they would accept (or "any price"). Later it may ask YES/NO.

Write 70 realistic SMS messages a farmer might send. Mix:
- about 40 in Tetum (the way people really text: short, no accents, typos, mixing in Indonesian or Portuguese words or numbers, dollar/cent amounts written many ways),
- about 18 in English (non-native, short, typos),
- about 6 in other languages the service does NOT support (Indonesian, Portuguese, etc., whole message in that language),
- some are replies to a single question (just a quantity, just a price, just yes/no), say which question they answer.
Vary everything: greetings or not, word order, quality words (good/clean/dry vs some black beans vs mouldy/wet), other crops sometimes.
Do not use the exact phrase "bondia! kafe 40kilu diak los.. fan 1.45 bele?".

For each message give the label the service should extract, as JSON with exactly these keys:
expect: "none" (a fresh message), "kg" (answering how many kg), "ask" (answering lowest price), or "decide" (answering yes/no)
msg: the SMS text
lang: "tet", "en", "unknown" (unsupported language) or null (message has no words, e.g. just "55")
crop: "coffee", "other", or null
kg: number or null
ask: lowest acceptable price in US dollars per kg as a number (e.g. 1.45), or null
any: true only if they say any price is fine
grade: "A" if they describe it as good/clean/very good, "B" for ok/average/some defects, "C" for bad/mouldy/wet/many black beans, else null
yn: "yes", "no" or null (only for expect=decide)
For unsupported-language messages, set lang "unknown" and every other field null/false.

Return only a JSON array of 70 objects, no commentary."""

def call(model, prompt, max_tokens=12000):
    body = json.dumps({"model": model, "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request('https://api.anthropic.com/v1/messages', data=body, headers={
        'x-api-key': KEY, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())

if __name__ == '__main__':
    out = call('claude-sonnet-5-5', PROMPT)
    txt = ''.join(b.get('text', '') for b in out['content'])
    txt = txt[txt.index('['): txt.rindex(']') + 1]
    rows = json.loads(txt)
    raw = [{'expect': r['expect'], 'msg': r['msg'],
            'label': {k: r.get(k) for k in ['lang', 'crop', 'kg', 'ask', 'any', 'grade', 'yn']}} for r in rows]
    for r in raw: r['label']['any'] = bool(r['label']['any'])
    json.dump(raw, open('test2_raw.json', 'w'), ensure_ascii=False, indent=1)
    print(len(raw), 'messages; usage', out['usage'])
