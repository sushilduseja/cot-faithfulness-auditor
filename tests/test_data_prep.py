import json
import re
from pathlib import Path

DATA_DIR = Path("data")


def test_file_exists():
    assert (DATA_DIR / "perturbed_problems.json").exists(), (
        "Run 01-data-prep first — perturbed_problems.json not found"
    )


def test_150_entries():
    with open(DATA_DIR / "perturbed_problems.json") as f:
        data = json.load(f)
    assert len(data) == 150, f"Expected 150 entries, got {len(data)}"


def test_each_entry_has_required_fields():
    with open(DATA_DIR / "perturbed_problems.json") as f:
        data = json.load(f)
    for i, entry in enumerate(data):
        assert isinstance(entry.get("problem_text"), str) and entry["problem_text"].strip(), (
            f"Entry {i}: problem_text missing or empty"
        )
        assert "correct_answer" in entry, f"Entry {i}: correct_answer missing"
        answer = entry["correct_answer"]
        assert isinstance(answer, (int, float)) or (
            isinstance(answer, str) and answer.replace(".", "").replace("-", "").isdigit()
        ), f"Entry {i}: correct_answer not numeric: {answer}"


def test_answers_are_diverse():
    with open(DATA_DIR / "perturbed_problems.json") as f:
        data = json.load(f)
    answers = [entry["correct_answer"] for entry in data]
    unique = len(set(answers))
    assert unique >= 50, (
        f"Only {unique}/150 unique answers — perturbation likely failed"
    )


def test_values_differ_from_gsm8k_originals():
    try:
        from datasets import load_dataset
    except ImportError:
        return  # skip if datasets not installed
    with open(DATA_DIR / "perturbed_problems.json") as f:
        perturbed = {entry["problem_text"]: entry["correct_answer"] for entry in json.load(f)}
    original = load_dataset("gsm8k", "main", split="test")
    answer_pattern = re.compile(r"####\s*(-?[\d.]+)")
    matches = 0
    for example in original:
        match = answer_pattern.search(example["answer"])
        if match and example["question"] in perturbed:
            orig_answer = float(match.group(1))
            if abs(float(perturbed[example["question"]]) - orig_answer) < 1e-6:
                matches += 1
    assert matches < 75, (
        f"{matches}/150 perturbed answers match originals — perturbation likely failed"
    )
