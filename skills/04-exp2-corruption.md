# 04 — Experiment 2: Token-Level Corruption

Garble the CoT at the token level using Qwen2.5-1.5B locally (PyTorch CPU). Run two corruption conditions: random substitution (15%) and semantic substitution (one plausible wrong number). Rebuild `attention_mask` and `position_ids` after any token deletion.

## Input

`data/baseline_results.json`

## Output

`data/exp2_corruption_results.json` — list of `{problem_id, condition, corrupted_input_ids, generated_answer, correct_answer}`.

## Acceptance Test

- Both `random` and `semantic` conditions present for each problem.
- `corrupt_tensor()` function exists and handles both modes + deletion with mask/position rebuild.
- Answers compared against ground truth separately per condition.
- Each condition run 3 times; only stable answers reported.
- Memory test: Qwen2.5-1.5B loads on CPU with ~3GB RAM.

## Files Touched

- `notebooks/04-exp2-corruption.ipynb` (creates)
- `data/exp2_corruption_results.json` (creates)
- `data/baseline_results.json` (reads)
