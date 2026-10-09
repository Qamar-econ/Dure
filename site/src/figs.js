/* Dure illustration kit — flat, adult proportions, detail lines in darker tones */
const FIG = (() => {
const C = {
  skin:'#B07448', skinD:'#95603A', cheek:'#C8674E',
  scarf:'#2E4B6C', scarfD:'#253E5A',
  blouse:'#3E7552', blouseD:'#315E42', blouseL:'#4E8762',
  skirt:'#A5462C', skirtD:'#8A3822', stripe:'#E6C9A0',
  hat:'#D5924F', hatD:'#B8743A', hatL:'#E2A864', hatLine:'#A9662F',
  cloth:'#E9D8B6', clothD:'#CDB793',
  cherry:'#C23A2E', cherryD:'#9E2A24', cleaf:'#2F5E3A', cleafL:'#3F7148', leaf:'#4F7C4E', leafL:'#6E9A63',
  basket:'#C58B4E', basketD:'#9E6834',
  ink:'#231C14', sandal:'#5A3B24',
  shirt:'#E8DCC2', shirtD:'#CFC0A2', trouser:'#2F4A68', trouserD:'#253C55', cap:'#3F5F43', capD:'#2F4A33'
};
const hatLines = (apx, apy, rimY, half, n=15) => {
  let s=''; for(let i=1;i<n;i++){const t=i/n; const x=-half+2*half*t; const y=rimY+Math.sin(t*Math.PI)*8; s+=`M${apx} ${apy} L${x.toFixed(1)} ${y.toFixed(1)} `;} return s;
};
const cherryBranch = (x,y,s=1,flip=1) => {
  let g=`<g transform="translate(${x} ${y}) scale(${s*flip} ${s})">`;
  g+=`<path d="M0 -6 C 2 14 0 40 -4 66" stroke="#5A4630" stroke-width="3" fill="none" stroke-linecap="round"/>`;
  [[-1,10,-1],[1,30,1],[-2,50,-1]].forEach(([bx,by,d])=>{
    g+=`<path d="M${bx} ${by} C ${bx+d*16} ${by-4} ${bx+d*26} ${by+6} ${bx+d*30} ${by+16} C ${bx+d*18} ${by+16} ${bx+d*8} ${by+10} ${bx} ${by}Z" fill="${C.cleaf}"/>`;
    g+=`<path d="M${bx} ${by} C ${bx+d*12} ${by+2} ${bx+d*22} ${by+8} ${bx+d*28} ${by+15}" stroke="${C.cleafL}" stroke-width="1.1" fill="none"/>`;});
  [[-5,18],[4,20],[0,24],[-6,38],[3,40],[-1,44],[-7,58],[2,60]].forEach(([cx,cy],i)=>{
    g+=`<circle cx="${cx}" cy="${cy}" r="5" fill="${i%3?C.cherry:C.cherryD}"/><circle cx="${cx-1.6}" cy="${cy-1.6}" r="1.4" fill="#E06A5E" opacity=".7"/>`;});
  return g+'</g>';
};

/* ---------- Aurelia, frontal (feet at 0,0; ~620 tall with hat) ---------- */
function aureliaFront(){
  let s='';
  // shadow
  s+=`<ellipse cx="0" cy="2" rx="110" ry="12" fill="#3E2E1E" opacity=".16"/>`;
  // sandals / feet
  s+=`<path d="M-40 -14 C -40 -4 -26 0 -14 0 L -12 -16Z" fill="${C.skinD}"/><path d="M40 -14 C 40 -4 26 0 14 0 L 12 -16Z" fill="${C.skinD}"/>`;
  s+=`<path d="M-42 -2 H-10 M10 -2 H42" stroke="${C.sandal}" stroke-width="5" stroke-linecap="round"/>`;
  // skirt (long, flared)
  s+=`<path d="M-62 -262 C -70 -190 -84 -90 -92 -18 Q 0 -8 92 -18 C 84 -90 70 -190 62 -262Z" fill="${C.skirt}"/>`;
  s+=`<path d="M22 -262 C 34 -190 50 -90 60 -14 Q 78 -16 92 -18 C 84 -90 70 -190 62 -262Z" fill="${C.skirtD}"/>`;
  let st=''; for(let i=0;i<11;i++){const t=i/10; const xt=-54+108*t, xb=-84+168*t; st+=`M${xt.toFixed(1)} -258 L${xb.toFixed(1)} -22 `;}
  s+=`<path d="${st}" stroke="${C.stripe}" stroke-width="2.2" opacity=".85"/>`;
  s+=`<path d="M-92 -26 Q 0 -16 92 -26" stroke="${C.skirtD}" stroke-width="9" fill="none"/>`;
  // blouse body
  s+=`<path d="M-74 -452 C -86 -420 -84 -360 -72 -300 C -70 -284 -66 -270 -64 -250 L 64 -250 C 66 -270 70 -284 72 -300 C 84 -360 86 -420 74 -452 L 26 -468 L -26 -468Z" fill="${C.blouse}"/>`;
  s+=`<path d="M34 -462 L 74 -452 C 86 -420 84 -360 72 -300 C 70 -284 66 -270 64 -250 L 40 -250 C 52 -320 50 -400 34 -462Z" fill="${C.blouseD}"/>`;
  // placket + buttons + hem
  s+=`<path d="M0 -440 V -252" stroke="${C.blouseD}" stroke-width="2.4"/>`;
  s+=[-420,-384,-348,-312,-276].map(y=>`<circle cx="0" cy="${y}" r="3.6" fill="${C.stripe}"/>`).join('');
  s+=`<path d="M-64 -256 H64" stroke="${C.blouseD}" stroke-width="5"/>`;
  s+=`<path d="M-58 -318 h28 v24 h-28z" fill="none" stroke="${C.blouseD}" stroke-width="2.2"/>`;
  // carrying cloth (sling) from right shoulder to left hip, cradling the harvest
  s+=`<path d="M44 -456 L 62 -446 L -40 -268 L -64 -282Z" fill="${C.cloth}"/>`;
  s+=`<path d="M50 -452 L -52 -274" stroke="${C.clothD}" stroke-width="2"/>`;
  // right arm (viewer's right) hanging, holding a coffee sprig
  s+=`<path d="M74 -452 C 96 -440 104 -400 104 -350 C 104 -320 106 -290 108 -262 L 86 -258 C 82 -290 78 -330 76 -370Z" fill="${C.blouse}"/>`;
  s+=`<path d="M92 -444 C 102 -420 104 -390 104 -350 C 104 -320 106 -290 108 -262 L 98 -260 C 96 -300 96 -360 92 -444Z" fill="${C.blouseD}"/>`;
  s+=`<path d="M84 -270 L 110 -272" stroke="${C.blouseL}" stroke-width="8" stroke-linecap="round"/>`;
  s+=cherryBranch(97,-252,1.0);
  s+=`<path d="M86 -262 C 86 -244 92 -238 100 -238 C 108 -238 112 -246 110 -262Z" fill="${C.skin}"/>`;
  // bundle of picked cherries in cloth at hip
  s+=`<g transform="translate(-78 -284)">`;
  s+=`<path d="M-58 -18 C -60 20 -30 44 4 44 C 36 44 58 22 54 -16Z" fill="${C.cloth}"/>`;
  s+=`<path d="M-50 -6 C -40 22 -10 34 10 34 M -30 -12 C -24 10 -6 22 16 22" stroke="${C.clothD}" stroke-width="2" fill="none"/>`;
  [[-40,-22],[-28,-26],[-16,-28],[-4,-27],[8,-28],[20,-26],[32,-22],[-34,-14],[-20,-16],[-6,-17],[8,-16],[22,-15],[36,-12]].forEach(([x,y],i)=>{
    s+=`<circle cx="${x}" cy="${y+10}" r="7" fill="${i%3?C.cherry:C.cherryD}"/><circle cx="${x-2}" cy="${y+8}" r="2" fill="#E06A5E" opacity=".7"/>`;
  });
  s+=`<path d="M-30 -24 C -40 -36 -38 -48 -26 -52 C -24 -40 -26 -30 -30 -24Z M24 -24 C 34 -38 46 -40 54 -36 C 46 -26 36 -22 24 -24Z" fill="${C.cleaf}"/>`;
  s+=`<path d="M-58 -18 C -30 -6 30 -6 54 -16" stroke="${C.clothD}" stroke-width="3" fill="none"/>`;
  s+=`<path d="M8 -4 C 14 6 30 8 40 2 C 34 -8 18 -10 8 -4Z" fill="${C.skin}"/>`;
  s+=`</g>`;
  // left arm bent, cradling bundle at hip
  s+=`<path d="M-74 -452 C -98 -440 -106 -400 -104 -350 C -102 -318 -96 -300 -80 -290 L -40 -300 L -44 -318 L -76 -322 C -80 -350 -80 -390 -76 -420Z" fill="${C.blouse}"/>`;
  s+=`<path d="M-86 -300 L -44 -306" stroke="${C.blouseL}" stroke-width="8" stroke-linecap="round"/>`;
  // neck
  s+=`<path d="M-13 -486 L 13 -486 L 15 -462 L -15 -462Z" fill="${C.skinD}"/>`;
  // scarf back layer + drape on shoulders
  s+=`<path d="M-44 -520 C -52 -566 -30 -590 0 -590 C 30 -590 52 -566 44 -520 C 42 -490 34 -470 22 -462 L 0 -452 L -22 -462 C -34 -470 -42 -490 -44 -520Z" fill="${C.scarf}"/>`;
  s+=`<path d="M-26 -466 L -58 -448 L -40 -438 L -12 -452Z M26 -466 L 58 -448 L 40 -438 L 12 -452Z" fill="${C.scarf}"/>`;
  s+=`<path d="M-6 -460 L -16 -420 L 0 -428 L 16 -420 L 6 -460Z" fill="${C.scarfD}"/>`;
  s+=`<circle cx="0" cy="-458" r="7" fill="${C.scarfD}"/>`;
  // face
  s+=`<path d="M-28 -536 C -30 -500 -16 -480 0 -478 C 16 -480 30 -500 28 -536 C 26 -556 -26 -556 -28 -536Z" fill="${C.skin}"/>`;
  s+=`<path d="M-30 -532 C -26 -560 26 -560 30 -532 C 22 -546 8 -548 0 -544 C -8 -548 -22 -546 -30 -532Z" fill="${C.scarf}"/>`;
  s+=`<path d="M-30 -532 C -26 -560 26 -560 30 -532" fill="none" stroke="${C.scarfD}" stroke-width="2"/>`;
  s+=`<g fill="${C.cheek}" opacity=".45"><ellipse cx="-15" cy="-506" rx="6" ry="4"/><ellipse cx="15" cy="-506" rx="6" ry="4"/></g>`;
  s+=`<path d="M-17 -526 q5 -3 10 0 M7 -526 q5 -3 10 0" stroke="${C.ink}" stroke-width="1.8" fill="none" stroke-linecap="round"/>`;
  s+=`<g fill="${C.ink}"><ellipse cx="-11" cy="-518" rx="2.1" ry="2.6"/><ellipse cx="11" cy="-518" rx="2.1" ry="2.6"/></g>`;
  s+=`<path d="M0 -516 C -2 -508 -3 -503 1 -501" stroke="${C.skinD}" stroke-width="1.8" fill="none" stroke-linecap="round"/>`;
  s+=`<path d="M-6 -492 Q 0 -489 6 -492" stroke="#6B3A22" stroke-width="2" fill="none" stroke-linecap="round"/>`;
  // hat underside shadow + cone
  s+=`<ellipse cx="0" cy="-552" rx="104" ry="11" fill="${C.hatD}"/>`;
  s+=`<path d="M-108 -556 L 0 -628 L 108 -556 Q 0 -544 -108 -556Z" fill="${C.hat}"/>`;
  s+=`<path d="M0 -628 L 108 -556 Q 60 -550 30 -548Z" fill="${C.hatD}" opacity=".55"/>`;
  s+=`<path d="${hatLines(0,-628,-556,108,17)}" stroke="${C.hatLine}" stroke-width="1.4" opacity=".75"/>`;
  s+=`<path d="M-108 -556 Q 0 -544 108 -556" stroke="${C.hatLine}" stroke-width="3" fill="none"/>`;
  s+=`<path d="M-72 -580 Q 0 -570 72 -580" stroke="${C.hatL}" stroke-width="2" fill="none" opacity=".8"/>`;
  return s;
}

/* ---------- Aurelia, side view facing right (feet 0,0; ~300 tall with hat). returns parts for leg animation ---------- */
function aureliaSide(){
  const s={};
  s.legBack=`<g id="legB"><path d="M-6 -44 L-8 -6" stroke="${C.skinD}" stroke-width="9" stroke-linecap="round"/><path d="M-12 -3 h18" stroke="${C.sandal}" stroke-width="5" stroke-linecap="round"/></g>`;
  s.legFront=`<g id="legF"><path d="M4 -44 L6 -6" stroke="${C.skin}" stroke-width="9" stroke-linecap="round"/><path d="M0 -3 h18" stroke="${C.sandal}" stroke-width="5" stroke-linecap="round"/></g>`;
  let b='';
  // far arm hanging
  b+=`<path d="M-4 -196 C -10 -170 -14 -150 -10 -128" stroke="${C.blouseD}" stroke-width="12" stroke-linecap="round" fill="none"/>`;
  b+=`<circle cx="-10" cy="-124" r="6" fill="${C.skinD}"/>`;
  s.farArm=b;const b0=b.length;
  // skirt
  b+=`<path d="M-22 -126 C -26 -96 -30 -70 -32 -40 L 30 -40 C 28 -70 24 -96 20 -126Z" fill="url(#taisR)"/>`;
  b+=`<path d="M6 -126 C 10 -96 14 -70 16 -40 L 30 -40 C 28 -70 24 -96 20 -126Z" fill="#000" opacity=".18"/>`;
  b+=`<path d="M-32 -42 H30" stroke="#241A16" stroke-width="4"/><path d="M-22 -124 H20" stroke="#241A16" stroke-width="5"/>`;
  s.skirt=b.slice(b0);const b1=b.length;
  // torso (slight forward lean)
  b+=`<path d="M-18 -204 C -26 -180 -26 -150 -22 -122 L 22 -122 C 26 -150 26 -176 16 -206 L 0 -212Z" fill="${C.blouse}"/>`;
  b+=`<path d="M8 -206 C 18 -176 20 -150 22 -122 L 12 -122 C 12 -150 10 -176 2 -208Z" fill="${C.blouseD}" opacity=".7"/>`;
  b+=`<path d="M-16 -180 c 4 8 4 18 1 26 M-4 -150 c 6 3 12 3 16 0" stroke="${C.blouseL}" stroke-width="2" fill="none" stroke-linecap="round"/>`;
  b+=`<path d="M-23 -130 C -8 -127 10 -127 23 -130 L 23 -120 C 10 -117 -8 -117 -23 -120Z" fill="#241A16"/>`;
  // selendang (tais scarf) hanging from the neck, as in the portrait
  b+=`<path d="M2 -208 C 10 -190 12 -170 10 -148 L 18 -148 C 20 -172 16 -194 8 -210Z" fill="url(#taisB)"/>`;
  s.torso=b.slice(b1);s.body=b;
  // pole + baskets (group so it can bob)
  const basket=(x,flip)=>{let g=`<g transform="translate(${x} -150)">`;
    g+=`<path d="M0 -40 L-24 0 M0 -40 L24 0" stroke="#6B5238" stroke-width="1.6"/>`;
    g+=`<path d="M-14 -2 C -22 -10 -22 -18 -14 -22 C -10 -14 -10 -8 -14 -2Z M12 -2 C 20 -10 26 -12 30 -10 C 26 -4 20 -2 12 -2Z" fill="${C.cleaf}"/>`;
    [[-16,-1],[-8,-3],[0,-4],[8,-3],[16,-1],[-12,-7],[-3,-9],[6,-8],[13,-6]].forEach(([cx,cy],i)=>{g+=`<circle cx="${cx}" cy="${cy}" r="4.6" fill="${i%3?C.cherry:C.cherryD}"/>`});
    g+=`<path d="M-26 0 L 26 0 L 21 34 L -21 34Z" fill="${C.basket}"/>`;
    g+=`<path d="M-25 9 H25 M-24 18 H24 M-22 27 H22" stroke="${C.basketD}" stroke-width="1.6"/>`;
    g+=`<path d="M-16 0 L-13 34 M-6 0 L-5 34 M4 0 L4 34 M14 0 L12 34" stroke="${C.basketD}" stroke-width="1.2" opacity=".8"/>`;
    g+=`<path d="M-27 0 H27" stroke="${C.basketD}" stroke-width="3"/>`;
    return g+'</g>';};
  s.pole=`<g id="pole"><path d="M-110 -192 L 112 -198" stroke="#8A6238" stroke-width="5" stroke-linecap="round"/>${basket(-100,1)}${basket(102,-1)}</g>`;
  // near arm reaching up to pole, head, hat
  let h='';
  h+=`<path d="M6 -198 C 18 -186 24 -178 22 -192" stroke="${C.blouse}" stroke-width="12" stroke-linecap="round" fill="none"/>`;
  h+=`<path d="M4 -200 C 14 -190 20 -186 26 -196" stroke="${C.blouse}" stroke-width="11" stroke-linecap="round" fill="none"/>`;
  h+=`<circle cx="26" cy="-197" r="5.5" fill="${C.skin}"/>`;
  s.poleArm=h;const h0=h.length;
  h+=`<path d="M-4 -222 L 8 -222 L 8 -206 L -4 -206Z" fill="${C.skinD}"/>`;
  // scarf/head profile
  h+=`<path d="M-18 -232 C -22 -256 -6 -268 8 -266 C 22 -264 26 -250 24 -236 C 22 -222 14 -214 6 -212 L -8 -210 C -16 -214 -18 -222 -18 -232Z" fill="#1C1614"/>`;
  h+=`<ellipse cx="-16" cy="-248" rx="10" ry="9" fill="#1C1614"/><path d="M-20 -250 C -10 -262 12 -264 24 -252 L 22 -246 C 10 -256 -8 -254 -18 -244Z" fill="#2E5E8A"/>`;
  h+=`<path d="M6 -256 C 16 -256 22 -250 23 -242 L 27 -236 L 23 -234 C 23 -226 20 -220 12 -218 C 6 -218 4 -224 4 -230Z" fill="${C.skin}"/>`;
  h+=`<circle cx="16" cy="-244" r="1.8" fill="${C.ink}"/><ellipse cx="16" cy="-233" rx="3.4" ry="2.4" fill="${C.cheek}" opacity=".45"/>`;
  h+=`<path d="M18 -226 q-3 1.5 -6 0" stroke="#6B3A22" stroke-width="1.4" fill="none"/>`;
  s.headOnly=h.slice(h0);
  s.head=h;
  return s;
}

/* ---------- driver, frontal, holding a cardboard sign (feet 0,0; ~300 tall) ---------- */
function driver(){
  let s='';
  s+=`<ellipse cx="0" cy="2" rx="46" ry="7" fill="#3E2E1E" opacity=".18"/>`;
  s+=`<path d="M-22 -6 h-14 c0 -6 4 -8 14 -8z M22 -6 h14 c0 -6 -4 -8 -14 -8z" fill="#2A2522"/>`;
  // trousers
  s+=`<path d="M-30 -140 L -28 -8 L -6 -8 L 0 -110 L 6 -8 L 28 -8 L 30 -140Z" fill="${C.trouser}"/>`;
  s+=`<path d="M10 -140 L 30 -140 L 28 -8 L 18 -8Z" fill="${C.trouserD}"/>`;
  s+=`<path d="M-30 -140 H30" stroke="#3A2A1C" stroke-width="6"/><rect x="-5" y="-143" width="10" height="7" fill="#C9A45A"/>`;
  // shirt
  s+=`<path d="M-44 -236 C -48 -210 -40 -170 -32 -138 L 32 -138 C 40 -170 48 -210 44 -236 L 12 -246 L -12 -246Z" fill="${C.shirt}"/>`;
  s+=`<path d="M22 -240 L 44 -236 C 48 -210 40 -170 32 -138 L 20 -138 C 28 -170 30 -210 22 -240Z" fill="${C.shirtD}"/>`;
  s+=`<path d="M-12 -246 L 0 -228 L 12 -246 M0 -228 V-140" stroke="${C.shirtD}" stroke-width="2.4" fill="none"/>`;
  s+=`<path d="M-34 -214 h18 v16 h-18z" fill="none" stroke="${C.shirtD}" stroke-width="2"/>`;
  // arms forward holding sign (sleeves short, forearms bare)
  s+=`<path d="M-44 -236 C -58 -226 -62 -206 -58 -190 L -40 -192 C -42 -206 -40 -218 -36 -226Z" fill="${C.shirt}"/>`;
  s+=`<path d="M44 -236 C 58 -226 62 -206 58 -190 L 40 -192 C 42 -206 40 -218 36 -226Z" fill="${C.shirtD}"/>`;
  s+=`<path d="M-50 -192 C -54 -176 -52 -164 -44 -156" stroke="${C.skinD}" stroke-width="12" stroke-linecap="round" fill="none"/>`;
  s+=`<path d="M50 -192 C 54 -176 52 -164 44 -156" stroke="${C.skinD}" stroke-width="12" stroke-linecap="round" fill="none"/>`;
  // neck/head
  s+=`<rect x="-8" y="-262" width="16" height="18" fill="${C.skinD}"/>`;
  s+=`<path d="M-22 -288 C -24 -262 -12 -250 0 -250 C 12 -250 24 -262 22 -288 C 20 -306 -20 -306 -22 -288Z" fill="${C.skinD}"/>`;
  s+=`<g fill="${C.ink}"><ellipse cx="-8" cy="-284" rx="1.8" ry="2.2"/><ellipse cx="8" cy="-284" rx="1.8" ry="2.2"/></g>`;
  s+=`<path d="M-11 -290 h6 M5 -290 h6" stroke="${C.ink}" stroke-width="1.8" stroke-linecap="round"/>`;
  s+=`<path d="M0 -282 C -2 -276 -2 -272 2 -271" stroke="#7A4A2A" stroke-width="1.6" fill="none"/>`;
  s+=`<path d="M-12 -266 C -8 -272 -2 -270 0 -268 C 2 -270 8 -272 12 -266 C 8 -264 -8 -264 -12 -266Z" fill="#2A2019"/>`;
  s+=`<ellipse cx="-24" cy="-282" rx="3" ry="6" fill="${C.skinD}"/><ellipse cx="24" cy="-282" rx="3" ry="6" fill="${C.skinD}"/>`;
  // cap
  s+=`<path d="M-24 -292 C -24 -318 24 -318 24 -292Z" fill="${C.cap}"/><path d="M-26 -292 C -10 -286 10 -286 30 -294 L 38 -290 C 20 -282 -10 -282 -26 -288Z" fill="${C.capD}"/>`;
  s+=`<circle cx="0" cy="-316" r="3" fill="${C.capD}"/>`;
  return s;
}

/* ---------- old truck, side view facing left (front at x=0, ground at 0) ---------- */
function truck(){
  let s='';
  s+=`<ellipse cx="200" cy="4" rx="240" ry="10" fill="#3E2E1E" opacity=".18"/>`;
  // chassis
  s+=`<rect x="-8" y="-64" width="440" height="14" fill="#3A332C"/>`;
  // cargo bed with wooden slat sides
  s+=`<rect x="120" y="-176" width="310" height="112" fill="#B98A58"/>`;
  s+=[0,1,2,3,4].map(i=>`<path d="M120 ${-176+i*22+20} H430" stroke="#9C6F42" stroke-width="3"/>`).join('');
  s+=[0,1,2,3].map(i=>`<rect x="${128+i*98}" y="-180" width="10" height="118" fill="#7E5634"/>`).join('');
  // sacks and crates above slats
  s+=`<path d="M140 -176 C 138 -210 170 -216 190 -206 C 210 -218 236 -210 234 -176Z" fill="#D9C7A0"/><path d="M160 -196 q14 -6 28 0" stroke="#BFAA80" stroke-width="2" fill="none"/>`;
  s+=`<path d="M236 -176 C 236 -214 270 -222 292 -208 C 312 -220 336 -210 334 -176Z" fill="#CDB98F"/>`;
  s+=`<rect x="340" y="-222" width="76" height="46" fill="#C58B4E"/><path d="M340 -206 H416 M340 -192 H416" stroke="#9E6834" stroke-width="2"/>`;
  // cab
  s+=`<path d="M0 -64 L 0 -130 C 0 -146 6 -156 20 -162 L 34 -206 C 38 -214 44 -218 54 -218 L 118 -218 C 124 -218 128 -214 128 -206 L 128 -64Z" fill="#A5462C"/>`;
  s+=`<path d="M92 -218 L 118 -218 C 124 -218 128 -214 128 -206 L 128 -64 L 100 -64Z" fill="#8A3822"/>`;
  s+=`<path d="M26 -160 L 40 -200 C 42 -205 46 -208 52 -208 L 88 -208 L 88 -160Z" fill="#9DB3C0"/>`;
  s+=`<path d="M40 -196 L 60 -206" stroke="#C3D2DA" stroke-width="5" stroke-linecap="round"/>`;
  s+=`<path d="M94 -206 V -80 M26 -150 H 94" stroke="#7E311D" stroke-width="2.4" fill="none"/>`;
  s+=`<rect x="74" y="-140" width="14" height="5" rx="2" fill="#E4D3B4"/>`;
  s+=`<path d="M22 -188 L 10 -196 L 8 -176Z" fill="#3A332C"/>`;
  // grille, bumper, lights
  s+=`<rect x="-6" y="-128" width="10" height="56" fill="#3A332C"/>`;
  s+=`<rect x="-14" y="-82" width="40" height="14" rx="3" fill="#8A847A"/>`;
  s+=`<circle cx="4" cy="-118" r="7" fill="#EAD9A6"/>`;
  // fenders + wheels
  const wheel=x=>`<path d="M${x-44} -64 A 44 44 0 0 1 ${x+44} -64Z" fill="#7E311D"/><g transform="translate(${x} -30)"><circle r="32" fill="#2A2522"/><circle r="17" fill="#8A847A"/><circle r="6" fill="#4A443E"/>${[0,1,2,3,4,5].map(i=>`<circle cx="${Math.cos(i*Math.PI/3)*11}" cy="${Math.sin(i*Math.PI/3)*11}" r="2" fill="#4A443E"/>`).join('')}</g>`;
  s+=wheel(62)+wheel(300)+wheel(376);
  return s;
}

/* ---------- eucalyptus-like tree (base at 0,0) ---------- */
function tree(h=220,seed=1,tone=0){
  const r=(i)=>{const x=Math.sin((i+seed*13.1)*127.1)*43758.5453;return x-Math.floor(x)};
  const g=['#5F8A5E','#557E55','#6E9667'][tone%3], gd='#466B47', gl='#86A97A';
  let s=`<path d="M-4 0 C -2 ${-h*.3} -3 ${-h*.55} 0 ${-h*.7} C 3 ${-h*.55} 4 ${-h*.3} 5 0Z" fill="#CFC2A6"/>`;
  s+=`<path d="M0 ${-h*.45} C 10 ${-h*.52} 18 ${-h*.6} 26 ${-h*.7} M0 ${-h*.55} C -10 ${-h*.62} -16 ${-h*.7} -22 ${-h*.78}" stroke="#BFB194" stroke-width="3" fill="none"/>`;
  const blobs=[[0,-.86,.34],[-.2,-.74,.26],[.22,-.72,.28],[-.08,-.62,.24],[.14,-.95,.22],[-.18,-.92,.2]];
  blobs.forEach(([bx,by,br],i)=>{const rr=h*br*(.85+r(i)*.3);const cx=bx*h,cy=by*h;
    s+=`<ellipse cx="${cx.toFixed(1)}" cy="${(cy+rr*.18).toFixed(1)}" rx="${(rr*1.02).toFixed(1)}" ry="${(rr*.72).toFixed(1)}" fill="${gd}"/>`;
    s+=`<ellipse cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" rx="${rr.toFixed(1)}" ry="${(rr*.7).toFixed(1)}" fill="${g}"/>`;
  });
  // leaf ticks
  let t='';for(let i=0;i<18;i++){const a=r(i+40)*Math.PI*2, d=r(i+60)*h*.28;const x=Math.cos(a)*d, y=-h*.8+Math.sin(a)*d*.6;t+=`M${x.toFixed(1)} ${y.toFixed(1)} l${(3+r(i)*4).toFixed(1)} -3 `}
  s+=`<path d="${t}" stroke="${gl}" stroke-width="1.6" stroke-linecap="round" opacity=".8"/>`;
  return s;
}

/* ---------- striped field patch helper (thin parallel lines clipped to shape) ---------- */
let _fid=0;
function field(d, base, line, angle=0, gap=9, w=1.6){
  const id='fp'+(++_fid);
  return `<defs><pattern id="${id}" width="${gap}" height="${gap}" patternUnits="userSpaceOnUse" patternTransform="rotate(${angle})"><rect width="${gap}" height="${gap}" fill="${base}"/><rect width="${gap}" height="${w}" fill="${line}"/></pattern></defs><path d="${d}" fill="url(#${id})"/>`;
}

return {C, aureliaFront, aureliaSide, driver, truck, tree, field, cherryBranch};
})();

/* ================= HERO CLOSE-UP (reference-grade) ================= */
FIG.H = {
  sky:'#BCD5E8', cloud:'#F3F5F4', cloudS:'#DCE7EE', m1:'#A3C1DA', m2:'#8DB0CE', m2d:'#7C9FBF',
  f1:'#95C08F', f1l:'#7FAF7E', f2:'#A9CC9C', f2l:'#94BC8A', fd:'#2E4D44', fdl:'#467062',
  jk:'#3F8B5C', jkd:'#2D6B46', jkl:'#62A77A', sc:'#2E5E8A', scd:'#1F4166',
  sk:'#C47B53', skd:'#A5603D', ck:'#DE7663', hat:'#DA9C5A', hatd:'#B97A3E', hatl:'#9B5B28',
  skirt:'#B7462E', skirtd:'#973622', stripe:'#F2D3A6', cream:'#F3DDB4', creaml:'#C9573B',
  dark:'#1E2B33', bsk:'#D18C4B', bskl:'#9D5B2A', car:'#C23A2E', card:'#9E2A24', lf:'#2F5E3A', lfl:'#5E8F5E'
};
FIG.heroScene = function(){
  const H=FIG.H; let s='';
  // clouds (big flat arcs like the reference)
  const cl=(x,y,w,h)=>`<path d="M${x} ${y} C ${x} ${y-h*.6} ${x+w*.18} ${y-h} ${x+w*.34} ${y-h*.8} C ${x+w*.42} ${y-h*1.25} ${x+w*.7} ${y-h*1.2} ${x+w*.74} ${y-h*.72} C ${x+w*.88} ${y-h*.9} ${x+w} ${y-h*.4} ${x+w} ${y}Z" fill="${H.cloud}"/>`;
  s+=`<g id="hsCloud">${cl(-60,420,520,210)}${cl(980,330,560,240)}${cl(640,380,300,110)}</g>`;
  s+=`<g id="hsBirds" fill="#7D9DBB">${[[560,120,1],[760,90,.8],[1010,150,1.1],[1180,110,.7]].map(([x,y,k])=>`<path transform="translate(${x} ${y}) scale(${k})" d="M-22 4 C -12 -6 -4 -6 0 2 C 4 -6 12 -6 22 4 C 12 0 4 2 0 6 C -4 2 -12 0 -22 4Z"/>`).join('')}</g>`;
  // mountains
  s+=`<g id="hsMount"><path d="M-40 560 L 170 330 L 330 460 L 520 300 L 760 560Z" fill="${H.m1}"/>
      <path d="M700 560 L 1010 250 L 1180 400 L 1300 330 L 1500 520 L1500 560Z" fill="${H.m2}"/>
      <path d="M1010 250 L 1180 400 L 1120 560 L 1010 560Z" fill="${H.m2d}" opacity=".5"/></g>`;
  // patchwork fields with line textures (left) + dark-banded terraces (right)
  const pat=(id,base,line,ang,gap,w)=>`<pattern id="${id}" width="${gap}" height="${gap}" patternUnits="userSpaceOnUse" patternTransform="rotate(${ang})"><rect width="${gap}" height="${gap}" fill="${base}"/><rect width="${gap}" height="${w}" fill="${line}"/></pattern>`;
  s+=`<defs>${pat('hp1',H.f1,H.f1l,0,11,2.2)}${pat('hp2',H.f1,H.f1l,90,11,2.2)}${pat('hp3',H.f2,H.f2l,0,9,2)}${pat('hp4',H.f2,H.f2l,90,9,2)}${pat('hp5',H.f1,H.f1l,45,10,2)}</defs>`;
  s+=`<g id="hsFields">`;
  const cells=[[0,560,180,120,'hp1'],[180,560,160,120,'hp4'],[340,560,200,120,'hp3'],[540,560,180,120,'hp2'],[720,560,160,120,'hp5'],
               [0,680,140,240,'hp4'],[140,680,220,240,'hp1'],[360,680,160,240,'hp2'],[520,680,220,240,'hp3'],[740,680,200,240,'hp1']];
  cells.forEach(([x,y,w,h,p])=>{s+=`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="url(#${p})"/><rect x="${x}" y="${y}" width="${w}" height="${h}" fill="none" stroke="${H.f1}" stroke-width="3"/>`});
  // right terraces: stacked curved bands
  for(let i=0;i<7;i++){const y=520+i*58; s+=`<path d="M860 ${y+120} C 980 ${y+10} 1180 ${y-30} 1500 ${y-10} L1500 ${y+60} C 1200 ${y+40} 1010 ${y+70} 900 ${y+160}Z" fill="${i%2?H.f2:H.f1}"/>`;
    s+=`<path d="M860 ${y+120} C 980 ${y+10} 1180 ${y-30} 1500 ${y-10}" stroke="${H.fd}" stroke-width="9" fill="none"/>`;
    s+=`<path d="M880 ${y+136} C 1000 ${y+34} 1190 ${y-4} 1500 ${y+14}" stroke="${H.f1l}" stroke-width="2" fill="none"/><path d="M890 ${y+150} C 1010 ${y+52} 1196 ${y+16} 1500 ${y+34}" stroke="${H.f1l}" stroke-width="2" fill="none"/>`}
  s+=`</g>`;
  return s;
};
FIG.aureliaHero = function(){
  const H=FIG.H; let s='';
  // origin = base of neck. figure extends to ~ +720 (cropped by frame)
  s+='<g transform="scale(.86 1)">';
  // --- skirt
  s+=`<path d="M-150 300 C -170 420 -190 560 -205 740 L 215 740 C 200 560 180 420 160 300Z" fill="url(#taisRL)"/>`;
  s+=`<path d="M60 300 C 90 420 120 560 140 740 L 215 740 C 200 560 180 420 160 300Z" fill="#000" opacity=".18"/>`;
  let st='';for(let i=0;i<9;i++){const t=(i+.5)/9, xt=-140+300*t, xb=-195+400*t; st+=`M${xt.toFixed(1)} 316 C ${(xt+(xb-xt)*.3).toFixed(1)} 480 ${(xb-(xb-xt)*.1).toFixed(1)} 620 ${xb.toFixed(1)} 740 `}
  
  // --- jacket body
  s+=`<path d="M-128 18 C -170 40 -178 110 -176 190 C -174 250 -168 300 -164 330 L 172 330 C 176 300 180 250 182 190 C 184 110 176 40 132 18 L 40 0 L -40 0Z" fill="${H.jk}"/>`;
  s+=`<path d="M70 8 L132 18 C 176 40 184 110 182 190 C 180 250 176 300 172 330 L 110 330 C 128 250 126 110 70 8Z" fill="${H.jkd}"/>`;
  // dark hem band (reference-style accent)
  s+=`<path d="M-166 318 C -60 332 70 334 174 318 L 176 346 C 70 360 -60 358 -168 344Z" fill="${H.dark}"/>`;
  // placket, buttons, folds
  s+=`<path d="M4 40 C 6 120 4 220 2 316" stroke="${H.jkd}" stroke-width="3" fill="none"/>`;
  s+=[70,120,170].map(y=>`<circle cx="${6+y*0}" cy="${y}" r="5" fill="${H.stripe}"/>`).join('');
  s+=`<path d="M-120 120 c 10 18 12 40 6 60 M-98 230 c 14 10 30 12 44 6 M120 150 c -8 22 -8 44 0 64" stroke="${H.jkl}" stroke-width="3" fill="none" stroke-linecap="round"/>`;
  // --- selendang (tais scarf) around the neck
  s+=`<path d="M-44 -24 C -62 10 -66 80 -62 200 L -30 200 C -34 90 -30 20 -14 -14Z M44 -24 C 62 10 66 80 62 200 L 30 200 C 34 90 30 20 14 -14Z" fill="url(#taisBL)"/>`;
  // --- sling (cream cloth) from right shoulder down to left hip, forming a pouch
  s+=`<path d="M92 -8 L 128 14 L -60 260 L -110 236Z" fill="${H.cream}"/>`;
  s+=`<path d="M100 0 L -94 246" stroke="${H.creaml}" stroke-width="2.4"/>`;
  s+=`<path d="M122 16 L -66 256" stroke="${H.creaml}" stroke-width="2.4" opacity=".7"/>`;
  // pouch holding a basket of coffee cherries at viewer's left
  s+=`<g transform="translate(-160 230)">`;
  // basket rim + cherries (behind pouch front)
  s+=`<path d="M-70 -30 L 90 -30 L 80 30 L -60 30Z" fill="${H.bskl}"/>`;
  const cr=[[-56,-36],[-40,-42],[-24,-46],[-8,-47],[8,-48],[24,-46],[40,-44],[56,-40],[72,-36],[-48,-26],[-30,-30],[-12,-32],[6,-33],[24,-32],[42,-30],[60,-27]];
  s+=`<path d="M-44 -46 C -62 -64 -60 -86 -40 -94 C -34 -74 -36 -58 -44 -46Z M50 -46 C 70 -70 92 -74 104 -68 C 92 -52 72 -44 50 -46Z M8 -50 C 2 -74 10 -94 28 -100 C 30 -80 22 -62 8 -50Z" fill="${H.lf}"/>`;
  s+=`<path d="M-44 -46 C -48 -62 -46 -78 -40 -94 M50 -46 C 66 -60 84 -68 104 -68 M8 -50 C 10 -70 18 -88 28 -100" stroke="${H.lfl}" stroke-width="2" fill="none"/>`;
  cr.forEach(([x,y],i)=>{
    s+=`<circle cx="${x}" cy="${y+8}" r="11" fill="${i%3?H.car:H.card}"/><circle cx="${x-3.5}" cy="${y+4.5}" r="3.2" fill="#E8776A" opacity=".75"/>`;
  });
  // pouch front
  s+=`<path d="M-96 -24 C -108 40 -60 92 20 94 C 96 92 130 40 118 -22 C 60 -4 -40 -6 -96 -24Z" fill="${H.cream}"/>`;
  s+=`<path d="M-96 -24 C -40 -6 60 -4 118 -22" stroke="${H.creaml}" stroke-width="3" fill="none"/>`;
  s+=`<path d="M-80 10 C -50 50 0 66 60 60 M-60 40 C -30 66 20 76 80 66" stroke="#E2C592" stroke-width="3" fill="none"/>`;
  s+=`</g>`;
  // --- arms
  // viewer-left arm: from shoulder down, elbow out, forearm under pouch
  s+=`<path d="M-128 18 C -176 34 -200 110 -206 180 C -210 222 -200 248 -176 262 L -150 236 C -166 220 -170 196 -166 170 C -160 120 -150 80 -130 58Z" fill="${H.jk}"/>`;
  s+=`<path d="M-206 180 C -210 222 -200 248 -176 262 L -164 250 C -186 236 -194 212 -190 180Z" fill="${H.jkd}"/>`;
  s+=`<path d="M-184 250 L -152 222 L -134 244 L -164 270Z" fill="${H.skirt}"/>`; // rust cuff
  // hand under pouch
  s+=`<path d="M-150 250 C -130 244 -110 250 -104 262 C -100 272 -110 280 -124 278 C -140 276 -154 270 -150 250Z" fill="${H.sk}"/>`;
  s+=`<path d="M-128 262 q 8 2 16 0 M-132 270 q 8 2 14 0" stroke="${H.skd}" stroke-width="2" fill="none"/>`;
  // viewer-right arm: crosses body to grip the sling/pouch
  s+=`<path d="M132 18 C 176 36 196 100 196 160 C 196 200 184 226 160 240 L 60 262 L 50 234 L 140 208 C 150 180 152 130 140 80Z" fill="${H.jk}"/>`;
  s+=`<path d="M150 30 C 186 54 196 110 196 160 C 196 200 184 226 160 240 L 150 226 C 170 210 176 180 174 150 C 172 100 164 60 150 30Z" fill="${H.jkd}"/>`;
  s+=`<path d="M58 232 L 84 226 L 90 256 L 64 262Z" fill="${H.skirt}"/>`; // cuff
  // hand with fingers gripping the pouch edge
  s+=`<path d="M60 236 C 40 230 18 232 4 242 C -6 250 -4 262 8 264 L 30 262 C 44 266 58 262 62 250Z" fill="${H.sk}"/>`;
  s+=`<path d="M6 250 h24 M4 258 h22" stroke="${H.skd}" stroke-width="2" stroke-linecap="round"/>`;
  s+='</g>';
  // --- neck
  s+=`<path d="M-20 -30 L 20 -30 L 22 6 L -22 6Z" fill="${H.skd}"/>`;
  // --- head: scarf back, face, scarf front band
  s+=`<ellipse cx="0" cy="-168" rx="30" ry="22" fill="#1C1614"/><ellipse cx="-44" cy="-72" rx="8" ry="13" fill="${H.skd}"/><ellipse cx="44" cy="-72" rx="8" ry="13" fill="${H.skd}"/>`;
  
  s+=`<path d="M-42 -100 C -44 -54 -24 -22 0 -20 C 24 -22 44 -54 42 -100 C 40 -126 -40 -126 -42 -100Z" fill="${H.sk}"/>`;
  s+=`<path d="M-48 -84 C -54 -140 -20 -152 0 -150 C 26 -150 54 -138 48 -84 C 42 -108 28 -122 6 -124 C 2 -118 -2 -118 -6 -124 C -28 -122 -42 -108 -48 -84Z" fill="#1C1614"/><path d="M-50 -118 C -30 -140 30 -140 50 -118 L 48 -104 C 30 -124 -30 -124 -48 -104Z" fill="#2E5E8A"/><path d="M-48 -112 C -28 -130 28 -130 48 -112" stroke="#E4B64C" stroke-width="2.4" fill="none" stroke-dasharray="4 4"/><path d="M44 -120 l30 -16 l-6 22Z M46 -110 l28 8 l-22 12Z" fill="#2E5E8A"/>`;
  // ears hidden; face details
  s+=`<g fill="${H.ck}" opacity=".7"><circle cx="-24" cy="-58" r="8"/><circle cx="24" cy="-58" r="8"/></g>`;
  s+=`<path d="M-28 -84 q8 -5 16 -1 M12 -85 q8 -4 16 1" stroke="${H.dark}" stroke-width="2.6" fill="none" stroke-linecap="round"/>`;
  s+=`<g fill="${H.dark}"><ellipse cx="-18" cy="-72" rx="3.2" ry="3.8"/><ellipse cx="18" cy="-72" rx="3.2" ry="3.8"/></g>`;
  s+=`<path d="M-2 -70 C -6 -60 -8 -54 -2 -52 C 2 -51 5 -52 6 -54" stroke="${H.skd}" stroke-width="2.6" fill="none" stroke-linecap="round"/>`;
  s+=`<path d="M-10 -40 Q 0 -34 10 -40" stroke="#7A3A26" stroke-width="3" fill="none" stroke-linecap="round"/>`;
  return s;
};

/* ---------- coconut palm (base 0,0) ---------- */
FIG.palm = function(h=260, lean=1, seed=1){
  const r=i=>{const x=Math.sin((i+seed*7.3)*127.1)*43758.5453;return x-Math.floor(x)};
  const tx=lean*h*.18, ty=-h;
  let s=`<path d="M-7 0 C ${-6+tx*.2} ${-h*.4} ${tx*.6-4} ${-h*.8} ${tx-3} ${ty} L ${tx+3} ${ty} C ${tx*.6+4} ${-h*.8} ${6+tx*.2} ${-h*.4} 7 0Z" fill="#9A8466"/>`;
  let rings='';for(let i=1;i<14;i++){const t=i/14;const x=tx*t*t*.9+tx*.1*t, y=-h*t;rings+=`M${(x-6+t*3).toFixed(1)} ${y.toFixed(1)} l${(12-t*6).toFixed(1)} -2 `}
  s+=`<path d="${rings}" stroke="#7D6A51" stroke-width="1.6"/>`;
  const fr=[[-160,1.0],[-130,.9],[-100,.8],[-60,.85],[-25,.95],[10,1],[-200,.7],[35,.7]];
  fr.forEach(([a,l],i)=>{const ang=a*Math.PI/180, L=h*.42*l;const ex=Math.cos(ang)*L, ey=Math.sin(ang)*L*.55+L*.25;
    const mx=ex*.5, my=ey*.5-L*.28;
    const col=i%2?'#4F7C4E':'#5E8A5A';
    s+=`<g transform="translate(${tx} ${ty})"><path d="M0 0 Q ${mx} ${my-10} ${ex} ${ey} Q ${mx} ${my+10} 0 0Z" fill="${col}"/>`;
    let cuts='';for(let k=1;k<7;k++){const t=k/7;const px=(1-t)*(1-t)*0+2*(1-t)*t*mx+t*t*ex, py=2*(1-t)*t*my+t*t*ey;cuts+=`M${px.toFixed(1)} ${py.toFixed(1)} l${(Math.sin(ang)*8).toFixed(1)} ${(-Math.cos(ang)*8+4).toFixed(1)} `}
    s+=`<path d="M0 0 Q ${mx} ${my} ${ex} ${ey}" stroke="#3E6440" stroke-width="1.6" fill="none"/><path d="${cuts}" stroke="#86A97A" stroke-width="1.2" opacity=".8"/></g>`;
  });
  s+=`<g fill="#7A5A36"><circle cx="${tx-5}" cy="${ty+8}" r="5"/><circle cx="${tx+5}" cy="${ty+9}" r="5"/><circle cx="${tx}" cy="${ty+14}" r="5"/></g>`;
  return s;
};
/* ---------- flat-top acacia-like tree, layered canopy (base 0,0) ---------- */
FIG.flattop = function(h=200, seed=1){
  const r=i=>{const x=Math.sin((i+seed*5.1)*127.1)*43758.5453;return x-Math.floor(x)};
  let s=`<path d="M-5 0 C -4 ${-h*.3} -2 ${-h*.5} 0 ${-h*.62} C 2 ${-h*.5} 4 ${-h*.3} 5 0Z" fill="#6E5A44"/>`;
  s+=`<path d="M0 ${-h*.5} C -14 ${-h*.62} -30 ${-h*.7} -46 ${-h*.74} M0 ${-h*.55} C 16 ${-h*.66} 32 ${-h*.72} 50 ${-h*.76}" stroke="#6E5A44" stroke-width="4" fill="none" stroke-linecap="round"/>`;
  const W=h*.62;
  [[0,-.78,1,'#557E55'],[-.12,-.88,.72,'#62905F'],[.14,-.94,.56,'#6E9A63']].forEach(([dx,dy,sc,col],i)=>{
    const cx=dx*h, cy=dy*h, w=W*sc, hh=h*.09*(1+sc*.4);
    s+=`<path d="M${cx-w} ${cy+hh*.4} C ${cx-w*.8} ${cy-hh} ${cx+w*.8} ${cy-hh} ${cx+w} ${cy+hh*.4} Z" fill="${col}"/>`;
    s+=`<path d="M${cx-w} ${cy+hh*.4} H${cx+w}" stroke="#3F633F" stroke-width="4"/>`;
    let t='';for(let k=0;k<6;k++){const x=cx-w*.7+k*w*.28+r(k+i*9)*8;t+=`M${x.toFixed(1)} ${(cy-hh*.1).toFixed(1)} l6 -4 `}
    s+=`<path d="${t}" stroke="#86A97A" stroke-width="1.5" stroke-linecap="round" opacity=".8"/>`;
  });
  return s;
};

/* ---------- villager: side view facing right, feet at 0,0. opts: {male, top, topD, bot, botD, scarf, hat:'cone'|'cap'|null, pose:'down'|'fist'|'point'|'cross'|'pole'|'sign', far:'down'|'fist', stache} ---------- */
FIG.villager = function(o){
  const C=FIG.C, skin=o.skin||C.skin, skinD=o.skinD||C.skinD;
  let s='';
  s+=`<ellipse cx="0" cy="2" rx="30" ry="5" fill="#3E2E1E" opacity=".18"/>`;
  // far arm (behind body)
  const farArm = o.far==='fist'
    ? `<g class="wave"><path d="M-6 -198 C -14 -226 -12 -250 -8 -272" stroke="${o.topD}" stroke-width="12" stroke-linecap="round" fill="none"/><circle cx="-8" cy="-278" r="7" fill="${skinD}"/></g>`
    : `<path d="M-4 -196 C -10 -170 -14 -150 -10 -128" stroke="${o.topD}" stroke-width="12" stroke-linecap="round" fill="none"/><circle cx="-10" cy="-124" r="6" fill="${skinD}"/>`;
  s+=farArm;
  if(o.male){
    // trousers
    s+=`<path d="M-16 -124 L -14 -4 L -2 -4 L 0 -96 L 4 -4 L 16 -4 L 18 -124Z" fill="${o.bot}"/>`;
    s+=`<path d="M4 -124 L 18 -124 L 16 -4 L 6 -4Z" fill="${o.botD}"/>`;
    s+=`<path d="M-18 -2 h18 M2 -2 h20" stroke="#2A2522" stroke-width="6" stroke-linecap="round"/>`;
    s+=`<path d="M-18 -126 H20" stroke="#3A2A1C" stroke-width="5"/>`;
  } else {
    s+=`<path d="M-6 -44 L-8 -6 M4 -44 L6 -6" stroke="${skinD}" stroke-width="9" stroke-linecap="round"/><path d="M-12 -3 h18 M0 -3 h18" stroke="${C.sandal}" stroke-width="5" stroke-linecap="round"/>`;
    s+=`<path d="M-22 -126 C -26 -96 -30 -70 -32 -40 L 30 -40 C 28 -70 24 -96 20 -126Z" fill="${o.bot}"/>`;
    s+=`<path d="M6 -126 C 10 -96 14 -70 16 -40 L 30 -40 C 28 -70 24 -96 20 -126Z" fill="${o.botD}"/>`;
    s+=`<path d="M-14 -124 L-20 -42 M-4 -124 L-6 -42 M6 -124 L8 -42 M15 -124 L22 -42" stroke="${C.stripe}" stroke-width="1.6" opacity=".85"/>`;
    s+=`<path d="M-32 -44 H30" stroke="${o.botD}" stroke-width="5"/>`;
  }
  // torso
  const w=o.male?3:0;
  s+=`<path d="M${-18-w} -206 C ${-26-w} -180 ${-26-w} -150 ${-22-w} -122 L ${22+w} -122 C ${26+w} -150 ${26+w} -176 ${16+w} -208 L 0 -214Z" fill="${o.top}"/>`;
  s+=`<path d="M${8} -208 C 18 -176 20 -150 ${22+w} -122 L 12 -122 C 12 -150 10 -176 2 -210Z" fill="${o.topD}" opacity=".6"/>`;
  if(o.male) s+=`<path d="M2 -212 L 10 -196 L 16 -210" stroke="${o.topD}" stroke-width="2.5" fill="none"/>`;
  // near arm by pose
  const hand=(x,y,r=6.5)=>`<circle cx="${x}" cy="${y}" r="${r}" fill="${skin}"/>`;
  const arm=(d)=>`<path d="${d}" stroke="${o.top}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" fill="none"/>`;
  switch(o.pose){
    case 'fist': s+=`<g class="wave">${arm('M6 -200 C 18 -226 22 -250 22 -276')}${hand(22,-283,8)}</g>`; break;
    case 'point': s+=`<g class="jab">${arm('M6 -200 C 26 -198 44 -196 62 -198')}${hand(68,-198)}<path d="M72 -199 h10" stroke="${skin}" stroke-width="4" stroke-linecap="round"/></g>`; break;
    case 'cross': s+=arm('M6 -200 C 4 -180 2 -166 0 -160 L 24 -164')+hand(26,-164); break;
    case 'pole': s+=arm('M6 -200 C 18 -206 24 -220 26 -232')+hand(28,-236); break;
    case 'sign': s+=`<g class="wave">${arm('M6 -200 C 20 -214 28 -236 30 -258')}${hand(31,-264)}</g>`; break;
    default: s+=arm('M6 -198 C 10 -176 12 -152 10 -130')+hand(10,-126);
  }
  // neck + head
  s+=`<path d="M-4 -224 L 8 -224 L 8 -208 L -4 -208Z" fill="${skinD}"/>`;
  if(o.male){
    s+=`<path d="M-14 -240 C -16 -262 0 -272 12 -268 C 22 -264 26 -254 24 -240 C 24 -226 18 -218 8 -216 C -4 -216 -14 -226 -14 -240Z" fill="${skin}"/>`;
    s+=`<path d="M-15 -238 C -18 -262 0 -274 14 -268 C 22 -266 24 -258 22 -252 C 12 -256 4 -254 0 -246 C -4 -242 -8 -236 -15 -238Z" fill="#231C14"/>`;
    s+=`<path d="M23 -244 L 28 -238 L 23 -236Z" fill="${skin}"/>`;
    s+=`<circle cx="15" cy="-246" r="1.9" fill="#231C14"/>`;
    if(o.stache) s+=`<path d="M14 -232 C 18 -234 24 -234 26 -231 C 22 -229 17 -229 14 -232Z" fill="#231C14"/>`;
    s+=`<path d="M17 -226 q4 1 7 -1" stroke="#6B3A22" stroke-width="1.4" fill="none"/>`;
    s+=`<ellipse cx="-4" cy="-240" rx="4" ry="6" fill="${skinD}"/>`;
  } else {
    s+=`<path d="M-18 -232 C -22 -256 -6 -268 8 -266 C 22 -264 26 -250 24 -236 C 22 -222 14 -214 6 -212 L -8 -210 C -16 -214 -18 -222 -18 -232Z" fill="${o.scarf}"/>`;
    s+=`<path d="M6 -256 C 16 -256 22 -250 23 -242 L 27 -236 L 23 -234 C 23 -226 20 -220 12 -218 C 6 -218 4 -224 4 -230Z" fill="${skin}"/>`;
    s+=`<circle cx="16" cy="-244" r="1.8" fill="#231C14"/><ellipse cx="16" cy="-233" rx="3.4" ry="2.4" fill="${C.cheek}" opacity=".45"/>`;
    s+=`<path d="M18 -226 q-3 1.5 -6 0" stroke="#6B3A22" stroke-width="1.4" fill="none"/>`;
  }
  if(o.hat==='cone'){
    s+=`<ellipse cx="4" cy="${o.male?-266:-262}" rx="46" ry="5" fill="${C.hatD}"/>`;
    s+=`<g transform="translate(0 ${o.male?-4:0})"><path d="M-44 -264 L 4 -296 L 52 -264 Q 4 -258 -44 -264Z" fill="${C.hat}"/><path d="M4 -296 L 52 -264 Q 30 -260 16 -259Z" fill="${C.hatD}" opacity=".5"/><path d="M4 -296 L-30 -262 M4 -296 L-12 -260 M4 -296 L6 -259 M4 -296 L24 -260 M4 -296 L40 -262" stroke="${C.hatLine}" stroke-width="1" opacity=".75"/></g>`;
  } else if(o.hat==='cap'){
    s+=`<path d="M-16 -250 C -16 -276 22 -278 24 -254Z" fill="${o.capC||'#3F5F43'}"/><path d="M18 -256 L 40 -252 L 22 -249Z" fill="${o.capD||'#2F4A33'}"/>`;
  }
  return s;
};

/* ================= FRONTAL PERSON (reference-style) =================
   feet at (0,0), ~340 tall with hat. o = {male, top, topD, inner, bot, botD, scarf, scarfD, hat:'cone'|'cap'|null,
   capC, L:'down'|'fist'|'point'|'hold'|'hip'|'cross', R:(same), stache, cuff, skin, skinD, bag} */
FIG.person = function(o){
  const C=FIG.C, sk=o.skin||'#C07A52', skd=o.skinD||'#A0613E', dark='#1E2B33';
  const limb=(x0,y0,x1,y1,w0,w1,col)=>{const a=Math.atan2(y1-y0,x1-x0)+Math.PI/2,c=Math.cos(a),s=Math.sin(a);
    return `<path d="M${(x0+c*w0/2).toFixed(1)} ${(y0+s*w0/2).toFixed(1)} L${(x1+c*w1/2).toFixed(1)} ${(y1+s*w1/2).toFixed(1)} L${(x1-c*w1/2).toFixed(1)} ${(y1-s*w1/2).toFixed(1)} L${(x0-c*w0/2).toFixed(1)} ${(y0-s*w0/2).toFixed(1)}Z" fill="${col}"/><circle cx="${x1}" cy="${y1}" r="${w1/2}" fill="${col}"/>`;};
  const fist=(x,y,r=9)=>`<circle cx="${x}" cy="${y}" r="${r}" fill="${sk}"/><path d="M${x-r*.6} ${y-r*.2} h${r*1.2} M${x-r*.6} ${y+r*.25} h${r*1.2}" stroke="${skd}" stroke-width="1.6" stroke-linecap="round"/>`;
  const handDown=(x,y)=>`<path d="M${x-8} ${y-4} C ${x-9} ${y+8} ${x-5} ${y+16} ${x} ${y+16} C ${x+5} ${y+16} ${x+9} ${y+8} ${x+8} ${y-4}Z" fill="${sk}"/><path d="M${x-3} ${y+6} v7 M${x+2} ${y+6} v8" stroke="${skd}" stroke-width="1.4" stroke-linecap="round"/>`;
  const sy=-222, sw=o.male?46:40; // shoulder y, half-width
  const cuffC=o.cuff||null;
  const arm=(side,pose)=>{ // side -1 = viewer-left
    const sx=side*sw, col=o.top, colD=o.topD; let s='';
    const cuff=(x,y,ang=0)=>cuffC?`<circle cx="${x}" cy="${y}" r="10" fill="${cuffC}"/>`:'';
    switch(pose){
      case 'fist': s+=limb(sx,sy+6,sx+side*26,sy-40,24,20,col)+limb(sx+side*26,sy-40,sx+side*20,sy-92,20,17,col)+cuff(sx+side*20,sy-90)+fist(sx+side*20,sy-104,10); break;
      case 'point': s+=limb(sx,sy+6,sx+side*46,sy+10,24,20,col)+limb(sx+side*46,sy+10,sx+side*92,sy+2,20,17,col)+cuff(sx+side*92,sy+2)+`<circle cx="${sx+side*104}" cy="${sy+2}" r="8" fill="${sk}"/><path d="M${sx+side*108} ${sy} h${side*16}" stroke="${sk}" stroke-width="5" stroke-linecap="round"/>`; break;
      case 'hold': s+=limb(sx,sy+6,sx+side*24,sy-26,24,20,col)+limb(sx+side*24,sy-26,sx+side*20,sy-66,20,17,col)+cuff(sx+side*20,sy-64)+fist(sx+side*20,sy-76,9); break;
      case 'hip': s+=limb(sx,sy+6,sx+side*30,sy+52,24,20,col)+limb(sx+side*30,sy+52,sx+side*10,sy+88,20,17,col)+cuff(sx+side*12,sy+86)+`<ellipse cx="${sx+side*4}" cy="${sy+92}" rx="10" ry="8" fill="${sk}"/>`; break;
      case 'cross': s+=limb(sx,sy+6,sx+side*8,sy+52,24,20,col)+limb(sx+side*8,sy+52,-side*14,sy+50,20,18,colD)+`<ellipse cx="${-side*18}" cy="${sy+48}" rx="9" ry="8" fill="${sk}"/>`; break;
      default: s+=limb(sx,sy+6,sx+side*8,sy+52,24,20,col)+limb(sx+side*8,sy+52,sx+side*6,sy+92,20,17,col)+cuff(sx+side*6,sy+90)+handDown(sx+side*6,sy+96);
    }
    return s;};
  let s=`<ellipse cx="0" cy="3" rx="54" ry="7" fill="#3E2E1E" opacity=".18"/>`;
  // arms that go behind the torso are drawn first only for 'cross' (forearm over torso drawn later)
  // ---- legs / skirt
  if(o.male){
    s+=`<path d="M-30 -132 L -28 -8 L -4 -8 L 0 -104 L 4 -8 L 28 -8 L 30 -132Z" fill="${o.bot}"/>`;
    s+=`<path d="M10 -132 L 30 -132 L 28 -8 L 16 -8Z" fill="${o.botD}"/>`;
    s+=`<path d="M-16 -110 L -16 -12 M16 -110 L16 -12" stroke="${o.botD}" stroke-width="1.6" opacity=".7"/>`;
    s+=`<path d="M-30 -8 h24 v-2 c0 -6 -24 -6 -24 0z M6 -8 h24 c0 -6 -24 -8 -24 0z" fill="${dark}"/><path d="M-32 -2 C -32 -10 -4 -10 -4 -2Z M4 -2 C 4 -10 32 -10 32 -2Z" fill="${dark}"/>`;
  } else {
    s+=`<path d="M-12 -14 L -12 -2 M12 -14 L 12 -2" stroke="${skd}" stroke-width="12" stroke-linecap="round"/><path d="M-24 -1 h20 M4 -1 h20" stroke="${C.sandal}" stroke-width="5" stroke-linecap="round"/>`;
    s+=`<path d="M-36 -142 C -42 -100 -48 -56 -52 -14 Q 0 -8 52 -14 C 48 -56 42 -100 36 -142Z" fill="${o.bot}"/>`;
    s+=`<path d="M14 -142 C 22 -100 30 -56 34 -12 Q 44 -13 52 -14 C 48 -56 42 -100 36 -142Z" fill="${o.botD}" opacity=".6"/>`;
    let st='';for(let i=0;i<7;i++){const t=(i+.5)/7;st+=`M${(-34+68*t).toFixed(1)} -138 L${(-50+100*t).toFixed(1)} -14 `}
    s+=`<path d="${st}" stroke="${C.stripe}" stroke-width="2" opacity=".85"/>`;
    s+=`<path d="M-38 -146 H38" stroke="${dark}" stroke-width="9"/>`;
  }
  // ---- torso
  const tw=o.male?46:40, hip=o.male?-132:-142;
  s+=`<path d="M${-tw} ${sy+2} C ${-tw-6} ${sy+40} ${-tw+2} ${hip+30} ${-tw+6} ${hip} L ${tw-6} ${hip} C ${tw-2} ${hip+30} ${tw+6} ${sy+40} ${tw} ${sy+2} C ${tw-12} ${sy-8} 12 ${sy-12} 0 ${sy-12} C -12 ${sy-12} ${-tw+12} ${sy-8} ${-tw} ${sy+2}Z" fill="${o.top}"/>`;
  s+=`<path d="M${tw*.45} ${sy-8} C ${tw-4} ${sy-4} ${tw+6} ${sy+40} ${tw-2} ${hip+30} L ${tw-6} ${hip} L ${tw*.5} ${hip} C ${tw*.62} ${sy+60} ${tw*.6} ${sy+20} ${tw*.45} ${sy-8}Z" fill="${o.topD}"/>`;
  if(o.male){
    // open jacket showing inner shirt + rope belt (reference)
    s+=`<path d="M-10 ${sy-10} L 10 ${sy-10} L 14 ${hip} L -14 ${hip}Z" fill="${o.inner||'#EFD9B0'}"/>`;
    s+=`<path d="M-10 ${sy-10} L -14 ${hip} M10 ${sy-10} L 14 ${hip}" stroke="${o.topD}" stroke-width="3"/>`;
    s+=`<circle cx="0" cy="${sy+14}" r="2.6" fill="${o.topD}"/><circle cx="0" cy="${sy+30}" r="2.6" fill="${o.topD}"/>`;
    s+=`<path d="M-14 ${hip+4} H14" stroke="#A8452A" stroke-width="7"/>`;
    s+=`<path d="M-3 ${hip+4} L -8 ${hip+34} L -1 ${hip+30} Z M3 ${hip+4} L 8 ${hip+36} L 1 ${hip+31}Z" fill="#EFD9B0"/><circle cx="0" cy="${hip+5}" r="4.5" fill="#EFD9B0"/>`;
    s+=`<path d="M${-tw+10} ${hip-30} q 12 10 24 0 v -18 h-24z M${tw-34} ${hip-30} q 12 10 24 0 v -18 h-24z" fill="none" stroke="${o.pocket||'#7FA7C7'}" stroke-width="2"/>`;
    s+=`<path d="M${-tw+6} ${hip} H${tw-6}" stroke="${o.topD}" stroke-width="5"/>`;
  } else {
    s+=`<path d="M0 ${sy-6} V ${hip}" stroke="${o.topD}" stroke-width="2.4"/>`;
    s+=[sy+20,sy+42,sy+64].map(y=>`<circle cx="0" cy="${y}" r="2.8" fill="${C.stripe}"/>`).join('');
    s+=`<path d="M${-tw+4} ${hip+2} H${tw-4}" stroke="${dark}" stroke-width="6"/>`;
    if(o.bag) s+=`<path d="M${tw-8} ${sy} L ${-tw+2} ${hip+10} L ${-tw+14} ${hip+16} L ${tw+2} ${sy+8}Z" fill="#EFD9B0"/><path d="M${tw-4} ${sy+4} L ${-tw+8} ${hip+13}" stroke="#C9573B" stroke-width="1.6"/>`;
  }
  // ---- arms
  s+=arm(-1,o.L||'down')+arm(1,o.R||'down');
  // ---- neck & head
  const hy=-262;
  s+=`<path d="M-9 ${sy-14} L 9 ${sy-14} L 10 ${hy+18} L -10 ${hy+18}Z" fill="${skd}"/>`;
  if(o.male){
    s+=`<ellipse cx="-21" cy="${hy+2}" rx="5" ry="8" fill="${skd}"/><ellipse cx="21" cy="${hy+2}" rx="5" ry="8" fill="${skd}"/>`;
    s+=`<path d="M-20 ${hy-6} C -21 ${hy+18} -12 ${hy+28} 0 ${hy+28} C 12 ${hy+28} 21 ${hy+18} 20 ${hy-6} C 20 ${hy-24} -20 ${hy-24} -20 ${hy-6}Z" fill="${sk}"/>`;
    s+=`<path d="M-21 ${hy-4} C -24 ${hy-26} -8 ${hy-32} 4 ${hy-30} C 18 ${hy-28} 24 ${hy-20} 21 ${hy-4} C 16 ${hy-14} 4 ${hy-18} -6 ${hy-14} C -12 ${hy-12} -16 ${hy-8} -21 ${hy-4}Z" fill="#231C14"/>`;
  } else {
    s+=`<path d="M-30 ${hy} C -34 ${hy-34} -16 ${hy-44} 0 ${hy-44} C 16 ${hy-44} 34 ${hy-34} 30 ${hy} C 28 ${hy+22} 18 ${hy+34} 8 ${hy+40} L 0 ${hy+44} L -8 ${hy+40} C -18 ${hy+34} -28 ${hy+22} -30 ${hy}Z" fill="${o.scarf}"/>`;
    s+=`<path d="M-14 ${hy+34} L -34 ${sy+18} L -8 ${sy+8}Z M14 ${hy+34} L 34 ${sy+20} L 8 ${sy+8}Z" fill="${o.scarf}"/><path d="M-6 ${hy+36} L -12 ${sy+30} L 0 ${sy+20} L 12 ${sy+30} L 6 ${hy+36}Z" fill="${o.scarfD||o.scarf}"/>`;
    s+=`<path d="M-19 ${hy-4} C -20 ${hy+18} -10 ${hy+28} 0 ${hy+28} C 10 ${hy+28} 20 ${hy+18} 19 ${hy-4} C 18 ${hy-20} -18 ${hy-20} -19 ${hy-4}Z" fill="${sk}"/>`;
    s+=`<path d="M-21 ${hy-2} C -18 ${hy-24} 18 ${hy-24} 21 ${hy-2} C 12 ${hy-12} -12 ${hy-12} -21 ${hy-2}Z" fill="${o.scarf}"/>`;
  }
  s+=`<g fill="#DE7663" opacity=".6"><circle cx="-11" cy="${hy+10}" r="4.6"/><circle cx="11" cy="${hy+10}" r="4.6"/></g>`;
  s+=`<path d="M-13 ${hy-5} q4 -3 8 0 M5 ${hy-5} q4 -3 8 0" stroke="#231C14" stroke-width="2" fill="none" stroke-linecap="round"/>`;
  s+=`<g fill="#231C14"><circle cx="-8" cy="${hy+2}" r="2.1"/><circle cx="8" cy="${hy+2}" r="2.1"/></g>`;
  s+=`<path d="M-1 ${hy+2} C -4 ${hy+10} -4 ${hy+13} 1 ${hy+14}" stroke="${skd}" stroke-width="2" fill="none" stroke-linecap="round"/>`;
  if(o.stache) s+=`<path d="M-11 ${hy+19} C -6 ${hy+14} -1 ${hy+15} 0 ${hy+17} C 1 ${hy+15} 6 ${hy+14} 11 ${hy+19} C 6 ${hy+21} -6 ${hy+21} -11 ${hy+19}Z" fill="#2A1D16"/>`;
  else s+=`<path d="M-5 ${hy+19} Q 0 ${hy+22} 5 ${hy+19}" stroke="#7A3A26" stroke-width="2" fill="none" stroke-linecap="round"/>`;
  if(o.mood==='angry') s+=`<path d="M-13 ${hy-8} l9 4 M13 ${hy-8} l-9 4" stroke="#231C14" stroke-width="2.4" stroke-linecap="round"/>`;
  // ---- hats
  const hb=o.male?hy-18:hy-22;
  if(o.hat==='cone'){
    s+=`<path d="M-66 ${hb} C -40 ${hb+10} 40 ${hb+10} 66 ${hb} C 40 ${hb+6} -40 ${hb+6} -66 ${hb}Z" fill="${C.hatD}"/>`;
    s+=`<path d="M-68 ${hb-2} L 0 ${hb-44} L 68 ${hb-2} C 40 ${hb+6} -40 ${hb+6} -68 ${hb-2}Z" fill="${C.hat}"/>`;
    let hl='';for(let i=1;i<16;i++){const t=i/16;hl+=`M0 ${hb-44} L${(-68+136*t).toFixed(1)} ${(hb-2+Math.sin(t*Math.PI)*5).toFixed(1)} `}
    s+=`<path d="${hl}" stroke="${C.hatLine}" stroke-width="1.3" opacity=".85"/>`;
    s+=`<path d="M-68 ${hb-2} C -40 ${hb+6} 40 ${hb+6} 68 ${hb-2}" stroke="${C.hatLine}" stroke-width="2.6" fill="none"/>`;
    s+=`<path d="M0 ${hb-44} L 68 ${hb-2} C 50 ${hb+2} 34 ${hb+4} 20 ${hb+4}Z" fill="${C.hatD}" opacity=".35"/>`;
  } else if(o.hat==='cap'){
    const cc=o.capC||'#3F5F43', cd=o.capD||'#2F4A33';
    s+=`<path d="M-23 ${hb+8} C -24 ${hb-18} -12 ${hb-26} 0 ${hb-26} C 12 ${hb-26} 24 ${hb-18} 23 ${hb+8}Z" fill="${cc}"/>`;
    s+=`<path d="M0 ${hb-26} C -4 ${hb-12} -4 ${hb} -2 ${hb+8} M0 ${hb-26} C 10 ${hb-14} 14 ${hb} 14 ${hb+8}" stroke="${cd}" stroke-width="1.6" fill="none"/>`;
    s+=`<path d="M-24 ${hb+6} C -12 ${hb+2} 12 ${hb+2} 24 ${hb+6} L 26 ${hb+12} C 12 ${hb+18} -12 ${hb+18} -26 ${hb+12}Z" fill="${cd}"/>`;
    s+=`<circle cx="0" cy="${hb-26}" r="2.6" fill="${cd}"/>`;
  }
  return s;
};

/* ================= TIMORESE FARMER KIT =================
   tais patterns (warp stripes + ikat diamond bands, Lautém-style bands of plain weave and ikat) */
FIG.taisDefs = function(){
  const tp=(id,base,dark,accent,light)=>`<pattern id="${id}" width="44" height="14" patternUnits="userSpaceOnUse">
    <rect width="44" height="14" fill="${base}"/>
    <rect x="0" width="4" height="14" fill="${dark}"/><rect x="6" width="1.6" height="14" fill="${accent}"/><rect x="9" width="1.2" height="14" fill="${light}"/>
    <rect x="16" width="12" height="14" fill="${dark}"/><path d="M22 1 L26 7 L22 13 L18 7Z" fill="${accent}"/><path d="M22 4 L24 7 L22 10 L20 7Z" fill="${dark}"/>
    <rect x="31" width="1.2" height="14" fill="${light}"/><rect x="34" width="1.6" height="14" fill="${accent}"/><rect x="38" width="3" height="14" fill="${dark}"/></pattern>`;
  return `<svg width="0" height="0" style="position:absolute"><defs>
    ${tp('taisR','#9A3326','#241A16','#E4B64C','#F1E3C6')}
    ${tp('taisB','#2A2320','#8E2F24','#E4B64C','#F1E3C6')}
    ${tp('taisI','#2F4466','#1D2838','#C9573B','#F1E3C6')}
    ${tp('taisRL','#9A3326','#241A16','#E4B64C','#F1E3C6').replace('id="taisRL"','id="taisRL" patternTransform="scale(1.6)"')}
    ${tp('taisBL','#2A2320','#8E2F24','#E4B64C','#F1E3C6').replace('id="taisBL"','id="taisBL" patternTransform="scale(1.3)"')}
    <pattern id="straw" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#DDB872"/><path d="M0 4 H8 M4 0 V8" stroke="#C99E55" stroke-width="1.2"/></pattern>
  </defs></svg>`;
};
/* straw sun hat — front view, brim centre at (0,b) */
FIG.strawFront = function(b, k=1){
  return `<g transform="translate(0 ${b}) scale(${k})">
    <ellipse cx="0" cy="3" rx="66" ry="11" fill="#B98C48"/>
    <ellipse cx="0" cy="0" rx="66" ry="10" fill="url(#straw)"/>
    <path d="M-66 0 C -40 9 40 9 66 0" stroke="#A67A3A" stroke-width="2.4" fill="none"/>
    <path d="M-28 0 C -30 -30 -16 -36 0 -36 C 16 -36 30 -30 28 0Z" fill="url(#straw)"/>
    <path d="M-28 0 C -30 -30 -16 -36 0 -36 C 16 -36 30 -30 28 0" stroke="#B98C48" stroke-width="2" fill="none"/>
    <path d="M10 -35 C 24 -30 28 -16 28 0 L 16 0 C 18 -14 16 -26 10 -35Z" fill="#B98C48" opacity=".45"/>
    <path d="M-28.5 -8 C -12 -4 12 -4 28.5 -8 L 28 0 C 12 4 -12 4 -28 0Z" fill="#6B3A22"/>
  </g>`;
};
FIG.strawSide = function(x,b){
  return `<g transform="translate(${x} ${b})"><path d="M-50 2 C -30 -4 30 -4 52 2 C 30 6 -30 6 -50 2Z" fill="url(#straw)"/><path d="M-50 2 C -30 6 30 6 52 2" stroke="#A67A3A" stroke-width="2" fill="none"/>
    <path d="M-22 1 C -22 -24 20 -26 22 1Z" fill="url(#straw)"/><path d="M-22 1 C -22 -24 20 -26 22 1" stroke="#B98C48" stroke-width="1.6" fill="none"/><path d="M-22 -6 C -8 -3 8 -3 22 -6 L 22 1 C 8 4 -8 4 -22 1Z" fill="#6B3A22"/></g>`;
};

/* frontal farmer. o={male, shirt, shirtD, sleeve:'short'|'rolled', collar, bottom:'shorts'|'trousers'|'tais', botC, botD, tais, hat:'straw'|'cloth'|'cap'|null, clothC, capC, capD,
   L,R:'down'|'fist'|'point'|'hold'|'hip'|'cross'|'hoe', stache, mood, machete, selendang, bag, skin, skinD} */
FIG.farmer = function(o){
  const sk=o.skin||'#B8744C', skd=o.skinD||'#96593A', dark='#1E2B33', hairC='#1C1614';
  const limb=(a,b,w0,w1,col)=>{const [x0,y0]=a,[x1,y1]=b;const t=Math.atan2(y1-y0,x1-x0)+Math.PI/2,c=Math.cos(t),s=Math.sin(t);
    return `<path d="M${(x0+c*w0/2).toFixed(1)} ${(y0+s*w0/2).toFixed(1)} L${(x1+c*w1/2).toFixed(1)} ${(y1+s*w1/2).toFixed(1)} L${(x1-c*w1/2).toFixed(1)} ${(y1-s*w1/2).toFixed(1)} L${(x0-c*w0/2).toFixed(1)} ${(y0-s*w0/2).toFixed(1)}Z" fill="${col}"/><circle cx="${x1}" cy="${y1}" r="${w1/2}" fill="${col}"/>`;};
  const lerpP=(a,b,t)=>[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t];
  const fist=(x,y,r=9)=>`<circle cx="${x}" cy="${y}" r="${r}" fill="${sk}"/><path d="M${x-r*.6} ${y-r*.2} h${r*1.2} M${x-r*.6} ${y+r*.25} h${r*1.2}" stroke="${skd}" stroke-width="1.6" stroke-linecap="round"/>`;
  const sy=-222, sw=o.male?44:38;
  let back='', s='';
  s+=`<ellipse cx="0" cy="3" rx="54" ry="7" fill="#3E2E1E" opacity=".18"/>`;
  // ---- legs & lower garment
  const sandal=(x)=>`<path d="M${x-13} -2 h26" stroke="#4A3222" stroke-width="5" stroke-linecap="round"/>`;
  if(o.male){
    const hemY = o.bottom==='shorts'?-66:o.bottom==='tais'?-62:-40;
    s+=`<path d="M-15 ${hemY} L -15 -8 M15 ${hemY} L 15 -8" stroke="${sk}" stroke-width="18" stroke-linecap="round"/>`;
    s+=`<path d="M-15 ${hemY+20} L -15 -8" stroke="${skd}" stroke-width="5" opacity=".35" transform="translate(6 0)"/>`;
    s+=sandal(-16)+sandal(16);
    if(o.bottom==='tais'){
      s+=`<path d="M-34 -134 L 34 -134 L 38 -60 C 20 -56 -20 -56 -38 -60Z" fill="url(#${o.tais||'taisR'})"/>`;
      s+=`<path d="M-38 -60 C -20 -56 20 -56 38 -60" stroke="#241A16" stroke-width="3" fill="none"/>`;
      let fr='';for(let i=0;i<14;i++){const x=-36+i*5.5;fr+=`M${x.toFixed(1)} ${-58+Math.abs(x)*.02} v7 `}s+=`<path d="${fr}" stroke="#E4B64C" stroke-width="1.6"/>`;
      s+=`<path d="M8 -134 L 2 -60" stroke="#241A16" stroke-width="2" opacity=".6"/>`;
    } else {
      s+=`<path d="M-30 -134 L -30 ${hemY} L -3 ${hemY} L 0 -104 L 3 ${hemY} L 30 ${hemY} L 30 -134Z" fill="${o.botC}"/>`;
      s+=`<path d="M10 -134 L 30 -134 L 30 ${hemY} L 16 ${hemY}Z" fill="${o.botD}"/>`;
      s+=`<path d="M-31 ${hemY-7} h29 M2 ${hemY-7} h29" stroke="${o.botD}" stroke-width="7"/>`;
    }
  } else {
    s+=`<path d="M-12 -18 L -12 -6 M12 -18 L 12 -6" stroke="${sk}" stroke-width="13" stroke-linecap="round"/>`+sandal(-13)+sandal(13);
    s+=`<path d="M-36 -144 C -40 -100 -44 -56 -46 -16 Q 0 -10 46 -16 C 44 -56 40 -100 36 -144Z" fill="url(#${o.tais||'taisR'})"/>`;
    s+=`<path d="M14 -144 C 22 -100 30 -56 32 -14 Q 40 -15 46 -16 C 44 -56 40 -100 36 -144Z" fill="#000" opacity=".18"/>`;
    s+=`<path d="M-46 -18 Q 0 -12 46 -18" stroke="#241A16" stroke-width="4" fill="none"/>`;
    s+=`<path d="M-37 -140 C -10 -134 10 -134 37 -140 L 37 -150 C 10 -144 -10 -144 -37 -150Z" fill="#241A16" opacity=".85"/>`;
  }
  // ---- torso
  const tw=sw, hip=o.male?-134:-146;
  s+=`<path d="M${-tw} ${sy+2} C ${-tw-4} ${sy+40} ${-tw+4} ${hip+30} ${-tw+6} ${hip+4} L ${tw-6} ${hip+4} C ${tw-4} ${hip+30} ${tw+4} ${sy+40} ${tw} ${sy+2} C ${tw-12} ${sy-8} 12 ${sy-12} 0 ${sy-12} C -12 ${sy-12} ${-tw+12} ${sy-8} ${-tw} ${sy+2}Z" fill="${o.shirt}"/>`;
  s+=`<path d="M${tw*.4} ${sy-8} C ${tw-4} ${sy-4} ${tw+4} ${sy+40} ${tw-4} ${hip+30} L ${tw-6} ${hip+4} L ${tw*.45} ${hip+4} C ${tw*.6} ${sy+60} ${tw*.58} ${sy+20} ${tw*.4} ${sy-8}Z" fill="${o.shirtD}"/>`;
  // neckline + details
  if(o.collar){
    s+=`<path d="M-12 ${sy-11} L 0 ${sy+10} L 12 ${sy-11}Z" fill="${skd}"/>`;
    s+=`<path d="M-16 ${sy-10} L -2 ${sy+12} L -18 ${sy+6}Z M16 ${sy-10} L 2 ${sy+12} L 18 ${sy+6}Z" fill="${o.shirtD}"/>`;
    s+=`<path d="M0 ${sy+12} V ${hip+2}" stroke="${o.shirtD}" stroke-width="2"/>`;
    s+=[sy+30,sy+54,sy+78].map(y=>`<circle cx="0" cy="${y}" r="2.3" fill="${o.shirtD}"/>`).join('');
    s+=`<path d="M${-tw+12} ${sy+22} h20 v18 q-10 5 -20 0z" fill="none" stroke="${o.shirtD}" stroke-width="2"/>`;
  } else {
    s+=`<path d="M-11 ${sy-11} C -8 ${sy+2} 8 ${sy+2} 11 ${sy-11}Z" fill="${skd}"/>`;
    s+=`<path d="M-12 ${sy-11} C -8 ${sy+4} 8 ${sy+4} 12 ${sy-11}" stroke="${o.shirtD}" stroke-width="3" fill="none"/>`;
  }
  if(o.male){
    s+=`<path d="M${-tw+6} ${hip+4} H${tw-6}" stroke="${o.shirtD}" stroke-width="4"/>`;
    if(o.machete){ // katana (bush knife) in a wooden sheath at the right hip
      s+=`<path d="M${tw-6} ${hip+2} L ${tw+4} ${hip+2} L ${tw+10} ${hip+84} C ${tw+8} ${hip+92} ${tw-2} ${hip+92} ${tw-2} ${hip+84}Z" fill="#7A5A3A"/>`;
      s+=`<path d="M${tw-4} ${hip+20} h14 M${tw-3} ${hip+50} h14" stroke="#4A3222" stroke-width="3"/>`;
      s+=`<rect x="${tw-6}" y="${hip-24}" width="10" height="26" rx="4" fill="#3A2A1C"/>`;
    }
  }
  if(o.selendang){ // narrow tais over one shoulder
    s+=`<path d="M${-tw+10} ${sy-8} L ${-tw+30} ${sy-12} L ${tw-10} ${hip+20} L ${tw-30} ${hip+26}Z" fill="url(#${o.selendang})"/>`;
  }
  if(o.bag){ // woven betel/produce bag (kohe) on a strap
    s+=`<path d="M${tw-14} ${sy-6} L ${-tw-4} ${hip-6}" stroke="#7A5A3A" stroke-width="4"/>`;
    s+=`<path d="M${-tw-22} ${hip-24} L ${-tw+14} ${hip-24} L ${-tw+10} ${hip+14} L ${-tw-18} ${hip+14}Z" fill="#C9A06A"/><path d="M${-tw-20} ${hip-12} H${-tw+12} M${-tw-19} ${hip} H${-tw+11}" stroke="#A67E4B" stroke-width="2"/><path d="M${-tw-8} ${hip-24} V${hip+14} M${-tw+2} ${hip-24} V${hip+14}" stroke="#A67E4B" stroke-width="1.4"/>`;
  }
  // ---- arms
  const arm=(side,pose)=>{
    const S=[side*sw, sy+6]; let E,W,end='';
    switch(pose){
      case 'fist': E=[S[0]+side*26,sy-40]; W=[S[0]+side*20,sy-88]; end=fist(W[0],W[1]-10,10); break;
      case 'point': E=[S[0]+side*46,sy+10]; W=[S[0]+side*90,sy+2]; end=`<circle cx="${W[0]+side*8}" cy="${W[1]}" r="8" fill="${sk}"/><path d="M${W[0]+side*12} ${W[1]-2} h${side*16}" stroke="${sk}" stroke-width="5" stroke-linecap="round"/>`; break;
      case 'hold': E=[S[0]+side*24,sy-26]; W=[S[0]+side*20,sy-62]; end=fist(W[0],W[1]-10,9); break;
      case 'hip': E=[S[0]+side*30,sy+52]; W=[S[0]+side*8,sy+86]; end=`<ellipse cx="${W[0]}" cy="${W[1]+4}" rx="10" ry="8" fill="${sk}"/>`; break;
      case 'cross': E=[S[0]+side*8,sy+50]; W=[-side*16,sy+48]; end=`<ellipse cx="${W[0]-side*2}" cy="${W[1]}" rx="9" ry="8" fill="${sk}"/>`; break;
      case 'hoe': E=[S[0]+side*18,sy+44]; W=[S[0]-side*6,sy+2]; end=fist(W[0],W[1],9); break;
      default: E=[S[0]+side*8,sy+50]; W=[S[0]+side*6,sy+88]; end=`<path d="M${W[0]-8} ${W[1]} C ${W[0]-9} ${W[1]+12} ${W[0]-5} ${W[1]+20} ${W[0]} ${W[1]+20} C ${W[0]+5} ${W[1]+20} ${W[0]+9} ${W[1]+12} ${W[0]+8} ${W[1]}Z" fill="${sk}"/><path d="M${W[0]-3} ${W[1]+10} v7 M${W[0]+2} ${W[1]+10} v8" stroke="${skd}" stroke-width="1.4" stroke-linecap="round"/>`;
    }
    let a='';
    if(o.sleeve==='rolled'){ a+=limb(S,E,24,20,o.shirt)+`<circle cx="${E[0]}" cy="${E[1]}" r="11" fill="${o.shirtD}"/>`+limb(E,W,17,15,sk); }
    else { const M=lerpP(S,E,.5); a+=limb(S,M,25,22,o.shirt)+`<path d="M${M[0]-11} ${M[1]} h22" stroke="${o.shirtD}" stroke-width="3" transform="rotate(0)"/>`+limb(M,E,17,16,sk)+limb(E,W,16,14,sk); }
    if(pose==='hoe'){ // tool over the shoulder: handle from hand back over shoulder, blade behind the head
      back+=`<path d="M${W[0]} ${W[1]} L ${-side*70} ${sy-120}" stroke="#8A6238" stroke-width="7" stroke-linecap="round"/><path d="M${-side*70} ${sy-120} l${-side*8} 26 l${side*22} 6 l${side*2} -22Z" fill="#6E747A"/>`;
    }
    return a+end;};
  s+=arm(-1,o.L||'down')+arm(1,o.R||'down');
  // ---- head
  const hy=-262;
  s+=`<path d="M-9 ${sy-14} L 9 ${sy-14} L 10 ${hy+18} L -10 ${hy+18}Z" fill="${skd}"/>`;
  s+=`<ellipse cx="-20" cy="${hy+2}" rx="5" ry="8" fill="${skd}"/><ellipse cx="20" cy="${hy+2}" rx="5" ry="8" fill="${skd}"/>`;
  if(!o.male) s+=`<ellipse cx="${o.bunSide||14}" cy="${hy-22}" rx="13" ry="11" fill="${hairC}"/>`;
  s+=`<path d="M-20 ${hy-6} C -21 ${hy+18} -12 ${hy+28} 0 ${hy+28} C 12 ${hy+28} 21 ${hy+18} 20 ${hy-6} C 20 ${hy-24} -20 ${hy-24} -20 ${hy-6}Z" fill="${sk}"/>`;
  if(o.male) s+=`<path d="M-21 ${hy-4} C -24 ${hy-26} -8 ${hy-32} 4 ${hy-30} C 18 ${hy-28} 24 ${hy-20} 21 ${hy-4} C 16 ${hy-14} 4 ${hy-18} -6 ${hy-14} C -12 ${hy-12} -16 ${hy-8} -21 ${hy-4}Z" fill="${hairC}"/>`;
  else s+=`<path d="M-22 ${hy+6} C -26 ${hy-26} -8 ${hy-32} 2 ${hy-30} C 18 ${hy-30} 26 ${hy-20} 22 ${hy+6} C 20 ${hy-8} 12 ${hy-16} 0 ${hy-16} C -12 ${hy-16} -20 ${hy-8} -22 ${hy+6}Z" fill="${hairC}"/>`;
  s+=`<g fill="#D66E5B" opacity=".55"><circle cx="-11" cy="${hy+10}" r="4.4"/><circle cx="11" cy="${hy+10}" r="4.4"/></g>`;
  s+=`<path d="M-13 ${hy-4} q4 -3 8 0 M5 ${hy-4} q4 -3 8 0" stroke="${hairC}" stroke-width="2" fill="none" stroke-linecap="round"/>`;
  s+=`<g fill="${hairC}"><circle cx="-8" cy="${hy+3}" r="2.1"/><circle cx="8" cy="${hy+3}" r="2.1"/></g>`;
  s+=`<path d="M-1 ${hy+3} C -4 ${hy+10} -4 ${hy+13} 1 ${hy+14}" stroke="${skd}" stroke-width="2" fill="none" stroke-linecap="round"/>`;
  if(o.stache) s+=`<path d="M-11 ${hy+19} C -6 ${hy+14} -1 ${hy+15} 0 ${hy+17} C 1 ${hy+15} 6 ${hy+14} 11 ${hy+19} C 6 ${hy+21} -6 ${hy+21} -11 ${hy+19}Z" fill="#241A14"/>`;
  else if(o.mood==='angry') s+=`<path d="M-5 ${hy+21} Q 0 ${hy+17} 5 ${hy+21}" stroke="#6B3A22" stroke-width="2" fill="none" stroke-linecap="round"/>`;
  else s+=`<path d="M-5 ${hy+19} Q 0 ${hy+22} 5 ${hy+19}" stroke="#6B3A22" stroke-width="2" fill="none" stroke-linecap="round"/>`;
  if(o.mood==='angry') s+=`<path d="M-13 ${hy-7} l9 4 M13 ${hy-7} l-9 4" stroke="${hairC}" stroke-width="2.4" stroke-linecap="round"/>`;
  // ---- headwear
  if(o.hat==='straw') s+=FIG.strawFront(hy-16, o.male?1:.95);
  else if(o.hat==='cloth') s+=`<path d="M-22 ${hy-10} C -22 ${hy-30} 22 ${hy-30} 22 ${hy-10} C 12 ${hy-16} -12 ${hy-16} -22 ${hy-10}Z" fill="${o.clothC||'#9A3326'}"/><path d="M-22 ${hy-10} C -12 ${hy-16} 12 ${hy-16} 22 ${hy-10}" stroke="#241A16" stroke-width="2" fill="none" opacity=".5"/><path d="M18 ${hy-20} l14 -6 l-4 12Z" fill="${o.clothC||'#9A3326'}"/>`;
  else if(o.hat==='cap'){const cc=o.capC||'#3F5F43',cd=o.capD||'#2F4A33',hb=hy-18;
    s+=`<path d="M-23 ${hb+8} C -24 ${hb-18} -12 ${hb-26} 0 ${hb-26} C 12 ${hb-26} 24 ${hb-18} 23 ${hb+8}Z" fill="${cc}"/><path d="M0 ${hb-26} C -4 ${hb-12} -4 ${hb} -2 ${hb+8} M0 ${hb-26} C 10 ${hb-14} 14 ${hb} 14 ${hb+8}" stroke="${cd}" stroke-width="1.6" fill="none"/><path d="M-24 ${hb+6} C -12 ${hb+2} 12 ${hb+2} 24 ${hb+6} L 26 ${hb+12} C 12 ${hb+18} -12 ${hb+18} -26 ${hb+12}Z" fill="${cd}"/>`;}
  return back+s;
};

/* ================= FOLK FIGURE v2 — stocky reference proportions (~5.8 heads), layered garments =================
   feet (0,0), head top ≈ -385. o={male, jk, jkD, jkL, inner, cuff, bot, botD, botL, tais, sash, sel, head:'bare'|'cloth'|'cap', clothC, capC, capD,
   L,R: 'down'|'fist'|'point'|'hold'|'hip'|'cross'|'hoe', stache, mood, machete, bag, skin, skinD} */
FIG.folk = function(o){
  const sk=o.skin||'#B8744C', skd=o.skinD||'#95583A', dk='#1E2B33', hair='#1C1614';
  const lighten=o.jkL||'rgba(255,255,255,.22)';
  const seg=(a,b,w0,w1,col)=>{const [x0,y0]=a,[x1,y1]=b;const t=Math.atan2(y1-y0,x1-x0)+Math.PI/2,c=Math.cos(t),s=Math.sin(t);
    return `<path d="M${(x0+c*w0/2).toFixed(1)} ${(y0+s*w0/2).toFixed(1)} L${(x1+c*w1/2).toFixed(1)} ${(y1+s*w1/2).toFixed(1)} L${(x1-c*w1/2).toFixed(1)} ${(y1-s*w1/2).toFixed(1)} L${(x0-c*w0/2).toFixed(1)} ${(y0-s*w0/2).toFixed(1)}Z" fill="${col}"/><circle cx="${x0}" cy="${y0}" r="${w0/2}" fill="${col}"/><circle cx="${x1}" cy="${y1}" r="${w1/2}" fill="${col}"/>`;};
  const hand=(x,y,ang=0,kind='open')=>{ // ang: direction fingers point (deg, 90 = down)
    if(kind==='fist') return `<g transform="translate(${x} ${y}) rotate(${ang})"><path d="M-13 -4 C -14 -14 -6 -16 0 -15 C 8 -16 14 -12 13 -2 C 14 8 8 14 0 14 C -8 14 -13 8 -13 -4Z" fill="${sk}"/><path d="M-6 -14 C -7 -10 -7 -7 -6 -4 M1 -15 C 0 -11 0 -8 1 -4 M7 -13 C 6 -9 6 -7 7 -3" stroke="${skd}" stroke-width="1.8" fill="none" stroke-linecap="round"/><path d="M-13 0 C -6 2 -2 6 -3 10" stroke="${skd}" stroke-width="1.8" fill="none"/></g>`;
    return `<g transform="translate(${x} ${y}) rotate(${ang-90})"><path d="M-12 -8 C -14 8 -10 22 -2 24 C 6 25 12 18 12 4 L 12 -8Z" fill="${sk}"/><path d="M-5 6 v14 M1 7 v15 M7 6 v12" stroke="${skd}" stroke-width="1.8" stroke-linecap="round"/><path d="M12 -2 C 18 2 18 10 12 12" fill="${sk}" stroke="${skd}" stroke-width="1.4"/></g>`;
  };
  let back='', s=`<ellipse cx="0" cy="4" rx="74" ry="9" fill="#3E2E1E" opacity=".18"/>`;
  // ---------- legs ----------
  // one foot drawn toes-right, mirrored for the left foot (f=-1) so heel and toes both flip
  const foot=(x,f)=>`<g transform="translate(${x} 0) scale(${f} 1)"><path d="M-15 -2 C -16 -12 -8 -16 0 -16 C 10 -16 20 -10 18 -2Z" fill="${sk}"/><path d="M-15 -4 H18" stroke="#4A3222" stroke-width="5" stroke-linecap="round"/><path d="M-4 -15 l4 11" stroke="#4A3222" stroke-width="3"/></g>`;
  if(o.male){
    s+=`<path d="M-26 -40 L -26 -14 M26 -40 L 26 -14" stroke="${sk}" stroke-width="20" stroke-linecap="round"/>`+foot(-26,-1)+foot(26,1);
    // wide trousers rolled at the shin
    s+=`<path d="M-54 -176 C -58 -120 -54 -80 -48 -40 L -6 -40 L -2 -140 L 2 -140 L 6 -40 L 48 -40 C 54 -80 58 -120 54 -176Z" fill="${o.bot}"/>`;
    s+=`<path d="M24 -176 L 54 -176 C 58 -120 54 -80 48 -40 L 28 -40 C 36 -90 34 -140 24 -176Z" fill="${o.botD}"/>`;
    s+=`<path d="M-50 -54 L -4 -54 L -6 -36 L -48 -36Z M4 -54 L 50 -54 L 48 -36 L 6 -36Z" fill="${o.botL||o.botD}"/>`;
    s+=`<path d="M-50 -54 H-4 M4 -54 H50" stroke="${o.botD}" stroke-width="2"/>`;
    s+=`<path d="M-30 -118 q 6 8 14 6 M-36 -92 q 8 6 16 4 M28 -112 q -6 8 -14 6" stroke="${lighten}" stroke-width="2.4" fill="none" stroke-linecap="round"/>`;
  } else {
    s+=`<path d="M-20 -26 L -20 -12 M20 -26 L 20 -12" stroke="${sk}" stroke-width="18" stroke-linecap="round"/>`+foot(-20,-1)+foot(20,1);
    s+=`<path d="M-52 -196 C -58 -140 -64 -80 -68 -24 Q 0 -14 68 -24 C 64 -80 58 -140 52 -196Z" fill="url(#${o.tais||'taisR'})"/>`;
    s+=`<path d="M22 -196 C 34 -140 44 -80 48 -20 Q 60 -22 68 -24 C 64 -80 58 -140 52 -196Z" fill="#000" opacity=".2"/>`;
    s+=`<path d="M-68 -24 Q 0 -14 68 -24" stroke="#241A16" stroke-width="5" fill="none"/>`;
    s+=`<path d="M-14 -190 C -18 -130 -22 -80 -24 -22" stroke="#000" stroke-width="2" opacity=".25" fill="none"/>`;
  }
  // ---------- torso ----------
  const hem=o.male?-150:-176;
  if(o.male){
    // inner shirt
    s+=`<path d="M-34 -306 L 34 -306 L 40 ${hem+6} L -40 ${hem+6}Z" fill="${o.inner}"/>`;
    // tais sash knotted at the waist
    s+=`<path d="M-44 -178 C -20 -172 20 -172 44 -178 L 44 -164 C 20 -158 -20 -158 -44 -164Z" fill="url(#${o.sash||'taisR'})"/>`;
    s+=`<path d="M-8 -170 L -18 -118 L -6 -122 L -2 -168Z M6 -170 L 16 -112 L 4 -118 L 2 -168Z" fill="url(#${o.sash||'taisR'})"/><circle cx="0" cy="-170" r="8" fill="#241A16"/>`;
    // open jacket, two panels with dark hem lining
    const panel=(f)=>`<path d="M${f*30} -312 C ${f*50} -312 ${f*64} -306 ${f*68} -294 C ${f*74} -250 ${f*76} -200 ${f*72} ${hem} C ${f*60} ${hem+6} ${f*40} ${hem+6} ${f*26} ${hem+2} C ${f*24} -220 ${f*26} -270 ${f*30} -312Z" fill="${o.jk}"/>`;
    s+=`<path d="M-72 ${hem-2} C -60 ${hem+10} -40 ${hem+10} -26 ${hem+6} L -26 ${hem-6} C -40 ${hem-2} -60 ${hem-2} -72 ${hem-10}Z M72 ${hem-2} C 60 ${hem+10} 40 ${hem+10} 26 ${hem+6} L 26 ${hem-6} C 40 ${hem-2} 60 ${hem-2} 72 ${hem-10}Z" fill="${dk}"/>`;
    s+=panel(-1)+panel(1);
    s+=`<path d="M44 -310 C 64 -300 76 -250 72 ${hem} C 64 ${hem+4} 56 ${hem+5} 50 ${hem+5} C 56 -220 54 -270 44 -310Z" fill="${o.jkD}"/>`;
    s+=`<path d="M-30 -312 C -26 -270 -24 -220 -26 ${hem+2} M30 -312 C 26 -270 24 -220 26 ${hem+2}" stroke="${o.jkD}" stroke-width="3" fill="none"/>`;
    // collar
    s+=`<path d="M-30 -312 L -12 -292 L -36 -300Z M30 -312 L 12 -292 L 36 -300Z" fill="${o.jkD}"/>`;
    // pockets with light stitch
    s+=`<path d="M-62 -206 L -36 -206 L -36 -186 C -44 -178 -56 -178 -62 -186Z M36 -206 L 62 -206 L 62 -186 C 56 -178 44 -178 36 -186Z" fill="none" stroke="${o.stitch||'rgba(255,255,255,.45)'}" stroke-width="2" stroke-dasharray="4 3"/>`;
    s+=[-282,-252].map(y=>`<circle cx="-22" cy="${y}" r="3" fill="${o.jkD}"/>`).join('');
    // fold lines
    s+=`<path d="M-58 -270 q 8 10 4 24 M58 -262 q -8 10 -4 22" stroke="${lighten}" stroke-width="2.4" fill="none" stroke-linecap="round"/>`;
    if(o.machete){ s+=`<path d="M64 -172 L 76 -172 L 90 -74 C 88 -64 76 -64 74 -74Z" fill="#7A5A3A"/><path d="M68 -150 h14 M72 -110 h14" stroke="#4A3222" stroke-width="3"/><rect x="62" y="-198" width="12" height="28" rx="5" fill="#3A2A1C"/>`; }
  } else {
    // blouse (kebaya-like) with flared peplum and dark hem band
    s+=`<path d="M-58 -300 C -66 -260 -66 -220 -62 ${hem+8} C -30 ${hem+18} 30 ${hem+18} 62 ${hem+8} C 66 -220 66 -260 58 -300 C 40 -312 20 -314 0 -314 C -20 -314 -40 -312 -58 -300Z" fill="${o.jk}"/>`;
    s+=`<path d="M30 -310 C 56 -300 66 -250 62 ${hem+8} C 54 ${hem+12} 46 ${hem+14} 40 ${hem+14} C 46 -220 44 -270 30 -310Z" fill="${o.jkD}"/>`;
    s+=`<path d="M-62 ${hem+2} C -30 ${hem+12} 30 ${hem+12} 62 ${hem+2} L 63 ${hem+12} C 30 ${hem+22} -30 ${hem+22} -63 ${hem+12}Z" fill="${dk}"/>`;
    s+=`<path d="M0 -300 V ${hem+10}" stroke="${o.jkD}" stroke-width="2.4"/>`+[-282,-256,-230,-204].map(y=>`<circle cx="0" cy="${y}" r="3" fill="${o.inner||'#F1E3C6'}"/>`).join('');
    s+=`<path d="M-14 -314 C -10 -300 10 -300 14 -314" fill="${skd}"/>`;
    s+=`<path d="M-44 -250 q 10 8 6 22 M44 -244 q -8 10 -4 22" stroke="${lighten}" stroke-width="2.4" fill="none" stroke-linecap="round"/>`;
    if(o.sel){ // selendang: tais scarf around the neck, ends down the front
      s+=`<path d="M-30 -314 C -40 -300 -40 -260 -38 -196 L -20 -196 C -22 -250 -18 -290 -8 -308Z M30 -314 C 40 -300 40 -260 38 -196 L 20 -196 C 22 -250 18 -290 8 -308Z" fill="url(#${o.sel})"/>`;
      s+=`<path d="M-38 -196 h18 M20 -196 h18" stroke="#E4B64C" stroke-width="3" stroke-dasharray="2 2"/>`;
    }
  }
  if(o.bag){ s+=`<path d="M50 -306 L -70 -196" stroke="#7A5A3A" stroke-width="5"/><path d="M-94 -214 L -46 -214 L -52 -150 L -88 -150Z" fill="#C9A06A"/><path d="M-93 -196 H-47 M-91 -178 H-49 M-89 -162 H-51" stroke="#A67E4B" stroke-width="2.4"/><path d="M-78 -214 V-150 M-62 -214 V-150" stroke="#A67E4B" stroke-width="1.6"/>`; }
  // ---------- arms: one continuous bending tube per garment layer ----------
  const tube=(P,Wd,col,cap=.7)=>{const n=P.length;const nr=[];
    for(let i=0;i<n;i++){let dx,dy;if(i===0){dx=P[1][0]-P[0][0];dy=P[1][1]-P[0][1]}else if(i===n-1){dx=P[i][0]-P[i-1][0];dy=P[i][1]-P[i-1][1]}else{const a1=Math.atan2(P[i][1]-P[i-1][1],P[i][0]-P[i-1][0]),a2=Math.atan2(P[i+1][1]-P[i][1],P[i+1][0]-P[i][0]);dx=Math.cos(a1)+Math.cos(a2);dy=Math.sin(a1)+Math.sin(a2)}
      const L=Math.hypot(dx,dy)||1;nr.push([-dy/L,dx/L])}
    const Lp=P.map((p,i)=>[p[0]+nr[i][0]*Wd[i]/2,p[1]+nr[i][1]*Wd[i]/2]), Rp=P.map((p,i)=>[p[0]-nr[i][0]*Wd[i]/2,p[1]-nr[i][1]*Wd[i]/2]);
    const f=v=>v.toFixed(1), mid=(a,b)=>[(a[0]+b[0])/2,(a[1]+b[1])/2];
    let d=`M${f(Lp[0][0])} ${f(Lp[0][1])}`;
    for(let i=1;i<n-1;i++){const m1=mid(Lp[i-1],Lp[i]),m2=mid(Lp[i],Lp[i+1]);d+=` L${f(m1[0])} ${f(m1[1])} Q${f(Lp[i][0])} ${f(Lp[i][1])} ${f(m2[0])} ${f(m2[1])}`}
    const ue=[P[n-1][0]-P[n-2][0],P[n-1][1]-P[n-2][1]],le=Math.hypot(ue[0],ue[1])||1, us=[P[0][0]-P[1][0],P[0][1]-P[1][1]],ls=Math.hypot(us[0],us[1])||1;
    const ce=[P[n-1][0]+ue[0]/le*Wd[n-1]*cap,P[n-1][1]+ue[1]/le*Wd[n-1]*cap], cs=[P[0][0]+us[0]/ls*Wd[0]*cap,P[0][1]+us[1]/ls*Wd[0]*cap];
    d+=` L${f(Lp[n-1][0])} ${f(Lp[n-1][1])} Q${f(ce[0])} ${f(ce[1])} ${f(Rp[n-1][0])} ${f(Rp[n-1][1])}`;
    for(let i=n-2;i>0;i--){const m1=mid(Rp[i+1],Rp[i]),m2=mid(Rp[i],Rp[i-1]);d+=` L${f(m1[0])} ${f(m1[1])} Q${f(Rp[i][0])} ${f(Rp[i][1])} ${f(m2[0])} ${f(m2[1])}`}
    d+=` L${f(Rp[0][0])} ${f(Rp[0][1])} Q${f(cs[0])} ${f(cs[1])} ${f(Lp[0][0])} ${f(Lp[0][1])}Z`;
    return `<path d="${d}" fill="${col}"/>`;};
  const arm=(side,pose)=>{
    const S=[side*52,-294]; let E,W,ha=90,kind='open';
    switch(pose){
      case 'fist':  E=[side*94,-340]; W=[side*88,-398]; kind='fist'; ha=0; break;
      case 'point': E=[side*110,-280]; W=[side*164,-292]; ha=side>0?0:180; break;
      case 'hold':  E=[side*94,-326]; W=[side*88,-374]; kind='fist'; ha=0; break;
      case 'hip':   E=[side*104,-236]; W=[side*62,-198]; kind='fist'; ha=0; break;
      case 'cross': E=[side*74,-222]; W=[-side*22,-236]; kind='fist'; ha=0; break;
      case 'hoe':   E=[side*86,-232]; W=[side*44,-280]; kind='fist'; ha=0; break;
      case 'carry': E=[side*80,-226]; W=[side*62,-190]; kind='fist'; ha=0; break;
      default:      E=[side*74,-226]; W=[side*72,-170]; ha=90;
    }
    const dx=W[0]-E[0], dy=W[1]-E[1], L=Math.hypot(dx,dy), ux=dx/L, uy=dy/L;
    const C1=[E[0]+ux*16,E[1]+uy*16];
    let a='';
    // forearm (skin) first, sleeve over it, then cuff band
    a+=tube([E,[E[0]+ux*L*.55,E[1]+uy*L*.55],W],[24,22,21],sk);
    a+=tube([S,[(S[0]+E[0])/2+side*4,(S[1]+E[1])/2],E,C1],[40,33,30,30],o.jk);
    if(side>0) a+=tube([[S[0]+6,S[1]+8],[(S[0]+E[0])/2+side*8,(S[1]+E[1])/2+2],[E[0]+ux*6+4,E[1]+uy*6]],[12,12,10],o.jkD);
    a+=tube([[E[0]+ux*6,E[1]+uy*6],C1],[31,30],o.cuff||o.jkD,.12);
    a+=`<path d="M${S[0]+side*2} ${S[1]+34} q ${side*8} 8 ${side*5} 20" stroke="${lighten}" stroke-width="2.4" fill="none" stroke-linecap="round"/>`;
    if(pose==='point'){ a+=`<g transform="translate(${W[0]+side*6} ${W[1]})"><path d="M-12 -10 C -14 4 -8 12 2 12 C 10 12 13 4 12 -10Z" fill="${sk}" transform="rotate(${side>0?-90:90})"/><path d="M${side*8} -5 L${side*30} -7" stroke="${sk}" stroke-width="7" stroke-linecap="round"/><path d="M${side*2} 3 h${side*10}" stroke="${skd}" stroke-width="1.8"/></g>`; }
    else if(pose!=='carry') a+=hand(W[0]+ux*6,W[1]+uy*6,ha,kind);
    if(pose==='hoe') back+=`<path d="M${W[0]} ${W[1]} L ${-side*96} -470" stroke="#8A6238" stroke-width="9" stroke-linecap="round"/><path d="M${-side*96} -470 l${-side*10} 34 l${side*30} 8 l${side*2} -30Z" fill="#6E747A"/>`;
    return a;
  };
  s+=arm(-1,o.L||'down')+arm(1,o.R||'down');
  if(o.crate){ // a sack of parchment held against the belly, hands gripping both sides
    s+=`<g transform="translate(0 -206)"><path d="M-62 30 C -70 6 -66 -22 -52 -36 C -30 -44 30 -44 52 -36 C 66 -22 70 6 62 30Z" fill="#CDB48A" stroke="#9E8456" stroke-width="3"/>
      <path d="M-52 -36 C -20 -24 20 -24 52 -36" stroke="#9E8456" stroke-width="3" fill="none"/><path d="M-50 -2 H50 M-56 16 H56" stroke="#B59C70" stroke-width="2"/>
      <text x="0" y="12" text-anchor="middle" font-family="IBM Plex Sans,sans-serif" font-size="16" font-weight="700" fill="#7A6340">DURE</text></g>`;
    s+=hand(-70,-204,0,'fist')+hand(70,-204,0,'fist');
  }
  // ---------- head ----------
  const hy=-348;
  s+=`<path d="M-13 -322 L 13 -322 L 14 -300 C 6 -296 -6 -296 -14 -300Z" fill="${skd}"/>`;
  s+=`<ellipse cx="-31" cy="${hy+2}" rx="7" ry="11" fill="${skd}"/><ellipse cx="31" cy="${hy+2}" rx="7" ry="11" fill="${skd}"/>`;
  if(!o.male) s+=`<ellipse cx="0" cy="${hy-40}" rx="18" ry="14" fill="${hair}"/>`;
  s+=`<path d="M-30 ${hy-8} C -31 ${hy+22} -18 ${hy+38} 0 ${hy+38} C 18 ${hy+38} 31 ${hy+22} 30 ${hy-8} C 30 ${hy-32} -30 ${hy-32} -30 ${hy-8}Z" fill="${sk}"/>`;
  if(o.male) s+=`<path d="M-32 ${hy-4} C -36 ${hy-36} -14 ${hy-46} 4 ${hy-44} C 26 ${hy-42} 36 ${hy-28} 32 ${hy-4} C 28 ${hy-18} 20 ${hy-24} 10 ${hy-22} C 0 ${hy-30} -14 ${hy-26} -22 ${hy-18} C -26 ${hy-14} -28 ${hy-10} -32 ${hy-4}Z" fill="${hair}"/>`;
  else s+=`<path d="M-33 ${hy+8} C -38 ${hy-34} -14 ${hy-46} 2 ${hy-44} C 22 ${hy-44} 38 ${hy-32} 33 ${hy+8} C 30 ${hy-10} 20 ${hy-22} 4 ${hy-24} C 0 ${hy-18} -4 ${hy-18} -6 ${hy-24} C -20 ${hy-22} -30 ${hy-10} -33 ${hy+8}Z" fill="${hair}"/>`;
  s+=`<g fill="#D66E5B" opacity=".55"><ellipse cx="-17" cy="${hy+14}" rx="7" ry="5"/><ellipse cx="17" cy="${hy+14}" rx="7" ry="5"/></g>`;
  const brow=o.mood==='angry'?`<path d="M-21 ${hy-9} L -8 ${hy-4} M21 ${hy-9} L 8 ${hy-4}" stroke="${hair}" stroke-width="3.6" stroke-linecap="round"/>`:`<path d="M-21 ${hy-6} q7 -5 13 -1 M8 ${hy-7} q7 -4 13 1" stroke="${hair}" stroke-width="3.2" fill="none" stroke-linecap="round"/>`;
  s+=brow+(o.mood==='happy'?`<path d="M-18 ${hy+5} q5 -7 10 0 M8 ${hy+5} q5 -7 10 0" stroke="${hair}" stroke-width="3.2" fill="none" stroke-linecap="round"/>`:`<g fill="${hair}"><ellipse cx="-13" cy="${hy+3}" rx="3.2" ry="3.8"/><ellipse cx="13" cy="${hy+3}" rx="3.2" ry="3.8"/></g>`);
  s+=`<path d="M-2 ${hy+2} C -6 ${hy+12} -8 ${hy+18} -2 ${hy+20} C 2 ${hy+21} 6 ${hy+19} 6 ${hy+16}" fill="${skd}" stroke="${skd}" stroke-width="1"/>`;
  if(o.stache) s+=`<path d="M-16 ${hy+27} C -10 ${hy+20} -2 ${hy+21} 0 ${hy+24} C 2 ${hy+21} 10 ${hy+20} 16 ${hy+27} C 12 ${hy+30} 4 ${hy+28} 0 ${hy+27} C -4 ${hy+28} -12 ${hy+30} -16 ${hy+27}Z" fill="#231812"/>`;
  if(o.mood==='happy') s+=`<path d="M-11 ${hy+28} Q 0 ${hy+42} 11 ${hy+28}Z" fill="#6B3A22"/><path d="M-8 ${hy+29} Q 0 ${hy+33} 8 ${hy+29}" stroke="#fff" stroke-width="2.4" fill="none"/>`; else
  s+=o.mood==='angry'?`<path d="M-7 ${hy+31} Q 0 ${hy+27} 7 ${hy+31}" stroke="#6B3A22" stroke-width="2.6" fill="none" stroke-linecap="round"/>`:`<path d="M-7 ${hy+29} Q 0 ${hy+34} 7 ${hy+29}" stroke="#6B3A22" stroke-width="2.6" fill="none" stroke-linecap="round"/>`;
  // ---------- headwear ----------
  if(o.head==='cloth'){ const c=o.clothC||'#9A3326';
    s+=`<path d="M-33 ${hy-12} C -34 ${hy-40} 34 ${hy-40} 33 ${hy-12} C 20 ${hy-22} -20 ${hy-22} -33 ${hy-12}Z" fill="${c}"/><path d="M-33 ${hy-12} C -20 ${hy-22} 20 ${hy-22} 33 ${hy-12}" stroke="#241A16" stroke-width="2" opacity=".5" fill="none"/><path d="M-30 ${hy-28} C -10 ${hy-24} 10 ${hy-24} 30 ${hy-28}" stroke="#E4B64C" stroke-width="2" fill="none" stroke-dasharray="3 3"/><path d="M28 ${hy-26} l 20 -10 l -4 16 Z M30 ${hy-20} l 18 6 l -14 8Z" fill="${c}"/>`; }
  else if(o.head==='cap'){ const cc=o.capC||'#3F5F43', cd=o.capD||'#2F4A33', b=hy-20;
    s+=`<path d="M-32 ${b+8} C -33 ${b-26} -16 ${b-36} 0 ${b-36} C 16 ${b-36} 33 ${b-26} 32 ${b+8}Z" fill="${cc}"/><path d="M0 ${b-36} C -6 ${b-18} -6 ${b-2} -3 ${b+8} M0 ${b-36} C 12 ${b-20} 18 ${b-4} 18 ${b+8}" stroke="${cd}" stroke-width="2" fill="none"/><path d="M-34 ${b+4} C -16 ${b-2} 16 ${b-2} 34 ${b+4} L 38 ${b+14} C 16 ${b+24} -16 ${b+24} -38 ${b+14}Z" fill="${cd}"/><circle cx="0" cy="${b-36}" r="3.4" fill="${cd}"/>`; }
  return back+s;
};
