# Dure SMS reader — results (coffee, Tetum + English)

Task: one farmer SMS -> one JSON record {lang, crop, kg, ask, any, grade, yn}. Metric: exact match (every field right).
Test 1: 51 hand-written messages (28 Tetum, 14 English, 6 unsupported language, 3 bare numbers). Test 2: 70 messages written by
Claude Sonnet 5.5 from a description of the service only (it never saw our generator or test 1), labels reviewed by hand.

| Reader | Test 1 exact | Test 2 exact | Median latency | Cost / 1,000 SMS | Needs internet |
|---|---|---|---|---|---|
| Rules only (first version) | 65% | 60% | <1 ms | $0 | no |
| Qwen2.5-0.5B, not fine-tuned (few-shot, test 3 only) | — | — | 5.9 s (fp32) | ~$0.02 (own server) | no |
| Qwen2.5-0.5B + LoRA (Dure small model), 8-bit GGUF | 88% | 71% | 1.8 s | ~$0.02 (own server) | no |
| Hybrid: rules engine when sure, small model otherwise | 100% | 87% | instant for 42–84%, else 1.8 s | ~$0.01 (own server) | no (rules part) |
| Claude Haiku 4.5 (API, few-shot) | 88% | 87% | 650 ms | $0.53 | yes |
| Claude Sonnet 5.5 (API, few-shot) | 100% | 99%* | 1,700 ms | $2.15 | yes |

\* Sonnet 5.5 also wrote test 2, so its score there is not a fair comparison.
Costs from list prices on platform.claude.com/docs/en/about-claude/pricing (Haiku 4.5 $1/$5, Sonnet 5.5 $2/$10 per million input/output tokens), measured token use (~365–490 in, 33–118 out per message), 2026-10-04. Latency measured from Seoul.

## Photo grader (A / B / C from one photo)

MobileNetV3-Small (ImageNet weights, torchvision) + a trained linear head. Data: 1,200 photos (300 per source grade) from the
Pre-Roast Coffee Bean Grading Dataset (MIT). Grade map: A → A, B and C → B, D (defective) → C. Split 70 / 15 / 15 by photo.
"Cheap phone" = every test photo shrunk to 64–96 px of detail, blurred, re-saved as JPEG at quality 25–50.

| Test (180 photos, never seen) | Accuracy | Answered | Accuracy when answered | Rest |
|---|---|---|---|---|
| Clean photos | 84% | 86% | 90% | asked for another photo |
| Cheap-phone photos | 88% | 84% | 93% | asked for another photo |

Abstain threshold 0.60, chosen on validation photos as the lowest giving ≥ 90% accuracy on answered photos.
Model file 3.8 MB; 11 ms per photo on one CPU thread.
Worst error: defective (C) beans graded A in 6 of 45 clean test photos. This is why the inspector's grade at pickup is the one paid,
and why a photo–sack mismatch costs the farmer nothing when the sack matches the photo.
Limits: single beans on a white backdrop, Robusta from India; parchment on a tarp in Ermera will look different. Needs local photos.

### Photos unlike the training set (novelty guard)

We then tried the grader on 10 real coffee photos from Wikimedia Commons (parchment with borer damage, sorted and rejected beans from
Tanzania, Colombian parchment). It answered with near-total confidence and was mostly wrong: damaged parchment came back grade A at 98%.
Confidence cannot catch this, so the exported model also returns a novelty score: the share of a photo's 576 image features that the
top 32 principal components of the training photos cannot explain. Threshold: 98th percentile of validation photos (0.299).

| Photos | Refused as "unlike training" |
|---|---|
| Test photos from the training dataset (180) | 0.6% |
| Real coffee photos from Wikimedia Commons (10) | 10 of 10 (novelty 0.36–0.72) |

Reproduce: `ai/photo/ood_export.py` (writes `grader.onnx` with outputs `probs` and `novelty`, `ood.json`, and the demo's cached results).
In the browser the scores differ slightly from Python because the canvas resizes the photo differently from PIL; the decisions on the six demo photos are the same.
Ten photos is a small check. It shows the guard does its job on obvious mismatches, not that it is calibrated for Ermera photos.


## Update 04:50 — rules engine improved, unseen test 3, hybrid routing

| Reader | Test 3 exact (60 unseen) | Notes |
|---|---|---|
| Rules engine (improved, frozen before test 3 existed) | **70%** | dev scores: test 1 100%, test 2 97% (both seen while improving, so not evidence) |
| Claude Haiku 4.5, few-shot | 87% | $0.53 per 1,000 messages, 650 ms median |
| Small model (Qwen2.5-0.5B + LoRA), 8-bit GGUF | **75%** | 1.8 s per message on 2 CPU cores, 531 MB file. Full precision (fp32, 2 GB): 72%, 5.1 s |
| Hybrid: rules engine when sure, small model otherwise | **80%** | 42% of texts answered instantly by the rules engine (all 25 right); fp32 model: 77% |

"Sure" rule (frozen after tuning on test 2 only): the rules engine recognised every word, made no spelling fix, saw at most two numbers,
and knows the language. On test 3 it was sure on 25 of 60 messages (42%) and **right on all 25**. The other 35 go to the small model.
If the model server is down, the rules engine answers all 60 (70% exact); every reading is texted back for the farmer to confirm.

### Small model, measured 07:30 (after the rules engine and both test sets were frozen)

Training: Qwen2.5-0.5B-Instruct + LoRA (r 16, alpha 32, dropout 0.05), 2,875 messages (2,625 synthetic + 250 real Tetum non-offers), 1 epoch,
batch 8, learning rate 3e-4, 360 steps on 2 CPU cores (about 3.3 hours). Adapter 35 MB. Merged and converted to 8-bit GGUF (531 MB) for llama.cpp.

| Test 3 (60 unseen), by language | Rules engine | Base model, few-shot | Small model (8-bit) | Hybrid (8-bit) | Claude Haiku 4.5 |
|---|---|---|---|---|---|
| Tetum (36) | **26** | 2 | 22 | 24 | 28 |
| English (16) | 10 | 2 | 15 | **16** | 16 |
| Other language, should be refused (6) | 4 | 0 | 6 | 6 | 6 |
| Bare number (2) | 2 | 0 | 2 | 2 | 2 |
| **All (60)** | 42 (70%) | 4 (7%) | 45 (75%) | **48 (80%)** | 52 (87%) |

Bold: best of the free, offline options.

What this shows:
- Fine-tuning is what makes the small model useful: the same model without it gets 7%.
- The model's gain is in English and in refusing other languages. **On Tetum the rules engine alone is better** (26 vs 22), so on Tetum
  the hybrid gains little over the rules engine and the model sometimes overrules a reading the rules engine had right. We did not re-tune
  the routing on test 3, because that would make it no longer an unseen test. More real Tetum messages are the next step.
- The hybrid is still the best free option (80%), keeps working without the server (falls back to 70%), and answers 42% of texts instantly.
- Claude Haiku is 7 points better but needs internet, sends farmers' messages abroad and costs about $0.53 per 1,000 texts.
- The 8-bit file scored slightly higher than full precision (75% vs 72%). On 60 messages that difference is noise; we report the 8-bit
  model because that is the one Dure would ship.

Where the small model goes wrong (test 2, the development set, 20 errors in 70): inventing a grade when the message has no
quality words (5, usually C); disagreeing on "a few black beans" (B by our labels, C by the model: 3); and number slips
("90 sen" as 90 instead of $0.90, 500 kg read as 50). These are exactly the readings the confirmation text exists for: Dure texts back
"40 kg, grade C, minimum 1.10 — OK?" and nothing counts until the farmer agrees.

Cost of the small model: one 2-vCPU, 4 GB server at $24/month is $0.033 an hour; 1,000 texts at 1.8 s each is about half an hour of
compute, so about $0.02 per 1,000 texts, and $0.01 for the hybrid (the model only reads 58% of texts). Sending the texts costs $30–$150 per 1,000.
