# 02 — Baseline Generation

Run Groq (Llama-3.1-8B) on all 150 perturbed problems at temperature=0, greedy decoding.

## Input

`data/perturbed_problems.json`

## Output

`data/baseline_results.json` — list of `{problem_text, correct_answer, cot, answer}`.

## Acceptance Test

- 150 entries, each with non-empty `cot` and `answer` strings.
- Each problem run 3 times at temperature=0 with fixed seed — all 3 runs produce the same answer.
- If any answer is unstable across 3 runs, flag it and either re-run with stronger determinism or exclude it from experiments.

## Files Touched

- `notebooks/02-baseline-gen.ipynb` (creates)
- `data/baseline_results.json` (creates)
- `data/perturbed_problems.json` (reads)
