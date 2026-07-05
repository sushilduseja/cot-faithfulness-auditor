import json
from pathlib import Path

DATA_DIR = Path("data")


def test_file_exists():
    assert (DATA_DIR / "exp1_truncation_results.json").exists(), (
        "Run 03-exp1-truncation first — exp1_truncation_results.json not found"
    )


def test_150_entries():
    with open(DATA_DIR / "exp1_truncation_results.json") as f:
        data = json.load(f)
    assert len(data) == 150, f"Expected 150 entries, got {len(data)}"


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


def test_100pct_matches_baseline():
    with open(DATA_DIR / "exp1_truncation_results.json") as f:
        data = json.load(f)
    mismatches = []
    for i, entry in enumerate(data):
        full_answer = entry.get("full_answer")
        for t in entry.get("truncations", []):
            if t.get("pct") == 100:
                if t.get("generated_answer") != full_answer:
                    mismatches.append((i, full_answer, t.get("generated_answer")))
    assert len(mismatches) == 0, (
        f"{len(mismatches)} entries have 100% truncation answer != baseline: {mismatches[:3]}"
    )


def test_each_truncation_has_answer():
    with open(DATA_DIR / "exp1_truncation_results.json") as f:
        data = json.load(f)
    for i, entry in enumerate(data):
        for t in entry.get("truncations", []):
            assert "generated_answer" in t, (
                f"Entry {i}, truncation {t.get('pct')}%: generated_answer missing"
            )
