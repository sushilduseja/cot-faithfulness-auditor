import json
from pathlib import Path
from src.config import config

DATA_DIR = Path("data")


def test_file_exists():
    assert (DATA_DIR / "exp1_truncation_results.json").exists(), (
        "Run 03-exp1-truncation first — exp1_truncation_results.json not found"
    )


def test_expected_entries():
    with open(DATA_DIR / "exp1_truncation_results.json") as f:
        data = json.load(f)
    assert len(data) == config.num_problems, (
        f"Expected {config.num_problems} entries, got {len(data)}"
    )


def test_each_entry_has_5_truncation_points():
    with open(DATA_DIR / "exp1_truncation_results.json") as f:
        data = json.load(f)
    expected_pcts = {10, 25, 50, 75, 100}
    for i, entry in enumerate(data):
        truncs = entry.get("truncations", [])
        pcts = {t.get("pct") for t in truncs}
        assert pcts == expected_pcts, (
            f"Entry {i}: expected truncation points {expected_pcts}, got {pcts}"
        )


def test_100pct_match_rate():
    with open(DATA_DIR / "exp1_truncation_results.json") as f:
        data = json.load(f)
    total = 0
    matched = 0
    for entry in data:
        full_answer = entry.get("full_answer")
        for t in entry.get("truncations", []):
            if t.get("pct") == 100:
                total += 1
                if t.get("generated_answer") == full_answer:
                    matched += 1
    rate = matched / total if total else 0
    assert rate >= 0, f"100% truncation match rate {rate:.2f} — should be >= 0"
    print(f"  100% truncation match rate: {matched}/{total} ({rate:.0%})")


def test_each_truncation_has_answer():
    with open(DATA_DIR / "exp1_truncation_results.json") as f:
        data = json.load(f)
    for i, entry in enumerate(data):
        for t in entry.get("truncations", []):
            assert "generated_answer" in t, (
                f"Entry {i}, truncation {t.get('pct')}%: generated_answer missing"
            )
