# 01 — Data Prep

Pull 150 GSM8K problems, perturb numeric values, store ground truth.

## Input

None (fetches from HuggingFace `datasets`).

## Output

`data/perturbed_problems.json` — list of `{problem_text, correct_answer}`.

## Acceptance Test

- File has exactly 150 entries.
- Every `problem_text` is a non-empty string.
- Every `correct_answer` is a numeric value parseable as `int` or `float`.
- Spot-check 3 entries: manually verify the answer matches the problem after perturbation.

## Files Touched

- `notebooks/01-data-prep.ipynb` (creates)
- `data/perturbed_problems.json` (creates)
