const DureAI=(()=>{
  const HANGUL=/[^\s\S]/; // never matches: no Hangul in this build
  const norm=s=>s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').normalize('NFC').replace(/[’'`]/g,'');
  const lev=(a,b)=>{const m=a.length,n=b.length;if(Math.abs(m-n)>2)return 9;const d=Array.from({length:m+1},(_,i)=>[i]);for(let j=1;j<=n;j++)d[0][j]=j;
    for(let i=1;i<=m;i++)for(let j=1;j<=n;j++)d[i][j]=Math.min(d[i-1][j]+1,d[i][j-1]+1,d[i-1][j-1]+(a[i-1]===b[j-1]?0:1));return d[m][n]};
  const LEX={
    coffee:['coffee','coffe','cofee','kofi','kafe','kafeh','cafe','kopi','parchment','perchment','pergaminho'],
    other:['potato','potatoes','batata','cabbage','repolho','tomato','tomatoes','tomate','onion','cebola','corn','milho','maize','rice','foos','vegetables','modo'],
    unit:['kg','kgs','kilo','kilos','kilu','kilus','quilo','quilos','kilogram','kilograms','kilograma'],
    cent:['sentavu','sentavus','sentavos','centavos','sen','cent','cents','c','ct'],
    dollar:['dollar','dollars','dolar','usd'],
    sell:['fan','faan','sell','selling','sale','hakarak','want'],
    priceW:['folin','presu','harga','price','minimu','minimum','min','least','lowest'],
    good:['diak','good','nice','great','clean','furak','kapaas','moos','mos'],
    mid:['normal','regular','ok-ish','mediu','average','notbad','soso'],
    bad:['aat','bad','poor','damaged','broken','wet','mouldy','moldy','mould','fuhuk','dodok','bokon','rotten'],
    very:['los','loos','very','really'],
    greet:['bondia','botarde','bonoite','hello','hi','hey'],
    any:['any','anything','whatever','laimporta'],
  };
  const LANGW={tet:['bondia','botarde','bonoite','diak','los','fan','faan','sentavu','kilu','kafe','bele','hau','ha','ita','ami','nia','nee','neebe','hakarak','atu','folin','presu','aat','obrigadu','laimporta','loos','lae','furak','iha','ho','no','ba','moos','mos','dolar','deit','mak','sei','simu','hatene','uitoan','barak','balun','maran','metan','bokon','fuhuk','minimu','tinan','ohin','aban','maun','mana','kilograma','sin','sim','sentavos','centavos','hotu-hotu','uluk','hein','saida','hira','ruma','leten',
      /* v2 question / chat words */ 'ajuda','udan','tempu','dalan','kamioneta','kareta','osan','selu','tama','ona','seidauk','bainhira','oinsa','tuku','mai','ka','favor','favór','obrigada','botarde','ida','iha','husi','fulan','kotuk','sae','tun','uza','lori','saku','dure'],
    en:['coffee','grade','quality','sell','selling','good','bad','price','cents','hello','hi','want','very','have','of','the','yes','no','any','not','clean','parchment','i','my','is','it','and','for','but','some','about','around','fine','go','ahead','nope','yep','thanks','please','lowest','per','take','sorry','can','dry','wet','kilos','minimum','morning','quality','sure','whatever','dollar','dollars','okay','ok',
      /* v2 question / chat words */ 'help','weather','rain','raining','road','truck','pickup','pick','up','paid','pay','paying','payment','money','when','where','what','whats','how','much','tell','me','did','do','does','today','todays','tomorrow','now','thank','thanks','you','u','work','get','will','come','coming','time','week','this','buyers','are','price','prices','pls','hi','hello','need','number','arrived','receive','sacks','sack','drop','leave','who','or','last','again','nah','wait','forecast','send','evening','lot']};
  const PREF=w=>{if(!HANGUL.test(w))return null;for(const k in LEX)for(const x of LEX[k])if(HANGUL.test(x)&&x.length>=2&&w.startsWith(x))return {k,fixed:x===w?null:x};return null};
  /* common words one letter away from a lexicon word ("would" ~ "mould") that must never be spell-fixed */
  const NOFUZZ=['would','could','should','there','where','these','those','which','while','about','pick','price'];
  function find(tok){
    for(const k in LEX){if(LEX[k].includes(tok))return {k,fixed:null}}
    const p=PREF(tok);if(p)return p;
    if(tok.length>=5&&!HANGUL.test(tok)&&!NOFUZZ.includes(tok))for(const k of ['coffee','other','unit','cent','sell','good','bad','any','priceW']){for(const w of LEX[k]){if(w.length<4||HANGUL.test(w))continue;const d=lev(tok,w);if(d<=(w.length>=6?2:1))return {k,fixed:w}}}
    return null;}
  const YES=['yes','y','ya','yeah','yep','sure','ok','okay','loos','ls','sin','sim'], NO=['no','n','nope','lae','nah'];

  /* v2.1: yes / no replies to "sell now?" (expect=decide). Phrase-level, with negation: "la diak", "la bele", "seidauk" are no; "diak", "bele", "konkorda" are yes. */
  function yesNo(text){
    const s=' '+norm(text).replace(/[^a-z0-9' ]+/g,' ').replace(/\s+/g,' ').trim()+' ';
    const NOP=[/ (la|lae|laos|la'os) (bele|diak|di'ak|hakarak|konkorda|simu|fan|aseita|aceita|lae) /,/ labele /,/ ladiak /,/ seidauk /,/ keta (fan|faan) /,/ hein (uluk|lai|tan) /,/ (no|nope|nah|not now|not yet|not at|not for|not this|not that|dont|don't|do not|wait|later|cancel|stop|never) /,/ (tidak|tdk|nggak|gak|belum|jangan) /,/ (nao|não) /,/ lae /,/ la /,/ n /];
    const YESP=[/ (loos|los|lo'os|ls|sin|sim|siin|yes|ya|yah|yeah|yep|yup|ok|oke|okay|okey|k|sure|fine|deal|agree|agreed|go|sell|confirm|confirmed|aseita|aceita|aceito|konkorda|konkordu|setuju|iya|boleh|bele|diak|di'ak|simu) /];
    let no=NOP.some(r=>r.test(s)); let yes=YESP.some(r=>r.test(s.replace(/ (la|lae|laos|la'os|not|dont|don't|do not) (bele|diak|di'ak|hakarak|konkorda|simu|fan|aseita|aceita|sell|go|agree|ok) /g,' ')));
    /* "lae obrigadu" / "no thanks" = no; "ok lae" is a contradiction -> unsure */
    if(no&&yes)return null; return yes?'yes':no?'no':null;}
  /* number words people text in Timor-Leste: Tetum, plus the Indonesian, Portuguese and English ones they mix in */
  const NW={sanulu:10,ruanulu:20,tolunulu:30,haatnulu:40,limanulu:50,neennulu:60,hitunulu:70,ualunulu:80,sianulu:90,
    ten:10,twenty:20,thirty:30,forty:40,fourty:40,fifty:50,sixty:60,seventy:70,eighty:80,ninety:90,
    vinte:20,trinta:30,quarenta:40,cinquenta:50,sessenta:60,setenta:70,oitenta:80,noventa:90,cem:100};
  const ID_UNITS={dua:2,tiga:3,empat:4,lima:5,enam:6,tujuh:7,delapan:8,sembilan:9};
  const TET_UNITS={ida:1,rua:2,tolu:3,haat:4,lima:5};
  function words2num(t){
    t=t.replace(/\b(dua|tiga|empat|lima|enam|tujuh|delapan|sembilan)\s+puluh\b/g,(m,a)=>String(ID_UNITS[a]*10)).replace(/\bseratus\b/g,'100');
    t=t.replace(/\b(one|two|three)\s+(dollar|dollars|dolar)\b/g,(m,a,b)=>({one:1,two:2,three:3})[a]+' '+b);   /* "one dollar twenty" */
    t=t.replace(/\batus\s+(ida|rua|tolu|haat|lima)\b/g,(m,a)=>String(TET_UNITS[a]*100)).replace(/\b(a|one)\s+hundred\b/g,'100');
    return t.replace(/\b[a-z]+\b/g,w=>NW[w]!==undefined?String(NW[w]):w);
  }
  /* "1 dolar 45 sentavu", "1 dollar 25", "1 dolar" -> "$1.45" */
  function money(t){
    t=t.replace(/(?<![\d.])(\d{1,2})\s*(?:dolar|dollar|dollars|dolares)\s+(\d{1,2})\b(?:\s*(?:sentavu|sentavus|sentavos|centavos|cents?|sen|c)\b)?/g,(m,d,c)=>` $${d}.${c.padStart(2,'0')} `);
    return t.replace(/(?<![\d.])(\d{1,2})\s*(?:dolar|dollar|dollars|dolares)\b(?!\s*\d)/g,(m,d)=>` $${d} `);
  }
  /* whole messages in a language Dure doesn't read yet (code-switched words alone don't count) */
  const FOREIGN=['saya','mau','jual','berapa','selamat','pagi','siang','sore','bagus','tolong','kirim','hari','ini','ada','boleh','saja','kualitas','terima','kasih',
    'bom','boa','vendo','quero','vender','tenho','para','preco','obrigado','ate','seco','dolares','quilos','minimo','nina','kahawa','nzuri','habari','sabini'];
  /* v2: what the farmer is ASKING (not offering). Topics in a fixed order; a message can ask several. */
  const QTOPICS=['price','weather','pickup','pay','help'];
  const QW={
    priceWord:/\b(price|prices|presu|folin|harga|rate|cost)\b/,
    priceStrong:/\b(how much|how many dollars|hira|what|whats|tell|hatene|know|saida|check)\b/,
    priceWeak:/\b(today|todays|now|current|latest|ohin|week|pls|please|\?)/,
    payForPrice:/\b(paying|(buyers?|they|others|people) pay|pay for|pay per)\b/,
    weather:/\b(weather|forecast|rain|raining|rains|rainy|udan|tempu|klima|road|roads|dalan|storm|flood|floods|landslide)\b/,
    pickup:/\bpick (it|them|\w+) up\b|\b(pick ?up|pickups|collect|collection|truck|trucks|kamioneta|kareta|drop|deliver|delivery|bring)\b|\btuku hira\b|\bsakus?\b.*\b(neebe|where|bainhira|when)\b|\b(neebe|where|bainhira|when)\b.*\bsakus?\b/,
    pay:/\b(paid|payment|payments|money|osan|selu|transfer|transferred|receive|received|cash)\b|\b(pay me|get pay|you pay me|when pay)\b/,
    helpStrong:/\b(help|ajuda|ajudu)\b/,
    helpWeak:/\b(how does|how do i|how to|how it works|what can i|who is this|who are you|what is (dure|this)|dure saida|saida mak dure|ida nee saida)\b|\boinsa( \w+){0,3} (fan|uza|sell)\b/,
  };
  const QFIX={hw:'how',wen:'when',wat:'what',wats:'whats',wht:'what',payed:'paid',pyd:'paid',pric:'price',tmrw:'tomorrow',tmr:'tomorrow',wheather:'weather'};
  const QKEYS=['weather','pickup','price','money','payment','kamioneta','tomorrow','raining','truck','ajuda','folin','bainhira'];
  const QKEEP=['prices','trucks','pickups','paying','payments','coffee','where','there','three','taken'];
  /* questions(text, offer) -> ['price',...] or null. offer = {ask, any} from the parse, so "price 1.20" stays an offer */
  function questions(text,offer){
    /* light spelling repair for question words ("wether", "pikup", "prise", "payed", "wen"); any repair makes the reading not sure */
    let qfix=false;
    const s=norm(text).replace(/[“”"]/g,' ').replace(/[a-z]+/g,w=>{
      if(QFIX[w]){qfix=true;return QFIX[w]}
      if(w.length>=5&&!QKEEP.includes(w))for(const k of QKEYS){if(w!==k&&lev(w,k)<=1){qfix=true;return k}}
      return w});
    offer.qfix=qfix;
    const clauses=s.split(/(?<=[.!;\n?])|,(?!\d)/).map(c=>c.trim()).filter(Boolean);
    const found=new Set();
    const osanHira=/\bosan hira\b/.test(s);
    const unsure=/\b(not sure|dont know|la hatene|no idea)\b[^?]*\bhow much\b/.test(s)&&!/\?/.test(s);   /* "not sure how much yet" is not a question */
    if((/\bhow much\b/.test(s)&&!unsure)||osanHira||(/\bhira\b/.test(s)&&!/\btuku hira\b/.test(s)&&!/\bhira deit\b/.test(s))||QW.payForPrice.test(s))found.add('price');
    for(const c of clauses){
      if(!QW.priceWord.test(c)||offer.any)continue;
      const hasNum=/\d/.test(c), sellW=/\b(fan|faan|sell|selling|sale|minimu|minimum|min|lowest|least)\b/.test(c);
      if(QW.priceStrong.test(c)&&!(hasNum&&!/\?|what|whats|how much|hira/.test(c)))found.add('price');
      else if(!hasNum&&!sellW)found.add('price');     /* "coffee price today?", "price of coffee pls", "folin kafe?" */
    }
    /* inside an offer ("wet coffee 70kg rain", "i can bring 50kg"), a topic word counts only in a clause that asks something */
    const isOffer=offer.kg!==null||offer.ask!==null||offer.any;
    const CUE=/\?|\b(when|where|what|whats|how|did|has|is|will|tell|any news|bainhira|neebe|oinsa|hira|saida|ka lae|ka seidauk|ona)\b/;
    const topic=re=>isOffer?clauses.some(c=>re.test(c)&&CUE.test(c)):re.test(s);
    if(topic(QW.weather))found.add('weather');
    if(topic(QW.pickup))found.add('pickup');
    if(topic(QW.pay)&&!(osanHira&&!/\b(paid|selu|tama|transfer|receive)\b/.test(s)))found.add('pay');
    if(QW.helpStrong.test(s)||(found.size===0&&QW.helpWeak.test(s)))found.add('help');
    const q=QTOPICS.filter(t=>found.has(t));
    return q.length?q:null;
  }
  /* v2: reply(q, lang, ctx) -> SMS text answering the questions, one line per topic (<= 2 lines kept short for SMS).
     ctx (all optional, filled by the site/back end): {price:'1.32', priceDate:'4 Oct', weather:'Rain likely tomorrow afternoon',
     pickup:'Thursday 9:00 at Letefoho market', paid:true|false|null, paidAmount:'$52.80'} */
  const REPLY={
    en:{price:c=>c.price?`Coffee today: buyers paid about $${c.price}/kg${c.priceDate?' ('+c.priceDate+')':''}.`:'Today\'s coffee price is not in yet. We will text you.',
        weather:c=>c.weather?`Weather: ${c.weather}.`:'No weather update yet. We will text you if rain is coming.',
        pickup:c=>c.pickup?`Pickup: ${c.pickup}.`:'Pickup day is set when your group\'s sacks are sold. We will text you.',
        pay:c=>c.paid===true?`Paid: ${c.paidAmount||'your money'} was sent.`:c.paid===false?'Not paid yet. Money goes to your wallet after the Thursday hand check.':'We will text you as soon as your money is sent.',
        help:()=>'Dure sells your coffee with your neighbours. Text e.g. "coffee 50 kg A 2.60". Ask "price", "pickup", "paid".'},
    tet:{price:c=>c.price?`Folin kafe ohin: kilu ida $${c.price}${c.priceDate?' ('+c.priceDate+')':''}.`:'Folin ohin nian seidauk iha. Ami haruka SMS.',
        weather:c=>c.weather?`Tempu: ${c.weather}.`:'Seidauk iha informasaun tempu. Ami haruka SMS se udan atu mai.',
        pickup:c=>c.pickup?`Pickup: ${c.pickup}.`:'Loron pickup sei hatene bainhira grupu nia kafe fan ona. Ami haruka SMS.',
        pay:c=>c.paid===true?`Selu ona: ${c.paidAmount||'ita nia osan'} haruka ona.`:c.paid===false?'Seidauk selu. Osan tama ba ita nia karteira depois verifikasaun Kinta.':'Ami haruka SMS bainhira osan haruka ona.',
        help:()=>'Dure fan ita nia kafe hamutuk ho viziñu sira. Haruka: "kafe 50 kilu A 2.60". Husu "folin", "pickup", "osan".'}};
  function reply(q,lang,ctx){const R=REPLY[lang==='tet'?'tet':'en'];return (q||[]).map(t=>R[t]?R[t](ctx||{}):'').filter(Boolean).join('\n')||null}
  const ANYPAIR=[['saida','deit'],['hira','deit'],['ruma','deit'],['neebe','deit'],['hotu-hotu','ok'],['any','price'],['simu','hotu']];
  const CJK=/[\u3040-\u30FF\u3400-\u9FFF\uAC00-\uD7A3]/;
  function parse(text,expect){
    let t=norm(text).replace(/(\d)\s*,(\d{1,2})(?!\d)/g,'$1.$2');
    t=t.replace(/(\d)\s*\/\s*(kgs?|kilos?|kilus?)\b/g,'$1 per');   /* "$1.50/kg" is a price per kilo, not 1.5 kg (fix added after test 4; see RESULTS.md) */
    const LB={tet:0,en:0};t.split(/[^a-z-]+/).forEach(w=>{if(['sanulu','ruanulu','tolunulu','haatnulu','limanulu','neennulu','hitunulu','ualunulu','sianulu','atus','dolar','sentavu','sentavus','sentavos','centavos','sen'].includes(w))LB.tet++;
      if(['ten','twenty','thirty','forty','fourty','fifty','sixty','seventy','eighty','ninety','hundred','dollar','dollars','cents'].includes(w))LB.en++});
    t=money(words2num(t));
    t=t.replace(/(\d+(?:\.\d+)?)([a-z\uAC00-\uD7A3]+)/g,'$1 $2').replace(/\$\s*/g,' $ ');
    const toks=t.split(/[^a-z0-9.$\uAC00-\uD7A3-]+/).map(x=>x.replace(/\.+$/,'')).filter(Boolean);
    const joined=[];for(let i=0;i<toks.length;i++){const two=toks[i]+(toks[i+1]||'');if(['laimporta','notbad','soso'].includes(two)){joined.push(two);i++}else joined.push(toks[i])}
    const out={lang:null,crop:null,other:null,kg:null,grade:null,ask:null,any:false,yes:false,no:false,fixes:[],spans:{},hits:0};
    const score={tet:LB.tet,en:LB.en};let letters=false,foreign=0;
    const tags=joined.map(w=>{const num=/^\d*\.?\d+$/.test(w)?parseFloat(w):null;const hit=num===null&&w!=='$'?find(w):null;
      if(num===null&&w!=='$'&&!(hit&&hit.k==='unit'))letters=true;if(hit&&hit.k!=='unit')out.wordHits=(out.wordHits||0)+1;if(YES.includes(w)||NO.includes(w))out.wordHits=(out.wordHits||0)+1;
      for(const L in LANGW)if(LANGW[L].includes(w)||(hit&&hit.fixed&&LANGW[L].includes(hit.fixed)))score[L]++;
      if(FOREIGN.includes(w))foreign++;
      if(hit)out.hits++;return {w,num,hit,dollar:w==='$'}});
    let q=null,very=false;const add=(k,w)=>{out.spans[k]=(out.spans[k]||[]).concat(w)};
    const units=tags.filter(x=>x.num!==null).length;
    tags.forEach((g,i)=>{const nx=tags[i+1],pv=tags[i-1];
      if(YES.includes(g.w)){out.yes=true;out.hits++}if(NO.includes(g.w)){out.no=true;out.hits++}
      if(pv&&ANYPAIR.some(([a,b])=>pv.w===a&&g.w===b))out.any=true;
      if(g.w==='grade'&&nx&&/^[abc]$/.test(nx.w)){q=nx.w.toUpperCase();add('grade',[g.w,nx.w])}
      if(g.hit){const k=g.hit.k;if(g.hit.fixed)out.fixes.push(`${g.w} → ${g.hit.fixed}`);
        if(k==='coffee'){out.crop='coffee';add('crop',g.w)}
        if(k==='other')out.other=g.hit.fixed||g.w;
        if(k==='very'){very=true;add('grade',g.w)}
        if(k==='good'&&!(pv&&(pv.w==='not'||pv.w==='no'||pv.w==='la'||pv.w==='dia'||pv.w==='bondia'))){q='A';add('grade',g.w)}
        if(k==='good'&&pv&&pv.w==='la'){q='C';add('grade',g.w)}
        if(k==='mid'){q='B';add('grade',g.w)}
        if(k==='bad'){q=(pv&&pv.w==='not')?'B':'C';add('grade',g.w)}
        if(k==='any')out.any=true;}
      /* defects: a few dark beans is B, many is C */
      if(g.w==='metan'||g.w==='black'){const few=(nx&&['uitoan','balun'].includes(nx.w))||(pv&&['some','few','a'].includes(pv.w));
        const many=(nx&&['barak','hotu'].includes(nx.w))||(pv&&['lots','many','lot'].includes(pv.w))||tags.slice(Math.max(0,i-2),i).some(x=>x.w==='lots'||x.w==='many');
        q=many?'C':few?'B':(q||'B');add('grade',g.w)}
      if(g.num!==null){
        const unit=nx&&nx.hit&&nx.hit.k==='unit', cent=nx&&nx.hit&&nx.hit.k==='cent', dol=(pv&&pv.dollar)||(nx&&(nx.dollar||nx.hit&&nx.hit.k==='dollar'));
        const priceCtx=tags.slice(Math.max(0,i-3),i).some(x=>x.hit&&(x.hit.k==='sell'||x.hit.k==='priceW'))||(pv&&pv.hit&&pv.hit.k==='priceW');
        const dec=/\./.test(g.w);
        const unitBefore=pv&&pv.hit&&pv.hit.k==='unit'&&!dec&&g.num>=5&&!(nx&&nx.hit&&nx.hit.k==='unit');   // Tetum order: "kilu 40"
        const nearCoffee=tags.slice(Math.max(0,i-3),i).some(x=>x.hit&&x.hit.k==='coffee');
        if(unit){if(out.kg===null||nearCoffee){out.kg=g.num;add('kg',[g.w,nx.w])}}
        else if(unitBefore&&out.kg===null){out.kg=g.num;add('kg',[pv.w,g.w])}
        else if(cent){out.ask=+(g.num/100).toFixed(2);add('ask',[g.w,nx.w])}
        else if(dol){out.ask=g.num;add('ask',[g.w])}
        else if(dec&&g.num<5){out.ask=g.num;add('ask',[g.w])}
        else if(expect==='ask'&&out.ask===null&&g.num<5){out.ask=g.num;add('ask',[g.w])}
        else if(expect==='ask'&&out.ask===null&&g.num>=50&&g.num<500){out.ask=+(g.num/100).toFixed(2);add('ask',[g.w])}   // "140" = 140 cents
        else if(expect==='kg'&&out.kg===null){out.kg=g.num;add('kg',[g.w])}
        else if(priceCtx&&g.num>=50&&g.num<500&&!dec&&(out.kg!==null||tags.some((x,j)=>j>i&&x.num!==null))){out.ask=+(g.num/100).toFixed(2);add('ask',[g.w])}
        else if(out.kg===null&&g.num>=5){out.kg=g.num;add('kg',[g.w]);out.fixes.push(`${g.w} → ${g.w} kg (assumed)`)}
        else if(priceCtx&&g.num>=50&&g.num<500){out.ask=+(g.num/100).toFixed(2);add('ask',[g.w])}
        if(out.kg!==null||out.ask!==null)out.hits++;
      }});
    if(q)out.grade=q;
    /* v2.1: grade sent as a letter: "40kg A", "grade B", "B grade", "kualidade C", "klase A", "A-grade", "kafe A 1.40" */
    {const raw=' '+text.replace(/[,;:!()\/]+/g,' ').replace(/\s+/g,' ')+' ';
     const QW='(?:grade|grd|gr|quality|qualty|kualidade|kualidadi|kualitas|qualidade|grau|klase|class|kategoria|tipu|type)';
     let m=raw.match(new RegExp(QW+'\\s*[-:]?\\s*([abcABC])(?![a-z])','i'))||raw.match(new RegExp('(?:^|\\s)([abcABC])\\s*-?\\s*'+QW+'\\b','i'));
     if(!m)m=raw.match(/(?:^|\s)([ABC])(?=\s|\.|$)/);   /* a capital letter on its own */
     if(!m&&(out.kg!==null||out.crop||out.ask!==null||expect==='grade'))m=raw.match(/(?:\d\s*(?:kg|kgs|kilo|kilos|kilu|kilus|quilo)|kafe|kopi|coffee|cafe)\s+([bc])(?=\s|\.|$)/i)||(expect==='grade'?raw.match(/^\s*([abc])\s*\.?\s*$/i):null);
     if(m){out.grade=m[1].toUpperCase();out.hits++;add('grade',m[1]);out.letterGrade=true}}
    if(out.any)out.ask=out.ask??null;
    const best=Object.entries(score).sort((a,b)=>b[1]-a[1])[0];
    out.lang=best[1]>0?best[0]:null;
    const own=score.tet+score.en;
    out.unknown=CJK.test(text)||(foreign>=2&&foreign>own)||(letters&&!out.wordHits&&best[1]===0&&!(expect&&units));
    if(!out.unknown&&!out.lang&&letters&&expect&&units)out.lang=null;
    /* sure = the rules engine answers on its own; otherwise the small model is asked (when it's reachable) */
    const nums=tags.filter(x=>x.num!==null).length;
    /* sure only if every word was recognised: a known word, a language marker, a greeting, yes/no or a number */
    const known=w=>/^[\d.$]+$/.test(w)||YES.includes(w)||NO.includes(w)||FOREIGN.includes(w)||Object.values(LANGW).some(L=>L.includes(w))||!!find(w)||['a','b','c','of','the','and','per','is','ok','pls','please','obrigadu','obrigada','grade','kualidade','klase','quality','grau'].includes(w);
    const unknownWords=joined.filter(w=>!known(w)).length;
    out.sure=out.unknown?(CJK.test(text)||foreign>=2):(!out.fixes.length&&unknownWords===0&&nums<=2&&(out.lang!==null||(!!expect&&nums>0&&!letters)));
    /* v2: questions. A message that only asks (no kilos, no price, no "sell") is not an offer, so drop crop and grade. */
    /* "diak obrigada" (fine, thanks): a quality word with no crop, kilos or price is chat, not a grade */
    if(out.grade&&!out.letterGrade&&!out.crop&&!out.other&&out.kg===null&&out.ask===null&&!/\b(kualidade|quality|grade|grau)\b/.test(norm(text)))out.grade=null;
    out.q=questions(text,out);
    if(out.qfix){out.fixes.push('question word spelling');out.sure=false}
    if(out.q&&out.kg===null&&out.ask===null&&!out.any&&!tags.some(x=>x.hit&&x.hit.k==='sell')){out.crop=null;out.other=null;out.grade=null;out.spans={}}
    if(expect==='decide'){const yn=yesNo(text);out.yes=yn==='yes';out.no=yn==='no';const nt=norm(text);
      /* "not at that price", "lae, folin kiik liu": talking about the price while answering is not a price question */
      if(yn&&out.q&&out.q.length===1&&out.q[0]==='price'&&!/\?|how much|what|hira|saida|berapa/.test(nt))out.q=null;
      if(yn&&out.kg===null&&out.ask===null&&!out.q){out.sure=true;out.unknown=false;out.lang=/\b(lae|la|loos|los|sin|sim|diak|bele|labele|konkorda|seidauk|hein|keta|obrigadu|obrigada|simu|fan|faan|hau|aseita|aceita|deit|maun|mana|folin)\b/.test(nt)?'tet':'en'}}
    out.raw=text;return out;}
  return {parse,questions,reply,yesNo};
})();

const T=require(process.argv[3]||'./test.json');const out=T.map(t=>{const e=t.expect==='kg'?'kg':t.expect==='ask'?'ask':t.expect==='decide'?'decide':null;const p=DureAI.parse(t.msg,e);
 return {lang:p.unknown?'unknown':p.lang,crop:p.crop?'coffee':(p.other?'other':null),kg:p.kg,ask:p.ask,any:p.any,grade:p.grade,yn:t.expect==='decide'?(p.yes&&!p.no?'yes':p.no?'no':null):null,_sure:!!p.sure}});
require('fs').writeFileSync(process.argv[2]||'pred_rules.json',JSON.stringify(out));
