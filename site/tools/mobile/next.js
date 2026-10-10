/* summit edition: the header link of the section being read is marked */
(()=>{const ls=[...document.querySelectorAll('.nxnav a')];if(!ls.length)return;const m=new Map(ls.map(a=>[a.getAttribute('href').slice(1),a]));
 const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){ls.forEach(a=>a.classList.remove('on'));const a=m.get(e.target.id);if(a)a.classList.add('on')}}),{rootMargin:'-45% 0px -50% 0px'});
 m.forEach((a,id)=>{const s=document.getElementById(id);if(s)io.observe(s)});
 /* a link to a closed detail opens it */
 document.querySelectorAll('details.dd').forEach(d=>d.addEventListener('toggle',()=>{if(d.open)d.querySelectorAll('.rv').forEach(x=>x.classList.add('in'))}));})();
/* the header turns dark with the page */
(()=>{const n=[...document.querySelectorAll('.night,.dark.close')];if(!n.length)return;const f=()=>{const y=58;document.body.classList.toggle('nightbar',n.some(e=>{const r=e.getBoundingClientRect();return r.top<y&&r.bottom>y}))};addEventListener('scroll',f,{passive:true});f()})();
