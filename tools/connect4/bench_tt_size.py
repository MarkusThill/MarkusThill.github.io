#!/usr/bin/env python3
"""Transposition-table size sweep -- measurement for part 5.

BitBully's table size is a compile-time constant (``TranspositionTable::LOG_2_SIZE``),
so it cannot be swept from Python. What *can* be measured from the shipped
wheel is the other half of the story: how much work the table saves in the first
place, and how the mirror-symmetry lookup contributes.

Two experiments:

1. **Nodes vs. plies.** Solve random positions at a range of ply counts with
   ``mtdf`` and record the visited-node counter. This shows the combined effect
   of everything in the engine on that sampled workload.
2. **Symmetry.** Count how many distinct positions at each ply collapse onto a
   single representative once mirror images are identified -- the factor a
   mirror-aware table (and the opening books of part 6) actually saves.

Run from the repo root::

    tools/.venv/bin/python tools/connect4/bench_tt_size.py
"""

from __future__ import annotations

import argparse
import json
import pathlib
import time

import bitbully as bb

DATA_DIR = pathlib.Path("tools/connect4/data")
CACHE = DATA_DIR / "tt_size.json"


def measure_nodes(plies, n_positions):
    """Solve random positions per ply and record nodes + wall clock."""
    agent = bb.BitBully()
    agent.reset_book()  # books would answer instantly and hide the search

    rows = []
    for n_ply in plies:
        boards = [
            bb.Board.random_board(n_ply=n_ply, forbid_direct_win=True)[0]
            for _ in range(n_positions)
        ]

        total_nodes, total_time = 0, 0.0
        for board in boards:
            agent.reset_transposition_table()
            agent.reset_node_counter()
            start = time.perf_counter()
            agent.mtdf(board)
            total_time += time.perf_counter() - start
            total_nodes += agent.get_node_counter()

        rows.append(
            {
                "n_ply": n_ply,
                "n_positions": n_positions,
                "nodes_per_position": total_nodes / n_positions,
                "seconds_per_position": total_time / n_positions,
            }
        )
        print(
            f"  {n_ply:>2} ply: {rows[-1]['nodes_per_position']:>12,.0f} nodes  "
            f"{rows[-1]['seconds_per_position'] * 1e3:>9.2f} ms"
        )
    return rows


def measure_symmetry(max_ply):
    """How many positions collapse once mirror images are identified?"""
    empty = bb.Board()
    rows = []
    for n_ply in range(1, max_ply + 1):
        positions = empty.all_positions(n_ply, True)
        uids = {p.uid() for p in positions}

        # Keep one representative per mirror pair.
        representatives = set()
        for p in positions:
            representatives.add(min(p.uid(), p.mirror().uid()))

        rows.append(
            {
                "n_ply": n_ply,
                "positions": len(uids),
                "after_mirror_dedup": len(representatives),
                "saving": 1 - len(representatives) / len(uids),
            }
        )
        print(
            f"  {n_ply:>2} ply: {len(uids):>10,} -> {len(representatives):>10,}"
            f"  ({rows[-1]['saving'] * 100:>4.1f}% saved)"
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="tiny smoke run")
    args = parser.parse_args()

    if args.quick:
        plies, n_positions, max_sym_ply = [16, 18], 5, 6
    else:
        plies, n_positions, max_sym_ply = [10, 12, 14, 16, 18, 20], 40, 8

    print("solving random positions (opening book disabled) ...")
    nodes = measure_nodes(plies, n_positions)

    print("\ncounting positions and mirror-symmetric duplicates ...")
    symmetry = measure_symmetry(max_sym_ply)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps({"nodes": nodes, "symmetry": symmetry}, indent=2) + "\n")
    print(f"\nwrote {CACHE}")


if __name__ == "__main__":
    main()
