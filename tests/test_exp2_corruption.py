import json
from pathlib import Path

DATA_DIR = Path("data")
EXPECTED_CONDITIONS = {"random", "semantic", "deletion"}


def test_file_exists():
    assert (DATA_DIR / "exp2_corruption_results.json").exists(), (
        "Run 04-exp2-corruption first - exp2_corruption_results.json not found"
    )


def test_all_conditions_present():
    with open(DATA_DIR / "exp2_corruption_results.json") as f:
        data = json.load(f)
    conditions = {entry.get("condition") for entry in data}
    for c in EXPECTED_CONDITIONS:
        assert c in conditions, f"No '{c}' corruption condition found"


def test_each_entry_has_required_fields():
    with open(DATA_DIR / "exp2_corruption_results.json") as f:
        data = json.load(f)
    for i, entry in enumerate(data):
        assert "condition" in entry, f"Entry {i}: condition missing"
        assert entry.get("condition") in EXPECTED_CONDITIONS, (
            f"Entry {i}: unexpected condition '{entry.get('condition')}'"
        )
        assert "generated_answer" in entry, f"Entry {i}: generated_answer missing"
        assert "correct_answer" in entry, f"Entry {i}: correct_answer missing"


def test_correct_answer_in_each_entry():
    with open(DATA_DIR / "exp2_corruption_results.json") as f:
        data = json.load(f)
    for i, entry in enumerate(data):
        ca = entry.get("correct_answer")
        assert ca is not None, f"Entry {i}: correct_answer is None"
