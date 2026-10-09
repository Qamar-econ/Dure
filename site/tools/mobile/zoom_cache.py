"""Prune each re-framed drawing in native.py to the shapes that fall inside its frame -> src/m_zoom.json."""
import json, os, re, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import native as N
N.ZOOM = {}
calls = []
orig = N.zoom
N.zoom = lambda k, vb, uid, label='': calls.append((k, vb)) or ''
for f in (N.pick, N.blend, N.fixed, lambda: N.rep('noor'), lambda: N.rep('big')): f()
JS = r"""([svg,vb])=>{document.body.innerHTML=svg;const src=document.querySelector('svg');const [x,y,w,h]=vb.split(' ').map(Number);
 src.setAttribute('viewBox',vb);src.setAttribute('width',w*4);src.setAttribute('height',h*4);
 const inv=src.getScreenCTM().inverse();const kill=[];
 const walk=(o,d)=>{[...o.children].forEach(ch=>{const t=ch.tagName.toLowerCase();
   if(['defs','style','clippath','lineargradient','radialgradient','pattern','filter','symbol','mask','marker'].includes(t))return;
   const r=ch.getBoundingClientRect();if(r.width===0&&r.height===0){if(t!=='g')kill.push(ch);return}
   const a=new DOMPoint(r.left,r.top).matrixTransform(inv),z=new DOMPoint(r.right,r.bottom).matrixTransform(inv);
   if(Math.max(a.x,z.x)<x||Math.min(a.x,z.x)>x+w||Math.max(a.y,z.y)<y||Math.min(a.y,z.y)>y+h){kill.push(ch);return}
   if(d<6&&t==='g')walk(ch,d+1)})};
 walk(src,0);kill.forEach(e=>e.remove());
 // drop definitions nothing points at any more
 for(let pass=0;pass<3;pass++){const html=src.outerHTML;src.querySelectorAll('defs > [id], defs [id]').forEach(e=>{if(!html.includes('#'+e.id+')')&&!html.includes('#'+e.id+'"'))e.remove()})}
 return src.outerHTML}"""
out = {}
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    for k, vb in calls:
        out[f'{k}|{vb}'] = pg.evaluate(JS, [N.FIG[k], vb])
    b.close()
json.dump(out, open(os.path.join(HERE, '../../src/m_zoom.json'), 'w'))
print({k: len(v) // 1024 for k, v in out.items()})
