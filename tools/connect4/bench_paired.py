#!/usr/bin/env python3
"""Paired timing comparison with a Wilcoxon signed-rank test -- part 8.

The BitBully README compares the solver against Pascal Pons' reference solver
using a related paired design. That baseline is a separate C++ program and is
not installed here, so this script applies the design to a comparison it can
run end to end: ``mtdf`` against plain wide-window ``negamax`` on identical
positions. Unlike the historical benchmark driver, this script also alternates
measurement order.

The point is the method, not the contestants:

* the two solvers see the *same* positions -- the samples are paired;
* each is timed independently, with the transposition table reset first;
* their measurement order alternates, so neither driver always runs first;
* they must agree on the score, or the run aborts;
* significance is assessed with a **Wilcoxon signed-rank test**, which avoids
  assuming normally distributed paired differences.

Run from the repo root::

    tools/.venv/bin/python tools/connect4/bench_paired.py
"""

from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import time

import bitbully as bb
from scipy.stats import wilcoxon

DATA_DIR = pathlib.Path("tools/connect4/data")
CACHE = DATA_DIR / "paired.json"
CACHE_RAW = DATA_DIR / "paired_raw.json"


def time_one(agent, board, driver):
    agent.reset_transposition_table()
    start = time.perf_counter()
    score = getattr(agent, driver)(board)
    return score, time.perf_counter() - start


def compare(n_ply, n_repeats):
    agent = bb.BitBully()
    agent.reset_book()

    t_a, t_b = [], []
    for repeat in range(n_repeats):
        board, _ = bb.Board.random_board(n_ply=n_ply, forbid_direct_win=True)

        order = ("mtdf", "negamax") if repeat % 2 == 0 else ("negamax", "mtdf")
        measurements = {
            driver: time_one(agent, board, driver)
            for driver in order
        }
        score_a, elapsed_a = measurements["mtdf"]
        score_b, elapsed_b = measurements["negamax"]

        # Correctness gate: a faster wrong answer is not a result.
        assert score_a == score_b, f"disagreement at {n_ply} ply: {score_a} != {score_b}"

        t_a.append(elapsed_a)
        t_b.append(elapsed_b)

    mean_a, mean_b = statistics.fmean(t_a), statistics.fmean(t_b)
    # One-sided: is mtdf faster than negamax?
    stat, p = wilcoxon(t_a, t_b, alternative="less")

    summary = {
        "n_ply": n_ply,
        "n_repeats": n_repeats,
        "mtdf_mean_s": mean_a,
        "mtdf_std_s": statistics.stdev(t_a),
        "negamax_mean_s": mean_b,
        "negamax_std_s": statistics.stdev(t_b),
        "speedup": mean_b / mean_a,
        "p_value": float(p),
        "significant": bool(p < 0.05),
    }
    # The raw pairs as well, so the paired scatter can be drawn without
    # re-measuring (see make_paired_figure.py).
    raw = {"n_ply": n_ply, "mtdf_s": t_a, "negamax_s": t_b}
    return summary, raw


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="tiny smoke run")
    args = parser.parse_args()

    if args.quick:
        plan = [(18, 20), (20, 20)]
    else:
        plan = [(12, 40), (14, 80), (16, 150), (18, 250), (20, 400), (22, 600)]

    rows, raw_rows = [], []
    print(f"  {'ply':>4} {'repeats':>8} {'MTD(f) [s]':>22} {'negamax [s]':>22} "
          f"{'speed-up':>9} {'p-value':>10}  sig")
    for n_ply, n_repeats in plan:
        row, raw = compare(n_ply, n_repeats)
        rows.append(row)
        raw_rows.append(raw)
        print(
            f"  {row['n_ply']:>4} {row['n_repeats']:>8} "
            f"{row['mtdf_mean_s']:>10.5f} +/- {row['mtdf_std_s']:<8.5f} "
            f"{row['negamax_mean_s']:>10.5f} +/- {row['negamax_std_s']:<8.5f} "
            f"{row['speedup']:>8.2f}x {row['p_value']:>10.2e}  "
            f"{'*' if row['significant'] else ''}"
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(rows, indent=2) + "\n")
    CACHE_RAW.write_text(json.dumps(raw_rows) + "\n")
    print(f"\nwrote {CACHE} and {CACHE_RAW}")


if __name__ == "__main__":
    main()
