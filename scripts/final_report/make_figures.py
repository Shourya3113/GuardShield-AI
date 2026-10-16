"""
Figures for the NTCC final project report (docs/01 Reports/Final Project Report/figures/).
Every number is read from the committed result files; nothing is typed in.

  python scripts/final_report/make_figures.py
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

BASE = Path(__file__).resolve().parents[2]
REPORTS = BASE / "docs" / "01 Reports"
OUT = REPORTS / "Final Project Report" / "figures"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e6e5e1"
BLUE, RED, GRAY = "#2a78d6", "#e34948", "#f0efec"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED})


def confusion(path, title, out, neg="Benign", pos="Attack"):
    d = json.loads(path.read_text(encoding="utf-8"))
    cm = d["metrics"]["confusion_matrix"]
    cells = [[cm["tn"], cm["fp"]], [cm["fn"], cm["tp"]]]
    fig, ax = plt.subplots(figsize=(3.6, 3.0))
    total = sum(sum(r) for r in cells)
    for i in range(2):
        for j in range(2):
            correct = i == j
            ax.add_patch(plt.Rectangle((j, i), 0.96, 0.96, facecolor=BLUE if correct else GRAY, edgecolor="none"))
            ax.text(j + 0.48, i + 0.42, f"{cells[i][j]}", ha="center", va="center", fontsize=15,
                    color="white" if correct else INK, fontweight="bold")
            ax.text(j + 0.48, i + 0.68, f"{100 * cells[i][j] / total:.1f}%", ha="center", va="center",
                    fontsize=8, color="white" if correct else MUTED)
    ax.set_xlim(0, 1.96)
    ax.set_ylim(1.96, 0)
    ax.set_xticks([0.48, 1.48], [f"Predicted\n{neg.lower()}", f"Predicted\n{pos.lower()}"])
    ax.set_yticks([0.48, 1.48], [f"Actual\n{neg.lower()}", f"Actual\n{pos.lower()}"])
    ax.tick_params(length=0, colors=MUTED)
    for s in ax.spines.values():
        s.set_visible(False)
    m = d["metrics"]
    ax.set_title(f"{title}\naccuracy {100 * m['accuracy']:.2f}%, recall {100 * m['recall']:.2f}%, FPR {100 * m['fpr']:.2f}%",
                 fontsize=8.5, color=INK)
    fig.tight_layout()
    fig.savefig(OUT / out, dpi=220)
    plt.close(fig)


def box(ax, x, y, w, h, text, fill="#ffffff", edge=MUTED, bold=False, size=8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                facecolor=fill, edgecolor=edge, linewidth=1.1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color=INK,
            fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, a, b, label=None, color=MUTED, dy=0.12):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=11, color=color, linewidth=1.2))
    if label:
        ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + dy, label, ha="center", va="bottom", fontsize=7, color=color)


def architecture(out):
    """Request path left to right; each stage's reject path drops below it; side inputs sit above."""
    fig, ax = plt.subplots(figsize=(7.6, 3.3))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    w, h, y = 1.45, 0.95, 2.0
    xs = [0.1, 1.85, 3.6, 5.35, 7.1, 8.85]
    main = [("User prompt", "#ffffff", False), ("Stage 1\nDeBERTa-v3\npre-scan", "#dbe8f8", True),
            ("Upstream LLM\n(streamed)", "#ffffff", False), ("Entropy\nmonitor", "#dbe8f8", True),
            ("Stage 2\nNLI fact\nverifier", "#dbe8f8", True), ("Verified\nresponse", "#e2f3ea", False)]
    for x, (t, fill, bold) in zip(xs, main):
        box(ax, x, y, w, h, t, fill=fill, bold=bold, size=7.5)
    for x0, x1 in zip(xs, xs[1:]):
        arrow(ax, (x0 + w, y + h / 2), (x1, y + h / 2))
    below = [(1, "Blocked: HTTP 403\n(risk >= 0.5)"), (3, "Generation halted\n(entropy spike)"),
             (4, "Contradiction flagged /\nunverified (neutral)")]
    for i, t in below:
        box(ax, xs[i] - 0.05, 0.25, w + 0.1, 0.85, t, fill="#fbe1e1", size=6.8)
        arrow(ax, (xs[i] + w / 2, y), (xs[i] + w / 2, 1.1), color=RED)
    above = [(1, "Signed assistant\nhistory (HMAC)"), (4, "Retrieval context\n(RAG evidence)")]
    for i, t in above:
        box(ax, xs[i] - 0.05, 3.55, w + 0.1, 0.8, t, size=6.8)
        arrow(ax, (xs[i] + w / 2, 3.55), (xs[i] + w / 2, y + h), color=BLUE)
    ax.text(5.2, 0.02, "GuardShield runs as a FastAPI sidecar in front of an OpenAI-compatible LLM endpoint",
            ha="center", fontsize=7, color=MUTED)
    fig.tight_layout()
    fig.savefig(OUT / out, dpi=220)
    plt.close(fig)


def gantt(out):
    tasks = [  # (label, first week, last week, kind) -- the 12-week NTCC schedule, from the WPRs
        ("Problem statement, architecture, synopsis", 1, 1, "plan"),
        ("Literature survey and threat model", 1, 2, "research"),
        ("Data ingestion and obfuscation synthesis", 2, 3, "data"),
        ("Stage 1 DeBERTa training", 3, 4, "build"),
        ("Stage 2 NLI verifier", 4, 5, "build"),
        ("Pipeline, proxy and entropy engine", 5, 6, "build"),
        ("Multi-dataset benchmarking", 6, 8, "eval"),
        ("Mega benchmark, FEVER/HaluEval, latency", 8, 10, "eval"),
        ("Project audit and decontaminated retraining", 10, 11, "eval"),
        ("Study 1: paired audit of 19 detectors", 10, 12, "research"),
        ("Study 2: canonicalization vs augmentation", 11, 12, "research"),
        ("Research paper and final report", 11, 12, "plan"),
    ]
    colors = {"plan": "#8a8985", "research": BLUE, "data": "#1baf7a", "build": "#eda100", "eval": RED}
    names = {"plan": "planning and writing", "research": "research", "data": "data", "build": "system build",
             "eval": "evaluation"}
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    for i, (label, a, b, kind) in enumerate(tasks):
        ax.barh(i, b - a + 0.9, left=a - 0.45, height=0.6, color=colors[kind], edgecolor="white")
    ax.set_yticks(range(len(tasks)), [t[0] for t in tasks], fontsize=7.5, color=INK)
    ax.invert_yaxis()
    ax.set_xticks(range(1, 13), [f"W{w}" for w in range(1, 13)], fontsize=7.5, color=MUTED)
    ax.set_xlim(0.4, 12.6)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[k]) for k in names]
    ax.legend(handles, names.values(), loc="lower center", bbox_to_anchor=(0.4, -0.22), ncol=5, frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / out, dpi=220)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    confusion(REPORTS / "raw_eval_in_distribution_test_698.json", "Stage 1, in-distribution test (698)", "cm_stage1_in_dist.png")
    confusion(REPORTS / "raw_eval_out_of_distribution_500.json", "Stage 1, zero-shot OOD test (500)", "cm_stage1_ood.png")
    confusion(REPORTS / "raw_eval_stage2_factuality_800.json", "Stage 2, FEVER + HaluEval (800)", "cm_stage2.png",
              neg="Grounded", pos="Hallucinated")
    architecture("architecture.png")
    gantt("gantt.png")
    print("wrote", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
