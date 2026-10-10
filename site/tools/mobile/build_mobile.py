"""Builds site/src/m_proto.html: the phone and tablet edition of the Dure story.

A plain vertical read. Illustrations are vector: the aerial road is drawn in aerial.py, and the dashboards and
walkthrough figures are rebuilt at phone size from the PC story's own numbers and drawings (native.py).

Type rules
  Newsreader       everything you read: headings, paragraphs, quotes, captions
  Libre Franklin   everything you scan or operate: labels, numbers in charts, buttons, table text
  system font      only inside a phone screen (the messages), as on a real phone
"""
import json, os, re, html
import native as N
from aerial import road_svg, together_svg, heap_svg, ROAD_H, TOG_H, PATHS, HEAP, W as AW

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '..', 'src')
FIG = json.load(open(os.path.join(SRC, 'm_figs.json')))
MSG = json.load(open(os.path.join(HERE, 'how_msgs.json')))
TXT = json.load(open(os.path.join(HERE, 'texts.json')))
PART = json.load(open(os.path.join(SRC, 'm_parts.json')))
BEAT = json.load(open(os.path.join(SRC, 'm_beats.json')))


def sprite(part, key, scale, cls='', attrs='', flip_ids=True):
    """a standing figure from the PC story, in its own small SVG layer"""
    x, y, w, h = part['bb']
    body = part['defs'] + part['html']
    if flip_ids:   # each copy needs its own ids
        body = re.sub(r' id="([^"]+)"', lambda m: f' id="{key}_{m.group(1)}"', body)
        body = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{key}_{m.group(1)})', body)
        body = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{key}_{m.group(1)}"', body)
    pw, ph = w * scale, h * scale
    foot = (y + h - 8) * scale - y * scale   # px from the top of the box to the feet
    return (f'<div class="sp {cls}" {attrs} style="width:{pw:.0f}px;height:{ph:.0f}px;--fx:{pw/2:.1f}px;--fy:{foot:.1f}px">'
            f'<svg viewBox="{x:.1f} {y:.1f} {w:.1f} {h:.1f}" width="{pw:.0f}" height="{ph:.0f}" aria-hidden="true">{body}</svg></div>')



def fig(key, mw=None, label=''):
    s = FIG[key]
    s = s.replace('font-family="Atkinson Hyperlegible Next"', 'font-family="Libre Franklin"')
    s = s.replace('class="fig"', f'class="fig" aria-label="{html.escape(label)}"' + (f' style="max-width:{mw}px"' if mw else ''), 1)
    return s


# ------------------------------------------------------------------ the morning price chart, re-plotted at phone size from the PC chart's own data
def price_chart():
    src = FIG['how0.price']
    band = re.search(r'id="[^"]*pBand"[^>]*d="([^"]+)"', src).group(1)
    mid = re.search(r'id="[^"]*pMid"[^>]*d="([^"]+)"', src).group(1)
    dots = [(float(a), float(b)) for a, b in re.findall(r'<circle class="pd"[^>]*cx="([\d.]+)" cy="([\d.]+)"', src)]
    # PC chart space: x 94..540 -> weeks 1..12; y 145.6 = $3.04, 300.3 = $2.65
    X0, X1, Y0, Y1 = 46, 344, 30, 190
    fx = lambda x: X0 + (x - 94.3) / (539.8 - 94.3) * (X1 - X0)
    val = lambda y: 3.04 + (y - 145.56) / (300.32 - 145.56) * (2.65 - 3.04)
    fy = lambda y: Y1 - (val(y) - 2.6) / (3.1 - 2.6) * (Y1 - Y0)
    def tr(d):
        nums = re.findall(r'[-\d.]+', d)
        out, i = '', 0
        for tok in re.findall(r'[MLHVCSZ]|[-\d.]+', d):
            if tok in 'MLHVCSZ':
                out += tok + ' '
            else:
                v = float(tok)
                out += (f'{fx(v):.1f} ' if i % 2 == 0 else f'{fy(v):.1f} ')
                i += 1
        return out
    g = ''
    for v in (2.65, 2.84, 3.04):
        y = Y1 - (v - 2.6) / (3.1 - 2.6) * (Y1 - Y0)
        g += f'<path d="M{X0} {y:.1f} H{X1}" stroke="#D8CCB2"/><text x="{X0-6}" y="{y+4:.1f}" text-anchor="end">${v:.2f}</text>'
    for w, lab in ((1, 'week 1'), (4, '4'), (8, '8'), (12, '12')):
        x = X0 + (w - 1) / 11 * (X1 - X0)
        g += f'<text x="{x:.1f}" y="{Y1+20}" text-anchor="middle">{lab}</text>'
    pts = ''.join(f'<circle cx="{fx(x):.1f}" cy="{fy(y):.1f}" r="3.6" fill="#A9783A" stroke="#fff" stroke-width="1"/>' for x, y in dots)
    return (f'<svg class="fig chart" viewBox="0 0 360 236" role="img" aria-label="Coffee A cleared prices over twelve weeks; today\'s reference $2.74 to $2.90">'
            f'<g font-family="Libre Franklin" font-size="11.5" fill="#5B5345">{g}</g>'
            f'<path d="M{X0} {Y1} H{X1}" stroke="#1F3A40" stroke-width="1.4"/>'
            f'<path d="{tr(band)}" fill="#4E8B5C" opacity=".2"/><path d="{tr(mid)}" stroke="#4E8B5C" stroke-width="2.4" fill="none"/>{pts}</svg>')


# ------------------------------------------------------------------ How it works as one message thread
HOW = [
    ('A price and a plan to start the day', 'At 6:30 Dure sends a fair price, built from past trades, weather and the road.'),
    ('From Tetum text to quality grading', 'Noor writes in her own words and sends one photo. Dure reads both.'),
    ('Leverage with a blended basket', 'Every grade goes into one lot. Together, smallholders have bargaining power.'),
    ('Interactive fair auction', 'When the lot is full, buyers bid. Dure sets a reasonable opening price.'),
    ('Autonomy: each farmer decides', 'Each farmer decides whether to sell at the final price. No one is forced.'),
    ('Collective supply chain', 'Dure books one truck. The grade is confirmed by hand at pickup.'),
    ('Simple and credible payment', 'The buyer prepays; after delivery each farmer gets her share.'),
    ('Every deal builds trust', 'Trades, punctuality and accurate quality build a reputation score.'),
]
# the phone edition's messages, cut to what each one has to say (None: dropped, it repeats another)
SAY = {
    ('0', 'F', 0): 'Bondia! This week, per kg<hr>A $3.17–3.23 · B $2.80–2.86 · C $2.12–2.18<hr>Selling? Reply in your own words.',
    ('0', 'F', 1): '<b>Suggestion</b><br>Heavy rain, Gleno road flooded: only 4 buyers.<br>Ask at least $3.17; photo before 10:00.',
    ('0', 'B', 0): None,
    ('0', 'B', 1): '<b>Buyer brief · 06:30</b><br>~1,800 kg expected · A 45% · B 35% · C 20%<br>Suggested bid <b>$2.69–2.94/kg</b>',
    ('1', 'F', 1): 'Got it ✓<hr>Coffee · 40 kg · grade A · ask $2.84/kg<hr>Now send one photo of your beans.',
    ('1', 'F', 3): '<b>First look: grade A</b> (93%)<br>A person checks every sack at pickup.',
    ('2', 'F', 0): 'You\'re in this week\'s pool · 190 of 2,000 kg',
    ('2', 'F', 1): '<b>Pool closed</b> · 1,890 kg · 22 farms<br>Bidding opens $2.74/kg, closes 17:00',
    ('2', 'B', 0): '<b>New pool</b> · 1,890 kg · 22 farms<br>First-look photo grades:',
    ('2', 'B', 2): None,
    ('3', 'F', 0): '<b>Auction closed</b> · $2.81/kg<br>A $3.14 · B $2.78 · C $2.11',
    ('3', 'B', 0): '<b>Auction open</b> until 17:00 · opens $2.74/kg<br>Reply with your price.',
    ('3', 'B', 4): '<b>You won</b> at $2.81/kg',
    ('4', 'F', 0): '<b>Sold ✓</b> 40 kg · A · $125.60<br>Pickup Thu 07:00, church',
    ('4', 'B', 0): '<b>Lot locked</b> · 1,530 kg · 18 farms<br><span class="paybtn">Pay $4,250.85</span>',
    ('4', 'B', 1): 'Paid ✓ Truck booked: Thu 07:00, Letefoho church.',
    ('5', 'F', 1): 'Got it ✓ Sack #0412, truck at 07:00.',
    ('5', 'F', 2): '<b>Picked up ✓</b> 40 kg<br>Grade A confirmed by hand[sack]',
    ('5', 'B', 0): '<b>Picked up ✓</b> 1,530 kg, hand-checked',
    ('6', 'F', 0): '<b>Paid ✓</b> +$125.60 to your mobile wallet',
    ('6', 'B', 0): '<b>Delivered ✓</b> 1,530 kg to your warehouse',
    ('6', 'B', 1): 'Your prepayment is released: 18 farmers paid.',
    ('7', 'F', 1): '<b>Your record</b> on time, grade matched<br>Likely to deliver: 83% (was 79%)',
    ('7', 'B', 1): '<b>Your record</b> 9 buys, all prepaid on time',
}
DUR = [4.4, 10.5, 5.4, 4.2, 4.2, 5.2, 5.6, 3.6]
# where each step's dashboard sits in its thread (after this many messages), and what it is
FIGS = {   # each step's dashboard, condensed to its essentials
    0: (0, lambda: N.mx_price(price_chart())),
    1: (0, N.mx_photo),
    2: (0, N.mx_pool),
    3: (0, N.mx_book),
    4: (0, N.mx_vote),
    5: (0, lambda: ''),
    6: (0, N.mx_pay),
    7: (0, N.mx_score),
}


def tsec(s, t):
    return float(t[1:]) if t[0] == 'a' else float(t[1:]) + 1.5 if t[0] == 'p' else float(t) * DUR[s]


def bubble_text(h):
    h = re.sub(r'<br>\s*-{4,}\s*<br>', '<hr>', h)
    h = re.sub(r'-{4,}<br>|<br>-{4,}', '<hr>', h)
    h = h.replace('<span class="paybtn">', '<span class="pay">')
    return h


def thread():
    out = []
    for s in range(8):
        d = MSG[str(s)]
        items = []
        for side in 'FB':
            for q, m in enumerate(d[side] if side == 'F' else []):
                key = (str(s), side, q)
                if key in SAY:
                    if SAY[key] is None:
                        continue
                    m = dict(m, html=(f'<span class="f">Dure AI</span><span>{SAY[key]}</span>' if side == 'F' else SAY[key]))
                items.append((tsec(s, m['t']), side, m))
        items.sort(key=lambda x: x[0])
        at, figf = FIGS[s]
        cols, n = {'F': [], 'B': []}, 0
        for k, (t, side, m) in enumerate(items):
            hm = m['html']
            if side == 'F':
                sender = re.search(r'<span class="f">(.*?)</span>', hm).group(1)
                text = re.search(r'</span><span>(.*)</span>$', hm, re.S).group(1)
            else:
                sender, text = ('Buyer' if m['me'] else 'Dure AI'), hm
            mine = m['me']
            if side == 'F' and text.strip() == '[photo sent]':
                text = PART['photoA'].replace('<svg ', '<svg class="ph" role="img" aria-label="Noor\'s photo of her coffee beans in a basket" ', 1)
            if '[sack]' in text:   # the truck driver's photo of her sack at pickup, as in the demo
                text = text.replace('[sack]', PART['sackA'].replace('<svg class="ph"', '<svg class="ph" role="img" aria-label="The driver\'s photo of sack #0412: 40 kg, grade A, checked"', 1))
            if '[img]' in text:
                text = '<span class="imgs">' + ''.join(f'<span>{PART["photo" + g].replace("<svg ", f"<svg class=ph aria-label=\"Grade {g} photo\" ", 1)}<i>{g}</i></span>' for g in 'ABC') + '</span>'
            cls = f'msg {side}{" me" if mine else ""}'
            cols[side].append(f'<div class="{cls}" style="--i:{n}"><span class="sd">{html.escape(re.sub("<[^>]+>", "", sender)) if not mine else ("Noor" if side == "F" else "Buyer")}</span>{bubble_text(text)}</div>')
            n += 1
        # Noor's phone: Dure on the left, Noor on the right. The buyers show up in what Dure tells her and in the dashboards
        phone = (f'<div class="abar"><span class="av">D</span><div><b>Dure AI</b><small>SMS · +670 7700 3873</small></div><i class="dots" aria-hidden="true"></i></div>'
                 f'<div class="chat">{"".join(cols["F"])}</div>')
        body = [phone]
        f = figf()
        dash = f'<figure class="dash">{f}</figure>' if f else ''   # what Dure did behind those messages, below the phone
        t, p = HOW[s]
        out.append(f'<article class="hstep rv"><header><span class="no">{s+1}<i>/8</i></span><h3>{t}</h3><p>{p}</p></header><div class="conv">{"".join(body)}</div>{dash}</article>')
    return ''.join(out)


# ------------------------------------------------------------------ the page
TAIS = ("data:image/svg+xml;utf8," +
        "<svg xmlns='http://www.w3.org/2000/svg' width='88' height='28' viewBox='0 0 44 14'><rect width='44' height='14' fill='%239A3326'/><rect x='0' width='4' height='14' fill='%23241A16'/><rect x='6' width='1.6' height='14' fill='%23E4B64C'/><rect x='9' width='1.2' height='14' fill='%23F1E3C6'/><rect x='16' width='12' height='14' fill='%23241A16'/><path d='M22 1 L26 7 L22 13 L18 7Z' fill='%23E4B64C'/><path d='M22 4 L24 7 L22 10 L20 7Z' fill='%23241A16'/><rect x='31' width='1.2' height='14' fill='%23F1E3C6'/><rect x='34' width='1.6' height='14' fill='%23E4B64C'/><rect x='38' width='3' height='14' fill='%23241A16'/></svg>")

LOGO = ('<svg viewBox="-2 0 336 130" aria-label="Dure."><text x="0" y="104" font-family="Newsreader" font-size="130" font-weight="680" letter-spacing="-5.8" fill="#1F3A40" style="font-variation-settings:\'opsz\' 72">Dure</text>'
        '<g transform="translate(316 89)"><g transform="rotate(-28)"><ellipse rx="11.5" ry="15" fill="#6B4226"/><ellipse cx="-3.6" cy="-4.5" rx="4" ry="6.4" fill="#8F5E38" opacity=".55"/>'
        '<path d="M0.6 -13.6 C -5.2 -7.4 5.2 -1.6 0 4 C -4.2 8.4 1.2 11.2 0.2 13.8" stroke="#2B180C" stroke-width="2.2" fill="none" stroke-linecap="round"/></g></g></svg>')

wa, ec = TXT['wa'], TXT['ec']
def head(hh):
    h3 = re.search(r'<h3>(.*?)</h3>', hh).group(1)
    p = re.search(r'<p>(.*?)</p>', hh).group(1)
    c = re.search(r'<cite>(.*?)</cite>', hh)
    n = re.search(r'<div class="n">(.*?)</div>', hh).group(1)
    return n, h3, p, (c.group(1) if c else '')
TW = [head(x) for x in wa + ec]
# the phone edition says each step in fewer words; citations stay as they are
SHORT = ["A small model (Qwen2.5-0.5B) plus a rules engine, trained on about 3,000 Tetum and English texts. Dialects and spelling slips are fine.",
         "A small vision model, trained on 1,200 real bean photos, sorts coffee into three grades on SCA defect criteria. It is exactly right 79% of the time; a hand check at pickup sets the final grade.",
         "Dure estimates a fair price from recent sales, buyers, road and rain. Bidding opens a little under it.",
         "Trust comes from trades, punctuality and steady quality, not farm size. Floods and other force majeure never count.",
         "The blended pool is an open market with scale. The fixed pool links part of trusted farmers' output to steady buyers."]
TW = [(n, h, SHORT[i], c) for i, (n, h, p, c) in enumerate(TW)]
TRAIN = re.findall(r'<img src="(assets/train/t\d+\.jpg)"[^>]*title="([^"]*)"', wa[1])


TWNO = {0: 1, 1: 2, 3: 3, 4: 4}   # 'makes the market' is left out: How it works already shows it


def tw_block(i, figs):
    n, h3, p, c = TW[i]
    n = f'Technical walkthrough — {TWNO[i]}'
    note = f'<p class="note">{c}</p>' if c else ''
    return (f'<div class="tw rv"><div class="twt"><div class="kick">{n}</div><h3>{h3}</h3><p>{p}</p>{note}</div><div class="twf">{figs}</div></div>')


PARSER = ('<div class="panel parser"><div class="ph"><span>Dure AI · message parser</span><span><i class="ok"></i>Tetum · 2 spellings fixed</span></div>'
          '<div class="raw"><mark>bondia!</mark> <mark class="k0">kafe</mark> <mark class="k1">40kilu</mark> <mark class="k2">diak los..</mark> <mark class="k3">fan 2.84</mark> <mark>bele? ok</mark></div>'
          '<dl>' + ''.join(f'<div><dt><span>{a}</span></dt><dd><small>{b}</small><b>{c}</b></dd></div>' for a, b, c in [
              ('kafe', 'Crop', 'coffee'), ('40kilu', 'Quantity', '40 kg'), ('diak los..', 'Grade', 'A · preliminary'),
              ('fan 2.84', 'Ask (hidden)', '$2.84 / kg'), ('bondia! bele? ok', 'Intent', 'offer to sell')]) +
          '</dl><div class="reply"><small>reply sent</small><span>Diak! Haruka foto ida? (a photo?)</span></div></div>')

BUYERS = ('<div class="panel buyers"><div><small>Buyers too · likely to pay on time</small><b>Exporter, Dili</b><span>9 purchases · 9 paid on time · 0 disputes</span></div><strong>88%</strong></div>'
          '<p class="est">Dure AI\'s estimate, ± a few points. Land and volume aren\'t counted.</p>')

BENCH = [('Dure', 'rules engine + small model', 80, 'works with no server · $0.01 per 1,000 texts', 'me'),
         ('Claude Haiku 4.5', 'large model, over the internet', 87, 'needs server and network · $0.53–2.15 per 1,000 texts', ''),
         ('Small model alone', 'Qwen2.5-0.5B, fine-tuned', 75, '~2 s per text · $0.02 per 1,000 texts', ''),
         ('Rules engine alone', 'no model, instant', 70, 'works with no server · $0', ''),
         ('Untrained small model', 'Qwen2.5-0.5B, examples only', 7, 'why training matters', 'dim')]
def bench_row(a, b, v, m, k):
    lab = f'<span class="nm">{a}</span><span class="pc">{v}%</span>'
    # a bar too short to hold its labels carries them beside it
    inner, out = ('', f'<span class="out">{lab}</span>') if v < 30 else (lab, '')
    return f'<li class="{k}"><div class="bar"><i style="width:{v}%">{inner}</i>{out}</div><div class="meta">{b} · {m}</div></li>'
bench = ''.join(bench_row(*r) for r in BENCH)

VIDS = [('981bf_9D56U', 'Meet the founder'), ('7GsosgZ9X-s', 'Product demo'), ('WSlZaQtR0n0', 'Technical walkthrough')]
vids = ''.join(f'<button class="vid" data-id="{i}" type="button"><img src="https://i.ytimg.com/vi/{i}/hqdefault.jpg" alt="" loading="lazy" width="480" height="360"><span>{t}</span></button>' for i, t in VIDS)

walkers = ''.join(sprite(PART['fnb'][i % len(PART['fnb'])], f'nb{i}', .2, 'walker nb front', f'data-p="nb{i}"') for i in range(len(PATHS)))

CSS = open(os.path.join(HERE, 'mobile.css')).read().replace('__TAIS__', TAIS)
JS = open(os.path.join(HERE, 'mobile.js')).read()

PAGE = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#F2EADA">
<title>Dure · Cooperate through messaging</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..800;1,6..72,300..800&family=Libre+Franklin:wght@400;500;600;700&family=VT323&family=Gochi+Hand&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
{N.SYMBOLS}
<div class="prog" aria-hidden="true"><i id="prog"></i></div>
<header class="bar"><a href="#top" class="logo" aria-label="Dure, back to top">{LOGO}</a><div class="chap" id="chap" aria-live="polite"><b>1</b>The field</div></header>

<main id="top">
<!-- 1 · the field -->
<section class="hero" data-c="1" data-t="The field">
  <div class="portrait">{fig('hero.noor', None, 'Noor, a coffee farmer in Letefoho, holding a basket of ripe cherries')}</div>
  <div class="portrait wide">{fig('hero.tab', None, 'Noor in her coffee field below the mountains').replace('<svg ', '<svg preserveAspectRatio="xMinYMax slice" ', 1)}</div>
  <div class="htxt">
    <div class="mark">{LOGO}</div>
    <p class="tag">Cooperate through messaging.</p>
    <p class="def"><b>Dure</b>: the Korean tradition of mutual aid between farmers.</p>
  </div>
</section>
<section class="txt" data-c="1" data-t="The field">
  <h2 class="rv">A good harvest is <em>not a good price.</em></h2>
  <p class="lead rv">Noor grows coffee on the slopes of Letefoho, Timor-Leste. <em>Is the market treating her well?</em></p>
</section>

<!-- 2 · the buyers -->
<section class="txt split" data-c="2" data-t="The buyers">
  <h2 class="rv">The buyers are mostly in the capital, <em>Dili.</em></h2>
  <div class="map rv">{fig('map.route', None, 'Map: Letefoho to Gleno 19 km, Gleno to Dili 45 km, 64 km by road')}</div>
  <div class="big rv"><span class="n"><span class="cnt" data-to="98">98</span>%</span><p>of Ermera's coffee is bought by just four traders in the capital <span class="soft">(survey of 100 farmers, 2014)</span>.</p><cite>Cristovão, Bogor Agricultural University, 2015</cite></div>
</section>

<!-- 3-5 · what happens to Noor, and what changes when she isn't alone -->
<section class="txt" data-c="3" data-t="The road">
  {N.story_beats()}
</section>
<section class="txt" data-c="5" data-t="Together">
  <h2 class="rv">What if her neighbours <em>sold with her?</em></h2>
  <div class="rv">{N.alone_together()}</div>
  <p class="lead rv">This is cooperation. <b>This is Dure.</b></p>
  <div class="big rv"><span class="n"><span class="cnt" data-to="58">58</span>%</span><p>of 239 studies found that farmer organisations raised their members' incomes.</p><cite>Bizikova et al., “A scoping review of the contributions of farmers' organizations to smallholder agriculture”, Nature Food, 2020</cite></div>
  <p class="q rv">So why isn't she benefiting from the Letefoho coffee cooperative?</p>
</section>

<!-- 6 · the catch -->
<section class="txt" data-c="6" data-t="The catch">
  <p class="kick rv">The catch</p>
  <h2 class="rv">Starting a cooperative in Timor-Leste is <em>not easy.</em></h2>
  <dl class="costs">
    <div class="rv"><dt>3–4<small>years</small></dt><dd><b>Time.</b> Recruiting, then paperwork.</dd></div>
    <div class="rv"><dt>$1,000</dt><dd><b>Capital.</b> A coffee household earns about $250 a year.</dd></div>
    <div class="rv pwr"><dt><em>power.</em><small>and then</small></dt><dd><b>Power.</b> Women like Noor are easily left out.</dd></div>
  </dl>
  <p class="src rv">KOICA value-chain cooperative, Timor-Leste; Decree-Law No. 16/2004; The Irish Times, 2013.</p>
  <figure class="scene spl rv">{PART['split']}<figcaption>Joining stops being a choice. Whoever is left out <b>undercuts prices to sink it.</b></figcaption></figure>
  <p class="lead rv">So Noor still sells alone, <em>at the trader's price.</em></p>
</section>

<!-- 7 · Dure -->
<section class="dark first" data-c="7" data-t="Dure">
  <div class="tais" aria-hidden="true"></div>
  <div class="in">
    <h2 class="rv">What if the village kept the cooperative's advantages, <em>but dropped the cooperative?</em></h2>
  </div>
  <div class="phoneNoor">
    <svg class="pn" viewBox="-86 -536 256 410" role="img" aria-label="Noor holding up her basic phone"><defs>{PART['tais']}</defs>
      {PART['fphone']}</svg>
    <div class="pt"><p class="kick">Introducing</p><div class="dmark">{LOGO.replace('fill="#1F3A40"', 'fill="#F4EBDA"')}</div><h3>Cooperating through <em>messages.</em></h3></div>
  </div>
  <div class="in">
    <div class="swtabs rv">{N.tabs([('What stays', '<ul class="swl"><li>Pooling the harvest</li><li>Buyers bidding for the whole lot</li><li>One shared truck and pickup point</li><li>A record that earns trust</li></ul>'), ('What goes', '<ul class="swl go"><li>A legal entity</li><li>$1,000 in share capital</li><li>Fifteen founders who must agree</li><li>A board to run, a leader to fight over</li></ul>')], 'What changes')}</div>
    <div class="sw rv">
      <div><h4>What stays</h4><ul><li>Pooling the harvest</li><li>Buyers bidding for the whole lot</li><li>One shared truck and pickup point</li><li>A record that earns trust</li></ul></div>
      <div class="go"><h4>What goes</h4><ul><li>A legal entity</li><li>$1,000 in share capital</li><li>Fifteen founders who must agree</li><li>A board to run, a leader to fight over</li></ul></div>
    </div>
    <p class="nokia rv"><b>Any phone. No internet. No app.</b> Dure works even on an old Nokia.</p>
  </div>
</section>

<div class="night">   <!-- from the first tais band to the end, the page stays dark -->
<!-- 8 · how it works -->
<section class="how" data-c="8" data-t="How it works">
  <p class="chapno rv">8 · How it works</p>
  <h2 class="rv">One week, <em>by text message.</em></h2>
  <p class="rv lead2">Noor's week, on her basic phone. Behind each message, Dure does a cooperative office's work with the buyers.</p>
  <div class="hsteps">{thread()}</div>
  <p class="illus">Illustrative example — names, volumes and prices are not real data.</p>
</section>

<!-- 9 · technical walkthrough -->
<section class="txt twsec" data-c="9" data-t="Technical walkthrough">
  <p class="chapno rv">9 · Technical walkthrough</p>
  {tw_block(0, PARSER)}
  {tw_block(1, N.grade_compact() + '<div class="train">' + ''.join(f'<img src="{a}" alt="" title="{t}" loading="lazy" width="60" height="60">' for a, t in TRAIN) + '</div><p class="tcap">Some of our training photos · Wikimedia Commons: H. Ulver, M. C. Wright, F. Quijano (CC BY-SA 4.0); Forest &amp; Kim Starr (CC BY 3.0)</p>')}
  {tw_block(3, N.tabs([('Noor · 2 ha', N.rep_compact('noor')), ('Big grower · 30 ha', N.rep_compact('big'))], 'Two farmers') + BUYERS)}
  {tw_block(4, N.tabs([('Blended pool', N.blend()), ('Fixed pool', N.fixed())], 'Two markets'))}
</section>

<!-- 10 · registry -->
<section class="txt" data-c="10" data-t="The Registry">
  <p class="chapno rv">10 · From the slope to the ministry</p>
  <h2 class="rv">An automated Registry <em>and AI policy suggestions.</em></h2>
  <p class="lead rv">A farmer Registry is costly to keep by hand. Every Dure deal leaves a record, <b>so the Registry builds itself.</b></p>
  <div class="reg rv">{N.tabs([('1 · Trades', N.ledger()), ('2 · Analysis', N.qchart()), ("3 · Monday's brief", N.brief())], 'The Registry')}</div>
  <p class="rv"><b>AI is not a silver bullet.</b> Noor knows farming better than Dure. Dure helps the extension officer make the most of two visits a year.</p>
  <a class="btn ghost rv" href="sheet.html">Open the sample Registry<span>→</span></a>
  <p class="src rv">Synthetic data for eight weeks in Letefoho.</p>
</section>

</div>
<section class="dark close">
  <div class="tais" aria-hidden="true"></div>
  <div class="in">
    <h2>Cooperate through <em>messaging.</em></h2>
    <a class="btn" href="demo.html">Try the demo<span>→</span></a>
    <div class="vids">{vids}</div>
    <p class="thanks">Thanks for paying attention, and enjoy the demo!</p>
  </div>
</section>
<div class="night more-info">   <!-- for readers who want the numbers behind it -->
<!-- 11 · benchmark -->
<section class="txt" data-c="11" data-t="Tetum Benchmark Index">
  <p class="chapno rv">For the curious · Tetum Benchmark Index</p>
  <h2 class="rv">How well does AI read <em>Tetum texts?</em></h2>
  <p class="rv">Large models overlook Tetum. A small model plus a rules engine gets Dure close to a large model.</p>
  <ul class="bench rv">{bench}</ul>
  <p class="src rv"><b>Method.</b> 60 test SMS (44 Tetum, 16 English), written by Claude Sonnet, not by us, and frozen before any reader was scored. A text counts only if crop, quantity, grade, price and intent are all right. On 80 texts we wrote ourselves: rules engine 98%, with the small model 99%. Costs are API list prices. Measured 4 Oct 2026.</p>
</section>

<!-- 12 · field problems -->
<section class="txt" data-c="12" data-t="Field problems">
  <p class="chapno rv">For the curious · Field problems</p>
  <h2 class="rv">What are the real <em>field problems?</em></h2>
  <div class="risks">
    <div class="rv"><h4>The road washes out.</h4><p>Dure books the truck and the pickup point. It can't fix the road, and doesn't pretend to.</p></div>
    <div class="rv"><h4>Who sees the records?</h4><p>Farmers' names and numbers stay with Dure. The ministry's Registry shows pseudonymous IDs and village totals, and only for farmers who said yes.</p></div>
    <div class="rv"><h4>The power or the server goes down.</h4><p>The rules engine keeps taking offers by text. The small model rechecks them later, and any change goes back to the farmer to confirm.</p></div>
  </div>
  <h3 class="sub rv">Electricity is a real problem in Timor-Leste.</h3>
  <dl class="costs ev">
    <div class="rv"><dt>40%</dt><dd>of firms had power cuts in a year, losing <b>9.4%</b> of sales.<cite>World Bank Enterprise Survey, 2015</cite></dd></div>
    <div class="rv"><dt>24 h</dt><dd>outages in Viqueque. Dili's hospital runs on generators each time.<cite>Tatoli, 2022–23</cite></dd></div>
    <div class="rv"><dt>36%</dt><dd>of Dili customers never report an outage.<cite>TANE survey, 2022</cite></dd></div>
  </dl>
</section>

</div>
</main>
<footer class="foot"><p>Tae Yoon Moon · <a href="mailto:taeyoonmoon@uos.ac.kr">taeyoonmoon@uos.ac.kr</a></p><p>© 2026 Tae Yoon Moon. All rights reserved. Illustrations and text may not be reused without permission.</p><p><a href="index.html?full=1">View the animated version</a></p></footer>
<script>{JS}</script>
</body>
</html>
'''

open(os.path.join(SRC, 'm_proto.html'), 'w', encoding='utf-8').write(PAGE)
print('m_proto.html', len(PAGE) // 1024, 'KB')
