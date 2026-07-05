# Checkpoint — 2026-07-05

## Completed

| Task | Status | Commit |
|------|--------|--------|
| Repo scaffold | ✅ | `initial: scaffold project structure` |
| SPEC.md | ✅ | `add SPEC.md: project spec as single source of truth` |
| Skills files (01-07) | ✅ | `add atomic task files in skills/ (01-07)` |
| Tests (01-07) | ✅ | `add pytest acceptance tests in tests/ (01-07)` |
| 01-data-prep | ✅ | `feat: 01-data-prep` — 150 perturbed problems in `data/perturbed_problems.json` |
| 02-baseline-gen | 🔴 Not done | `src/run_baseline.py` written but never completed |

## Outstanding

### 02-baseline-gen (blocker)

150 perturbed problems need Groq (primary) + NVIDIA NIM (fallback) calls, 3 runs each = 450 API calls.

**Issue:** Sequential and even 4-thread parallel execution times out (>15 min) due to rate limits + slow problems. Problem #2 has malformed numbers (`$116,0`, `$28,0` from bad perturbation of comma-separated values), which may cause the model to generate erratic output or hang.

**Attempted approaches:**
1. Sequential with retry + backoff — too slow (~86s for 5 problems → ~43 min for 150)
2. 4-thread ThreadPoolExecutor — still timed out at 15 min
3. Batched 25-problem chunks with ThreadPoolExecutor — aborted

**Suspected root causes:**
- `data/perturbed_problems.json` has artifacts from GSM8K comma-format numbers (e.g. `$116,000` parsed as `116` and `000` separately). The perturbation code's `\b` word-boundary regex doesn't handle commas properly, producing malformed problems.
- Groq free tier rate limit (6000 TPM) and NVIDIA NIM (40 RPM) together still bottleneck on slow problems.
- No per-problem timeout in `call_llm()` — a single slow call can stall a worker thread.

### Future tasks (blocked by 02):
- 03-exp1-truncation
- 04-exp2-corruption
- 05-exp3-bias
- 06-visualize
- 07-readme

## Files

```
/notebooks/
  01-data-prep.ipynb    ✅
  02-baseline-gen.ipynb ✅ (needs re-run with fixed data)
/src/
  run_baseline.py       ✅ (needs per-problem timeout + better error handling)
/data/
  perturbed_problems.json ✅ (may need re-generation to fix comma artifacts)
/tests/
  test_data_prep.py     ✅
  test_baseline_gen.py  ✅
  test_exp1_truncation.py ✅
  test_exp2_corruption.py ✅
  test_exp3_bias.py     ✅
  test_visualize.py     ✅
  test_readme.py        ✅
```

## To resume

1. Fix `perturbed_problems.json` — handle comma-separated numbers in GSM8K so `$116,000` is treated as a single number, not two.
2. Re-run 01-data-prep if fix changes the data format.
3. Add per-problem timeout (30s) to `call_llm()` in `src/run_baseline.py`.
4. Run baseline again — estimate 10-15 min with 4 workers + proper timeouts.
5. Continue with 03-07 as each test passes.
