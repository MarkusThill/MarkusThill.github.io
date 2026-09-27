"""
Loading and analysing the training runs of the Connect-4 n-tuple agent.

This module holds the analysis code quoted in the post "Near-Perfect Connect-4 after Five Minutes of
Training: Reinforcement Learning from Scratch by Self-Play". It reads the files which techdays26's
`TrainingLogger` writes for every repeat of a run:

    <run>/0_params.json                  configuration, GPU name, versions
    <run>/repeat_<i>/0_metrics.json      training metrics, every 100 steps
    <run>/repeat_<i>/0_arena_metrics.json  arena results, every 1,000 steps

or the compact extract of `export_run_results.py` (params.json, metrics.csv.gz, arena.csv.gz).

Arena rows store the outcome from Yellow's point of view (Yellow moves first). All functions
below turn them into outcomes of the learned agent ("ntuple"), for the side it played.
"""

from __future__ import annotations

import csv
import gzip
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

AGENT = "ntuple"
FULL_STRENGTH = "bitbully-full-strength"
SEARCH_OPPONENTS = [  # weakest to strongest, as configured in the training notebook
    "bitbully-1ply",
    "bitbully-2ply",
    "bitbully-4ply",
    "bitbully-8ply",
    "bitbully-8-ply-book8ply",
    "bitbully-10-ply-book8ply",
    "bitbully-16ply-book12ply",
    FULL_STRENGTH,
]


@dataclass
class Repeat:
    index: int
    metrics: list[dict]  # one row every 100 training steps
    arena: list[dict]  # one row every 1,000 training steps


def load_run(folder: str | Path) -> tuple[dict, list[Repeat]]:
    """Configuration and all repeats of a training run."""
    folder = Path(folder)
    if (folder / "metrics.csv.gz").exists():
        return _load_extract(folder)
    params = json.loads((folder / "0_params.json").read_text())
    repeats = []
    for d in sorted(folder.glob("repeat_*"), key=lambda p: int(p.name.split("_")[1])):
        repeats.append(Repeat(
            index=int(d.name.split("_")[1]),
            metrics=json.loads((d / "0_metrics.json").read_text()),
            arena=json.loads((d / "0_arena_metrics.json").read_text()),
        ))
    return params, repeats


def _number(text: str) -> int | float | str:
    for kind in (int, float):
        try:
            return kind(text)
        except ValueError:
            pass
    return text


def _read_csv_gz(path: Path) -> list[dict]:
    with gzip.open(path, "rt", newline="") as f:
        return [{k: _number(v) for k, v in row.items()} for row in csv.DictReader(f)]


def _load_extract(folder: Path) -> tuple[dict, list[Repeat]]:
    params = json.loads((folder / "params.json").read_text())
    metrics, arena = {}, {}
    for row in _read_csv_gz(folder / "metrics.csv.gz"):
        metrics.setdefault(row.pop("repeat"), []).append(row)
    for row in _read_csv_gz(folder / "arena.csv.gz"):
        steps = arena.setdefault(row.pop("repeat"), [])
        step, elapsed = row.pop("step"), row.pop("training_elapsed_s")
        if not steps or steps[-1]["step"] != step:
            steps.append({"step": step, "training_elapsed_s": elapsed, "aggregates": []})
        steps[-1]["aggregates"].append(row)
    return params, [Repeat(index=i, metrics=metrics[i], arena=arena[i]) for i in sorted(metrics)]


# ---------------------------------------------------------------------------
# Timing: training minutes without the evaluation pauses
# ---------------------------------------------------------------------------
def evaluation_pauses(rep: Repeat) -> dict[int, float]:
    """Duration (s) of every arena evaluation.

    At an evaluation step, the logger writes the metrics row first and runs the arena right
    afterwards; both rows carry the time elapsed since the same start. Their difference is
    the time for which training was paused.
    """
    t_metrics = {m["step"]: m["training_elapsed_s"] for m in rep.metrics}
    return {a["step"]: a["training_elapsed_s"] - t_metrics[a["step"]] for a in rep.arena}


def training_time(rep: Repeat) -> dict[int, float]:
    """Training-only time (s) at every evaluation step: elapsed time minus all earlier pauses."""
    t_metrics = {m["step"]: m["training_elapsed_s"] for m in rep.metrics}
    times, paused = {}, 0.0
    for step, pause in sorted(evaluation_pauses(rep).items()):
        times[step] = t_metrics[step] - paused
        paused += pause
    return times


def check_timing(rep: Repeat, tol_s: float = 1.0) -> None:
    """Training time plus all pauses must add up to the time of the last arena row."""
    pauses = evaluation_pauses(rep)
    last = max(pauses)
    assert all(p > 0 for p in pauses.values()), f"repeat {rep.index}: non-positive pause"
    total = training_time(rep)[last] + sum(pauses.values())
    assert abs(total - rep.arena[-1]["training_elapsed_s"]) < tol_s, f"repeat {rep.index}: timing mismatch"


# ---------------------------------------------------------------------------
# Outcomes from the agent's point of view
# ---------------------------------------------------------------------------
def agent_outcome(rows: list[dict], opponent: str, first: bool, opponent_eps: float = 0.0) -> tuple[int, int, int]:
    """Wins, draws and losses of the learned agent against `opponent` in one arena evaluation.

    `first=True`: the agent plays Yellow and moves first; otherwise it plays Red.
    `opponent_eps`: probability with which the opponent plays a random non-losing move instead.
    """
    for r in rows:
        if first and (r["agent_yellow"], r["agent_red"]) == (AGENT, opponent) and r["epsilon_red"] == opponent_eps:
            return r["yellow_wins"], r["draws"], r["red_wins"]
        if not first and (r["agent_yellow"], r["agent_red"]) == (opponent, AGENT) and r["epsilon_yellow"] == opponent_eps:
            return r["red_wins"], r["draws"], r["yellow_wins"]
    raise KeyError(f"no games of {AGENT} against {opponent} (first={first}, eps={opponent_eps})")


def arena_at(rep: Repeat, step: int) -> list[dict]:
    for a in rep.arena:
        if a["step"] == step:
            return a["aggregates"]
    raise KeyError(f"repeat {rep.index} has no evaluation at step {step}")


def outcome_curve(repeats: list[Repeat], opponent: str, first: bool, opponent_eps: float = 0.0):
    """Evaluation steps and a [repeats, steps, 3] array of wins/draws/losses (aligned by step)."""
    steps = sorted(set.intersection(*[{a["step"] for a in r.arena} for r in repeats]))
    wdl = np.array([[agent_outcome(arena_at(r, s), opponent, first, opponent_eps) for s in steps]
                    for r in repeats], dtype=float)
    return np.array(steps), wdl


def rates(wdl: np.ndarray) -> dict[str, np.ndarray]:
    """Win, draw and loss rates and the score (W - L) / N from counts [..., 3]."""
    n = wdl.sum(axis=-1)
    w, d, l = wdl[..., 0] / n, wdl[..., 1] / n, wdl[..., 2] / n
    return {"win": w, "draw": d, "loss": l, "score": w - l}


def bootstrap_ci(values: np.ndarray, n_boot: int = 10_000, ci: float = 0.95, seed: int = 42) -> tuple[float, float]:
    """Percentile bootstrap interval for the mean over repeats (as in lab2/2_plot_metrics.ipynb)."""
    values = np.asarray(values, dtype=float)
    if len(values) < 2:
        return float(values[0]), float(values[0])
    rng = np.random.default_rng(seed)
    means = rng.choice(values, size=(n_boot, len(values)), replace=True).mean(axis=1)
    alpha = (1 - ci) / 2
    return float(np.percentile(means, 100 * alpha)), float(np.percentile(means, 100 * (1 - alpha)))


def estimated_games(rep: Repeat, batch_size: int, n_steps: int) -> float:
    """Completed self-play games, estimated from the fraction of boards finishing at the logged steps."""
    done = np.array([m["done_frac"] for m in rep.metrics])
    return float(done.mean() * batch_size * (n_steps + 1))
