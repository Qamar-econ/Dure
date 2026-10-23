/* summit edition: the header link of the section being read is marked */
(()=>{const ls=[...document.querySelectorAll('.nxnav a')];if(!ls.length)return;const m=new Map(ls.map(a=>[a.getAttribute('href').slice(1),a]));
 const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){ls.forEach(a=>a.classList.remove('on'));const a=m.get(e.target.id);if(a)a.classList.add('on')}}),{rootMargin:'-45% 0px -50% 0px'});
 m.forEach((a,id)=>{const s=document.getElementById(id);if(s)io.observe(s)});
 /* an opened detail shows its contents at once (its cards play their entrance) */
 document.querySelectorAll('details.dd,details.wk').forEach(d=>d.addEventListener('toggle',()=>{if(!d.open)return;
   const t=d.querySelector(':scope > template.lz');if(t){d.appendChild(t.content.cloneNode(true));t.remove()}   // steps are built on first open
   d.querySelectorAll('.rv').forEach(x=>x.classList.add('in'));requestAnimationFrame(()=>d.querySelectorAll('.dash,.nf').forEach(x=>x.classList.add('on')))}));})();

/* Contact link: go to the founder profile, correcting for layout shifts during the scroll */
/* Contact: land on the founder profile, just under the header. Pictures and videos above can change height while the smooth scroll
   runs, which made it stop short, so the position is re-checked until it settles (and clamped at the end of the page). */
function goProfile(sel){const el=document.querySelector(sel);if(!el)return false;
  const hd=document.querySelector('header.bar'),RM=matchMedia('(prefers-reduced-motion:reduce)').matches;
  const tgt=()=>{const off=(hd?hd.getBoundingClientRect().bottom:0)+16;return Math.max(0,Math.min(document.documentElement.scrollHeight-innerHeight,Math.round(scrollY+el.getBoundingClientRect().top-off)))};
  scrollTo({top:tgt(),behavior:RM?'auto':'smooth'});
  let last=-1,n=0;const chk=()=>{const y=Math.round(scrollY),t=tgt();if(Math.abs(y-t)<=3&&y===last)return;
    if(y===last)scrollTo({top:t,behavior:RM?'auto':'smooth'});last=y;if(++n<40)setTimeout(chk,120)};setTimeout(chk,120);return true}
document.querySelectorAll('.nxnav a[href="#contact"]').forEach(a=>a.addEventListener('click',e=>{if(goProfile('#contact .fdr')){e.preventDefault();history.replaceState(null,'','#contact')}}));
