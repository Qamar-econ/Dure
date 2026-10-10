"""A summit edition of the phone page (draft, not deployed): the same story and drawings as build_mobile.py,
re-ordered for a visitor who scans a QR code at a booth.

  Level 1 (10 s)    what Dure is, who it helps, the problem, how SMS and AI fit; demo + quick links
  Level 2 (30-60 s) the market logic (alone vs together, why not a cooperative), the week in five steps,
                    and what is working / simulated / still to be tested in the field
  Level 3 (opt-in)  Noor's week message by message, technical walkthrough, benchmark, Registry, field risks,
                    founder and links

Writes site/src/m_phone.html; build.py publishes it as m.html.
"""
import os, sys
sys.argv = sys.argv[:1]
import build_mobile as B
N = B.N

HERE = os.path.dirname(os.path.abspath(__file__))
CSS = B.CSS + open(os.path.join(HERE, 'phone.css'), encoding='utf-8').read()
JS = B.JS + open(os.path.join(HERE, 'phone.js'), encoding='utf-8').read()

REPO = 'https://github.com/Qamar-econ/Dure'
LOGO = B.LOGO


import re


def more(title, sub, body, open_=False, cls=''):
    sub = f'<small>{sub}</small>' if sub else ''
    return (f'<details class="dd {cls}"{" open" if open_ else ""}><summary><span><b>{title}</b>{sub}</span><i aria-hidden="true"></i></summary>'
            f'<div class="ddb">{body}</div></details>')


ICONS = [   # one small line drawing per step (24 x 24, drawn in currentColor)
    '<path d="M3 17h18"/><path d="M7 17a5 5 0 0 1 10 0"/><path d="M12 6v3M5.6 9.6l1.8 1.8M18.4 9.6l-1.8 1.8M2.5 13.5h2M19.5 13.5h2"/>',   # sunrise: the morning price
    '<path d="M4 5h11a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2H9l-4 3v-3H4a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z"/><rect x="14" y="12" width="8" height="7" rx="1.5"/><circle cx="18" cy="15.5" r="1.6"/>',   # text and photo
    '<path d="M3 10h18l-2 9H5z"/><path d="M8 10l2-5M16 10l-2-5"/><circle cx="9.5" cy="14.5" r="1"/><circle cx="14.5" cy="14.5" r="1"/>',   # one basket
    '<path d="M3 20h18"/><path d="M6 20v-5M10 20V11M14 20V8M18 20V4"/><path d="M16.5 5.5L18 4l1.5 1.5"/>',   # rising bids: the auction
    '<path d="M3 13h18v8H3z"/><path d="M7.5 13V3.5h9V13"/><path d="M9.8 8.2l1.6 1.6 3-3.2"/>',   # ballot box: each farmer casts her own vote
    '<path d="M2 7h11v9H2zM13 10h4l3 3v3h-7"/><circle cx="6" cy="17.5" r="1.8"/><circle cx="16.5" cy="17.5" r="1.8"/>',   # truck
    '<rect x="3" y="6" width="18" height="13" rx="2"/><path d="M3 10h18"/><path d="M16 14.5h2"/>',   # wallet: payment
    '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/>',   # star: trust
]


def week():
    """How it works: the eight steps of Noor's week, each a short line that opens onto its messages"""
    out = []
    k = 0
    for a in re.findall(r'<article class="hstep rv">(.*?)</article>', B.thread(), re.S):
        if re.search(r'<span class="no">5<', a):   # the phone edition leaves out step 5 (each farmer decides)
            continue
        hd = re.search(r'<header>(.*?)</header>', a, re.S).group(1)
        orig = int(re.search(r'<span class="no">(\d+)', hd).group(1)); k += 1; no = str(k)
        t = re.search(r'<h3>(.*?)</h3>', hd).group(1)
        p = re.search(r'<p>(.*?)</p>', hd).group(1)
        rest = a[a.index('</header>') + 9:]
        ic = ICONS[orig - 1]
        out.append(f'<details class="wk rv"><summary><span class="no" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ic}</svg></span><span class="tx"><b><em class="n">{no}.</em> {t}</b><small>{p}</small></span><i aria-hidden="true"></i></summary>'
                   f'<template class="lz"><div class="hstep rv wkb">{rest}</div></template></details>')   # built only when opened: a lighter first load
    return '<div class="wks">' + ''.join(out) + '</div>'


# the phone edition's notes, shorter
_tw = list(B.TW[0]); _tw[3] = 'Open-source Qwen, trained on 3,125 texts incl. 250 real Tetum (Labadain-30k+, CC BY 4.0).'; B.TW[0] = tuple(_tw)
_tw = list(B.TW[1]); _tw[2] = 'A small vision model trained on 1,200 bean photos grades coffee A, B or C, right 79% of the time. A hand check sets the final grade.'; B.TW[1] = tuple(_tw)

TECH = (
    B.tw_block(0, B.PARSER)
    + B.tw_block(1, N.grade_compact() + '<div class="train">' + ''.join(f'<img src="{a}" alt="" title="{t}" loading="lazy" width="60" height="60">' for a, t in B.TRAIN) + '</div><p class="tcap">Some of our training photos · Wikimedia Commons: H. Ulver, M. C. Wright, F. Quijano (CC BY-SA 4.0); Forest &amp; Kim Starr (CC BY 3.0)</p>')
    + B.tw_block(3, N.tabs([('Noor · 2 ha', N.rep_compact('noor')), ('Big grower · 30 ha', N.rep_compact('big'))], 'Two farmers') + B.BUYERS)
    + B.tw_block(4, N.tabs([('Blended pool', N.blend()), ('Fixed pool', N.fixed())], 'Two markets'))
)

BENCH = (f'<p>Large models overlook Tetum. A small model plus a rules engine gets Dure close to a large model.</p>'
         f'<ul class="bench rv">{B.bench}</ul>'
         '<p class="src"><b>Method.</b> 60 test SMS (44 Tetum, 16 English) written by Claude Sonnet and frozen before scoring. A text counts only if every field is right. Measured 4 Oct 2026.</p>')

REGISTRY = ('<p class="lead">A farmer Registry is costly to keep by hand. Every Dure deal leaves a record, <b>so the Registry builds itself.</b></p>'
            f'<div class="reg">{N.tabs([("1 · Trades", N.ledger()), ("2 · Analysis", N.qchart()), ("3 · Monday&#39;s brief", N.brief())], "The Registry")}</div>'
            '<p><b>AI is not a silver bullet.</b> Noor knows farming better than Dure. Dure helps the extension officer make the most of two visits a year.</p>'
            '<a class="btn ghost" href="sheet.html">Open the sample Registry<span>→</span></a>'
            '<p class="src">Synthetic data for eight weeks in Letefoho.</p>')

RISKS = ('<div class="risks">'
         '<div><h4>The road washes out.</h4><p>Dure books the truck and the pickup point. It can\'t fix the road, and doesn\'t pretend to.</p></div>'
         '<div><h4>Who sees the records?</h4><p>Farmers\' names and numbers stay with Dure. The ministry\'s Registry shows pseudonymous IDs and village totals, and only for farmers who said yes.</p></div>'
         '<div><h4>The power or the server goes down.</h4><p>The rules engine keeps taking offers by text. The small model rechecks them later, and any change goes back to the farmer to confirm.</p></div>'
         '</div>'
         '<h3 class="sub">Electricity is a real problem in Timor-Leste.</h3>'
         '<dl class="costs ev">'
         '<div><dt>40%</dt><dd>of firms had power cuts in a year, losing <b>9.4%</b> of sales.<cite>World Bank Enterprise Survey, 2015</cite></dd></div>'
         '<div><dt>24 h</dt><dd>outages in Viqueque. Dili\'s hospital runs on generators each time.<cite>Tatoli, 2022–23</cite></dd></div>'
         '<div><dt>36%</dt><dd>of Dili customers never report an outage.<cite>TANE survey, 2022</cite></dd></div></dl>')

AWARD = '<div class="award"><img src="assets/worldbank.png" alt="The World Bank" width="720" height="146"><span><b>Winner · Agriculture track</b>Small AI for Development<br>Hackathon 2026</span></div>'
STAYS = '<ul class="swl"><li>Pooling the harvest</li><li>Buyers bidding for the whole lot</li><li>One shared truck and pickup point</li><li>A record that earns trust</li></ul>'
GOES = '<ul class="swl go"><li>A legal entity</li><li>$1,000 in share capital</li><li>A board to run, a leader to fight over</li><li>Unequal voice: a few decide for everyone</li></ul>'

ZOOM = "<script>/* big tablets read like an iPad mini: the whole page is scaled up from the mini's width (768 tall, 1024 wide) */\n(function(){var d=document.documentElement;function f(){var w=innerWidth,h=innerHeight,base=h>=w?768:1024,z=(Math.min(w,h)>=700&&w>base+30)?Math.min(w/base,1.45):1;d.style.zoom=z===1?'':z.toFixed(3);d.style.setProperty('--z',z.toFixed(3))}f();addEventListener('resize',f)})();</script>"

PAGE = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#F2EADA">
<title>Dure · Cooperate through messaging</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..800;1,6..72,300..800&family=Libre+Franklin:wght@400;500;600;700&family=VT323&family=Gochi+Hand&display=swap" rel="stylesheet">
<style>{CSS}</style>
{ZOOM}
</head>
<body class="nx">
{N.SYMBOLS}
<div class="prog" aria-hidden="true"><i id="prog"></i></div>
<header class="bar nxbar">
  <a href="#top" class="logo" aria-label="Dure, back to top">{LOGO}</a>
  <nav class="nxnav" aria-label="Sections"><a href="#how">How it works</a><a href="#tech">Tech</a><a href="#contact">Contact</a></nav>
  <span id="chap" hidden></span>
</header>

<main id="top">
<section class="hero" data-c="1" data-t="The field">
  <div class="portrait">{B.fig('hero.noor', None, 'Noor, a coffee farmer in Letefoho, holding a basket of ripe cherries').replace('viewBox="180 0 460 900"', 'viewBox="258 0 460 900" preserveAspectRatio="xMidYMin slice"', 1)}</div>
  <div class="portrait wide">{B.fig('hero.tab', None, 'Noor in her coffee field below the mountains').replace('<svg ', '<svg preserveAspectRatio="xMinYMax slice" ', 1)}</div>
  <div class="htxt">
    {AWARD}
    <div class="mark">{LOGO}</div>
    <p class="tag">Cooperate through messaging.</p>
    <p class="def"><b>Dure</b>: the Korean tradition of mutual aid between farmers.</p>
  </div>
  <div class="nxintro">
    <div class="cta"><a class="btn" href="demo.html">Try the demo<span>→</span></a><a class="btn ghost" href="#how">How it works<span>↓</span></a></div>
  </div>
</section>


<section class="txt" data-c="1" data-t="The field">
  <h2 class="rv">A good harvest is <em>not a good price.</em></h2>
  <p class="lead rv">Noor grows coffee on the slopes of Letefoho, Timor-Leste. <em class="nl">Is the market treating her well?</em></p>
</section>
<section class="txt split" data-c="2" data-t="The buyers">
  <h2 class="rv">The buyers are mostly in the capital, <em>Dili.</em></h2>
  <div class="map rv">{B.fig('map.route', None, 'Map: Letefoho to Gleno 19 km, Gleno to Dili 45 km, 64 km by road')}</div>
  <div class="big rv"><span class="n"><span class="cnt" data-to="98">98</span>%</span><p>of Ermera's coffee is bought by just four traders in the capital <span class="soft">(survey of 100 farmers, 2014)</span>.</p><cite>Cristovão, Bogor Agricultural University, 2015</cite></div>
</section>
<section class="txt" data-c="5" data-t="Together">
  <h2 class="rv">What if her neighbours <em>sold with her?</em></h2>
  <div class="rv">{N.alone_together()}</div>
  <p class="lead rv">This is cooperation. <b>This is Dure.</b></p>
  <div class="big rv"><span class="n"><span class="cnt" data-to="58">58</span>%</span><p>of 239 studies found that farmer organisations raised their members' incomes.</p><cite>Bizikova et al., Nature Food, 2020</cite></div>
  <p class="q rv">So why isn't she benefiting from the Letefoho coffee cooperative?</p>
</section>
<section class="txt" data-c="6" data-t="The catch">
  <p class="kick rv">The catch</p>
  <h2 class="rv">Starting a cooperative in Timor-Leste is <em>not easy.</em></h2>
  <dl class="costs">
    <div class="rv"><dt>3–4<small>years</small></dt><dd><b>Time.</b> Recruiting, then paperwork.</dd></div>
    <div class="rv"><dt>$1,000</dt><dd><b>Capital.</b> A coffee household earns about $250 a year.</dd></div>
    <div class="rv pwr"><dt><em>power.</em><small>and then</small></dt><dd><b>Power.</b> Women like Noor are easily left out.</dd></div>
  </dl>
  <p class="src rv">KOICA value-chain cooperative, Timor-Leste; Decree-Law No. 16/2004; The Irish Times, 2013.</p>
  <figure class="scene spl rv">{B.PART['split']}<figcaption>Joining stops being a choice. Whoever is left out <b>undercuts prices to sink it.</b></figcaption></figure>
  <h2 class="rv endline">So Noor still sells alone, <em>at the trader's price.</em></h2>
</section>

<section class="dark first" data-c="7" data-t="Dure">
  <div class="tais" aria-hidden="true"></div>
  <div class="in">
    <h2 class="rv">What if the village kept the cooperative's advantages, <em>but dropped the cooperative?</em></h2>
  </div>
  <div class="phoneNoor">
    <svg class="pn" viewBox="-86 -536 256 410" role="img" aria-label="Noor holding up her basic phone"><defs>{B.PART['tais']}</defs>
      {B.PART['fphone']}</svg>
    <div class="pt"><p class="kick">Introducing</p><div class="dmark">{LOGO.replace('fill="#1F3A40"', 'fill="#F4EBDA"')}</div><h3>Cooperating through <em>messages.</em></h3></div>
  </div>
  <div class="in">
    <div class="swtabs rv">{N.tabs([('What stays', STAYS), ('What goes', GOES)], 'What changes')}</div>
    <div class="sw rv"><div><h4>What stays</h4>{STAYS}</div><div class="go"><h4>What goes</h4>{GOES}</div></div>
    <p class="q rv sms2">No internet. No app. <b>Just SMS.</b></p>
  </div>
</section>

<div class="night">
<section class="how nxhow" id="how" data-c="8" data-t="How it works">
  <p class="chapno rv">How it works</p>
  <h2 class="rv">One week, <em>by text message.</em></h2>
  <p class="rv lead2">Noor's week, on her basic phone. Behind each message, Dure does a cooperative office's work with the buyers. <span class="soft">Tap a step to open its messages.</span></p>
  {week()}
  <p class="illus">Illustrative example — names, volumes and prices are not real data.</p>
</section>

<section class="txt nx3" id="tech" data-c="9" data-t="For the curious">
  <p class="chapno rv">For the curious</p>
  {more('Technical walkthrough', 'Tetum texts · photo grades · reputation · two markets', '<div class="twsec">' + TECH + '</div>')}
  {more('How well does AI read <em>Tetum texts?</em>', 'Tetum Benchmark Index', BENCH)}
  {more('An automated Registry <em>and AI policy suggestions.</em>', 'From the slope to the ministry', REGISTRY)}
  {more('What are the real <em>field problems?</em>', 'Roads, records, power', RISKS)}
</section>
</div>

<section class="dark close nxcontact" id="contact">
  <div class="tais" aria-hidden="true"></div>
  <div class="in">
    <h2>Cooperate through <em>messaging.</em></h2>
    <a class="btn" href="demo.html">Try the demo<span>→</span></a>
    <div class="vids">{B.vids}</div>
    <div class="fdr"><p class="kick">Founder</p><p class="fname">Tae Yoon Moon</p><p class="fwho">University of Seoul · International Relations &amp; Economics</p>
      <p class="ct"><a href="mailto:taeyoonmoon@uos.ac.kr">taeyoonmoon@uos.ac.kr</a><a href="https://www.linkedin.com/in/tae-yoon-moon-398b11313" target="_blank" rel="noopener">LinkedIn</a><a href="https://docs.google.com/document/d/1BhcbQTZ8WVTYN4VDnK4LSs0JsRNSKh60xIMSUa_87dM/view" target="_blank" rel="noopener">CV</a><a href="{REPO}" target="_blank" rel="noopener">GitHub</a><a href="sheet.html">Sample Registry</a></p></div>
    <p class="thanks">Thanks for paying attention, and enjoy the demo!</p>
  </div>
  <div class="tais" aria-hidden="true"></div>
</section>
</main>
<footer class="foot"><p>© 2026 Tae Yoon Moon. All rights reserved. Illustrations and text may not be reused without permission.</p><p><a href="index.html?full=1">View the animated version</a></p></footer>
<script>{JS}</script>
</body>
</html>
'''

open(os.path.join(B.SRC, 'm_phone.html'), 'w', encoding='utf-8').write(PAGE)
print('m_phone.html', len(PAGE) // 1024, 'KB')
