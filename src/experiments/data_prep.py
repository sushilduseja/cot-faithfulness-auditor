"""Data preparation - pull GSM8K problems, perturb numeric values, store as JSON."""
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


def recompute_last_expression(text: str) -> float | None:
    matches = list(re.finditer(r'(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)', text))
    if not matches:
        return None
    a_str, op, b_str = matches[-1].groups()
    a, b = float(a_str), float(b_str)
    if op == '+': return a + b
    elif op == '-': return a - b
    elif op == '*': return a * b
    elif op == '/': return a / b if b != 0 else None
    return None


def extract_original_answer(answer_chain: str) -> float:
    m = re.search(r'####\s*(-?[\d.]+)', answer_chain)
    if m:
        return float(m.group(1))
    return 0.0


def perturb_problem(question: str, answer_chain: str, seed: int) -> tuple[str, float]:
    random.seed(seed)
    numbers_in_q = list(dict.fromkeys(m.group(0) for m in re.finditer(r'\d+(?:\.\d+)?', question)))
    mapping = {n: perturb_value(n) for n in numbers_in_q}
    sorted_nums = sorted(numbers_in_q, key=len, reverse=True)
    new_q = question
    for old, new in [(n, mapping[n]) for n in sorted_nums]:
        new_q = re.sub(rf'\b{re.escape(old)}\b', new, new_q)
    new_chain = answer_chain
    for old, new in [(n, mapping[n]) for n in sorted_nums]:
        new_chain = re.sub(rf'\b{re.escape(old)}\b', new, new_chain)
    new_answer = recompute_last_expression(new_chain)
    if new_answer is None:
        new_answer = extract_original_answer(answer_chain)
    if isinstance(new_answer, float):
        new_answer = round(new_answer, 2)
        if new_answer == int(new_answer):
            new_answer = int(new_answer)
    return new_q, new_answer


def main():
    random.seed(42)
    dataset = load_dataset("gsm8k", "main", split="test")
    results = []
    for i in range(NUM_PROBLEMS):
        example = dataset[i]
        q = example["question"]
        answer_chain = example["answer"]
        perturbed_q, new_answer = perturb_problem(q, answer_chain, seed=i)
        results.append({"problem_text": perturbed_q, "correct_answer": new_answer})
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved {len(results)} perturbed problems to {OUTPUT}")


if __name__ == "__main__":
    main()
