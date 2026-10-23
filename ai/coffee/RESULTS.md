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

## Update 23 Oct 2026: re-scored with the current rules engine (v2.1)

The rules engine in the live demo (`site/src/demo_map.html`) is byte-for-byte the same as `rules.js` (v2.1). We re-ran it on all three
test sets and rebuilt the hybrid from it and the small model's saved 8-bit readings (`pred_gguf_test*.json`; the model itself has not
changed since 4 Oct). The routing rule ("sure") is the one built into v2.1; we did not tune anything on test 3.

| Test 3 (60, frozen), by language | Rules engine v1 | **Rules engine v2.1** | Small model (8-bit) | **Hybrid v2.1** | Claude Haiku 4.5 | Base model, few-shot |
|---|---|---|---|---|---|---|
| Tetum (36) | 26 | **28** | 22 | 23 | 28 | 2 |
| English (16) | 10 | 13 | 15 | **16** | 16 | 2 |
| Other language, should be declined (6) | 4 | 4 | 6 | **6** | 6 | 0 |
| Bare number (2) | 2 | 2 | 2 | 2 | 2 | 0 |
| **All (60)** | 42 (70%) | **47 (78%)** | 45 (75%) | **47 (78%)** | 52 (87%) | 4 (7%) |

| All test sets, exact match | Test 1 (51) | Test 2 (70) | Test 3 (60, frozen) |
|---|---|---|---|
| Rules engine v2.1 | 100% | 97% | 78% |
| Hybrid v2.1 (rules engine when sure, small model otherwise) | 100% | 89% | 78% |

- v2.1 is sure more often: on test 3 it answers 34 of 60 texts (57%) itself, and is right on 33 of them; 26 go to the small model
  (with v1: 25 sure, all right, 35 to the model).
- **The hybrid no longer beats the rules engine on its own.** It gains on English (13 → 16) and on declining other languages (4 → 6),
  and loses the same amount on Tetum (28 → 23), where the model overrules readings the rules engine had right. This is the pattern
  noted on 4 Oct, now larger because v2.1 got better at Tetum and the model did not change.
- Tests 1 and 2 were seen while v2.1 was written, so their scores are not evidence. Test 2 shows the same pattern (rules engine 97%, hybrid 89%).
- Caveat: v2.1 was written after test 3 and its error review (`test3_review.md`) existed, so test 3 is no longer strictly unseen
  for v2.1. Read 78% as a re-score, not a fresh blind test.
- Next: route Tetum offers that the rules engine reads in full to the rules engine, and retrain the small model on real Tetum messages.
  Any new routing must be judged on a new frozen test set, not test 3.

Reproducibility check (23 Oct): we merged the LoRA adapter in `lora/` into a fresh download of Qwen2.5-0.5B-Instruct and re-ran
`infer.py` (full precision, greedy) on all three test sets. Every reading matched the saved `pred_model_test*.json` (51/51, 70/70,
60/60 identical; 88%, 70%, 72%), about 3–4 s per text on 2 CPU cores. The 8-bit GGUF was not rebuilt this time; its saved readings are used above.

Files: `pred_rules_v21_test*.json`, `pred_hybrid_v21_test*.json` (from `node rules.js OUT TEST` and `hybrid.py`), scored by `score.py`.
