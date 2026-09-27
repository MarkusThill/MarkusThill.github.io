"""
Comparison of training recipes for "Near-Perfect Connect-4 after Five Minutes of Training: Reinforcement Learning from Scratch by Self-Play": the recipe of the post against two variants, ten runs each.

Run from the repository root with the published extracts (or the run folders written by the training notebook):

    tools/connect4_rl/.venv/bin/python tools/connect4_rl/make_connect4_comparison_figures.py \
        --run "this post (τ = 0.15)=assets/data/2026-08-27-near-perfect-connect4-in-five-minutes" \
        --run "slower target network (τ = 0.05)=assets/data/2026-08-27-near-perfect-connect4-in-five-minutes/variant-slow-target" \
        --run "decaying exploration (ε 0.2 → 0.02, λ = 0.75, n = 8)=assets/data/2026-08-27-near-perfect-connect4-in-five-minutes/variant-decaying-epsilon" \
        --out assets/img/2026-08-27-near-perfect-connect4-in-five-minutes \
        --numbers tools/connect4_rl/data/post09/comparison_numbers.json

The first run is the reference. Late-phase numbers pool the last five evaluations of every run (steps 21,000 to
25,000, i.e. 250 games per run and condition), which describes the level a recipe ends at with less noise than a
single evaluation of 50 games.
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
COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]  # fixed categorical order: reference, first variant, second variant
FIVE_MINUTES = 5.0
LATE_STEPS = range(21_000, 25_001, 1_000)
EARLY_EVALUATIONS = 5  # steps 1,000 to 5,000, the first minutes of training
# (label, opponent, agent moves first, opponent epsilon) of the late-phase panel
CONDITIONS = [
    ("first vs.\nperfect play", cr.FULL_STRENGTH, True, 0.0),
    ("second vs.\ndepth 16 + book", "bitbully-16ply-book12ply", False, 0.0),
    ("second vs.\nperfect, ε = 0.1", cr.FULL_STRENGTH, False, 0.1),
    ("second vs.\nperfect, ε = 0.2", cr.FULL_STRENGTH, False, 0.2),
    ("second vs.\nperfect, ε = 0.3", cr.FULL_STRENGTH, False, 0.3),
]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
    "axes.titlecolor": INK, "axes.titlesize": 11, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "figure.facecolor": "white", "savefig.facecolor": "white",
    "savefig.dpi": 160, "legend.frameon": False,
})
percent = matplotlib.ticker.PercentFormatter(1.0)


def pooled(rep: cr.Repeat, opponent: str, first: bool, eps: float, steps) -> tuple[float, float]:
    """Win rate and score of one run over several evaluations (games pooled)."""
    w = d = l = 0
    for s in steps:
        a, b, c = cr.agent_outcome(cr.arena_at(rep, s), opponent, first, eps)
        w, d, l = w + a, d + b, l + c
    n = w + d + l
    return w / n, (w - l) / n


def all_round_score(rep: cr.Repeat, steps, sides=(True, False)) -> float:
    """Mean score over the conditions against BitBully (as the selection tournament), optionally one side only."""
    scores = []
    for opp in cr.SEARCH_OPPONENTS:
        for first in sides:
            for eps in ([0.0, 0.1, 0.2, 0.3] if opp == cr.FULL_STRENGTH else [0.0]):
                if len(sides) == 1 and not first and opp == cr.FULL_STRENGTH and eps == 0.0:
                    continue  # unwinnable; excluded from the one-sided second-player score
                scores.append(pooled(rep, opp, first, eps, steps)[1])
    return float(np.mean(scores))


def summary(values: np.ndarray) -> dict:
    lo, hi = cr.bootstrap_ci(values)
    return {"mean": float(values.mean()), "ci": [float(lo), float(hi)], "per_run": values.tolist()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="append", required=True, help="label=folder (run folder or extract)")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--numbers", type=Path)
    args = parser.parse_args()
    recipes = []
    for item in args.run:
        label, folder = item.rsplit("=", 1)  # labels may contain "=", folders do not
        params, repeats = cr.load_run(folder)
        recipes.append((label, params, repeats))

    numbers = {"late_steps": list(LATE_STEPS), "recipes": {}}
    early_by_recipe = []
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 4.6), gridspec_kw={"width_ratios": [1.0, 1.25]})
    width = 0.8 / len(recipes)
    for k, (label, params, repeats) in enumerate(recipes):
        color = COLORS[k]
        steps, wdl = cr.outcome_curve(repeats, cr.FULL_STRENGTH, first=True)
        win = cr.rates(wdl)["win"]
        minutes = np.array([[cr.training_time(r)[s] / 60 for s in steps] for r in repeats])
        ci = np.array([cr.bootstrap_ci(win[:, j]) for j in range(len(steps))])
        t_mean, w_mean = minutes.mean(axis=0), win.mean(axis=0)
        ax1.fill_between(t_mean, ci[:, 0], ci[:, 1], color=color, alpha=0.14, lw=0)
        ax1.plot(t_mean, w_mean, color=color, lw=2, label=label)

        rec = {"settings": {key: params[key] for key in ("batch_size", "tau", "epsilon", "lam", "n_truncate",
                                                          "commit_sha", "gpu_name")},
               "training_minutes": summary(np.array([cr.training_time(r)[params["n_steps"]] / 60 for r in repeats])),
               "curve": {int(s): {"win_mean": float(w_mean[j]), "ci": ci[j].tolist(), "minutes": float(t_mean[j])}
                         for j, s in enumerate(steps)}}
        first90 = next((j for j in range(len(steps)) if w_mean[j] >= 0.9), None)
        rec["first_step_mean_ge_90"] = None if first90 is None else {"step": int(steps[first90]),
                                                                       "minutes": float(t_mean[first90])}
        early = win[:, :EARLY_EVALUATIONS].mean(axis=1)  # per run: mean win rate over the first evaluations
        rec["early"] = {**summary(early), "steps": [int(s) for s in steps[:EARLY_EVALUATIONS]],
                        "minutes": float(t_mean[EARLY_EVALUATIONS - 1])}
        early_by_recipe.append(early)
        within = np.flatnonzero(minutes.max(axis=0) <= FIVE_MINUTES)
        j5 = int(within[-1])
        rec["five_minutes"] = {"step": int(steps[j5]), "win_mean": float(w_mean[j5]), "ci": ci[j5].tolist()}

        late = {}
        for i, (cond, opp, first, eps) in enumerate(CONDITIONS):
            rates = np.array([pooled(r, opp, first, eps, LATE_STEPS)[0] for r in repeats])
            late[cond.replace("\n", " ")] = summary(rates)
            lo, hi = late[cond.replace("\n", " ")]["ci"]
            x = i + (k - (len(recipes) - 1) / 2) * width
            ax2.scatter(np.full(len(rates), x), rates, s=9, color=color, alpha=0.35, lw=0, zorder=2)
            ax2.errorbar(x, rates.mean(), yerr=[[rates.mean() - lo], [hi - rates.mean()]], fmt="o", ms=6,
                         color=color, ecolor=color, elinewidth=1.6, capsize=0, zorder=3,
                         markeredgecolor="white", markeredgewidth=1.2)
        rec["late_win_rates"] = late
        rec["all_round_late"] = summary(np.array([all_round_score(r, LATE_STEPS) for r in repeats]))
        rec["all_round_final"] = summary(np.array([all_round_score(r, [params["n_steps"]]) for r in repeats]))
        rec["first_side_score_late"] = summary(np.array([all_round_score(r, LATE_STEPS, (True,)) for r in repeats]))
        rec["second_side_score_late"] = summary(np.array([all_round_score(r, LATE_STEPS, (False,)) for r in repeats]))
        numbers["recipes"][label] = rec

    # Early head start of the reference recipe over each variant: difference of the means, bootstrap over runs.
    rng = np.random.default_rng(42)
    for (label, _, _), early in zip(recipes[1:], early_by_recipe[1:]):
        ref = early_by_recipe[0]
        diffs = [rng.choice(ref, len(ref)).mean() - rng.choice(early, len(early)).mean() for _ in range(10_000)]
        numbers["recipes"][label]["early_difference_to_reference"] = {
            "mean": float(ref.mean() - early.mean()), "ci": [float(np.percentile(diffs, 2.5)),
                                                             float(np.percentile(diffs, 97.5))]}

    ax1.axvline(FIVE_MINUTES, color=AXIS, lw=1)
    ax1.text(FIVE_MINUTES + 0.08, 0.24, "5 minutes", fontsize=8, color=MUTED, ha="left")
    ax1.set_ylim(0, 1.02)
    ax1.set_xlim(0, 9.2)
    ax1.yaxis.set_major_formatter(percent)
    ax1.set_xlabel("training time without evaluations (minutes)")
    ax1.set_ylabel("win rate when moving first")
    ax1.set_title("learning curve against perfect play", loc="left")
    ax1.legend(loc="lower right", fontsize=8.2)  # colours identify the recipes in both panels

    ax2.set_xticks(range(len(CONDITIONS)), [c[0] for c in CONDITIONS], fontsize=8.6)
    ax2.set_ylim(0.3, 1.02)
    ax2.yaxis.set_major_formatter(percent)
    ax2.set_ylabel("win rate, last five evaluations")
    ax2.set_title("level at the end of training", loc="left")
    ax2.grid(axis="x", visible=False)
    fig.tight_layout()
    args.out.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out / "recipe-comparison.png", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print("wrote", args.out / "recipe-comparison.png")

    text = json.dumps(numbers, indent=1, ensure_ascii=False)
    if args.numbers:
        args.numbers.write_text(text)
    for label, rec in numbers["recipes"].items():
        print(label, "| minutes", round(rec["training_minutes"]["mean"], 2), "| ≥90% at", rec["first_step_mean_ge_90"],
              "| 5 min", rec["five_minutes"], "| all-round late", rec["all_round_late"]["mean"], rec["all_round_late"]["ci"])


if __name__ == "__main__":
    main()
