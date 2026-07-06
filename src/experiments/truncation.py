"""Experiment 1: Progressive truncation — truncate CoT at % points, force continuation."""
import sys, json, time
sys.path.insert(0, ".")
from pathlib import Path

from src.config import config
from src.llm import LLMClient
from src.schema import TruncationResult, TruncationPoint, dictify

DATA_DIR = Path("data")
INPUT = DATA_DIR / "baseline_results.json"
OUTPUT = DATA_DIR / "exp1_truncation_results.json"
TRUNCATION_PCTS = [10, 25, 50, 75, 100]

SYSTEM_PROMPT = "Continue the following partial reasoning and determine the final answer."
USER_PROMPT = "Partial reasoning:\n{cot}\n\nContinue from here and give the final answer as: Answer: <number>"

client = LLMClient(timeout=config.api_timeout, retry_max=config.retry_max)


def truncate_cot(cot: str, pct: int) -> str:
    cutoff = max(1, int(len(cot) * pct / 100))
    return cot[:cutoff]


def main():
    with open(INPUT) as f:
        baselines = json.load(f)

    results: list[TruncationResult] = []
    for idx, entry in enumerate(baselines[:config.num_problems]):
        truncations = []
        for pct in TRUNCATION_PCTS:
            truncated = truncate_cot(entry["cot"], pct)
            resp_text, _ = client.generate([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT.format(cot=truncated)},
            ])
            ans = LLMClient.extract_answer(resp_text or "")
            truncations.append(TruncationPoint(pct=pct, truncated_cot=truncated, generated_answer=ans))
            time.sleep(0.3)

        results.append(TruncationResult(
            problem_text=entry["problem_text"],
            correct_answer=str(entry["correct_answer"]),
            full_cot=entry["cot"],
            full_answer=entry.get("answer"),
            truncations=truncations,
        ))
        print(f"[{idx+1}/{len(baselines)}] Done")

    with open(OUTPUT, "w") as f:
        json.dump([dictify(r) for r in results], f, indent=2)
    print(f"Complete. {len(results)} entries saved to {OUTPUT}")


if __name__ == "__main__":
    main()
