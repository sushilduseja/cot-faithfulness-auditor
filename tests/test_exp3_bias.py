import json, sys
from pathlib import Path
sys.path.insert(0, ".")
from src.config import config

DATA_DIR = Path("data")


def test_file_exists():
    assert (DATA_DIR / "exp3_bias_results.json").exists(), (
        "Run 05-exp3-bias first — exp3_bias_results.json not found"
    )


def test_expected_entries():
    with open(DATA_DIR / "exp3_bias_results.json") as f:
        data = json.load(f)
    assert len(data) == config.num_problems, (
        f"Expected {config.num_problems} entries, got {len(data)}"
    )


def test_each_entry_has_flagged_bool():
    with open(DATA_DIR / "exp3_bias_results.json") as f:
        data = json.load(f)
    for i, entry in enumerate(data):
        assert "flagged" in entry, f"Entry {i}: 'flagged' field missing"
        assert isinstance(entry["flagged"], bool), (
            f"Entry {i}: flagged should be bool, got {type(entry['flagged'])}"
        )


def test_each_entry_has_cot():
    with open(DATA_DIR / "exp3_bias_results.json") as f:
        data = json.load(f)
    for i, entry in enumerate(data):
        assert isinstance(entry.get("cot"), str) and len(entry["cot"]) > 0, (
            f"Entry {i}: cot missing or empty"
        )


def test_flag_rate_computable():
    with open(DATA_DIR / "exp3_bias_results.json") as f:
        data = json.load(f)
    flags = [entry["flagged"] for entry in data]
    rate = sum(flags) / len(flags) if flags else 0
    assert 0.0 <= rate <= 1.0, f"Flag rate {rate} outside [0, 1]"
