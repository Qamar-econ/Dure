"""Synthetic training data for the Dure message reader (coffee, Ermera).

Farmers text Dure in Tetum or English, spelling as it comes, often mixing in
Indonesian or Portuguese words and numbers (code-switching is normal in
Timor-Leste). The model turns one SMS into a fixed JSON record.

Every example here is SYNTHETIC: written from templates, with typos and
word-order changes added at random. No real farmer messages are included.

Output label (compact JSON, keys always present):
  {"lang": "tet|en|unknown|null", "crop": "coffee|other|null",
   "kg": number|null, "ask": number|null, "any": bool,
   "grade": "A|B|C|null", "yn": "yes|no|null"}
lang is null when the message carries no language (a bare number), so the
conversation keeps its language.
"""
import json, random, unicodedata

R = random.Random(11)
SYSTEM = "You read SMS from coffee farmers for Dure. Return one line of JSON only."

# ---------------------------------------------------------------- lexicon
COFFEE = {
    'tet': ['kafé', 'kafe', 'kafé maran', 'kafe maran', 'kafé kulit mutin', 'kafe kulit mutin', 'kafé ne\'e', 'kafe sira', 'kafeh', 'kopi'],
    'en': ['coffee', 'parchment', 'parchment coffee', 'dry coffee', 'cofee', 'coffe'],
}
OTHER = {
    'tet': ['batata', 'repolho', 'fehuk', 'modo', 'foos', 'batar', 'aimaris', 'snoura'],
    'en': ['potatoes', 'cabbage', 'rice', 'corn', 'beans', 'carrots'],
}
UNIT = {
    'tet': ['kilu', 'kg', 'kilo', 'kilograma', 'kilus', 'quilo'],
    'en': ['kg', 'kgs', 'kilos', 'kilo', 'kilograms'],
}
GREET = {
    'tet': ['bondia', 'bondia!', 'botarde', 'bonoite', 'olá maun', 'bondia mana', 'bondia Dure'],
    'en': ['hi', 'hello', 'good morning', 'hey', 'morning'],
}
SELL = {
    'tet': ['hau hakarak fan', 'hau atu fan', 'fan', 'hau iha', 'hakarak fan', 'hau fan', 'ami fan', "hau hakarak fa'an", "fa'an", 'hau atu faan'],
    'en': ['selling', 'i want to sell', 'i have', 'want to sell', 'got', 'sell'],
}
QUALITY = {
    'tet': [('diak', 'A'), ('diak los', 'A'), ('moos', 'A'), ('furak', 'A'), ('maran diak', 'A'), ('diak liu', 'A'),
            ('normal', 'B'), ('diak uitoan', 'B'), ('mediu', 'B'), ('metan balun', 'B'),
            ('kualidade diak', 'A'), ('aat', 'C'), ('aat uitoan', 'C'), ('metan barak', 'C'), ('bokon', 'C'), ('fuhuk', 'C'), ('fuhuk balun', 'C'), ('dodok', 'C'), ('la maran', 'C'), ('kualidade aat', 'C')],
    'en': [('good', 'A'), ('very good', 'A'), ('clean', 'A'), ('dry and clean', 'A'), ('great quality', 'A'),
           ('not bad', 'B'), ('ok', 'B'), ('average', 'B'), ('some dark beans', 'B'),
           ('bad', 'C'), ('damaged', 'C'), ('a bit mouldy', 'C'), ('wet', 'C'), ('poor', 'C'), ('lots of black beans', 'C')],
}
PRICE_PRE = {
    'tet': ['folin', 'folin minimu', 'minimu', 'fan ho folin', 'la kiak liu', 'harga'],
    'en': ['price', 'at least', 'min', 'not less than', 'for', 'minimum'],
}
ANY = {
    'tet': ['la importa', 'folin saida de\'it', 'saida de\'it bele', 'la importa folin', 'folin ruma de\'it'],
    'en': ['any price', 'any', 'whatever', 'any price is fine', "don't mind"],
}
YES = {
    'tet': ['loos', 'sin', 'loos, fan', 'diak, fan', 'ok loos', 'loos ba'],
    'en': ['yes', 'YES', 'ok sell', 'yes please', 'sure', 'yep'],
}
NO = {
    'tet': ['lae', 'lae obrigadu', 'lae, hein', 'la fan', 'lae lai'],
    'en': ['no', 'NO', 'no thanks', 'nope', "don't sell"],
}
# Tetum number words, plus the Indonesian and Portuguese numbers people also use
NUMWORD = {
    'tet': {20: ['ruanulu', 'dua puluh'], 30: ['tolunulu', 'tiga puluh'], 40: ['haatnulu', 'empat puluh', 'quarenta'],
            50: ['limanulu', 'lima puluh', 'cinquenta'], 60: ['neennulu', 'enam puluh'], 80: ['ualunulu', 'delapan puluh'],
            100: ['atus ida', 'seratus', 'cem']},
    'en': {20: ['twenty'], 30: ['thirty'], 40: ['forty'], 50: ['fifty'], 60: ['sixty'], 80: ['eighty'], 100: ['a hundred']},
}
UNKNOWN = [  # whole messages in languages Dure does not support yet
    'saya mau jual kopi {kg} kg kualitas bagus', 'halo, ada kopi {kg} kilo, harga berapa?', 'selamat pagi, kopi saya {kg} kilo',
    'bom dia, quero vender {kg} quilos de café', 'tenho café seco para vender, {kg} kg', 'boa tarde, o café está bom',
    'bonjour je vends {kg} kg de café', 'ich verkaufe {kg} kg kaffee',
    'nina kahawa kilo {kg} nzuri', 'magbebenta ako ng kape {kg} kilo', 'tôi muốn bán {kg} kg cà phê',
    'コーヒー{kg}キロ売りたいです', '我要卖咖啡{kg}公斤',
]

# ---------------------------------------------------------------- noise
def strip_acc(s):
    return unicodedata.normalize('NFC', ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

def typo(w):
    if len(w) < 4 or R.random() > .25:
        return w
    i = R.randrange(1, len(w) - 1)
    k = R.random()
    if k < .33: return w[:i] + w[i + 1:]
    if k < .66: return w[:i] + w[i] + w[i:]
    return w[:i] + w[i + 1] + w[i] + w[i + 2:] if i + 2 <= len(w) else w

def noisy(s):
    s = ' '.join(typo(w) for w in s.split(' '))
    r = R.random()
    if r < .15: s = s.upper()
    elif r < .6: s = s.lower()
    if R.random() < .4: s = strip_acc(s)
    if R.random() < .2: s = s.replace(', ', ' ').replace('. ', ' ')
    if R.random() < .15: s += R.choice(['..', '!', '?', ' pls', ' :)', '...', ' obrigadu'])
    return s.strip()

def P(x): return R.choice(x)

# ---------------------------------------------------------------- pieces
KGS = [10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 75, 80, 90, 100, 120, 150, 200]
ASKS = [.90, .95, 1.00, 1.05, 1.10, 1.15, 1.20, 1.22, 1.25, 1.28, 1.30, 1.35, 1.38, 1.40, 1.42, 1.45, 1.48, 1.50, 1.55, 1.60]

def qty(lang, kg):
    if R.random() < .14 and kg in NUMWORD[lang]:
        return f"{P(NUMWORD[lang][kg])} {P(UNIT[lang]).strip()}"
    u = P(UNIT[lang]).strip()
    if lang == 'tet' and R.random() < .35:
        return f"{u} {kg}"                      # Tetum: noun before number ("kilu 40")
    return f"{kg}{u}" if R.random() < .35 else f"{kg} {u}"

def price(lang, ask):
    d, c = int(ask), round(ask * 100) % 100
    forms = {
        'tet': [f"{d} dolar {c} sentavu" if c else f"{d} dolar", f"dolar {ask:.2f}", f"${ask:.2f}", f"{ask:.2f}",
                f"{ask:.2f}".replace('.', ','), f"{ask:.2f} dolar", f"${ask:.2f}".replace('.', ',')],
        'en': [f"${ask:.2f}", f"{ask:.2f}", f"{ask:.2f} a kilo", f"{ask:.2f}/kg", f"{ask:.2f} dollars", f"{d} dollar {c}" if c else f"{d} dollar"],
    }[lang]
    f = P(forms)
    if R.random() < .6:
        f = f"{P(PRICE_PRE[lang])} {f}"
    return f

def label(lang, crop=None, kg=None, ask=None, any_=False, grade=None, yn=None):
    return {"lang": lang, "crop": crop, "kg": kg, "ask": ask, "any": any_, "grade": grade, "yn": yn}

# ---------------------------------------------------------------- generators
def offer_full(lang):
    kg, ask = P(KGS), P(ASKS)
    has_price, has_q, has_greet = R.random() < .6, R.random() < .6, R.random() < .45
    any_ = (not has_price) and R.random() < .15
    q = P(QUALITY[lang]) if has_q else None
    other = R.random() < .1
    cropw = P(OTHER[lang]) if other else P(COFFEE[lang])
    parts = []
    if has_greet: parts.append(P(GREET[lang]) + ',')
    if lang == 'tet':
        seq = [P(SELL[lang]), cropw, qty(lang, kg)] if R.random() < .6 else [cropw, qty(lang, kg), P(SELL[lang])]
    else:
        seq = [P(SELL[lang]), qty(lang, kg), 'of ' + cropw] if R.random() < .5 else [cropw, qty(lang, kg)]
    parts += seq
    if q: parts.append((', ' if R.random() < .5 else '') + q[0])
    if has_price: parts.append((', ' if R.random() < .5 else ' ') + price(lang, ask) + (' bele?' if lang == 'tet' and R.random() < .4 else ''))
    if any_: parts.append(', ' + P(ANY[lang]))
    txt = noisy(' '.join(parts).replace(' ,', ','))
    return txt, 'none', label(lang, 'other' if other else 'coffee', kg, ask if has_price else None, any_, q[1] if q else None)

def partial(lang):
    r = R.random()
    if r < .35:   # reply to "how many kg?"
        kg = P(KGS)
        t = P([str(kg), qty(lang, kg), qty(lang, kg) + ' ' + P(COFFEE[lang])])
        if lang == 'en' and R.random() < .3: t = 'about ' + t
        if lang == 'tet' and R.random() < .3: t = t + ' de\'it'
        return noisy(t), 'kg', label(None if t.strip().isdigit() else lang, None, kg)
    if r < .75:   # reply to "lowest price?"
        ask = P(ASKS)
        t = P([f"{ask:.2f}", f"{ask}", f"{ask:.2f}".replace('.', ','), price(lang, ask)])
        return noisy(t), 'ask', label(lang if any(ch.isalpha() for ch in t) else None, None, None, ask)
    return noisy(P(ANY[lang])), 'ask', label(lang, None, None, None, True)

def decide(lang):
    y = R.random() < .55
    return noisy(P(YES[lang] if y else NO[lang])), 'decide', label(lang, yn='yes' if y else 'no')

def unknown():
    t = P(UNKNOWN).format(kg=P([30, 40, 50, 80, 100]))
    return noisy(t), P(['none', 'none', 'kg', 'ask']), label('unknown')

def real_tetum(k):
    """Short sentences from Labadain-30k+ (CC BY 4.0, native-audited Tetum web text).
    Used only as 'not an offer' messages, so the model learns to recognise ordinary Tetum."""
    import re as _re
    try: txt = open('../tetun/labadain.txt', encoding='utf-8', errors='ignore').read()
    except FileNotFoundError: return []
    skip = _re.compile(r'(kaf[eé]|kopi|kilu|kilo|\d|http|@|dolar|sentavu|folin|fa.an|sosa)', _re.I)
    sents = [x.strip() for x in _re.split(r'(?<=[.!?])\s+', txt) if 4 <= len(x.split()) <= 12 and not skip.search(x)]
    rr = random.Random(5); rr.shuffle(sents)
    return [{"expect": "none", "msg": noisy(x[:160]), "label": label('tet')} for x in sents[:k]]

def make(n):
    out = []
    for _ in range(n):
        lang = P(['tet', 'tet', 'tet', 'en', 'en'])   # Tetum weighted up: it is the local language
        r = R.random()
        if r < .5: t, e, l = offer_full(lang)
        elif r < .8: t, e, l = partial(lang)
        elif r < .92: t, e, l = decide(lang)
        else: t, e, l = unknown()
        out.append({"expect": e, "msg": t, "label": l})
    return out + real_tetum(250)

def to_chat(ex):
    return {"messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"expect={ex['expect']}\nmsg: {ex['msg']}"},
        {"role": "assistant", "content": json.dumps(ex['label'], ensure_ascii=False, separators=(',', ':'))},
    ]}

if __name__ == '__main__':
    import sys
    test_msgs = set()
    try:
        test_msgs = {(t['expect'], t['msg'].lower()) for t in json.load(open('test.json'))}
    except FileNotFoundError:
        pass
    data = make(3200)
    seen, uniq, dropped = set(), [], 0
    for d in data:
        k = (d['expect'], d['msg'])
        if (d['expect'], d['msg'].lower()) in test_msgs: dropped += 1; continue   # never train on a test message
        if k not in seen: seen.add(k); uniq.append(d)
    R.shuffle(uniq)
    with open('train.jsonl', 'w') as f:
        for d in uniq: f.write(json.dumps(to_chat(d), ensure_ascii=False) + '\n')
    print(len(uniq), 'examples;', dropped, 'dropped because they matched a test message')
    for d in uniq[:20]: print(d['expect'], '|', d['msg'], '=>', json.dumps(d['label'], ensure_ascii=False))
