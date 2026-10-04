# Daily brief written by a small open model — results (4 Oct 2026)

Pipeline: code computes every finding from the register (per village, week 3 against week 1 and against the other villages) and ranks
them by how unusual they are (`findings.js`). A small open model writes the brief as JSON, citing the finding ids behind each sentence
(`brief.py`). A checker then drops any sentence that:
- uses a number that is not in the findings it cites, or names a village it cites no finding for;
- calls a rise a fall (or the reverse);
- states a cause ("because", "due to", ...) outside the review questions, or uses judgement words ("significant", "alarming");
- gives advice ("should", "must") or puts numbers in a review question, or copies the instructions.
If the headline fails or too little survives, the sheet shows the template brief instead. Models run 4-bit (GGUF, llama.cpp) on 2 CPU cores, no internet.

| Version | Model | Result |
|---|---|---|
| 1. Model reads the whole register table, no ranking | Qwen2.5-1.5B (bf16) | Missed the main event (Lebudu), wrote a "10%" that was in the table but meant something else, gave farmers advice. Not usable. |
| 2. Same, numbers checked against the cited findings | 1.5B / 3B | 1.5B copied the JSON template. 3B took the "other villages" figure as one village's own (caught by the checker), missed Lebudu. Not usable. |
| 3. Code ranks findings, model writes them up | 3B | Found Lebudu with the right numbers, but copied template text and wrote "drop" for a rise from 10% to 70%. All 6 sentences dropped. |
| 4. As 3, plus one worked example (a made-up village), direction / judgement-word checks, cited review questions, and a coverage rule (code adds any of the three biggest changes the model left out) | **3B** | **9 of 10 sentences kept**, 1 finding added by code (the 60% mould flag), about 2–5 minutes. Shown in the sheet. The checker removed a question that cited a Ducurai finding to ask about Lebudu. |
| 4, same prompt | 1.5B | 700 tokens of unparseable output. Not usable. |
| 4 on a **held-out register** (new seed; the rain hits Eraulo instead of Lebudu; prompt not changed) | 3B | Right village and numbers in the headline; 12 of 17 sentences kept, 1 added by code. Removed: Lacau's numbers written up without citing Lacau, "8 cents" (not a figure in the findings), a Lebudu rise written as "19% less", and the grade B price quoted as grade C's. |
| 4 with a repetition penalty (1.15) | 3B | Worse: wrote Ducurai's 68 kg under Lebudu (caught) and a headline "against 10% in week 1 and other villages" that drops the 8% (not caught). Not used. |

Honesty note: the "less" direction word and the grade-price check were added after reading the held-out output, so the held-out run is
no longer unseen for those two checks. The model and prompt were not changed after it.

What this means: a 3B model on a laptop can write a usable brief, but only after code has done the analysis and with a checker in front
of it. The checker is not optional: on the held-out register it caught the model putting one village's numbers under another's.
The checker cannot catch everything: a number that appears in a cited finding but is attached to the wrong measure would pass.
Every sentence therefore links to its finding and its rows, and a person decides what to do.

Files: `brief_3b.json` (shown in the sheet), `brief_3b_heldout.json`, `brief_1.5b.json`, `findings.json`, `findings_heldout.json`.
