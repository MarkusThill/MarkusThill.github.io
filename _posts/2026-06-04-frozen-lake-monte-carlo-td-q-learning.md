---
layout: post
title: "Crossing the Frozen Lake&#58; Monte Carlo, TD(0) and Q-Learning"
modified: 2026-06-04T09:00:51+01:00
categories: [ML, programming]
description: "Monte Carlo, TD(0) and Q-learning on an 8×8 Frozen Lake that is small enough to inspect every learned value: how experience turns into state values, why slippery ice changes them, and how action values lead to a policy that crosses the lake."
tags: [reinforcement learning, temporal difference learning, Q-learning, Monte Carlo, frozen lake, Connect-4, AI, python]
thumbnail: assets/img/2026-06-04-frozen-lake-monte-carlo-td-q-learning/lake-map.png
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-06-04T09:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
series: connect4-rl
series_part: 3
---

{% include series_connect4_rl.liquid %}

Before an agent can learn Connect-4 from self-play, the central ideas of temporal difference learning
should be visible somewhere, and a game with trillions of positions is a poor place to look at them. In
this post I therefore use a world which is small enough to print its complete value table: the Frozen
Lake, a grid of $$8\times 8$$ cells in which an agent has to walk from the upper left corner to a goal in
the lower right corner without falling into one of the holes in the ice. With 64 cells and four possible
moves in each of them, every number the algorithms below learn fits into a single figure, so that we can
watch the estimates change and compare them with the exact values.

The question which runs through the whole post is how experience alone can tell us which decisions are
good. We first fix a way of behaving and estimate how good each cell is under it, once with the Monte
Carlo method, which waits for the outcome of an episode, and once with TD(0), which updates its estimate
after every single step. We then make the ice slippery, so that the same move can end in different cells,
and finally change the objective from evaluating a fixed behavior to improving it, which leads to
Q-learning. The returns and value functions of
{% include series_link.liquid series="connect4-rl" part=2 text="part 2" %} are recapped where they are
needed, so that the post can also be read on its own. All experiments run within minutes on an old laptop
CPU, and the code for each of them is linked at the end of the post.

<!--more-->

## Notation

Upper-case letters denote the random quantities of an episode and lower-case letters particular values,
following Sutton and Barto {% cite SuttonBarto18 --file thesis %}. Estimates which are learned from
experience are written without superscripts, e.g. $$V(s)$$, whereas $$V^\pi(s)$$ and $$V^*(s)$$ denote
the true values which they estimate.

| Symbol                 | Type             | Description                                                                                                                       |
| ---------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| $$s,\ s'$$             | state            | A cell of the lake, numbered row by row, $$s = 8\cdot\text{row}+\text{column}\in\{0,\dots,63\}$$; $$s'$$ denotes a successor state |
| $$a$$                  | action           | One of the four moves: 0 = left, 1 = down, 2 = right, 3 = up                                                                      |
| $$t,\ T$$              | time step        | $$t=0,1,\dots$$ counts the steps of an episode; the episode ends at step $$T$$                                                    |
| $$S_t,\ A_t$$          | random variables | State and action at time step $$t$$                                                                                               |
| $$R_{t+1}$$            | scalar           | Reward for the transition from $$S_t$$ to $$S_{t+1}$$: $$+1$$ for entering the goal, $$-1$$ for entering a hole, $$0$$ otherwise   |
| $$\gamma$$             | scalar           | Reward discount, $$\gamma=0.9$$ throughout the post                                                                               |
| $$G_t$$                | scalar           | Return: the discounted sum of the rewards from time step $$t$$ until the end of the episode                                       |
| $$\pi(a\mid s)$$       | probability      | Policy: the probability of choosing action $$a$$ in state $$s$$                                                                   |
| $$V^\pi(s)$$           | function         | State value: the expected return when starting in $$s$$ and following $$\pi$$                                                     |
| $$Q^\pi(s,a)$$         | function         | Action value: the expected return after taking $$a$$ in $$s$$ and following $$\pi$$ afterwards                                    |
| $$V^*(s),\ Q^*(s,a)$$  | function         | State and action values of an optimal policy                                                                                      |
| $$V(s),\ Q(s,a)$$      | table            | Current estimates, stored in a table with 64 or $$64\times 4$$ entries                                                            |
| $$N(s)$$               | counter          | Number of episodes in which state $$s$$ has been visited so far                                                                   |
| $$\alpha$$             | scalar           | Step size of an update                                                                                                            |
| $$d_t$$                | 0 or 1           | Termination flag: 1 if $$S_{t+1}$$ is a hole or the goal                                                                          |
| $$y_t,\ \delta_t$$     | scalar           | Target of a TD update and the TD error $$\delta_t = y_t - V(S_t)$$                                                                |
| $$\varepsilon$$        | probability      | Exploration rate of an $$\varepsilon$$-greedy policy                                                                              |

<br>

## The Frozen Lake Environment

The lake is shown in the next figure. The agent starts in cell 0 in the upper left corner and walks until
it enters either the goal in cell 63 or one of the nine holes, which ends the episode. A cell is identified
by a single number counted row by row from the top, so that cell $$s$$ lies in row $$\lfloor s/8\rfloor$$
and column $$s \bmod 8$$. The rewards belong to transitions rather than to cells: entering the goal yields
$$+1$$, entering a hole $$-1$$, and every other move $$0$$. A move against the edge of the lake leaves the
agent where it is. Since holes and goal end the episode, nothing can be earned after entering them, and
their own value is zero by definition.

{% include figure.liquid
   path="assets/img/2026-06-04-frozen-lake-monte-carlo-td-q-learning/lake-map.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="70%"
   caption="The 8×8 lake used throughout this post, as rendered by the environment, with the state number s = 8·row + column added to each cell. The agent starts in cell 0 in the upper left corner. Entering the goal in cell 63 earns +1, entering one of the nine holes earns −1, and both end the episode; every other move earns 0. The elf and the stool are from franuka's RPG snow tileset, all other tiles by Mel Tillery, as in Gymnasium's Frozen Lake."
%}

I use a slightly modified version of the Frozen Lake from the
[Gymnasium](https://gymnasium.farama.org/environments/toy_text/frozen_lake/) library, which my repository
[techdays26](https://github.com/MarkusThill/techdays26/blob/c18a0b5f3f2a3fdc48fec5c8872c698ac647dc49/src/techdays26/frozen_lake/frozen_lake_enhanced.py)
provides as `FrozenLakeEnv`. Three details differ from Gymnasium's standard 8×8 task and change the
learning problem, so they are worth stating explicitly: cell 42 is frozen instead of being a hole (nine holes
instead of ten), entering a hole costs $$-1$$ instead of nothing, and on slippery ice the agent moves in the
intended direction with probability 0.75 instead of 1/3. The ice is not slippery in the first half of the
post; we turn slipping on in the section on slippery ice. The following function creates the environment with
these parameters:

```python
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
```

The optional argument `max_steps` wraps the lake into Gymnasium's `TimeLimit`. I use a limit of 200 steps only
for the Q-learning agent and its evaluation, where we will see why cutting an episode off requires some care.
Otherwise, the interaction follows the usual Gymnasium pattern: `reset` places the agent on the start cell
and returns its state, and `step(action)` returns the next state, the reward, and the two flags `terminated`
(a hole or the goal was entered) and `truncated` (the time limit cut the episode off). The function
`run_episode` plays one episode with a given policy and records the visited states, actions and rewards, and
all algorithms in this post learn from such records:

```python
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
```

The environment can also render the lake, and it can print a state value or the four action values onto each
cell, in black for values near zero, turning red for negative and blue for positive values. All board figures
in this post are produced with this renderer. The next video shows an agent which moves uniformly at random; it
only illustrates states, moves and the ends of episodes, and nothing is learned in it.

{% include video.liquid
   path="assets/video/2026-06-04-frozen-lake-monte-carlo-td-q-learning-random-walk.mp4"
   class="img-fluid rounded z-depth-1 imgcenter" controls=true loop=true muted=true width="400"
   caption="The rendered lake with an agent which chooses its moves uniformly at random on the deterministic lake. Whenever it falls into a hole or reaches the goal, the episode ends and a new one starts in the upper left corner. The clip only illustrates states, moves and the ends of episodes; nothing is learned in it."
%}

#### Playing on the Lake Yourself

The repository techdays26 also contains an introductory Jupyter notebook,
[`lab1/0_frozen_lake_problem.ipynb`](https://github.com/MarkusThill/techdays26/blob/c18a0b5f3f2a3fdc48fec5c8872c698ac647dc49/lab1/0_frozen_lake_problem.ipynb),
which follows the same path as this post. In it, you can steer the agent across the lake with the arrow keys,
let the two policies below walk on it, and watch the estimates of Monte Carlo, TD(0) and Q-learning appear on
the cells while they are being learned. The notebook opens a Pygame window and waits for key presses, so it has
to run locally on a computer with a display; it does not work in Google Colab, which cannot show such a window.
It is meant as an interactive introduction: it renders every step, which makes the learning loops slow, and
its code is kept simpler than the code quoted in this post, from which all numbers here are computed. With
Python 3.11 or newer, the following commands set it up:

```bash
git clone https://github.com/MarkusThill/techdays26.git
cd techdays26
python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -e ".[lab1]" jupyterlab
jupyter lab lab1/0_frozen_lake_problem.ipynb
```

The Pygame window only reacts to keys while it has the focus. `Esc` ends a session, `P` pauses it, and the keys
`+` and `-` change the speed of the animation. For the longer training runs, `0` removes the speed limit
(including the short pause after each episode), and `9` additionally switches the drawing off.

<br>

## Policies, Returns and State Values

A policy $$\pi(a\mid s)$$ assigns a probability to each action in each state. I use two fixed policies in
this post. The first, $$\pi_1$$, ignores the state entirely and moves down or right with probability 0.45
each and left or up with probability 0.05 each, which is a random walk with a drift towards the goal. The
second, $$\pi_2$$, is deterministic: it moves right until it reaches the last column and then moves down.
On the deterministic lake, $$\pi_2$$ happens to follow a safe route along the upper and the right edge and
always reaches the goal after 14 steps, which makes it a transparent example for calculations by hand,
whereas the varied episodes of $$\pi_1$$ are more informative for the learning experiments. Both policies
receive a random number generator, since sampling from $$\pi_1$$ requires one; $$\pi_2$$ simply ignores it:

```python
PI_1 = np.array([0.05, 0.45, 0.45, 0.05])  # ← ↓ → ↑


def pi_1(state: int, rng: np.random.Generator) -> int:
    """Biased random walk: mostly down or right."""
    return int(rng.choice(N_ACTIONS, p=PI_1))


def pi_2(state: int, rng: np.random.Generator) -> int:
    """Right until the last column, then down."""
    return RIGHT if state % N_COLS < N_COLS - 1 else DOWN
```

The quantity which the agent should care about is the return, the discounted sum of all rewards from time
step $$t$$ until the episode ends at step $$T$$:

\begin{equation}
G_t = R_{t+1} + \gamma R_{t+2} + \gamma^2 R_{t+3} + \dots + \gamma^{T-t-1} R_T = R_{t+1} + \gamma G_{t+1}, \qquad G_T = 0.
\label{eq:return}
\end{equation}

The recursive form on the right is the one we will use in practice, since it allows us to compute all
returns of an episode in a single backward pass. The state value
$$V^\pi(s)=\mathbb{E}_\pi[G_t\mid S_t=s]$$ is the expected return when the agent starts in $$s$$ and follows
$$\pi$$ from there on. The expectation is needed because both the policy and, on slippery ice, the
environment can produce different episodes from the same state. It is worth stressing that a value always
belongs to a particular policy and a particular environment and not to a cell as such. Under $$\pi_2$$ on
the deterministic lake, for example, cell 16 has the value $$-0.81$$, because $$\pi_2$$ walks from there
straight into the hole at cell 19, although cell 16 is perfectly safe for a policy which moves down instead.

The next figure shows the route of $$\pi_2$$ together with the values of all states under $$\pi_2$$. Since the
lake and the policy are both deterministic, each of these values is simply the return of the single episode
which starts in that state, and along the route they are the returns observed from the start. The
last three transitions are 39 → 47 → 55 → 63 with the rewards 0, 0 and +1, so that equation
\eqref{eq:return} gives $$G = 1$$ in state 55, $$G = 0 + 0.9\cdot 1 = 0.9$$ in state 47, and
$$G = 0 + 0.9\cdot 0.9 = 0.81$$ in state 39. Continuing backwards, the return from the start is
$$0.9^{13}\approx 0.254$$, since the goal is worth less the further away it is. Note that the $$+1$$ is
attached to the transition into the goal and is therefore counted in the return of state 55, while the
goal itself has a continuation value of zero, since the episode is over as soon as it has been entered. A
transition into a hole works in the same way, with $$-1$$ instead of $$+1$$.

{% include figure.liquid
   path="assets/img/2026-06-04-frozen-lake-monte-carlo-td-q-learning/pi2-route-returns.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="70%"
   caption="State values of π₂ on the deterministic lake (γ = 0.9), printed onto the cells by the environment's renderer; the arrows mark the route of π₂ from the start in the upper left corner. Along the route, only the last transition, into the goal, is rewarded, and the values shrink by a factor of 0.9 per step of distance to the goal. From many cells in the lower rows, π₂ walks right into a hole, which gives them negative values."
%}

<br>

## Monte Carlo Prediction

The Monte Carlo method estimates $$V^\pi(s)$$ in the most direct way possible: it lets the agent follow
$$\pi$$, records the returns which are actually observed from each state, and averages them. After each
complete episode, the returns are computed backwards with equation \eqref{eq:return}, and the estimate of
every visited state is moved towards the return observed from it:

\begin{equation}
N(S_t) \leftarrow N(S_t) + 1, \qquad
V(S_t) \leftarrow V(S_t) + \frac{1}{N(S_t)}\,\bigl(G_t - V(S_t)\bigr).
\label{eq:mc}
\end{equation}

With the step $$1/N(S_t)$$, this is simply an incremental way of computing the sample mean: after $$n$$
updates, $$V(s)$$ is exactly the average of the $$n$$ returns observed from $$s$$. A state can, however, be
visited several times within one episode, for example when the agent bumps into the edge of the lake and
stays where it is. Consider the episode 39 → 39 → 47 → 55 → 63, in which the first move to the right is
blocked by the edge. State 39 is visited at $$t=0$$ and at $$t=1$$, with the returns
$$G_0 = 0.9^3 = 0.729$$ and $$G_1 = 0.9^2 = 0.81$$. The first-visit variant, which I use here, counts only
the return after the first visit, 0.729, so that each episode contributes at most one sample per state; the
every-visit variant would use both returns. The implementation therefore computes all returns backwards but
selects the first visits in chronological order. Collecting the states during the backward pass and
skipping those already seen would look very similar, but it would record the last visit (0.81) instead of
the first:

```python
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
```

The optional argument `alpha` replaces the step $$1/N(s)$$ by a constant, which we will need for a
comparison further below. For $$\pi_2$$ on the deterministic lake, a single episode is already sufficient:
every episode is the same, so the first one yields the exact values of all 14 states on the route. States
which are never visited keep their initial estimate of zero, and it is important not to read this zero as a
statement about the state, since it only means that nothing is known about it yet. For $$\pi_1$$, whose
episodes vary, the estimates converge to $$V^{\pi_1}$$ as the number of visits grows, and each observed
return is an unbiased sample of the quantity being estimated. The price is twofold. Nothing can be learned
before an episode has ended, and the individual returns vary considerably, since each of them depends on all
random decisions until the end of its episode.

<br>

## Temporal Difference Learning with TD(0)

Temporal difference learning {% cite Sutton88 --file thesis %} starts from a different observation.
Splitting the return into its first reward and the rest, $$G_t = R_{t+1} + \gamma G_{t+1}$$, and taking
expectations yields the Bellman equation of $$V^\pi$$,

\begin{equation}
V^\pi(s) = \mathbb{E}_\pi\bigl[R_{t+1} + \gamma V^\pi(S_{t+1}) \,\big|\, S_t = s\bigr],
\label{eq:bellman}
\end{equation}

which relates the value of a state to the values of its successors. TD(0) turns this relation into an
update rule: after each single transition from $$S_t$$ to $$S_{t+1}$$, the observed reward plus the
discounted current estimate of the next state serves as a sample of the right-hand side,

\begin{equation}
y_t = R_{t+1} + \gamma\,(1-d_t)\,V(S_{t+1}), \qquad
\delta_t = y_t - V(S_t), \qquad
V(S_t) \leftarrow V(S_t) + \alpha\,\delta_t.
\label{eq:td0}
\end{equation}

The target $$y_t$$ uses our own estimate $$V(S_{t+1})$$ in place of the rest of the return, which is called
bootstrapping. The flag $$d_t$$ is one if $$S_{t+1}$$ is a hole or the goal, so that the target then
consists of the reward alone. A zero-initialized table would give the same result without the flag, since
terminal entries are never updated, but the explicit flag keeps the update correct for any initialization.
The difference $$\delta_t$$ between the target and the current estimate is the TD error, and the step size
$$\alpha$$ determines how far the estimate moves towards the target:

```python
def td0_update(V, s, r, s_next, terminated: bool, alpha: float, gamma: float = GAMMA) -> float:
    """One TD(0) update after the transition s -> s_next with reward r."""
    target = r + gamma * (1.0 - terminated) * V[s_next]  # no bootstrap after termination
    delta = target - V[s]
    V[s] += alpha * delta
    return delta
```

Let us again follow $$\pi_2$$ on the deterministic lake, now with $$\alpha = 0.1$$ and all estimates
initialized to zero. During the first episode, every target is zero except the last one, so only the state
before the goal changes: $$V(55) = 0 + 0.1\cdot(1 - 0) = 0.1$$. In the second episode, the transition
47 → 55 has the target $$0 + 0.9\cdot 0.1 = 0.09$$, so that $$V(47)$$ becomes $$0.1\cdot 0.09 = 0.009$$,
and one step later $$V(55)$$ moves on to $$0.1 + 0.1\cdot(1 - 0.1) = 0.19$$. In contrast to Monte Carlo,
TD(0) has updated a state before the episode was over, but it has also learned much less from the same two
episodes, because the information about the goal travels backwards by only one state per episode. The next
figure contrasts the two update schemes.

{% include figure.liquid
   path="assets/img/2026-06-04-frozen-lake-monte-carlo-td-q-learning/mc-vs-td-update-timing.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="90%"
   caption="When the two methods update. Monte Carlo waits until the episode has ended and then moves the estimate of each visited state towards its observed return G_t. TD(0) updates the estimate of S_t right after the transition to S_{t+1}, using the reward R_{t+1} and the current estimate V(S_{t+1}). Earlier TD(0) updates are not revisited: when the reward R_4 is observed, only the estimate of S_3 benefits from it in this episode."
%}

How slowly this propagation proceeds on the route of $$\pi_2$$ is shown in the next figure. The start state,
14 transitions away from the goal, changes for the first time in episode 14, and then only to about
$$2.5\cdot10^{-15}$$, since the reward of the goal has been multiplied by $$\alpha$$ once for every state it
had to pass on its way back. Even with $$\alpha = 1$$, which copies each target into the table completely,
14 episodes would be required, one per state of the route. After 200 episodes the TD(0) estimates are close
to the exact values, which Monte Carlo had after a single episode. The route is the credit-assignment problem
of {% include series_link.liquid series="connect4-rl" part=2 text="part 2" %} in its most concrete form: only
the last of 14 decisions is rewarded directly, and TD(0) has to pass the credit back through all earlier
states, one per episode. This slow flow of information backwards along a trajectory is a well-known weakness
of one-step TD methods, and the eligibility traces of
{% include series_link.liquid series="connect4-rl" part=5 text="part 5" %} are one way to address it.

{% include figure.liquid
   path="assets/img/2026-06-04-frozen-lake-monte-carlo-td-q-learning/td-reward-propagation.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="90%"
   caption="Estimates of V(s) along the route of π₂ on the deterministic lake, after TD(0) with α = 0.1 has seen 1, 2, 5, 14, 50 and 200 identical episodes, compared with the Monte Carlo estimate after a single episode, which equals the exact values here. On this route, the reward of the goal travels backwards by one state per episode."
%}

#### Monte Carlo and TD(0) on the Same Experience

The deterministic example is extreme, so let us compare the two methods on the more varied episodes of
$$\pi_1$$. Both learners receive exactly the same complete episodes, and their errors are plotted against the
number of environment transitions (replaying a recorded episode gives the same TD(0) updates as learning during
it, because $$\pi_1$$ does not look at the estimates). The error is the root mean squared deviation over all
54 non-terminal states from the exact values $$V^{\pi_1}(s)$$, which can be computed from the transition table
of the environment (see the box below) but are never shown to the learners. All 54 states are reachable under
$$\pi_1$$, although the cells 56, 57 and 60 to 62 in the bottom row are visited in only about one percent of
the episodes or less.

One more variable has to be controlled. The sample mean in equation \eqref{eq:mc} uses the shrinking step
$$1/N(s)$$, whereas TD(0) is normally used with a constant step size, so a comparison of just these two
would mix the target (a complete return versus a bootstrapped one-step target) with the step-size rule. I
therefore add a third learner, Monte Carlo with the same constant step size $$\alpha=0.05$$ as TD(0). Each
run consists of 20,000 episodes (about 196,000 transitions on the deterministic lake and 236,000 on the
slippery one of the next section) and is repeated with five seeds.

{% include figure.liquid
   path="assets/img/2026-06-04-frozen-lake-monte-carlo-td-q-learning/mc-td-prediction-error.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="100%"
   caption="Root mean squared error of three learners of V^π₁ over the 54 non-terminal states, all fed with the same episodes of π₁, against the number of environment transitions (log scale). Left: deterministic lake; right: slippery lake. The lines show the mean over five seeds, the bands the range between the best and the worst seed. Monte Carlo with the sample mean uses the step 1/N(s); the other two learners use the constant step size α = 0.05."
%}

The result is instructive in both directions. At the same constant step size, Monte Carlo is ahead during
the first few thousand episodes. TD(0) starts from estimates which are all zero, and as we have seen, it
needs many visits before the information about holes and goal has travelled back to the states near the
start, so its early targets are built from estimates which are still uninformative. Later, however, the
ordering reverses. After roughly 4,500 episodes on the deterministic lake and 3,000 on the slippery one,
TD(0) has the lower average error, and it ends at 0.055 compared with 0.065 for Monte Carlo with a constant
step size (0.049 and 0.060 on slippery ice), although the ranges of the individual seeds still overlap. With
a constant step size, neither estimate ever settles exactly,
since every new target moves it by a fixed fraction. The remaining error therefore reflects how much the
targets vary, and the one-step targets of TD(0) vary less than complete returns, which accumulate the
randomness of all remaining steps of an episode. In the usual terms, the Monte Carlo target is unbiased but
has a high variance, whereas the TD target varies less but is biased as long as the estimate of the next
state is wrong, and the early and the late part of the curves show the two sides of this trade-off, which
{% include series_link.liquid series="connect4-rl" part=4 text="part 4" %} takes up again and
{% include series_link.liquid series="connect4-rl" part=5 text="part 5" %} turns into an adjustable dial.

The sample mean, finally, beats both of them over the whole run and ends at an error of 0.016 on the
deterministic lake and 0.025 on the slippery one. This is less an advantage of the Monte Carlo target than
one of the step-size rule: the step $$1/N(s)$$ weights all returns ever observed equally, so that the error
keeps shrinking, whereas a constant step size keeps forgetting old targets. The remaining error of the sample
mean sits mostly in the rarely visited bottom row, whose five cells account for between a quarter and almost
all of its final squared error, depending on the seed; for the two learners with a constant step size, the
error is spread over the whole lake. Forgetting is exactly what is
needed when the estimated quantity changes over time, which is the case as soon as the policy itself is being
improved; this is why constant step sizes are the usual choice for control methods such as Q-learning below.
Also, the comparison covers one small task, one policy and one step size, so it does not establish a general
ranking of the two methods. In the random-walk example of Sutton and Barto
{% cite SuttonBarto18 --file thesis %}, for instance, TD(0) is ahead of constant-step Monte Carlo over a
whole range of step sizes. In general, the advantages of bootstrapping show most clearly when episodes are
long or never end, and when the estimates of the next states are already reasonable.

<details markdown="1">
<summary>How the exact values were computed</summary>

The environment stores its complete transition model in the attribute `env.P`, which maps each state and
action to a list of tuples (probability, next state, reward, terminated). For a fixed policy, the Bellman
equation \eqref{eq:bellman} is a linear system with one equation per state,
$$\mathbf{v} = \mathbf{r}_\pi + \gamma\mathbf{P}_\pi\mathbf{v}$$, in which $$\mathbf{P}_\pi$$ contains the
probabilities of moving from one state to another under $$\pi$$ and $$\mathbf{r}_\pi$$ the expected immediate
rewards. The helper `model_arrays` reads $$\mathbf{P}$$ and $$\mathbf{r}$$ from `env.P` and removes all
transitions into holes and goal, since they contribute no continuation value, so that the system has a
unique solution:

```python
def policy_values(pi: np.ndarray, slippery: bool, gamma: float = GAMMA) -> np.ndarray:
    """Exact V for an arbitrary policy matrix pi(a|s)."""
    P, R = model_arrays(slippery)
    P_pi = np.einsum("sa,sat->st", pi, P)
    r_pi = (pi * R).sum(axis=1)
    return np.linalg.solve(np.eye(N_STATES) - gamma * P_pi, r_pi)
```

The same arrays are used for value iteration, which computes the optimal action values $$Q^*$$ in the last
part of the post, and for the probabilities of reaching the goal quoted below. None of these computations is
available to the learners.

</details>

<br>

## Slippery Ice

So far, every action had a single outcome. On slippery ice, the agent moves in the intended direction only
with probability 0.75 and slips into each of the two perpendicular directions with probability 0.125, as
shown in the next figure. A slip against the edge of the lake leaves the agent in place, so that near the
edges several outcomes can lead to the same cell. It is important to keep two sources of randomness apart
here: $$\pi_1$$ chooses its actions at random, and the slippery environment adds a second random step after
the action has been chosen. The reward definition, the discount and the algorithms remain exactly the same;
only the call `make_lake(slippery=True)` differs. The right half of the error figure above shows that the
three prediction learners behave as on the deterministic lake, although the rare states take longer to be
covered (all 54 states had been visited after 359 to 3,095 episodes, depending on the seed, compared with 99
to 851 episodes on the deterministic lake).

{% include figure.liquid
   path="assets/img/2026-06-04-frozen-lake-monte-carlo-td-q-learning/slip-directions.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="70%"
   caption="Transition probabilities on slippery ice for the action ↓. Left: in an interior cell, the agent moves down with probability 0.75 and slips to the left or to the right with probability 0.125 each. Right: at the left edge of the lake, the slip to the left is blocked, and the agent stays in its cell with probability 0.125."
%}

The next figure compares the exact values of both policies on the deterministic and on the slippery lake. The
route of $$\pi_2$$ collapses: its start value drops from 0.254 to $$-0.012$$,
and the probability of reaching the goal from the start falls from 1 to 0.63. The policy was never designed
for slipping. Each slip moves the agent off its route, and in most of the rows below, walking to the right
leads sooner or later into one of the holes. Even the cells directly below the former route therefore lose
most of their value, and the left half of them becomes negative. A single successful trajectory says little
about the expected value of a policy in a stochastic world.

{% include figure.liquid
   path="assets/img/2026-06-04-frozen-lake-monte-carlo-td-q-learning/value-maps-deterministic-vs-slippery.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="100%"
   caption="Exact state values of π₂ (top) and π₁ (bottom) on the deterministic lake (left) and the slippery lake (right), computed from the transition table and printed onto the cells by the environment's renderer (blue for positive, red for negative values). Holes and goal are terminal and have no value of their own. The precise route of π₂ loses most of its value on slippery ice, whereas the values of the random walk π₁ change comparably little."
%}

For $$\pi_1$$ the picture is different and, at first sight, surprising, since its start value even increases
from $$-0.426$$ to $$-0.374$$. Because $$\pi_1$$ chooses its actions independently of the state, the slip
merely changes the probabilities with which the four directions are actually taken, from (0.05, 0.45, 0.45,
0.05) to (0.1, 0.4, 0.4, 0.1). The left direction, for example, now results from choosing left and not
slipping, $$0.05\cdot 0.75$$, or from choosing down or up and slipping to the left,
$$0.45\cdot 0.125 + 0.05\cdot 0.125$$, which adds up to 0.1. Under $$\pi_1$$, the slippery lake is therefore
exactly equivalent to a deterministic lake with a slightly more hesitant random walk. This walk reaches the
goal less often than before (in 5.1% instead of 8.2% of the episodes, again computed from the transition
table), but it also takes longer on average (11.9 instead of 9.8 steps), so that the $$-1$$ of the hole which
ends most of its episodes is discounted more strongly. A higher value is therefore not the same as a higher
probability of success. The value measures the discounted reward, and with $$\gamma = 0.9$$ a late arrival is
worth less than an early one, whether the arrival is good or bad. We will meet this distinction again when we
evaluate the learned policy.

<br>

## From State Values to Action Values

The values of the previous sections evaluate a fixed policy. They tell us how good a state is if we continue
to behave in the same way, but not which action we should choose in it. From now on, the objective changes:
instead of estimating the consequences of a given behavior, we want to find a better one.

For this purpose, it is convenient to learn a value for each pair of state and action. The action value
$$Q^\pi(s,a)$$ is the expected return when the agent takes action $$a$$ in state $$s$$ and follows $$\pi$$
afterwards. The two kinds of values are related by

\begin{equation}
V^\pi(s) = \sum_a \pi(a\mid s)\,Q^\pi(s,a), \qquad V^*(s) = \max_a Q^*(s,a),
\label{eq:vq}
\end{equation}

where the second equation holds for the optimal values $$V^*$$ and $$Q^*$$, i.e. the largest values that
any policy can achieve. To choose an action with the help of state values alone, the agent would have to know
where each action leads, $$\arg\max_a \sum_{s'} p(s'\mid s,a)\,[r(s,a,s') + \gamma V(s')]$$, which requires the
transition probabilities $$p(s'\mid s,a)$$ of the environment. With action values, this comparison has
already been made, and the greedy action is simply $$\arg\max_a Q(s,a)$$. Our environment does in fact
expose its transition model as `env.P`, and I use it for the exact reference values, but the learning
algorithms in this post never look at it. Note also that state values are not useless for control in
general. If the immediate consequence of an action is known exactly, as it is for a move in a board game, the
agent can compare the values of the resulting positions directly. This is the afterstate idea on which the
Connect-4 agent of {% include series_link.liquid series="connect4-rl" part=7 text="part 7" %} is built.

State 47, which lies directly above cell 55 and to the right of the hole at cell 46, illustrates what action
values capture on slippery ice. Its optimal action values are $$Q^*(47,\downarrow) = 0.395$$,
$$Q^*(47,\rightarrow) = 0.382$$, $$Q^*(47,\uparrow) = 0.139$$ and $$Q^*(47,\leftarrow) = -0.634$$. Moving down
leads towards the goal, but a slip to the left drops the agent into the hole with probability 0.125. Moving
right pushes against the edge of the lake: the agent mostly stays where it is, and its slips lead up or down,
but never into a hole, so this move is completely safe but slow. With $$\gamma = 0.9$$, the faster and
riskier move is slightly better, and a single look at the four action values reveals this trade-off without
any knowledge of the slip probabilities.

<br>

## Q-Learning with an ε-greedy Behavior

Q-learning {% cite Watkins89 --file thesis %} learns action values with a TD update which looks almost like
equation \eqref{eq:td0}:

\begin{equation}
y_t = R_{t+1} + \gamma\,(1-d_t)\,\max_{a'} Q(S_{t+1},a'), \qquad
Q(S_t,A_t) \leftarrow Q(S_t,A_t) + \alpha\,\bigl[y_t - Q(S_t,A_t)\bigr].
\label{eq:qlearning}
\end{equation}

The maximum in the target means that the update bootstraps from the best action the agent currently knows in
the next state, regardless of the action it will actually take there. If every pair of state and action is
tried infinitely often and the step sizes decrease appropriately, $$Q$$ converges to $$Q^*$$
{% cite WatkinsDayan92 --file thesis %}. The first of these conditions points to the second ingredient of
the method: the agent has to explore. If it always chose the action which currently looks best, it would
never try the alternatives whose estimates are still zero, and it could settle on a mediocre route. The
standard remedy is an $$\varepsilon$$-greedy behavior, in which the agent picks a uniformly random action with
probability $$\varepsilon$$ and the greedy one otherwise. Ties between equal action values are broken at
random, which matters at the beginning, when all entries are zero and `np.argmax` would always return the
first action, left:

```python
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
```

The action which the agent actually takes next does not appear in the update at all; only the value of the
greedy action does. Q-learning therefore learns about the greedy policy while it behaves differently, which
is why it is called an off-policy method. This remains true if the $$\varepsilon$$-greedy behavior is
replaced by any other policy which explores sufficiently, for example by $$\pi_1$$: the target still
estimates $$Q^*$$ and not the action values of the behavior itself, which would require a different target.

The training loop applies this update for 15,000 episodes on the slippery lake, with $$\alpha = 0.1$$ and
$$\gamma = 0.9$$. The exploration rate starts at $$\varepsilon = 0.5$$ and decreases linearly by $$10^{-4}$$
per episode, so that it reaches zero after 5,000 episodes. During the remaining 10,000 episodes the agent
acts purely greedily and keeps learning from its own decisions and the randomness of the ice. These settings
are a working recipe for this particular task and not a choice which guarantees convergence:

```python
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
```

The environment passed to this loop is `make_lake(slippery=True, max_steps=200)`, and the limit of 200 steps
needs some care. An episode which reaches the limit has not really ended, since the agent is still standing
on the ice and the value of its state is not zero. The loop therefore starts a new episode when either flag
is set, but it suppresses the bootstrap only for `terminated` and never for `truncated`, as recommended in
Gymnasium's
[guide on time limits](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/). The
prediction experiments of the previous sections did not need a limit, since every recorded episode of
$$\pi_1$$ and $$\pi_2$$ ended in a hole or in the goal. One training run of 15,000 episodes took 64 seconds
on an Intel Core i7-3520M, a laptop CPU from 2012, measured without the intermediate evaluations described
next.

<br>

## Evaluation of the Learned Policy

A table of action values, however colorful, is no evidence that the agent can cross the lake. To evaluate
a learned table, I freeze it, switch off exploration, and let its greedy policy play on the same slippery lake
with separate random seeds, counting how each episode ends: in the goal, in a hole, or still on the ice after
200 steps. During training, this evaluation runs every 500 episodes with 1,000 evaluation episodes, and after
training each table is evaluated on 10,000 episodes. The whole training is repeated with five seeds. As a
reference, I compute the optimal action values $$Q^*$$ by value iteration from the transition table and
evaluate their greedy policy in the same way.

{% include figure.liquid
   path="assets/img/2026-06-04-frozen-lake-monte-carlo-td-q-learning/q-learning-evaluation.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="90%"
   caption="Evaluation of the greedy policy during Q-learning on the slippery lake, for five training seeds (lines: mean, bands: range over the seeds). Top: the fraction of 1,000 evaluation episodes, played without exploration and with separate seeds, which reach the goal, fall into a hole, or are still on the ice after 200 steps. Bottom: the exact expected discounted return of the same greedy policy from the start state, computed from the transition table. The black lines show the optimal policy, and the gray vertical line marks the episode in which ε reaches zero."
%}

After training, the five greedy policies reach the goal in 95.0% of their 10,000 evaluation episodes on
average (84.7% for the worst seed and 97.9% for the best one), they fall into a hole in 4.9%, and the time
limit ends only 0.1% of the episodes. While $$\varepsilon$$ is still positive, the greedy policy changes
considerably from one evaluation to the next, and the curves settle only after exploration has ended. The
comparison with the optimal policy is surprising at first: the optimal policy reaches the goal in only 73% of
its episodes and falls into a hole in the remaining 27%, so the learned policies succeed far more often than
the optimal one.

This is the distinction we met on slippery ice. The optimal policy maximizes the discounted return, and with
$$\gamma = 0.9$$ a goal which is reached in step 20 is worth $$0.9^{19}\approx 0.14$$ at the start, one which
is reached in step 46 less than 0.01. The optimal policy therefore takes rather direct routes and accepts the
risk of sideways slips, and its episodes last about 20 steps on average. Four of the five learned policies
instead prefer detours along the edges of the lake, where slips are harmless, and need about 46 steps on
average (the fifth one about 30). Measured by the objective which Q-learning is supposed to maximize, the
learned policies are clearly worse: the exact expected return from the start is 0.040 on average (between
0.035 and 0.056 for the individual seeds), compared with $$V^*(0) = 0.066$$ for the optimal policy. With a
discount closer to one, the optimal policy itself becomes cautious; for $$\gamma = 0.99$$, it reaches the goal
in 98.6% of the episodes, again computed from the transition table.

The reason for the detours can be read off the learned table of the first seed, which the next figure shows
next to the optimal action values. Its greedy actions differ from the optimal ones in 11 of the 54 states, and in the states 28, 43, 47 and 51 all
five tables deviate from the optimal policy. In state 55, directly above the goal, the learned table pushes
right against the edge and values the move down at only 0.149. This estimate is certainly too low, since the
move down reaches the goal with probability 0.75 and a hole with probability 0.125, which makes it worth more
than 0.5 whatever the agent does afterwards. Replaying the training run shows how the estimate got there.
When exploration ended after 5,000 episodes, the table valued the move down at 0.735, close to the optimal
0.704. The greedy agent kept taking it, 1,348 times in total, and reached the goal in three quarters of these
attempts, until it slipped into the hole at cell 54 in three consecutive episodes (6,697 to 6,699). With the
constant step size $$\alpha = 0.1$$, these three targets of $$-1$$ pulled the estimate below that of pushing
right. Q-learning only updates the action which is actually taken, and without exploration an action which
has fallen behind in this way is never tried again, so the estimate was never corrected. State 47 shows
the same pattern: the learned values for down and right, 0.078 and 0.225, reverse the ranking of the optimal
values 0.395 and 0.382. The recipe with a linearly decreasing $$\varepsilon$$ has therefore produced policies
which cross the lake reliably, but not optimal ones. Keeping a small amount of exploration, or exploring for
longer with decreasing step sizes, would be the natural candidates for an improvement, which I have not
measured here.

{% include figure.liquid
   path="assets/img/2026-06-04-frozen-lake-monte-carlo-td-q-learning/q-learning-policy.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="100%"
   caption="Left: the Q-table learned with the first seed after 15,000 episodes on the slippery lake. Right: the optimal action values Q*, computed from the transition table. The renderer prints the four action values of a cell at the side of the respective move (the value of ↓ at the bottom, and so on), readable from the centre of the cell, and it prints the largest one in bold. Orange frames mark the 11 states in which the learned greedy action differs from the optimal one, black frames the states 47 and 55 discussed in the text. In both states, the learned table prefers pushing right against the edge, and its estimates for the move down are far below the optimal values."
%}

The final video shows the first three evaluation episodes of the same table, played with a fixed evaluation
seed; the episodes were not selected. All three reach the goal, and the cautious behavior is easy to see: at
the lower end of the right column, the agent pushes against the edge and waits until a slip carries it
downwards.

{% include video.liquid
   path="assets/video/2026-06-04-frozen-lake-monte-carlo-td-q-learning-greedy-slippery.mp4"
   class="img-fluid rounded z-depth-1 imgcenter" controls=true loop=true muted=true width="400"
   caption="The first three evaluation episodes of the greedy policy learned with the first seed, played on slippery ice without exploration (evaluation seed 40,000; the episodes were not selected). After a slip, a blue arrow shows the intended direction and a red arrow the move which actually happened. All three episodes reach the goal; at the lower end of the right column, the agent pushes against the edge of the lake until a slip carries it downwards."
%}

<br>

## Summary and Outlook

The following table summarizes what the three methods of this post learn, which target they move their
estimates towards, and when they do so.

| Method      | Learns                                         | Target                                          | Update                           |
| ----------- | ---------------------------------------------- | ----------------------------------------------- | -------------------------------- |
| Monte Carlo | $$V^\pi$$ of a fixed policy                    | the observed return $$G_t$$                     | after the episode has ended      |
| TD(0)       | $$V^\pi$$ of a fixed policy                    | $$R_{t+1}+\gamma V(S_{t+1})$$                   | after every step                 |
| Q-learning  | $$Q^*$$, while behaving $$\varepsilon$$-greedily | $$R_{t+1}+\gamma \max_{a'} Q(S_{t+1},a')$$     | after every step                 |

Returning to the question from the beginning, experience tells us which decisions are good in two steps. For
a fixed behavior, the returns which actually follow a state estimate its value, either by waiting for them, as
Monte Carlo does, or by combining one observed reward with the current estimate of the next state, as TD(0)
does. To improve the behavior, it is more convenient to estimate the value of each action, and Q-learning does
so with the same kind of one-step target, while an exploring behavior makes sure that every action gets a
chance to be tried. Along the way, the small lake has also shown a few things which are easy to overlook in
larger problems: the value of a state belongs to a policy and an environment, a zero in a table may simply
mean that nothing is known yet, the step-size rule can matter as much as the target, and a higher value is
not the same as a higher probability of success.

Everything in this post relied on a table with one entry per state or per pair of state and action, which is
only possible because the lake has 64 cells. Connect-4, with about $$4.5\cdot 10^{12}$$ positions
{% cite Edelkamp08 --file thesis %}, rules out any such table, and the vast majority of its positions would
never be visited even once during training.
{% include series_link.liquid series="connect4-rl" part=4 text="The next part" %} therefore replaces the table
by a function with far fewer parameters than there are states, so that experience with one position can
inform the estimates of similar positions. The slow backward flow of rewards which we observed for TD(0)
returns in {% include series_link.liquid series="connect4-rl" part=5 text="part 5" %} together with its
remedy, eligibility traces, and parts 7 to 9 apply all of this to Connect-4, where the agent learns from games
against itself until it plays
{% include series_link.liquid series="connect4-rl" part=9 text="close to perfectly" %}.

<br>

## Source Code

- **Experiments, figures and videos of this post** — `tools/connect4_rl/` in the
  [source of this blog](https://github.com/MarkusThill/MarkusThill.github.io/tree/master/tools/connect4_rl).
  The module `frozen_lake_rl.py` contains every function quoted above, and `make_frozen_lake_figures.py`
  runs all experiments with fixed seeds and caches their results in `data/`.
- **The Frozen Lake environment** —
  [`frozen_lake_enhanced.py`](https://github.com/MarkusThill/techdays26/blob/c18a0b5f3f2a3fdc48fec5c8872c698ac647dc49/src/techdays26/frozen_lake/frozen_lake_enhanced.py)
  in the repository [techdays26](https://github.com/MarkusThill/techdays26), including the renderer which
  draws the lake and the values in the figures of this post.
- **Interactive notebook** —
  [`lab1/0_frozen_lake_problem.ipynb`](https://github.com/MarkusThill/techdays26/blob/c18a0b5f3f2a3fdc48fec5c8872c698ac647dc49/lab1/0_frozen_lake_problem.ipynb),
  to be run locally as described in the section on the environment.
- **Gymnasium** — [Frozen Lake documentation](https://gymnasium.farama.org/environments/toy_text/frozen_lake/)
  · [handling time limits](https://gymnasium.farama.org/tutorials/gymnasium_basics/handling_time_limits/)

<br>

## References

<div class="publications">
{% bibliography --file thesis --cited --group_by none %}
</div>

**Related posts:** [Building Intelligent Agents for Connect-4: First Steps]({% post_url 2026-01-01-connect-4-introduction-and-tree-search-algorithms %});
[Building Intelligent Agents for Connect-4: Final Considerations]({% post_url 2026-04-23-connect-4-final-considerations %}).
