"""Experiment 2: Token-level corruption — pure rules + NVIDIA NIM (no local model)."""
import sys, json, random
sys.path.insert(0, ".")
from pathlib import Path

from src.config import config
from src.llm import LLMClient
from src.corrupt import corrupt_random, corrupt_semantic, corrupt_deletion
from src.schema import CorruptionResult, dictify

DATA_DIR = Path("data")
INPUT = DATA_DIR / "baseline_results.json"
OUTPUT = DATA_DIR / "exp2_corruption_results.json"
SYSTEM_PROMPT = "Continue the following corrupted reasoning and determine the final answer."
USER_PROMPT = "Corrupted reasoning:\n{cot}\n\nContinue from here and give the final answer as: Answer: <number>"

client = LLMClient(timeout=config.api_timeout, retry_max=config.retry_max)


def main():
    with open(INPUT) as f:
        baselines = json.load(f)

    results: list[CorruptionResult] = []
    for entry in baselines[:config.num_problems]:
        cot = entry["cot"]
        pid = entry["problem_text"][:40]

        for cond_name, corrupt_fn in [("random", corrupt_random), ("semantic", corrupt_semantic), ("deletion", corrupt_deletion)]:
            corrupted = corrupt_fn(cot)
            resp_text, _ = client.generate([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT.format(cot=corrupted)},
            ])
            ans = LLMClient.extract_answer(resp_text or "")
            results.append(CorruptionResult(
                problem_id=pid,
                condition=cond_name,
                generated_answer=ans,
                correct_answer=str(entry["correct_answer"]),
            ))

    with open(OUTPUT, "w") as f:
        json.dump([dictify(r) for r in results], f, indent=2)
    print(f"Complete. {len(results)} entries saved to {OUTPUT}")


if __name__ == "__main__":
    main()
