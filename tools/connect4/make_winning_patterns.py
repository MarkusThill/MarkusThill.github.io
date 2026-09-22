#!/usr/bin/env python3
"""The three winning patterns of part 9, drawn as board diagrams.

Part 9 describes three types of positions which are decided before they are
expanded: (1) the zugzwang case in which every playable cell lies directly
beneath an opponent threat, (2) a move which creates two immediate threats at
once, and (3) a move with two of the mover's own threats stacked directly on
top of it. This script renders one example of each, side by side.

None of the highlights are typed in by hand. For every panel the example
position is replayed with the real engine and the pattern is *asserted*:
``generateNonLosingMoves() == 0`` (and no immediate opponent threat) for the
zugzwang case, an empty reply set after the double-threat move for pattern 2,
and a firing ``doubleThreat()`` for pattern 3. The amber threat cells and the
traced four-in-a-row lines are then computed from the board masks.

Run from the repo root::

    tools/.venv/bin/python tools/connect4/make_winning_patterns.py
"""

from __future__ import annotations

import pathlib

import bitbully as bb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT_DIR = pathlib.Path("assets/img/2026-04-23-connect-4-final-considerations")

N_COLUMNS, N_ROWS, OFF = 7, 6, 9
MASK64 = (1 << 64) - 1

C_MOVER = "#4C78A8"  # the player to move (panel 1) / who just moved (2, 3)
C_OPP = "#D1495B"
C_MOVE = "#7FBF7B"  # the decisive move itself
C_THREAT = "#EDAE49"  # a winning cell
C_EMPTY = "#E9E9E9"
C_TEXT = "#333333"
C_TEXT_LIGHT = "#666666"

# The example positions, as move sequences from the empty board.
ZUGZWANG = [3, 5, 6, 6, 2, 2, 0, 5, 3, 6, 2, 0, 5, 0, 0, 6, 6, 3, 5, 2, 6, 2, 0, 0, 2, 5, 3, 1, 3, 1, 5, 3]
DOUBLE_THREAT_BEFORE = [3, 3, 4, 4]  # ... then the move into column 2
DOUBLE_THREAT_MOVE = 2
STACKED_BEFORE = [5, 4, 5, 2, 2, 2, 2, 0, 4, 6]  # ... then the move into column 3
STACKED_MOVE = 3

LEGAL_CELLS = sum(1 << (c * OFF + r) for c in range(N_COLUMNS) for r in range(N_ROWS))

# All 69 four-in-a-row lines as cell quadruples, for tracing.
LINES = (
    [[(c, r + i) for i in range(4)] for c in range(7) for r in range(3)]
    + [[(c + i, r) for i in range(4)] for c in range(4) for r in range(6)]
    + [[(c + i, r + i) for i in range(4)] for c in range(4) for r in range(3)]
    + [[(c + i, r + 3 - i) for i in range(4)] for c in range(4) for r in range(3)]
)


def bit(c, r):
    return 1 << (c * OFF + r)


def winning_positions(x):
    """Transcription of Board::winningPositions() (all directions)."""
    wins = (x << 1) & (x << 2) & (x << 3)
    for k in (OFF - 1, OFF, OFF + 1):
        t = (x << k) & (x << 2 * k)
        wins |= (t & (x << 3 * k)) | (t & (x >> k))
        t = (x >> k) & (x >> 2 * k)
        wins |= (t & (x << k)) | (t & (x >> 3 * k))
    return wins & LEGAL_CELLS & MASK64


def replay(moves):
    board = bb.Board()
    for c in moves:
        assert board.play(c)
    return board


def masks(board):
    all_t, active_t, _ = board.native.rawState()
    return all_t, active_t, (all_t ^ active_t) & MASK64


def threat_lines(stones, cell):
    """The four-in-a-row lines which `stones` completes at `cell`."""
    out = []
    for line in LINES:
        cells = [bit(c, r) for c, r in line]
        if bit(*cell) in cells and all(b == bit(*cell) or (stones & b) for b in cells):
            out.append(line)
    return out


def cells_of(mask):
    return [(c, r) for c in range(N_COLUMNS) for r in range(N_ROWS) if mask & bit(c, r)]


def build_panels():
    """Replay the three examples, assert each pattern, return draw specs."""
    panels = []

    # -- 1: zugzwang -- every playable cell lies under an opponent threat.
    b = replay(ZUGZWANG)
    core = b.native
    all_t, active_t, opp = masks(b)
    legal = core.legalMovesMask()
    opp_threats = winning_positions(opp)
    assert not core.hasWin()
    assert core.generateNonLosingMoves() == 0
    assert opp_threats & legal == 0  # no immediate threat: this is pure zugzwang
    assert legal & ~(opp_threats >> 1) == 0  # every landing sits under one
    # engine self-check for the transcription above
    assert bool(winning_positions(active_t) & legal) == core.canWin()
    hot = opp_threats & (legal << 1)  # the threats directly above the landings
    panels.append(
        {
            "title": "1 — zugzwang: every move lands\nunder an opponent threat",
            "mover": active_t,
            "opp": opp,
            "move_cell": None,
            "outline": cells_of(legal),
            "threats": cells_of(hot),
            "lines": [ln for cell in cells_of(hot) for ln in threat_lines(opp, cell)],
        }
    )

    # -- 2: one move creates two immediate threats.
    b = replay(DOUBLE_THREAT_BEFORE)
    assert b.native.doubleThreat(b.native.legalMovesMask()) == 0  # not the stacked kind
    after = replay(DOUBLE_THREAT_BEFORE + [DOUBLE_THREAT_MOVE])
    core = after.native
    all_t, active_t, mover = masks(after)  # the mover is now the *opponent* side
    legal = core.legalMovesMask()
    direct = winning_positions(mover) & legal
    assert bin(direct).count("1") == 2  # two immediate threats ...
    assert core.generateNonLosingMoves() == 0  # ... of which only one can be blocked
    move_cell = cells_of(bit(DOUBLE_THREAT_MOVE, after.native.getColumnHeight(DOUBLE_THREAT_MOVE) - 1))[0]
    panels.append(
        {
            "title": "2 — one move, two immediate\nthreats: only one can be blocked",
            "mover": mover & ~bit(*move_cell),
            "opp": active_t,
            "move_cell": move_cell,
            "outline": [],
            "threats": cells_of(direct),
            "lines": [ln for cell in cells_of(direct) for ln in threat_lines(mover, cell)],
        }
    )

    # -- 3: two stacked threats -- doubleThreat() fires without any search.
    b = replay(STACKED_BEFORE)
    core = b.native
    dt = core.doubleThreat(core.generateNonLosingMoves())
    assert dt == bit(STACKED_MOVE, 0)  # the engine finds exactly this move
    after = replay(STACKED_BEFORE + [STACKED_MOVE])
    all_t, active_t, mover = masks(after)
    stacked = winning_positions(mover) & ~all_t & (dt << 1 | dt << 2)
    assert stacked == (dt << 1) | (dt << 2)  # the two threats sit right on top
    panels.append(
        {
            "title": "3 — two stacked threats: blocking\nthe lower one opens the upper one",
            "mover": mover & ~dt,
            "opp": active_t,
            "move_cell": cells_of(dt)[0],
            "outline": [],
            "threats": cells_of(stacked),
            "lines": [ln for cell in cells_of(stacked) for ln in threat_lines(mover, cell)],
        }
    )
    return panels


def draw(panels):
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 4.6))

    for ax, p in zip(axes, panels):
        for c in range(N_COLUMNS):
            for r in range(N_ROWS):
                cell = (c, r)
                if p["move_cell"] == cell:
                    face = C_MOVE
                elif cell in p["threats"]:
                    face = C_THREAT
                elif p["mover"] & bit(c, r):
                    face = C_MOVER
                elif p["opp"] & bit(c, r):
                    face = C_OPP
                else:
                    face = C_EMPTY
                ax.add_patch(Rectangle((c + 0.04, r + 0.04), 0.92, 0.92, facecolor=face, edgecolor="none"))
                if cell in p["outline"]:
                    ax.add_patch(
                        Rectangle((c + 0.10, r + 0.10), 0.80, 0.80, facecolor="none", edgecolor=C_TEXT, lw=1.4, ls=(0, (3, 2)))
                    )
        for line in p["lines"]:
            xs = [c + 0.5 for c, _ in line]
            ys = [r + 0.5 for _, r in line]
            ax.plot(xs, ys, color=C_TEXT, lw=1.8, alpha=0.55, solid_capstyle="round", zorder=3)
        for c in range(N_COLUMNS):
            ax.text(c + 0.5, -0.32, "abcdefg"[c], ha="center", va="center", fontsize=8, color=C_TEXT_LIGHT)
        ax.set_title(p["title"], fontsize=9.5, color=C_TEXT)
        ax.set_xlim(-0.1, N_COLUMNS + 0.1)
        ax.set_ylim(-0.75, N_ROWS + 0.15)
        ax.set_aspect("equal")
        ax.axis("off")

    fig.text(
        0.5,
        0.045,
        "blue / red = the two players     green = the decisive move     amber = winning cell     "
        "dashed = the only playable cells",
        ha="center",
        va="bottom",
        fontsize=8.5,
        color=C_TEXT_LIGHT,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1.02))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "winning-patterns.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", pad_inches=0.10, facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    draw(build_panels())
