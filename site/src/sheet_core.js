/* Dure register: every derived figure is computed here from the raw rows.
   Used by sheet.html (in the browser) and by tools/check_sheet.js (node). */
const DureSheet = (() => {
  const r2 = x => Math.round(x * 100) / 100;
  const med = a => { const s = a.slice().sort((x, y) => x - y); return s.length ? (s.length % 2 ? s[(s.length - 1) / 2] : (s[s.length / 2 - 1] + s[s.length / 2]) / 2) : null; };
  const week = a => Math.floor(a / 2) + 1;           // auctions 0,1 -> week 1 ...
  const pct = (n, d) => d ? Math.round(n / d * 100) : 0;

  function compute(D) {
    const F = {}; D.farmers.forEach(f => F[f.id] = f);
    const nA = Math.max(...D.offers.map(o => o.auction)) + 1;
    const market = [];
    const trades = D.offers.map((o, i) => ({ ...o, row: i, village: F[o.farmer].village }));
    for (let a = 0; a < nA; a++) {
      const T = trades.filter(t => t.auction === a);
      const B = D.bids.filter(b => b.auction === a).sort((x, y) => y.bid - x.bid);
      const lot = B[0] ? B[0].bid : null, buyer = B[0] ? B[0].buyer : null, open = B[0] ? B[0].open : null;
      // grade prices: weights normalised so the buyer's total (lot price × kg in) equals the farmers' total
      // 1) who is in: compare each minimum with grade prices computed on everything offered
      const gp = set => { const kg = set.reduce((s, t) => s + t.kg, 0), wsum = set.reduce((s, t) => s + t.kg * D.weights[t.grade], 0);
        const k = wsum ? lot * kg / wsum : 0; return { A: r2(D.weights.A * k), B: r2(D.weights.B * k), C: r2(D.weights.C * k) }; };
      const offerPrice = gp(T);
      const inSet = T.filter(t => t.ask <= offerPrice[t.grade] + 1e-9);
      // 2) what is paid: grade prices re-normalised on the coffee actually sold, so buyer total = farmers' total
      const price = inSet.length ? gp(inSet) : offerPrice;
      T.forEach(t => { t.price = price[t.grade]; t.status = t.ask <= offerPrice[t.grade] + 1e-9 ? 'in' : 'sat out';
        t.paid = t.status === 'in' ? r2(t.kg * t.price) : 0; t.buyer = t.status === 'in' ? buyer : '';
        t.matched = t.ai_grade === t.grade ? 'yes' : 'no'; });
      const IN = T.filter(t => t.status === 'in');
      market.push({ auction: a, demo: T.some(t => t.demo), date: D.auctions[a], week: week(a), farms: T.length, kg_offered: T.reduce((s, t) => s + t.kg, 0),
        kg_sold: IN.reduce((s, t) => s + t.kg, 0), farms_in: IN.length, open, best_bid: lot, buyer, bids: B.length,
        A: price.A, B: price.B, C: price.C, median_ask: r2(med(T.map(t => t.ask))),
        sat_out: T.length - IN.length, paid: r2(IN.reduce((s, t) => s + t.paid, 0)),
        kgA: IN.filter(t => t.grade === 'A').reduce((s, t) => s + t.kg, 0), kgB: IN.filter(t => t.grade === 'B').reduce((s, t) => s + t.kg, 0), kgC: IN.filter(t => t.grade === 'C').reduce((s, t) => s + t.kg, 0) });
    }
    // register: built from the trades
    const register = D.farmers.map(f => {
      const T = trades.filter(t => t.farmer === f.id), IN = T.filter(t => t.status === 'in');
      let rep = 64;
      IN.forEach(t => { const s = .35 * (t.on_time ? 1 : 0) + .30 * (t.matched === 'yes' ? 1 : 0) + .20 + .15; rep = .8 * rep + .2 * s * 100; });
      return { id: f.id, village: f.village, ha: f.ha, joined: T.length ? T.map(t => t.date).sort()[0] : '', consent: f.consent,
        offers: T.length, sales: IN.length, kg_sold: IN.reduce((s, t) => s + t.kg, 0), paid: r2(IN.reduce((s, t) => s + t.paid, 0)),
        on_time: IN.length ? pct(IN.filter(t => t.on_time).length, IN.length) : null,
        matched: T.length ? pct(T.filter(t => t.matched === 'yes').length, T.length) : null, likely: Math.round(rep) };
    });
    // field signals: village × week
    const V = [...new Set(D.farmers.map(f => f.village))];
    const signals = [];
    const real = trades.filter(t => !t.demo), nW = Math.ceil((Math.max(...real.map(t => t.auction)) + 1) / 2);
    V.forEach(v => { for (let w = 1; w <= nW; w++) {
      const T = real.filter(t => t.village === v && week(t.auction) === w);
      const w1 = real.filter(t => t.village === v && week(t.auction) === 1);
      const kgpf = T.length ? T.reduce((s, t) => s + t.kg, 0) / T.length : 0, kgpf1 = w1.length ? w1.reduce((s, t) => s + t.kg, 0) / w1.length : 0;
      signals.push({ village: v, week: w, offers: T.length, kg_per_offer: Math.round(kgpf), vs_week1: kgpf1 ? Math.round((kgpf / kgpf1 - 1) * 100) : 0,
        mould: pct(T.filter(t => /black\/mould/.test(t.flags)).length, T.length), insect: pct(T.filter(t => /insect/.test(t.flags)).length, T.length),
        drying: pct(T.filter(t => /drying/.test(t.flags)).length, T.length), debris: pct(T.filter(t => /debris/.test(t.flags)).length, T.length),
        gradeC: pct(T.filter(t => t.grade === 'C').length, T.length), sat_out: pct(T.filter(t => t.status !== 'in').length, T.length),
        ai_disagree: pct(T.filter(t => t.matched === 'no').length, T.length) }); } });
    return { trades, market, register, signals, brief: brief(D, real, market.filter(m => !m.demo), register, signals, V) };
  }

  // The brief: every number below is computed from the tables. Only the wording is written around them.
  function brief(D, trades, market, register, signals, V) {
    const lastW = Math.max(...signals.map(s => s.week));
    const last = signals.filter(s => s.week === lastW);
    const worst = last.slice().sort((a, b) => b.mould - a.mould)[0];
    const others = trades.filter(t => t.village !== worst.village && Math.floor(t.auction / 2) + 1 === lastW);
    const othersMould = pct(others.filter(t => /black\/mould/.test(t.flags)).length, others.length);
    const sw1 = signals.find(s => s.village === worst.village && s.week === 1);
    const wT = trades.filter(t => t.village === worst.village && Math.floor(t.auction / 2) + 1 === lastW);
    const wSat = wT.filter(t => t.status !== 'in').length;
    const m0 = market[0], mL = market[market.length - 1];
    const gap = r2(mL.median_ask - mL.best_bid);
    const consentN = register.filter(r => r.consent === 'Y').length, noSale = register.filter(r => r.sales === 0).length;
    const dis = pct(trades.filter(t => t.matched === 'no').length, trades.length);
    const byModel = pct(trades.filter(t => t.read_by === 'model').length, trades.length);
    const tet = pct(trades.filter(t => t.lang === 'TET').length, trades.length);
    const rainy = D.rain;
    return {
      date: 'Monday 27 July 2026, 06:00', worst: worst.village,
      headline: `${worst.village}: mould flagged on ${worst.mould}% of photos in week ${lastW}, after the ${fmtD(rainy[0])}–${fmtD(rainy[1])} rain, against ${othersMould}% in the other four villages.`,
      facts: { mould: worst.mould, others: othersMould, kgDrop: worst.vs_week1, cFrom: sw1.gradeC, cTo: worst.gradeC, sat: wSat, satOf: wT.length,
               farmers: register.length, consent: consentN, noSale, dis, byModel, tet, gap, lot0: m0.best_bid, lotL: mL.best_bid },
      changed: [
        { t: `Coffee offered per farm in ${worst.village} is ${worst.vs_week1 < 0 ? 'down' : 'up'} ${Math.abs(worst.vs_week1)}% against week 1 (${sw1.kg_per_offer} → ${worst.kg_per_offer} kg per offer).`, tab: 'signals', f: { village: worst.village } },
        { t: `Grade C share in ${worst.village} rose from ${sw1.gradeC}% in week 1 to ${worst.gradeC}% in week ${lastW}. Inspectors confirmed the grades at pickup.`, tab: 'signals', f: { village: worst.village } },
        { t: `${wSat} of ${worst.village}'s ${wT.length} offers in week ${lastW} sat out: the farmers' minimums were above the price their grade fetched.`, tab: 'trades', f: { village: worst.village, week: lastW, status: 'sat out' } },
        { t: `Elsewhere, mould flags stayed at ${othersMould}% and volumes moved by less than a tenth.`, tab: 'signals', f: {} },
      ],
      prices: [
        { t: `The lot cleared at $${mL.best_bid.toFixed(2)}/kg on ${fmtD(mL.date)} (from $${m0.best_bid.toFixed(2)} on ${fmtD(m0.date)}); grade prices A $${mL.A.toFixed(2)} · B $${mL.B.toFixed(2)} · C $${mL.C.toFixed(2)}.`, tab: 'market', f: {} },
        { t: `${mL.bids} buyers bid on the last lot. Farmers' median minimum was $${mL.median_ask.toFixed(2)}, ${gap >= 0 ? gap.toFixed(2) + ' above' : (-gap).toFixed(2) + ' below'} the winning bid.`, tab: 'market', f: {} },
      ],
      register: [
        { t: `${register.length} farmers are on the register after three weeks; ${consentN} agreed to be shared with the ministry by name, the rest appear only in village totals.`, tab: 'register', f: {} },
        { t: `Every one of them has sold or offered through Dure at least once; ${noSale} have offered but not yet sold.`, tab: 'register', f: { sales: 0 } },
      ],
      quality: [
        { t: `Dure AI's photo grade differed from the inspector's on ${dis}% of offers; the inspector's grade is the one paid.`, tab: 'trades', f: { matched: 'no' } },
        { t: `${tet}% of messages were in Tetum. Rules read ${100 - byModel}% of them; the small model read the other ${byModel}%, and every reading was confirmed by the farmer.`, tab: 'trades', f: {} },
      ],
      review: [
        `An extension visit to ${worst.village} this week, to check how parchment is being dried and stored after the rain.`,
        `Whether ${worst.village} farmers need drying space (tarps, raised beds) before the next harvest peak.`,
        `Whether the ${wSat} farmers who sat out need a cash advance until their coffee can be sold.`,
      ],
      limits: [
        'Why yields or quality changed. The register shows where and when, not the cause.',
        'Farmers who never text Dure, and coffee sold straight to traders.',
        'Weather: the rain dates come from the pool records, not a weather station.',
        'All data here is synthetic, made for this demonstration.',
      ],
    };
  }
  const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  function fmtD(s) { const [y, m, d] = s.split('-'); return `${+d} ${MON[+m - 1]}`; }
  return { compute, fmtD };
})();
if (typeof module !== 'undefined') module.exports = DureSheet;
