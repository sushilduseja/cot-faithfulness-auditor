import json
from pathlib import Path
from src.config import config

DATA_DIR = Path("data")


def test_file_exists():
    assert (DATA_DIR / "baseline_results.json").exists(), (
        "Run 02-baseline-gen first — baseline_results.json not found"
    )


def test_expected_entries():
    with open(DATA_DIR / "baseline_results.json") as f:
        data = json.load(f)
    assert len(data) == config.num_problems, (
        f"Expected {config.num_problems} entries, got {len(data)}"
    )


def test_each_entry_has_cot_and_answer():
    with open(DATA_DIR / "baseline_results.json") as f:
        data = json.load(f)
    for i, entry in enumerate(data):
        assert isinstance(entry.get("cot"), str) and len(entry["cot"]) > 0, (
            f"Entry {i}: cot missing or empty"
        )
        assert "correct_answer" in entry, f"Entry {i}: correct_answer missing"


def test_answer_stability_reported():
    with open(DATA_DIR / "baseline_results.json") as f:
        data = json.load(f)
    for i, entry in enumerate(data):
        assert "stable" in entry, f"Entry {i}: stable field missing"
        if "runs" in entry and len(entry["runs"]) > 1:
            answers = [r.get("answer") for r in entry["runs"]]
            expected = len(set(answers)) == 1
            assert entry["stable"] == expected, (
                f"Entry {i}: stable={entry['stable']} but answers={answers}"
            )
