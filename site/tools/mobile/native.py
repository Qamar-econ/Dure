"""Phone-native versions of the PC story's dashboards.

The PC figures are drawn for a 1440px stage; cropping them for a phone leaves cut panels, tiny type and
stray edges. Each figure here is rebuilt at phone size from the same numbers, colours and type:
text is real HTML (crisp, wraps, scales with the reader's font size), geometry is a small SVG.
Character art (avatars, Noor at pickup, buyer icons) is reused from the PC drawings by re-framing the
vector, never by screenshot."""
import json, os, random, re

HERE = os.path.dirname(__file__)
FIG = json.load(open(os.path.join(HERE, '../../src/m_figs.json'), encoding='utf-8'))
try:
    ZOOM = json.load(open(os.path.join(HERE, '../../src/m_zoom.json'), encoding='utf-8'))   # pruned frames, see zoom_cache.py
except FileNotFoundError:
    ZOOM = {}

G = {'A': ('#D29A50', '#9A672C'), 'B': ('#A06C42', '#6B4527'), 'C': ('#4E3426', '#2A1A10')}
INK, INK2, RUST, GOLD, LEAF = '#1F3A40', '#4F4A40', '#A8452A', '#E4B64C', '#4E8B5C'

# one set of bean drawings, referenced everywhere with <use>
SYMBOLS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>' + ''.join(
    f'<symbol id="bn{g}" viewBox="-12 -9 24 18"><g transform="rotate(-24)"><ellipse rx="10.6" ry="7.2" fill="{f}" stroke="{d}" stroke-width="1"/>'
    f'<path d="M-7.5 2.6 C-3 -2.4 3 2.4 7.5 -2.6" stroke="{d}" stroke-width="1.7" fill="none" stroke-linecap="round"/></g>'
    f'<text y="3.4" text-anchor="middle" font-family="Newsreader,Georgia,serif" font-size="9.5" font-weight="700" fill="#FBF3E2">{g}</text></symbol>'
    for g, (f, d) in G.items()) + '</defs></svg>')


def bean(g, w=22):
    return f'<svg class="bn" width="{w}" height="{w*.75:.0f}" aria-hidden="true"><use href="#bn{g}"/></svg>'


def zoom(key, vb, uid, label=''):
    """The same vector drawing, re-framed on one detail (an avatar, a building). ids are re-prefixed so a
    drawing can be framed twice on one page."""
    s = ZOOM.get(f'{key}|{vb}') or FIG[key]
    m = re.search(r' id="(m[a-z0-9]+_)', s)
    if m:
        s = s.replace(m.group(1), m.group(1)[:-1] + uid + '_')
    s = re.sub(r'viewBox="[^"]+"', f'viewBox="{vb}"', s, 1)
    s = s.replace('class="fig" role="img"', f'class="zm" role="img" aria-label="{label}"' if label else 'class="zm" aria-hidden="true"', 1)
    return s.replace('font-family="Atkinson Hyperlegible Next"', 'font-family="Libre Franklin"')


# ---------------------------------------------------------------- How it works
def checks():
    rows = [('Black or mouldy beans', 'none'), ('Insect holes', 'none'), ('Broken beans', 'few'), ('Drying, colour', 'even')]
    return ('<div class="nf nf-checks" role="img" aria-label="Four photo-visible defects checked: none, none, few, even; first look grade A">'
            + ''.join(f'<div><i></i><b>{a}</b><em>{b}</em></div>' for a, b in rows)
            + '<p>First look <b>A</b><span>93% sure</span></p></div>')


def pool():
    segs = [('A', 1000, 10), ('B', 600, 6), ('C', 400, 4)]
    x, out = 10, ''
    for g, kg, n in segs:
        w = 320 * kg / 2000
        cols = n // 2
        for k in range(n):
            c, r = k % cols, k // cols
            cx = x + w / cols * (c + .5)
            out += f'<use href="#bn{g}" x="{cx-14:.1f}" y="{40+r*28:.1f}" width="28" height="21"/>'
        out += f'<text x="{x+w/2:.1f}" y="118" text-anchor="middle" class="t" fill="{G[g][1]}"><tspan font-weight="700">{g}</tspan> · {kg:,} kg</text>'
        if x > 10:
            out += f'<path d="M{x:.1f} 34 V96" stroke="{INK}" stroke-opacity=".22"/>'
        x += w
    return (f'<div class="nf nf-lot"><svg viewBox="0 0 340 140" role="img" aria-label="One blended lot of 2,000 kg: A 1,000, B 600, C 400">'
            f'<text x="10" y="14" class="t i" fill="{RUST}">2,000 kg · auction opens</text><path d="M10 22 H330" stroke="{RUST}" stroke-width="1.6" stroke-dasharray="5 4"/>'
            f'<rect x="10" y="30" width="320" height="70" rx="12" fill="#FBF6EC" stroke="{INK}" stroke-width="1.8"/>{out}'
            f'<text x="330" y="136" text-anchor="end" class="t i s" fill="{INK2}">one blended lot · each bean 100 kg</text></svg></div>')


def book():
    bids = [('2.81', 'Exporter', 'Dili · this phone'), ('2.79', 'Roaster', 'Dili'), ('2.76', 'Exporter', 'Dili'), ('2.74', 'Café chain', 'Dili')]
    rows = ''.join(f'<li{" class=win" if i == 0 else ""}><b>${p}</b><span>{n}<small>{s}</small></span>{"<i>won</i>" if i == 0 else ""}</li>'
                   for i, (p, n, s) in enumerate(bids))
    return ('<div class="nf nf-book" role="img" aria-label="Order book closed at 17:00; best bid $2.81 per kg from an exporter in Dili">'
            '<div class="clr"><small>cleared at 17:00</small><b>$2.81 / kg</b></div>'
            f'<div class="dk"><div class="hd"><span>order book · closed</span><span>4 buyers bid</span></div><ol>{rows}</ol>'
            '<p class="ft">Dure AI · matching server</p></div></div>')


def vote():
    seq = {'A': 'yyyyynyyyn', 'B': 'yyyyyy', 'C': 'yynyyn'}
    price = {'A': '3.14', 'B': '2.78', 'C': '2.11'}
    rows = ''
    for g, s in seq.items():
        chips = ''.join(f'<i class="{"y" if c == "y" else "n"}{" noor" if g == "A" and k == 0 else ""}"></i>' for k, c in enumerate(s))
        rows += f'<div class="vg g{g}"><span class="vp"><b>{g}</b>${price[g]}</span><span class="chips">{chips}</span></div>'
    return ('<div class="nf nf-vote" role="img" aria-label="One lot: 18 yes, 4 no; A $3.14, B $2.78, C $2.11">'
            '<div class="vt"><b>one lot</b><span><em>18 YES</em> · 4 NO</span></div>' + rows +
            '<p class="vk"><i class="y"></i>sells at the grade price <i class="n"></i>said no, sits out</p></div>')


def pick():
    return ('<div class="nf nf-pick">' + zoom('how5.pick', '0 70 380 257', 'pk', 'Pickup at the church: Noor beside her three sacks') +
            '<div class="tag"><i></i><div><b>Grade A</b><small>confirmed by hand</small></div></div>'
            '<p class="pk"><b>Pickup</b> Thu 07:00 · Letefoho church · 40 kg</p></div>')


def pay():
    amts = [37.6, 42.3, 33.8, 47, 39.5, 28.2, 44.2, 35.7] + [34.4, 41, 28.7, 38.5, 32.8, 29.5] + [30, 27, 33, 24]
    grades = 'A' * 8 + 'B' * 6 + 'C' * 4
    out = ''
    for i, (g, a) in enumerate(zip(grades, amts)):
        x = 22 + i * 17.4
        sx = 128 + i * (84 / 17)
        out += f'<path d="M{sx:.1f} 190 C{sx:.1f} 222 {x:.1f} 218 {x:.1f} 246" stroke="{G[g][0]}" stroke-opacity=".75" stroke-width="{1.4+a/16:.1f}" fill="none"/>'
        out += (f'<rect x="{x-7:.1f}" y="246" width="14" height="12" rx="3" fill="{G[g][0]}" stroke="{G[g][1]}"/>'
                f'<path d="M{x-3.4:.1f} 252 l2.4 2.4 l4.4 -4.8" stroke="#FBF3E2" stroke-width="1.6" fill="none"/>')
    rates = [('A', '3.14'), ('B', '2.78'), ('C', '2.11')]
    rr = ''.join(f'<rect x="84" y="{100+k*28}" width="172" height="23" rx="5" fill="#2C4F57"/>'
                 f'<text x="96" y="{116+k*28}" class="t b" fill="{G[g][0] if g != "C" else "#C49A78"}">{g}</text><text x="244" y="{116+k*28}" text-anchor="end" class="t b" fill="#F4EBDA">${p}/kg</text>'
                 for k, (g, p) in enumerate(rates))
    return ('<div class="nf nf-pay"><svg viewBox="0 0 340 296" role="img" aria-label="One payment of $4,250.85 in; Dure AI splits it by grade and weight into 18 payments; Noor gets $125.60">'
            f'<rect x="90" y="4" width="160" height="46" rx="10" fill="#FBF6EC" stroke="{INK}" stroke-width="1.6"/>'
            f'<text x="170" y="22" text-anchor="middle" class="t i s" fill="{INK2}">exporter prepays</text><text x="170" y="42" text-anchor="middle" class="t b l" fill="{INK}">$4,250.85</text>'
            '<path d="M150 50 C150 62 140 62 140 74 L200 74 C200 62 190 62 190 50Z" fill="#A9B0A4"/>'
            f'<rect x="70" y="74" width="200" height="116" rx="14" fill="{INK}"/><text x="170" y="92" text-anchor="middle" class="t i s" fill="#B9C8C6">Dure AI splits by grade and kg</text>{rr}{out}'
            f'<rect x="4" y="266" width="112" height="24" rx="12" fill="{LEAF}"/><text x="60" y="283" text-anchor="middle" class="t b" fill="#fff">Noor +$125.60</text>'
            f'<path d="M22 260 V266" stroke="{LEAF}" stroke-width="2"/></svg></div>')


def score():
    import math
    def arc(f):
        a0, a1 = math.pi, math.pi * (1 - f)
        cx, cy, r = 150, 128, 100
        return f'M{cx+r*math.cos(a0):.1f} {cy-r*math.sin(a0):.1f} A{r} {r} 0 0 1 {cx+r*math.cos(a1):.1f} {cy-r*math.sin(a1):.1f}'
    return ('<div class="nf nf-score" role="img" aria-label="Reputation: 92% of grades confirmed; 14 sales, 13 of 14 on time, 1 dispute">'
            f'<svg viewBox="0 0 300 150" aria-hidden="true"><path d="{arc(1)}" stroke="#E2D7C1" stroke-width="18" fill="none" stroke-linecap="round"/>'
            f'<path d="{arc(.92)}" stroke="{LEAF}" stroke-width="18" fill="none" stroke-linecap="round"/>'
            f'<text x="150" y="122" text-anchor="middle" font-family="Newsreader,Georgia,serif" font-size="62" font-weight="700" fill="{INK}">92</text>'
            f'<text x="150" y="146" text-anchor="middle" class="t i" fill="{INK2}">grades confirmed, %</text></svg>'
            '<dl><div><dt>14</dt><dd>sales</dd></div><div><dt>13 / 14</dt><dd>on time</dd></div><div><dt>1</dt><dd>dispute</dd></div></dl></div>')


# ---------------------------------------------------------------- Technical walkthrough
def _beanfield(seed, w, h, n, mix, size=1.0, force=()):
    """Coffee spread on a blue tray, drawn top-down. mix: weights for pale, tan, brown, black, grey-green."""
    cols = ['#E6CB93', '#C79A5C', '#7A5332', '#2B211A', '#9FA88E']
    R = random.Random(seed)
    gx = max(1, int(w / (26 * size))); gy = max(1, int(h / (22 * size)))
    out = ''
    for j in range(gy):
        for i in range(gx):
            x = (i + .5 + R.uniform(-.28, .28)) * w / gx
            y = (j + .5 + R.uniform(-.28, .28)) * h / gy
            c = R.choices(cols, mix)[0]
            for (bx, by, bw, bh, bc) in force:
                if bx < x < bx + bw and by < y < by + bh and R.random() < .55:
                    c = bc
            d = {'#E6CB93': '#B99A62', '#C79A5C': '#8C6534', '#7A5332': '#4D311B', '#2B211A': '#140E0A', '#9FA88E': '#6F7862'}[c]
            out += (f'<g transform="translate({x:.1f} {y:.1f}) rotate({R.uniform(0,180):.0f}) scale({size*R.uniform(.9,1.1):.2f})">'
                    f'<ellipse rx="9.4" ry="6.4" fill="{c}" stroke="{d}" stroke-width=".8"/><path d="M-6.4 2 C-2.6 -2 2.6 2 6.4 -2" stroke="{d}" stroke-width="1.3" fill="none"/></g>')
    return out


def tile(seed, mix):
    return (f'<svg viewBox="0 0 90 60" aria-hidden="true"><rect width="90" height="60" fill="#47708F"/>'
            f'{_beanfield(seed, 90, 60, 0, mix, .5)}</svg>')


def photo():
    boxes = [(1, 34, 64, 70, 76, '#2B211A'), (3, 150, 112, 58, 76, '#7A5332'), (2, 226, 132, 64, 50, '#9FA88E')]
    f = _beanfield(11, 340, 236, 0, [52, 20, 14, 6, 8], 1.06, force=[(x, y, w, h, c) for _, x, y, w, h, c in boxes])
    bx = ''.join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="rgba(228,182,76,.16)" stroke="{GOLD}" stroke-width="2.4"/>'
                 f'<circle cx="{x+w}" cy="{y}" r="10" fill="{GOLD}"/><text x="{x+w}" y="{y+4.5}" text-anchor="middle" class="t b s" fill="{INK}">{n}</text>'
                 for n, x, y, w, h, _ in boxes)
    return ('<div class="nf nf-photo dk"><svg viewBox="0 0 340 236" role="img" aria-label="Photo check: three boxes where the model found defects">'
            f'<rect width="340" height="236" fill="#47708F"/><path d="M0 80 H340 M0 160 H340 M110 0 V236 M226 0 V236" stroke="#3B5F7B" stroke-width="3"/>{f}'
            f'<rect x="22" y="40" width="292" height="164" fill="none" stroke="#F4EBDA" stroke-width="2" stroke-dasharray="7 5"/>'
            f'<rect x="22" y="22" width="96" height="20" fill="#F4EBDA"/><text x="30" y="36" class="t b s" fill="{INK}">coffee · 98%</text>{bx}</svg>'
            '<p class="cap">Each box is something the model spotted.</p></div>')


def steps():
    defs = [('1', 'Black beans', 'found'), ('2', 'Mould', 'found'), ('3', 'Broken beans', 'found'), ('', 'Uneven drying', 'slight')]
    cmp_ = [('A', 3, 21, [70, 18, 6, 1, 5]), ('B', 18, 22, [48, 24, 16, 4, 8]), ('C', 79, 23, [30, 20, 22, 18, 10])]
    return ('<div class="nf nf-steps dk" role="img" aria-label="Black beans, mould and broken beans found; preliminary grade C">'
            '<p class="st"><i>1</i>Find the beans<span class="ok">done</span></p><p class="st"><i>2</i>Look for defects</p><ul>'
            + ''.join(f'<li{" class=dim" if not n else ""}><i>{n}</i>{l}<b>{r}</b></li>' for n, l, r in defs)
            + '</ul><p class="st"><i>3</i>Compare with graded photos</p><div class="cmp">'
            + ''.join(f'<div class="{"hi" if g == "C" else ""}">{tile(s, m)}<p><b class="g{g}">{g}</b><span>{v}%</span></p><s><i style="width:{v}%"></i></s></div>'
                      for g, v, s, m in cmp_)
            + '</div><div class="pre">Preliminary grade <b>C</b></div></div>')


def weighs():
    rows = [('Recent sales', '2.47–2.63'), ('Buyers this week', '5'), ('Road to Dili', 'open'), ('Rain this week', 'light'), ("Farmers' asks", '23')]
    return ('<div class="nf nf-weigh dk" role="img" aria-label="What the opening price weighs: recent sales, buyers, road, rain, farmers asks; fair price $2.55, opens at $2.43">'
            '<p class="hd">What it weighs</p><ul>' + ''.join(f'<li>{a}<b>{b}</b></li>' for a, b in rows) +
            '</ul><div class="fair"><div><small>fair price</small><b>$2.55</b></div><div><small>opens at</small><b class="g">$2.43</b></div><em>−5% this week</em></div>'
            '<p class="ft">The discount changes week to week.</p></div>')


def dots():
    asks = [2.20, 2.25, 2.31, 2.31, 2.37, 2.37, 2.37, 2.43, 2.43, 2.43, 2.47, 2.47, 2.49, 2.49, 2.51, 2.53, 2.53, 2.55, 2.55, 2.55, 2.61, 2.67, 2.78]
    Y = lambda v: 224 - (v - 2.15) / (2.85 - 2.15) * 196
    seen, d = {}, ''
    for v in asks:
        j = seen.get(v, 0); seen[v] = j + 1
        d += f'<circle cx="{66+j*12}" cy="{Y(v):.1f}" r="4.6" fill="{"#7FD18B" if v <= 2.55 else "#8FA1A3"}"/>'
    ax = ''.join(f'<text x="34" y="{Y(v)+4:.1f}" text-anchor="end" class="t s" fill="#B9C8C6">{v:.2f}</text><path d="M40 {Y(v):.1f} H46" stroke="#5E7B80"/>'
                 for v in (2.3, 2.5, 2.7))
    return ('<div class="nf nf-dots dk"><svg viewBox="0 0 340 290" role="img" aria-label="Each dot is one farmer\'s ask; cleared at $2.55 with 21 in">'
            f'<text x="50" y="16" class="t i s" fill="#B9C8C6">each dot: one farmer\'s ask, $/kg</text><path d="M46 26 V232" stroke="#5E7B80" stroke-width="1.4"/>{ax}'
            f'<rect x="120" y="{Y(2.63):.1f}" width="210" height="{Y(2.47)-Y(2.63):.1f}" fill="#7FD18B" fill-opacity=".14"/>'
            f'<path d="M100 {Y(2.55):.1f} H330" stroke="#7FD18B" stroke-width="1.6" stroke-dasharray="5 4"/><text x="330" y="{Y(2.55)-8:.1f}" text-anchor="end" class="t s" fill="#7FD18B">fair 2.55</text>'
            f'<circle cx="190" cy="{Y(2.55):.1f}" r="9" fill="{GOLD}"/><text x="176" y="{Y(2.55)+5:.1f}" text-anchor="end" class="t b" fill="#F4EBDA">2.55</text>'
            f'<path d="M120 {Y(2.43):.1f} H330" stroke="{GOLD}" stroke-width="2"/><text x="330" y="{Y(2.43)+17:.1f}" text-anchor="end" class="t s" fill="{GOLD}">opens 2.43</text>{d}'
            f'<circle cx="54" cy="252" r="4" fill="#7FD18B"/><text x="62" y="256" class="t s" fill="#D7CDB9">in</text><circle cx="88" cy="252" r="4" fill="#8FA1A3"/><text x="96" y="256" class="t s" fill="#D7CDB9">sits out</text>'
            f'<rect x="170" y="240" width="160" height="30" rx="7" fill="{GOLD}"/><text x="250" y="260" text-anchor="middle" class="t b" fill="{INK}">cleared 2.55 · 21 in</text></svg></div>')


def rep(who):
    if who == 'noor':
        name, sub, sc, col, rows, av = 'Noor', '2 ha, smallholder', 92, LEAF, [('14', 'completed sales', 1, 0), ('13', 'on-time deliveries', 13/14, 0), ('92%', 'grades confirmed at pickup', .92, 0), ('1', 'quality dispute', 1/14, 1), ('1', 'flood week, not counted', 1/14, 2)], zoom('econ0.noor', '17 19 54 54', 'avn')
    else:
        name, sub, sc, col, rows, av = 'Big grower', '30 ha, 15× more land', 64, '#C9A06A', [('12', 'completed sales', 1, 0), ('9', 'on-time deliveries', 9/12, 0), ('75%', 'grades confirmed at pickup', .75, 0), ('3', 'quality disputes', 3/12, 1), ('0', 'flood weeks, not counted', 0, 2)], zoom('econ0.big', '357 19 54 54', 'avb')
    li = ''.join(f'<li class="{["", "bad", "fm"][b]}"><b>{v}</b>{l}<s><i style="width:{f*100:.0f}%"></i></s></li>' for v, l, f, b in rows)
    return (f'<div class="nf nf-rep" style="--c:{col}" role="img" aria-label="{name}: {sc}% likely to deliver">'
            f'<div class="rh"><span class="av">{av}</span><div><b>{name}</b><small>{sub}</small></div><strong>{sc}%<small>likely to deliver</small></strong></div><ul>{li}</ul></div>')


BUSTS = [99, 135, 167, 200, 235, 271]


def blend():
    rows = [('A', 2, .92), ('B', 4, .35), ('C', 3, .72), ('A', 4, .55), ('B', 3, .88), ('C', 5, .15)]
    col = lambda r: LEAF if r > .6 else ('#C9A06A' if r > .4 else RUST)
    rr = ''.join(f'<div class="pr"><span class="av">{zoom("econ1.blend", f"-3 {y-1} 46 34", f"b{i}")}</span><span class="bns">{"".join(bean(g) for _ in range(n))}</span>'
                 f'<s><i style="width:{r*100:.0f}%;background:{col(r)}"></i></s></div>' for i, ((g, n, r), y) in enumerate(zip(rows, BUSTS)))
    return ('<div class="nf nf-pool" role="img" aria-label="Blended pool: every farmer sells here, every week, to Dili traders">'
            '<h4>Blended pool</h4><p class="sub">every farmer sells here, every week</p>'
            f'<div class="box"><p class="ph"><span>harvest</span><span>reputation</span></p>{rr}</div>'
            f'<div class="sink">{zoom("econ1.blend", "118 322 102 84", "tr")}<b>Dili traders</b><small>bulk buyers · price moves weekly</small></div></div>')


def fixed():
    rows = [('A', 4, 'Specialty roasters', '548 78 86 64'), ('B', 3, 'Export contracts', '538 170 102 76'), ('C', 2, 'Local market', '548 288 86 62')]
    rr = ''.join(f'<div class="fr g{g}"><b>{g}</b><span class="fb">{"".join(bean(g) for _ in range(n))}</span><i class="ln"></i>'
                 f'<span class="by">{zoom("econ1.fixed", vb, f"f{g}")}<small>{who}</small></span></div>' for g, n, who, vb in rows)
    return ('<div class="nf nf-pool fixed" role="img" aria-label="Fixed pool: one grade, a fixed buyer, every week">'
            f'<h4>Fixed pool</h4><p class="sub">one grade · a fixed buyer · every week</p>{rr}'
            '<p class="leg"><s><i></i></s><span><b>higher reputation</b>, more steady orders</span></p><p class="rs">Dure AI sets the split every week</p></div>')


# ---------------------------------------------------------------- Registry
def ledger():
    farms = [('LTF-002 · Lebudu · 0.8 ha', [(3, 60, 'B', '2.49', ''), (4, 55, 'B', '2.51', ''), (5, 50, 'B', '2.47', ''), (6, 40, 'C', '1.90', 'mould'), (7, 35, 'C', '1.92', 'mould')]),
             ('LTF-009 · Ducurai · 2 ha', [(3, 60, 'A', '2.84', ''), (4, 65, 'A', '2.88', ''), (5, 60, 'A', '2.86', ''), (6, 70, 'A', '2.90', ''), (7, 60, 'A', '2.86', '')])]
    body = ''
    for name, rows in farms:
        body += f'<tr class="fm"><th colspan="5">{name}</th></tr>'
        body += ''.join(f'<tr{" class=fl" if f else ""}><td>wk {w}</td><td>{kg} kg</td><td><b class="g{g}">{g}</b></td><td>{p}</td><td>{f}</td></tr>' for w, kg, g, p, f in rows)
    return ('<div class="nf nf-card"><p class="kk">1 · Daily accumulated trades</p><table class="nf-led"><thead><tr><th>week</th><th>kg</th><th>grade</th><th>$/kg</th><th>flag</th></tr></thead>'
            f'<tbody>{body}</tbody></table><p class="ft">+ 593 more trades · every SMS lands here the same day</p></div>')


def qchart():
    S = [('Insect damage', '#B8862E', [6, 12, 11, 8, 11, 11, 11, 17]), ('Low grade (C) share', '#6B4A26', [22, 29, 18, 25, 25, 11, 17, 19]), ('Black or mouldy beans', RUST, [3, 7, 4, 9, 3, 1, 12, 12])]
    X = lambda w: 40 + (w - 1) * 38
    Y = lambda v: 190 - v * 5.4
    g = f'<rect x="{X(6.5):.0f}" y="18" width="38" height="{Y(0)-18:.0f}" fill="#BFD0DA" opacity=".55"/><text x="{X(7):.0f}" y="31" text-anchor="middle" class="t s" fill="#4F6A7A">rain</text>'
    for v in (0, 10, 20, 30):
        g += f'<path d="M40 {Y(v):.0f} H310" stroke="{INK}" stroke-opacity=".1"/><text x="32" y="{Y(v)+4:.0f}" text-anchor="end" class="t s" fill="{INK2}">{v}%</text>'
    g += ''.join(f'<text x="{X(w):.0f}" y="208" text-anchor="middle" class="t s" fill="{INK2}">{w}</text>' for w in range(1, 9))
    g += f'<text x="40" y="224" class="t i s" fill="{INK2}">week</text>'
    ends = {17: -4, 19: -4, 12: 4}
    for n, c, v in S:
        g += f'<polyline pathLength="1" points="{" ".join(f"{X(i+1):.0f},{Y(x):.1f}" for i, x in enumerate(v))}" fill="none" stroke="{c}" stroke-width="2.4" stroke-linejoin="round"/>'
        g += ''.join(f'<circle cx="{X(i+1):.0f}" cy="{Y(x):.1f}" r="3" fill="{c}"/>' for i, x in enumerate(v))
    for (n, c, v), dy in zip(S, (-1, -12, 6)):
        g += f'<text x="318" y="{Y(v[-1])+4+dy:.1f}" class="t b s" fill="{c}">{v[-1]}%</text>'
    leg = ''.join(f'<span><i style="background:{c}"></i>{n}</span>' for n, c, _ in S)
    return ('<div class="nf nf-card"><p class="kk">2 · Data analysis</p><h4>Quality signals by week, whole pool</h4>'
            f'<p class="lg">{leg}</p><svg viewBox="0 0 340 230" role="img" aria-label="Quality signals by week for the whole pool; all three rise after the rain in week 7">{g}</svg>'
            '<p class="ft">One of the Registry\'s charts · synthetic data</p></div>')


def brief():
    return ('<div class="nf nf-brief dk"><p class="kk">3 · Monday\'s brief</p><p class="dt">Mon 27 July · 06:00 · Letefoho pool</p>'
            '<h4>Lebudu: mould on 60% of photos after the rain</h4><p class="vs">against 3% in the other four villages</p>'
            '<ul><li>kg per offer down 35% since week 1</li><li>grade C share 10% → 70%</li><li>7 of 10 offers sat out last week</li></ul>'
            '<p class="rv2"><em>Not a diagnosis. For expert review:</em><b>an extension visit to Lebudu this week and a check on drying space</b></p>'
            '<p class="ft">every number links to its rows in the Registry</p></div>')


# ---------------------------------------------------------------- How it works: the demo's dashboard cards (same design as demo.html)
def _stat(l, v, c='#F6EFE0'):
    return f'<div class="mxs"><span>{l}</span><b style="color:{c}">{v}</b></div>'


def _li(a, b, cls='', small='', col=''):
    return f'<div class="mxli {cls}"><span>{a}{f" <small>{small}</small>" if small else ""}</span><b{f" style=color:{col}" if col else ""}>{b}</b></div>'


GOLDV, GREEN, CORAL = '#E4B64C', '#7FD18B', '#F08A6A'


def mx_price(chart):
    chart = (chart.replace('stroke="#D8CCB2"', 'stroke="#35585F"').replace('fill="#5B5345"', 'fill="#BFD0CC"')
             .replace('stroke="#1F3A40" stroke-width="1.4"', 'stroke="#46656B" stroke-width="1.4"')
             .replace('fill="#4E8B5C" opacity=".2"', 'fill="#7FD18B" opacity=".16"').replace('stroke="#4E8B5C" stroke-width="2.4"', 'class="draw" pathLength="1" stroke="#7FD18B" stroke-width="2.4"')
             .replace('fill="#A9783A" stroke="#fff"', 'fill="#E4B64C" stroke="#24434A"'))
    return ('<div class="mx"><div class="mxstatus">Morning brief · 06:30</div>'
            f'<div class="mxrow">{_stat("Grade A today", "$2.74–2.90", GOLDV)}{_stat("Buyers this week", "4")}{_stat("Gleno road", "flooded", CORAL)}</div>'
            f'<div class="mxbox"><div class="mxh">Coffee A · cleared prices <i>each dot: one auction</i></div>{chart}</div></div>')


def mx_photo(photo):
    rows = [('Black or mouldy beans', 'none'), ('Insect holes', 'none'), ('Broken beans', 'few'), ('Drying, colour', 'even')]
    return (f'<div class="mx">{photo}<div class="mxcap2">Noor · first look on the photo</div>'
            f'<div class="mxrow">{_stat("Preliminary grade", "A", GOLDV)}{_stat("Confidence", "93%")}</div>'
            '<div class="mxbox"><div class="mxh">Defects a photo can show <i>SCA classification</i></div>' + ''.join(_li(a, b, col=GREEN) for a, b in rows) +
            '</div><div class="mxnote">The rest is checked by hand. A person checks every sack at pickup.</div></div>')


def mx_pool():
    return ('<div class="mx"><div class="mxstatus">Pool closed · 1,890 kg · 22 farms</div>'
            '<div class="mxbox"><div class="mxh">One lot <i>bidding opens $2.74/kg</i></div><div class="mxbar"><i style="flex:1000;background:#D29A50"><b>A</b></i><i style="flex:600;background:#B4825A"><b>B</b></i><i style="flex:400;background:#8A6A55"><b>C</b></i></div>'
            '<div class="mxleg"><span><b style="color:#D29A50">■</b> A 1,000 kg</span><span><b style="color:#B4825A">■</b> B 600 kg</span><span><b style="color:#8A6A55">■</b> C 400 kg</span></div></div>'
            '<div class="mxnote">Every grade goes into one lot; buyers bid on the whole lot.</div></div>')


def mx_book():
    rows = [('Exporter', 'Dili · this phone', '$2.81', 'lead'), ('Roaster', 'Dili', '$2.79', 'dim'), ('Exporter', 'Dili', '$2.76', 'dim'), ('Café chain', 'Dili', '$2.74', 'dim')]
    return ('<div class="mx"><div class="mxstatus">Cleared at $2.81 · 17:00</div>'
            '<div class="mxbox"><div class="mxh">Order book <i>opened at $2.74</i></div>' + ''.join(_li(n, p, c, s) for n, s, p, c in rows) +
            '</div><div class="mxnote">At 17:00 the best bid takes the whole lot.</div></div>')


def mx_vote():
    seq = {'A': 'yyyyynyyyn', 'B': 'yyyyyy', 'C': 'yynyyn'}
    price = {'A': '$3.14', 'B': '$2.78', 'C': '$2.11'}
    col = {'A': '#D29A50', 'B': '#B4825A', 'C': '#8A6A55'}
    rows = ''.join(f'<div class="mxvg"><b style="color:{col[g]}">{g} {price[g]}</b><span>' + ''.join(
        f'<i class="{c}" style="--c:{col[g]};--k:{k}"></i>' for k, c in enumerate(s)) + '</span></div>' for g, s in seq.items())
    return ('<div class="mx"><div class="mxstatus">Each farmer decides</div>'
            f'<div class="mxbox"><div class="mxh">One lot · 22 farms <i><b style="color:{GREEN}">18 YES</b> · 4 NO</i></div>{rows}</div>'
            f'<div class="mxbox you"><div class="mxh">You · Noor</div>{_li("40 kg · grade A · min $2.84", "in ✓", col=GREEN)}</div>'
            '<div class="mxnote">Price at or above your minimum: you are in. Below: you choose YES or NO.</div></div>')


def mx_pick(scene):
    return (f'<div class="mx">{scene}<div class="mxrow">{_stat("Sack #0412", "40 kg")}{_stat("Grade, by hand", "A ✓", GREEN)}</div>'
            '<div class="mxnote">Pickup Thu 07:00, Letefoho church. The hand-checked grade is the one paid.</div></div>')


def mx_pay():
    rows = [('You · Noor', '40 kg · A', '+$125.60 ✓', 'lead'), ('8 grade A farms', '$3.14/kg', '✓', ''), ('6 grade B farms', '$2.78/kg', '✓', ''), ('4 grade C farms', '$2.11/kg', '✓', '')]
    return ('<div class="mx"><div class="mxstatus">One payment in, 18 payments out</div>'
            f'<div class="mxrow">{_stat("Exporter paid", "$4,250.85", GOLDV)}{_stat("Wallets paid", "18 / 18", GREEN)}</div>'
            '<div class="mxbox tick">' + ''.join(_li(a, b, c, s, GREEN) for a, s, b, c in rows) +
            '</div><div class="mxnote">Split by grade and kilos. Farmers without mobile money are paid by the truck driver at the next pickup.</div></div>')


def mx_score():
    bars = [('Grades confirmed', 92), ('On time', 93), ('Likely to deliver', 83)]
    return ('<div class="mx"><div class="mxstatus">Noor\'s record</div>'
            f'<div class="mxrow">{_stat("Sales", "14")}{_stat("On time", "13 / 14", GREEN)}{_stat("Disputes", "1", CORAL)}</div>'
            '<div class="mxbox"><div class="mxh">Reputation <i>flood weeks never count</i></div>' + ''.join(
                f'<div class="mxpb"><span>{l}</span><i><u style="--w:{v}%"></u></i><b>{v}%</b></div>' for l, v in bars) +
            '</div><div class="mxnote">Farm size isn\'t counted. Better trust, better deals.</div></div>')
