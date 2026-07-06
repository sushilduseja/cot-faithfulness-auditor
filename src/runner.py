"""Shared experiment runner - handles I/O, iteration, and progress."""
import json
from pathlib import Path
from src.config import config
from src.llm import LLMClient


def run_experiment(process_fn, input_path, output_path, *,
                   limit=None, label=""):
    """Load entries, call process_fn(idx, entry, client) for each, save results.
    
    If process_fn returns a list, entries are flattened (one per condition).
    """
    client = LLMClient(timeout=config.api_timeout, retry_max=config.retry_max)
    entries = json.loads(Path(input_path).read_text())
    num = limit or config.num_problems
    results = []
    for i, e in enumerate(entries[:num]):
        r = process_fn(i, e, client)
        if isinstance(r, list):
            results.extend(r)
        else:
            results.append(r)
    Path(output_path).write_text(json.dumps(results, indent=2))
    print(f"[{label}] {len(results)} entries -> {output_path}")
    return results
