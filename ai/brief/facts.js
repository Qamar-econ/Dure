// Turns the register into the facts table the brief writer reads. Every number the writer may use is in `allowed`.
const S = require('../../site/src/sheet_core.js'), D = require('../../site/src/sheet_data.json');
const crypto = require('crypto'), fs = require('fs');
const r = S.compute(D), sig = r.signals, mk = r.market.filter(m => !m.demo), reg = r.register, tr = r.trades.filter(t => !t.demo);
const allowed = new Set(), add = v => { if (v == null || isNaN(v)) return v; const n = +(+v).toFixed(2); allowed.add(n); allowed.add(Math.abs(n)); return v; };
const L = [];
L.push(`REGISTER: Letefoho coffee pool, 3 weekly periods, 6 auctions (2 per week). Today is Monday 27 July 2026. Rain fell ${S.fmtD(D.rain[0])} to ${S.fmtD(D.rain[1])} (pool records, not a weather station).`);
[13, 15, 27, 1, 2, 3, 6, 5].forEach(add);
L.push('\nVILLAGE SIGNALS (per village per week; percentages are shares of that village-week\'s offers)');
L.push('village | week | offers | kg_per_offer | kg_per_offer_change_vs_week1_% | mould_% | insect_% | drying_% | debris_% | gradeC_% | sat_out_% | photo_vs_inspector_disagree_%');
for (const s of sig) { L.push([s.village, s.week, s.offers, s.kg_per_offer, s.vs_week1, s.mould, s.insect, s.drying, s.debris, s.gradeC, s.sat_out, s.ai_disagree].map(add).join(' | ')); }
L.push('\nAUCTIONS (USD per kg of parchment)');
L.push('date | week | farms | kg_offered | kg_sold | winning_lot_bid | bids | price_A | price_B | price_C | farmers_median_minimum | farms_sat_out | total_paid_usd');
for (const m of mk) L.push([S.fmtD(m.date), m.week, m.farms, m.kg_offered, m.kg_sold, m.best_bid.toFixed(2), m.bids, m.A.toFixed(2), m.B.toFixed(2), m.C.toFixed(2), m.median_ask.toFixed(2), m.sat_out, m.paid.toFixed(2)].map(v => (add(+v), v)).join(' | '));
mk.forEach(m => { add(+m.date.slice(8)); add(+(m.median_ask - m.best_bid).toFixed(2)); });
const consent = reg.filter(x => x.consent === 'Y').length, noSale = reg.filter(x => x.sales === 0).length;
const pc = (a, b) => b ? Math.round(100 * a / b) : 0;
const dis = pc(tr.filter(t => t.matched === 'no').length, tr.length), byModel = pc(tr.filter(t => t.read_by === 'model').length, tr.length), tet = pc(tr.filter(t => t.lang === 'TET').length, tr.length);
L.push(`\nREGISTER TOTALS: ${reg.length} farmers; ${consent} agreed to be named to the ministry; ${noSale} have offered but not yet sold; ${tr.length} offers in total.`);
L.push(`MESSAGES AND PHOTOS: ${tet}% of messages in Tetum; the small model read ${byModel}% of messages, rules read ${100 - byModel}%; the photo grade differed from the inspector's on ${dis}% of offers (inspector's grade is paid).`);
[reg.length, consent, reg.length - consent, noSale, tr.length, tet, byModel, 100 - byModel, dis].forEach(add);
// per-village week-3 sat-out counts, as counts (the writer may say "7 of 10")
const lastW = Math.max(...sig.map(s => s.week));
L.push(`\nWEEK ${lastW} SAT-OUT COUNTS (offers whose minimum was above the price their grade fetched)`);
for (const v of [...new Set(sig.map(s => s.village))]) {
  const T = tr.filter(t => t.village === v && Math.floor(t.auction / 2) + 1 === lastW), n = T.filter(t => t.status !== 'in').length;
  L.push(`${v}: ${n} of ${T.length}`); add(n); add(T.length);
}
// "other villages" pooled, so the writer can compare one village with the rest
for (const v of [...new Set(sig.map(s => s.village))]) {
  const O = tr.filter(t => t.village !== v && Math.floor(t.auction / 2) + 1 === lastW);
  add(pc(O.filter(t => /black\/mould/.test(t.flags)).length, O.length));
}
L.push(`POOLED: mould share in week ${lastW} for all villages except each one: ` + [...new Set(sig.map(s => s.village))].map(v => { const O = tr.filter(t => t.village !== v && Math.floor(t.auction / 2) + 1 === lastW); return `without ${v} ${pc(O.filter(t => /black\/mould/.test(t.flags)).length, O.length)}%`; }).join('; '));
const text = L.join('\n'), hash = crypto.createHash('sha256').update(JSON.stringify(D)).digest('hex').slice(0, 12);
fs.writeFileSync(__dirname + '/facts.json', JSON.stringify({ hash, villages: [...new Set(sig.map(s => s.village))], allowed: [...allowed].sort((a, b) => a - b), text }, null, 1));
console.log(text); console.log('\nallowed numbers:', allowed.size, 'hash', hash);
