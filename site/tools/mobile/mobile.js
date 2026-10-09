/* Phone edition: everything here runs on scroll or once on reveal; nothing redraws the illustrations.
   The walkers are small separate layers moved with a transform, so the maps underneath never repaint. */
(()=>{
const RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];

/* reveal once */
const count=el=>{const to=+el.dataset.to;if(RM)return;const t0=performance.now();el.textContent='0';
  const f=t=>{const u=Math.min(1,(t-t0)/1100);el.textContent=Math.round(to*(1-Math.pow(1-u,3)));if(u<1)requestAnimationFrame(f)};requestAnimationFrame(f)};
const io=new IntersectionObserver(es=>es.forEach(e=>{if(!e.isIntersecting)return;e.target.classList.add('in');e.target.querySelectorAll('.cnt').forEach(count);io.unobserve(e.target)}),{rootMargin:'0px 0px -10% 0px'});
$$('.rv').forEach(el=>io.observe(el));

/* chapter label */
const chap=$('#chap');let last='';
const io2=new IntersectionObserver(es=>es.forEach(e=>{if(!e.isIntersecting)return;const c=e.target.dataset.c,t=e.target.dataset.t;if(c+t!==last){last=c+t;chap.innerHTML=`<b>${c}</b>${t}`};document.body.classList.toggle('nightbar',+c>=7)}),{rootMargin:'-40% 0px -55% 0px'});
$$('[data-c]').forEach(m=>io2.observe(m));

/* walkers: standing figures from the story follow their paths as their section scrolls by.
   Each is its own small layer: moving it, or swinging its legs, never redraws the map. On the zoomed road the map
   slides sideways to keep Noor in view. */
const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
const scenes=$$('.road').map(sec=>{const svg=sec.querySelector('svg.aerial'),vb=svg.viewBox.baseVal,pan=sec.querySelector('.pan'),sky=sec.querySelector('.sky');
  const ws=[...sec.querySelectorAll('.sp.walker')].map(el=>{const p=svg.getElementById(el.dataset.p);
    return {el,p,L:p.getTotalLength(),fx:parseFloat(el.style.getPropertyValue('--fx')),fy:parseFloat(el.style.getPropertyValue('--fy')),
      legF:el.querySelector('[id$="_legF"],.lf'),legB:el.querySelector('[id$="_legB"],.lb'),bd:el.querySelector('.bd'),front:el.classList.contains('front'),last:null,ph:0,still:0}});
  const st=[...sec.querySelectorAll('.sp.still')].map(el=>{const [x,y]=el.dataset.at.split(',').map(Number);return {el,x,y,fx:parseFloat(el.style.getPropertyValue('--fx')),fy:parseFloat(el.style.getPropertyValue('--fy'))}});
  return {sec,svg,vb,pan,sky,ws,st,zoom:sec.classList.contains('zoom'),on:false,rain:sec.querySelector('.rain'),sign:sec.querySelector('#kg'),heap:sec.querySelector('.heap')}});
const ioS=new IntersectionObserver(es=>es.forEach(e=>{const s=scenes.find(x=>x.sec===e.target);s.on=e.isIntersecting;if(s.rain)s.rain.classList.toggle('on',e.isIntersecting&&!RM);if(s.on)tick()}),{rootMargin:'20% 0px'});
scenes.forEach(s=>ioS.observe(s.sec));
let raf=0;
function step(w,a,k){   // feet step with the distance actually walked
  if(w.last){const d=Math.hypot(a.x-w.last.x,a.y-w.last.y)*k;w.ph+=d/11;w.moving=d>.4}
  w.last={x:a.x,y:a.y};const sn=w.moving&&!RM?Math.sin(w.ph):0;
  if(w.front){   // walking toward the reader: one foot lifts, then the other, and the body rises a little on each step
    if(w.legF)w.legF.setAttribute('transform',`translate(0 ${(-Math.max(0,sn)*16).toFixed(1)})`);
    if(w.legB)w.legB.setAttribute('transform',`translate(0 ${(-Math.max(0,-sn)*16).toFixed(1)})`);
    if(w.bd)w.bd.setAttribute('transform',`translate(0 ${(-Math.abs(sn)*6).toFixed(1)}) rotate(${(sn*1.2).toFixed(2)} 0 -200)`);
    w.bks=w.bks||[...w.el.querySelectorAll('.bk')];w.bks.forEach(b=>b.setAttribute('transform',`rotate(${(-sn*5).toFixed(1)} ${b.dataset.x} -300)`));return}   // baskets swing from the pole
  const sw=sn*16;
  if(w.legF)w.legF.setAttribute('transform',`rotate(${sw.toFixed(1)} 4 -44)`);if(w.legB)w.legB.setAttribute('transform',`rotate(${(-sw).toFixed(1)} -6 -44)`)}
function place(s){const r=s.svg.getBoundingClientRect(),k=r.width/s.vb.width,H=innerHeight;
  const prog=clamp((H*.58-r.top)/r.height,0,1);let noorX=null;
  s.ws.forEach((w,i)=>{let u;
    if(w.el.classList.contains('nb'))u=clamp((prog-.06-i*.04)/.6,0,1);             // neighbours set off one after another
    else{   // Noor: wherever her road is at the same height on screen. One continuous walk across both maps:
            // the road's Noor shows only while that height is on the road, the gathering's only once it is on the gathering
      const yT=(H*.58-r.top)/k;w.el.style.visibility=(s.heap?yT>=0:yT<=s.vb.height)?'visible':'hidden';
      let lo=0,hi=w.L;for(let n=0;n<22;n++){const m=(lo+hi)/2;if(w.p.getPointAtLength(m).y<yT)lo=m;else hi=m}u=lo/w.L}
    const a=w.p.getPointAtLength(u*w.L),b=w.p.getPointAtLength(Math.min(w.L,u*w.L+3)),c=w.p.getPointAtLength(Math.max(0,u*w.L-3));
    const dx=b.x-c.x;if(!w.front&&Math.abs(dx)>.6)w.el.classList.toggle('left',dx<0);   // front-facing figures never turn
    w.el.style.transform=`translate3d(${((a.x-s.vb.x)*k-w.fx).toFixed(1)}px,${(a.y*k-w.fy).toFixed(1)}px,0)`;
    step(w,a,k);if(w.el.classList.contains('noor'))noorX=(a.x-s.vb.x)*k});
  s.st.forEach(t=>{t.el.style.transform=`translate3d(${((t.x-s.vb.x)*k-t.fx).toFixed(1)}px,${(t.y*k-t.fy).toFixed(1)}px,0)`});
  {const vw=s.sky.clientWidth,pw=s.pan.offsetWidth,mid=(200-s.vb.x)*k,e=clamp((prog-.8)/.2,0,1),fx=s.zoom&&noorX!=null?noorX*(1-e)+mid*e:mid;   // at the road's end the view eases back to centre, where the gathering map picks up   // the road follows Noor; the gathering stays centred on the lot
    s.pan.style.transform=`translate3d(${clamp(vw/2-fx,vw-pw,0).toFixed(1)}px,0,0)`}
  if(s.heap){const g=clamp((prog-.12)/.62,0,1);   // one more basket on the stack as each neighbour arrives
    if(!s.hb)s.hb=[...s.heap.querySelectorAll('.hb')];const n=Math.max(1,Math.ceil(g*s.hb.length));
    if(n!==s.hn){s.hn=n;s.hb.forEach((b,i)=>b.style.opacity=i<n?1:0)}
    if(s.sign)s.sign.textContent=`${Math.round(40+g*460)} kg`}}
function tick(){if(raf)return;raf=requestAnimationFrame(()=>{raf=0;scenes.forEach(s=>{if(s.on)place(s)});
  const h=document.documentElement.scrollHeight-innerHeight;$('#prog').style.transform=`scaleX(${h>0?scrollY/h:0})`})}
addEventListener('scroll',tick,{passive:true});addEventListener('resize',tick);
scenes.forEach(place);

/* cards play their small entrance once, when they come into view */
const io3=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('on');io3.unobserve(e.target)}}),{rootMargin:'0px 0px -15% 0px'});
$$('.dash,.nf').forEach(el=>io3.observe(el));

/* the opening picture: clouds and mountains drift at different speeds as the page leaves it */
const hero=$('.hero'),layers=hero?[['_pCloud',.32],['_pMount',.16]].flatMap(([id,f])=>[...hero.querySelectorAll(`[id$="${id}"]`)].map(el=>[el,f])):[];
if(layers.length&&!RM){let hr=0;const par=()=>{hr=0;const y=scrollY;if(y>innerHeight*1.2)return;layers.forEach(([el,f])=>el.setAttribute('transform',`translate(0 ${(y*f).toFixed(1)})`))};
  addEventListener('scroll',()=>{if(!hr)hr=requestAnimationFrame(par)},{passive:true})}

/* tabs: one view shows, the others are a tap (or an arrow key) away */
$$('.tabs').forEach(tb=>{const bs=[...tb.querySelectorAll('[role=tab]')],ps=[...tb.querySelectorAll('[role=tabpanel]')];
  const sel=i=>{bs.forEach((b,k)=>{b.setAttribute('aria-selected',k===i);b.tabIndex=k===i?0:-1});ps.forEach((p,k)=>{p.hidden=k!==i;if(k===i)p.querySelectorAll('.nf').forEach(n=>n.classList.add('on'))})};
  bs.forEach((b,i)=>{b.addEventListener('click',()=>sel(i));b.addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='ArrowLeft'){const j=(i+(e.key==='ArrowRight'?1:bs.length-1))%bs.length;sel(j);bs[j].focus()}})});sel(0)});
/* an opened detail plays its card's entrance */
$$('details.more').forEach(d=>d.addEventListener('toggle',()=>{if(d.open)requestAnimationFrame(()=>d.querySelectorAll('.nf,.dash').forEach(n=>n.classList.add('on')))}));
$$('details.dsh').forEach(d=>d.addEventListener('toggle',()=>{if(d.open)requestAnimationFrame(()=>d.closest('.dash').classList.remove('on')||requestAnimationFrame(()=>d.closest('.dash').classList.add('on')))}));

/* on a wide screen there is room: whole conversations show from the start */


/* the step row is as tall as the step on screen, so a short step leaves no gap below it */
$$('.hsteps').forEach(h=>{const st=[...h.children];let t=0;
  const fit=()=>{const i=Math.round(h.scrollLeft/h.clientWidth),el=st[Math.max(0,Math.min(st.length-1,i))];h.style.height=(el.offsetHeight+26)+'px'};
  h.addEventListener('scroll',()=>{clearTimeout(t);t=setTimeout(fit,90)},{passive:true});addEventListener('resize',fit);
  h.addEventListener('toggle',fit,true);new ResizeObserver(fit).observe(st[0]);fit()});

/* videos load only when tapped */
$$('.vid').forEach(b=>b.addEventListener('click',()=>{if(b.classList.contains('on'))return;b.classList.add('on');
  b.innerHTML=`<iframe src="https://www.youtube-nocookie.com/embed/${b.dataset.id}?autoplay=1&rel=0" title="${b.textContent.trim()}" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>`}));
})();
