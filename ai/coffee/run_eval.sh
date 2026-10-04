#!/bin/bash
# After training: score the fine-tuned reader, the untrained base (few-shot), and the hybrid on all three test sets.
cd "$(dirname "$0")"; set -e
for t in test test2 test3; do
  python3 infer.py merged pred_model_$t.json --test $t.json | tee -a eval.log
  python3 score.py pred_model_$t.json $t.json | sed "s/^/model $t: /" | tee -a eval.log
  python3 hybrid.py pred_rules_$t.json pred_model_$t.json $t.json | sed "s/^/hybrid $t: /" | tee -a eval.log
done
python3 infer.py base pred_base_test3.json --test test3.json --fewshot | tee -a eval.log
python3 score.py pred_base_test3.json test3.json | sed "s/^/base few-shot test3: /" | tee -a eval.log
