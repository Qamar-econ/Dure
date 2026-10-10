/* summit edition: the header link of the section being read is marked */
(()=>{const ls=[...document.querySelectorAll('.nxnav a')];if(!ls.length)return;const m=new Map(ls.map(a=>[a.getAttribute('href').slice(1),a]));
 const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){ls.forEach(a=>a.classList.remove('on'));const a=m.get(e.target.id);if(a)a.classList.add('on')}}),{rootMargin:'-45% 0px -50% 0px'});
 m.forEach((a,id)=>{const s=document.getElementById(id);if(s)io.observe(s)});
 /* an opened detail shows its contents at once (its cards play their entrance) */
 document.querySelectorAll('details.dd,details.wk').forEach(d=>d.addEventListener('toggle',()=>{if(!d.open)return;
   const t=d.querySelector(':scope > template.lz');if(t){d.appendChild(t.content.cloneNode(true));t.remove()}   // steps are built on first open
   d.querySelectorAll('.rv').forEach(x=>x.classList.add('in'));requestAnimationFrame(()=>d.querySelectorAll('.dash,.nf').forEach(x=>x.classList.add('on')))}));})();
