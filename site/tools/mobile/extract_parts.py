# Usage: serve site/dist on :8793, then  python3 tools/mobile/extract_parts.py src/m_parts.json
"""Single drawings lifted from the PC story (walkers, farmers, Noor with her phone, small icons) with the
definitions they use, so the phone edition can draw them exactly as the story does."""
import json,sys
from playwright.sync_api import sync_playwright
JS=r"""
([sel,inner])=>{const el=document.querySelector(sel);if(!el)return null;
  const host=el.ownerSVGElement||el;let html=inner?el.innerHTML:el.outerHTML;
  const ids=new Set();const add=h=>[...h.matchAll(/url\(#([^)]+)\)|href="#([^"]+)"/g)].forEach(m=>ids.add(m[1]||m[2]));
  add(html);let defs='';const seen=new Set();
  for(let pass=0;pass<4;pass++){[...ids].forEach(id=>{if(seen.has(id))return;seen.add(id);if(el.querySelector('[id="'+id+'"]'))return;const d=document.getElementById(id);if(d){const o=d.outerHTML;defs+=o;add(o)}})}
  let bb=null;try{const b=(inner?el:el).getBBox();bb=[b.x,b.y,b.width,b.height]}catch(e){}
  return {html,defs,bb}}"""
P={}
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport=dict(width=1440,height=900))
    pg.goto('http://localhost:8793/index.html?tap=0');pg.wait_for_timeout(1500)
    pg.evaluate("__dure.at('road',.4)");pg.wait_for_timeout(1500)
    P['walker']=pg.evaluate(JS,['#walker',True])
    pg.evaluate("__dure.at('road',.95)");pg.wait_for_timeout(1800)
    P['trader']=pg.evaluate(JS,['#scenes > g:last-child',True])
    pg.evaluate("__dure.at('together',.05)");pg.wait_for_timeout(1500)
    P['farmers']=[pg.evaluate(JS,[f'#Tfarmers .tf[data-i="{i}"]',True]) for i in range(pg.evaluate("document.querySelectorAll('#Tfarmers .tf').length"))]
    P['trio']=pg.evaluate("[...document.querySelectorAll('#trio svg')].map(s=>s.outerHTML)")
    pg.evaluate("__dure.at('curtain',.4)");pg.wait_for_timeout(1800)
    P['phoneNoor']=pg.evaluate(JS,['#cuFig',False])
    b.close()
json.dump(P,open(sys.argv[1],'w'))
print({k:(len(json.dumps(v))//1024) for k,v in P.items()}, len(P['farmers']), P['walker']['bb'], [f['bb'] for f in P['farmers']])
