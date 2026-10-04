"""Synthetic register for the Letefoho pool: three weeks, six auctions (6–23 July 2026).
Writes src/sheet_data.json with RAW inputs only (farmers, offers, bids). Every derived figure
(who is in, prices, payments, signals, the brief) is computed in the page by sheet_core.js.
All data is synthetic and labelled as such."""
import json, random
R = random.Random(13)

VILL = ['Ducurai', 'Lacau', 'Lebudu', 'Hatugau', 'Eraulo']
COUNT = {'Ducurai': 19, 'Lacau': 18, 'Lebudu': 17, 'Hatugau': 18, 'Eraulo': 18}
FIXED = {7: 'Ducurai', 12: 'Ducurai', 31: 'Lacau', 41: 'Lacau', 52: 'Lebudu', 55: 'Lebudu', 58: 'Lebudu', 60: 'Lebudu',
         63: 'Hatugau', 71: 'Hatugau', 79: 'Eraulo'}
AUCTIONS = ['2026-07-06', '2026-07-09', '2026-07-13', '2026-07-16', '2026-07-20', '2026-07-23']
RAIN_FROM = 3   # index of the first auction after the 13–15 July rain (Thu 16 July)

# ---- farmers ----
pool = []
for v in VILL: pool += [v] * COUNT[v]
for v in FIXED.values(): pool.remove(v)
R.shuffle(pool)
farmers = []
for i in range(1, 91):
    v = FIXED.get(i) or pool.pop()
    ha = 2.0 if i == 41 else round(R.choice([.5, .8, 1, 1, 1.2, 1.5, 1.5, 2, 2, 2.5, 3]), 1)
    farmers.append({'id': f'LTF-{i:03d}', 'village': v, 'ha': ha,
                    'tet': R.random() < .82, 'model_share': R.random()})
consent_no = set(R.sample([f['id'] for f in farmers if f['id'] != 'LTF-041'], 29))   # 61 of 90 say yes
for f in farmers: f['consent'] = 'N' if f['id'] in consent_no else 'Y'

# ---- offers: ~23 farms per auction, every farmer offers at least once ----
# each auction takes about 23 offers, in proportion to village size (19/18/17/18/18 of 90)
QUOTA = {'Ducurai': 5, 'Lacau': 4, 'Lebudu': 5, 'Hatugau': 5, 'Eraulo': 4}
byv = {v: [f['id'] for f in farmers if f['village'] == v] for v in VILL}
slots = {a: [] for a in range(6)}
for v in VILL:
    ids = byv[v][:]; R.shuffle(ids); k = 0
    for a in range(6):
        for _ in range(QUOTA[v] + (1 if v == 'Lacau' and a % 2 else 0)):
            slots[a].append(ids[k % len(ids)]); k += 1
FV = {f['id']: f for f in farmers}

def grade_draw(v, a):
    lebudu_wet = v == 'Lebudu' and a >= RAIN_FROM
    if lebudu_wet: p = [.20, .28, .52]
    elif v == 'Lebudu': p = [.52, .34, .14]
    else: p = [.52, .32, .16]
    x = R.random()
    return 'A' if x < p[0] else 'B' if x < p[0] + p[1] else 'C'

offers = []
for a, ids in slots.items():
    for fid in sorted(ids):
        f = FV[fid]; v = f['village']
        base = f['ha'] * R.uniform(24, 34) + 12
        if v == 'Lebudu' and a >= RAIN_FROM: base *= R.uniform(.64, .74)
        kg = int(round(base / 5) * 5) or 10
        g = grade_draw(v, a)
        if fid == 'LTF-041': g = 'A'
        # what the photo shows
        mould_p = .55 if (v == 'Lebudu' and a >= RAIN_FROM) else .07
        flags = []
        if R.random() < mould_p: flags.append('black/mould')
        if R.random() < .05: flags.append('insect')
        if R.random() < (.30 if (v == 'Lebudu' and a >= RAIN_FROM) else .08): flags.append('uneven drying')
        if R.random() < .04: flags.append('debris')
        # AI preliminary grade disagrees with the inspector ~6% of the time
        ai = g
        if R.random() < .06: ai = {'A': 'B', 'B': R.choice('AC'), 'C': 'B'}[g]
        conf = R.randint(72, 95)
        # farmer's minimum: farmers price their coffee by last month's prices, not by this week's rain
        band = {'A': (1.30, 1.45), 'B': (1.12, 1.27), 'C': (.86, .99)}[g]
        if v == 'Lebudu' and a >= RAIN_FROM and g == 'C': band = (1.00, 1.18)
        ask = round(R.uniform(*band) / .01) * .01
        if fid == 'LTF-041': kg, ask = 40, 1.45
        offers.append({'auction': a, 'date': AUCTIONS[a], 'farmer': fid, 'kg': kg, 'ask': round(ask, 2),
                       'ai_grade': ai, 'conf': conf, 'flags': ', '.join(flags), 'grade': g,
                       'read_by': 'model' if f['model_share'] < .3 else 'rules', 'lang': 'TET' if f['tet'] else 'EN',
                       'on_time': R.random() < .94})

# ---- buyers' bids on each lot (blended lot price per kg) ----
BUYERS = [('BUY-01', 'Exporter, Dili'), ('BUY-02', 'Roaster, Dili'), ('BUY-03', 'Exporter, Dili'), ('BUY-04', 'Café chain, Dili'), ('BUY-05', 'Exporter, Dili')]
# buyers bid on quality: the lot price is what the grade mix on offer is worth at the week's grade prices
TARGET = [{'A': 1.45, 'B': 1.27, 'C': .97}, {'A': 1.46, 'B': 1.28, 'C': .98}, {'A': 1.46, 'B': 1.28, 'C': .98},
          {'A': 1.44, 'B': 1.26, 'C': .95}, {'A': 1.45, 'B': 1.27, 'C': .96}, {'A': 1.46, 'B': 1.28, 'C': .97}]
bids = []
for a in range(6):
    O = [o for o in offers if o['auction'] == a]
    top = round(sum(o['kg'] * TARGET[a][o['grade']] for o in O) / sum(o['kg'] for o in O), 2)
    open_ = round(top - .06, 2)
    for r, b in enumerate(R.sample(range(5), 5)):
        bids.append({'auction': a, 'buyer': BUYERS[b][0], 'bid': round(top - r * R.choice([.01, .02]), 2), 'open': open_})

json.dump({'auctions': AUCTIONS, 'rain': ['2026-07-13', '2026-07-15'], 'farmers': farmers, 'offers': offers,
           'buyers': [{'id': b, 'name': n} for b, n in BUYERS], 'bids': bids,
           'weights': {'A': 1.12, 'B': 0.98, 'C': 0.75}},
          open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), '..', 'src', 'sheet_data.json'), 'w'), separators=(',', ':'))
print(len(farmers), 'farmers,', len(offers), 'offers,', len(bids), 'bids')
