"""LLM client — one seam for all API calls. Groq primary, NVIDIA fallback."""
import os, re, time, random
from dotenv import load_dotenv
from groq import Groq, RateLimitError
from openai import OpenAI, APITimeoutError

from src.config import config

load_dotenv()


class LLMClient:
    def __init__(self, timeout=60, retry_max=5):
        self.timeout = timeout
        self.retry_max = retry_max
        self.groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.nvidia_client = OpenAI(
            api_key=os.environ["NVIDIA_API_KEY"],
            base_url="https://integrate.api.nvidia.com/v1",
        )
        self.groq_model = config.groq_model
        self.nvidia_model = config.nvidia_model

    def generate(self, messages) -> tuple[str | None, str]:
        """Returns (text, provider). Respects primary_provider ordering."""
        providers = [("groq", self._try_groq), ("nvidia", self._try_nvidia)]
        if config.primary_provider == "nvidia":
            providers.reverse()
        for name, fn in providers:
            text = fn(messages)
            if text:
                return text, name
        return None, "error"

    def _try_groq(self, messages):
        for attempt in range(self.retry_max):
            try:
                resp = self.groq_client.chat.completions.create(
                    model=self.groq_model, temperature=0.0, seed=42,
                    messages=messages, timeout=self.timeout,
                )
                return resp.choices[0].message.content.strip()
            except (RateLimitError, APITimeoutError):
                if attempt < self.retry_max - 1:
                    time.sleep(2 ** attempt + random.random() * 2)
            except Exception:
                if attempt < self.retry_max - 1:
                    time.sleep(2 ** attempt + random.random() * 2)
        return None

    def _try_nvidia(self, messages):
        for attempt in range(self.retry_max):
            try:
                resp = self.nvidia_client.chat.completions.create(
                    model=self.nvidia_model, temperature=0.0, seed=42,
                    messages=messages, timeout=self.timeout,
                )
                return resp.choices[0].message.content.strip()
            except APITimeoutError:
                if attempt < self.retry_max - 1:
                    time.sleep(2 ** attempt + random.random() * 2)
            except Exception:
                if attempt < self.retry_max - 1:
                    time.sleep(2 ** attempt + random.random() * 2)
        return None


def extract_answer(text: str) -> str | None:
    m = re.search(r"Answer:\s*(-?[\d.]+)", text)
    if m:
        return m.group(1)
    m = re.search(r"answer\s*[=:]\s*(-?[\d.]+)", text, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def is_malformed(text: str) -> bool:
    return bool(re.search(r",0", text))
