"""
Select the strongest of the trained Connect-4 agents with a larger tournament, then evaluate the
selected agent once more on fresh games (so that the selection does not inflate its numbers).

Self-contained: needs only techdays26 (with the `lab2` extra) and the run folder with the ten
`step_25000_snapshot.pt` files. The opponents and the arena setup are those of the training notebook
`lab2/1_train_ntuple_net.ipynb`; only the number of games and the seeds differ.

Colab, after `pip install -e techdays26[lab2]` and mounting Google Drive:

    python select_strongest.py --run /content/drive/MyDrive/models/exp_L_batch_fast_tau_20260925_22-36 \
        --games 200 --out selection.json

Ranking criterion: mean score (W - L) / N of the agent over all conditions against search opponents,
i.e. every BitBully opponent from both sides, including the epsilon-weakened full-strength variants.
Each condition has the same weight.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from pathlib import Path

from bitbully import BitBully

from techdays26 import bitbully_arena as ba
from techdays26.td_agent import TDConnect4AgentTorch

AGENT = "ntuple"
SELECTION_SEED = 20_260_927
FRESH_SEED = 90_210


def make_opponents() -> dict[str, BitBully]:
    """The BitBully opponents of the training notebook's evaluation."""
    opponents = {}
    for depth in (1, 2, 4, 8):
        opponents[f"bitbully-{depth}ply"] = BitBully(opening_book=None, tie_break="random", max_depth=depth)
    for depth in (8, 10):
        opponents[f"bitbully-{depth}-ply-book8ply"] = BitBully(opening_book="8-ply", tie_break="random", max_depth=depth)
    opponents["bitbully-16ply-book12ply"] = BitBully(opening_book="12-ply-dist", tie_break="random", max_depth=16)
    opponents["bitbully-full-strength"] = BitBully(opening_book="12-ply-dist", tie_break="random")
    return opponents


def evaluate(model_path: str, opponents: dict[str, BitBully], n_games: int, seed: int, n_workers: int):
    """Round-robin of the agent against all opponents, both sides, as in the training notebook."""
    logger = logging.getLogger("bitbully.arena")
    logger.setLevel(logging.WARNING)
    agent_specs = [
        ba.AgentSpec(agent_id=k, agent=v, colors=(ba.Color.YELLOW, ba.Color.RED),
                     epsilons=(0.00, 0.1, 0.2, 0.3) if "full-strength" in k else (0.00,))
        for k, v in opponents.items()
    ]
    matchups = (
        [ba.Matchup(yellow_id=k, red_id=AGENT) for k in opponents]
        + [ba.Matchup(yellow_id=AGENT, red_id=k) for k in opponents]
        + [ba.Matchup(yellow_id=AGENT, red_id="random"), ba.Matchup(yellow_id="random", red_id=AGENT)]
    )
    agent_factory = None
    if n_workers > 1:
        agent_factory = {
            k: (BitBully, {"opening_book": v.opening_book_type, "tie_break": v.tie_break, "max_depth": v.max_depth})
            for k, v in opponents.items()
        }
        agent_factory["random"] = (ba.RandomAgent, {})
        agent_factory[AGENT] = (TDConnect4AgentTorch, {"model_path": model_path})
    cfg = ba.ArenaConfig(
        agents=(
            *agent_specs,
            ba.AgentSpec(agent_id="random", agent=ba.RandomAgent(), colors=(ba.Color.YELLOW, ba.Color.RED),
                         epsilons=(0.00,)),
            ba.AgentSpec(agent_id=AGENT, agent=TDConnect4AgentTorch(model_path=model_path),
                         colors=(ba.Color.YELLOW, ba.Color.RED), epsilons=(0.00,)),
        ),
        n_games=n_games,
        time_control=ba.TimeControl(per_move_timeout_s=4.0, per_game_budget_s=45.0),
        matchups=matchups,
        seed=seed,
        use_tqdm=True,
        logger=logger,
        n_workers=n_workers,
        agent_factory=agent_factory,
    )
    return ba.BitBullyArena().run(cfg)


def agent_rows(result) -> list[dict]:
    """Aggregates from the agent's point of view: side, opponent, opponent epsilon, W/D/L."""
    rows = []
    for r in result.aggregates:
        if r.agent_yellow == AGENT:
            side, opp, eps, w, l = "first", r.agent_red, r.epsilon_red, r.yellow_wins, r.red_wins
        elif r.agent_red == AGENT:
            side, opp, eps, w, l = "second", r.agent_yellow, r.epsilon_yellow, r.red_wins, r.yellow_wins
        else:
            continue
        rows.append({"side": side, "opponent": opp, "opponent_eps": float(eps), "wins": int(w),
                     "draws": int(r.draws), "losses": int(l), "games": int(r.games)})
    return rows


def criterion(rows: list[dict]) -> float:
    """Mean score over all conditions against search opponents (random play excluded)."""
    scores = [(r["wins"] - r["losses"]) / r["games"] for r in rows if r["opponent"] != "random"]
    return sum(scores) / len(scores)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True, help="run folder with repeat_*/step_25000_snapshot.pt")
    parser.add_argument("--games", type=int, default=200, help="games per opponent, side and epsilon")
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 1) - 1))
    parser.add_argument("--out", type=Path, default=Path("selection.json"))
    args = parser.parse_args()

    checkpoints = sorted(args.run.glob("repeat_*/step_25000_snapshot.pt"),
                         key=lambda p: int(p.parent.name.split("_")[1]))
    opponents = make_opponents()
    report = {"run": str(args.run), "games": args.games, "selection_seed": SELECTION_SEED,
              "fresh_seed": FRESH_SEED, "criterion": "mean score over all search-opponent conditions",
              "candidates": []}
    for ckpt in checkpoints:
        t0 = time.perf_counter()
        rows = agent_rows(evaluate(str(ckpt), opponents, args.games, SELECTION_SEED, args.workers))
        report["candidates"].append({"checkpoint": str(ckpt), "criterion": criterion(rows), "rows": rows,
                                     "seconds": time.perf_counter() - t0})
        print(f"{ckpt.parent.name}: criterion {report['candidates'][-1]['criterion']:.4f}")
        args.out.write_text(json.dumps(report, indent=1))  # keep partial results if the runtime stops

    best = max(report["candidates"], key=lambda c: c["criterion"])
    print(f"strongest: {best['checkpoint']} ({best['criterion']:.4f}); evaluating on fresh games ...")
    rows = agent_rows(evaluate(best["checkpoint"], opponents, args.games, FRESH_SEED, args.workers))
    report["selected"] = {"checkpoint": best["checkpoint"], "fresh_criterion": criterion(rows), "fresh_rows": rows}
    args.out.write_text(json.dumps(report, indent=1))
    print(f"fresh games: criterion {criterion(rows):.4f}; wrote {args.out}")


if __name__ == "__main__":
    main()
