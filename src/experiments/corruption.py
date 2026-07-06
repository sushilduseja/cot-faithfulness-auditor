"""Experiment 2: Text-level string corruption — pure rules + Groq/NVIDIA API."""
import re, random
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
SYSTEM_PROMPT = "Determine the final answer based on the corrupted reasoning below."
USER_PROMPT = "Problem: {problem}\n\nCorrupted reasoning:\n{cot}\n\nGive the final answer as: Answer: <number>"


def strip_answer(cot: str) -> str:
    idx = cot.rfind("Answer:")
    if idx == -1:
        return cot
    return cot[:idx].rstrip()


def process(idx, entry, client):
    cot = strip_answer(entry["cot"])
    pid = entry["problem_text"][:40]
    problem = entry["problem_text"]
    baseline_answer = entry.get("answer") or entry.get("correct_answer", "0")
    results = []
    for cond_name, corrupt_fn in [("random", corrupt_random), ("semantic", corrupt_semantic), ("deletion", corrupt_deletion)]:
        corrupted = corrupt_fn(cot)
        resp_text, _ = client.generate([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT.format(problem=problem, cot=corrupted)},
        ])
        ans = extract_answer(resp_text or "")
        results.append(asdict(CorruptionResult(
            problem_id=pid, condition=cond_name,
            generated_answer=ans, correct_answer=str(baseline_answer),
        )))
    return results


def main():
    run_experiment(process_fn=process, input_path=str(INPUT), output_path=str(OUTPUT),
                   limit=config.num_problems, label="Corruption")


if __name__ == "__main__":
    main()
