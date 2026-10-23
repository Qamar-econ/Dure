# Dure: Cooperate through messaging

**Winner, Agriculture track · World Bank Small AI for Development Hackathon 2026** (Challenge 04, Annex B: Noor)

Dure does a farmers' cooperative's jobs by plain text message. Smallholder coffee farmers in Letefoho, Ermera, Timor-Leste, get a fair morning price, sell together, have buyers compete for their coffee, get paid, and build a record that earns trust. It all happens in Tetum or English, on any phone that can send SMS. There is no app and no data plan.

| | |
|---|---|
| **Live site** | https://dure-ai.pages.dev (phones and tablets get the mobile edition, [`m.html`](https://dure-ai.pages.dev/m.html)) |
| **Interactive demo** | https://dure-ai.pages.dev/demo.html: a full market week in your browser, with nothing to install and no server |
| **Photo grader** | https://dure-ai.pages.dev/demo.html?photo=1 |
| **Farmer Registry** | https://dure-ai.pages.dev/sheet.html: eight weeks of synthetic data from Letefoho, plus a brief for extension officers |
| **Videos** | [Promotion](https://www.youtube.com/watch?v=fv_WMSEmthA) · [Meet the founder](https://www.youtube.com/watch?v=981bf_9D56U) · [Product demo](https://www.youtube.com/watch?v=ZacBiMIBw34) · [Technical walkthrough](https://www.youtube.com/watch?v=enQjGFoiuKY) |
| **Builder** | Tae Yoon Moon (solo), University of Seoul · taeyoonmoon@uos.ac.kr |

> **Status.** This is a working prototype. All farmers, buyers, volumes and prices in the demo and the Registry are synthetic, and there has been no field test yet. The SMS gateway and mobile money are simulated. The AI models and the numbers reported below are real.

---

## In one minute

- **The problem.** Ermera grows close to half of Timor-Leste's coffee, yet four traders in Dili bought 98% of it (Cristovão 2015, survey of 100 farmers, 2014). In the rainy season, one trader's truck makes it up the hill and names its price. Noor can't check that price, and there is no one else to ask.
- **Why cooperatives don't solve it.** Farmer organisations raised members' incomes in 58% of 239 studies (Bizikova et al., *Nature Food* 2020). But starting one in Timor-Leste takes about 3–4 years, $1,000 in share capital and 15 founders, while a typical coffee household earns about $250 a year. The process also tends to end in a fight over power, and women farmers are easily left out.
- **What Dure keeps.** Pooling the harvest, buyers bidding for the whole lot, one shared truck and pickup point, and a record that earns trust.
- **What Dure drops.** The legal entity, the $1,000 in share capital, the board to fight over, and the few who decide for everyone. Nobody has to join, and anyone can leave at any time.
- **Where the AI is.** Small models read Tetum texts and grade coffee from one photo. Simple, auditable algorithms set prices, score reputation and split the two markets. Each morning, code computes a brief for extension officers, and a checker verifies every sentence in it. A person always makes the final call.

## How it works (one week)

Noor's steps follow the live site's *How it works* section. The prices are the site's illustrative week.

1. **A price and a plan to start the day.** At 06:30 every farmer and buyer gets the same price text (A $3.17–3.23, B $2.80–2.86, C $2.12–2.18 per kg). It comes with *Dure's suggestion*: recent trades, the market, weather and road, and a suggested minimum. Buyers get a brief with the expected lot and a suggested bid range.
2. **From Tetum text to quality grading.** Noor texts in her own words, with typos and all: `bondia! kafe 40kilu diak los.. fan 2.84 bele?`. Dure repeats back what it understood (coffee, 40 kg, grade A, ask $2.84/kg), and nothing is recorded until she confirms. She then sends one photo and gets a first-look grade (A, 93%).
3. **Leverage with a blended basket.** Coffee of every grade goes into one pool. In the example, the pool closes at 1,890 kg from 22 farms.
4. **Interactive fair auction.** Bidding opens a little under Dure's fair-price estimate ($2.74/kg, grade B basis) and closes at 17:00. The lot clears at $2.81/kg, and each grade is paid by its own weight: A $3.14, B $2.78, C $2.11.
5. **Autonomy: each farmer decides.** Each farmer's minimum is her floor, and nobody is forced to trade. Noor sells 40 kg × $3.14 = $125.60.
6. **Collective supply chain.** The buyer prepays ($4,250.85 for 1,530 kg from 18 farms), and Dure books the truck. At the Thursday pickup, a person checks every sack by hand, and that grade is final.
7. **Simple and credible payment.** The prepayment is released after delivery and split to mobile wallets. Farmers without one are paid by the truck driver at the next pickup.
8. **Every deal builds trust.** Reputation updates from the number of trades, punctuality and whether the grade matched the photo (Noor's score goes from 79% to 83%). Force majeure is never counted. Every step is also a row in the Registry.

Before Dure, the roadside trader in the story offers Noor $2.25/kg. The interactive demo simulates a fresh market week on every run (`?seed=N` replays a week).

## Two markets, one ladder

Reputation lets Dure run two markets at once. The site's *Technical walkthrough 4–5* covers this.

- **Blended pool:** every farmer can sell here, every week, to bulk buyers in Dili. It builds economies of scale.
- **Fixed pool:** one grade, a fixed buyer, every week (A → specialty roasters, B → export contracts, C → local market). The higher a farmer's reputation, the larger the share of her harvest that goes to steady orders. Dure AI sets the split every week.
- **Farm size doesn't count.** In the site's example, Noor (2 ha) scores 92 and a 30-ha grower scores 64. Buyers are scored too, on paying on time (Exporter, Dili: 88%).

In the demo, reputation and the fixed pool run on pre-accumulated synthetic records.

## What is AI, and what is ordinary software

| Part | AI or software | Where it runs |
|---|---|---|
| Reading farmers' SMS (kilos, grade, price, yes/no, questions) in Tetum and English | **AI, hybrid.** A rules engine reads every text. A Qwen2.5-0.5B model fine-tuned with LoRA reads the texts routing sends it: English, other languages, and anything the rules engine could not place. | Rules engine on the phone or hub. The fine-tuned reader runs as an 8-bit GGUF on the hub laptop (llama.cpp). The web demo runs the rules engine only for offers (see below). |
| Off-script questions ("is today a good day to sell?", "why is the price low?") | **AI.** Stock Qwen2.5-0.5B-Instruct reads the intent. The reply is composed from live market data, so every number is real. | On the visitor's device (transformers.js, WebGPU or WebAssembly), ~3 s per reply on a 2-core CPU |
| Preliminary grade from one phone photo | **AI (computer vision).** CLIP ViT-B/32 (int8) plus our own 5-class head (A/B/C, roasted, not coffee) | On the visitor's device (onnxruntime-web), ~2 s per photo |
| Daily brief for extension services | **On the site: code computes the findings and fills a hand-written phrase bank; a checker verifies every sentence.** A small model (Qwen2.5-3B) writing the sentences instead was tested offline (`ai/brief/`) | Site version in the browser; the model version on a laptop, not on the site |
| Morning price, suggestion, opening price, reputation, two pools | Algorithms run on pre-accumulated synthetic records in the demo | In the browser |
| Pooling, auction, floor, escrow, payout, Registry | Ordinary software, which must be predictable and auditable | In the browser (simulated) |

On phones and tablets, the 500 MB Qwen model does not fit in a browser tab's memory. There, the Small AI is Dure's own question-topic model (`ai/intent`):

- **Design:** a fastText-style classifier (hashed word and character n-grams, 32-d averaged embedding, 8 topics).
- **Training:** in numpy, on 4,480 synthetic questions in English, Tetum, Indonesian and Portuguese.
- **Size and speed:** exported as int8 (`site/src/assets/intent.json`), 0.2 MB gzipped, under 1 ms per question.
- **Accuracy:** 222 of 227 hand-written test questions right (`ai/intent/test*.json`).

On computers, the topic model also cross-checks Qwen's pick. Either way, the reply answers the exact question (sell or keep, why the price moved, outlook, buyers, weather and road, quality, pool) from the live simulated market. To retrain it, run `cd ai/intent && python3 gen.py && python3 train.py`.

Both on-device models download in the background while the visitor reads the story page (Cache Storage), so the demo starts instantly. The site is served with cross-origin isolation headers, which let WebAssembly use several threads.

## The fine-tuned reader and the web demo

Dure has two small models, and they have different jobs.

1. **The fine-tuned reader** (Qwen2.5-0.5B + LoRA, current adapter in `ai/coffee/lora_v2/`, 35 MB).
   - **Training data:** 2,625 synthetic SMS and 250 real Tetum sentences (Labadain-30k+) for v1 (`ai/coffee/lora/`), then one short extra pass (39 minutes on 2 CPU cores) on 847 targeted synthetic SMS plus 450 replayed v1 examples for v2 (`gen2.py`, `train2.py`).
   - **Job:** it turns an unclear offer into fields (kilos, grade, minimum, yes/no). Alone it scores 85% on test 3 and 83% on the held-out test 6; with the rules engine, 90% and 86% (see the Tetum Benchmark Index below).
   - **Where it runs:** it is built for the **hub laptop at the pickup point**. v1, merged and quantised to an 8-bit GGUF (531 MB), reads a text in 1.8 s on two CPU cores with llama.cpp (`ai/coffee/infer_gguf.py`). v2 was measured at full precision (about 3 s per text); its 8-bit file has not been built yet.
2. **The on-device question reader** (stock Qwen2.5-0.5B-Instruct, ONNX). It runs in the visitor's browser and only picks the topic of an off-script question (one of eight letters). The reply is written from live market data.

**What runs on the live site, and what the benchmark measures.** The web demo reads offers with the rules engine only, and uses the second model for questions. The fine-tuned reader and the routing measured in the Tetum Benchmark Index run on the hub laptop and in `ai/coffee/`, not on the site. (The demo has a developer option, `?api=URL`, that sends offers to a hosted reader; it predates routing v2, and the site does not link to a hosted reader.) We kept the fine-tuned reader out of the web demo on purpose:

- **The demo has to run with no server.** Anyone who opens the link gets the whole week in their own browser, with nothing for us to host or keep alive.
- **It matches where each model lives in the real service.** Farmers text from basic phones, so offers are read on the hub laptop, not on the farmer's phone. Shipping the reader to every visitor would show a deployment Dure does not use.
- **Speed in a browser.** The reader writes a short structured answer (about 30 tokens). In a typical laptop browser that takes several times longer than the 1.8 s it needs under llama.cpp. The question reader answers in one step (about 1.5–3 s).

To see the fine-tuned reader at work, run `ai/coffee/infer_gguf.py` on the merged GGUF. The benchmark predictions it produced are in `ai/coffee/pred_gguf_test3.json`, and `ai/coffee/score.py` scores them.

## Tetum Benchmark Index

Tetum is one of the languages large language models overlook most. A text counts as correct only if every field is right (crop, quantity, grade, price and intent).

Dure reads every text with a rules engine and, when routing says so, a small fine-tuned model. Routing sends each text to the reader that handles it best: the rules engine's sure answers and the Tetum messages it understood stay with it; English, messages in other languages, and anything it could not place go to the model (`ai/coffee/hybrid2.py`).

| Reader (current versions) | Test 3 (60) | **Test 6 (64, held out)** |
|---|---|---|
| **Dure: rules engine v2.1 + small model v2, routing v2** | **90%** (54/60) | **86%** (55/64) |
| Claude Haiku 4.5 (large model over the internet) | 87% (52/60) | not run |
| Small model v2 alone (Qwen2.5-0.5B + LoRA) | 85% (51/60) | 83% (53/64) |
| Rules engine v2.1 alone | 78% (47/60) | 78% (50/64) |
| Qwen2.5-0.5B without fine-tuning (examples only) | 7% (4/60) | — |

- **Test 3:** 60 SMS (36 Tetum, 16 English, 6 in languages Dure should decline, 2 bare numbers), written by Claude Sonnet on 4 Oct and frozen before any reader was scored. Its errors were looked at again on 23 Oct before the model was retrained, so read 90% as optimistic.
- **Test 6:** 64 new SMS written on 23 Oct (by Claude Opus, same conventions) and committed before any reader saw them. Routing and model were chosen on tests 1, 2 and 5 only, and the choice was committed before test 6 was scored once. **This is the clean number.**
- **What changed on 23 Oct:** with the improved rules engine (v2.1), the old routing ("rules engine if sure, else model") tied the rules engine at 78%, because the model overruled correct Tetum readings. New routing alone lifts the hybrid to 88% on test 3 and 86% on test 6; the retrained model adds 2 more points on test 3. The rules engine itself was not changed.
- **History:** 4 Oct, rules engine v1: rules engine 70%, small model 75% (8-bit), hybrid 80% on test 3.
- **Test 4:** on 80 texts we wrote ourselves, including questions, the rules engine scored 98% alone and 99% with the small model (4 Oct). Test 4 was written by the builder, so it is not independent.
- **Cost:** reading a text adds under 1% to the cost of sending the SMS (API list prices).
- **Limits:** every test text is synthetic (written by AI models, not farmers), so these are benchmark scores, not field accuracy, which is likely lower. 64 texts is a small set: one text is 1.6 points, so 86% has an uncertainty of roughly ±8 points. Test 6 and the retraining data were written by the same author (Claude Opus), so the small model's own gain on test 6 (62% → 83%) may be partly flattered; the hybrid's gain over the rules engine came from routing, which was designed without test 6. An independent test set written by Tetum speakers, and later real messages collected with consent, are needed for a field number.
- **No test text was trained on.** The generator drops any exact test message; only short generic replies such as "60 kilu" or "1.40" share a pattern with training data, and most of those were already in the 4 Oct data.
- **Details and protocol:** see [`ai/coffee/RESULTS.md`](ai/coffee/RESULTS.md).

## Photo grader

- **Criteria:** grading follows the SCA green coffee defect classification. The grader looks only at the defects a photo can show: black or mouldy beans, insect holes, broken beans, and uneven drying or colour.
- **Training data:**
  - 900 synthetic piles composed from 1,202 real bean crops (Pre-Roast Coffee Bean Grading Dataset, MIT)
  - labelled Wikimedia Commons photos
  - 143 photos with no coffee in them
- **Results (leave-one-photo-out cross-validation):**
  - exact grade: 46 of 58 photos (79%)
  - kind of answer (graded, roasted or not coffee): right on every bean photo
  - photos with no coffee: 34 of 35 refused
- **Limits:** the labels are ours, the test set is small, and there are no Timor-Leste farmer photos yet. The final grade always comes from the hand check at pickup.

Note: the training scripts for photo grader v2 and for a later reader experiment (v2) were lost when our build environment was reset on 4 Oct. What survived is the deployed grader (`site/src/assets/grader_v2.js`, with the head weights inlined), the benchmarked reader (the LoRA adapter in `ai/coffee/lora/`) and the measured numbers above.

## The Registry and the daily brief

A farmer Registry is valuable but labour-intensive and expensive to keep up. In Dure, every deal leaves a row, so the Registry builds itself.

Each morning, code computes findings from those rows and writes them up from a hand-written phrase bank, and a checker drops any sentence whose numbers it cannot trace back to the rows. Letting a small model (Qwen2.5-3B, on a laptop) write the sentences was tested offline: with code doing the analysis and the same checker in front, it kept 9 of 10 sentences on the July data and 12 of 17 on a held-out register. That model version is not shown on the site. Extension officers visit about twice a year, and the brief helps them use those visits where they matter. Dure stays out of how farmers farm. Try the [sample Registry](https://dure-ai.pages.dev/sheet.html); the brief experiments are in [`ai/brief/`](ai/brief/).

## Guardrails

- The farmer confirms what Dure understood before anything is recorded.
- Photo grades are preliminary. A person confirms the grade at pickup.
- AI never sets the price a farmer is paid. Farmers set minimums, buyers bid, and the auction clears.
- Chat replies take numbers only from live market data. Dure suggests and gives reasons; the farmer decides.
- Exclusion is never automatic. A person confirms any sanction.
- The brief only states numbers computed by code and cites the rows behind them.
- If the power, the network or a model fails, the rules engine keeps taking offers. The small model rechecks them later, and any change goes back to the farmer to confirm.
- Farmers' names and numbers stay with Dure. The ministry's Registry shows pseudonymous IDs and village totals, and only for farmers who said yes.

More detail: [RESPONSIBLE_AI.md](RESPONSIBLE_AI.md) · data sources: [DATA_CARD.md](DATA_CARD.md).

## Run locally

```bash
cd site
python build.py                       # builds src/ into dist/
python tools/mobile/build_phone.py    # regenerates the phone edition (run before build.py after story changes)
cd dist && python -m http.server 8000
```

Then open these pages, over http rather than file://:

| Page | What it is | Options |
|---|---|---|
| `index.html` | The story | Phones and tablets are sent to `m.html`; add `?full=1` to stay. |
| `m.html` | The mobile edition | |
| `demo.html` | The demo | `?photo=1` opens the photo step, `?llm=0` turns the small-AI chat off, `?seed=N` replays a week. |
| `sheet.html` | The Registry | |

For multithreaded WebAssembly, serve with the headers in `site/src/_headers`.

Deployment: every push to `main` that touches `site/**` is built and published to Cloudflare Pages by `.github/workflows/deploy-cloudflare.yml`.

## Repository layout

```
site/build.py           builds src/ into dist/ (dist/ is not committed; the deploy workflow builds it)
site/src/               site.html (story, PC), m_phone.html (phone and tablet edition, generated), demo_map.html (demo),
                        sheet.html (Registry + brief), assets/ (grader_v2.js, sample photos, Letefoho satellite base map,
                        training-photo thumbnails, World Bank logo used with permission), _headers, shared.css, figs.js,
                        geo.json, m_*.json (phone figures), m_classic.html (earlier phone edition, source only: not published; build_phone.py builds on its tools)
site/tools/mobile/      phone edition generator: build_phone.py (+ phone.css, phone.js) on top of build_mobile.py and its
                        figure/scene extractors
site/tools/             gen_sheet_data.py, check_sheet.js (synthetic Registry data)
docs/                   redirects from the old GitHub Pages address to dure-ai.pages.dev
ai/coffee/              SMS reader: rules.js (v2.1), synthetic data generators (gen.py, gen2.py), LoRA training (lora/, lora_v2/),
                        routing (hybrid2.py), test sets 1–6, evaluation, GGUF inference
ai/intent/              on-device question-topic model for phones and tablets (generator, numpy trainer, test sets)
ai/photo/               photo grader v1 (MobileNetV3) scripts and results
ai/brief/               brief findings + model writer + checker experiments
```

## Limitations

- There has been no field test. The demo market, farmers and buyers are synthetic.
- The SMS gateway, mobile-money escrow and payout are simulated.
- The on-device chat downloads ~500 MB once. Slow devices may take longer than 3 s per reply.
- Tetum text data is scarce, and the test sets are synthetic or model-written.
- Price bands are anchored to published averages and need live calibration.
- Dure can't fix a washed-out road. It needs buyers who will bid, and a pickup point with a trusted person.

## Next steps

1. Collect real Tetum messages (with consent) and retrain the reader, replaying earlier data.
2. Pilot one pickup point with a real SMS gateway and a mobile-money partner.
3. Collect real Ermera coffee photos with inspector grades and re-test the grader.
4. Let extension staff use the Registry brief and tell us which lines they cannot act on.

## Licence

| What | Licence |
|---|---|
| Code | MIT ([LICENSE](LICENSE)) |
| Synthetic data | CC BY 4.0 |
| Illustrations and story text | © 2026 Tae Yoon Moon, all rights reserved |

Third-party components:

- Models and runtimes: Qwen2.5 (Apache-2.0); CLIP ViT-B/32 ONNX via Xenova (MIT); onnxruntime-web (MIT); transformers.js (Apache-2.0)
- Photos: Pre-Roast Coffee Bean Grading Dataset (MIT); Wikimedia Commons (credited per photo)
- Maps: satellite imagery © Esri, Maxar, Earthstar Geographics; roads © OpenStreetMap contributors
- Text data: Labadain-30k+ (CC BY 4.0)
- Site libraries: Lenis (MIT); SheetJS CE (Apache-2.0)
- The World Bank logo is used with permission.
