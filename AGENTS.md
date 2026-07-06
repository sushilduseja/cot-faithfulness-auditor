# CoT Faithfulness Auditor — Project Conventions

Merges with the global AGENTS.md at `~/.config/opencode/AGENTS.md`. Project-specific overrides and additions below.

## Module Paths

- Do **not** use `sys.path.insert(0, ".")` in new files. Import directly from `src.` — the package is installed via `pip install -e .` or discovered via `PYTHONPATH`.
- Existing files with `sys.path.insert(0, ".")` may remain until they are otherwise touched.
- `conftest.py` or `pyproject.toml` is preferred for path configuration.

## LLM Calls — Single Seam

- All LLM calls go through `LLMClient.generate()` in `src/llm.py`. No experiment module creates a `Groq()` or `OpenAI()` client directly.
- The fallback chain (Groq → NVIDIA) is the caller's concern only via the `(text, provider)` return tuple.
- `extract_answer()` and `is_malformed()` are module-level functions in `src/llm.py`, not methods on `LLMClient`.

## Rate-Limit Delays

- Inter-request delays must come from a shared config field or module-level constant, not a hardcoded literal like `time.sleep(0.3)` in each experiment.
- Reason: 3 copies of the same literal means changing the delay requires 3 edits (shotgun surgery).

## Configuration

- Every field in `src/config.py` must have at least one consumer in the codebase. An env-var-backed config field with no consumers is speculative generality.
- Config fields are the single source of truth for model names (`GROQ_MODEL`, `NVIDIA_MODEL`), API timeouts, retry counts, and scale (`NUM_PROBLEMS`).

## Entry Points

- Prefer `pyproject.toml` `[project.scripts]` entry points or `python -m src.experiments.<name>` over thin `run_*.py` wrapper files.
- If a `run_*.py` wrapper exists and does nothing but `import main; main()`, it's a Middle Man — remove it when the file is otherwise touched.

## Experiments

- Use `src.runner.run_experiment()` for shared I/O, iteration, and progress reporting unless the experiment has unique needs (e.g., baseline has parallel execution + resume support).
- Each experiment module exposes a `main()` function as its entry point.
- `process_fn` passed to `run_experiment` must return a flat dict (not a list of dicts) unless all downstream consumers handle nesting.

## No Local Models

- Corruption rules live in `src/corrupt.py` as pure Python functions. No PyTorch, no HuggingFace downloads, no local inference.
- If token-level control is needed, it must use the API seam — never a local model.
