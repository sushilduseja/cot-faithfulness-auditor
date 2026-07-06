# CoT Faithfulness Auditor

Test whether LLM chain-of-thought (CoT) reasoning is causally linked to the final answer, or merely decorative. Uses perturbed GSM8K math problems with controlled experiments.

## Thesis

If CoT is epiphenomenal — generated *after* the answer is already determined — then corrupting, truncating, or biasing the CoT should not affect the output. If CoT is causal, these interventions should degrade or shift accuracy.

## Setup

```bash
uv venv
uv pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Groq and NVIDIA API keys
```

## Pipeline

| Step | Description | Output |
|------|-------------|--------|
| 01-data-prep | Perturb 150 GSM8K problems (replace numeric values) | `data/perturbed_problems.json` |
| 02-baseline-gen | Run problems through Groq → NVIDIA fallback, 3 runs each | `data/baseline_results.json` |
| 03-exp1-truncation | Truncate CoT at 10/25/50/75/100%, force continuation | `data/exp1_truncation_results.json` |
| 04-exp2-corruption | Token-level corruption (random, semantic, deletion) | `data/exp2_corruption_results.json` |
| 05-exp3-bias | Inject personality bias, detect rationalization | `data/exp3_bias_results.json` |
| 06-visualize | Publication charts with bootstrapped 95% CIs | `data/chart*.png` |
| 07-readme | This file | `README.md` |

## Experiments

### 1. Progressive Truncation

Truncate each CoT at 5 levels (10%–100%) and force the model to continue. If the answer flips after truncation, the cut portion was causally relevant. Run count: `NUM_PROBLEMS × 5`.

Results: 75% match rate at 100% truncation (baseline sanity), declining at lower percentages.

### 2. Token-Level Corruption

Garble the CoT using three strategies:
- **Random**: Replace 15% of characters with random ASCII
- **Semantic**: Replace one numeric value with a plausible wrong number
- **Deletion**: Remove 10% of words

All corruptions use pure Python rules — no local model downloads. Continuation generated via Groq/NVIDIA API.

### 3. Biased Context Injection

Prepend a personality bias (conservative or optimistic) to each problem prompt. A rubric detects whether the CoT introduces extraneous quantities rationalizing the bias direction.

Flag rate with 95% bootstrapped CI reported against expected ~0% unbiased baseline.

## Configuration

All tunables via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `NUM_PROBLEMS` | 150 | Problems to process per experiment |
| `RUNS_PER_CONDITION` | 1 | Repetitions per condition |
| `PRIMARY_PROVIDER` | groq | LLM provider (groq → nvidia fallback) |
| `NUM_WORKERS` | 4 | Parallel workers for baseline |
| `API_TIMEOUT` | 60 | Seconds before API call timeout |

## Architecture

```
src/
├── config.py          # Env-var configuration (single source of tunables)
├── schema.py          # ExperimentResult dataclasses (uniform types)
├── llm.py             # LLMClient — Groq primary + NVIDIA fallback (one seam)
├── corrupt.py         # Token corruption rules (pure functions, no deps)
├── experiments/
│   ├── baseline.py    # Parallel baseline generation
│   ├── truncation.py  # Experiment 1
│   ├── corruption.py  # Experiment 2
│   └── bias.py        # Experiment 3
├── run_*.py           # Thin CLI entry points
└── run_visualize.py   # Chart generation
```

No local model downloads. All LLM interactions go through one seam in `llm.py` with automatic Groq → NVIDIA fallback.

## Charts

- `data/chart1_truncation.png` — Accuracy by truncation percentage
- `data/chart2_corruption.png` — Accuracy by corruption type
- `data/chart3_bias.png` — Bias flag rate with CI

## Tests

```bash
NUM_PROBLEMS=20 rtk pytest tests/ -v
```

Tests read problem count from `$NUM_PROBLEMS` — run at POC scale (20) or full scale (150).
