// Code lists every candidate finding with its numbers; the model chooses which matter and writes them up,
// citing finding ids. The checker then allows only the numbers of the findings a sentence cites.
const S = require('../../site/src/sheet_core.js'), D = require(process.env.DATA || '../../site/src/sheet_data.json');
const crypto = require('crypto'), fs = require('fs');
const r = S.compute(D), sig = r.signals, mk = r.market.filter(m => !m.demo), reg = r.register, tr = r.trades.filter(t => !t.demo);
const pc = (a, b) => b ? Math.round(100 * a / b) : 0, V = [...new Set(sig.map(s => s.village))], W = Math.max(...sig.map(s => s.week));
const wk = t => Math.floor(t.auction / 2) + 1, F = [];
const add = (village, text, nums, score = 5, dir = 0) => F.push({ id: 'F' + (F.length + 1), village, text, nums, score, dir });
const MET = [['mould', 'photos flagged black or mouldy', /black\/mould/], ['insect', 'photos flagged insect damage', /insect/], ['drying', 'photos flagged uneven drying', /drying/]];
for (const v of V) {
  const s1 = sig.find(s => s.village === v && s.week === 1), s3 = sig.find(s => s.village === v && s.week === W);
  const O = tr.filter(t => t.village !== v && wk(t) === W);
  for (const [k, label, re] of MET) {
    const oth = pc(O.filter(t => re.test(t.flags)).length, O.length);
    add(v, `${v}, week ${W}: ${label} ${s3[k]}% (week 1: ${s1[k]}%; the other four villages in week ${W}: ${oth}%)`, [W, s3[k], 1, s1[k], oth, 4], Math.abs(s3[k] - s1[k]) + Math.abs(s3[k] - oth), Math.sign(s3[k] - s1[k]));
  }
  const oC = pc(O.filter(t => t.grade === 'C').length, O.length);
  add(v, `${v}, week ${W}: grade C ${s3.gradeC}% of offers, confirmed by inspectors (week 1: ${s1.gradeC}%; other four villages: ${oC}%)`, [W, s3.gradeC, 1, s1.gradeC, oC, 4], Math.abs(s3.gradeC - s1.gradeC) + Math.abs(s3.gradeC - oC), Math.sign(s3.gradeC - s1.gradeC));
  add(v, `${v}, week ${W}: ${s3.kg_per_offer} kg per offer, ${s3.vs_week1}% against week 1 (${s1.kg_per_offer} kg)`, [W, s3.kg_per_offer, s3.vs_week1, 1, s1.kg_per_offer], 2 * Math.abs(s3.vs_week1), Math.sign(s3.vs_week1));
  const T = tr.filter(t => t.village === v && wk(t) === W), n = T.filter(t => t.status !== 'in').length;
  add(v, `${v}, week ${W}: ${n} of ${T.length} offers sat out (the farmer's minimum was above the price for that grade)`, [W, n, T.length], 100 * n / Math.max(1, T.length));
}
const m0 = mk[0], mL = mk[mk.length - 1], gap = +(mL.median_ask - mL.best_bid).toFixed(2);
add(null, `Last auction (${S.fmtD(mL.date)}): the lot cleared at $${mL.best_bid.toFixed(2)}/kg, against $${m0.best_bid.toFixed(2)} at the first auction (${S.fmtD(m0.date)})`, [+mL.date.slice(8), mL.best_bid, m0.best_bid, +m0.date.slice(8)]);
add(null, `Last auction: grade prices A $${mL.A.toFixed(2)}, B $${mL.B.toFixed(2)}, C $${mL.C.toFixed(2)} per kg; ${mL.bids} buyers bid`, [mL.A, mL.B, mL.C, mL.bids]);
add(null, `Last auction: farmers' median minimum $${mL.median_ask.toFixed(2)}/kg, ${Math.abs(gap).toFixed(2)} ${gap < 0 ? 'below' : 'above'} the winning bid; ${mL.sat_out} farms sat out`, [mL.median_ask, Math.abs(gap), mL.sat_out]);
const lo = mk.reduce((a, b) => b.best_bid < a.best_bid ? b : a);
add(null, `Lowest lot price in the three weeks: $${lo.best_bid.toFixed(2)}/kg on ${S.fmtD(lo.date)}, with ${lo.sat_out} farms sitting out`, [lo.best_bid, +lo.date.slice(8), lo.sat_out]);
add(null, `Rain fell ${S.fmtD(D.rain[0])} to ${S.fmtD(D.rain[1])}, in week 2 (from the pool records)`, [+D.rain[0].slice(8), +D.rain[1].slice(8), 2], 30);
const consent = reg.filter(x => x.consent === 'Y').length;
add(null, `${reg.length} farmers on the register after three weeks; ${consent} agreed to be named to the ministry`, [reg.length, consent]);
// code ranks the findings by how unusual they are (change against week 1 plus gap to the other villages);
// the model sees the ten most unusual, plus the price findings, and writes them up
const top = F.filter(f => f.village).sort((a, b) => b.score - a.score).slice(0, 8);
const ctx = F.filter(f => !f.village);
const text = 'Today is Monday 27 July 2026, 06:00. Letefoho coffee pool, five villages, three weeks of data.\nMOST UNUSUAL FINDINGS, most unusual first (ranked by code):\n' + top.map(f => `${f.id}: ${f.text}`).join('\n') + '\n\nPRICES AND CONTEXT:\n' + ctx.map(f => `${f.id}: ${f.text}`).join('\n');
const hash = crypto.createHash('sha256').update(JSON.stringify(D)).digest('hex').slice(0, 12);
fs.writeFileSync(process.env.OUT || (__dirname + '/findings.json'), JSON.stringify({ hash, villages: V, findings: F, text }, null, 1));
console.log(text);
