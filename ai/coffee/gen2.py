"""Targeted synthetic data for a short follow-up fine-tune of the Dure reader (adapter v2).

The first generator (gen.py) left gaps that the development sets (tests 2 and 5) exposed. This adds templates for them, then mixes
in a replay sample of the original training data so the model does not forget what it already reads well:
  - prices in cents only ("140 sentavus", "125 cent", "90 sen"), decimal commas, and today's price range ($2-3.5/kg)
  - Tetum messages with English or Portuguese words mixed in ("ok deit", "bom dia", "qualquer presu"): still Tetum
  - more quality phrases in Tetum and English, and offers with no quality words at all (grade stays null, never guessed)
  - more crops that are not coffee, and messages with two crops (only the coffee counts)
  - questions and remarks that are not offers (price questions, "not selling this week")
  - greetings that contain "good" ("good morning") without saying anything about quality
Every example is synthetic. Nothing here is copied from any test set; the de-duplication below also drops any exact test message.
Usage: python3 gen2.py  -> train2.jsonl"""
import json, random
import gen
from gen import P, noisy, label, qty, to_chat, NUMWORD, UNIT

R = random.Random(23)
gen.R = R

COFFEE = {'tet': ['kafe', 'kafé', 'kafe maran', 'kafe pergaminho', 'kafe parchment', 'kafeh', 'kafe hau nian', "ha'u nia kafe", 'kafe ne\'e'],
          'en': ['coffee', 'parchment', 'coffe', 'cofee', 'dry parchment', 'my coffee', 'cof']}
OTHER = {'tet': ['batata', 'fehuk', 'modo', 'batar', 'hudi', 'fore', 'aifarina', 'kakau', 'koko', 'lakeru', 'repolho', 'foos', 'tomate'],
         'en': ['maize', 'cassava', 'bananas', 'cocoa', 'beans', 'rice', 'potatoes', 'cabbage', 'pumpkin', 'peanuts']}
GREET = {'tet': ['bondia', 'botarde', 'bonoite', 'bom dia', 'boa tarde', 'bondia maun', 'botarde mana', 'olá', 'bondia senhor'],
         'en': ['hi', 'hello', 'good morning', 'good afternoon', 'good evening', 'morning sir', 'hello Dure']}
SELLW = {'tet': ["hau fan", "hau hakarak fa'an", "ha'u iha", "hau iha", "fa'an", "ami fan", "hau sei fa'an", "hau ba fa'an"],
         'en': ['i sell', 'i want to sell', 'i have', 'selling', 'can sell', 'i would like to sell']}
Q = {'tet': [('diak', 'A'), ('diak los', 'A'), ('diak liu', 'A'), ('moos', 'A'), ('maran no moos', 'A'), ('kualidade diak', 'A'),
             ('la iha bolor', 'A'), ('grade A', 'A'), ('klase A', 'A'), ('A', 'A'),
             ('normal', 'B'), ('ok deit', 'B'), ('kualidade ok', 'B'), ('fuan metan uitoan', 'B'), ('metan balun', 'B'),
             ('diak uitoan', 'B'), ('grade B', 'B'), ('B', 'B'), ('mediu', 'B'),
             ('aat', 'C'), ('metan barak', 'C'), ('bokon', 'C'), ('basa', 'C'), ('basa uitoan', 'C'), ('bolor', 'C'), ('fuhuk', 'C'),
             ('la maran', 'C'), ('aat los', 'C'), ('grade C', 'C'), ('C', 'C')],
     'en': [('good', 'A'), ('good quality', 'A'), ('clean and dry', 'A'), ('very good', 'A'), ('grade A', 'A'), ('no mould', 'A'),
            ('ok quality', 'B'), ('normal quality', 'B'), ('average', 'B'), ('a few black beans', 'B'), ('some black beans', 'B'),
            ('mostly ok', 'B'), ('grade B', 'B'),
            ('wet', 'C'), ('mouldy', 'C'), ('many black beans', 'C'), ('lots of black beans', 'C'), ('damaged', 'C'), ('poor', 'C'),
            ('a bit wet', 'C'), ('grade C', 'C')]}
ANY = {'tet': ["folin saida deit", "presu saida de'it", "laimporta", "qualquer presu", "presu hira deit", "folin hotu-hotu ok", "la iha minimu"],
       'en': ['any price', 'whatever price', 'any price ok', 'no minimum', 'whatever is fine']}
PRE = {'tet': ['folin', 'presu', 'minimu', 'folin minimu', 'hau hakarak', 'fan', ''], 'en': ['price', 'minimum', 'lowest', 'at least', 'for', '']}
ASKS = [0.85, 0.9, 0.95, 1.0, 1.1, 1.15, 1.2, 1.25, 1.3, 1.32, 1.35, 1.38, 1.4, 1.45, 1.48, 1.5,
        2.1, 2.25, 2.5, 2.6, 2.75, 2.8, 2.84, 2.9, 3.0, 3.1, 3.15, 3.2]
KGS = [5, 8, 10, 12, 15, 18, 20, 22, 25, 28, 30, 33, 35, 40, 45, 48, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 110, 120, 130, 140,
       150, 160, 180, 200, 220, 250, 300, 400]


def price(lang, a):
    d, c = int(a), round(a * 100) % 100
    cents = round(a * 100)
    forms = [f"{a:.2f}", f"{a:.2f}".replace('.', ','), f"${a:.2f}", f"{a:.2f}$"]
    small = a < 2   # people quote cents only for prices under two dollars
    if lang == 'tet':
        forms += [f"{d} dolar {c}" if c else f"{d} dolar", f"dolar {a:.2f}", f"{a:.2f} dolar"]
        if small: forms += [f"{cents} sentavu", f"{cents} sentavus", f"{cents} sentavos", f"sentavu {cents}", f"{cents} sen"]
    else:
        forms += [f"{a:.2f} dollar", f"{a:.2f} per kg", f"{d} dollar {c}" if c else f"{d} dollar"]
        if small: forms += [f"{cents} cents", f"{cents} cent"]
    f = P(forms)
    pre = P(PRE[lang])
    return (pre + ' ' + f).strip()


def offer(lang):
    kg, a = P(KGS), P(ASKS)
    has_p, has_q, greet = R.random() < .7, R.random() < .5, R.random() < .4
    any_ = (not has_p) and R.random() < .3
    q = P(Q[lang]) if has_q else None
    crop2 = R.random() < .12
    parts = [P(GREET[lang]) + ','] if greet else []
    cw = P(COFFEE[lang])
    if lang == 'tet':
        mix = R.random() < .35   # code-switching: English or Portuguese words inside a Tetum message
        if R.random() < .5:
            parts += [P(SELLW[lang]), cw, qty(lang, kg)]
        else:
            parts += [cw, qty(lang, kg)]
        if crop2:
            parts += ['no', P(OTHER[lang]), qty(lang, P(KGS))]
        if q:
            parts.append(q[0] if not (mix and q[1] == 'B') else P(['ok deit', 'ok', 'normal']))
        if has_p:
            parts.append(price(lang, a) + P(['', '', ' bele?', ' minimu', ' ka liu', ' deit']))
        if any_:
            parts.append(P(ANY[lang]))
        if mix and R.random() < .5:
            parts.append(P(['obrigadu', 'obrigada', 'please', 'thanks', 'ok?', 'hehe']))
    else:
        if R.random() < .5:
            parts += [P(SELLW[lang]), qty(lang, kg), P(['', 'of ']) + cw]
        else:
            parts += [cw, qty(lang, kg)]
        if crop2:
            parts += ['and', P(OTHER[lang]), qty(lang, P(KGS))]
        if q:
            parts.append(q[0])
        if has_p:
            parts.append(price(lang, a))
        if any_:
            parts.append(P(ANY[lang]))
    txt = noisy(' '.join(parts).replace(' ,', ','))
    gq = q[1] if q else None
    if lang == 'tet' and q and mix and q[1] == 'B':
        gq = 'B'
    return txt, 'none', label(lang, 'coffee', kg, a if has_p else None, any_, gq)


def other_crop(lang):
    kg = P(KGS)
    parts = [P(SELLW[lang])] if R.random() < .5 else []
    parts += [P(OTHER[lang]), qty(lang, kg)]
    a = None
    if R.random() < .4:
        a = P([0.3, 0.4, 0.5, 0.6, 0.75, 1.0, 2.0])
        parts.append(price(lang, a))
    return noisy(' '.join(parts)), 'none', label(lang, 'other', kg, a)


def not_offer(lang):
    if lang == 'tet':
        t, crop = P([("presu kafe ohin hira?", 'coffee'), ("ohin folin kafe hira maun?", 'coffee'), ("hau la fa'an kafe semana ne'e", 'coffee'),
                     ("hau seidauk iha kafe", 'coffee'), ("kafe hau seidauk maran", 'coffee'), ("bainhira mak kamioneta mai?", None),
                     ("osan seidauk tama", None), ("obrigadu barak", None), ("hau iha Gleno ohin", None), ("presu ohin hira?", None)])
    else:
        t, crop = P([("what is the coffee price today?", 'coffee'), ("not selling coffee this week", 'coffee'), ("my coffee is not dry yet", 'coffee'),
                     ("when does the truck come?", None), ("money not received yet", None), ("thank you", None),
                     ("how much is the price this week?", None), ("is it raining in Gleno?", None)])
    return noisy(t), 'none', label(lang, crop)


def answers(lang):
    r = R.random()
    if r < .35:
        kg = P(KGS)
        t = P([qty(lang, kg), f"{kg}", (f"hau iha {kg}kg" if lang == 'tet' else f"only {kg} kg"), (f"kilu {kg} mak iha" if lang == 'tet' else f"about {kg} kilos")])
        return noisy(t), 'kg', label(None if t.strip().isdigit() else lang, None, kg)
    if r < .75:
        a = P(ASKS)
        t = price(lang, a)
        bare = not any(ch.isalpha() for ch in t)
        return noisy(t), 'ask', label(None if bare else lang, None, None, a)
    return noisy(P(ANY[lang])), 'ask', label(lang, None, None, None, True)


def make(n):
    out = []
    for _ in range(n):
        lang = P(['tet', 'tet', 'tet', 'en', 'en'])
        r = R.random()
        f = offer if r < .55 else other_crop if r < .65 else not_offer if r < .78 else answers
        t, e, l = f(lang)
        out.append({'expect': e, 'msg': t, 'label': l})
    return out


if __name__ == '__main__':
    tests = set()
    for name in ('test.json', 'test2.json', 'test3.json', 'test5.json', 'test6.json'):
        try:
            tests |= {(t['expect'], t['msg'].lower().strip()) for t in json.load(open(name))}
        except FileNotFoundError:
            pass
    new = make(900)
    old = [json.loads(l) for l in open('train.jsonl')]
    rr = random.Random(7); rr.shuffle(old)
    replay = old[:450]   # replay so the model keeps what it already reads well
    seen, rows, dropped = set(), [], 0
    for d in new:
        k = (d['expect'], d['msg'].lower().strip())
        if k in tests: dropped += 1; continue
        if k in seen: continue
        seen.add(k); rows.append(to_chat(d))
    rows += replay
    R.shuffle(rows)
    with open('train2.jsonl', 'w') as f:
        for d in rows: f.write(json.dumps(d, ensure_ascii=False) + '\n')
    print(len(rows), 'examples (', len(rows) - len(replay), 'new +', len(replay), 'replay );', dropped, 'dropped as test messages')
    for d in rows[:12]: print(d['messages'][1]['content'].replace('\n', ' | '), '=>', d['messages'][2]['content'])
