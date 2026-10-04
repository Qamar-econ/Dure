# Responsible AI note: Dure

Scope: the prototype and the pilot design. Dure has not run with real farmers. Everything below is a design commitment or a plan to test, and says so where it is not yet verified.

## 1. The limits from the brief (section 06), and how Dure meets each

| Brief rule | Dure |
|---|---|
| Runs on a device the user already has | Plain SMS on any basic phone. No app, no data. Photos need a camera phone; without one the farmer sells ungraded and a person grades at pickup. |
| Core feature works offline | Taking an offer works with the rules engine alone. If the server is down the rules engine keeps taking offers; the model rechecks later and any change goes back to the farmer to confirm. The whole service can run on one machine without internet: on 4 Oct we served the 8-bit reader (531 MB) from a local file with Hugging Face offline mode, about 1.8 s per message on 2 CPU cores, and the static pages and rules engine need no server at all. Not yet tried on a real laptop at a pickup point with the network physically off. |
| Model files small enough to side-load or send over a weak connection | Qwen2.5-0.5B-Instruct with a LoRA adapter, quantised. Photo grader: 3.7 MB (ONNX). SMS reader: LoRA adapter about 35 MB on top of the 0.5B base model (about 1 GB in fp16; quantised size in RESULTS.md). |
| At least one interaction in a local language | Tetum and English. Expect the question about a less-supported language: the rules and the confirmation step make Dure usable with little data, but accuracy in any new language must be measured first. |
| Human in the loop: a person makes the final call; the tool informs and flags what it is unsure of; it does not act on the user's behalf; an agentic flow must check in with the user | Farmer confirms every reading. Person confirms the grade at pickup. Person confirms any exclusion. Experts decide on the brief. Payments are released by the auction and pickup rules, not by the AI. |
| Avoid hallucinations | The reader outputs a fixed schema (kilos, grade, price, intent); anything outside it is "not sure, ask a person". The daily brief: code computes and ranks every finding; the small model writes sentences that must cite the findings they use; a checker drops any sentence whose numbers are not in the cited findings, that calls a rise a fall, or that states a cause. If too little survives, the template brief is shown. Each claim links to rows. |
| Pass/fail fail-safe: "not sure, ask a person" instead of guessing | Reader abstains and asks; photo grader abstains below 60% confidence ("send another photo") and refuses photos unlike its training set (novelty guard: 10 of 10 real field photos refused); brief states what it cannot tell. |

## 2. Privacy

- **Pseudonymous IDs.** The Registry and brief use IDs (for example LTF-041), not names. The link from ID to phone number is held only by the service operator.
- **Minimum data.** Phone number, village, farm size, offers, volumes, grades, prices, payouts, reputation. No location tracking, no contacts, no photos kept beyond what grading needs. Proposed: photos are kept 30 days after pickup for disputes, then deleted. In the demo, grading runs in the browser and no photo is uploaded.
- **Consent by SMS.** On joining, the farmer gets a short text in Tetum or English explaining what is stored and who sees it, and replies to agree. Consent to share with the ministry is a separate yes/no, asked separately, and the answer does not affect her access to the auction. She can withdraw by SMS. In the demo scenario 61 of 90 farmers consent to sharing (synthetic).
- **What the ministry and extension services see.** Village-level aggregates, and individual rows only for farmers who consented. Farmers who did not consent still count in village totals but appear without any ID (proposed: a village total covering fewer than 5 farmers is not shown).
- **Lost or shared phones.** The phone number is the credential in the prototype, which is weak. Before payout, a person at pickup checks the farmer in person; mobile-money payout uses the provider's own PIN. Phone-sharing within a household is common; payout to a number other than the registered one is blocked (design rule, not yet tested).
- **Where data sits.** One server or hub laptop controlled by the operator. Proposed: a server in Dili run by the pilot operator, who holds the keys. Farmer messages are never sent to a third-party AI API; the large-model comparison in RESULTS.md used synthetic test messages only.
- **Buyers.** Buyers see bids, pooled volumes and grades. They do not see farmer minimums or identities before the auction clears.

## 3. Consent and honesty about the AI

- Messages from Dure say it is an automatic system. Farmers can text a word (for example HELP) to ask for a person (proposed: HELP, answered by the pickup-point coordinator by phone).
- The photo grade is described as "preliminary" in the message itself.
- Dure asks for the minimum price instead of suggesting one in a way that could push her. The morning band is information, shown to everyone alike.

## 4. Bias and fairness

| Risk | What we do | What is still open |
|---|---|---|
| Language: reader works better in English than Tetum; regional spelling and Portuguese loanwords | Rules for common patterns; confirmation echo; test set must include variants | On unseen test 3 the rules engine got 72% of Tetum messages exactly right (26/36) and 63% of English (10/16); small-model split in RESULTS.md. No real farmer messages yet. |
| Literacy: farmers who cannot read or write SMS are left out | Short messages, numbers and a few fixed words; a pickup person or relative can send for her | Voice (IVR) is a next step, not built. The people least able to text are likely the ones most missing from the Registry. |
| Larger vs smaller farms | Reputation ignores land size and volume. A farmer with one sack and a farmer with fifty are scored the same way on on-time delivery and grade match | Buyers may still prefer big lots; pooling helps but does not remove this. We will check whether small farms sit out more often. |
| Weather | Flood and heavy-rain weeks are not counted against reputation (proposed: a week the pickup coordinator flags as a road or rain closure; weather-station or CHIRPS data later) | Roads closing in rain is a disadvantage that falls on remote farms; this rule reduces but does not remove it. |
| Photo grade: lighting, drying tarp colour, phone quality, beans from different areas | Abstention; person confirms at pickup; grade disagreement between AI and inspector is logged and shown in the brief | Measured on 180 unseen photos: 84% right on clean photos, 88% on photos degraded to cheap-phone quality; it declines 14–16% and is right 90–93% of the time when it answers. Worst error: defective beans called A in 6 of 45 clean test photos, which is why the inspector's grade is the one paid. On real field photos unlike its training set it was confidently wrong, so it now refuses them. The photo model may favour the conditions of its training data (see DATA_CARD). |
| Registry: those who join first and those who consent are not a random sample | The brief says how many farmers and how many consented, and what it cannot tell | Brief conclusions about a village can be wrong if the missing farmers differ. |
| Women: Noor's household has two phones and shared use | Reputation and payout are tied to the registered seller; any member can be registered | Not yet checked against GSMA gender-gap data for Timor-Leste. |

## 5. Human oversight points

1. Farmer confirms each reading of her message.
2. Person at pickup confirms the grade; that grade decides the payment.
3. Person confirms any exclusion; warnings and time-outs are automatic and can be appealed to a person.
4. Auction clears by rule; no one, including the operator, edits bids.
5. Experts decide what to do with the brief. It points to rows and says "for expert review".
6. The operator reviews a sample of AI readings and grades each week (proposed: 20 SMS readings and 20 photo grades a week).

## 6. Failure modes and fallbacks

| Failure | What happens |
|---|---|
| Model server down | Rules engine keeps taking offers. Unclear messages are queued; the model rechecks later; any difference from what the farmer confirmed goes back to her as a new confirmation. |
| Reader unsure | Dure replies "not sure, please send again like this: 40 kg A 1.45" or hands to a person. |
| Reader misreads and the farmer confirms the wrong thing | The echo shows kilos, grade and price in plain words. She can correct until the pool closes. Large changes (more than 20% in kilos or price) trigger a person's check. |
| Photo is blurry, dark or off-topic | Grader abstains: "send another photo". |
| Photo grade differs from inspector | Inspector grade wins. The difference is logged. |
| Buyer does not pay | Prefunded escrow means there is no unpaid deal; the buyer cannot bid beyond the funds put in (design rule; simulated in the demo). |
| SMS delayed or lost | Reply window runs until 20:00; the farmer gets a confirmation after the cut-off or the offer is not counted and she is told. (design rule; simulated in the demo) |
| Brief sentence disagrees with the data | Cannot happen in the prototype: the brief's wording comes from fixed templates and every number is filled in by code from the Registry. If a model is later used to rephrase it, any sentence whose numbers differ from the computed ones is replaced by the template sentence. |
| Mobile-money or SMS gateway outage | Pool is held; no payouts are made until it is back. |

## 7. What the AI must never do

- Set or suggest a price on its own that replaces the auction, or change a farmer's minimum.
- Exclude a farmer or decide a sanction beyond warning and time-out.
- Give agronomic advice or diagnose a crop problem. The brief may say "consistent with parchment that could not dry" only as an observation flagged for expert review, never as a diagnosis or instruction to a farmer.
- Invent a number in the brief. Every figure is computed from the Registry and links to rows.
- Act for the farmer without confirmation, spend or move money, or message buyers on her behalf.
- Claim certainty when unsure. The right answer is "not sure, ask a person".

## 8. Testing plan for the responsible-AI claims

Not done yet, before the pilot: abstention rate and error rate by language; photo grade vs inspector by condition; check that reputation scores do not correlate with farm size; check that village aggregates hide small groups; a person reads a sample of briefs against the rows.
