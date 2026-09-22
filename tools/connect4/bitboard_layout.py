#!/usr/bin/env python3
"""Bit-layout diagrams for part 3 of the Connect-4 series.

Emits one PNG per engine so that the post can place them side by side in an
al-folio ``.row`` / ``.col-sm`` grid:

* ``bit-layout-cfour.png``    -- CFour (2012, Java): 42 usable bits,
  ``bit = 41 - 6*col - row``, no guard bits, column heights kept in
  ``colHeight[]``.
* ``bit-layout-bitbully.png`` -- BitBully (C++): 9 bits per column,
  ``bit = col * 9 + row``, the top three bits of every column are guard bits.

Both grids are seven cells wide and are drawn with the *same* inches-per-cell,
so when the two images are scaled to equal column widths the cells come out at
identical size and only the height differs -- which is exactly the point being
made. Drawing them as two subplots of one figure does the opposite: equal
subplot heights shrink the taller 9-row grid.

Run from the repo root::

    tools/.venv/bin/python tools/connect4/bitboard_layout.py
"""

from __future__ import annotations

import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

N_COLUMNS = 7
N_ROWS = 6

OUT_DIR = pathlib.Path("assets/img/2026-01-29-connect-4-board-representations")

CELL_INCHES = 0.62  # identical in both figures -> identical cell size on screen

C_PLAYABLE = "#4C78A8"
C_GUARD = "#B0B0B0"
C_TEXT = "#FFFFFF"
C_TEXT_DARK = "#333333"
C_ACCENT = "#D62728"


def draw_layout(out_name, bit_index, n_rows_drawn, title, subtitle, guard_rows=False):
    """Render one bit-layout grid to its own PNG."""
    # Extra vertical room for the title, the subtitle and the guard-bit label.
    pad_top = 1.15 if guard_rows else 0.75
    pad_bottom = 1.05
    fig_w = N_COLUMNS * CELL_INCHES
    fig_h = (n_rows_drawn + pad_top + pad_bottom) * CELL_INCHES
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    for row in range(n_rows_drawn):
        for col in range(N_COLUMNS):
            idx = bit_index(col, row)
            is_guard = row >= N_ROWS
            face, text_col = (
                (C_GUARD, C_TEXT_DARK) if is_guard else (C_PLAYABLE, C_TEXT)
            )
            ax.add_patch(
                Rectangle((col, row), 0.92, 0.92, facecolor=face, edgecolor="none")
            )
            ax.text(
                col + 0.46,
                row + 0.46,
                str(idx),
                ha="center",
                va="center",
                fontsize=9,
                color=text_col,
                family="monospace",
            )

    if guard_rows:
        ax.plot(
            [-0.05, N_COLUMNS - 0.03],
            [N_ROWS - 0.06, N_ROWS - 0.06],
            color=C_ACCENT,
            lw=1.4,
            ls="--",
        )
        ax.text(
            N_COLUMNS / 2 - 0.05,
            n_rows_drawn + 0.14,
            "guard bits (never played)",
            ha="center",
            va="bottom",
            fontsize=8.5,
            color=C_ACCENT,
        )

    ax.set_xlim(-0.15, N_COLUMNS)
    ax.set_ylim(-pad_bottom, n_rows_drawn + pad_top)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(
        N_COLUMNS / 2 - 0.05,
        n_rows_drawn + pad_top - 0.28,
        title,
        ha="center",
        va="top",
        fontsize=10.5,
        weight="bold",
        color=C_TEXT_DARK,
    )
    ax.text(
        N_COLUMNS / 2 - 0.05,
        -0.30,
        subtitle,
        ha="center",
        va="top",
        fontsize=8.5,
        family="monospace",
        color=C_TEXT_DARK,
    )

    out = OUT_DIR / out_name
    # Opaque white: the figure reads as a light "card" so the dark labels stay
    # legible in both the light and the dark site theme.
    fig.savefig(out, dpi=200, bbox_inches="tight", pad_inches=0.06, facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    draw_layout(
        "bit-layout-cfour.png",
        bit_index=lambda col, row: N_COLUMNS * N_ROWS - 1 - col * N_ROWS - row,
        n_rows_drawn=N_ROWS,
        title="CFour (2012, Java)",
        subtitle="bit = 41 - 6*col - row\n42 bits used, heights in colHeight[]",
    )
    draw_layout(
        "bit-layout-bitbully.png",
        bit_index=lambda col, row: col * 9 + row,
        n_rows_drawn=N_ROWS + 3,
        guard_rows=True,
        title="BitBully (C++)",
        subtitle="bit = col * 9 + row\n63 bits used, no height array needed",
    )


if __name__ == "__main__":
    main()
