import json
from pathlib import Path

DATA_DIR = Path("data")


def test_file_exists():
    assert (DATA_DIR / "baseline_results.json").exists(), (
        "Run 02-baseline-gen first — baseline_results.json not found"
    )


def test_150_entries():
    with open(DATA_DIR / "baseline_results.json") as f:
        data = json.load(f)
    assert len(data) == 150, f"Expected 150 entries, got {len(data)}"


def test_each_entry_has_cot_and_answer():
    with open(DATA_DIR / "baseline_results.json") as f:
        data = json.load(f)
    for i, entry in enumerate(data):
        assert isinstance(entry.get("cot"), str) and len(entry["cot"]) > 0, (
            f"Entry {i}: cot missing or empty"
        )
        assert isinstance(entry.get("answer"), str) and len(entry["answer"]) > 0, (
            f"Entry {i}: answer missing or empty"
        )
        assert "correct_answer" in entry, f"Entry {i}: correct_answer missing"


def test_answer_stability_across_runs():
    with open(DATA_DIR / "baseline_results.json") as f:
        data = json.load(f)
    unstable = []
    for i, entry in enumerate(data):
        if "runs" in entry and isinstance(entry["runs"], list) and len(entry["runs"]) > 1:
            answers = [r.get("answer") for r in entry["runs"]]
            if len(set(answers)) > 1:
                unstable.append((i, answers))
    assert len(unstable) == 0, (
        f"{len(unstable)} entries have unstable answers across runs: {unstable[:5]}"
    )
