#!/usr/bin/env python3
"""MTD(f) vs. null-window vs. plain negamax -- measurement for part 7.

The three drivers sit on top of the same recursive search and must return the
same game-theoretic score for every position; only the sequence of alpha-beta
windows they use differs. This script checks that they agree and records how
many nodes and how much wall clock each one needs.

Opening books are disabled throughout -- with a book loaded, every position at
or below 12 stones is answered by a lookup and there is nothing to compare.

Run from the repo root::

    tools/.venv/bin/python tools/connect4/bench_drivers.py
"""

from __future__ import annotations

import argparse
import json
import pathlib
import time

import bitbully as bb

DATA_DIR = pathlib.Path("tools/connect4/data")
CACHE = DATA_DIR / "drivers.json"

DRIVERS = ("mtdf", "negamax", "null_window")


def run_driver(agent, board, driver):
    agent.reset_transposition_table()
    agent.reset_node_counter()
    start = time.perf_counter()
    score = getattr(agent, driver)(board)
    elapsed = time.perf_counter() - start
    return score, agent.get_node_counter(), elapsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="tiny smoke run")
    args = parser.parse_args()

    if args.quick:
        plies, n_positions = [18, 20], 5
    else:
        plies, n_positions = [12, 14, 16, 18, 20, 22], 30

    agent = bb.BitBully()
    agent.reset_book()

    rows = []
    for n_ply in plies:
        boards = [
            bb.Board.random_board(n_ply=n_ply, forbid_direct_win=True)[0]
            for _ in range(n_positions)
        ]

        totals = {d: {"nodes": 0, "seconds": 0.0} for d in DRIVERS}
        for board in boards:
            reference = None
            for driver in DRIVERS:
                score, nodes, elapsed = run_driver(agent, board, driver)
                totals[driver]["nodes"] += nodes
                totals[driver]["seconds"] += elapsed
                if reference is None:
                    reference = score
                else:
                    assert score == reference, (
                        f"{driver} disagrees at {n_ply} ply: {score} != {reference}"
                    )

        row = {"n_ply": n_ply, "n_positions": n_positions}
        for driver in DRIVERS:
            row[driver] = {
                "nodes_per_position": totals[driver]["nodes"] / n_positions,
                "ms_per_position": totals[driver]["seconds"] / n_positions * 1e3,
            }
        rows.append(row)

        print(
            f"  {n_ply:>2} ply | "
            + " | ".join(
                f"{d}: {row[d]['nodes_per_position']:>10,.0f} nodes "
                f"{row[d]['ms_per_position']:>7.2f} ms"
                for d in DRIVERS
            )
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(rows, indent=2) + "\n")
    print(f"\nwrote {CACHE}")


if __name__ == "__main__":
    main()
