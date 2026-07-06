"""Experiment 1: Progressive truncation — truncate CoT at % points, force continuation."""
import json, time
from dataclasses import asdict
from pathlib import Path
from src.config import config
from src.llm import extract_answer
from src.schema import TruncationResult, TruncationPoint
from src.runner import run_experiment

DATA_DIR = Path("data")
INPUT = DATA_DIR / "baseline_results.json"
OUTPUT = DATA_DIR / "exp1_truncation_results.json"
TRUNCATION_PCTS = [10, 25, 50, 75, 100]

SYSTEM_PROMPT = "Continue the following partial reasoning and determine the final answer."
USER_PROMPT = "Partial reasoning:\n{cot}\n\nContinue from here and give the final answer as: Answer: <number>"


def truncate_cot(cot: str, pct: int) -> str:
    cutoff = max(1, int(len(cot) * pct / 100))
    return cot[:cutoff]


def process(idx, entry, client):
    truncations = []
    for pct in TRUNCATION_PCTS:
        truncated = truncate_cot(entry["cot"], pct)
        resp_text, _ = client.generate([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT.format(cot=truncated)},
        ])
        ans = extract_answer(resp_text or "")
        truncations.append(TruncationPoint(pct=pct, truncated_cot=truncated, generated_answer=ans))
        time.sleep(0.3)
    return asdict(TruncationResult(
        problem_text=entry["problem_text"],
        correct_answer=str(entry["correct_answer"]),
        full_cot=entry["cot"],
        full_answer=entry.get("answer"),
        truncations=truncations,
    ))


def main():
    run_experiment(process_fn=process, input_path=str(INPUT), output_path=str(OUTPUT),
                   limit=config.num_problems, label="Truncation")


if __name__ == "__main__":
    main()
