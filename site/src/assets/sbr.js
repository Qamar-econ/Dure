/* Samsung Internet's dark ("night") mode recolours every page itself: it ignores color-scheme and
   prefers-color-scheme, distorts drawings (SVG) worst of all, dims or inverts many bitmap images, and cannot be
   detected from the page. It never touches <canvas> or <video>. So on Samsung Internet each drawing is shown on a
   canvas of the same size and place: the SVG is drawn into it (words keep their web font), and redrawn when the
   drawing changes (animated scenes frame by frame). The SVG stays in the page, hidden, for the scripts that move it.
   Words laid over a drawing get a soft plate so they stay readable in either mode.
   ?sbr=1 forces this on for testing, ?sbr=0 turns it off. */
(function(){
  var q=location.search;
  var on=/SamsungBrowser/i.test(navigator.userAgent)||/[?&]sbr=1\b/.test(q);
  if(!on||/[?&]sbr=0\b/.test(q))return;
  var root=document.documentElement;root.classList.add('sbr');
  var css=document.createElement('style');
  css.textContent='.sbr svg.sbr-off{display:none!important}.sbr canvas.sbr-cv{pointer-events:none}'+
    '.sbr .hero .htxt .tag,.sbr .hero .htxt .def,.sbr #hero .tag,.sbr #hero .def{background:rgba(242,234,218,.8);border-radius:8px;box-shadow:0 0 0 5px rgba(242,234,218,.8);-webkit-box-decoration-break:clone;box-decoration-break:clone}';
  document.head.appendChild(css);
  var NS='http://www.w3.org/2000/svg',DPR=Math.min(2,window.devicePixelRatio||1);
  var PROPS=['fill','stroke','stroke-width','stroke-dasharray','stroke-linecap','stroke-linejoin','opacity','fill-opacity','stroke-opacity','stop-color','stop-opacity','visibility','display','transform','transform-origin','mix-blend-mode',
             'font-family','font-size','font-weight','font-style','letter-spacing','text-anchor','dominant-baseline','font-variation-settings'];
  var DEF={'opacity':'1','fill-opacity':'1','stroke-opacity':'1','stop-opacity':'1','visibility':'visible','transform':'none','mix-blend-mode':'normal','stroke-dasharray':'none','letter-spacing':'normal','font-variation-settings':'normal','dominant-baseline':'auto','text-anchor':'start','stroke-linecap':'butt','stroke-linejoin':'miter'};
  var BOX=['position','top','right','bottom','left','margin-top','margin-right','margin-bottom','margin-left','z-index','transform','transform-origin','opacity','filter','float','grid-area','align-self','justify-self','vertical-align','border-radius','flex','order','box-shadow','mix-blend-mode','clip-path','mask-image','-webkit-mask-image'];
  /* ---- web fonts, embedded so words inside a drawing look the same ---- */
  var faces=null,fontData={},fontCache={};
  function loadFaces(){if(faces)return faces;
    var links=[].slice.call(document.querySelectorAll('link[rel=stylesheet][href*="fonts.googleapis.com"]'));
    faces=Promise.all(links.map(function(l){return fetch(l.href).then(function(r){return r.text()}).catch(function(){return ''})})).then(function(all){
      var out=[];all.join('\n').replace(/\/\*\s*([\w-]+)\s*\*\/\s*@font-face\s*{([^}]*)}/g,function(_,sub,body){
        if(sub!=='latin'&&sub!=='latin-ext')return;var fam=(body.match(/font-family:\s*['"]?([^;'"]+)/)||[])[1],url=(body.match(/url\(([^)]+)\)/)||[])[1];
        if(fam&&url)out.push({fam:fam.trim(),url:url.replace(/['"]/g,''),body:body})});return out});
    return faces}
  function dataUrl(u){if(!fontData[u])fontData[u]=fetch(u).then(function(r){return r.blob()}).then(function(b){return new Promise(function(ok){var fr=new FileReader();fr.onload=function(){ok(fr.result)};fr.readAsDataURL(b)})}).catch(function(){return null});return fontData[u]}
  function fontCss(fams){if(!fams.length)return Promise.resolve('');var key=fams.join('|');if(fontCache[key])return fontCache[key];
    return fontCache[key]=loadFaces().then(function(list){var use=list.filter(function(f){return fams.some(function(x){return x.toLowerCase().indexOf(f.fam.toLowerCase())>=0})});
      return Promise.all(use.map(function(f){return dataUrl(f.url).then(function(d){return d?'@font-face{'+f.body.replace(/url\([^)]+\)/,'url('+d+')')+'}':''})}))}).then(function(a){return a.join('')})}
  /* ---- which drawings ---- */
  function skip(svg){
    if(svg.parentElement&&svg.parentElement.closest('svg'))return true;    // inside another drawing
    if(svg.querySelector('foreignObject,image'))return true;               // holds a photo or HTML: leave it
    var r=svg.getBoundingClientRect();if(r.width<56||r.height<48)return true;   // logos and icons
    if(svg.closest('button,a'))return true;
    return false}
  var S=new WeakMap(),all=[];
  function measure(svg){var s=S.get(svg);svg.classList.remove('sbr-off');
    var cs=getComputedStyle(svg),w=parseFloat(cs.width)||svg.getBoundingClientRect().width,h=parseFloat(cs.height)||svg.getBoundingClientRect().height,st='';
    for(var i=0;i<BOX.length;i++){var v=cs.getPropertyValue(BOX[i]);if(v)st+=BOX[i]+':'+v+';'}
    var d=cs.display;st+='display:'+(d==='inline'?'inline-block':d==='none'?'none':d)+';width:'+w+'px;height:'+h+'px;box-sizing:border-box;';
    if(s.drawn)svg.classList.add('sbr-off');else st+='display:none!important;';   // until the first picture is ready the drawing itself stays on screen
    if(s.st!==st){s.cv.setAttribute('style',st);s.st=st}
    var W=Math.max(1,Math.round(w*DPR)),H=Math.max(1,Math.round(h*DPR));if(s.cv.width!==W||s.cv.height!==H){s.cv.width=W;s.cv.height=H}
    s.w=w;s.h=h}
  /* the drawing as a standalone SVG: its look (computed styles) written onto every shape, outside definitions brought in */
  function standalone(svg,s){
    var c=svg.cloneNode(true),fams=[];
    if(!s.raw){var src=[svg].concat([].slice.call(svg.querySelectorAll('*'))),dst=[c].concat([].slice.call(c.querySelectorAll('*')));
      for(var i=0;i<src.length;i++){var cs=getComputedStyle(src[i]),st='',isT=/^(text|tspan|textPath)$/.test(src[i].tagName);
        for(var k=0;k<PROPS.length;k++){var p=PROPS[k];if(!isT&&p.indexOf('font')===0&&p!=='font-size')continue;var v=cs.getPropertyValue(p);if(!v||v===DEF[p])continue;
          if(i===0&&(p==='display'||p==='transform'||p==='opacity'||p==='visibility'))continue;   // the box itself: the canvas carries those
          if(v.indexOf('url(')>=0)v=v.replace(/url\((['"]?)[^)#'"]*#([^)'"]+)\1\)/g,'url(#$2)');v=v.replace(/"/g,"'");
          if(p==='transform-origin'&&cs.getPropertyValue('transform')==='none')continue;
          if(p==='font-family'&&fams.indexOf(v)<0)fams.push(v);st+=p+':'+v+';'}
        dst[i].setAttribute('style',st);dst[i].removeAttribute('class')}}
    else{var tf=c.querySelectorAll('[font-family]');for(var j=0;j<tf.length;j++){var f=tf[j].getAttribute('font-family');if(fams.indexOf(f)<0)fams.push(f)}c.removeAttribute('style')}
    var defs=null,guard=0,miss=function(){var ids=[],h=new XMLSerializer().serializeToString(c),re=/url\(#([^)'"]+)\)|href="#([^"]+)"/g,m;
      while((m=re.exec(h))){var id=m[1]||m[2];if(ids.indexOf(id)<0&&!c.querySelector('[id="'+id+'"]'))ids.push(id)}return ids};
    for(var ids=miss();ids.length&&guard<6;ids=miss(),guard++){ids.forEach(function(id){var el=document.getElementById(id);if(!el)return;
      if(!defs){defs=document.createElementNS(NS,'defs');c.insertBefore(defs,c.firstChild)}defs.appendChild(el.cloneNode(true))})}
    c.setAttribute('width',s.w);c.setAttribute('height',s.h);c.setAttribute('xmlns',NS);c.removeAttribute('class');
    if(!s.raw)c.removeAttribute('style');
    return {c:c,fams:c.querySelector('text')?fams:[]}}
  var slow=0,off=false,SLOW=+((q.match(/[?&]sbrslow=(\d+)/)||[])[1]||150);   // ms of work for one redraw: ~45 on a mid-range phone, ~90 on a low-end one
  /* if the phone turns out too slow (a redraw needing over 150 ms of work, twice), everything goes back to the drawings as they are */
  function teardown(){off=true;all.forEach(function(svg){var s=S.get(svg);clearTimeout(s.tm);if(s.mo)s.mo.disconnect();s.cv.remove();svg.classList.remove('sbr-off')});all=[];cm.disconnect();io.disconnect();vio.disconnect();root.classList.remove('sbr')}
  function draw(svg){if(off)return;var s=S.get(svg);if(!s)return;if(s.busy){s.again=true;return}s.busy=true;var cost=0,c0=performance.now();
    var done=function(){s.busy=false;s.cost=cost;(window.__sbrCost=window.__sbrCost||[]).push(Math.round(cost));if(cost>SLOW&&++slow>=2){teardown();return}if(s.again){s.again=false;draw(svg)}};
    try{measure(svg);if(!s.w||!s.h){done();return}
      var o=standalone(svg,s);cost+=performance.now()-c0;if(s.raw&&svg.style.filter)s.cv.style.filter=svg.style.filter;
      fontCss(o.fams).then(function(fc){if(fc){var st=document.createElementNS(NS,'style');st.textContent=fc;o.c.insertBefore(st,o.c.firstChild)}
        var img=new Image();img.onload=function(){var d0=performance.now(),x=s.cv.getContext('2d');x.clearRect(0,0,s.cv.width,s.cv.height);x.drawImage(img,0,0,s.cv.width,s.cv.height);if(!s.drawn){s.drawn=true;measure(svg)}cost+=performance.now()-d0;done()};
        img.onerror=done;img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(new XMLSerializer().serializeToString(o.c))})}
    catch(e){done()}}
  function mount(svg){if(off||S.has(svg))return;var cv=document.createElement('canvas');cv.className='sbr-cv';cv.setAttribute('aria-hidden','true');
    var lab=svg.getAttribute('aria-label');if(lab){cv.setAttribute('role','img');cv.setAttribute('aria-label',lab);cv.removeAttribute('aria-hidden')}
    byCv.set(cv,svg);svg.after(cv);S.set(svg,{cv:cv,raw:false,n:0,t:0,vis:true});all.push(svg);measure(svg);soon(svg);vio.observe(cv);
    watch(svg,true)}
  /* changes inside a drawing: redraw; one that changes all the time (an animated scene) is copied as it is, without restyling, at up to ~25 frames a second */
  /* redrawing means re-serialising the whole drawing and decoding it as an image: far too heavy to do per frame on a phone.
     A drawing is redrawn 120 ms after it stops changing; while it keeps changing (scroll-driven scenes), at most once a second. */
  var lastScroll=0;addEventListener('scroll',function(){lastScroll=performance.now()},{passive:true});
  function soon(svg){var s=S.get(svg),now=performance.now();if(!s.vis){s.dirty=true;return}clearTimeout(s.tm);
    var sc=now-lastScroll<450;   // while the page scrolls nothing is redrawn: once it rests, one redraw
    if(!s.first||sc)s.first=now;var wait=sc?460:(s.raw?Math.max(0,Math.max(250,(s.cost||0)*4)-(now-(s.last||0))):(now-s.first>1000?0:120));
    s.tm=setTimeout(function(){if(performance.now()-lastScroll<450){soon(svg);return}s.first=0;s.last=performance.now();draw(svg)},wait)}
  function watch(svg,on){var s=S.get(svg);if(!s.mo)s.mo=new MutationObserver(function(list){if(list.every(function(m){return m.target===svg&&m.attributeName==='class'}))return;   /* our own show/hide of the drawing: not a change */var now=performance.now();if(now-s.t>1000){s.n=0;s.t=now}s.n++;if(s.n>12)s.raw=true;soon(svg)});
    if(on&&!s.watching){s.mo.observe(svg,{subtree:true,attributes:true,childList:true,characterData:true});s.watching=true}else if(!on&&s.watching){s.mo.disconnect();s.watching=false}}
  var cm=new MutationObserver(function(list){var tg=[];list.forEach(function(m){if(tg.indexOf(m.target)<0)tg.push(m.target)});
    all.forEach(function(svg){for(var i=0;i<tg.length;i++)if(tg[i]!==svg&&tg[i].contains(svg)&&!svg.contains(tg[i])){soon(svg);break}})});
  cm.observe(root,{subtree:true,attributes:true,attributeFilter:['class','data-theme','data-step']});
  /* only drawings on screen are redrawn; one that changed while off screen is redrawn when it comes back */
  var byCv=new WeakMap();
  var vio=new IntersectionObserver(function(es){es.forEach(function(e){var svg=byCv.get(e.target);if(!svg)return;var s=S.get(svg);s.vis=e.isIntersecting;watch(svg,s.vis);if(s.vis){s.dirty=false;soon(svg)}})},{rootMargin:'150px'});
  var seen=new WeakSet();
  var io=new IntersectionObserver(function(es){es.forEach(function(e){var svg=e.target;if(!e.isIntersecting||seen.has(svg))return;seen.add(svg);io.unobserve(svg);if(!skip(svg))mount(svg)})},{rootMargin:'400px'});
  function scan(){var l=document.querySelectorAll('svg');for(var i=0;i<l.length;i++)if(!seen.has(l[i])&&!S.has(l[i]))io.observe(l[i])}
  var rs;addEventListener('resize',function(){clearTimeout(rs);rs=setTimeout(function(){all.forEach(soon)},250)});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',scan);else scan();
  addEventListener('load',function(){scan();setTimeout(function(){scan();all.forEach(soon)},1500)});
  var sm;new MutationObserver(function(){if(sm)return;sm=setTimeout(function(){sm=null;scan()},300)}).observe(document.body||root,{childList:true,subtree:true});
  document.addEventListener('toggle',function(e){var d=e.target;if(d&&d.open)all.forEach(function(s){if(d.contains(s))draw(s)})},true);
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(function(){all.forEach(soon)});
})();
