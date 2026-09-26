"""
Tabular Monte Carlo, TD(0) and Q-learning on the 8x8 Frozen Lake.

This module holds the code quoted in the post "Crossing the Frozen Lake: Monte Carlo,
TD(0) and Q-Learning" (part 3 of the Connect-4 reinforcement-learning series). The
environment is the custom Frozen Lake of the techdays26 package; everything else is
plain NumPy, so that each update can be read line by line.

The learners only ever see sampled transitions. The transition table `env.P` is used
exclusively by the reference computations at the end of the module (exact policy
evaluation and value iteration), which serve to judge the learned estimates.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from gymnasium.wrappers import TimeLimit
from techdays26.frozen_lake.frozen_lake_enhanced import FrozenLakeEnv

N_ROWS, N_COLS = 8, 8
N_STATES, N_ACTIONS = N_ROWS * N_COLS, 4
LEFT, DOWN, RIGHT, UP = 0, 1, 2, 3
ARROWS = "←↓→↑"
GAMMA = 0.9  # reward discount
MAX_STEPS = 200  # rollout cap for interactive play, Q-learning and evaluation

Policy = Callable[[int, np.random.Generator], int]


# ---------------------------------------------------------------------------
# The task
# ---------------------------------------------------------------------------
def make_lake(slippery: bool, max_steps: int | None = None, render_mode=None):
    """The 8x8 lake with the task parameters used throughout the post."""
    env = FrozenLakeEnv(
        map_name="8x8",
        is_slippery=slippery,
        success_rate=0.75,  # intended direction; each perpendicular one gets 0.125
        reward_schedule=(1, -1, 0),  # (goal, hole, any other cell)
        render_mode=render_mode,
    )
    return env if max_steps is None else TimeLimit(env, max_episode_steps=max_steps)


def lake_map() -> list[str]:
    """The map as eight strings of S (start), F (frozen), H (hole) and G (goal)."""
    return ["".join(c.decode() for c in row) for row in make_lake(slippery=False).desc]


def terminal_states() -> np.ndarray:
    """Boolean mask of holes and goal."""
    desc = make_lake(slippery=False).desc.ravel()
    return np.isin(desc, [b"H", b"G"])


# ---------------------------------------------------------------------------
# Two fixed policies
# ---------------------------------------------------------------------------
PI_1 = np.array([0.05, 0.45, 0.45, 0.05])  # ← ↓ → ↑


def pi_1(state: int, rng: np.random.Generator) -> int:
    """Biased random walk: mostly down or right."""
    return int(rng.choice(N_ACTIONS, p=PI_1))


def pi_2(state: int, rng: np.random.Generator) -> int:
    """Right until the last column, then down."""
    return RIGHT if state % N_COLS < N_COLS - 1 else DOWN


def policy_matrix(policy: str) -> np.ndarray:
    """pi(a|s) as a (64, 4) array, for the reference computations."""
    if policy == "pi_1":
        return np.tile(PI_1, (N_STATES, 1))
    pi = np.zeros((N_STATES, N_ACTIONS))
    for s in range(N_STATES):
        pi[s, RIGHT if s % N_COLS < N_COLS - 1 else DOWN] = 1.0
    return pi


# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------
def run_episode(env, policy: Policy, rng: np.random.Generator, seed: int | None = None):
    """Play one episode; return the lists S_0..S_T, A_0..A_{T-1}, R_1..R_T."""
    state, _ = env.reset(seed=seed)
    states, actions, rewards = [state], [], []
    terminated = truncated = False
    while not (terminated or truncated):
        action = policy(state, rng)
        state, reward, terminated, truncated, _ = env.step(action)
        states.append(state)
        actions.append(action)
        rewards.append(float(reward))
    return states, actions, rewards, terminated


# ---------------------------------------------------------------------------
# Monte Carlo prediction
# ---------------------------------------------------------------------------
def returns(rewards: list[float], gamma: float = GAMMA) -> np.ndarray:
    """G_t = R_{t+1} + gamma * G_{t+1}, computed backwards from the end."""
    G = np.zeros(len(rewards))
    g = 0.0
    for t in reversed(range(len(rewards))):
        g = rewards[t] + gamma * g
        G[t] = g
    return G


def mc_first_visit_update(V, N, states, rewards, alpha: float | None = None, gamma: float = GAMMA) -> None:
    """One first-visit Monte Carlo update from a complete episode.

    With alpha=None, V(s) is the running mean of the returns observed in s (step 1/N(s));
    otherwise V(s) moves a constant fraction alpha towards each new return.
    """
    G = returns(rewards, gamma)
    seen = set()
    for t in range(len(rewards)):  # chronological order: first visits come first
        s = states[t]
        if s in seen:
            continue
        seen.add(s)
        N[s] += 1
        step = 1.0 / N[s] if alpha is None else alpha
        V[s] += step * (G[t] - V[s])


# ---------------------------------------------------------------------------
# TD(0) prediction
# ---------------------------------------------------------------------------
def td0_update(V, s, r, s_next, terminated: bool, alpha: float, gamma: float = GAMMA) -> float:
    """One TD(0) update after the transition s -> s_next with reward r."""
    target = r + gamma * (1.0 - terminated) * V[s_next]  # no bootstrap after termination
    delta = target - V[s]
    V[s] += alpha * delta
    return delta


def td0_episode(V, states, rewards, terminated: bool, alpha: float, gamma: float = GAMMA) -> None:
    """Replay a recorded episode transition by transition, in the order it happened."""
    T = len(rewards)
    for t in range(T):
        done = terminated and t == T - 1
        td0_update(V, states[t], rewards[t], states[t + 1], done, alpha, gamma)


# ---------------------------------------------------------------------------
# Q-learning
# ---------------------------------------------------------------------------
def greedy_action(q_row: np.ndarray, rng: np.random.Generator) -> int:
    """argmax with random tie-breaking (np.argmax would always prefer 'left')."""
    best = np.flatnonzero(q_row == q_row.max())
    return int(rng.choice(best))


def epsilon_greedy(Q, state: int, epsilon: float, rng: np.random.Generator) -> int:
    if rng.random() < epsilon:
        return int(rng.integers(N_ACTIONS))
    return greedy_action(Q[state], rng)


def q_learning_update(Q, s, a, r, s_next, terminated: bool, alpha: float, gamma: float = GAMMA) -> None:
    target = r + gamma * (1.0 - terminated) * Q[s_next].max()
    Q[s, a] += alpha * (target - Q[s, a])


def q_learning(
    env,
    n_episodes: int,
    rng: np.random.Generator,
    alpha: float = 0.1,
    gamma: float = GAMMA,
    epsilon_start: float = 0.5,
    epsilon_decay: float = 1e-4,
    seed: int | None = None,
    callback: Callable[[int, np.ndarray], None] | None = None,
) -> np.ndarray:
    """Tabular Q-learning with a linearly decaying epsilon-greedy behaviour policy."""
    Q = np.zeros((N_STATES, N_ACTIONS))
    epsilon = epsilon_start
    env.reset(seed=seed)
    for episode in range(n_episodes):
        s, _ = env.reset()
        terminated = truncated = False
        while not (terminated or truncated):
            a = epsilon_greedy(Q, s, epsilon, rng)
            s_next, r, terminated, truncated, _ = env.step(a)
            q_learning_update(Q, s, a, r, s_next, terminated, alpha, gamma)
            s = s_next  # a truncated episode is reset, but its last target still bootstraps
        epsilon = max(epsilon - epsilon_decay, 0.0)
        if callback is not None:
            callback(episode + 1, Q)
    return Q


def evaluate_greedy(Q, env, n_episodes: int, seed: int, rng: np.random.Generator) -> dict:
    """Freeze Q and follow its greedy policy; count goal, hole and timeout endings."""
    counts = {"goal": 0, "hole": 0, "timeout": 0}
    returns_ = []
    env.reset(seed=seed)
    for _ in range(n_episodes):
        s, _ = env.reset()
        terminated = truncated = False
        g, discount = 0.0, 1.0
        while not (terminated or truncated):
            s, r, terminated, truncated, _ = env.step(greedy_action(Q[s], rng))
            g += discount * r
            discount *= GAMMA
        returns_.append(g)
        if terminated:
            counts["goal" if r > 0 else "hole"] += 1
        else:
            counts["timeout"] += 1
    return {k: v / n_episodes for k, v in counts.items()} | {"mean_return": float(np.mean(returns_))}


# ---------------------------------------------------------------------------
# Reference computations (use the model env.P; never called by the learners)
# ---------------------------------------------------------------------------
def transition_table(slippery: bool):
    """Transition probabilities P[s, a, s'] and expected rewards R[s, a], read from env.P.

    In env.P, holes and goal loop onto themselves with reward 0.
    """
    env = make_lake(slippery)
    P = np.zeros((N_STATES, N_ACTIONS, N_STATES))
    R = np.zeros((N_STATES, N_ACTIONS))
    for s in range(N_STATES):
        for a in range(N_ACTIONS):
            for p, s_next, r, _ in env.P[s][a]:
                P[s, a, s_next] += p
                R[s, a] += p * r
    return P, R


def model_arrays(slippery: bool):
    """P and R for value computations: entering a hole or the goal ends the return."""
    P, R = transition_table(slippery)
    terminal = terminal_states()
    P[terminal] = 0.0
    R[terminal] = 0.0
    P[:, :, terminal] = 0.0
    return P, R


def exact_state_values(policy: str, slippery: bool, gamma: float = GAMMA) -> np.ndarray:
    """Solve V = r_pi + gamma * P_pi V for one of the two fixed policies."""
    return policy_values(policy_matrix(policy), slippery, gamma)


def optimal_action_values(slippery: bool, gamma: float = GAMMA, tol: float = 1e-12) -> np.ndarray:
    """Value iteration for Q*."""
    P, R = model_arrays(slippery)
    Q = np.zeros((N_STATES, N_ACTIONS))
    while True:
        Q_new = R + gamma * P @ Q.max(axis=1)
        if np.abs(Q_new - Q).max() < tol:
            return Q_new
        Q = Q_new


def greedy_policy_matrix(Q) -> np.ndarray:
    """pi(a|s) of the greedy policy of Q, with ties broken uniformly at random."""
    best = Q == Q.max(axis=1, keepdims=True)
    return best / best.sum(axis=1, keepdims=True)


def outcome_probabilities(pi: np.ndarray, slippery: bool, horizon: int = MAX_STEPS, start: int = 0) -> dict:
    """Exact probabilities of ending in the goal / a hole / still on the ice after `horizon` steps."""
    P, _ = transition_table(slippery)  # holes and goal are absorbing here
    P_pi = np.einsum("sa,sat->st", pi, P)
    d = np.zeros(N_STATES)
    d[start] = 1.0
    for _ in range(horizon):
        d = d @ P_pi
    terminal = terminal_states()
    goal = d[N_STATES - 1]
    hole = d[terminal].sum() - goal
    return {"goal": float(goal), "hole": float(hole), "timeout": float(1.0 - goal - hole)}


def policy_values(pi: np.ndarray, slippery: bool, gamma: float = GAMMA) -> np.ndarray:
    """Exact V for an arbitrary policy matrix pi(a|s)."""
    P, R = model_arrays(slippery)
    P_pi = np.einsum("sa,sat->st", pi, P)
    r_pi = (pi * R).sum(axis=1)
    return np.linalg.solve(np.eye(N_STATES) - gamma * P_pi, r_pi)
