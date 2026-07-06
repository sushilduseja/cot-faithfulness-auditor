"""06 — Generate publication-quality charts from experiment outputs."""
import json, random
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

plt.rcParams.update({"font.size": 11, "figure.dpi": 150})
DATA_DIR = Path("data")


def bootstrap_ci(values, n=1000, ci=0.95):
    means = []
    for _ in range(n):
        sample = [random.choice(values) for _ in range(len(values))]
        means.append(sum(sample) / len(sample))
    means.sort()
    alpha = (1 - ci) / 2
    return means[int(alpha * n)], means[int((1 - alpha) * n)]


def main():
    with open(DATA_DIR / "baseline_results.json") as f:
        baseline = json.load(f)
    with open(DATA_DIR / "exp1_truncation_results.json") as f:
        trunc = json.load(f)
    with open(DATA_DIR / "exp2_corruption_results.json") as f:
        corrupt = json.load(f)
    with open(DATA_DIR / "exp3_bias_results.json") as f:
        bias = json.load(f)

    # Chart 1: Truncation
    pcts = [10, 25, 50, 75, 100]
    rates, cis = [], []
    for pct in pcts:
        matches = []
        for entry in trunc:
            full = entry.get("full_answer")
            for t in entry.get("truncations", []):
                if t.get("pct") == pct:
                    matches.append(1 if t.get("generated_answer") == full else 0)
        r = sum(matches) / len(matches) if matches else 0
        lo, hi = bootstrap_ci(matches)
        rates.append(r)
        cis.append((r - lo, hi - r))

    fig, ax = plt.subplots(figsize=(6, 4))
    xs = np.array(pcts)
    ax.errorbar(xs, rates, yerr=np.array(cis).T, fmt="o-", capsize=4, capthick=1.5, color="#2563eb")
    ax.set_xlabel("Truncation %")
    ax.set_ylabel("Match rate vs full CoT")
    ax.set_title("Chart 1: Progressive Truncation")
    ax.set_ylim(-0.05, 1.05)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.axhline(y=1.0, color="gray", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(DATA_DIR / "chart1_truncation.png")
    plt.close()
    print(f"Chart 1 saved. Match rates: {list(zip(pcts, [f'{r:.0%}' for r in rates]))}")

    # Chart 2: Corruption
    conditions = ["random", "semantic", "deletion"]
    cond_acc = {c: [] for c in conditions}
    for entry in corrupt:
        cond = entry["condition"]
        gen = entry.get("generated_answer")
        correct = entry.get("correct_answer")
        cond_acc[cond].append(1 if gen == str(correct) else 0)

    means = [sum(cond_acc[c]) / len(cond_acc[c]) if cond_acc[c] else 0 for c in conditions]
    errs = []
    for c in conditions:
        lo, hi = bootstrap_ci(cond_acc[c])
        idx = conditions.index(c)
        errs.append((means[idx] - lo, hi - means[idx]))

    fig, ax = plt.subplots(figsize=(6, 4))
    xs = np.arange(len(conditions))
    ax.bar(xs, means, yerr=np.array(errs).T, capsize=4, width=0.5, color=["#2563eb", "#059669", "#d97706"])
    ax.set_xticks(xs)
    ax.set_xticklabels(conditions)
    ax.set_ylabel("Accuracy (answer matches correct)")
    ax.set_title("Chart 2: Token Corruption")
    ax.set_ylim(-0.05, 1.05)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    plt.tight_layout()
    plt.savefig(DATA_DIR / "chart2_corruption.png")
    plt.close()
    print(f"Chart 2 saved. Accuracies: {dict(zip(conditions, [f'{m:.0%}' for m in means]))}")

    # Chart 3: Flag rate
    flags = [1 if e["flagged"] else 0 for e in bias]
    rate = sum(flags) / len(flags) if flags else 0
    lo, hi = bootstrap_ci(flags)

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(["Biased prompt"], [rate], yerr=[[rate - lo], [hi - rate]],
           capsize=4, width=0.4, color="#dc2626")
    ax.axhline(y=0, color="gray", linestyle="--", alpha=0.3, label="Unbiased baseline (expected)")
    ax.set_ylabel("Flag rate")
    ax.set_title("Chart 3: Bias Flag Rate")
    ax.set_ylim(-0.05, 1.05)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.legend()
    plt.tight_layout()
    plt.savefig(DATA_DIR / "chart3_bias.png")
    plt.close()
    print(f"Chart 3 saved. Flag rate: {rate:.0%} (95% CI: {lo:.0%}–{hi:.0%})")

    print(f"\nBaseline stability: {sum(1 for e in baseline if e.get('stable'))}/{len(baseline)}")
    print("All charts saved to data/chart*.png")


if __name__ == "__main__":
    main()
