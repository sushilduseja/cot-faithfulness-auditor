from pathlib import Path

README = Path("README.md")


def test_readme_exists():
    assert README.exists(), "README.md not found"


def test_readme_has_thesis():
    content = README.read_text()
    assert "faithfulness" in content.lower(), "README missing mention of 'faithfulness'"


def test_readme_has_setup_instructions():
    content = README.read_text()
    assert "uv" in content, "README missing uv setup instructions"
    assert ".env" in content or "GROQ_API_KEY" in content, (
        "README missing API key setup instructions"
    )


def test_readme_has_experiment_summaries():
    content = README.read_text()
    expected = ["truncation", "corruption", "bias"]
    missing = [s for s in expected if s not in content.lower()]
    assert len(missing) == 0, f"README missing mentions of: {missing}"
