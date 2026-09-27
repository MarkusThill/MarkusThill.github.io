"""
Figures for the side post "Counting the Realisable States of an N-Tuple".

Run with a Python environment that has PyTorch and techdays26 installed (the per-tuple figure reads the ten
final checkpoints):

    python tools/connect4_rl/make_realisable_states_figures.py \
        --checkpoints 'tools/connect4_rl/checkpoints/L_repeat_*_step_25000.pt' \
        --out assets/img/2026-08-06-counting-realisable-ntuple-states --numbers tools/connect4_rl/data/s1_numbers.json
"""

from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

import realisable_states as rs

# Board style of the search series (tools/connect4/make_winning_patterns.py), with the game colours of
# the reinforcement-learning series.
C_YELLOW, C_RED, C_REACH, C_EMPTY = "#F2C230", "#D1495B", "#7FBF7B", "#E9E9E9"
C_TEXT, C_TEXT_LIGHT, C_WRONG = "#333333", "#666666", "#D1495B"
BLUE, ORANGE, GRID, AXIS = "#2a78d6", "#eb6834", "#e1e0d9", "#c3c2b7"
N_COLUMNS, N_ROWS = 7, 6

EXAMPLE = 0  # tuple 0 of the agent: a1, b1-b2, c1-c3, d2 and d4

# Four-in-a-row lines as cell quadruples.
LINES = (
    [[(c, r + i) for i in range(4)] for c in range(7) for r in range(3)]
    + [[(c + i, r) for i in range(4)] for c in range(4) for r in range(6)]
    + [[(c + i, r + i) for i in range(4)] for c in range(4) for r in range(3)]
    + [[(c + i, r + 3 - i) for i in range(4)] for c in range(4) for r in range(3)]
)

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": AXIS, "axes.labelcolor": "#52514e",
    "xtick.color": "#898781", "ytick.color": "#898781", "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": "white", "savefig.facecolor": "white", "savefig.dpi": 160, "legend.frameon": False,
})


def draw_tuple_state(ax, tuple_cells, codes, title, wrong=()):
    """The board with the tuple's cells coloured by their codes; other cells light and unlabelled."""
    colour = {rs.EMPTY: "white", rs.YELLOW: C_YELLOW, rs.RED: C_RED, rs.REACHABLE: C_REACH}
    for c in range(N_COLUMNS):
        for r in range(N_ROWS):
            ax.add_patch(Rectangle((c + 0.04, r + 0.04), 0.92, 0.92, facecolor=C_EMPTY, edgecolor="none"))
    for (c, r), code in zip(tuple_cells, codes):
        ax.add_patch(Rectangle((c + 0.04, r + 0.04), 0.92, 0.92, facecolor=colour[code], edgecolor="none"))
        ax.add_patch(Rectangle((c + 0.10, r + 0.10), 0.80, 0.80, facecolor="none", edgecolor=C_TEXT, lw=1.3,
                               ls=(0, (3, 2))))
        if (c, r) in wrong:
            ax.plot([c + 0.2, c + 0.8], [r + 0.2, r + 0.8], color=C_WRONG, lw=2.2)
            ax.plot([c + 0.2, c + 0.8], [r + 0.8, r + 0.2], color=C_WRONG, lw=2.2)
    for c in range(N_COLUMNS):
        ax.text(c + 0.5, -0.32, "abcdefg"[c], ha="center", va="center", fontsize=8, color=C_TEXT_LIGHT)
    ax.set_title(title, fontsize=9.5, color=C_TEXT)
    ax.set_xlim(-0.1, N_COLUMNS + 0.1)
    ax.set_ylim(-0.75, N_ROWS + 0.15)
    ax.set_aspect("equal")
    ax.axis("off")


def fig_patterns(tuple_bits, out):
    tc = rs.cells(tuple_bits)
    pos = {cell: i for i, cell in enumerate(tc)}

    def codes(assign):
        return [assign.get(cell, rs.EMPTY) for cell in tc]

    Y, R, A = rs.YELLOW, rs.RED, rs.REACHABLE
    ok = {(0, 0): Y, (1, 0): R, (1, 1): A, (2, 0): Y, (2, 1): R, (2, 2): Y, (3, 1): A}
    floating = {**ok, (2, 0): A, (2, 1): rs.EMPTY, (2, 2): Y}  # stone above an empty cell
    two_reach = {**ok, (3, 1): A, (3, 3): A}  # two landing cells in one column
    empty_bottom = {**ok, (0, 0): rs.EMPTY}  # an empty bottom cell is always reachable
    panels = [(ok, "realisable", ()), (floating, "stone above an empty cell", ((2, 2),)),
              (two_reach, "two landing cells in one column", ((3, 3),)),
              (empty_bottom, "empty but unreachable bottom cell", ((0, 0),))]
    fig, axes = plt.subplots(1, 4, figsize=(12.6, 3.7))
    for ax, (assign, title, wrong) in zip(axes, panels):
        draw_tuple_state(ax, tc, codes(assign), title, wrong)
    fig.text(0.5, 0.03, "dashed = the eight cells of the tuple     yellow / red = stones     green = empty and "
             "reachable     white = empty, not reachable     cross = the cell that makes the state impossible",
             ha="center", va="bottom", fontsize=8.5, color=C_TEXT_LIGHT)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "tuple-states.png", bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    print("wrote", out / "tuple-states.png")


def terminal_mask(tuple_bits) -> np.ndarray:
    """For every realisable state (rank order): does it contain a complete four of one colour inside the tuple?

    Such states belong to finished games, which are never trained; their weights must stay zero.
    """
    index = np.array(rs.Ranking(tuple_bits).indices())
    tc = rs.cells(tuple_bits)
    pos = {cell: i for i, cell in enumerate(tc)}
    codes = np.stack([(index >> (2 * i)) & 3 for i in range(len(tc))], axis=1)
    mask = np.zeros(len(index), dtype=bool)
    for line in LINES:
        if all(cell in pos for cell in line):
            cols = [pos[cell] for cell in line]
            for colour in (rs.YELLOW, rs.RED):
                mask |= np.all(codes[:, cols] == colour, axis=1)
    return mask


def fig_per_tuple(tuples, checkpoints, out, numbers):
    import torch

    counts = np.array([rs.count_recursive(t) for t in tuples])
    orders = [np.array(rs.Ranking(t).indices()) for t in tuples]
    terminal = [terminal_mask(t) for t in tuples]
    nonterminal = np.array([int((~t).sum()) for t in terminal])
    visited = []  # [checkpoints, tuples]: share of non-terminal realisable entries (both players) that are non-zero
    outside = on_terminal = 0
    for ck in checkpoints:
        W = torch.load(ck, map_location="cpu", weights_only=False)["state_dict"]["W"].numpy()
        row = []
        for m, (o, term) in enumerate(zip(orders, terminal)):
            nz = W[:, m, o] != 0
            outside += int((W[:, m] != 0).sum() - nz.sum())
            on_terminal += int(nz[:, term].sum())
            row.append(nz[:, ~term].sum() / (2 * (~term).sum()))
        visited.append(row)
    visited = np.array(visited)
    pooled = (visited * nonterminal).sum(axis=1) / nonterminal.sum()
    numbers.update({"checkpoints": len(checkpoints), "nonzero_outside_realisable": outside,
                    "nonzero_on_four_in_a_row_states": on_terminal,
                    "nonterminal_realisable_per_player": int(nonterminal.sum()),
                    "four_in_a_row_states_per_player": int(counts.sum() - nonterminal.sum()),
                    "visited_nonterminal_pooled_min": float(pooled.min()), "visited_nonterminal_pooled_max": float(pooled.max()),
                    "visited_per_tuple_min": float(visited.mean(0).min()),
                    "tuples_fully_visited": int((visited.mean(0) >= 1 - 1e-12).sum()),
                    "tuples_below_99pct": int((visited.mean(0) < 0.99).sum()),
                    "counts_min": int(counts.min()), "counts_max": int(counts.max()),
                    "counts_median": float(np.median(counts))})
    order = np.argsort(counts)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 3.9))
    ax1.bar(np.arange(len(counts)), counts[order] / 4**8, color=BLUE, width=1.0, edgecolor="white", lw=0.3)
    ax1.axhline(counts.sum() / (len(counts) * 4**8), color=C_TEXT, lw=1)
    ax1.text(4, counts.sum() / (len(counts) * 4**8) * 1.04, f"all 200 tuples: {counts.sum() / (len(counts) * 4**8):.1%}",
             fontsize=8.5, color=C_TEXT, va="bottom")
    ax1.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax1.set_xlabel("tuples, sorted by their number of realisable states")
    ax1.set_ylabel("realisable share of the 65,536 entries")
    ax1.set_title("what gravity allows", loc="left", fontsize=11)
    ax1.grid(axis="y", color=GRID, lw=0.6)
    m = visited.mean(0)[order]
    ax2.scatter(np.arange(len(m)), m, s=10, color=ORANGE, lw=0)
    ax2.set_ylim(min(0.93, m.min() - 0.005), 1.002)
    ax2.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax2.set_xlabel("tuples, same order")
    ax2.set_ylabel("non-terminal states visited")
    ax2.set_title("what training visits (mean of ten agents)", loc="left", fontsize=11)
    ax2.grid(axis="y", color=GRID, lw=0.6)
    fig.tight_layout()
    fig.savefig(out / "realisable-per-tuple.png", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print("wrote", out / "realisable-per-tuple.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoints", required=True, help="glob of the final checkpoints")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--numbers", type=Path)
    args = parser.parse_args()
    import torch

    checkpoints = sorted(glob.glob(args.checkpoints))
    tuples = [list(map(int, t)) for t in torch.load(checkpoints[0], map_location="cpu", weights_only=False)["n_tuple_list"]]
    numbers = {"example_tuple": EXAMPLE, "example_cells": ["abcdefg"[c] + str(r + 1) for c, r in rs.cells(tuples[EXAMPLE])],
               "example_column_counts": [rs.count_column([r for c2, r in rs.cells(tuples[EXAMPLE]) if c2 == c])
                                         for c in sorted({c for c, _ in rs.cells(tuples[EXAMPLE])})],
               "example_count": rs.count_recursive(tuples[EXAMPLE]),
               "total_realisable_per_player": int(sum(rs.count_recursive(t) for t in tuples))}
    fig_patterns(tuples[EXAMPLE], args.out)
    fig_per_tuple(tuples, checkpoints, args.out, numbers)
    text = json.dumps(numbers, indent=1)
    if args.numbers:
        args.numbers.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
