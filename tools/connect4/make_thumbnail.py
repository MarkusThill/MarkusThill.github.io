#!/usr/bin/env python3
"""Thumbnail for part 3 of the Connect-4 series.

Shows what the post is about in one image: a Connect-4 position, and underneath
the two 64-bit words it is actually stored in, drawn in the 9-bits-per-column
layout with the guard bits greyed out. The hex values are computed with
BitBully, so the picture is not a mock-up.

The blog listing renders thumbnails with ``object-fit: cover`` inside a narrow
``col-sm-3`` column (see ``_pages/blog.md``), which crops the left and right
edges of anything wide. The canvas is therefore square and the composition is
centred, so that a horizontal crop removes only margin.

Run from the repo root::

    tools/.venv/bin/python tools/connect4/make_thumbnail.py
"""

from __future__ import annotations

import pathlib

import bitbully as bb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrow, FancyBboxPatch, Rectangle

OUT = pathlib.Path("assets/img/2026-01-29-connect-4-board-representations/thumbnail.png")

N_COLUMNS, N_ROWS = 7, 6
COLUMN_BIT_OFFSET = 9

C_PANEL = "#20395c"
C_EMPTY = "#f4f6f9"
C_YELLOW = "#f2c14e"
C_RED = "#d1495b"
C_SET = "#4c78a8"
C_UNSET = "#dfe4ea"
C_GUARD = "#b9bfc7"
C_TEXT = "#20395c"
C_MUTED = "#6b7480"

# A position with a few tokens, so that both bit patterns look interesting.
MOVES = "3342135642"


def draw_board(ax, board, cx, y0, cell):
    """Connect-4 position as a panel with circular holes, centred on cx."""
    x0 = cx - N_COLUMNS * cell / 2
    ax.add_patch(
        FancyBboxPatch(
            (x0 - 0.16 * cell, y0 - 0.16 * cell),
            N_COLUMNS * cell + 0.32 * cell,
            N_ROWS * cell + 0.32 * cell,
            boxstyle="round,pad=0.02,rounding_size=0.2",
            facecolor=C_PANEL,
            edgecolor="none",
            mutation_scale=cell,
        )
    )
    arr = board.to_array()  # arr[col][row], row 0 at the bottom
    for c in range(N_COLUMNS):
        for r in range(N_ROWS):
            v = int(arr[c][r])
            colour = C_EMPTY if v == 0 else (C_YELLOW if v == 1 else C_RED)
            ax.add_patch(
                Circle(
                    (x0 + (c + 0.5) * cell, y0 + (r + 0.5) * cell),
                    0.38 * cell,
                    facecolor=colour,
                    edgecolor="none",
                )
            )


def draw_bits(ax, value, cx, y0, cell, label, hex_text):
    """One 64-bit word in the 9-bits-per-column layout, centred on cx."""
    x0 = cx - N_COLUMNS * cell / 2
    for c in range(N_COLUMNS):
        for r in range(N_ROWS + 3):
            on = (value >> (c * COLUMN_BIT_OFFSET + r)) & 1
            face = C_GUARD if r >= N_ROWS else (C_SET if on else C_UNSET)
            ax.add_patch(
                Rectangle(
                    (x0 + c * cell, y0 + r * cell),
                    cell * 0.84,
                    cell * 0.84,
                    facecolor=face,
                    edgecolor="none",
                )
            )
    ax.text(
        cx - cell * 0.08,
        y0 + (N_ROWS + 3) * cell + 0.16 * cell,
        label,
        fontsize=10,
        family="monospace",
        color=C_TEXT,
        ha="center",
        va="bottom",
    )
    ax.text(
        cx - cell * 0.08,
        y0 - 0.30 * cell,
        hex_text,
        fontsize=8.5,
        family="monospace",
        color=C_MUTED,
        ha="center",
        va="top",
    )


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    board = bb.Board(MOVES)
    all_tokens, active_tokens, _ = board.native.rawState()

    fig, ax = plt.subplots(figsize=(5.12, 5.12))  # 1024 x 1024 at 200 dpi
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(
        5.0,
        9.75,
        "Connect-4 in two",
        fontsize=17.5,
        weight="bold",
        color=C_TEXT,
        ha="center",
        va="top",
    )
    ax.text(
        5.0,
        9.0,
        "64-bit integers",
        fontsize=17.5,
        weight="bold",
        color=C_TEXT,
        ha="center",
        va="top",
    )

    draw_board(ax, board, cx=5.0, y0=4.55, cell=0.60)

    ax.add_patch(
        FancyArrow(
            5.0,
            4.15,
            0.0,
            -0.55,
            width=0.09,
            head_width=0.32,
            head_length=0.30,
            length_includes_head=True,
            facecolor=C_MUTED,
            edgecolor="none",
        )
    )

    draw_bits(
        ax,
        all_tokens,
        cx=3.02,
        y0=1.05,
        cell=0.235,
        label="m_bAllTokens",
        hex_text=f"0x{all_tokens:016x}",
    )
    draw_bits(
        ax,
        active_tokens,
        cx=6.98,
        y0=1.05,
        cell=0.235,
        label="m_bActivePTokens",
        hex_text=f"0x{active_tokens:016x}",
    )

    fig.savefig(OUT, dpi=200, bbox_inches="tight", pad_inches=0.1, facecolor="white")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
