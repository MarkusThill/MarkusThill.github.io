"""
Data, figures and videos for "Crossing the Frozen Lake: Monte Carlo, TD(0) and Q-Learning".

Run from the repository root (pygame needs no display with the dummy driver):

    SDL_VIDEODRIVER=dummy tools/connect4_rl/.venv/bin/python \
        tools/connect4_rl/make_frozen_lake_figures.py [--quick]

Experiment results are cached as JSON/NPZ in tools/connect4_rl/data/. Delete a file to
recompute it. --quick runs a cheap smoke version and writes nothing to assets/.
All randomness is seeded; the seeds are listed next to each experiment below.
"""

from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patheffects
from matplotlib.patches import FancyArrowPatch, Rectangle

import frozen_lake_rl as fl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SLUG = "2026-06-04-frozen-lake-monte-carlo-td-q-learning"
IMG = ROOT / "assets" / "img" / SLUG
VIDEO = ROOT / "assets" / "video"
DATA = HERE / "data"

# ---------------------------------------------------------------------------
# Experiment settings
# ---------------------------------------------------------------------------
PRED_SEEDS = [0, 1, 2, 3, 4]  # env seed = s, policy seed = 100 + s
PRED_EPISODES = 20_000
PRED_ALPHA = 0.05

Q_SEEDS = [0, 1, 2, 3, 4]  # env seed = s, behaviour seed = 100 + s
Q_EPISODES = 15_000
Q_EVAL_EVERY = 500
Q_EVAL_EPISODES = 1_000  # per point of the learning curve, eval seed = 10_000 + episode
Q_FINAL_EVAL_EPISODES = 10_000  # eval seed = 20_000 + s

# ---------------------------------------------------------------------------
# Style (light surface; the blog renders figures as static PNGs)
# ---------------------------------------------------------------------------
SURFACE = "#ffffff"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
ICE, HOLE = "#cde2fb", "#383835"
BLUE_RAMP = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281", "#0d366b"]  # ordinal steps 250..700

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.edgecolor": AXIS,
    "axes.labelcolor": INK2,
    "axes.titlecolor": INK,
    "axes.titlesize": 11,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "savefig.dpi": 160,
    "legend.frameon": False,
})

TERMINAL = fl.terminal_states()
NONTERMINAL = ~TERMINAL


QUICK_DIR: Path | None = None  # --quick writes figures here if --img-dir is given


def save(fig, name: str, quick: bool) -> None:
    out = QUICK_DIR if quick else IMG
    if out is None:
        plt.close(fig)
        return
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / name, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print("wrote", out / name)


# ---------------------------------------------------------------------------
# Board drawing: the environment's own renderer (sprites and value overlays, as in the
# lab notebook), re-initialised at a higher resolution, with matplotlib annotations on top
# ---------------------------------------------------------------------------
def cell_xy(s: int) -> tuple[float, float]:
    """Centre of state s in board coordinates (x = column, y = row, row 0 at the top)."""
    return s % fl.N_COLS + 0.5, s // fl.N_COLS + 0.5


def render_board(values=None, q=None, agent: int = 63, facing: int = fl.DOWN, slippery: bool = False,
                 scale: int = 2) -> np.ndarray:
    """RGB image of the lake from FrozenLakeEnv's renderer, optionally with V(s) or Q(s, a) on the cells.

    The renderer draws 64-pixel cells. For the blog it is re-initialised with cells, sprites and fonts
    `scale` times larger, which keeps its layout; only the Q-value font is slightly smaller, so that the
    four labels of a cell collide less. When values are printed, the start stool is left out and the
    agent stands on the goal (by default), so that neither hides a value.
    """
    import pygame

    env = fl.make_lake(slippery, render_mode="rgb_array")
    env.reset(seed=0)
    u = env.unwrapped
    env.render()  # initialises pygame, fonts and sprites at the default size
    if scale != 1:
        side = 512 * scale
        u.window_size, u.cell_size = (side, side), (side // fl.N_COLS, side // fl.N_ROWS)
        u.window_surface = pygame.Surface(u.window_size)
        u.hole_img = u.cracked_hole_img = u.ice_img = u.goal_img = u.start_img = u.elf_images = None
        u.text_padding = 5 * scale
        u.q_font = pygame.font.SysFont("Courier", 12 * scale)
        u.q_font_bold = pygame.font.SysFont("Courier", 12 * scale, True)
        u.v_font_bold = pygame.font.SysFont("Courier", 14 * scale, True)
    if values is not None or q is not None:
        u.start_img = pygame.Surface(u.cell_size, pygame.SRCALPHA)  # transparent: no stool
    u.set_show_q_labels(values is not None or q is not None)
    u.set_v(values)
    u.set_q(q)
    u.s, u.lastaction = agent, facing
    return env.render()


def show_board(ax, frame: np.ndarray) -> None:
    ax.imshow(frame, extent=(0, fl.N_COLS, fl.N_ROWS, 0))
    ax.set_xlim(0, fl.N_COLS)
    ax.set_ylim(fl.N_ROWS, 0)
    ax.axis("off")


def frame_cell(ax, s: int, color: str, inset: float, lw: float = 2.2) -> None:
    x, y = s % fl.N_COLS, s // fl.N_COLS
    ax.add_patch(Rectangle((x + inset, y + inset), 1 - 2 * inset, 1 - 2 * inset, fill=False, edgecolor=color,
                           lw=lw, zorder=6))


def arrow(ax, s_from: int, s_to: int, color=INK, lw=1.6, shrink=0.28, style="-|>", ms=10, zorder=4):
    (x0, y0), (x1, y1) = cell_xy(s_from), cell_xy(s_to)
    dx, dy = x1 - x0, y1 - y0
    ax.add_patch(FancyArrowPatch((x0 + shrink * dx, y0 + shrink * dy), (x1 - shrink * dx, y1 - shrink * dy),
                                 arrowstyle=style, mutation_scale=ms, color=color, lw=lw, zorder=zorder))


HALO = [patheffects.withStroke(linewidth=2.5, foreground="white")]


# ---------------------------------------------------------------------------
# Experiments
# ---------------------------------------------------------------------------
def checkpoints(n: int) -> list[int]:
    return sorted(set(np.unique(np.round(np.logspace(0, np.log10(n), 70)).astype(int)).tolist()))


def run_prediction(slippery: bool, n_episodes: int, seeds: list[int]) -> dict:
    """Feed the same pi_1 episodes to three learners and record their RMS error."""
    v_ref = fl.exact_state_values("pi_1", slippery)
    marks = set(checkpoints(n_episodes))
    runs = []
    for seed in seeds:
        env, rng = fl.make_lake(slippery), np.random.default_rng(100 + seed)
        env.reset(seed=seed)
        V = {"mc_mean": np.zeros(fl.N_STATES), "mc_const": np.zeros(fl.N_STATES), "td": np.zeros(fl.N_STATES)}
        N_mean, N_const = np.zeros(fl.N_STATES), np.zeros(fl.N_STATES)
        rec = {"episodes": [], "transitions": [], "coverage": []} | {k: [] for k in V}
        transitions = 0
        for episode in range(1, n_episodes + 1):
            states, _, rewards, terminated = fl.run_episode(env, fl.pi_1, rng)
            assert terminated  # prediction episodes always end in a hole or the goal
            transitions += len(rewards)
            fl.mc_first_visit_update(V["mc_mean"], N_mean, states, rewards)
            fl.mc_first_visit_update(V["mc_const"], N_const, states, rewards, alpha=PRED_ALPHA)
            fl.td0_episode(V["td"], states, rewards, terminated, alpha=PRED_ALPHA)
            if episode in marks:
                rec["episodes"].append(episode)
                rec["transitions"].append(transitions)
                rec["coverage"].append(int((N_mean[NONTERMINAL] > 0).sum()))
                for k, v in V.items():
                    rec[k].append(float(np.sqrt(np.mean((v - v_ref)[NONTERMINAL] ** 2))))
        rec["final"] = {k: v.tolist() for k, v in V.items()}
        runs.append(rec)
        print(f"  prediction slippery={slippery} seed={seed}: {transitions} transitions")
    return {"slippery": slippery, "alpha": PRED_ALPHA, "n_episodes": n_episodes, "seeds": seeds,
            "v_ref": v_ref.tolist(), "runs": runs}


def run_q_learning(n_episodes: int, seeds: list[int], eval_every: int, eval_episodes: int, final_episodes: int):
    q_star = fl.optimal_action_values(slippery=True)
    runs, tables = [], {}
    for seed in seeds:
        t0 = time.perf_counter()
        curve = []

        def evaluate(episode, Q):
            if episode % eval_every == 0:
                ev = fl.evaluate_greedy(Q, fl.make_lake(True, fl.MAX_STEPS), eval_episodes,
                                        seed=10_000 + episode, rng=np.random.default_rng(10_000 + episode))
                pi = fl.greedy_policy_matrix(Q)  # model-based analysis of the same greedy policy
                exact = {"exact_start_value": float(fl.policy_values(pi, slippery=True)[0])}
                exact |= {f"exact_{k}": v for k, v in fl.outcome_probabilities(pi, slippery=True).items()}
                curve.append({"episode": episode} | ev | exact)

        Q = fl.q_learning(fl.make_lake(True, fl.MAX_STEPS), n_episodes, np.random.default_rng(100 + seed),
                          seed=seed, callback=evaluate)
        final = fl.evaluate_greedy(Q, fl.make_lake(True, fl.MAX_STEPS), final_episodes,
                                   seed=20_000 + seed, rng=np.random.default_rng(20_000 + seed))
        pi_greedy = fl.greedy_policy_matrix(Q)
        v_greedy = fl.policy_values(pi_greedy, slippery=True)
        runs.append({
            "seed": seed, "curve": curve, "final": final,
            "exact_outcomes": fl.outcome_probabilities(pi_greedy, slippery=True),
            "exact_start_value": float(v_greedy[0]), "max_q_start": float(Q[0].max()),
            "agreement_with_optimal": float(np.mean((Q.argmax(1) == q_star.argmax(1))[NONTERMINAL])),
            "seconds_incl_evaluation": time.perf_counter() - t0,
        })
        tables[f"seed{seed}"] = Q
        print(f"  q-learning seed={seed}: {final}")
    t0 = time.perf_counter()
    fl.q_learning(fl.make_lake(True, fl.MAX_STEPS), n_episodes, np.random.default_rng(999), seed=999)
    train_seconds = time.perf_counter() - t0
    optimal = fl.evaluate_greedy(q_star, fl.make_lake(True, fl.MAX_STEPS), final_episodes,
                                 seed=30_000, rng=np.random.default_rng(30_000))
    pi_opt = fl.greedy_policy_matrix(q_star)
    v_opt = fl.policy_values(pi_opt, slippery=True)
    optimal_by_gamma = {}
    for gamma in (0.9, 0.95, 0.99):
        pi_g = fl.greedy_policy_matrix(fl.optimal_action_values(slippery=True, gamma=gamma))
        optimal_by_gamma[str(gamma)] = fl.outcome_probabilities(pi_g, slippery=True)
    summary = {"n_episodes": n_episodes, "alpha": 0.1, "gamma": fl.GAMMA, "epsilon_start": 0.5,
               "epsilon_decay": 1e-4, "max_steps": fl.MAX_STEPS, "eval_every": eval_every,
               "eval_episodes": eval_episodes, "final_eval_episodes": final_episodes, "runs": runs,
               "training_seconds_without_evaluation": train_seconds,
               "optimal": optimal | {"exact_start_value": float(v_opt[0]),
                                     "exact_outcomes": fl.outcome_probabilities(pi_opt, slippery=True)},
               "optimal_outcomes_by_gamma": optimal_by_gamma}
    return summary, tables | {"q_star": q_star}


def cached_json(name: str, compute, quick: bool):
    path = DATA / name
    if not quick and path.exists():
        return json.loads(path.read_text())
    result = compute()
    if not quick:
        DATA.mkdir(exist_ok=True)
        path.write_text(json.dumps(result, indent=1))
    return result


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
def fig_lake(quick):
    fig, ax = plt.subplots(figsize=(6.4, 7.1))
    show_board(ax, render_board(agent=0))
    for s in range(fl.N_STATES):
        x, y = s % fl.N_COLS, s // fl.N_COLS
        ax.text(x + 0.06, y + 0.05, str(s), ha="left", va="top", fontsize=8, color=INK, path_effects=HALO, zorder=5)
    legend = ["start: upper left corner (cell 0)       goal: lower right corner (cell 63), +1 on entry",
              "holes: −1 on entry       every other move: 0",
              "actions:  0 = ← left    1 = ↓ down    2 = → right    3 = ↑ up"]
    for i, line in enumerate(legend):
        ax.text(0, 8.28 + 0.36 * i, line, fontsize=8.5, color=INK2, va="top")
    ax.set_ylim(9.35, 0)
    save(fig, "lake-map.png", quick)


def fig_route(quick):
    env = fl.make_lake(False)
    states, _, rewards, _ = fl.run_episode(env, fl.pi_2, np.random.default_rng(0), seed=0)
    fig, ax = plt.subplots(figsize=(7.3, 6.4))
    show_board(ax, render_board(values=fl.exact_state_values("pi_2", slippery=False)))
    for s0, s1 in zip(states[:-1], states[1:]):
        arrow(ax, s0, s1, color=INK, lw=2.0, shrink=0.4, ms=12, zorder=5)
    for s0, s1, r in [(39, 47, 0), (47, 55, 0), (55, 63, 1)]:
        (_, y0), (_, y1) = cell_xy(s0), cell_xy(s1)
        ax.text(8.12, (y0 + y1) / 2, f"$R$ = {r:+d}" if r else "$R$ = 0", ha="left", va="center",
                fontsize=9, color=INK2)
    ax.set_xlim(0, 9.15)
    save(fig, "pi2-route-returns.png", quick)


def fig_update_timing(quick):
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 4.2), sharex=True)
    xs = np.arange(5)
    for ax, title in zip(axes, ["Monte Carlo", "TD(0)"]):
        ax.set_xlim(-0.6, 4.9)
        ax.set_ylim(-1.25, 1.5)
        ax.axis("off")
        ax.text(-0.6, 1.4, title, fontsize=11, color=INK, fontweight="bold", va="top")
        for x in xs:
            terminal = x == 4
            ax.plot(x, 0, marker="s" if terminal else "o", ms=24, color=HOLE if terminal else ICE, zorder=2)
            ax.text(x, 0, f"$S_{x}$", ha="center", va="center", fontsize=9,
                    color="white" if terminal else INK, zorder=3)
        for x in xs[:-1]:
            ax.annotate("", xy=(x + 0.76, 0), xytext=(x + 0.24, 0),
                        arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.0))
            ax.text(x + 0.5, -0.17, f"$R_{x + 1}$", ha="center", va="top", fontsize=8, color=INK2)
        ax.plot([-0.4, 4.4], [-0.75, -0.75], color=AXIS, lw=0.8)
        for x in xs:
            ax.plot([x, x], [-0.8, -0.7], color=AXIS, lw=0.8)
            ax.text(x, -0.88, f"t = {x}", ha="center", va="top", fontsize=7.5, color=MUTED)
    ax = axes[0]
    for x in range(4):
        ax.add_patch(FancyArrowPatch((4, 0.22), (x, 0.22), connectionstyle=f"arc3,rad={0.18 + 0.05 * (3 - x)}",
                                     arrowstyle="-|>", mutation_scale=9, color=BLUE, lw=1.3, zorder=1))
    ax.text(2.0, 1.15, r"after the episode has ended: $V(S_t) \leftarrow$ mean of the returns $G_t$",
            ha="center", fontsize=8.5, color=INK2)
    ax.plot([4, 4], [-0.75, -0.75], marker="v", color=BLUE, ms=7, zorder=5)
    ax.text(4.22, -0.6, "all updates", fontsize=7.5, color=BLUE, va="bottom")
    ax = axes[1]
    for x in range(4):
        ax.add_patch(FancyArrowPatch((x + 1, 0.22), (x, 0.22), connectionstyle="arc3,rad=0.55",
                                     arrowstyle="-|>", mutation_scale=9, color=AQUA, lw=1.3, zorder=1))
        ax.plot([x + 1, x + 1], [-0.75, -0.75], marker="v", color=AQUA, ms=7, zorder=5)
    ax.text(2.0, 1.15, r"right after each step: $V(S_t) \leftarrow V(S_t) + \alpha\,[R_{t+1} + \gamma V(S_{t+1}) - V(S_t)]$",
            ha="center", fontsize=8.5, color=INK2)
    ax.text(4.22, -0.6, "one update\nper step", fontsize=7.5, color=AQUA, va="bottom")
    fig.tight_layout(h_pad=0.4)
    save(fig, "mc-vs-td-update-timing.png", quick)


def fig_td_propagation(quick):
    env = fl.make_lake(False)
    states, _, rewards, terminated = fl.run_episode(env, fl.pi_2, np.random.default_rng(0), seed=0)
    route = states[:-1]
    exact = fl.returns(rewards)
    shown = [1, 2, 5, 14, 50, 200]
    snapshots = {}
    V = np.zeros(fl.N_STATES)
    for episode in range(1, max(shown) + 1):
        fl.td0_episode(V, states, rewards, terminated, alpha=0.1)
        if episode in shown:
            snapshots[episode] = V[route].copy()
    x = np.arange(len(route))
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    ax.plot(x, exact, color=INK, lw=2, marker="o", ms=4, zorder=5, label="MC after 1 episode (= exact)")
    for color, episode in zip(BLUE_RAMP, shown):
        label = f"TD(0) after {episode} episode" + ("s" if episode > 1 else "")
        ax.plot(x, snapshots[episode], color=color, lw=2, zorder=4, label=label)
    ax.set_xticks(x, [str(s) for s in route], fontsize=7.5)
    ax.set_xlabel("state along the route of π₂ (start → goal)")
    ax.set_ylabel("estimate of V(s)")
    ax.set_xlim(-0.4, len(route) - 0.6)
    ax.set_ylim(-0.03, 1.05)
    ax.legend(loc="upper left", fontsize=8)
    ax.grid(axis="x", visible=False)
    save(fig, "td-reward-propagation.png", quick)


def band_plot(ax, runs, key, color, label, x_key="transitions"):
    x = np.array(runs[0][x_key])
    y = np.array([r[key] for r in runs])
    ax.fill_between(x, y.min(0), y.max(0), color=color, alpha=0.18, lw=0)
    ax.plot(x, y.mean(0), color=color, lw=2, label=label)
    return x, y.mean(0)


def fig_prediction_error(pred_det, pred_slip, quick):
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.9), sharey=True)
    learners = [("mc_mean", BLUE, "MC, sample mean"), ("mc_const", ORANGE, f"MC, α = {PRED_ALPHA}"),
                ("td", AQUA, f"TD(0), α = {PRED_ALPHA}")]
    for ax, pred, title in zip(axes, [pred_det, pred_slip], ["deterministic lake", "slippery lake"]):
        for key, color, label in learners:
            x, y = band_plot(ax, pred["runs"], key, color, label)
        ax.set_xscale("log")
        ax.set_title(title, loc="left")
        ax.set_xlabel("environment transitions (log scale)")
        ax.grid(axis="x", which="both", visible=False)
    axes[0].set_ylabel("RMS error of V over the 54 non-terminal states")
    axes[0].legend(loc="lower left", fontsize=8.5)
    fig.tight_layout()
    save(fig, "mc-td-prediction-error.png", quick)


def fig_slip(quick):
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.9), gridspec_kw={"width_ratios": [3, 2.95]})
    red = "#e34948"
    cases = [(9, (0, 3), (0, 3), False, "interior cell, action ↓"),
             (24, (2, 5), (0, 2), True, "cell at the left edge, action ↓")]
    for ax, (s, rows, cols, edge, title) in zip(axes, cases):
        ax.imshow(render_board(agent=s, facing=fl.DOWN), extent=(0, fl.N_COLS, fl.N_ROWS, 0))
        ax.set_xlim(cols[0] - (0.95 if edge else 0), cols[1])
        ax.set_ylim(rows[1], rows[0])
        ax.axis("off")
        ax.set_title(title, fontsize=9.5, loc="left")
        cx, cy = cell_xy(s)
        ax.add_patch(FancyArrowPatch((cx, cy + 0.3), (cx, cy + 0.92), arrowstyle="-|>", mutation_scale=13,
                                     color=BLUE, lw=2.4, zorder=5))
        ax.text(cx + 0.1, cy + 0.72, "0.75", ha="left", va="center", fontsize=9.5, color=INK, path_effects=HALO)
        ax.add_patch(FancyArrowPatch((cx + 0.3, cy), (cx + 0.92, cy), arrowstyle="-|>", mutation_scale=11,
                                     color=red, lw=1.8, zorder=5))
        ax.text(cx + 0.62, cy - 0.12, "0.125", ha="center", va="bottom", fontsize=9.5, color=INK, path_effects=HALO)
        if edge:  # the slip to the left is blocked by the edge
            ax.plot([0, 0], [rows[0], rows[1]], color=INK, lw=3)
            ax.add_patch(FancyArrowPatch((cx - 0.25, cy - 0.2), (cx - 0.25, cy + 0.2), connectionstyle="arc3,rad=1.4",
                                         arrowstyle="-|>", mutation_scale=10, color=red, lw=1.8, zorder=5))
            ax.text(-0.08, cy, "0.125:\nblocked,\nstays put", ha="right", va="center", fontsize=9, color=INK2)
            ax.text(-0.08, rows[0] + 0.25, "edge of\nthe lake", ha="right", va="top", fontsize=8.5, color=MUTED)
        else:
            ax.add_patch(FancyArrowPatch((cx - 0.3, cy), (cx - 0.92, cy), arrowstyle="-|>", mutation_scale=11,
                                         color=red, lw=1.8, zorder=5))
            ax.text(cx - 0.62, cy - 0.12, "0.125", ha="center", va="bottom", fontsize=9.5, color=INK, path_effects=HALO)
    fig.tight_layout()
    save(fig, "slip-directions.png", quick)


def fig_value_maps(quick):
    fig, axes = plt.subplots(2, 2, figsize=(9.2, 9.8))
    for i, policy in enumerate(["pi_2", "pi_1"]):
        for j, slippery in enumerate([False, True]):
            v = fl.exact_state_values(policy, slippery)
            show_board(axes[i, j], render_board(values=v, slippery=slippery))
            name = "π₂" if policy == "pi_2" else "π₁"
            world = "slippery" if slippery else "deterministic"
            axes[i, j].set_title(f"{name}, {world}:  V(0) = {v[0]:.3f}".replace("-", "−"), fontsize=10.5, loc="left")
    fig.tight_layout(h_pad=1.2, w_pad=1.0)
    save(fig, "value-maps-deterministic-vs-slippery.png", quick)


def fig_q_curve(qres, quick):
    fig, (ax, ax_v) = plt.subplots(2, 1, figsize=(7.6, 6.0), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
    keys = ("episode", "goal", "hole", "timeout", "exact_start_value")
    runs = [{k: [c[k] for c in r["curve"]] for k in keys} for r in qres["runs"]]
    eps_zero = qres["epsilon_start"] / qres["epsilon_decay"]
    for key, color, label in [("goal", BLUE, "reaches the goal"), ("hole", ORANGE, "falls into a hole"),
                              ("timeout", AQUA, f"still on the ice after {fl.MAX_STEPS} steps")]:
        x, y = band_plot(ax, runs, key, color, label, x_key="episode")
        ax.text(x[-1] + 150, y[-1], f"{y[-1]:.0%}", color=color, fontsize=8.5, va="center")
    opt = qres["optimal"]["exact_outcomes"]["goal"]
    ax.axhline(opt, color=INK, lw=1)
    ax.text(qres["n_episodes"], opt + 0.015, f"optimal policy: goal in {opt:.0%}", fontsize=8, color=INK,
            va="bottom", ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("fraction of greedy\nevaluation episodes")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.legend(loc="center right", fontsize=8.5, bbox_to_anchor=(1.0, 0.42))
    x, y = band_plot(ax_v, runs, "exact_start_value", BLUE, "greedy policy", x_key="episode")
    v_opt = qres["optimal"]["exact_start_value"]
    ax_v.axhline(v_opt, color=INK, lw=1)
    ax_v.text(qres["n_episodes"], v_opt + 0.004, f"optimal: $V^*(0)$ = {v_opt:.3f}", fontsize=8, color=INK,
              va="bottom", ha="right")
    ax_v.set_ylabel("exact value of the\ngreedy policy at the start")
    ax_v.set_xlabel("training episodes")
    for a in (ax, ax_v):
        a.grid(axis="x", visible=False)
        if eps_zero < qres["n_episodes"]:
            a.axvline(eps_zero, color=AXIS, lw=1)
    if eps_zero < qres["n_episodes"]:
        ax.text(eps_zero + 120, 0.97, "ε reaches 0", fontsize=8, color=MUTED, va="top")
    ax_v.set_xlim(0, qres["n_episodes"] + 1200)
    fig.tight_layout()
    save(fig, "q-learning-evaluation.png", quick)


def fig_q_policy(Q, q_star, highlight: tuple[int, ...], quick):
    """Learned and optimal Q-tables as the environment prints them; orange: greedy action differs."""
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 6.8))
    differ = np.flatnonzero(NONTERMINAL & (Q.argmax(1) != q_star.argmax(1)))
    titles = ["learned Q(s, a), first seed, after 15,000 episodes", "optimal Q*(s, a), computed from the transition table"]
    for ax, table, title in zip(axes, [Q, q_star], titles):
        show_board(ax, render_board(q=table, slippery=True))
        ax.set_title(title, fontsize=11, loc="left")
        for s in highlight:
            frame_cell(ax, s, INK, inset=-0.02, lw=3.0)
    for s in differ:
        frame_cell(axes[0], s, ORANGE, inset=0.02, lw=2.4)
    fig.tight_layout(w_pad=1.5)
    save(fig, "q-learning-policy.png", quick)


# ---------------------------------------------------------------------------
# Videos
# ---------------------------------------------------------------------------
def video_greedy(Q, quick, n_episodes=3, seed=40_000, fps=4):
    import imageio.v2 as imageio

    env = fl.make_lake(True, fl.MAX_STEPS, render_mode="rgb_array")
    rng = np.random.default_rng(seed)
    frames, outcomes = [], []
    env.reset(seed=seed)
    for _ in range(n_episodes):
        s, _ = env.reset()
        frames.append(env.render())
        terminated = truncated = False
        while not (terminated or truncated):
            s, r, terminated, truncated, _ = env.step(fl.greedy_action(Q[s], rng))
            frames.append(env.render())
        frames += [frames[-1]] * fps  # hold the final frame for a second
        outcomes.append("goal" if terminated and r > 0 else "hole" if terminated else "timeout")
    env.close()
    print("  greedy video episodes:", outcomes, "frames:", len(frames))
    if not quick:
        VIDEO.mkdir(parents=True, exist_ok=True)
        path = VIDEO / f"{SLUG}-greedy-slippery.mp4"
        imageio.mimsave(path, frames, fps=fps, codec="libx264", macro_block_size=16, quality=7)
        print("wrote", path.relative_to(ROOT))
    return outcomes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="cheap smoke run, nothing written to assets/")
    parser.add_argument("--img-dir", type=Path, help="with --quick: write the smoke-run figures here")
    args = parser.parse_args()
    quick = args.quick
    global QUICK_DIR
    QUICK_DIR = args.img_dir

    n_pred = 300 if quick else PRED_EPISODES
    seeds_pred = PRED_SEEDS[:2] if quick else PRED_SEEDS
    pred_det = cached_json("prediction_deterministic.json", lambda: run_prediction(False, n_pred, seeds_pred), quick)
    pred_slip = cached_json("prediction_slippery.json", lambda: run_prediction(True, n_pred, seeds_pred), quick)

    q_path = DATA / "q_learning_tables.npz"
    if not quick and q_path.exists() and (DATA / "q_learning.json").exists():
        qres = json.loads((DATA / "q_learning.json").read_text())
        tables = dict(np.load(q_path))
    else:
        qres, tables = run_q_learning(1_500 if quick else Q_EPISODES, Q_SEEDS[:2] if quick else Q_SEEDS,
                                      Q_EVAL_EVERY, 100 if quick else Q_EVAL_EPISODES,
                                      500 if quick else Q_FINAL_EVAL_EPISODES)
        if not quick:
            DATA.mkdir(exist_ok=True)
            (DATA / "q_learning.json").write_text(json.dumps(qres, indent=1))
            np.savez(q_path, **tables)

    fig_lake(quick)
    fig_route(quick)
    fig_update_timing(quick)
    fig_td_propagation(quick)
    fig_prediction_error(pred_det, pred_slip, quick)
    fig_slip(quick)
    fig_value_maps(quick)
    fig_q_curve(qres, quick)
    fig_q_policy(tables["seed0"], tables["q_star"], highlight=(47, 55), quick=quick)
    video_greedy(tables["seed0"], quick)
    if not quick:
        src = HERE / ".techdays26" / "artifacts" / "frozen_lake_elf.mp4"
        dst = VIDEO / f"{SLUG}-random-walk.mp4"
        shutil.copyfile(src, dst)
        print("wrote", dst.relative_to(ROOT), "(copied from techdays26/artifacts)")


if __name__ == "__main__":
    main()
