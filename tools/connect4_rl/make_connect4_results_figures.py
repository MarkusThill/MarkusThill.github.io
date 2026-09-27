"""
Figures for "Near-Perfect Connect-4 after Five Minutes of Training: Reinforcement Learning from Scratch by Self-Play".

Run from the repository root, with the published extract of the ten runs (or the run folder written by
the training notebook, which gives identical results):

    tools/connect4_rl/.venv/bin/python tools/connect4_rl/make_connect4_results_figures.py \
        --run assets/data/2026-08-27-near-perfect-connect4-in-five-minutes \
        --out assets/img/2026-08-27-near-perfect-connect4-in-five-minutes \
        --numbers tools/connect4_rl/data/post09/numbers.json

Test renders (for example of an older run) go to any other --out directory. The script also prints
the numbers the post quotes, so that text and figures come from the same computation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import connect4_results as cr

INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
DRAW = "#c3c2b7"
LABELS = {
    "random": "random moves",
    "bitbully-1ply": "search, depth 1",
    "bitbully-2ply": "search, depth 2",
    "bitbully-4ply": "search, depth 4",
    "bitbully-8ply": "search, depth 8",
    "bitbully-8-ply-book8ply": "depth 8 + 8-ply book",
    "bitbully-10-ply-book8ply": "depth 10 + 8-ply book",
    "bitbully-16ply-book12ply": "depth 16 + 12-ply book",
    cr.FULL_STRENGTH: "full strength (perfect)",
}
FIVE_MINUTES = 5.0

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
    "axes.titlecolor": INK, "axes.titlesize": 11, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "figure.facecolor": "white", "savefig.facecolor": "white",
    "savefig.dpi": 160, "legend.frameon": False,
})
percent = matplotlib.ticker.PercentFormatter(1.0)


def save(fig, out: Path, name: str) -> None:
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / name, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print("wrote", out / name)


def fig_learning_curve(repeats, out, numbers):
    steps, wdl = cr.outcome_curve(repeats, cr.FULL_STRENGTH, first=True)
    win = cr.rates(wdl)["win"]  # [repeats, steps]
    minutes = np.array([[cr.training_time(r)[s] / 60 for s in steps] for r in repeats])
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    for i in range(len(repeats)):
        ax.plot(minutes[i], win[i], color=BLUE, alpha=0.22, lw=1)
    ci = np.array([cr.bootstrap_ci(win[:, j]) for j in range(len(steps))])
    t_mean = minutes.mean(axis=0)
    ax.fill_between(t_mean, ci[:, 0], ci[:, 1], color=BLUE, alpha=0.18, lw=0)
    ax.plot(t_mean, win.mean(axis=0), color=BLUE, lw=2.2, label="mean of the repeats (95% CI)")
    ax.axvline(FIVE_MINUTES, color=AXIS, lw=1)
    within = np.flatnonzero(minutes.max(axis=0) <= FIVE_MINUTES)
    if len(within):
        j = within[-1]
        numbers["five_minutes"] = {"step": int(steps[j]), "win_rate_mean": float(win[:, j].mean()),
                                   "ci": ci[j].tolist(), "minutes_max": float(minutes[:, j].max())}
        ax.annotate(f"{win[:, j].mean():.1%} after {steps[j]:,} steps", xy=(t_mean[j], win[:, j].mean()),
                    xytext=(t_mean[j], 0.62), ha="center", fontsize=8.5, color=INK2,
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8))
    ax.text(FIVE_MINUTES - 0.06, 0.04, "5 minutes", fontsize=8, color=MUTED, ha="right")
    ax.set_ylim(0, 1.02)
    ax.yaxis.set_major_formatter(percent)
    ax.set_xlim(0, max(minutes.max() * 1.02, FIVE_MINUTES + 0.8))
    ax.set_xlabel("training time without evaluations (minutes)")
    ax.set_ylabel("win rate when moving first")
    ax.set_title("against full-strength BitBully", loc="left")
    ax.legend(loc="lower right", fontsize=8.5)
    save(fig, out, "learning-curve.png")
    numbers["final_first_vs_full"] = {"win_rate_mean": float(win[:, -1].mean()), "ci": ci[-1].tolist(),
                                      "per_repeat": win[:, -1].tolist()}


def fig_final_outcomes(repeats, out, numbers):
    opponents = ["random"] + cr.SEARCH_OPPONENTS
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.6), sharey=True)
    for ax, first, title in zip(axes, (True, False), ("agent moves first", "agent moves second")):
        rows = []
        for opp in opponents:
            step = max(a["step"] for a in repeats[0].arena)
            counts = np.sum([cr.agent_outcome(cr.arena_at(r, step), opp, first) for r in repeats], axis=0)
            rows.append(counts / counts.sum())
            numbers.setdefault("final_outcomes", {})[f"{opp}|{'first' if first else 'second'}"] = counts.tolist()
        rows = np.array(rows)
        y = np.arange(len(opponents))[::-1]
        left = np.zeros(len(opponents))
        for k, (color, name) in enumerate([(BLUE, "win"), (DRAW, "draw"), (ORANGE, "loss")]):
            ax.barh(y, rows[:, k], left=left, color=color, height=0.72, label=name, edgecolor="white", lw=1)
            left += rows[:, k]
        for yi, r in zip(y, rows):
            if r[0] >= 0.12:
                ax.text(r[0] / 2, yi, f"{r[0]:.0%}", ha="center", va="center", fontsize=8, color="white")
        ax.set_xlim(0, 1)
        ax.xaxis.set_major_formatter(percent)
        ax.set_title(title, loc="left")
        ax.set_xlabel("share of the final games (all repeats pooled)")
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(np.arange(len(opponents))[::-1], [LABELS[o] for o in opponents])
    axes[1].legend(loc="lower right", fontsize=8.5, ncol=3, bbox_to_anchor=(1.0, -0.28))
    fig.tight_layout()
    save(fig, out, "final-outcomes.png")


def fig_opponent_epsilon(repeats, out, numbers):
    eps_values = [0.0, 0.1, 0.2, 0.3]
    step = max(a["step"] for a in repeats[0].arena)
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    rng = np.random.default_rng(0)
    for first, color, label in ((True, BLUE, "agent moves first"), (False, ORANGE, "agent moves second")):
        means, cis = [], []
        for e in eps_values:
            wdl = np.array([cr.agent_outcome(cr.arena_at(r, step), cr.FULL_STRENGTH, first, e) for r in repeats], float)
            win = cr.rates(wdl)["win"]
            ax.scatter(e + rng.uniform(-0.008, 0.008, len(win)), win, s=12, color=color, alpha=0.35, lw=0)
            means.append(win.mean())
            cis.append(cr.bootstrap_ci(win))
            numbers.setdefault("epsilon_curve", {})[f"{'first' if first else 'second'}|{e}"] = {
                "win_rate_mean": float(win.mean()), "ci": cis[-1]}
        cis = np.array(cis)
        ax.errorbar(eps_values, means, yerr=[np.array(means) - cis[:, 0], cis[:, 1] - np.array(means)],
                    color=color, lw=2, capsize=3, marker="o", ms=5, label=label)
    ax.set_xticks(eps_values)
    ax.set_xlabel("opponent's probability ε of a random non-losing move")
    ax.set_ylabel("win rate after training")
    ax.yaxis.set_major_formatter(percent)
    ax.set_ylim(-0.02, 1.02)
    ax.set_title("against full-strength BitBully", loc="left")
    ax.legend(loc="center right", fontsize=8.5)
    save(fig, out, "win-rate-vs-opponent-epsilon.png")


def fig_time_split(repeats, out, numbers):
    train = np.array([max(cr.training_time(r).values()) for r in repeats]) / 60
    evaluation = np.array([sum(cr.evaluation_pauses(r).values()) for r in repeats]) / 60
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    y = np.arange(len(repeats))[::-1]
    ax.barh(y, train, color=BLUE, height=0.7, label="training", edgecolor="white", lw=1)
    ax.barh(y, evaluation, left=train, color=DRAW, height=0.7, label="evaluations (paused training)",
            edgecolor="white", lw=1)
    ax.set_yticks(y, [f"repeat {r.index + 1}" for r in repeats])
    ax.set_xlabel("minutes")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower center", fontsize=8.5, ncol=2, bbox_to_anchor=(0.5, 1.0))
    save(fig, out, "training-vs-evaluation-time.png")
    numbers["time_minutes"] = {"training_mean": float(train.mean()), "training_min": float(train.min()),
                               "training_max": float(train.max()), "evaluation_mean": float(evaluation.mean())}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True, help="run folder or its extract (export_run_results.py)")
    parser.add_argument("--out", type=Path, required=True, help="directory for the figures")
    parser.add_argument("--numbers", type=Path, help="write the quoted numbers to this JSON file (default: print)")
    args = parser.parse_args()
    params, repeats = cr.load_run(args.run)
    for r in repeats:
        cr.check_timing(r)
    numbers = {"gpu_name": params.get("gpu_name"), "commit_sha": params.get("commit_sha"),
               "batch_size": params["batch_size"], "tau": params["tau"], "n_steps": params["n_steps"],
               "repeats": len(repeats),
               "games_estimate_mean": float(np.mean([cr.estimated_games(r, params["batch_size"], params["n_steps"])
                                                     for r in repeats]))}
    fig_learning_curve(repeats, args.out, numbers)
    fig_final_outcomes(repeats, args.out, numbers)
    fig_opponent_epsilon(repeats, args.out, numbers)
    fig_time_split(repeats, args.out, numbers)
    if args.numbers:
        args.numbers.parent.mkdir(parents=True, exist_ok=True)
        args.numbers.write_text(json.dumps(numbers, indent=1))
        print("wrote", args.numbers)
    else:
        print(json.dumps(numbers, indent=1))


if __name__ == "__main__":
    main()
