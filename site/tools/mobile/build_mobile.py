"""Builds site/src/m_proto.html: the phone and tablet edition of the Dure story.

A plain vertical read. Illustrations are vector: the aerial road is drawn in aerial.py, and the dashboards and
walkthrough figures are the PC story's own SVGs, cut into phone-sized pieces (src/m_figs.json, see extract_figs.py).

Type rules
  Newsreader       everything you read: headings, paragraphs, quotes, captions
  Libre Franklin   everything you scan or operate: labels, numbers in charts, buttons, table text
  system font      only inside a phone screen (the messages), as on a real phone
"""
import json, os, re, html
from aerial import road_svg, together_svg, walker_svg, ROAD_H, TOG_H, PATHS, W as AW

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '..', 'src')
FIG = json.load(open(os.path.join(SRC, 'm_figs.json')))
MSG = json.load(open(os.path.join(HERE, 'how_msgs.json')))
TXT = json.load(open(os.path.join(HERE, 'texts.json')))


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
    ('A price and a plan to start the day', 'At 6:30 every morning, Dure AI briefs a fair price from past trades and weather and road conditions. Noor uses it to decide her strategy.'),
    ('From Tetum text to quality grading', 'An AI model trained on about 3,000 Tetum messages and 1,200 coffee bean photos helps Noor decide how to sell.'),
    ('Leverage with a blended basket', 'Coffee of every grade goes into one basket. Together, smallholders gain bargaining power.'),
    ('Interactive fair auction', 'When the basket reaches its threshold, the auction opens. Dure acts as a skilled broker: it offers buyers a reasonable starting price and adjusts it when demand is weak.'),
    ('Democracy: the essence of a cooperative', 'Once the top bid is set, each farmer decides whether to sell. No one is forced to trade; Dure helps everyone make a sound choice.'),
    ('Collective supply chain', 'Dure books the truck the moment the deal closes. Noor only leaves the agreed amount at the agreed place, and the grade is confirmed by hand at pickup.'),
    ('Simple and credible payment', 'The buyer prepays. After delivery, each farmer gets her share. Noor has mobile money; farmers without it are paid by the truck driver at the next pickup.'),
    ('Every deal builds trust', 'Dure AI builds a reputation score from the number of trades, punctuality and accurate quality. Better trust means better deals.'),
]
DUR = [4.4, 10.5, 5.4, 4.2, 4.2, 5.2, 5.6, 3.6]
# where each step's dashboard sits in its thread (after this many messages), and what it is
FIGS = {
    0: (2, lambda: price_chart() + '<figcaption>Coffee A, cleared prices · each dot is one cleared auction. <b>Today\'s reference: $2.74–2.90.</b></figcaption>'),
    1: (3, lambda: fig('how1.checks', 250, 'Four photo-visible defects checked: none, none, few, even; grade A') + '<figcaption>Four photo-visible defects from the SCA green coffee defect classification. The rest is checked by hand.</figcaption>'),
    2: (2, lambda: fig('how2.pool', 380, 'One blended lot of 2,000 kg: A 1,000, B 600, C 400')),
    3: (4, lambda: fig('how3.book', 410, 'Order book closed at 17:00; best bid $2.81 per kg')),
    4: (1, lambda: '<div class="duo">' + fig('how4.vote', 210, 'One lot: 18 yes, 4 no; A $3.14, B $2.78, C $2.11') + '</div>'),
    5: (2, lambda: fig('how5.pick', 560, 'Pickup: the grade is confirmed by hand')),
    6: (2, lambda: fig('how6.pay', 390, 'One payment in, 18 payments out') + '<figcaption><b>$4,250.85 in · 18 farmers paid</b> · each by grade and weight.</figcaption>'),
    7: (2, lambda: fig('how7.score', 420, 'Reputation: 92% grades confirmed; 14 sales, 13 of 14 on time, 1 dispute')),
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
            for m in d[side]:
                items.append((tsec(s, m['t']), side, m))
        items.sort(key=lambda x: x[0])
        at, figf = FIGS[s]
        body, lastside, n = [], None, 0
        for k, (t, side, m) in enumerate(items):
            if k == at:
                body.append(f'<figure class="dash">{figf()}</figure>')
                lastside = None
            hm = m['html']
            if side == 'F':
                sender = re.search(r'<span class="f">(.*?)</span>', hm).group(1)
                text = re.search(r'</span><span>(.*)</span>$', hm, re.S).group(1)
            else:
                sender, text = ('Buyer' if m['me'] else 'Dure AI'), hm
            mine = m['me']
            if side == 'F' and text.strip() == '[photo sent]':
                text = '<img src="assets/samples/sample_A.jpg" alt="Photo of Noor\'s coffee beans" width="200" height="150" loading="lazy">'
            if '[img]' in text:
                text = '<span class="imgs">' + ''.join(f'<img src="assets/samples/sample_{g}.jpg" alt="Grade {g} sample" loading="lazy"><i>{g}</i>' for g in 'ABC') + '</span>'
            who = ''
            if side != lastside:
                who = f'<div class="who {side}">{"Noor’s phone" if side == "F" else "A buyer’s phone · exporter, Dili"}</div>'
                lastside = side
            cls = f'msg {side}{" me" if mine else ""}'
            body.append(f'{who}<div class="{cls}" style="--i:{n}"><span class="sd">{html.escape(re.sub("<[^>]+>", "", sender)) if not mine else ("Noor" if side == "F" else "Buyer")}</span>{bubble_text(text)}</div>')
            n += 1
        if at >= len(items):
            body.append(f'<figure class="dash">{figf()}</figure>')
        t, p = HOW[s]
        out.append(f'<article class="hstep rv"><header><span class="no">{s+1}<i>/8</i></span><h3>{t}</h3><p>{p}</p></header><div class="conv">{"".join(body)}</div></article>')
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
TRAIN = re.findall(r'<img src="(assets/train/t\d+\.jpg)"[^>]*title="([^"]*)"', wa[1])


def tw_block(i, figs):
    n, h3, p, c = TW[i]
    return (f'<div class="tw rv"><div class="kick">{n}</div><h3>{h3}</h3><p>{p}</p>{figs}<p class="note">{c}</p></div>')


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

walkers = ''.join(f'<div class="wk nb" data-p="nb{i}">{walker_svg(j)}</div>' for i, (_, _, j) in enumerate(PATHS))

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
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..800;1,6..72,300..800&family=Libre+Franklin:wght@400;500;600;700&family=VT323&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="prog" aria-hidden="true"><i id="prog"></i></div>
<header class="bar"><a href="#top" class="logo" aria-label="Dure, back to top">{LOGO}</a><div class="chap" id="chap" aria-live="polite"><b>1</b>The field</div></header>

<main id="top">
<!-- 1 · the field -->
<section class="hero" data-c="1" data-t="The field">
  <div class="mark">{LOGO}</div>
  <p class="tag">Cooperate through messaging.</p>
  <p class="def"><b>Dure</b>: the Korean tradition of mutual aid between farmers.</p>
  <div class="portrait">{fig('hero.noor', None, 'Noor, a coffee farmer in Letefoho, holding a basket of ripe cherries')}</div>
</section>
<section class="txt" data-c="1" data-t="The field">
  <p class="kick rv">Ermera, Timor-Leste — the coffee highlands</p>
  <h2 class="rv">A good harvest is <em>not a good price.</em></h2>
  <p class="lead rv">Noor is an ambitious mother growing coffee on the slopes of Letefoho, Timor-Leste. She's capable. <em>But is the market treating her well?</em></p>
</section>

<!-- 2 · the buyers -->
<section class="txt" data-c="2" data-t="The buyers">
  <p class="kick rv">Where she farms</p>
  <h2 class="rv">The buyers who pay properly <em>are in Dili.</em></h2>
  <p class="rv">Ermera grows close to half of Timor-Leste's coffee.</p>
  <div class="map rv">{fig('map.route', None, 'Map: Letefoho to Gleno 19 km, Gleno to Dili 45 km, 64 km by road')}</div>
  <div class="big rv"><span class="n"><span class="cnt" data-to="98">98</span>%</span><p>of Ermera's coffee is bought by just four traders in the capital <span class="soft">(survey of 100 farmers, 2014)</span>.</p><cite>Cristovão, Bogor Agricultural University, 2015</cite></div>
</section>

<!-- 3-4 · the road, seen from above -->
<section class="road" id="road" data-c="3" data-t="The road" style="--h:{ROAD_H}">
  <div class="sky">{road_svg()}<div class="rain" aria-hidden="true"><i></i></div><div class="wk noor" data-p="roadLine">{walker_svg('#3F8B5C')}</div>
    <div class="cap" style="--y:16;--x:4"><p class="kick">Harvest season</p><p>Noor has harvested fine Timor-Leste coffee. <em>She needs cash within three days to pay her daughter's school fees.</em></p></div>
    <div class="cap r" style="--y:300;--x:46"><p class="kick">Monsoon</p><p>Timor-Leste's rainy season is notorious.</p></div>
    <div class="bang" style="--y:700;--x:4">Flood.</div>
    <div class="cap" style="--y:900;--x:40"><p>“Recent heavy rains have damaged many roads and bridges in the country, disrupting people's access to markets.”</p><cite>Asian Development Bank, Timor-Leste</cite></div>
    <div class="bang" style="--y:1150;--x:4">Landslide.</div>
    <div class="cap" style="--y:1360;--x:42"><p><em>And no truck from Dili will risk the road.</em></p></div>
    <div class="cap" style="--y:1470;--x:4" data-c="4" data-t="The buyer"><p class="kick">Unfair pricing</p><p>One trader's truck makes it up the hill. <b>He names his price.</b> She can't check it, and there's no one else to ask.</p></div>
  </div>
</section>

<!-- 5 · together -->
<section class="road tog" id="tog" data-c="5" data-t="Together" style="--h:{TOG_H}">
  <div class="sky">{together_svg()}{walkers}<div class="wk noor" data-p="mainLine">{walker_svg('#3F8B5C')}</div>
    <div class="sign" id="sign"><b id="kg">40 kg</b><span>best offer?</span></div>
    <div class="cap" style="--y:150;--x:24"><p class="kick">The magic of cooperation</p><p>Noor isn't the only one on that road. <em>Her neighbours are carrying coffee baskets too.</em></p></div>
    <div class="cap" style="--y:440;--x:40"><p class="kick">Collective bargaining</p><p>More farmers, more bargaining power. <em>Only the quantity went up, yet the price got better.</em></p></div>
  </div>
</section>
<section class="txt" data-c="5" data-t="Together">
  <p class="lead rv">This is cooperation. <b>This is Dure.</b></p>
  <div class="big rv"><span class="n"><span class="cnt" data-to="58">58</span>%</span><p>of 239 studies found that farmer organisations raised their members' incomes.</p><cite>Bizikova et al., “A scoping review of the contributions of farmers' organizations to smallholder agriculture”, Nature Food, 2020</cite></div>
  <h3 class="sub rv">How cooperatives work</h3>
  <ol class="ways">
    <li class="rv"><b>Bargaining power.</b> One farm takes the price it's given. A full truck names its own.</li>
    <li class="rv"><b>One route to market.</b> One shipment to where the fair prices are, instead of every family making the trip.</li>
    <li class="rv"><b>Buying together.</b> Seed, fertiliser and transport cost less, bought for twenty farms at once.</li>
  </ol>
  <blockquote class="rv">“Farmers who are already marginalized … require additional support before they are able to benefit.”<cite>Bizikova et al., Nature Food, 2020</cite></blockquote>
  <p class="q rv">So why isn't she benefiting from the Letefoho coffee cooperative?</p>
</section>

<!-- 6 · the catch -->
<section class="txt" data-c="6" data-t="The catch">
  <p class="kick rv">The catch</p>
  <h2 class="rv">Running a cooperative in Timor-Leste is <em>not easy.</em></h2>
  <dl class="costs">
    <div class="rv"><dt>3–4<small>years</small></dt><dd><b>Time.</b> From recruiting members to the legal paperwork, with slow administration at every step.</dd></div>
    <div class="rv"><dt>$1,000</dt><dd><b>Capital.</b> A typical coffee household earns about $250 a year. $1,000 is a lot.</dd></div>
    <div class="rv"><dt>15<small>founders</small></dt><dd><b>Structure.</b> Then a cooperative needs an assembly, elections and an audit body.</dd></div>
  </dl>
  <p class="src rv">A cooperative formed under a KOICA agricultural value-chain project, Timor-Leste; Decree-Law No. 16/2004 on cooperatives. Coffee income: The Irish Times, 2013.</p>
  <h3 class="power rv">And then, <em>power.</em></h3>
  <p class="rv">Women farmers are easily left out. For a while, it was one village; then the members and the opposition.</p>
  <ol class="three">
    <li class="rv"><b>One.</b> The cooperative copies the village pecking order.</li>
    <li class="rv"><b>Two.</b> Joining stops being a choice.</li>
    <li class="rv"><b>Three.</b> Whoever is left out undercuts prices to sink it.</li>
  </ol>
  <p class="lead rv">The benefits are real. Getting there is slow, expensive and exclusive, <em>and it ends in a fight over power.</em></p>
</section>

<!-- 7 · Dure -->
<section class="dark" data-c="7" data-t="Dure">
  <div class="tais" aria-hidden="true"></div>
  <div class="in">
    <p class="kick rv">Introducing Dure</p>
    <h2 class="rv">What if the village kept the cooperative's advantages, <em>but dropped the cooperative?</em></h2>
    <p class="lead rv">Dure works just like a cooperative. A simple text from any phone is all it takes to help Noor get a fair price.</p>
    <div class="sw rv">
      <div><h4>What stays</h4><ul><li>Pooling the harvest</li><li>Buyers bidding for the whole lot</li><li>One shared truck and pickup point</li><li>A record that earns trust</li></ul></div>
      <div class="go"><h4>What goes</h4><ul><li>A legal entity</li><li>$1,000 in share capital</li><li>Fifteen founders who must agree</li><li>A board to run, a leader to fight over</li></ul></div>
    </div>
    <p class="nokia rv"><b>Any phone. No internet. No app.</b> SMS has been around since 1992. Dure works even on an old Nokia, and its central server pairs a small AI with a rules engine, so it runs cheaply and accurately.</p>
  </div>
</section>

<!-- 8 · how it works -->
<section class="how" data-c="8" data-t="How it works">
  <p class="chapno rv">8 · How it works</p>
  <h2 class="rv">One week, <em>by text message.</em></h2>
  <p class="rv lead2">Noor writes from a basic phone, a buyer from a smartphone. Both talk to Dure; in between, Dure does the work a cooperative office would.</p>
  {thread()}
  <p class="illus">Illustrative example — names, volumes and prices are not real data.</p>
</section>

<!-- 9 · technical walkthrough -->
<section class="txt twsec" data-c="9" data-t="Technical walkthrough">
  <p class="chapno rv">9 · Technical walkthrough</p>
  {tw_block(0, PARSER)}
  {tw_block(1, '<div class="panelwrap">' + fig('wai1.photo', 380, 'Photo check: three boxes where the model found defects') + fig('wai1.list', 330, 'Black beans, mould and broken beans found; preliminary grade C') + '</div>' + '<div class="train">' + ''.join(f'<img src="{a}" alt="" title="{t}" loading="lazy" width="60" height="60">' for a, t in TRAIN) + '</div><p class="tcap">Some of our training photos · Wikimedia Commons: H. Ulver, M. C. Wright, F. Quijano (CC BY-SA 4.0); Forest &amp; Kim Starr (CC BY 3.0)</p>')}
  {tw_block(2, '<div class="panelwrap">' + fig('wai2.list', 320, 'What the opening price weighs: recent sales, buyers, road, rain, farmers asks; fair price $2.55, opens at $2.43') + fig('wai2.dots', 380, 'Each dot is one farmer\'s ask; cleared at $2.55 with 21 in') + '</div>')}
  {tw_block(3, '<div class="cards">' + fig('econ0.noor', 340, 'Noor: 92% likely to deliver') + fig('econ0.big', 340, 'A big grower: 64% likely to deliver') + '</div>' + BUYERS)}
  {tw_block(4, '<div class="cards">' + fig('econ1.blend', 340, 'Blended pool: every farmer sells here, every week, to Dili traders') + fig('econ1.fixed', 380, 'Fixed pool: one grade, a fixed buyer, every week') + '</div>')}
</section>

<!-- 10 · registry -->
<section class="txt" data-c="10" data-t="The Registry">
  <p class="chapno rv">10 · From the slope to the ministry</p>
  <h2 class="rv">An automated Registry <em>and AI policy suggestions.</em></h2>
  <p class="lead rv">A farmer Registry is important and effective, but labour-intensive and expensive to keep. Dure works as a market itself, and every deal leaves a footprint. <b>So the Registry builds itself.</b></p>
  <div class="reg rv">{fig('ledger.grid', 380, 'Daily accumulated trades per farmer')}</div>
  <div class="reg rv">{fig('ledger.chart', 380, 'Quality signals by week for the whole pool')}</div>
  <div class="reg rv">{fig('ledger.brief', 370, "Monday's brief: Lebudu, mould on 60% of photos after the rain")}</div>
  <p class="rv">Policy makers and extension officers get accurate, good-quality information on limited resources.</p>
  <p class="rv"><b>AI is not a silver bullet.</b> Noor knows farming better than Dure, so Dure stays out of how she farms. But when the extension officer visits Noor twice a year, they can make the best of it.</p>
  <a class="btn ghost rv" href="sheet.html">Open the sample Registry<span>→</span></a>
  <p class="src rv">Synthetic data for eight weeks in Letefoho.</p>
</section>

<!-- 11 · benchmark -->
<section class="txt" data-c="11" data-t="Tetum Benchmark Index">
  <p class="chapno rv">11 · Tetum Benchmark Index</p>
  <h2 class="rv">How well does AI read <em>Tetum texts?</em></h2>
  <p class="rv">Tetum is one of the languages large language models overlook most. Pairing Qwen's small AI with a rules engine, Dure reads Tetum texts close to the level of a large model.</p>
  <ul class="bench rv">{bench}</ul>
  <p class="src rv"><b>Method.</b> 60 test SMS (44 Tetum, 16 English), written by Claude Sonnet, not by us, and frozen before any reader was scored. A text counts only if crop, quantity, grade, price and intent are all right. On 80 texts we wrote ourselves: rules engine 98%, with the small model 99%. Costs are API list prices. Measured 4 Oct 2026.</p>
</section>

<!-- 12 · field problems -->
<section class="txt" data-c="12" data-t="Field problems">
  <p class="chapno rv">12 · Field problems</p>
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
  <h3 class="sub rv">Dure always has a backup plan.</h3>
  <p class="rv">A rules engine reads every text instantly, with no model to load. Only the texts it isn't sure about go to the small model. If the server or the power fails, the rules engine keeps the pool open.</p>
</section>

<section class="dark close">
  <div class="tais" aria-hidden="true"></div>
  <div class="in">
    <h2>Cooperate through <em>messaging.</em></h2>
    <a class="btn" href="demo.html">Try the demo<span>→</span></a>
    <div class="vids">{vids}</div>
    <p class="thanks">Thanks for paying attention, and enjoy the demo!</p>
  </div>
</section>
</main>
<footer class="foot"><p>Tae Yoon Moon · <a href="mailto:taeyoonmoon@uos.ac.kr">taeyoonmoon@uos.ac.kr</a></p><p>© 2026 Tae Yoon Moon. All rights reserved. Illustrations and text may not be reused without permission.</p><p><a href="index.html?full=1">View the animated version</a></p></footer>
<script>{JS}</script>
</body>
</html>
'''

open(os.path.join(SRC, 'm_proto.html'), 'w', encoding='utf-8').write(PAGE)
print('m_proto.html', len(PAGE) // 1024, 'KB')
