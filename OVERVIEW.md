# CoT Faithfulness Auditor - Overview

## What it does

Tests whether LLM chain-of-thought (CoT) reasoning is **causal** (the model actually uses its stated reasoning to reach the answer) or **decorative** (the answer is determined by internal heuristics and the CoT is post-hoc rationalization).

Three controlled experiments on perturbed GSM8K math problems:

| Experiment | Intervention | Measures |
|------------|--------------|----------|
| **1. Progressive Truncation** | Cut CoT at 10/25/50/75/100%, force continuation | Does the answer change when reasoning is cut early? |
| **2. Text-Level String Corruption** | Random char replacement / semantic number swap / word deletion | Does garbled reasoning still yield the correct answer? |
| **3. Biased Context Injection** | Prepend "cautious/optimistic" personality prompts | Does the CoT introduce extraneous quantities to justify the bias? |

## Why it matters

- **Interpretability**: If CoT is decorative, current alignment/transparency claims based on CoT are unreliable
- **Safety**: Models that rationalize predetermined answers cannot be trusted to self-correct
- **Benchmarking**: Most GSM8K evaluations suffer from training-data contamination; perturbing numeric values removes memorization as a confound

## Architecture (concise)

```
src/
├── config.py          # Env-var configuration (single source of truth)
├── schema.py          # Dataclasses for uniform experiment results
├── llm.py             # LLMClient - Groq primary + NVIDIA NIM fallback (one seam)
├── corrupt.py         # Pure Python string corruption rules (no deps)
├── runner.py          # Shared experiment runner (I/O, iteration, progress)
├── run_visualize.py   # Publication charts with bootstrapped 95% CIs
└── experiments/
    ├── data_prep.py   # GSM8K perturbation (numeric values only)
    ├── baseline.py    # Parallel baseline generation
    ├── truncation.py  # Experiment 1
    ├── corruption.py  # Experiment 2 (strips Answer: line before corrupting)
    └── bias.py        # Experiment 3
```

- **No local models** - all LLM calls via API seam with Groq→NVIDIA fallback
- **Config-driven** - `NUM_PROBLEMS=20` default (overridable), `INTER_REQUEST_DELAY=0.3s`
- **Entry points** - `cot-prep`, `cot-baseline`, `cot-truncation`, `cot-corruption`, `cot-bias`, `cot-visualize` (via `pyproject.toml`)

## Key finding so far

With 20 problems: corruption accuracy is **50-60%** (semantic 55%, deletion 60%, random 50%) - the model often ignores corrupted reasoning and recomputes correctly, but semantic corruption fools it ~45% of the time.