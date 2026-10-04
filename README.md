# Dure: Cooperate through messaging

Challenge 04, Agriculture (Annex B, Noor). World Bank Small AI for Development Hackathon, 3–4 October 2026.
Builder: Tae Yoon Moon (solo), University of Seoul. Licence: code MIT; synthetic data CC BY 4.0; illustrations and site text all rights reserved.

**Live:** https://dure-ai.pages.dev · demo: https://dure-ai.pages.dev/demo.html · photo grader: https://dure-ai.pages.dev/demo.html?photo=1 · Registry: https://dure-ai.pages.dev/sheet.html

Status (4 Oct 2026): story site, map demo with a live simulated market, on-device photo grader, on-device small-AI chat, and the Registry with an AI brief are built and deployed. All farmers, buyers, volumes and prices in the demo are synthetic; there has been no field test.

## What it is

Dure does a farmers' cooperative's jobs (a shared morning price, selling together, buyers who compete, payment, a record everyone can check) by plain text message, for smallholder coffee farmers in Letefoho, Ermera, Timor-Leste. It works in Tetum and English on any phone that can send SMS: no app, no data plan. Every deal also fills an automated Registry and a weekly brief for extension officers and policymakers.

## Problem statement

Because of this tool, Noor and the smallholder coffee farmers around her will sell their coffee together, to buyers who bid against each other above a floor the farmers set, and be paid by mobile money after the Thursday pickup, where they would otherwise sell alone to whichever trader's truck reaches the village, at the price he names. Four traders bought 98% of Ermera's coffee (Cristovão 2015, survey of 100 farmers, 2014).

## How it works (one week)

1. 06:30: every farmer and buyer gets the same price text, plus **Dure's suggestion**: recent trades, market prices, weather and road, and a suggested minimum. Buyers get a brief with the expected lot and a suggested bid range.
2. A farmer texts an offer in her own words (kilos, grade, minimum), Tetum or English, any spelling. Dure repeats back what it understood; nothing is recorded before she confirms.
3. She sends one phone photo and gets a preliminary grade A, B or C (or "send another photo" if no coffee beans can be seen).
4. Offers of every grade fill one blended basket. At 2,000 kg the auction opens; bids arrive until 17:00. Each farmer's minimum is her floor.
5. Each farmer decides: nobody is forced to trade.
6. Dure books the truck; buyers prepay. At Thursday pickup a person checks every sack by hand, and that grade is paid.
7. Payment goes to mobile wallets (the truck driver settles farmers without one at the next pickup). Reputation (trades, punctuality, matching quality) is updated; force majeure is excluded.
8. Every step is a row in the Registry, and a brief for extension services is written from those rows.

Demo prices are synthetic: grade B ≈ $2.45/kg, A ≈ $2.77, C ≈ $1.86 (the roadside trader in the story offers $2.25).

## What is AI, what is ordinary software

| Part | AI or software | Where it runs |
|---|---|---|
| Reading farmers' SMS (kilos, grade, price, yes/no, questions) in Tetum and English | **AI, hybrid**: rules engine on every text + Qwen2.5-0.5B fine-tuned with LoRA for texts the rules engine is unsure of | Rules engine in the browser; fine-tuned model as an 8-bit GGUF on a hub laptop (llama.cpp), optional in the demo via `?api=` |
| Off-script questions ("is today a good day to sell?", "why is the price low?") | **AI**: stock Qwen2.5-0.5B-Instruct reads the intent; the reply is composed from live market data, so every number is real | On the visitor's device (transformers.js, WebGPU or WebAssembly), ~3 s per reply on a 2-core CPU |
| Preliminary grade from one phone photo | **AI** (computer vision): CLIP ViT-B/32 (int8) + our 5-class head (A/B/C, roasted, not coffee) | On the visitor's device (onnxruntime-web), ~2 s per photo |
| Weekly brief for extension services | **Code computes findings; AI writes; a checker verifies every sentence** | In the browser |
| Morning price, suggestion, opening price, reputation, two pools | Algorithms on pre-accumulated synthetic records in the demo | In the browser |
| Pooling, auction, floor, escrow, payout, Registry | Ordinary software (must be predictable and auditable) | In the browser (simulated) |

Both on-device models are pre-downloaded in the background while the story page is read (Cache Storage), so the demo starts instantly. The site is served with cross-origin isolation headers so WebAssembly can use several threads.

## Tetum Benchmark Index

Exact match on every field (crop, kg, grade, ask, yes/no, intent, language).

| Reader | Test 3 (60 texts written by Claude Sonnet, frozen before scoring) |
|---|---|
| Rules engine v1 | 70% |
| Small model (Qwen2.5-0.5B + LoRA, 8-bit) | 75% |
| **Dure: rules engine + small model** | **80%** (English 16/16) |
| Claude Haiku 4.5 (large model via API) | 87% |
| Qwen2.5-0.5B without fine-tuning (few-shot) | 7% |

Later work: rules engine v2.1 scores 78% on test 3 on its own, and 98% on test 4 (80 texts we wrote, including questions); yes/no replies 100% on both. Test 4 was written by the builder, so it is not independent.

## Photo grader

Grading criteria follow the SCA green coffee defect classification; the grader looks only at photo-visible defects (black or mouldy beans, insect holes, broken beans, uneven drying/colour). Training: 900 synthetic piles composed from 1,202 real bean crops (Pre-Roast Coffee Bean Grading Dataset, MIT), labelled Wikimedia Commons photos, and 143 not-coffee photos. Leave-one-photo-out cross-validation: exact grade 46/58 (79%); the kind of answer (graded / roasted / not coffee) right on every bean photo; 34/35 not-coffee photos refused. Labels are ours, the test set is small, and there are no Timor-Leste farmer photos yet. The final grade is always the hand check at pickup.

Note: the training scripts for photo grader v2 and the reader v2 weights were lost when our build environment was reset on 4 Oct; the deployed grader (`site/src/assets/grader_v2.js`, head weights inlined) and the measured numbers above were preserved.

## Guardrails

- The farmer confirms what Dure understood before anything is recorded.
- Photo grades are preliminary; a person confirms the grade at pickup.
- AI never sets the price a farmer is paid: farmers set minimums, buyers bid, the auction clears.
- Chat replies take numbers only from live market data; Dure suggests and gives reasons, the farmer decides.
- Exclusion is never automatic; a person confirms any sanction.
- The brief only states numbers computed by code and cites the rows behind them.
- If the network or a model is unavailable, the rules engine keeps taking offers.

More: [RESPONSIBLE_AI.md](RESPONSIBLE_AI.md) · data sources: [DATA_CARD.md](DATA_CARD.md).

## Run locally

```bash
cd site
python build.py                 # builds src/ into dist/
cd dist && python -m http.server 8000
```

Open `index.html` (story), `demo.html` (demo; `?photo=1` opens the photo step, `?llm=0` turns the small-AI chat off, `?seed=N` replays a week), `sheet.html` (Registry). Serve over http, not file://. For multithreaded WebAssembly, serve with the headers in `site/src/_headers`.

## Repository layout

```
site/build.py           builds src/ into dist/
site/src/               site.html (story), demo_map.html (demo), sheet.html (Registry + brief), assets/ (grader_v2.js, sample photos,
                        Letefoho satellite base map, training-photo thumbnails), _headers, shared.css, figs.js, geo.json
site/dist/              built static site
ai/coffee/              SMS reader: synthetic data generator, LoRA training, test sets 1–3, rules.js (v2.1), evaluation, FastAPI service
ai/photo/               photo grader v1 (MobileNetV3) scripts and results
ai/brief/               brief findings + model writer + checker experiments
```

## Limitations

- No field test. Demo market, farmers and buyers are synthetic.
- SMS gateway, mobile-money escrow and payout are simulated.
- The on-device chat downloads ~500 MB once; slow devices may take longer than 3 s per reply.
- Tetum text data is scarce; test sets are synthetic or model-written.
- Price bands are anchored to published averages and need live calibration.
- Dure needs buyers who will bid and a pickup point with a trusted person.

## Next steps

1. Collect real Tetum messages (with consent) and retrain the reader with replay of earlier data.
2. Pilot one pickup point with a real SMS gateway and a mobile-money partner.
3. Collect real Ermera coffee photos with inspector grades and re-test the grader.
4. Let extension staff use the Registry brief and tell us which lines they cannot act on.

## Licence

Code: MIT. Synthetic data: CC BY 4.0. Illustrations and story text: © 2026 Tae Yoon Moon, all rights reserved. Third-party: Qwen2.5 (Apache-2.0); CLIP ViT-B/32 ONNX via Xenova (MIT); onnxruntime-web (MIT); transformers.js (Apache-2.0); bean photos: Pre-Roast Coffee Bean Grading Dataset (MIT) and Wikimedia Commons (credited per photo); satellite imagery © Esri, Maxar, Earthstar Geographics; roads © OpenStreetMap contributors; Labadain-30k+ (CC BY 4.0); Lenis (MIT); SheetJS CE (Apache-2.0).
