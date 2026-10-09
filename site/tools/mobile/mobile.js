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

/* walkers: each follows its path as its section scrolls by */
const scenes=$$('.road').map(sec=>{const svg=sec.querySelector('svg.aerial'),vb=svg.viewBox.baseVal;
  const ws=[...sec.querySelectorAll('.wk')].map(el=>{const p=svg.getElementById(el.dataset.p);return {el,p,L:p.getTotalLength()}});
  return {sec,svg,vb,ws,on:false,rain:sec.querySelector('.rain'),sign:sec.querySelector('#kg')}});
const ioS=new IntersectionObserver(es=>es.forEach(e=>{const s=scenes.find(x=>x.sec===e.target);s.on=e.isIntersecting;if(s.rain)s.rain.classList.toggle('on',e.isIntersecting&&!RM);if(s.on)tick()}),{rootMargin:'20% 0px'});
scenes.forEach(s=>ioS.observe(s.sec));
let raf=0;
function place(s){const r=s.svg.getBoundingClientRect(),k=r.width/s.vb.width,H=innerHeight;
  // progress: the walker stays a little below the middle of the screen while the map scrolls under it
  const prog=Math.min(1,Math.max(0,(H*.58-r.top)/r.height));
  s.ws.forEach((w,i)=>{
    let u=prog;
    if(w.el.classList.contains('nb')){u=Math.min(1,Math.max(0,(prog-.08-i*.035)/.62))}   // neighbours set off one after another and reach the lot
    else if(s.sign){u=Math.min(1,Math.max(0,(prog-.02)/.7))}
    else{const P=w.p,L=w.L;let lo=0,hi=L,yT=(H*.58-r.top)/k;   // Noor on the long road: put her where the road is at that height
      for(let n=0;n<22;n++){const m=(lo+hi)/2;if(P.getPointAtLength(m).y<yT)lo=m;else hi=m}u=lo/L}
    const a=w.p.getPointAtLength(u*w.L),b=w.p.getPointAtLength(Math.min(w.L,u*w.L+2));
    const ang=Math.atan2(b.y-a.y,b.x-a.x)*180/Math.PI+90;
    w.el.style.transform=`translate3d(${(a.x*k).toFixed(1)}px,${(a.y*k).toFixed(1)}px,0) rotate(${ang.toFixed(1)}deg)`});
  if(s.sign){const n=Math.round(40+Math.min(1,Math.max(0,(prog-.1)/.6))*460);s.sign.textContent=`${n} kg`}}
function tick(){if(raf)return;raf=requestAnimationFrame(()=>{raf=0;scenes.forEach(s=>{if(s.on)place(s)});
  const h=document.documentElement.scrollHeight-innerHeight;$('#prog').style.transform=`scaleX(${h>0?scrollY/h:0})`})}
addEventListener('scroll',tick,{passive:true});addEventListener('resize',tick);
scenes.forEach(place);

/* videos load only when tapped */
$$('.vid').forEach(b=>b.addEventListener('click',()=>{if(b.classList.contains('on'))return;b.classList.add('on');
  b.innerHTML=`<iframe src="https://www.youtube-nocookie.com/embed/${b.dataset.id}?autoplay=1&rel=0" title="${b.textContent.trim()}" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>`}));
})();
