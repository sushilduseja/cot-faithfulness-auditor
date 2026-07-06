"""Experiment 2: Token-level corruption — pure rules + NVIDIA NIM (no local model)."""
import json, random
from dataclasses import asdict
from pathlib import Path
from src.config import config
from src.llm import extract_answer
from src.corrupt import corrupt_random, corrupt_semantic, corrupt_deletion
from src.schema import CorruptionResult
from src.runner import run_experiment

DATA_DIR = Path("data")
INPUT = DATA_DIR / "baseline_results.json"
OUTPUT = DATA_DIR / "exp2_corruption_results.json"
SYSTEM_PROMPT = "Continue the following corrupted reasoning and determine the final answer."
USER_PROMPT = "Corrupted reasoning:\n{cot}\n\nContinue from here and give the final answer as: Answer: <number>"


def process(idx, entry, client):
    cot = entry["cot"]
    pid = entry["problem_text"][:40]
    results = []
    for cond_name, corrupt_fn in [("random", corrupt_random), ("semantic", corrupt_semantic), ("deletion", corrupt_deletion)]:
        corrupted = corrupt_fn(cot)
        resp_text, _ = client.generate([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT.format(cot=corrupted)},
        ])
        ans = extract_answer(resp_text or "")
        results.append(asdict(CorruptionResult(
            problem_id=pid, condition=cond_name,
            generated_answer=ans, correct_answer=str(entry["correct_answer"]),
        )))
    return results


def main():
    run_experiment(process_fn=process, input_path=str(INPUT), output_path=str(OUTPUT),
                   limit=config.num_problems, label="Corruption")


if __name__ == "__main__":
    main()
