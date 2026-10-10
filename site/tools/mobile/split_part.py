"""The PC story's split scene (members under the KOOPERATIVA banner, the ground cracked open, the opposition with
their price sign), frozen at its last frame and re-framed for phones and tablets -> m_parts.json['split']."""
import json, os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '..', 'src')
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8794/index.html?full=1'
VB = '70 200 1420 600'
JS = r"""(VB)=>{const svg=document.getElementById('spSvg').cloneNode(true);
 svg.querySelectorAll('#S1 > *').forEach(e=>{if(+(e.getAttribute('opacity')??1)<.05)e.remove()});svg.querySelector('#spRust')?.setAttribute('opacity',getComputedStyle(document.getElementById('spRust')).opacity||document.getElementById('spRust').getAttribute('opacity'));
 const D=40;svg.querySelector('#SL').setAttribute('transform',`translate(${-110+D} 0)`);svg.querySelector('#SR').setAttribute('transform',`translate(${110-D} 0)`);
 [...svg.querySelector('#SP').children].forEach(g=>{const m=/translate\(([-\d.]+) ([-\d.]+)\)/.exec(g.getAttribute('transform')||'');if(!m)return;const x=+m[1];if(x<0||x>1500){g.remove();return}g.setAttribute('transform',g.getAttribute('transform').replace(m[0],`translate(${x+(x<800?D:-D)} ${m[2]})`))});
 svg.querySelectorAll('[class]').forEach(e=>e.removeAttribute('class'));
 // definitions the scene borrows from the shared pool
 const need=new Set(),add=h=>{for(const m of h.matchAll(/url\(#([^)]+)\)|href="#([^"]+)"/g))need.add(m[1]||m[2])};add(svg.outerHTML);
 let defs='',done=new Set();for(let i=0;i<6;i++){[...need].forEach(id=>{if(done.has(id)||svg.querySelector('#'+CSS.escape(id)))return;const e=document.getElementById(id);done.add(id);if(e){defs+=e.outerHTML;add(e.outerHTML)}})}
 let h=svg.innerHTML;const ids=new Set([...h.matchAll(/id="([^"]+)"/g),...defs.matchAll(/id="([^"]+)"/g)].map(m=>m[1]));
 let all='<defs>'+defs+'</defs>'+h;ids.forEach(id=>{const r=id.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');all=all.replace(new RegExp('id="'+r+'"','g'),'id="sp_'+id+'"').replace(new RegExp('#'+r+'([)"])','g'),'#sp_'+id+'$1')});
 return `<svg viewBox="${VB}" class="spl" role="img" aria-label="The cooperative's members under their banner, the ground cracked open, and the opposition across it with their own price">${all}</svg>`}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport=dict(width=1440, height=900))
    pg.goto(URL); pg.wait_for_timeout(2500)
    top = pg.evaluate("document.getElementById('split').offsetTop")
    pg.evaluate(f"window.__lenis.scrollTo({top}+180*innerHeight/100,{{immediate:true,force:true}})"); pg.wait_for_timeout(1500)
    s = pg.evaluate(JS, VB); b.close()
P = json.load(open(os.path.join(SRC, 'm_parts.json')))
P['split'] = s
json.dump(P, open(os.path.join(SRC, 'm_parts.json'), 'w'))
print('split', len(s) // 1024, 'KB')
