"""Data preparation — pull GSM8K problems, perturb numeric values, store as JSON."""
import re, json, random
from pathlib import Path
from datasets import load_dataset

DATA_DIR = Path("data")
OUTPUT = DATA_DIR / "perturbed_problems.json"
NUM_PROBLEMS = 150


def perturb_value(num_str: str) -> str:
    is_int = '.' not in num_str
    num = int(num_str) if is_int else float(num_str)
    factor = 0.5 + random.random() * 1.0
    new_num = num * factor
    if is_int:
        new_num = int(round(new_num))
    else:
        new_num = round(new_num, 2)
    return str(new_num)


def extract_original_answer(answer_chain: str) -> float:
    m = re.search(r'####\s*(-?[\d.]+)', answer_chain)
    if m:
        return float(m.group(1))
    return 0.0


def perturb_question(question: str, seed: int) -> str:
    """Perturb numbers in the question only. Return perturbed question."""
    random.seed(seed)
    numbers = list(dict.fromkeys(m.group(0) for m in re.finditer(r'\d+(?:\.\d+)?', question)))
    mapping = {n: perturb_value(n) for n in numbers}
    sorted_nums = sorted(numbers, key=len, reverse=True)
    new_q = question
    for old, new in [(n, mapping[n]) for n in sorted_nums]:
        new_q = re.sub(rf'\b{re.escape(old)}\b', new, new_q)
    return new_q


def main():
    random.seed(42)
    dataset = load_dataset("gsm8k", "main", split="test")
    results = []
    for i in range(NUM_PROBLEMS):
        example = dataset[i]
        q = example["question"]
        answer_chain = example["answer"]
        perturbed_q = perturb_question(q, seed=i)
        orig_answer = extract_original_answer(answer_chain)
        results.append({"problem_text": perturbed_q, "correct_answer": orig_answer})
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} perturbed problems to {OUTPUT}")


if __name__ == "__main__":
    main()
