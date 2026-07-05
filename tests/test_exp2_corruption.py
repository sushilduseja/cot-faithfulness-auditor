import json
from pathlib import Path

DATA_DIR = Path("data")


def test_file_exists():
    assert (DATA_DIR / "exp2_corruption_results.json").exists(), (
        "Run 04-exp2-corruption first — exp2_corruption_results.json not found"
    )


def test_both_conditions_present():
    with open(DATA_DIR / "exp2_corruption_results.json") as f:
        data = json.load(f)
    conditions = {entry.get("condition") for entry in data}
    assert "random" in conditions, "No 'random' corruption condition found"
    assert "semantic" in conditions, "No 'semantic' corruption condition found"


def test_each_entry_has_required_fields():
    with open(DATA_DIR / "exp2_corruption_results.json") as f:
        data = json.load(f)
    for i, entry in enumerate(data):
        assert "condition" in entry, f"Entry {i}: condition missing"
        assert entry.get("condition") in ("random", "semantic"), (
            f"Entry {i}: unexpected condition '{entry.get('condition')}'"
        )
        assert "generated_answer" in entry, f"Entry {i}: generated_answer missing"
        assert "correct_answer" in entry, f"Entry {i}: correct_answer missing"
        ans = entry["generated_answer"]
        assert isinstance(ans, str) and len(ans) > 0, f"Entry {i}: generated_answer empty"

def test_correct_answer_in_each_entry():
    with open(DATA_DIR / "exp2_corruption_results.json") as f:
        data = json.load(f)
    for i, entry in enumerate(data):
        ca = entry.get("correct_answer")
        assert ca is not None, f"Entry {i}: correct_answer is None"
