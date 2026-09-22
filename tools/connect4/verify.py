#!/usr/bin/env python3
"""Correctness checks -- measurement for part 8.

Four independent ways to catch a wrong answer, in increasing order of how much
they would embarrass the solver:

1. **Driver agreement.** ``mtdf``, ``negamax`` and ``null_window`` explore
   different parts of the tree and must return the same score.
2. **Mirror invariance.** A position and its mirror image are the same position
   as far as game theory is concerned.
3. **Score/distance consistency.** ``score_to_moves_left`` must fit both the
   number of empty cells and the parity implied by the score's sign.
4. **The external oracle.** The 8-ply opening book was computed by John Tromp in
   1994, independently of this code. Searching an 8-stone position *with the book
   disabled* and comparing against the book is the one check that can catch a bug
   shared by the whole engine.

Run from the repo root::

    tools/.venv/bin/python tools/connect4/verify.py
"""

from __future__ import annotations

import argparse
import json
import pathlib

import bitbully as bb
import bitbully_databases as bbd

DATA_DIR = pathlib.Path("tools/connect4/data")
CACHE = DATA_DIR / "verify.json"


def solve_fresh(agent, board, driver="mtdf"):
    """Solve without inheriting transposition entries from an earlier check."""
    agent.reset_transposition_table()
    return getattr(agent, driver)(board)


def to_row_major(board):
    """bitbully: arr[col][row], row 0 bottom. decoder: board[row][col], row 0 top."""
    arr = board.to_array()
    return [[int(arr[c][5 - r]) for c in range(7)] for r in range(6)]


def check_drivers(agent, boards):
    failures = []
    for board in boards:
        scores = {
            driver: solve_fresh(agent, board, driver)
            for driver in ("mtdf", "negamax", "null_window")
        }
        if len(set(scores.values())) != 1:
            failures.append({"uid": board.uid(), "scores": scores})
    return failures


def check_mirror(agent, boards):
    failures = []
    for board in boards:
        a = solve_fresh(agent, board)
        b = solve_fresh(agent, board.mirror())
        if a != b:
            failures.append({"uid": board.uid(), "score": a, "mirrored": b})
    return failures


def check_moves_left(agent, boards):
    failures = []
    for board in boards:
        score = solve_fresh(agent, board)
        left = agent.score_to_moves_left(score, board)
        board_left = board.moves_left()
        if score > 0:
            valid = 1 <= left <= board_left and left % 2 == 1
        elif score < 0:
            valid = 2 <= left <= board_left and left % 2 == 0
        else:
            valid = left == board_left
        if not valid:
            failures.append(
                {"uid": board.uid(), "score": score, "moves_left": left,
                 "board_moves_left": board_left}
            )
    return failures


def check_against_book(boards):
    """Search 8-stone positions with the book off; compare against Tromp's book.

    The book stores the outcome from the point of view of the player to move;
    BitBully's score carries the same sign convention, so only the signs are
    compared -- the 8-ply book has no distance information.
    """
    agent = bb.BitBully()
    agent.reset_book()  # the search must not consult the thing it is checked against
    db = bbd.BitBullyDatabases("8-ply")

    failures, compared = [], 0
    for board in boards:
        book_value = db.get_book_value(to_row_major(board))
        if book_value is None:
            continue
        searched = solve_fresh(agent, board)
        compared += 1
        if (searched > 0) - (searched < 0) != (book_value > 0) - (book_value < 0):
            failures.append(
                {"uid": board.uid(), "searched": searched, "book": book_value}
            )
    return failures, compared


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="tiny smoke run")
    args = parser.parse_args()

    n = 25 if args.quick else 300
    n_book = 25 if args.quick else 400

    agent = bb.BitBully()
    agent.reset_book()

    print(f"generating {n} random positions (16 stones) ...")
    boards = [
        bb.Board.random_board(n_ply=16, forbid_direct_win=True)[0] for _ in range(n)
    ]

    results = {}

    print("1. driver agreement ...")
    results["drivers"] = check_drivers(agent, boards)
    print(f"   {n - len(results['drivers'])}/{n} agree")

    print("2. mirror invariance ...")
    results["mirror"] = check_mirror(agent, boards)
    print(f"   {n - len(results['mirror'])}/{n} invariant")

    print("3. score -> moves-left range and parity ...")
    results["moves_left"] = check_moves_left(agent, boards)
    print(f"   {n - len(results['moves_left'])}/{n} consistent")

    print(f"4. against Tromp's 8-ply book ({n_book} positions, book disabled in search) ...")
    book_boards = [
        bb.Board.random_board(n_ply=8, forbid_direct_win=True)[0] for _ in range(n_book)
    ]
    book_failures, compared = check_against_book(book_boards)
    results["book"] = book_failures
    results["book_compared"] = compared
    print(f"   {compared - len(book_failures)}/{compared} agree")

    total_failures = sum(len(v) for k, v in results.items() if isinstance(v, list))
    summary = {
        "n_positions": n,
        "n_book_positions": compared,
        "failures": {k: len(v) for k, v in results.items() if isinstance(v, list)},
        "total_failures": total_failures,
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps({"summary": summary, "detail": results}, indent=2) + "\n")

    print(f"\ntotal failures: {total_failures}")
    print(f"wrote {CACHE}")
    raise SystemExit(1 if total_failures else 0)


if __name__ == "__main__":
    main()
