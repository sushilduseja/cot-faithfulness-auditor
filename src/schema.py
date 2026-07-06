"""Result schemas for all experiments — uniform types across the pipeline."""
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Run:
    cot: str
    answer: str | None
    provider: str


@dataclass
class BaselineResult:
    problem_text: str
    correct_answer: str
    cot: str
    answer: str | None
    runs: list[Run]
    stable: bool


@dataclass
class TruncationPoint:
    pct: int
    truncated_cot: str
    generated_answer: str | None


@dataclass
class TruncationResult:
    problem_text: str
    correct_answer: str
    full_cot: str
    full_answer: str | None
    truncations: list[TruncationPoint]


@dataclass
class CorruptionResult:
    problem_id: str
    condition: str
    generated_answer: str | None
    correct_answer: str


@dataclass
class BiasResult:
    problem_text: str
    correct_answer: str
    full_prompt: str
    cot: str
    answer: str | None
    flagged: bool
