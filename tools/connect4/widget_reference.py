#!/usr/bin/env python3
"""Emit reference board states from BitBully for the widget cross-check.

Prints JSON on stdout; consumed by `tools/connect4/check_widget.mjs`, which
extracts the operations from `assets/js/connect4-core.js` and compares.
"""

from __future__ import annotations

import json
import random

import bitbully as bb


def snapshot(board, want_huffman=False):
    core = board.native
    all_tokens, active_tokens, moves_left = core.rawState()
    entry = {
        "all": str(all_tokens),
        "active": str(active_tokens),
        "legal": str(core.legalMovesMask()),
        "uid": str(core.uid()),
        "hash": str(core.hash()),
        "hasWin": bool(core.hasWin()),
        "movesLeft": moves_left,
        "nonLosing": str(core.generateNonLosingMoves()),
        "doubleThreat": str(core.doubleThreat(core.legalMovesMask())),
        "ordered": core.legalMoves(False, True),
    }
    if want_huffman:
        entry["huffman"] = board.to_huffman()
    return entry


def main() -> None:
    random.seed(7)
    out = []

    # Random play-outs: exercises the general board operations.
    for _ in range(300):
        board = bb.Board()
        applied = []
        for _ in range(random.randint(0, 20)):
            col = random.randint(0, 6)
            if board.is_game_over() or not board.is_legal_move(col):
                continue
            board.play(col)
            applied.append(col)
        entry = snapshot(board)
        entry["moves"] = applied
        out.append(entry)

    # Positions with exactly 8 and 12 tokens: the Huffman encoding is only
    # defined there, so those are checked separately.
    for n_ply in (8, 12):
        for _ in range(100):
            board, moves = bb.Board.random_board(n_ply=n_ply, forbid_direct_win=True)
            entry = snapshot(board, want_huffman=True)
            entry["moves"] = list(moves)
            out.append(entry)

    # Endgame positions with the game-theoretic value: the JS solver of the
    # part-7 widget (connect4-search.js) must return the same score as the
    # real engine, and the same number of plies until the game ends.
    agent = bb.BitBully()
    agent.reset_book()
    for n_ply in (16, 18, 20, 22, 24):
        for _ in range(8):
            board, moves = bb.Board.random_board(n_ply=n_ply, forbid_direct_win=True)
            agent.reset_transposition_table()
            score = agent.mtdf(board)
            entry = snapshot(board)
            entry["moves"] = list(moves)
            entry["score"] = score
            entry["endsIn"] = agent.score_to_moves_left(score, board)
            out.append(entry)

    print(json.dumps(out))


if __name__ == "__main__":
    main()
