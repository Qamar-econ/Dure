# Test set 2 — review notes
70 messages written by Claude Sonnet 5.5 (claude-sonnet-5-5) on 2026-10-04, prompted only with a description of the service
and the label schema; it was not shown gen.py, train.jsonl or test.json. Labels were then reviewed by hand, message by message.
Result of review: all 70 labels accepted as written. Judgement calls kept as labelled:
- #15 "kafe 18kg ok deit" -> grade B ("ok" maps to B in Dure's scheme).
- #53 "cacao 40kg and coffee 65kg" -> crop coffee, kg 65 (the coffee part of a mixed message).
- #6 / #37 Portuguese greeting or "sim" inside an otherwise Tetum message -> lang tet (normal code-switching).
Limits: still synthetic (a model wrote it, not farmers).
