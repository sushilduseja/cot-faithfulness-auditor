"""Token-level corruption rules — pure functions, no model downloads."""
import re
import random


def corrupt_random(text: str, rate: float = 0.15) -> str:
    """Replace `rate` fraction of characters with random ASCII (not whitespace)."""
    chars = list(text)
    n = max(1, int(len(chars) * rate))
    indices = random.sample(range(len(chars)), n)
    for i in indices:
        if not chars[i].isspace():
            chars[i] = chr(random.randint(33, 126))
    return "".join(chars)


def corrupt_semantic(text: str) -> str:
    """Replace one numeric value with a plausible wrong number (off-by-one or near-miss)."""
    nums = re.findall(r"\b\d+(?:\.\d+)?\b", text)
    if not nums:
        return text
    target = random.choice(nums)
    val = float(target)
    if val > 1 and random.random() < 0.5:
        wrong = str(max(1, int(val) + random.choice([-1, 1])))
    else:
        shift = random.choice([0.9, 1.1])
        wrong = str(int(round(val * shift)))
    return text.replace(target, wrong, 1)


def corrupt_deletion(text: str, rate: float = 0.1) -> str:
    """Delete `rate` fraction of tokens (words)."""
    words = text.split()
    n = max(1, int(len(words) * rate))
    indices = set(random.sample(range(len(words)), n))
    return " ".join(w for i, w in enumerate(words) if i not in indices)
