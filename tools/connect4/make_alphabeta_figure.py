#!/usr/bin/env python3
"""Alpha-beta pruning diagram for part 2 of the Connect-4 series.

A 3-ply example tree (MAX to move at the root, three MIN children, nine
leaves). The diagram is not hand-asserted: the script first *runs* a small
fail-hard alpha-beta pair over the tree, records which leaves are visited,
where the cutoffs fire and which windows are passed down, and then draws the
figure from that trace. If the values below are ever changed, the drawing
follows automatically -- and the assertions at the bottom of ``search()`` keep
the caption's claims true.

Run from the repo root::

    tools/.venv/bin/python tools/connect4/make_alphabeta_figure.py
"""

from __future__ import annotations

import math
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle

OUT_DIR = pathlib.Path("assets/img/2026-01-15-connect-4-tree-search-algorithms")

# The static leaf values, one list per MIN node (searched left to right).
LEAVES = [[3, 5, 4], [2, 9, 7], [6, 3, 8]]

INF = math.inf

C_LIVE = "#4C78A8"
C_PRUNED = "#B0B0B0"
C_ACCENT = "#D62728"
C_TEXT = "#333333"
C_TEXT_LIGHT = "#666666"


def search():
    """The max()/min() pair from the post, fail-hard, with a trace."""
    trace = {"min_nodes": [], "order": {}}
    alpha, beta = -INF, INF
    step = 0

    for i, leaves in enumerate(LEAVES):
        node = {"window": (alpha, beta), "visited": 0, "cutoff": False}
        a, b = alpha, beta  # the window the MIN node receives
        for value in leaves:
            step += 1
            trace["order"][(i, node["visited"])] = step
            node["visited"] += 1
            if value <= a:  # min(): if (value <= alpha) return alpha;
                node["cutoff"] = True
                node["bound"] = value  # all we know: true value <= this
                ret = a
                break
            if value < b:  # min(): if (value < beta) beta = value;
                b = value
        else:
            ret = b
            node["value"] = b
        node["ret"] = ret
        trace["min_nodes"].append(node)
        if ret > alpha:  # max(): if (value > alpha) alpha = value;
            alpha = ret

    trace["root_value"] = alpha
    trace["leaves_visited"] = sum(n["visited"] for n in trace["min_nodes"])

    # The facts the caption states, kept true mechanically.
    assert trace["root_value"] == 3
    assert trace["leaves_visited"] == 6  # minimax would visit all 9
    assert [n.get("cutoff") for n in trace["min_nodes"]] == [False, True, True]
    return trace


def fmt(v):
    return "−∞" if v == -INF else ("+∞" if v == INF else str(v))


def draw(trace):
    fig, ax = plt.subplots(figsize=(8.6, 5.0))

    leaf_x = [[i * 3 + j for j in range(3)] for i in range(3)]
    min_x = [xs[1] for xs in leaf_x]
    root_x = min_x[1]
    y_leaf, y_min, y_root = 0.0, 2.1, 4.2
    half = 0.34  # half-width of the node shapes

    def tri(x, y, down, color):
        pts = (
            [(x - half, y + half), (x + half, y + half), (x, y - half)]
            if down
            else [(x - half, y - half), (x + half, y - half), (x, y + half)]
        )
        ax.add_patch(Polygon(pts, closed=True, facecolor=color, edgecolor="none", zorder=3))

    def edge(x0, y0, x1, y1, pruned=False):
        ax.plot(
            [x0, x1],
            [y0, y1],
            color=C_PRUNED if pruned else C_TEXT_LIGHT,
            lw=1.1,
            ls=(0, (4, 3)) if pruned else "-",
            zorder=1,
        )
        if pruned:  # the classical double slash across the pruned edge
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            for d in (-0.07, 0.07):
                ax.plot(
                    [mx - 0.11 + d, mx + 0.11 + d],
                    [my - 0.14, my + 0.14],
                    color=C_ACCENT,
                    lw=1.6,
                    zorder=2,
                )

    # Root (MAX).
    tri(root_x, y_root, down=False, color=C_LIVE)
    ax.text(root_x, y_root - 0.09, str(trace["root_value"]), ha="center", va="center", fontsize=11, color="white", family="monospace", weight="bold", zorder=4)
    ax.text(root_x + 0.55, y_root + 0.05, "MAX", ha="left", va="center", fontsize=9, color=C_TEXT_LIGHT)
    ax.text(
        root_x + 0.55,
        y_root - 0.38,
        "α: −∞ → 3 after the first reply",
        ha="left",
        va="center",
        fontsize=8.5,
        family="monospace",
        color=C_TEXT_LIGHT,
    )

    for i, node in enumerate(trace["min_nodes"]):
        cut = node["cutoff"]
        # Edge root -> MIN node, labelled with the window handed down.
        edge(root_x, y_root - half, min_x[i], y_min + half)
        lo, hi = node["window"]
        t = 0.62 if i == 2 else 0.5  # slide the right label down its edge
        mx = root_x + (min_x[i] - root_x) * t
        my = y_root + (y_min - y_root) * t
        left_side = i <= 1
        ax.text(
            mx + (-0.18 if left_side else 0.18),
            my + 0.28,
            f"[{fmt(lo)}, {fmt(hi)}]",
            ha="right" if left_side else "left",
            va="center",
            fontsize=8.5,
            family="monospace",
            color=C_TEXT,
        )

        # MIN node with its exact value or its bound.
        tri(min_x[i], y_min, down=True, color=C_ACCENT if cut else C_LIVE)
        label = f"≤{node['bound']}" if cut else str(node["value"])
        ax.text(min_x[i], y_min + 0.10, label, ha="center", va="center", fontsize=10, color="white", family="monospace", weight="bold", zorder=4)
        if i == 0:
            ax.text(min_x[i] - 0.55, y_min + 0.05, "MIN", ha="right", va="center", fontsize=9, color=C_TEXT_LIGHT)
        if cut:
            ax.text(
                min_x[i],
                y_min - 0.62,
                f"{node['bound']} ≤ α — prune",
                ha="center",
                va="top",
                fontsize=8.5,
                color=C_ACCENT,
            )

        # Leaves.
        for j, value in enumerate(LEAVES[i]):
            x = leaf_x[i][j]
            visited = j < node["visited"]
            edge(min_x[i], y_min - half, x, y_leaf + half, pruned=not visited)
            face = C_LIVE if visited else "white"
            ec = "none" if visited else C_PRUNED
            ax.add_patch(
                Rectangle((x - 0.30, y_leaf - 0.30), 0.60, 0.60, facecolor=face, edgecolor=ec, lw=1.1, ls="-" if visited else (0, (3, 2)), zorder=3)
            )
            ax.text(
                x,
                y_leaf,
                str(value),
                ha="center",
                va="center",
                fontsize=10,
                family="monospace",
                weight="bold" if visited else "normal",
                color="white" if visited else C_PRUNED,
                zorder=4,
            )
            if visited:
                ax.text(x, y_leaf - 0.62, str(trace["order"][(i, j)]), ha="center", va="top", fontsize=7.5, color=C_TEXT_LIGHT, family="monospace")

    ax.text(
        leaf_x[0][0] - 0.35,
        y_leaf - 0.62,
        "visit order:",
        ha="right",
        va="top",
        fontsize=7.5,
        color=C_TEXT_LIGHT,
    )

    # A small legend line at the bottom.
    ax.text(
        (leaf_x[0][0] + leaf_x[2][2]) / 2,
        -1.45,
        "△ MAX node     ▽ MIN node     dashed = never generated     "
        f"{trace['leaves_visited']} of {sum(len(l) for l in LEAVES)} leaves evaluated",
        ha="center",
        va="center",
        fontsize=8.5,
        color=C_TEXT_LIGHT,
    )

    ax.set_xlim(-1.6, 9.4)
    ax.set_ylim(-1.8, 5.0)
    ax.set_aspect("equal")
    ax.axis("off")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "alpha-beta-pruning.png"
    # Opaque white card, like the other figures of the series, so the labels
    # stay legible in the dark site theme as well.
    fig.savefig(out, dpi=200, bbox_inches="tight", pad_inches=0.10, facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


if __name__ == "__main__":
    draw(search())
