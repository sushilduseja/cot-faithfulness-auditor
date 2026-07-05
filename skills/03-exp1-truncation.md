# 03 — Experiment 1: Progressive Truncation

Test whether the model commits to an answer before the CoT is complete by truncating CoTs at 10/25/50/75/100% and forcing continuation.

## Input

`data/baseline_results.json`

## Output

`data/exp1_truncation_results.json` — list of `{problem_text, correct_answer, full_cot, full_answer, truncations: [{pct, truncated_cot, generated_answer}]}`.

## Acceptance Test

- For each of the 150 baseline entries, exactly 5 truncation points recorded.
- Each truncation entry has `generated_answer` that can be compared against `correct_answer`.
- Truncation at 100% must produce the same answer as the baseline (sanity check).
- Each condition run 3 times; only stable answers are reported.

## Files Touched

- `notebooks/03-exp1-truncation.ipynb` (creates)
- `data/exp1_truncation_results.json` (creates)
- `data/baseline_results.json` (reads)
