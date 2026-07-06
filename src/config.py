"""Configuration from environment variables — single source of tunables."""
import os
from dataclasses import dataclass


@dataclass
class Config:
    num_problems: int = 150
    runs_per_condition: int = 1
    primary_provider: str = "groq"
    groq_model: str = "llama-3.1-8b-instant"
    nvidia_model: str = "meta/llama-3.1-8b-instruct"
    num_workers: int = 4
    api_timeout: int = 60
    retry_max: int = 5

    def __post_init__(self):
        self.num_problems = int(os.environ.get("NUM_PROBLEMS", self.num_problems))
        self.runs_per_condition = int(os.environ.get("RUNS_PER_CONDITION", self.runs_per_condition))
        self.primary_provider = os.environ.get("PRIMARY_PROVIDER", self.primary_provider)
        self.num_workers = int(os.environ.get("NUM_WORKERS", self.num_workers))
        self.api_timeout = int(os.environ.get("API_TIMEOUT", self.api_timeout))


config = Config()
