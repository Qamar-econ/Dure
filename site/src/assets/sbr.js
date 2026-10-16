/* Samsung Internet's dark mode repaints pages itself and ignores the page's color-scheme, so the light skies,
   clouds and cream in our drawn (inline SVG) illustrations turn dark grey and navy. It leaves images alone.
   On Samsung Internet only, each drawing is therefore shown as a picture of itself: the SVG is rendered into an
   image (as a background of the same element, so layout is untouched; words inside it keep their web font) and
   its own shapes are hidden. Ordinary page text keeps following the browser. A drawing that is still moving is
   pictured again once it settles; one that never stops (the demo map) is left as it is.
   ?sbr=1 forces this on for testing, ?sbr=0 turns it off. */
(function(){
  var q=location.search;
  var on=/SamsungBrowser/i.test(navigator.userAgent)||/[?&]sbr=1\b/.test(q);
  if(!on||/[?&]sbr=0\b/.test(q))return;
  var root=document.documentElement;root.classList.add('sbr');
  var css=document.createElement('style');
  css.textContent='.sbr svg.sbr-pic>*{visibility:hidden!important}'+
    '.sbr svg.sbr-pic{background-repeat:no-repeat;background-size:100% 100%}'+
    /* words laid over a drawing get a soft plate in dark mode, so they stay readable whatever colour the browser gives them */
    '@media (prefers-color-scheme:dark){.sbr .hero .htxt .tag,.sbr .hero .htxt .def,.sbr #hero .tag,.sbr #hero .def{background:rgba(242,234,218,.78);border-radius:10px;box-shadow:0 0 0 6px rgba(242,234,218,.78);-webkit-box-decoration-break:clone;box-decoration-break:clone}}';
  document.head.appendChild(css);
  var NS='http://www.w3.org/2000/svg';
  var PROPS=['fill','stroke','stroke-width','stroke-dasharray','stroke-linecap','stroke-linejoin','opacity','fill-opacity','stroke-opacity','stop-color','stop-opacity','visibility','display','transform','transform-origin','mix-blend-mode',
             'font-family','font-size','font-weight','font-style','letter-spacing','text-anchor','dominant-baseline','font-variation-settings'];
  var DEF={'opacity':'1','fill-opacity':'1','stroke-opacity':'1','stop-opacity':'1','visibility':'visible','transform':'none','mix-blend-mode':'normal','stroke-dasharray':'none','letter-spacing':'normal','font-variation-settings':'normal','dominant-baseline':'auto','text-anchor':'start','stroke-linecap':'butt','stroke-linejoin':'miter'};
  /* ---- web fonts, embedded so words inside a picture look the same ---- */
  var faces=null,fontData={};
  function loadFaces(){if(faces)return faces;
    var links=[].slice.call(document.querySelectorAll('link[rel=stylesheet][href*="fonts.googleapis.com"]'));
    faces=Promise.all(links.map(function(l){return fetch(l.href).then(function(r){return r.text()}).catch(function(){return ''})})).then(function(all){
      var out=[];all.join('\n').replace(/\/\*\s*([\w-]+)\s*\*\/\s*@font-face\s*{([^}]*)}/g,function(_,sub,body){
        if(sub!=='latin'&&sub!=='latin-ext')return;var fam=(body.match(/font-family:\s*['"]?([^;'"]+)/)||[])[1],url=(body.match(/url\(([^)]+)\)/)||[])[1];
        if(fam&&url)out.push({fam:fam.trim(),url:url.replace(/['"]/g,''),body:body})});return out});
    return faces}
  function dataUrl(u){if(!fontData[u])fontData[u]=fetch(u).then(function(r){return r.blob()}).then(function(b){return new Promise(function(ok){var fr=new FileReader();fr.onload=function(){ok(fr.result)};fr.readAsDataURL(b)})}).catch(function(){return null});return fontData[u]}
  function fontCss(fams){if(!fams.length)return Promise.resolve('');
    return loadFaces().then(function(list){var use=list.filter(function(f){return fams.some(function(x){return x.toLowerCase().indexOf(f.fam.toLowerCase())>=0})});
      return Promise.all(use.map(function(f){return dataUrl(f.url).then(function(d){return d?'@font-face{'+f.body.replace(/url\([^)]+\)/,'url('+d+')')+'}':''})}))}).then(function(a){return a.join('')})}
  function skip(svg){
    if(svg.parentElement&&svg.parentElement.closest('svg'))return true;   // a drawing inside another drawing cannot carry a background
    if(svg.querySelector('foreignObject'))return true;
    var r=svg.getBoundingClientRect();if(r.width<56||r.height<48)return true;   // logos and icons: small, and they change colour with the header
    if(svg.closest('button'))return true;
    return false}
  var timers=new WeakMap(),gen=new WeakMap();
  function live(svg){clearTimeout(timers.get(svg));svg.classList.remove('sbr-pic');svg.style.backgroundImage='';svg.removeAttribute('data-sbr');svg.dataset.sbrLive='1'}
  function picture(svg){if(svg.dataset.sbrLive)return;
    var r=svg.getBoundingClientRect();if(!r.width||!r.height)return;
    var my=(gen.get(svg)||0)+1;gen.set(svg,my);
    var had=svg.classList.contains('sbr-pic');if(had)svg.classList.remove('sbr-pic');   // read the shapes as they really are, not as hidden
    var c=svg.cloneNode(true),src=[svg].concat([].slice.call(svg.querySelectorAll('*'))),dst=[c].concat([].slice.call(c.querySelectorAll('*'))),fams=[];
    for(var i=0;i<src.length;i++){var cs=getComputedStyle(src[i]),st='',isT=/^(text|tspan|textPath)$/.test(src[i].tagName);
      for(var k=0;k<PROPS.length;k++){var p=PROPS[k];if(!isT&&p.indexOf('font')===0&&p!=='font-size')continue;var v=cs.getPropertyValue(p);if(!v||v===DEF[p])continue;
        if(v.indexOf('url(')>=0)v=v.replace(/url\((['"]?)[^)#'"]*#([^)'"]+)\1\)/g,'url(#$2)');   // paint servers: keep the reference inside the picture
        v=v.replace(/"/g,"'");
        if(p==='transform-origin'&&cs.getPropertyValue('transform')==='none')continue;
        if(p==='font-family'&&fams.indexOf(v)<0)fams.push(v);
        st+=p+':'+v+';'}
      dst[i].setAttribute('style',st);dst[i].removeAttribute('class')}
    if(had)svg.classList.add('sbr-pic');
    /* shapes painted with patterns or gradients defined in another SVG on the page: bring those definitions along */
    var defs=null,guard=0,miss=function(){var ids=[],h=new XMLSerializer().serializeToString(c),re=/url\(#([^)'"]+)\)|href="#([^"]+)"/g,m;
      while((m=re.exec(h))){var id=m[1]||m[2];if(ids.indexOf(id)<0&&!c.querySelector('[id="'+id+'"]'))ids.push(id)}return ids};
    for(var ids=miss();ids.length&&guard<6;ids=miss(),guard++){ids.forEach(function(id){var el=document.getElementById(id);if(!el)return;
      if(!defs){defs=document.createElementNS(NS,'defs');c.insertBefore(defs,c.firstChild)}defs.appendChild(el.cloneNode(true))})}
    if(c.querySelector('image')){live(svg);return}   // an embedded photo cannot load inside a picture: keep this one as it is
    c.setAttribute('width',r.width);c.setAttribute('height',r.height);
    c.setAttribute('xmlns',NS);c.removeAttribute('style');
    fontCss(c.querySelector('text')?fams:[]).then(function(fc){if(gen.get(svg)!==my)return;   // a newer picture is on its way
      if(fc){var st=document.createElementNS(NS,'style');st.textContent=fc;c.insertBefore(st,c.firstChild)}
      var s=new XMLSerializer().serializeToString(c);
      svg.style.backgroundImage='url("data:image/svg+xml;charset=utf-8,'+encodeURIComponent(s).replace(/'/g,'%27')+'")';
      svg.classList.add('sbr-pic')})}
  function later(svg,ms){clearTimeout(timers.get(svg));timers.set(svg,setTimeout(function(){
    var go=function(){try{picture(svg)}catch(e){}};(window.requestIdleCallback||setTimeout)(go,{timeout:800})},ms))}
  /* a drawing that keeps changing for 8 s without a pause never settles (the demo map): leave it live */
  var seen=new WeakSet(),burst=new WeakMap();
  var mo=new MutationObserver(function(list){var done=new Set(),now=Date.now();
    for(var i=0;i<list.length;i++){var t=list[i].target,svg=t.closest?t.closest('svg[data-sbr]'):null;if(!svg||done.has(svg))continue;done.add(svg);
      var b=burst.get(svg);if(!b||now-b.last>500)b={start:now,last:now};b.last=now;burst.set(svg,b);
      if(now-b.start>8000){live(svg);mo2(svg);continue}later(svg,450)}});
  function mo2(svg){/* nothing more to watch on a live drawing */}
  /* a class switched on a section or the page (a theme change, a step of a story) can recolour a drawing: picture it again */
  var cm=new MutationObserver(function(list){var tg=[];list.forEach(function(m){if(tg.indexOf(m.target)<0)tg.push(m.target)});
    [].forEach.call(document.querySelectorAll('svg[data-sbr]'),function(svg){for(var i=0;i<tg.length;i++)if(tg[i]!==svg&&tg[i].contains(svg)&&!svg.contains(tg[i])){later(svg,350);break}})});
  cm.observe(document.documentElement,{subtree:true,attributes:true,attributeFilter:['class','data-theme','data-step']});
  var io=new IntersectionObserver(function(es){es.forEach(function(e){var svg=e.target;if(!e.isIntersecting)return;
    if(!seen.has(svg)){seen.add(svg);io.unobserve(svg);if(skip(svg))return;svg.setAttribute('data-sbr','');
      picture(svg);mo.observe(svg,{subtree:true,attributes:true,childList:true,characterData:true});
      later(svg,1600);setTimeout(function(){later(svg,0)},3800)}   // drawings that animate in: picture them again once settled
  })},{rootMargin:'300px'});
  function scan(){[].forEach.call(document.querySelectorAll('svg'),function(svg){if(!seen.has(svg))io.observe(svg)})}
  var rs;addEventListener('resize',function(){clearTimeout(rs);rs=setTimeout(function(){[].forEach.call(document.querySelectorAll('svg[data-sbr]'),function(s){later(s,0)})},300)});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',scan);else scan();
  addEventListener('load',function(){scan();setTimeout(scan,2000)});
  var sm;new MutationObserver(function(){if(sm)return;sm=setTimeout(function(){sm=null;scan()},700)}).observe(document.body||document.documentElement,{childList:true,subtree:true});
  /* a collapsed section that opens: its drawings get measured then */
  document.addEventListener('toggle',function(e){var d=e.target;if(d&&d.open)[].forEach.call(d.querySelectorAll('svg[data-sbr]'),function(s){later(s,200)})},true);
})();
