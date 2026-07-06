"""Baseline generation — parallel API calls with configurable workers/problems."""
import sys, json, time, logging
from dataclasses import asdict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from src.config import config
from src.llm import LLMClient, extract_answer, is_malformed
from src.schema import BaselineResult, Run

DATA_DIR = Path("data")
OUTPUT = DATA_DIR / "baseline_results.json"
SYSTEM_PROMPT = "You are a math solver. Show your reasoning step by step, then give the final answer."
USER_PROMPT = "Solve the following math problem step by step.\nAfter your reasoning, on the final line, write the answer as: Answer: <number>\n\nProblem: {problem}"

client = LLMClient(timeout=config.api_timeout, retry_max=config.retry_max)
write_lock = Lock()
provider_counts: dict[str, int] = {}


def process_one(idx: int, problem: dict) -> BaselineResult:
    text = problem["problem_text"]
    if is_malformed(text):
        logging.warning("Malformed problem #%d: contains comma artifacts", idx)

    runs: list[Run] = []
    for _ in range(config.runs_per_condition):
        resp_text, provider = client.generate([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT.format(problem=text)},
        ])
        ans = extract_answer(resp_text or "")
        runs.append(Run(cot=resp_text or "", answer=ans, provider=provider))
        time.sleep(config.inter_request_delay)

    answers = [r.answer for r in runs]
    stable = len(set(answers)) == 1 and all(a is not None for a in answers)

    with write_lock:
        provider_counts[runs[0].provider] = provider_counts.get(runs[0].provider, 0) + 1

    return BaselineResult(
        problem_text=text,
        correct_answer=str(problem["correct_answer"]),
        cot=runs[0].cot,
        answer=runs[0].answer,
        runs=runs,
        stable=stable,
    )


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    with open(DATA_DIR / "perturbed_problems.json") as f:
        problems = json.load(f)
    if limit:
        problems = problems[:limit]
    else:
        problems = problems[:config.num_problems]

    results: list[BaselineResult] = []
    if OUTPUT.exists():
        with open(OUTPUT) as f:
            results = [BaselineResult(**r) for r in json.load(f)]
        print(f"Resuming: {len(results)} already done")

    remaining = list(enumerate(problems))[len(results):]
    if not remaining:
        print("All done already.")
        return

    print(f"Processing {len(remaining)} problems with {config.num_workers} workers...")
    with ThreadPoolExecutor(max_workers=config.num_workers) as executor:
        fut_map = {executor.submit(process_one, i, p): i for i, p in remaining}
        done = len(results)
        for f in as_completed(fut_map):
            r = f.result()
            with write_lock:
                results.append(r)
                done += 1
                if done % 10 == 0 or done == len(problems):
                    with open(OUTPUT, "w") as fh:
                        json.dump([asdict(r) for r in results], fh, indent=2)
                    stable = sum(1 for r in results if r.stable)
                    print(f"{done}/{len(problems)} done, {stable} stable, providers: {provider_counts}")

    with open(OUTPUT, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)
    stable = sum(1 for r in results if r.stable)
    print(f"Complete. {stable}/{len(results)} stable. Providers: {provider_counts}")


if __name__ == "__main__":
    main()
