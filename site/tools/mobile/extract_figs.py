# Usage: serve site/dist on :8793, then
#   python3 tools/mobile/extract_figs.py tools/mobile/fig_specs.json src/m_figs.json
"""Pull finished-state vector figures out of the PC story and cut them into phone-sized crops.
Each crop keeps only the top-level shapes that fall inside it, ids are prefixed, nothing is rasterised."""
import json,sys
from playwright.sync_api import sync_playwright
SPECS=json.load(open(sys.argv[1]))
OUT=sys.argv[2]
JS=r"""
([sel,crops,name])=>{
  const src=document.querySelector(sel); const out={};
  const svgR=src.getBoundingClientRect(); const vb=src.viewBox.baseVal;
  const sx=svgR.width/vb.width, sy=svgR.height/vb.height;
  // preserveAspectRatio meet: uniform scale, centred
  const inv=src.getScreenCTM().inverse(); const s=Math.min(sx,sy), ox=svgR.left+(svgR.width-vb.width*s)/2, oy=svgR.top+(svgR.height-vb.height*s)/2;
  crops.forEach(([cn,x,y,w,h,deep])=>{
    const c=src.cloneNode(true);
    // walk original and clone in parallel to decide what to drop
    const keep=(o,k,depth)=>{
      [...o.children].forEach((ch,i)=>{const kc=k.children[i];if(!kc)return;
        const tag=ch.tagName.toLowerCase();
        if(['defs','style','clippath','lineargradient','radialgradient','pattern','filter','symbol','mask','marker'].includes(tag))return;
        const op=getComputedStyle(ch).opacity, disp=getComputedStyle(ch).display, vis=getComputedStyle(ch).visibility;
        if(op==='0'||disp==='none'||vis==='hidden'){kc.setAttribute('data-zcut','1');return}
        const r=ch.getBoundingClientRect();
        const a=new DOMPoint(r.left,r.top).matrixTransform(inv), z=new DOMPoint(r.right,r.bottom).matrixTransform(inv);
        const ux0=Math.min(a.x,z.x), uy0=Math.min(a.y,z.y), ux1=Math.max(a.x,z.x), uy1=Math.max(a.y,z.y);
        if(r.width===0&&r.height===0&&tag!=='g'){return}
        if(ux1<x||ux0>x+w||uy1<y||uy0>y+h){kc.setAttribute('data-zcut','1');return}
        if(depth<(deep||1)&&tag==='g')keep(ch,kc,depth+1);
      })};
    keep(src,c,0);
    c.querySelectorAll('[data-zcut]').forEach(e=>e.remove());
    // bring along definitions that live elsewhere on the page (shared patterns, symbols)
    {let d=c.querySelector('defs');if(!d){d=document.createElementNS('http://www.w3.org/2000/svg','defs');c.prepend(d)}
     for(let pass=0;pass<3;pass++){const html=c.outerHTML,ids=new Set([...html.matchAll(/url\(#([^)]+)\)|href="#([^"]+)"/g)].map(m=>m[1]||m[2]));
       ids.forEach(id=>{if(c.querySelector('[id="'+id+'"]'))return;const el=document.getElementById(id);if(el)d.appendChild(el.cloneNode(true))})}}
    let html=c.outerHTML;
    const p='m'+name+cn+'_';
    html=html.replace(/ id="([^"]+)"/g,(m,a)=>` id="${p}${a}"`).replace(/url\(#([^)]+)\)/g,(m,a)=>`url(#${p}${a})`).replace(/href="#([^"]+)"/g,(m,a)=>`href="#${p}${a}"`);
    html=html.replace(/<svg[^>]*?>/,`<svg xmlns="http://www.w3.org/2000/svg" viewBox="${x} ${y} ${w} ${h}" class="fig" role="img">`);
    out[cn]=html;
  });
  return out;
}"""
res={}
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport=dict(width=1440,height=900))
    pg.goto('http://localhost:8793/index.html?tap=0');pg.wait_for_timeout(1500)
    for sp in SPECS:
        pg.evaluate(sp['state']);pg.wait_for_timeout(sp.get('wait',1800))
        r=pg.evaluate(JS,[sp['sel'],sp['crops'],sp['name']])
        for k,v in r.items(): res[sp['name']+'.'+k]=v
    b.close()
json.dump(res,open(OUT,'w'))
for k,v in res.items(): print(k,len(v)//1024,'KB')
