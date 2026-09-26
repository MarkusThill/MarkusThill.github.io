"""
Alternative board figures for the Frozen Lake post, drawn with plain matplotlib instead of the
environment's sprite renderer. The post uses the sprite versions from make_frozen_lake_figures.py;
these are kept in case the flat style is preferred later. Output: tools/connect4_rl/figures_matplotlib/.

Run from the repository root (needs the cached data of make_frozen_lake_figures.py):

    SDL_VIDEODRIVER=dummy tools/connect4_rl/.venv/bin/python \
        tools/connect4_rl/make_frozen_lake_figures_matplotlib.py
"""

from __future__ import annotations

import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyArrowPatch, Rectangle

import frozen_lake_rl as fl
import make_frozen_lake_figures as mf
from make_frozen_lake_figures import BLUE, HOLE, ICE, INK, INK2, NONTERMINAL, ORANGE, cell_xy, plt

OUT = mf.HERE / "figures_matplotlib"
YELLOW, NEUTRAL = "#eda100", "#f0efec"
DIVERGING = LinearSegmentedColormap.from_list(
    "red_gray_blue", [(0.0, "#8c1c1c"), (0.25, "#e34948"), (0.5, NEUTRAL), (0.75, "#3987e5"), (1.0, "#104281")]
)
LAKE = fl.lake_map()


def save(fig, name: str) -> None:
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / name, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print("wrote", OUT / name)


def draw_board(ax, fills: dict[int, str] | None = None, values=None, cmap=DIVERGING, vmax=1.0,
               value_fmt="{:.2f}", fontsize=8, index=False, gap=0.05, start_label=True):
    """Draw the 8x8 lake. Terminal cells are always drawn as holes/goal."""
    ax.set_xlim(0, fl.N_COLS)
    ax.set_ylim(fl.N_ROWS, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    for s in range(fl.N_STATES):
        x, y = s % fl.N_COLS, s // fl.N_COLS
        letter = LAKE[y][x]
        if letter == "H":
            color, text, tcolor = HOLE, "H", "white"
        elif letter == "G":
            color, text, tcolor = YELLOW, "G", INK
        elif values is not None:
            v = values[s]
            color = cmap(0.5 + 0.5 * np.clip(v / vmax, -1, 1))
            text = value_fmt.format(v).replace("-", "−")
            tcolor = "white" if abs(v) / vmax > 0.55 else INK
        else:
            color = (fills or {}).get(s, ICE)
            text, tcolor = ("S" if letter == "S" and start_label else ""), INK
        ax.add_patch(Rectangle((x + gap / 2, y + gap / 2), 1 - gap, 1 - gap, facecolor=color,
                               edgecolor="none", zorder=1))
        if text:
            ax.text(x + 0.5, y + 0.5, text, ha="center", va="center", fontsize=fontsize,
                    color=tcolor, fontweight="bold" if letter in "HGS" else "normal", zorder=3)
        if index and letter not in "HG":
            ax.text(x + 0.08, y + 0.1, str(s), ha="left", va="top", fontsize=6.5, color=INK2, zorder=3)


def fig_lake():
    fig, ax = plt.subplots(figsize=(5.2, 5.6))
    draw_board(ax, index=True, fontsize=12)
    ax.text(0, 8.35, "S start      G goal (+1 on entry)      H hole (−1 on entry)      other moves 0",
            fontsize=8, color=INK2, va="top")
    ax.text(0, 8.75, "actions:  0 = ← left    1 = ↓ down    2 = → right    3 = ↑ up",
            fontsize=8, color=INK2, va="top")
    ax.set_ylim(9.0, 0)
    save(fig, "lake-map.png")


def fig_route():
    env = fl.make_lake(False)
    states, _, rewards, _ = fl.run_episode(env, fl.pi_2, np.random.default_rng(0), seed=0)
    G = fl.returns(rewards)
    fig, ax = plt.subplots(figsize=(6.0, 5.2))
    draw_board(ax, fills={s: "#9ec5f4" for s in states[:-1]}, fontsize=12, start_label=False)
    for s0, s1 in zip(states[:-1], states[1:]):
        mf.arrow(ax, s0, s1, color=INK2, lw=1.2, shrink=0.36, ms=8)
    for t, s in enumerate(states[:-1]):
        x, y = cell_xy(s)
        highlight = s in (39, 47, 55)
        ax.text(x, y, f"{G[t]:.2f}", ha="center", va="center", fontsize=9 if highlight else 8,
                color=INK, fontweight="bold" if highlight else "normal", zorder=5)
    for s0, s1, r in [(39, 47, 0), (47, 55, 0), (55, 63, 1)]:
        (x0, y0), (x1, y1) = cell_xy(s0), cell_xy(s1)
        ax.text(8.12, (y0 + y1) / 2, f"$R$ = {r:+d}" if r else "$R$ = 0", ha="left", va="center",
                fontsize=8.5, color=INK2)
    ax.annotate("", xy=(0.1, 0.5), xytext=(-0.25, 0.5), annotation_clip=False,
                arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.2))
    ax.text(-0.3, 0.5, "S", ha="right", va="center", fontsize=11, fontweight="bold", color=INK)
    ax.set_xlim(-0.6, 9.0)
    save(fig, "pi2-route-returns.png")


def fig_slip():
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.4))
    for ax, (center, title) in zip(axes, [((1, 1), "interior cell, action ↓"), ((1, 0), "cell at the left edge, action ↓")]):
        ax.set_xlim(-0.05, 3.05)
        ax.set_ylim(3.05, -0.05)
        ax.set_aspect("equal")
        ax.axis("off")
        r0, c0 = center
        for r in range(3):
            for c in range(3):
                if c0 == 0 and c == 0:
                    continue
                ax.add_patch(Rectangle((c + 0.03, r + 0.03), 0.94, 0.94, facecolor=ICE, edgecolor="none"))
        if c0 == 0:
            ax.plot([1, 1], [0, 3], color=INK, lw=3)
            ax.text(0.9, 0.2, "edge of\nthe lake", ha="right", va="top", color=mf.MUTED, fontsize=8.5)
        cx, cy = 1.5, 1.5
        ax.add_patch(plt.Circle((cx, cy), 0.16, facecolor=INK, edgecolor="none", zorder=4))
        targets = [((0, 1), "0.75", BLUE), ((-1, 0), "0.125", ORANGE), ((1, 0), "0.125", ORANGE)]
        for (dx, dy), p, color in targets:
            if c0 == 0 and dx == -1:
                ax.add_patch(FancyArrowPatch((cx - 0.12, cy - 0.17), (cx - 0.12, cy + 0.17), connectionstyle="arc3,rad=1.6",
                                             arrowstyle="-|>", mutation_scale=9, color=color, lw=1.4, zorder=5))
                ax.text(0.9, cy, f"{p}:\nblocked,\nstays put", ha="right", va="center", fontsize=8.5, color=INK2)
                continue
            ax.add_patch(FancyArrowPatch((cx + 0.2 * dx, cy + 0.2 * dy), (cx + 0.82 * dx, cy + 0.82 * dy),
                                         arrowstyle="-|>", mutation_scale=11, color=color, lw=2 if p == "0.75" else 1.4, zorder=5))
            ax.text(cx + 0.55 * dx + (0.18 if dx == 0 else 0), cy + 0.55 * dy - (0.16 if dy == 0 else 0), p,
                    ha="left" if dx == 0 else "center", va="center", fontsize=8.5, color=INK2)
        ax.set_title(title, fontsize=9.5, loc="left")
    fig.tight_layout()
    save(fig, "slip-directions.png")


def fig_value_maps():
    fig, axes = plt.subplots(2, 2, figsize=(8.0, 8.9))
    for i, policy in enumerate(["pi_2", "pi_1"]):
        for j, slippery in enumerate([False, True]):
            v = fl.exact_state_values(policy, slippery)
            ax = axes[i, j]
            draw_board(ax, values=v, fontsize=7.5)
            name = "π₂" if policy == "pi_2" else "π₁"
            world = "slippery" if slippery else "deterministic"
            ax.set_title(f"{name}, {world}:  V(0) = {v[0]:.3f}".replace("-", "−"), fontsize=10, loc="left")
    cax = fig.add_axes([0.25, 0.055, 0.5, 0.014])
    sm = plt.cm.ScalarMappable(cmap=DIVERGING, norm=plt.Normalize(-1, 1))
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cb.outline.set_visible(False)
    cb.set_label("exact state value $V^\\pi(s)$, computed from the transition table", color=INK2, fontsize=9)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.1, wspace=0.06, hspace=0.12)
    save(fig, "value-maps-deterministic-vs-slippery.png")


def fig_q_policy(Q, q_star, detail_state: int):
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(9.2, 5.0), gridspec_kw={"width_ratios": [1.6, 1]})
    v = Q.max(axis=1)
    draw_board(ax, values=np.where(NONTERMINAL, v, 0), value_fmt="", fontsize=11)
    greedy, optimal = Q.argmax(1), q_star.argmax(1)
    offsets = {fl.LEFT: (-1, 0), fl.DOWN: (0, 1), fl.RIGHT: (1, 0), fl.UP: (0, -1)}
    for s in np.flatnonzero(NONTERMINAL):
        x, y = cell_xy(s)
        dx, dy = offsets[greedy[s]]
        color = "white" if abs(v[s]) > 0.55 else INK
        ax.add_patch(FancyArrowPatch((x - 0.28 * dx, y - 0.28 * dy), (x + 0.3 * dx, y + 0.3 * dy),
                                     arrowstyle="-|>", mutation_scale=11, color=color, lw=1.6, zorder=5))
        if greedy[s] != optimal[s]:
            ax.add_patch(Rectangle((s % 8 + 0.06, s // 8 + 0.06), 0.88, 0.88, fill=False, edgecolor=ORANGE, lw=2, zorder=6))
    dx, dy = detail_state % 8, detail_state // 8
    ax.add_patch(Rectangle((dx + 0.02, dy + 0.02), 0.96, 0.96, fill=False, edgecolor=INK, lw=2.2, zorder=7))
    ax.set_title("greedy action and max$_a$ Q(s, a) after 15,000 episodes", fontsize=10, loc="left")
    # one-cell detail
    ax2.set_xlim(-1.6, 1.6)
    ax2.set_ylim(1.75, -1.6)
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.add_patch(Rectangle((-0.5, -0.5), 1, 1, facecolor=NEUTRAL, edgecolor="none"))
    ax2.text(0, 0, f"state\n{detail_state}", ha="center", va="center", fontsize=9, color=INK2)
    for a, (ddx, ddy) in offsets.items():
        best = a == greedy[detail_state]
        ax2.text(1.0 * ddx, 0.95 * ddy, f"{fl.ARROWS[a]}  {Q[detail_state, a]:+.3f}".replace("-", "−"),
                 ha="center", va="center", fontsize=10, color=INK, fontweight="bold" if best else "normal")
        ax2.text(1.0 * ddx, 0.95 * ddy + 0.25, f"Q* {q_star[detail_state, a]:+.3f}".replace("-", "−"),
                 ha="center", va="center", fontsize=8, color=mf.MUTED)
    ax2.set_title(f"the four action values of state {detail_state}", fontsize=10, loc="left")
    fig.tight_layout()
    save(fig, "q-learning-policy.png")


def main():
    tables = dict(np.load(mf.DATA / "q_learning_tables.npz"))
    fig_lake()
    fig_route()
    fig_slip()
    fig_value_maps()
    fig_q_policy(tables["seed0"], tables["q_star"], detail_state=47)


if __name__ == "__main__":
    main()
