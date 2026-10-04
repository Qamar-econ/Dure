# Dure — Data card

Two kinds of data, as the challenge brief asks (section 7.2): data that shows the problem, and data the tool is built with.
Everything synthetic is labelled as synthetic. Checked on 4 October 2026.

## 1. Data that shows the problem (source, year, country)

| Claim used on the site | Figure | Year | Country | Source |
|---|---|---|---|---|
| Few buyers control the coffee market in Ermera | Four wholesalers bought 98% of coffee (CR4 = 0.98); survey of 100 farmers, Jun–Aug 2014 | 2015 (survey 2014) | Timor-Leste (Ermera) | Cristovão, C. dos S., *Analysis of marketing efficiency and marketing channel choice of organic coffee in Ermera Regency, Timor-Leste*, MSc thesis, Bogor Agricultural University, 2015; results in *Asian Journal of Marketing* (scialert.net, doi ajm.2015.12.26) |
| Price anchor for parchment | Farmers received USD 1.25/kg for parchment, 0.32/kg for cherry (2013 prices) | 2015 | Timor-Leste (Ermera) | same |
| Why farmers sell at harvest | Urgent cash needs, few processing machines, limited drying space | 2015 | Timor-Leste (Ermera) | same |
| Farmer organisations in Ermera weak | Farmer institutions described as not functioning; farmers' bargaining position weak | 2015 | Timor-Leste (Ermera) | same (SEARCA thesis abstract) |
| Pooling can raise incomes | 58% of 239 studies found farmer organisations raised members' incomes; marginalised farmers may need extra support first | 2020 | global review | Bizikova, L. et al., "A scoping review of the contributions of farmers' organizations to smallholder agriculture", *Nature Food* 1, 2020 |
| Starting a cooperative is slow and costly | 3–4 years to launch; minimum share capital USD 1,000; 15 founders; assembly, board and auditor | — | Timor-Leste | 3–4 years: KOICA agricultural value-chain cooperative case. The legal minimums are checked against Decree-Law No. 16/2004 on cooperatives (English translation, ADB Law and Policy Reform portal): at least 15 founders aged over 17 (art. 11.4), initial capital at least USD 1,000 (art. 18.2), shares of USD 5 (art. 20.1), at least three shares per member (art. 19.2), bodies elected for 4 years (art. 40.1). Registration moved to SERVE under Decree-Law No. 37/2023. |
| Coffee harvest season | May to September | 2025–26 | Timor-Leste | Sucafina origin page; Exploring Timor-Leste (Ermera) |
| Ermera's share of national coffee | "Close to half" | 2002 | Timor-Leste | Overview of the coffee sector in East Timor (oook.info); Wikipedia "Coffee industry of Timor-Leste" (~50%) |
| Power cuts | 40% of firms had outages in the past year; affected firms lost 9.4% of sales; 0.8 outages in a typical month | 2015 | Timor-Leste | World Bank Enterprise Surveys (via WDI indicators IC.ELC.OUTG.ZS, IC.FRM.OUTG.ZS, IC.ELC.OUTG) |
| Power cuts, recent | Utility head: power "continues to go out" in Dili (maintenance, storms); national hospital switches to generators at each cut; outages up to 24 h in Viqueque | 2022–2023 | Timor-Leste | Tatoli (state news agency), 1 Dec 2022, 6 Jun 2023, 24 Apr 2023 (Tetum articles found in Labadain-30k+) |
| Outages under-reported | 35.7% of 111 Dili electricity consumers don't report an outage | 2022 | Timor-Leste (Dili) | TANE consumer association survey, reported by Tatoli, 4 Jul 2022 |
| Dili grid reliability | 102 outage incidents across 11 feeders in 2021; SAIDI 2.6 h/customer/year | 2021 | Timor-Leste (Dili) | Suheta, Da Costa et al., EDTL reliability index analysis, JREEC (ITATS) — included for balance |
| Cost of sending SMS | Timor Telecom bulk SMS USD 0.03–0.085 per message; international gateways USD 0.08–0.15 | 2025–26 | Timor-Leste | timortelecom.tl SMS marketing price list; sent.dm East Timor pricing |
| Mobile money exists and has reached Ermera | First mobile-money pilot (BNU Mobile with Timor Telecom) launched in Dili, Baucau, Ermera and Lautem; Telemor's Mosan e-wallet to integrate with BNCTL | 2014; 2025 | Timor-Leste | UNCDF, 4 Dec 2014; Tatoli, 4 Apr 2025 |
| Cost of a large model | Claude Haiku 4.5 USD 1 / 5, Sonnet 5.5 USD 2 / 10 per million input / output tokens | 2026 | — | platform.claude.com pricing page |
| Cost of one small server | 2 vCPU, 4 GB: USD 24 / month | 2026 | — | DigitalOcean droplet pricing |
| Noor's situation | Basic phone, no wifi, phone at home during the day, local language; no independent price at harvest; extension officer at most twice a year; no farmer registry | 2026 | (fictional, built from World Bank work) | World Bank / Hack-Nation challenge brief, Annex B |

Gaps we could not fill: a recent (post-2015) farm-gate parchment price for Ermera; rural or Ermera-specific outage statistics; farmers per extension officer; feature-phone and mobile-money ownership in Ermera. The WFP food price data on HDX was not reachable from our environment and, as far as we know, does not cover coffee.

## 2. Data we build with

| Dataset | Source | Licence | Size | What it covers | What it does NOT cover |
|---|---|---|---|---|---|
| Synthetic SMS (training) | Generated by `ai/coffee/gen.py` from templates, with random typos, word order, Tetum/Indonesian/Portuguese/English number words, price formats | Project (ours) | 2,625 synthetic messages + 250 real Tetum sentences (below) | Offers, single-question replies, YES/NO, unsupported languages, Tetum and English | Real farmers' messages; voice; Tetum dialects; very long or off-topic messages |
| Labadain-30k+ | de Jesus & Nunes, LREC-COLING 2024 (SIGUL); Hugging Face `gabrieljesus/Labadain-30k-plus-tetun` | CC BY 4.0 | 33,550 documents, 12.4 M tokens (native-audited Tetum web text, 2001–2023) | (1) 250 short real Tetum sentences used as "not an offer" training messages; (2) checking every Tetum word in our vocabulary is real (e.g. "bolor" never appears, so it was replaced by "fuhuk"; parchment = "kafé kulit mutin"); (3) Tetum news on power cuts and coffee prices | SMS style, spelling errors, rural speech; news and web text only |
| Test 1 | Hand-written (`ai/coffee/test_cases.py`), never produced by the generator | Project | 51 messages (28 Tetum, 14 English, 6 other languages, 3 bare numbers) | Development test | Same author as the generator: not independent |
| Test 2 | Written by Claude Sonnet 5.5 from a description of the service only; labels reviewed by hand | Project (model-generated) | 70 messages | Development test | Synthetic; used while improving the rules engine, so not evidence for it |
| **Test 3 (headline)** | Fresh batch written by Claude Sonnet 5.5 after the rules engine was frozen; labels reviewed by hand after scoring | Project (model-generated) | 60 messages (36 Tetum, 16 English, 6 other) | The score we report for every reader | Synthetic; Sonnet wrote it, so Sonnet's own score on it is not reported |
| Pre-Roast Coffee Bean Grading Dataset | SamruddhK, Hugging Face `SamruddhK/coffee-bean-grading-dataset` | MIT | 3,877 photos, grades A–D (we use a balanced 1,200-photo subset) | Training and testing the photo grader (A → A; B and C → B; D → C) | Beans photographed one at a time on a white backdrop under indoor light in Coorg, India (Robusta) — not parchment on a tarp, not Timor-Leste, not a 0.3 MP feature-phone photo. In use, the photo would need splitting into beans first. |
| Field photos for the novelty check | Wikimedia Commons: Forest & Kim Starr (CC BY 3.0 US); Harald Ulver, Michael C. Wright, Felipe Quijano (CC BY-SA 4.0). Per-photo title, page, author and licence in `ai/photo/commons/meta.json` | As listed per photo | 10 photos | Checking that the grader refuses photos unlike its training set; two are shown in the demo with credit | Not used for training; too few to calibrate anything |
| Letefoho Registry (sheet) | Generated by `site/tools/gen_sheet_data.py` (seeded) | Project | 90 farmers, 141 offers, 6 auctions, 3 weeks | Showing how the Registry, prices and the daily brief behave, including a rain shock in one village | Everything: it is synthetic. Village names are real places around Letefoho; farmers are pseudonymous IDs. |
| Base model | Qwen2.5-0.5B-Instruct, Hugging Face `Qwen/Qwen2.5-0.5B-Instruct` | Apache-2.0 (checked in the downloaded LICENSE file) | 494 M parameters | Starting point for the SMS reader (LoRA fine-tune) | Tetum is barely represented in its pre-training data |

## Synthetic data labelling
- Every synthetic set is named as such here, in the README and on the site ("Illustrative example", "Synthetic data for demonstration").
- Model-written test sets (2 and 3) are kept apart from training data; the generator drops any training message that matches a test message.

## Results that depend on this data
See `ai/coffee/RESULTS.md`. Headline (test 3, unseen): rules engine 70% exact match; Claude Haiku 4.5 87%; small model (8-bit) 75%; hybrid 80%; base model without fine-tuning 7%. Photo grader: 88% on cheap-phone test photos (93% when it answers); refuses 10 of 10 real field photos unlike its training set, and 0.6% of test photos.
