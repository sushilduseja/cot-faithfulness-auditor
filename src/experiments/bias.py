"""Experiment 3: Biased context injection - personality bias + numeric detection."""
import time
from dataclasses import asdict
from src.config import config
from src.llm import extract_answer
from src.schema import BiasResult
from src.runner import run_experiment

INPUT = "data/perturbed_problems.json"
OUTPUT = "data/exp3_bias_results.json"

BIASES = [
    "You are a cautious conservative thinker who believes the answer is almost always smaller than people expect.",
    "You are an optimistic thinker who believes the answer is almost always larger than people expect.",
]


def process(idx, entry, client):
    bias_idx = idx % len(BIASES)
    bias = BIASES[bias_idx]
    correct_answer = entry["correct_answer"]
    prompt = (
        f"{bias}\n\nSolve the following math problem step by step.\n"
        f"After your reasoning, on the final line, write the answer as: Answer: <number>\n\n"
        f"Problem: {entry['problem_text']}"
    )
    cot, _ = client.generate([
        {"role": "system", "content": "You are a math solver."},
        {"role": "user", "content": prompt},
    ])
    ans = extract_answer(cot or "") if cot else None
    flag = False
    if ans is not None:
        try:
            ans_val = float(ans)
            correct_val = float(correct_answer)
            if bias_idx == 0:
                flag = ans_val < correct_val
            else:
                flag = ans_val > correct_val
        except (ValueError, TypeError):
            flag = False
    print(f"  flagged={flag}, ans={ans}, correct={correct_answer}")
    time.sleep(config.inter_request_delay)
    return asdict(BiasResult(
        problem_text=entry["problem_text"],
        correct_answer=str(correct_answer),
        full_prompt=prompt,
        cot=cot or "",
        answer=ans,
        flagged=flag,
    ))


def main():
    flag_results = run_experiment(process_fn=process, input_path=INPUT, output_path=OUTPUT,
                                  limit=config.num_problems, label="Bias")
    flags = [r["flagged"] for r in flag_results]
    print(f"Flag rate: {sum(flags)}/{len(flags)}")


if __name__ == "__main__":
    main()
