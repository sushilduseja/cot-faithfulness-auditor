import json
from pathlib import Path

DATA_DIR = Path("data")
NOTEBOOKS_DIR = Path("notebooks")


def test_all_experiment_data_exists():
    required = [
        "exp1_truncation_results.json",
        "exp2_corruption_results.json",
        "exp3_bias_results.json",
        "baseline_results.json",
    ]
    missing = [f for f in required if not (DATA_DIR / f).exists()]
    assert len(missing) == 0, (
        f"Run experiments 01-05 first - missing: {missing}"
    )


def test_notebook_exists():
    assert (NOTEBOOKS_DIR / "06-visualize.ipynb").exists(), (
        "06-visualize.ipynb not found - run the visualize task first"
    )


def test_notebook_is_valid_json():
    with open(NOTEBOOKS_DIR / "06-visualize.ipynb") as f:
        nb = json.load(f)
    assert "cells" in nb, "Notebook has no 'cells' - invalid .ipynb format"
