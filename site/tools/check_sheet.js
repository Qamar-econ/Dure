const S=require('../src/sheet_core.js');const D=require('../src/sheet_data.json');
const r=S.compute(D);
console.log(JSON.stringify(r.brief.headline));console.log(r.brief.facts);
r.brief.changed.concat(r.brief.prices,r.brief.register,r.brief.quality).forEach(b=>console.log('-',b.t));
console.table(r.market.map(m=>({d:m.date,farms:m.farms,kgO:m.kg_offered,kgS:m.kg_sold,in:m.farms_in,lot:m.best_bid,A:m.A,B:m.B,C:m.C,ask:m.median_ask,paid:m.paid})));
console.table(r.signals.filter(s=>s.week>0).map(s=>({v:s.village,w:s.week,n:s.offers,kg:s.kg_per_offer,vs:s.vs_week1,mould:s.mould,C:s.gradeC,sat:s.sat_out})));
const noor=r.trades.filter(t=>t.farmer==='LTF-041');console.log('Noor',noor.map(t=>[t.date,t.kg,t.grade,t.ask,t.price,t.status]));
