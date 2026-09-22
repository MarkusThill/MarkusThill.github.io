#!/usr/bin/env python3
"""Opening-book statistics -- measurement for part 6.

Reads the three books shipped in ``bitbully-databases`` and reports, for each:

* the file size and the bytes actually spent per stored position,
* what a byte-aligned 2 x 42-bit dump of the same positions would have cost,
* the win / loss / draw distribution over the stored entries,
* and, for the book with distances, the spread of distance-to-end values.

Also times a solve with and without the book, which is the whole reason the
books exist.

Run from the repo root::

    tools/.venv/bin/python tools/connect4/book_stats.py
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import time

import bitbully as bb
import bitbully_databases as bbd

DATA_DIR = pathlib.Path("tools/connect4/data")
CACHE = DATA_DIR / "book_stats.json"

BOOKS = ("8-ply", "12-ply", "12-ply-dist")


def book_summary(name):
    db = bbd.BitBullyDatabases(name)
    path = pathlib.Path(bbd.BitBullyDatabases.get_database_path(name))
    size_bytes = path.stat().st_size
    n_entries = db.get_book_size()

    n_stones = 8 if name == "8-ply" else 12
    # Two 42-bit boards need 11 byte-aligned bytes. Their four padding bits can
    # also hold an outcome; only the distance book needs a separate value byte.
    naive_bytes = n_entries * (12 if db.with_distances else 11)

    return {
        "book": name,
        "file": path.name,
        "entries": n_entries,
        "stones": n_stones,
        "file_bytes": size_bytes,
        "bytes_per_entry": size_bytes / n_entries,
        "naive_bytes": naive_bytes,
        "compression": naive_bytes / size_bytes,
        "with_distances": db.with_distances,
    }


def to_row_major(board):
    """bitbully gives arr[col][row] with row 0 at the bottom; the pure-Python
    decoder in bitbully-databases wants board[row][col] with row 0 at the top."""
    arr = board.to_array()
    return [[int(arr[c][5 - r]) for c in range(7)] for r in range(6)]


def value_distribution(name, sample_positions):
    """Win / loss / draw split over a sample of book positions.

    Note the encoding trick this exposes: the books *without* distances do not
    store player-1 wins at all. A miss is the answer "player 1 wins", so those
    books only pay for the minority outcomes.
    """
    db = bbd.BitBullyDatabases(name)
    counts = collections.Counter()
    distances = []

    for board in sample_positions:
        grid = to_row_major(board)
        value = db.get_book_value(grid)
        if value is None:
            counts["not in book"] += 1
            continue
        if value > 0:
            counts["win"] += 1
        elif value < 0:
            counts["loss"] += 1
        else:
            counts["draw"] += 1
        if db.with_distances and value != 0:
            distances.append(100 - abs(value))

    return {
        "book": name,
        "sampled": len(sample_positions),
        "counts": dict(counts),
        "moves_to_end_min": min(distances) if distances else None,
        "moves_to_end_max": max(distances) if distances else None,
    }


def timing(n_positions, n_ply):
    """Solve the same positions with and without the opening book."""
    boards = [
        bb.Board.random_board(n_ply=n_ply, forbid_direct_win=True)[0]
        for _ in range(n_positions)
    ]

    rows = {}
    for label, use_book in (("with book", True), ("without book", False)):
        agent = bb.BitBully()
        if not use_book:
            agent.reset_book()

        total_time, total_nodes = 0.0, 0
        for board in boards:
            agent.reset_transposition_table()
            agent.reset_node_counter()
            start = time.perf_counter()
            agent.mtdf(board)
            total_time += time.perf_counter() - start
            total_nodes += agent.get_node_counter()

        rows[label] = {
            "seconds_per_position": total_time / n_positions,
            "nodes_per_position": total_nodes / n_positions,
        }

    rows["speedup"] = (
        rows["without book"]["seconds_per_position"] / rows["with book"]["seconds_per_position"]
    )
    rows["n_ply"] = n_ply
    rows["n_positions"] = n_positions
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="tiny smoke run")
    args = parser.parse_args()

    n_sample = 200 if args.quick else 3000
    n_timing = 5 if args.quick else 40

    print("book sizes and encoding cost")
    summaries = [book_summary(name) for name in BOOKS]
    for s in summaries:
        print(
            f"  {s['book']:<12} {s['entries']:>10,} entries "
            f"{s['file_bytes'] / 1e6:>8.2f} MB "
            f"{s['bytes_per_entry']:>5.2f} B/entry  "
            f"{s['compression']:>4.1f}x vs naive"
        )

    print(f"\nvalue distribution over {n_sample} random book positions")
    distributions = []
    for name in BOOKS:
        n_stones = 8 if name == "8-ply" else 12
        sample = [
            bb.Board.random_board(n_ply=n_stones, forbid_direct_win=True)[0]
            for _ in range(n_sample)
        ]
        d = value_distribution(name, sample)
        distributions.append(d)
        print(f"  {name:<12} {d['counts']}")

    print(f"\nsolve time with vs. without the opening book ({n_timing} positions, 10 stones)")
    times = timing(n_timing, n_ply=10)
    for label in ("with book", "without book"):
        print(
            f"  {label:<14}{times[label]['seconds_per_position'] * 1e3:>9.2f} ms  "
            f"{times[label]['nodes_per_position']:>12,.0f} nodes"
        )
    print(f"  speed-up      {times['speedup']:>9.1f}x")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(
        json.dumps(
            {"books": summaries, "distributions": distributions, "timing": times}, indent=2
        )
        + "\n"
    )
    print(f"\nwrote {CACHE}")


if __name__ == "__main__":
    main()
