"""Top-down ("from the sky") illustrations for the phone layout, drawn as plain SVG.

The PC story walks Noor from left to right. On a phone the reader scrolls down, so the road is seen
from above and runs down the page: harvest at the top, the flooded bridge, the landslide, then the trader.
Colours are the story's own palette."""
import math

W = 400
C = dict(
    ground='#C2CC9E', ground2='#B5C291', ground3='#CBD3AA',
    field='#A3BD8F', field2='#94B282', row='#84A374',
    shrub='#557E55', shrub2='#4B7249', cherry='#C23A2E',
    soil='#C8A877', soil2='#B4804F',
    road='#D5BD93', roadEdge='#A57A4E', track='#C4A87A',
    water='#6A93AA', water2='#7FA3B7', ripple='#A9C6D5',
    mud='#A07550', mud2='#8C5E36', scar='#A9825C', rock='#8E8A80', rock2='#6F6A60',
    wall='#D9C8A6', rust='#A8452A', rust2='#8E3A22', teal='#2C4F57', teal2='#22403F', tan='#C9A06A', tan2='#A9824F',
    tree='#6E9A63', tree2='#86AE74', treeD='#557E55', ink='#1F3A40',
)


def rnd(i):
    x = math.sin(i * 78.233 + 12.9898) * 43758.5453
    return x - math.floor(x)


def tree(x, y, r, k=0):
    """a tree seen from above: canopy, a lighter crown, a soft shadow"""
    return (f'<ellipse cx="{x+r*.35:.1f}" cy="{y+r*.4:.1f}" rx="{r:.1f}" ry="{r*.9:.1f}" fill="#5F7A4E" opacity=".28"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{C["tree"] if k % 2 else C["treeD"]}"/>'
            f'<circle cx="{x-r*.25:.1f}" cy="{y-r*.3:.1f}" r="{r*.55:.1f}" fill="{C["tree2"]}" opacity=".75"/>')


def palm(x, y, r, k=0):
    leaves = ''.join(
        f'<path d="M{x:.1f} {y:.1f} Q {x+math.cos(a+.35)*r*.7:.1f} {y+math.sin(a+.35)*r*.7:.1f} {x+math.cos(a)*r:.1f} {y+math.sin(a)*r:.1f}" '
        f'stroke="{C["treeD"]}" stroke-width="3.2" fill="none" stroke-linecap="round"/>'
        for a in [i * 2 * math.pi / 7 + k for i in range(7)])
    return f'<circle cx="{x+3:.1f}" cy="{y+4:.1f}" r="{r*.7:.1f}" fill="#5F7A4E" opacity=".22"/>{leaves}<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="#6B5238"/>'


def house(x, y, w, h, roof, ridge, rot=0):
    """a pitched roof from above: two planes and a ridge"""
    return (f'<g transform="translate({x} {y}) rotate({rot})">'
            f'<rect x="{-w/2+3}" y="{-h/2+4}" width="{w}" height="{h}" fill="#000" opacity=".12" rx="1.5"/>'
            f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h/2}" fill="{roof}" rx="1.5"/>'
            f'<rect x="{-w/2}" y="0" width="{w}" height="{h/2}" fill="{ridge}" rx="1.5"/>'
            f'<path d="M{-w/2} 0 H{w/2}" stroke="#000" stroke-opacity=".18" stroke-width="1.2"/></g>')


def coffee_rows(x0, y0, cols, rows, dx=15, dy=17, seed=0, ripe=.35):
    s = ''
    for r in range(rows):
        for c in range(cols):
            i = seed + r * 31 + c
            x = x0 + c * dx + (r % 2) * dx / 2 + (rnd(i) - .5) * 3
            y = y0 + r * dy + (rnd(i + 7) - .5) * 3
            rr = 5.2 + rnd(i + 3) * 1.6
            s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="{C["shrub"] if (r+c) % 3 else C["shrub2"]}"/>'
            if rnd(i + 11) < ripe:
                s += f'<circle cx="{x+1.6:.1f}" cy="{y-1.2:.1f}" r="1.5" fill="{C["cherry"]}"/><circle cx="{x-1.4:.1f}" cy="{y+1.3:.1f}" r="1.3" fill="{C["cherry"]}"/>'
    return s


def road_path(d, w=15, track=True):
    s = (f'<path d="{d}" stroke="{C["roadEdge"]}" stroke-width="{w+5}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
         f'<path d="{d}" stroke="{C["road"]}" stroke-width="{w}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    if track:
        s += f'<path d="{d}" stroke="{C["track"]}" stroke-width="1.6" stroke-dasharray="5 9" fill="none" stroke-linecap="round"/>'
    return s


def truck(x, y, rot, body, cab, load=True):
    sacks = ''
    if load:
        for r in range(4):
            for c in range(2):
                sacks += f'<rect x="{-22+c*23}" y="{-36+r*21}" width="20" height="18" rx="6" fill="#D9C29A" stroke="#B89E72" stroke-width="1"/>'
    return (f'<g transform="translate({x} {y}) rotate({rot})">'
            f'<rect x="-27" y="-62" width="60" height="140" rx="6" fill="#000" opacity=".14"/>'
            f'<rect x="-29" y="-44" width="58" height="96" rx="3" fill="{body}"/>{sacks}'
            f'<rect x="-27" y="-74" width="54" height="34" rx="7" fill="{cab}"/>'
            f'<rect x="-21" y="-71" width="42" height="11" rx="3" fill="#5D7B86"/>'
            f'<rect x="-31" y="-66" width="4" height="9" rx="1.5" fill="#2A2522"/><rect x="27" y="-66" width="4" height="9" rx="1.5" fill="#2A2522"/></g>')


def person(x, y, rot, jacket, hair='#241A16', baskets=False, scale=1):
    """a person seen from above: shoulders, head; optionally a shoulder pole with two baskets"""
    b = ''
    if baskets:
        b = (f'<path d="M-21 0 H21" stroke="#8B6A43" stroke-width="2.6" stroke-linecap="round"/>'
             + ''.join(f'<circle cx="{sx}" cy="0" r="6.6" fill="#C9A06A" stroke="#A07B45" stroke-width="1.4"/>'
                       f'<circle cx="{sx-1.6}" cy="-1.4" r="1.6" fill="#C23A2E"/><circle cx="{sx+1.8}" cy=".8" r="1.6" fill="#9E2A24"/><circle cx="{sx-.4}" cy="2.4" r="1.4" fill="#C23A2E"/>'
                       for sx in (-21, 21)))
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({scale})">'
            f'<ellipse cx="2" cy="3" rx="13" ry="8" fill="#000" opacity=".16"/>{b}'
            f'<ellipse cx="0" cy="1" rx="10.5" ry="6.5" fill="{jacket}"/>'
            f'<circle cx="0" cy="-1" r="5.4" fill="{hair}"/></g>')


# --------------------------------------------------------------------------- the road
ROAD_H = 1840
ROAD_D = ("M 300 196 C 300 262, 252 300, 196 326 S 92 404, 112 482 S 258 560, 268 650 "
          "S 232 760, 222 838 S 160 958, 142 1040 S 172 1162, 232 1232 S 300 1342, 262 1424 "
          "S 168 1520, 180 1604 S 226 1676, 222 1712")


def road_svg():
    s = [f'<svg class="aerial" viewBox="0 0 {W} {ROAD_H}" preserveAspectRatio="xMidYMin slice" aria-hidden="true">']
    s.append(f'<rect width="{W}" height="{ROAD_H}" fill="{C["ground"]}"/>')
    # soft terrain variation
    for i in range(18):
        x, y = rnd(i) * W, rnd(i + 40) * ROAD_H
        s.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{90+rnd(i+5)*90:.0f}" ry="{50+rnd(i+9)*60:.0f}" fill="{C["ground2"] if i % 2 else C["ground3"]}" opacity=".7" transform="rotate({rnd(i+3)*60-30:.0f} {x:.0f} {y:.0f})"/>')
    # --- village and Noor's coffee garden (harvest)
    s.append(f'<path d="M14 40 L230 24 L246 286 L22 300 Z" fill="{C["field2"]}"/>')
    s.append(f'<path d="M14 40 L230 24 L246 286 L22 300 Z" fill="none" stroke="{C["row"]}" stroke-width="1.2" opacity=".6"/>')
    s.append(coffee_rows(30, 52, 13, 14, seed=3))
    s.append(f'<rect x="266" y="44" width="120" height="96" fill="{C["field"]}" rx="3"/>' + ''.join(
        f'<path d="M{272+i*9} 50 V134" stroke="{C["row"]}" stroke-width="2" opacity=".55"/>' for i in range(12)))
    # yard, drying tarp with coffee on it, houses
    s.append(f'<rect x="262" y="150" width="110" height="64" rx="4" fill="{C["soil"]}"/>')
    s.append('<rect x="318" y="160" width="46" height="34" fill="#3D6C8A" rx="1.5" transform="rotate(-4 341 177)"/>')
    s.append(''.join(f'<ellipse cx="{322+(i%9)*4.6+rnd(i)*2:.1f}" cy="{164+(i//9)*4.4+rnd(i+3)*2:.1f}" rx="1.9" ry="1.3" fill="#D8BC86"/>' for i in range(54)))
    s.append(house(288, 168, 40, 30, C['rust'], C['rust2'], -3))
    s.append(house(360, 236, 34, 24, C['teal'], C['teal2'], 8))
    s.append(house(54, 330, 30, 22, C['tan'], C['tan2'], -12))
    for i, (x, y, r) in enumerate([(254, 34, 13), (380, 22, 11), (262, 262, 12), (378, 290, 13), (20, 332, 12), (150, 352, 14), (330, 340, 10)]):
        s.append(tree(x, y, r, i))
    # --- fields down the slope
    s.append(f'<path d="M 270 400 L 396 380 L 398 520 L 300 540 Z" fill="{C["field"]}"/>' + ''.join(
        f'<path d="M{276+i*10} {402-i*1.5} L{298+i*9.5} {538-i*1.5}" stroke="{C["row"]}" stroke-width="1.8" opacity=".5"/>' for i in range(10)))
    s.append(f'<path d="M 6 520 L 150 548 L 132 690 L 4 664 Z" fill="{C["field2"]}"/>' + ''.join(
        f'<path d="M10 {532+i*13} L{148-i*1.6:.0f} {558+i*13}" stroke="{C["row"]}" stroke-width="1.8" opacity=".5"/>' for i in range(10)))
    for i, (x, y) in enumerate([(40, 430), (200, 420), (360, 600), (330, 700), (60, 760), (380, 960), (20, 980), (90, 1150), (40, 1300)]):
        s.append(palm(x, y, 15, i) if i % 3 == 1 else tree(x, y, 12 + (i % 3) * 2, i))
    # --- the river and the flooded bridge
    s.append(f'<path d="M -20 788 C 70 760, 150 838, 226 820 S 352 766, 420 796 L 420 858 C 352 830, 300 884, 226 878 S 78 824, -20 852 Z" fill="{C["water"]}"/>')
    s.append(f'<path d="M -20 788 C 70 760, 150 838, 226 820 S 352 766, 420 796" stroke="{C["ripple"]}" stroke-width="2" fill="none" opacity=".7"/>')
    s.append(road_path(ROAD_D))
    # bridge planks across the river, then the flood over them
    s.append('<g transform="translate(224 834) rotate(-8)">' + ''.join(
        f'<rect x="-14" y="{-40+i*7}" width="28" height="5" rx="1" fill="#A5774A"/>' for i in range(12)) +
        '<rect x="-17" y="-42" width="3" height="86" fill="#6B5238"/><rect x="14" y="-42" width="3" height="86" fill="#6B5238"/></g>')
    s.append(f'<path d="M 120 792 C 160 760, 300 770, 330 806 C 352 836, 318 902, 236 904 C 150 906, 96 868, 104 828 Z" fill="{C["water2"]}" opacity=".88"/>')
    s.append(''.join(f'<path d="M{150+rnd(i)*150:.0f} {800+rnd(i+5)*90:.0f} q 9 -4 18 0 t 18 0" stroke="{C["ripple"]}" stroke-width="1.6" fill="none" opacity=".85"/>' for i in range(12)))
    s.append('<g transform="translate(276 862) rotate(24)"><rect x="-14" y="-2.5" width="28" height="5" rx="1" fill="#A5774A"/></g>'
             '<g transform="translate(176 812) rotate(-30)"><rect x="-12" y="-2.5" width="24" height="5" rx="1" fill="#A5774A"/></g>')
    # --- the hill and the landslide
    for i, (rx, ry, f) in enumerate([(150, 170, '#AFC28E'), (122, 140, '#A2B783'), (94, 110, '#95AC77'), (66, 80, '#889F6B'), (38, 48, '#7C935F')]):
        s.append(f'<ellipse cx="392" cy="1196" rx="{rx}" ry="{ry}" fill="{f}"/>')
    s.append(f'<path d="M 350 1098 C 330 1140, 316 1176, 300 1196 C 268 1226, 206 1246, 146 1266 C 166 1294, 246 1302, 306 1290 C 340 1270, 362 1200, 366 1140 Z" fill="{C["mud"]}"/>')
    s.append(f'<path d="M 352 1104 C 344 1140, 336 1170, 328 1190" stroke="{C["scar"]}" stroke-width="9" fill="none" stroke-linecap="round"/>')
    s.append(''.join(f'<path d="M{330-i*16} {1180+i*8} q -18 10 -34 30" stroke="{C["mud2"]}" stroke-width="2" fill="none" opacity=".7"/>' for i in range(6)))
    for i in range(22):
        x, y, r = 170 + rnd(i + 60) * 170, 1200 + rnd(i + 70) * 90, 3.5 + rnd(i + 80) * 6
        if x + (y - 1200) * .9 < 380:
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{C["rock"] if i % 3 else C["rock2"]}" stroke="#5C574E" stroke-width=".8"/>')
    s.append('<g transform="translate(214 1278) rotate(-62)"><rect x="-26" y="-2.5" width="52" height="5" rx="2" fill="#6B5238"/>' + tree(-30, 0, 9, 1) + '</g>')
    # --- the trader at the end of the road
    s.append(f'<ellipse cx="236" cy="1730" rx="168" ry="78" fill="{C["soil"]}"/>')
    s.append(truck(320, 1742, 6, '#8B6A43', C['rust']))
    s.append(person(262, 1716, -170, '#E3D6BA', hair='#3E7552'))
    s.append('<g transform="translate(212 1668) rotate(-5)"><rect x="-46" y="-19" width="92" height="38" rx="3" fill="#C9A06A" stroke="#A67E4B" stroke-width="2"/>'
             '<text x="0" y="7" text-anchor="middle" font-family="Newsreader" font-style="italic" font-weight="600" font-size="20" fill="#2A2522">$2.25/kg</text></g>')
    s.append(f'<path id="roadLine" d="{ROAD_D}" fill="none" stroke="none"/>')
    s.append('</svg>')
    return ''.join(s)


# --------------------------------------------------------------------------- together: the neighbours' paths join one road
TOG_H = 980
MAIN_D = "M 200 -10 C 200 120, 214 260, 206 400 S 192 600, 200 720"
PATHS = [  # (start house, path into the main road, jacket)
    ((58, 70), "M 58 96 C 70 190, 150 230, 204 300 S 200 600, 200 712", '#2E5E8A'),
    ((340, 56), "M 336 82 C 320 170, 240 230, 208 330 S 196 610, 202 716", '#C9A06A'),
    ((40, 330), "M 64 336 C 120 360, 170 400, 206 450 S 196 640, 198 718", '#6B5238'),
    ((360, 330), "M 336 340 C 290 380, 240 420, 206 480 S 200 650, 202 722", '#5B6F7A'),
    ((84, 590), "M 104 586 C 140 600, 176 640, 196 724", '#B7462E'),
]


def together_svg():
    s = [f'<svg class="aerial" viewBox="0 0 {W} {TOG_H}" preserveAspectRatio="xMidYMin slice" aria-hidden="true">']
    s.append(f'<rect width="{W}" height="{TOG_H}" fill="{C["ground"]}"/>')
    for i in range(10):
        x, y = rnd(i + 200) * W, rnd(i + 240) * TOG_H
        s.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{80+rnd(i+5)*80:.0f}" ry="{50+rnd(i+9)*50:.0f}" fill="{C["ground2"] if i % 2 else C["ground3"]}" opacity=".7"/>')
    s.append(coffee_rows(10, 140, 4, 6, seed=60) + coffee_rows(300, 140, 6, 5, seed=90) + coffee_rows(12, 430, 5, 5, seed=120) + coffee_rows(270, 450, 8, 5, seed=150))
    for (hx, hy), d, _ in PATHS:
        s.append(f'<path d="{d}" stroke="{C["soil"]}" stroke-width="7" fill="none" stroke-linecap="round"/>'
                 f'<path d="{d}" stroke="{C["soil2"]}" stroke-width="1.4" stroke-dasharray="3 6" fill="none" opacity=".6"/>')
    s.append(road_path(MAIN_D + " L 200 1000", w=15))
    roofs = [(C['tan'], C['tan2']), (C['teal'], C['teal2']), (C['rust'], C['rust2']), (C['tan'], C['tan2']), (C['teal'], C['teal2'])]
    for i, ((hx, hy), _, _) in enumerate(PATHS):
        s.append(house(hx, hy, 34, 26, *roofs[i], (i * 23) % 40 - 20))
    for i, (x, y, r) in enumerate([(120, 40, 12), (280, 30, 11), (150, 560, 13), (300, 620, 12), (30, 820, 14), (370, 800, 13), (130, 900, 11)]):
        s.append(tree(x, y, r, i))
    # the gathering point: one big lot, and buyers arriving from Dili
    s.append(f'<ellipse cx="200" cy="772" rx="150" ry="62" fill="{C["soil"]}"/>')
    s.append('<g id="pile">' + ''.join(
        f'<rect x="{214+(i%5)*19}" y="{742+(i//5)*17}" width="17" height="15" rx="5" fill="#D9C29A" stroke="#B89E72" stroke-width="1"/>' for i in range(20)) + '</g>')
    s.append(truck(122, 900, -4, '#8B6A43', C['teal'], load=False))
    s.append(truck(278, 912, 5, '#8B6A43', C['tan'], load=False))
    s.append(f'<path id="mainLine" d="{MAIN_D}" fill="none" stroke="none"/>')
    for i, (_, d, _) in enumerate(PATHS):
        s.append(f'<path id="nb{i}" d="{d}" fill="none" stroke="none"/>')
    s.append('</svg>')
    return ''.join(s)


def walker_svg(jacket, baskets=True):
    """the moving figure, drawn once in its own small SVG so moving it never repaints the map"""
    return (f'<svg viewBox="-24 -24 48 48" width="48" height="48" aria-hidden="true">{person(0, 0, 0, jacket, baskets=baskets)}</svg>')
