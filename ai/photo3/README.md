# Photo grader v3

Same CLIP ViT-B/32 int8 image model as v2 (`site/src/assets/grader_v2.js`). The head changes.
- **Kind head:** coffee, not coffee (N) or roasted (R).
- **Grade head:** A, B or C.

Per view the grader reports p(A)=p(coffee)·p(A|coffee), p(B), p(C), p(N), p(R). The JS averages these over the same 6 views and applies the same decision rules as v2.

## Files
- `src/graders.py`: Python port of `grader_v2.js`. It matches the browser within ±0.03 on the demo samples. It also holds the ResNet-18 variant used for comparison.
- `src/fetch_mit.py`, `src/fetch_commons.py`: download the data.
  - Bean crops: MIT Pre-Roast Coffee Bean Grading Dataset.
  - Commons search photos: credits in `commons_photo_credits*.json`.
- `review_labels*.json`: every Commons photo labelled by eye (R / G / N / drop) before any model saw it.
- `real_grades*.json`: our A/B/C labels for real coffee photos. `null` means coffee, too far away to grade.
- `src/compose.py`: synthetic piles. `src/build.py`: 6-view CLIP and ResNet-18 features.
- `src/train_eval.py`, `src/real_eval.py`: ResNet-18 vs CLIP with the same recipe. `results/results*.json` hold the outputs.
- `src/improve.py`: v3 heads, evaluated with leave-one-photo-out on real coffee photos and a held-out split for the rest. `results/improve_final_eval.json` holds the outputs.
- `src/final_head.py`: v3 trained on all data → `results/head_v3.json`, which is inlined in `grader_v2.js`.

The scripts were run from a working folder next to this repo (`work/` beside `dure/`), with images and models downloaded there. They are not committed.

## Results
See the main README ("Photo grader").

ResNet-18 vs CLIP with the same recipe:
- ResNet-18 is smaller: 12 MB int8.
- It is weaker on cheap-phone photos: synthetic piles 70–73% vs 88%.
- It refuses fewer photos with no coffee: 94% vs 99%.
