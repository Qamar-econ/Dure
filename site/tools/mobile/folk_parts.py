"""Front-facing figures from the PC story's own folk generator (figs.js): Noor and her neighbours walking toward
the reader, and the phone composition of the power scene. Writes into src/m_parts.json."""
import json, os
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '..', 'src')
P = json.load(open(os.path.join(SRC, 'm_parts.json')))

JS = r"""
(PHONE) => {
const F = FIG;
const NOOR = {jk:'#3F8B5C',jkD:'#2D6B46',tais:'taisR',sel:'taisB',head:'cloth',clothC:'#2E5E8A',cuff:'#B7462E'};
const M=(jk,jkD,bot,botD,extra)=>Object.assign({male:1,jk,jkD,bot,botD,inner:'#EFD9B0'},extra);
const W=(jk,jkD,tais,extra)=>Object.assign({jk,jkD,tais},extra);
const NB=[M('#2F5C85','#244A6C','#5A4632','#46362A',{head:'cloth',clothC:'#A8452A',stache:1,cuff:'#7FA7C7',sash:'taisR'}),
          W('#C9A06A','#A9824F','taisB',{sel:'taisR',cuff:'#2E5E8A'}),
          M('#6B5238','#57422D','#2F4A68','#253C55',{head:'cap',capC:'#3F5F43',capD:'#2F4A33',cuff:'#C9A06A',sash:'taisB'}),
          W('#5B6F7A','#4A5C66','taisB',{sel:'taisI',head:'cloth',clothC:'#3E7552',cuff:'#A8452A'}),
          M('#B7462E','#973622','#2F4A68','#253C55',{head:'cloth',clothC:'#241A16',stache:1,cuff:'#EFD9B0',sash:'taisR'})];
const tais0=F.taisDefs().replace(/^<svg[^>]*><defs>/,'').replace(/<\/defs><\/svg>$/,'');
const clip=tais0+'<clipPath id="cL"><rect x="-200" y="-120" width="200" height="160"/></clipPath><clipPath id="cR"><rect x="0" y="-120" width="200" height="160"/></clipPath>';
// legs get their own layers so the feet can step; the rest bobs as one body
const walker=o=>{const s=F.folk(Object.assign({L:'down',R:'down',bag:1},o));
  const a=s.indexOf('/>')+2, b=s.indexOf(o.male?'<path d="M-54 -176':'<path d="M-52 -196');
  const legs=s.slice(a,b);
  const html=s.slice(0,a)+`<g class="lb"><g clip-path="url(#cR)">${legs}</g></g><g class="lf"><g clip-path="url(#cL)">${legs}</g></g><g class="bd">${s.slice(b)}</g>`;
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');document.body.appendChild(svg);svg.innerHTML=html;const bb=svg.getBBox();svg.remove();
  return {html, defs:'<defs>'+clip+'</defs>', bb:[bb.x-6, bb.y-6, bb.width+12, 8-(bb.y-6)]}};
const tais=F.taisDefs().replace(/^<svg[^>]*><defs>/,'').replace(/<\/defs><\/svg>$/,'');
const out={noor:walker(NOOR), nb:NB.map(walker), tais};
// ---- the power scene, composed for a phone (400 x 300)
const fig=(o,x,y,k)=>`<g transform="translate(${x} ${y}) scale(${k})">${F.folk(o)}</g>`;
const G=276, K=.235;
let s=`<path d="M-10 196 L 70 112 L 120 150 L 190 70 L 262 160 L 330 104 L 410 180 L 410 196Z" fill="#B7CAD8"/>
<path d="M150 196 L 190 70 L 216 112 L 196 196Z" fill="#C9D8E3"/><path d="M300 196 L 330 104 L 350 128 L 336 196Z" fill="#C9D8E3"/>
<path d="M-10 190 C 80 182 160 190 268 186 L 268 300 L -10 300Z" fill="#A9C493"/>
<path d="M262 188 C 320 184 370 186 410 190 L 410 300 L 262 300Z" fill="#9DBA86"/>
${[0,1,2,3,4,5].map(i=>`<path d="M-10 ${206+i*12} C 90 ${202+i*12} 180 ${206+i*12} 266 ${204+i*12}" stroke="#97B57F" stroke-width="1.2" fill="none" opacity=".7"/>`).join('')}
<path d="M268 186 L 280 188 L 276 206 L 284 222 L 274 246 L 286 268 L 280 300 L 262 300 L 270 270 L 258 246 L 270 224 L 262 206Z" fill="#241A16"/>
<rect x="18" y="40" width="3.4" height="${G-40}" fill="#6B5238"/><rect x="226" y="40" width="3.4" height="${G-40}" fill="#6B5238"/>
<path d="M21 44 L 226 44 L 226 78 C 180 84 74 74 21 82Z" fill="#EFE3C8" stroke="#D9C9A6"/>
<text x="124" y="70" text-anchor="middle" font-family="Gochi Hand,cursive" font-size="25" textLength="140" lengthAdjust="spacingAndGlyphs" fill="#A8452A">KOOPERATIVA</text>`;
s+=fig(M('#5B6F7A','#4A5C66','#2F4A68','#253C55',{L:'hold',R:'fist',cuff:'#C9A06A',sash:'taisI'}),46,G,K);
s+=fig(M('#C9A06A','#A9824F','#5A4A3A','#463A2E',{head:'cloth',clothC:'#9A3326',L:'fist',R:'fist',cuff:'#2E5E8A',sash:'taisB'}),100,G+4,K);
s+=fig(M('#2F5C85','#244A6C','#2F5C85','#244A6C',{stache:1,L:'down',R:'fist',cuff:'#7FA7C7',sash:'taisR'}),154,G-2,K);
s+=fig(M('#B7462E','#973622','#2F4A68','#253C55',{head:'cloth',clothC:'#241A16',stache:1,L:'fist',R:'point',mood:'angry',cuff:'#EFD9B0',sash:'taisR'}),212,G+2,K*1.04);
s+=fig(Object.assign({},NOOR,{L:'down',R:'down',bag:1}),346,G,K);
s+=`<rect y="262" width="400" height="38" fill="url(#pwFade)"/>`;
out.power=`<svg viewBox="0 0 400 300" class="pw" role="img" aria-label="The cooperative's men under their banner, pointing across a crack in the ground at Noor, who stands alone"><defs>${tais.replace(/id="/g,'id="pw_')}<linearGradient id="pwFade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F2EADA" stop-opacity="0"/><stop offset="1" stop-color="#F2EADA"/></linearGradient></defs>${s.replace(/url\(#(tais[A-Z]+L?|straw)\)/g,'url(#pw_$1)')}</svg>`;
// ---- Noor holding up her phone, for the dark Dure intro (figure units: feet at 0)
const phone=eval('`'+PHONE+'`');
out.phoneNoor=F.folk(Object.assign({},NOOR,{L:'down',R:'hold',bag:1}))+phone;
return out;
}
"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.set_content('<body></body>'); pg.add_script_tag(path=os.path.join(SRC, 'figs.js'))
    site = open(os.path.join(SRC, 'site.html'), encoding='utf-8').read()
    i = site.index('const phone=`') + len('const phone=`'); j = site.index('`;', i)
    r = pg.evaluate(JS, site[i:j])
    b.close()
P['fnoor'] = r['noor']; P['fnb'] = r['nb']; P['tais'] = r['tais']; P['power'] = r['power']; P['fphone'] = r['phoneNoor']
json.dump(P, open(os.path.join(SRC, 'm_parts.json'), 'w'))
print('noor bb', r['noor']['bb'], 'power', len(r['power']) // 1024, 'KB')
