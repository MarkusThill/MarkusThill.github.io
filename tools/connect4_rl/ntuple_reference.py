"""
Reference data for the in-browser n-tuple agent: positions with the scores and the chosen move of
techdays26's `TDConnect4AgentTorch`.

The positions come from games of the agent against itself in which a fraction of the moves is random,
so that they resemble real games but still vary. For every position before the end of a game, the
script records the raw bit boards, the agent's integer scores per column (`score_all_moves`), its move
(`best_move`) and the unrounded network value of every non-tactical move, which shows how close a score
is to the next integer.

Run with a Python environment that has PyTorch and techdays26 installed:
    python tools/connect4_rl/ntuple_reference.py <checkpoint.pt> <out.json> --games 300
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

import torch
from bitbully import Board

from techdays26.td_agent import TDConnect4AgentTorch
from techdays26.torch_board import BoardBatch


def raw_values(agent: TDConnect4AgentTorch, board: Board) -> dict[int, float]:
    """Network value (Yellow's view) of the afterstate of every legal column."""
    all_tokens, active_tokens, moves_left = board._board.rawState()
    batch = BoardBatch(
        all_tokens=torch.full((7,), all_tokens, dtype=torch.int64),
        active_tokens=torch.full((7,), active_tokens, dtype=torch.int64),
        moves_left=torch.full((7,), moves_left, dtype=torch.int64),
    )
    legal = batch.play_columns(torch.arange(7, dtype=torch.int64))
    with torch.no_grad():
        values = agent._eval.forward(batch)
    return {c: float(values[c]) for c in range(7) if legal[c]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--games", type=int, default=300)
    parser.add_argument("--random-move-prob", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    agent = TDConnect4AgentTorch(model_path=str(args.checkpoint))
    positions = []
    for _ in range(args.games):
        board = Board()
        while not board.is_game_over():
            all_tokens, active_tokens, moves_left = board._board.rawState()
            scores = agent.score_all_moves(board)
            best = agent.best_move(board)
            positions.append({
                "all": str(all_tokens), "active": str(active_tokens), "movesLeft": int(moves_left),
                "scores": {str(c): int(s) for c, s in scores.items()}, "best": int(best),
                "values": {str(c): v for c, v in raw_values(agent, board).items()},
            })
            move = rng.choice(board.legal_moves()) if rng.random() < args.random_move_prob else best
            board.play(move)
    args.out.write_text(json.dumps({"checkpoint": str(args.checkpoint), "positions": positions}))
    print(f"{len(positions)} positions from {args.games} games -> {args.out}")


if __name__ == "__main__":
    main()
