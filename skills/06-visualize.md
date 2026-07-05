# 06 — Visualize

Generate all publication-quality charts from experiment outputs. Compute bootstrapped 95% CIs for every reported metric.

## Input

- `data/exp1_truncation_results.json`
- `data/exp2_corruption_results.json`
- `data/exp3_bias_results.json`
- `data/baseline_results.json`

## Output

Charts rendered inline in notebook. Saved figures in `notebooks/` as PNGs.

## Acceptance Test

- **Chart 1 (Truncation):** X-axis = truncation % (10/25/50/75/100), Y-axis = % answers matching full-CoT baseline. Flat curve near 100% by 25% = headline finding.
- **Chart 2 (Corruption):** X-axis = corruption type (random 15%, semantic 1-step) crossed with corruption %. Two lines. Y-axis = % answers remaining correct. CIs on every point.
- **Text callouts:** At least 2 side-by-side examples: semantically corrupted CoT with wrong number, model output reaching original correct answer anyway.
- **Chart 3 (Flag-rate bar):** Bar chart showing biased-prompt flag rate with CI, compared to unbiased baseline (expected 0%).
- All CIs use bootstrap over 150 examples.

## Files Touched

- `notebooks/06-visualize.ipynb` (creates)
- `notebooks/*.png` (creates, optional)
- All experiment data files (reads)
