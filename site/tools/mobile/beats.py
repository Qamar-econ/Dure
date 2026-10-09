"""Five still pictures cut from the aerial map, one per beat of the story, plus the gathering.
Each is pruned to what its frame shows (playwright) and cached in src/m_beats.json."""
import json, os, re, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from aerial import road_svg, together_svg, heap_svg, PATHS, HEAP
SRC = os.path.join(HERE, '..', '..', 'src')
P = json.load(open(os.path.join(SRC, 'm_parts.json')))


def fig(part, key, x, y, k):
    """a standing figure from the story, feet at (x, y) in map units"""
    body = part['defs'] + part['html']
    body = re.sub(r' id="([^"]+)"', lambda m: f' id="{key}_{m.group(1)}"', body)
    body = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{key}_{m.group(1)})', body)
    body = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{key}_{m.group(1)}"', body)
    return f'<g transform="translate({x} {y}) scale({k})">{body}</g>'


RAIN = ('<rect x="-400" y="0" width="1200" height="2000" fill="rgb(48,60,70)" opacity=".3"/>'
        '<g stroke="#DCE6EA" stroke-width="1.4" stroke-linecap="round" opacity=".5">' +
        ''.join(f'<path d="M{(i*37) % 1100 - 350} {((i*53) % 2000)} l-4 14"/>' for i in range(900)) + '</g>')
K = .1   # figure scale in map units (the gathering)
KR = .19   # on the road pictures, closer up

road, tog = road_svg(), together_svg()
def strip(svg):
    return re.sub(r' id="(roadLine|roadMeasure|mainLine|nb\d)"', '', svg)
road, tog = strip(road), strip(tog)

def add(svg, extra):
    return svg.replace('</svg>', extra + '</svg>')

stack = heap_svg().replace(' style="opacity:0"', '').replace('<svg ', f'<svg x="{HEAP[0]-64}" y="{HEAP[1]-70}" width="128" height="87" ', 1)
sign = (f'<g transform="translate({HEAP[0]+52} {HEAP[1]-96}) rotate(-4)"><rect width="74" height="38" rx="3" fill="#C9A06A" stroke="#A67E4B" stroke-width="2"/>'
        '<text x="37" y="17" text-anchor="middle" font-family="Newsreader,Georgia,serif" font-size="15" font-weight="700" fill="#2A2522">500 kg</text>'
        '<text x="37" y="31" text-anchor="middle" font-family="Newsreader,Georgia,serif" font-style="italic" font-size="11" fill="#7A3322">best offer?</text></g>')
ends = [(132, 748), (300, 752), (112, 800), (318, 806), (168, 830)]

BEATS = {
    'harvest': (road, '0 20 400 250', fig(P['fnoor'], 'b1', 300, 250, KR)),
    'flood': (road, '20 690 400 250', fig(P['fnoor'], 'b2', 330, 800, KR) + RAIN),
    'slide': (road, '60 1070 400 250', fig(P['fnoor'], 'b3', 236, 1250, KR) + RAIN),
    'buyer': (road, '40 1600 400 250', fig(P['trader'], 'b4t', 262, 1760, .2) + fig(P['fnoor'], 'b4', 170, 1790, KR)),
    'together': (tog, '14 640 400 290', stack + ''.join(fig(P['fnb'][i], f'b5n{i}', x, y, K) for i, (x, y) in enumerate(ends)) + fig(P['fnoor'], 'b5', 262, 862, K) + sign),
}
JS = r"""([svg,vb])=>{document.body.innerHTML=svg;const src=document.querySelector('svg');const [x,y,w,h]=vb.split(' ').map(Number);
 src.setAttribute('viewBox',vb);src.setAttribute('width',w*3);src.setAttribute('height',h*3);
 const inv=src.getScreenCTM().inverse();const kill=[];
 [...src.children].forEach(ch=>{const t=ch.tagName.toLowerCase();if(['defs','style','lineargradient','pattern','clippath'].includes(t))return;
   const r=ch.getBoundingClientRect();if(!r.width&&!r.height){kill.push(ch);return}
   const a=new DOMPoint(r.left,r.top).matrixTransform(inv),z=new DOMPoint(r.right,r.bottom).matrixTransform(inv);
   if(Math.max(a.x,z.x)<x||Math.min(a.x,z.x)>x+w||Math.max(a.y,z.y)<y||Math.min(a.y,z.y)>y+h)kill.push(ch)});
 kill.forEach(e=>e.remove());src.removeAttribute('width');src.removeAttribute('height');src.setAttribute('class','bt');src.setAttribute('preserveAspectRatio','xMidYMid slice');return src.outerHTML}"""
out = {}
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    for k, (base, vb, extra) in BEATS.items():
        out[k] = pg.evaluate(JS, [add(base, extra), vb])
    b.close()
json.dump(out, open(os.path.join(SRC, 'm_beats.json'), 'w'))
print({k: len(v) // 1024 for k, v in out.items()})
