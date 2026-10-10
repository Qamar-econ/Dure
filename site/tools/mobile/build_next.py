"""A summit edition of the phone page (draft, not deployed): the same story and drawings as build_mobile.py,
re-ordered for a visitor who scans a QR code at a booth.

  Level 1 (10 s)    what Dure is, who it helps, the problem, how SMS and AI fit; demo + quick links
  Level 2 (30-60 s) the market logic (alone vs together, why not a cooperative), the week in five steps,
                    and what is working / simulated / still to be tested in the field
  Level 3 (opt-in)  Noor's week message by message, technical walkthrough, benchmark, Registry, field risks,
                    founder and links

Writes site/src/m_next.html (not part of build.py, so nothing here reaches the live site).
"""
import os, sys
sys.argv = sys.argv[:1]
import build_mobile as B
N = B.N

HERE = os.path.dirname(os.path.abspath(__file__))
CSS = B.CSS + open(os.path.join(HERE, 'next.css'), encoding='utf-8').read()
JS = B.JS + open(os.path.join(HERE, 'next.js'), encoding='utf-8').read()

REPO = 'https://github.com/Qamar-econ/Dure'
LOGO = B.LOGO


def tag(kind):
    lab = {'p': 'Working prototype', 's': 'Simulated in the demo', 'f': 'Needs a field pilot'}[kind]
    return f'<span class="st st-{kind}">{lab}</span>'


STEPS = [
    ('Text an offer', 'Every morning each farmer gets the same price text. She replies from any phone, in Tetum or English, in her own words: kilos, grade, her minimum. Dure repeats back what it understood before anything is recorded.', 'p', 'The reader (a rules engine plus a small language model) runs in the demo.'),
    ('Pool the harvest', 'Offers from the whole village fill one lot, every grade together. A truck and a buyer now see 2,000 kg, not 40.', 's', 'Farmers and volumes in the demo are synthetic.'),
    ('Buyers compete', 'When the lot is full, buyers bid for all of it until 17:00. Each farmer\'s minimum is her floor, and she still answers YES or NO herself.', 's', 'The auction runs on simulated buyers.'),
    ('AI looks, people confirm', 'One phone photo gets a preliminary grade A, B or C. A person checks every sack by hand at pickup, and that grade is the one paid.', 'p', 'The photo grader runs on the visitor\'s phone; the pickup check is part of the proposed field process.'),
    ('Records build trust', 'Every deal leaves a row: a reputation for farmers and buyers, an automated Registry and a weekly brief for extension officers.', 'p', 'Built and running on eight weeks of synthetic data.'),
]


def steps():
    li = ''.join(f'<li class="rv"><span class="sn">{i+1}</span><div><h3>{t}</h3><p>{p}</p><p class="stl">{tag(k)}<span>{n}</span></p></div></li>' for i, (t, p, k, n) in enumerate(STEPS))
    return f'<ol class="flow5">{li}</ol>'


STATUS = [
    ('p', 'Working prototype', 'Runs today, in a browser, with no server', [
        'SMS reader for Tetum and English: rules engine, plus a small model for unclear texts',
        'Photo grader on the phone itself: grade A, B or C, or "send another photo"',
        'Small-AI chat for off-script questions, answered from live market data',
        'Registry and weekly brief: code computes the findings, AI writes, a checker verifies each sentence']),
    ('s', 'Simulated in the demo', 'Shows the mechanism, not real outcomes', [
        'Farmers, buyers, volumes and prices are synthetic',
        'SMS gateway, mobile-money escrow and payout are simulated',
        'Price gains shown (such as +25%) are illustrative examples, not measured results']),
    ('f', 'Needs a field pilot', 'Not yet tested with farmers', [
        'A real SMS gateway and a mobile-money partner',
        'One pickup point with a trusted person to check every sack',
        'Buyers willing to bid; price bands calibrated on live trades',
        'Real Tetum messages and Ermera coffee photos, collected with consent, to retrain and re-test the models']),
]


def status():
    cards = ''.join(f'<div class="stc stc-{k} rv"><p class="stl">{tag(k)}</p><p class="sub">{sub}</p><ul>{"".join(f"<li>{x}</li>" for x in items)}</ul></div>' for k, _, sub, items in STATUS)
    return f'<div class="status">{cards}</div><p class="note rv">There has been no field test. Real effects would depend on buyer participation, transport, quality and how the pickup point is run.</p>'


def more(title, sub, body, open_=False, cls=''):
    return (f'<details class="dd {cls}"{" open" if open_ else ""}><summary><span><b>{title}</b><small>{sub}</small></span><i aria-hidden="true"></i></summary>'
            f'<div class="ddb">{body}</div></details>')


TECH = (
    B.tw_block(0, B.PARSER)
    + B.tw_block(1, N.grade_compact() + '<div class="train">' + ''.join(f'<img src="{a}" alt="" title="{t}" loading="lazy" width="60" height="60">' for a, t in B.TRAIN) + '</div><p class="tcap">Some of our training photos · Wikimedia Commons: H. Ulver, M. C. Wright, F. Quijano (CC BY-SA 4.0); Forest &amp; Kim Starr (CC BY 3.0)</p>')
    + B.tw_block(3, N.tabs([('Noor · 2 ha', N.rep_compact('noor')), ('Big grower · 30 ha', N.rep_compact('big'))], 'Two farmers') + B.BUYERS)
    + B.tw_block(4, N.tabs([('Blended pool', N.blend()), ('Fixed pool', N.fixed())], 'Two markets'))
)

BENCH = (f'<p>Large models overlook Tetum. A small model plus a rules engine gets Dure close to a large model, with no server.</p>'
         f'<ul class="bench">{B.bench}</ul>'
         '<p class="src"><b>Method.</b> 60 test SMS (44 Tetum, 16 English), written by Claude Sonnet, not by us, and frozen before any reader was scored. '
         'A text counts only if crop, quantity, grade, price and intent are all right. On 80 texts we wrote ourselves: rules engine 98%, with the small model 99% '
         '(not independent). Costs are API list prices. Measured 4 Oct 2026.</p>')

REGISTRY = (f'<div class="reg">{N.tabs([("1 · Trades", N.ledger()), ("2 · Analysis", N.qchart()), ("3 · Monday&#39;s brief", N.brief())], "The Registry")}</div>'
            '<a class="btn ghost" href="sheet.html">Open the sample Registry<span>→</span></a>'
            '<p class="src">Synthetic data for eight weeks in Letefoho.</p>')

RISKS = ('<div class="risks">'
         '<div><h4>The road washes out.</h4><p>Dure books the truck and the pickup point. It can\'t fix the road, and doesn\'t pretend to.</p></div>'
         '<div><h4>Who sees the records?</h4><p>Proposed: farmers\' names and numbers stay with Dure. The ministry\'s Registry shows pseudonymous IDs and village totals, and only for farmers who said yes.</p></div>'
         '<div><h4>The power or the server goes down.</h4><p>The rules engine keeps taking offers by text. The small model rechecks them later, and any change goes back to the farmer to confirm.</p></div>'
         '<div><h4>AI never sets the price.</h4><p>Farmers set minimums, buyers bid, the auction clears. Photo grades are preliminary; a person confirms. No one is excluded automatically.</p></div>'
         '</div>'
         '<dl class="costs ev">'
         '<div><dt>40%</dt><dd>of firms had power cuts in a year, losing <b>9.4%</b> of sales.<cite>World Bank Enterprise Survey, 2015</cite></dd></div>'
         '<div><dt>24 h</dt><dd>outages in Viqueque. Dili\'s hospital runs on generators each time.<cite>Tatoli, 2022–23</cite></dd></div>'
         '<div><dt>36%</dt><dd>of Dili customers never report an outage.<cite>TANE survey, 2022</cite></dd></div></dl>'
         f'<p class="src">More: <a href="{REPO}/blob/main/RESPONSIBLE_AI.md">Responsible AI</a> · <a href="{REPO}/blob/main/DATA_CARD.md">Data card</a></p>')

LINKS = [
    ('Try the demo', 'demo.html', 'A week of selling by text, in your browser', 'main'),
    ('Code on GitHub', REPO, 'Source, models, benchmark and README', ''),
    ('Sample Registry', 'sheet.html', 'The records and the weekly brief', ''),
    ('Full illustrated story', 'index.html?full=1', 'The animated version, best on a computer', ''),
]
links = ''.join(f'<a class="lk {c}" href="{h}"{" target=_blank rel=noopener" if h.startswith("http") else ""}><b>{t}</b><small>{s}</small><span>→</span></a>' for t, h, s, c in LINKS)

PAGE = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#F2EADA">
<title>Dure · Small farmers, one stronger market</title>
<meta name="description" content="Dure helps smallholder coffee farmers in Timor-Leste pool their harvest, have buyers compete for it and build a trusted trading record, by plain text message on any phone.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..800;1,6..72,300..800&family=Libre+Franklin:wght@400;500;600;700&family=VT323&family=Gochi+Hand&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body class="nx">
{N.SYMBOLS}
<div class="prog" aria-hidden="true"><i id="prog"></i></div>
<header class="bar nxbar">
  <a href="#top" class="logo" aria-label="Dure, back to top">{LOGO}</a>
  <nav class="nxnav" aria-label="Sections"><a href="#how">How</a><a href="#status">What's real</a><a href="#tech">Tech</a><a href="#contact">Contact</a></nav>
  <span id="chap" hidden></span>
</header>

<main id="top">
<!-- LEVEL 1 · ten seconds -->
<section class="nxhero">
  <p class="award">Winner · Agriculture · World Bank Small AI for Development Hackathon 2026</p>
  <h1>Small farmers, <em>one stronger market.</em></h1>
  <p class="lede">Dure lets smallholder coffee farmers in Timor-Leste <b>pool their harvest</b>, have <b>buyers compete</b> for it and build a <b>trusted trading record</b>, by plain text message on any phone. AI works behind the scenes; people check what matters.</p>
  <div class="cta"><a class="btn" href="demo.html">Try the demo<span>→</span></a><a class="btn ghost" href="#how">How it works<span>↓</span></a></div>
  <p class="pills"><span>Any phone · no internet · no app</span><span>Tetum &amp; English</span><span>Prototype · synthetic data</span></p>
  <div class="hpic" aria-hidden="true">{B.fig('hero.tab', None, 'Noor in her coffee field below the mountains').replace('<svg ', '<svg preserveAspectRatio="xMidYMax slice" ', 1)}</div>
</section>

<section class="txt nx1" id="why">
  <p class="kick rv">The problem</p>
  <h2 class="rv">A good harvest is <em>not a good price.</em></h2>
  <p class="lead rv">Noor grows coffee on the slopes of Letefoho. Alone, she sells 40 kg to whichever trader's truck reaches her village, <b>at the price he names.</b></p>
  <div class="map rv">{B.fig('map.route', None, 'Map: Letefoho to Gleno 19 km, Gleno to Dili 45 km, 64 km by road')}</div>
  <div class="big rv"><span class="n"><span class="cnt" data-to="98">98</span>%</span><p>of Ermera's coffee is bought by just four traders <span class="soft">(survey of 100 farmers, 2014)</span>.</p><cite>Cristovão, Bogor Agricultural University, 2015</cite></div>

  <p class="kick rv">The idea</p>
  <h2 class="rv">What if her neighbours <em>sold with her?</em></h2>
  <p class="rv">More coffee in one lot brings one truck and several buyers bidding. That is what a cooperative does.</p>
  <div class="rv">{N.alone_together()}</div>
  <div class="big rv"><span class="n"><span class="cnt" data-to="58">58</span>%</span><p>of 239 studies found that farmer organisations raised their members' incomes.</p><cite>Bizikova et al., Nature Food, 2020</cite></div>

  <p class="kick rv">The catch</p>
  <h2 class="rv">Starting a cooperative is <em>not easy.</em></h2>
  <dl class="costs">
    <div class="rv"><dt>3–4<small>years</small></dt><dd><b>Time.</b> Recruiting, then paperwork.</dd></div>
    <div class="rv"><dt>$1,000</dt><dd><b>Capital.</b> A coffee household earns about $250 a year.</dd></div>
    <div class="rv pwr"><dt><em>power.</em><small>and then</small></dt><dd><b>Power.</b> Women like Noor are easily left out.</dd></div>
  </dl>
  <p class="src rv">KOICA value-chain cooperative, Timor-Leste; Decree-Law No. 16/2004; The Irish Times, 2013.</p>
  <figure class="scene spl rv">{B.PART['split']}<figcaption>Joining stops being a choice. Whoever is left out <b>undercuts prices to sink it.</b></figcaption></figure>
  <div class="thesis rv">
    <p class="kick">Dure</p>
    <h2>Keep the cooperative's advantages, <em>drop the cooperative.</em></h2>
    <div class="sw2"><div><h4>What stays</h4><ul><li>Pooling the harvest</li><li>Buyers bidding for the whole lot</li><li>One shared truck and pickup point</li><li>A record that earns trust</li></ul></div>
      <div class="go"><h4>What goes</h4><ul><li>A legal entity</li><li>$1,000 in share capital</li><li>A board to run, a leader to fight over</li><li>Unequal voice: a few decide for everyone</li></ul></div></div>
    <p class="first"><b>Market coordination and trust come first; AI comes second.</b> AI only does narrow jobs: reading texts, a first look at quality, drafting a brief. Prices come from buyers bidding against farmers' own minimums.</p>
  </div>
</section>

<div class="night">
<!-- LEVEL 2 · thirty to sixty seconds -->
<section class="how nx2" id="how">
  <p class="chapno rv">How it works</p>
  <h2 class="rv">One week, <em>by text message.</em></h2>
  <p class="rv lead2">Five steps from a basic phone to a better-informed ministry.</p>
  {steps()}
  {more("See Noor's week, message by message", '8 steps · her phone and what Dure does behind it', '<div class="hsteps">' + B.thread() + '</div><p class="illus">Illustrative example — names, volumes and prices are not real data.</p>', cls='wk')}
</section>

<section class="txt nx2" id="status">
  <p class="chapno rv">What's real today</p>
  <h2 class="rv">Prototype, simulation, <em>and what needs a pilot.</em></h2>
  {status()}
</section>

<!-- LEVEL 3 · for the curious -->
<section class="txt nx3" id="tech">
  <p class="chapno rv">For the curious</p>
  <h2 class="rv">How it is built, <em>and how well it works.</em></h2>
  <p class="rv">The whole demo runs on the visitor's phone or laptop, so it needs no server. Every model is small enough for a pickup-point laptop.</p>
  {more('Technical walkthrough', 'Reading Tetum texts · grading photos · reputation · two markets', '<div class="twsec">' + TECH + '</div>')}
  {more('Tetum Benchmark Index', 'How well small and large models read Tetum texts', BENCH)}
  {more('From the slope to the ministry', 'An automated Registry and AI policy briefs', '<p>A farmer Registry is costly to keep by hand. Every Dure deal leaves a record, <b>so the Registry builds itself.</b> AI is not a silver bullet: it helps an extension officer make the most of two visits a year.</p>' + REGISTRY)}
  {more('Field problems and responsible AI', 'Roads, data, power cuts, and where people stay in charge', RISKS)}
</section>
</div>

<section class="dark close nxcontact" id="contact">
  <div class="tais" aria-hidden="true"></div>
  <div class="in">
    <p class="kick">Founder</p>
    <h2>Tae Yoon Moon</h2>
    <p class="fwho">University of Seoul · International Relations &amp; Economics. Built Dure solo for the World Bank Small AI for Development Hackathon, 3–4 October 2026.</p>
    <p class="ct"><a href="mailto:taeyoonmoon@uos.ac.kr">taeyoonmoon@uos.ac.kr</a><a href="https://www.linkedin.com/in/tae-yoon-moon-398b11313" target="_blank" rel="noopener">LinkedIn</a><a href="{REPO}" target="_blank" rel="noopener">GitHub</a></p>
    <div class="links">{links}</div>
    <div class="vids">{B.vids}</div>
    <p class="thanks">Thanks for stopping by. Happy to talk about pilots, data and partnerships.</p>
  </div>
  <div class="tais" aria-hidden="true"></div>
</section>
</main>
<footer class="foot"><p>© 2026 Tae Yoon Moon. Code MIT; synthetic data CC BY 4.0; illustrations and text all rights reserved.</p><p><a href="m.html">Current phone edition</a> · <a href="index.html?full=1">Animated version</a></p></footer>
<script>{JS}</script>
</body>
</html>
'''

open(os.path.join(B.SRC, 'm_next.html'), 'w', encoding='utf-8').write(PAGE)
print('m_next.html', len(PAGE) // 1024, 'KB')
