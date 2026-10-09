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
const io2=new IntersectionObserver(es=>es.forEach(e=>{if(!e.isIntersecting)return;const c=e.target.dataset.c,t=e.target.dataset.t;if(c+t!==last){last=c+t;chap.innerHTML=`<b>${c}</b>${t}`}}),{rootMargin:'-40% 0px -55% 0px'});
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
    if(w.bd)w.bd.setAttribute('transform',`translate(0 ${(-Math.abs(sn)*6).toFixed(1)}) rotate(${(sn*1.2).toFixed(2)} 0 -200)`);return}
  const sw=sn*16;
  if(w.legF)w.legF.setAttribute('transform',`rotate(${sw.toFixed(1)} 4 -44)`);if(w.legB)w.legB.setAttribute('transform',`rotate(${(-sw).toFixed(1)} -6 -44)`)}
function place(s){const r=s.svg.getBoundingClientRect(),k=r.width/s.vb.width,H=innerHeight;
  const prog=clamp((H*.58-r.top)/r.height,0,1);let noorX=null;
  s.ws.forEach((w,i)=>{let u;
    if(w.el.classList.contains('nb'))u=clamp((prog-.06-i*.04)/.6,0,1);             // neighbours set off one after another
    else if(s.heap)u=clamp((prog-.02)/.66,0,1);
    else{let lo=0,hi=w.L;const yT=(H*.58-r.top)/k;                                      // Noor on the long road: where the road is at that height
      for(let n=0;n<22;n++){const m=(lo+hi)/2;if(w.p.getPointAtLength(m).y<yT)lo=m;else hi=m}u=lo/w.L}
    const a=w.p.getPointAtLength(u*w.L),b=w.p.getPointAtLength(Math.min(w.L,u*w.L+3)),c=w.p.getPointAtLength(Math.max(0,u*w.L-3));
    const dx=b.x-c.x;if(!w.front&&Math.abs(dx)>.6)w.el.classList.toggle('left',dx<0);   // front-facing figures never turn
    w.el.style.transform=`translate3d(${(a.x*k-w.fx).toFixed(1)}px,${(a.y*k-w.fy).toFixed(1)}px,0)`;
    step(w,a,k);if(w.el.classList.contains('noor'))noorX=a.x*k});
  s.st.forEach(t=>{t.el.style.transform=`translate3d(${(t.x*k-t.fx).toFixed(1)}px,${(t.y*k-t.fy).toFixed(1)}px,0)`});
  if(s.zoom&&noorX!=null){const vw=s.sky.clientWidth,pw=s.pan.offsetWidth;s.pan.style.transform=`translate3d(${clamp(vw/2-noorX,vw-pw,0).toFixed(1)}px,0,0)`}
  if(s.heap){const g=clamp((prog-.12)/.62,0,1);s.heap.style.transform=`translate(-50%,-86%) scale(${(.12+.88*g).toFixed(3)})`;
    if(s.sign)s.sign.textContent=`${Math.round(40+g*460)} kg`}}
function tick(){if(raf)return;raf=requestAnimationFrame(()=>{raf=0;scenes.forEach(s=>{if(s.on)place(s)});
  const h=document.documentElement.scrollHeight-innerHeight;$('#prog').style.transform=`scaleX(${h>0?scrollY/h:0})`})}
addEventListener('scroll',tick,{passive:true});addEventListener('resize',tick);
scenes.forEach(place);

/* videos load only when tapped */
$$('.vid').forEach(b=>b.addEventListener('click',()=>{if(b.classList.contains('on'))return;b.classList.add('on');
  b.innerHTML=`<iframe src="https://www.youtube-nocookie.com/embed/${b.dataset.id}?autoplay=1&rel=0" title="${b.textContent.trim()}" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>`}));
})();
