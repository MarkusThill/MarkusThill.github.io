---
layout: post
title: "Near-Perfect Connect-4 after Five Minutes of Training&#58; Reinforcement Learning from Scratch by Self-Play"
modified: 2026-08-27T09:00:51+01:00
categories: [ML, programming]
description: "An n-tuple network learns Connect-4 from scratch by self-play on a single GPU and, after about five minutes of training, wins almost every game it starts against a perfect solver. Learning curves, results from both sides of the board, and how the training time was measured."
tags: [reinforcement learning, temporal difference learning, self-play, n-tuple networks, Connect-4, AI, python]
thumbnail: assets/img/2026-08-27-near-perfect-connect4-in-five-minutes/self-play-cartoon.webp
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-08-27T09:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
series: connect4-rl
series_part: 9
---

{% include series_connect4_rl.liquid %}

In the series on tree search, BitBully learned nothing and still played perfectly: it proves the value of
every position it is asked about by searching the game tree down to the end, supported by bit boards,
transposition tables and an opening book. This series took the opposite route. An agent starts with a value
function that knows nothing about Connect-4, plays against itself, and adjusts its estimates towards what
actually happened afterwards. The previous parts described the ingredients one by one; this post shows what
they add up to. After about five minutes of training on a single NVIDIA A100, the agent wins 94.6% of its games
against the perfect solver when it makes the first move, and 96.6% at the end of training, after about eight
and a half minutes.

These numbers come from ten independent training runs with the same recipe. Each run lets the agent play
50,000 games at once on the GPU and evaluates it every 1,000 training steps against a ladder of opponents,
from random moves over depth-limited searches up to BitBully at full strength. The training times quoted in
this post exclude these evaluations, which would otherwise inflate them considerably, and I describe further
below how the two were taken apart. The mechanics of the training loop are the subject of
{% include series_link.liquid series="connect4-rl" part=7 text="part 7" %} and
{% include series_link.liquid series="connect4-rl" part=8 text="part 8" %}; here the focus is on the results,
on what "near-perfect" means for the two sides of the board, and on how to play against the finished agent.

<!--more-->

## Notation

The following symbols are used in this post. Counts refer to the games of one evaluation unless stated
otherwise.

| Symbol                   | Type        | Description                                                                                                |
| ------------------------ | ----------- | ---------------------------------------------------------------------------------------------------------- |
| $$B$$                    | integer     | Number of boards played in parallel, $$B=50{,}000$$                                                        |
| $$t$$                    | integer     | Training step: one move on each of the $$B$$ boards, followed by one gradient step; $$t\le 25{,}000$$       |
| $$\varepsilon$$          | probability | Exploration rate of the learning agent during self-play, $$\varepsilon=0.1$$                               |
| $$\varepsilon_{\text{opp}}$$ | probability | Probability with which an evaluation opponent plays a random non-losing move instead of its search move |
| $$\lambda,\ n$$          | scalar      | Weighting and notebook truncation parameter of the truncated $$\lambda$$-return, $$\lambda=0.7$$, $$n=5$$             |
| $$\tau$$                 | scalar      | Coefficient of the exponential moving average which updates the target network, $$\tau=0.15$$             |
| $$W,\ D,\ L,\ N$$        | counts      | Wins, draws and losses of the learning agent, and the number of games $$N=W+D+L$$                         |
| $$W/N$$                  | rate        | Win rate, the headline measure of this post                                                                 |
| $$(W-L)/N$$              | score       | Score between $$-1$$ and $$+1$$; draws count zero                                                           |
| $$T_{\text{train}}$$     | seconds     | Training time without the evaluation pauses                                                               |

<br>

## The Result in Brief

The next figure shows how the agent's win rate against full-strength BitBully develops over the training
time when the agent moves first. Each thin line is one of the ten training runs, the thick line their mean.
The runs agree closely on the overall course. At the first evaluation, after 1,000 steps and 25 seconds of
training, the agents win 39% of their games on average, and after 4,000 steps, less than a minute and a half
into the training, the mean exceeds 90% for the first time. From then on it fluctuates between 89% and 98%,
more than the sampling noise of the evaluation games explains (about one percentage point for the mean over
ten runs of 50 games each), so the play of the agents still changes somewhat from one checkpoint to the next.
At step 13,000, the last evaluation which every run reached within five minutes of training, the mean win
rate is 94.6% (95% confidence interval 90.4–98.4%), and after all 25,000 steps, which took 8.6 minutes on an
NVIDIA A100 (8.6 to 8.8 minutes for the individual runs), it is 96.6% (94.2–98.4%). Three of the ten agents
won all fifty of their final games, and the weakest one won 44.

{% include figure.liquid
   path="assets/img/2026-08-27-near-perfect-connect4-in-five-minutes/learning-curve.png"
   alt="First-player win rate exceeds 90 percent within 1.5 minutes and reaches 94.6 percent by five minutes."
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="100%"
   caption="Win rate of the learning agent against full-strength BitBully when the agent moves first, over the training time without evaluations. Thin lines: the ten training runs, each evaluated with 50 games every 1,000 steps; thick line and band: their mean and a 95% bootstrap confidence interval. The vertical line marks five minutes of training; the annotation marks step 13,000, the last evaluation which all ten runs reached within five minutes."
%}

"Near-perfect" deserves a precise meaning here. Connect-4 is a first-player win: with perfect play, the side
which moves first wins, as the game-theoretic results summarized in
{% include series_link.liquid series="connect4-search" part=1 text="the first part of the search series" %}
show. Moving first against a perfect opponent is therefore the one situation in which a learned agent can be
measured against the ideal of winning every game. BitBully defends as well as possible and breaks ties
between equally good moves at random to vary the games. Every game the agent does not win is a game in
which it missed the winning line somewhere. Moving second, the same
opponent wins every game, whoever plays against it; the second-player results below therefore use opponents
which are weakened in controlled ways.

You can play against the agent selected for release right here; the appendix describes how it was
selected. In a separate evaluation, it won 91% of 200 games as the first player against perfect play and
drew the rest. The widget loads the agent's weights when you ask for
them (7.9 MB) and runs it entirely in the browser. It is a JavaScript transcription of the Python agent, and on
7,447 positions from self-play games it chose the same move as the original every single time. The numbers
below the board show how the agent scored each of its options before its last move.

<link rel="stylesheet" href="{{ '/assets/css/connect4-widgets.css' | relative_url }}" />

<div class="c4bb" data-c4-play data-weights="{{ '/assets/data/connect4-ntuple-agent.bin.gz' | relative_url }}" data-size="7.9 MB"></div>

<script src="{{ '/assets/js/connect4-core.js' | relative_url }}"></script>
<script src="{{ '/assets/js/connect4-ntuple.js' | relative_url }}"></script>
<script src="{{ '/assets/js/connect4-play.js' | relative_url }}"></script>

<br>

## What Was Trained

The agent is the one developed in the previous parts, and I only recapitulate it here. It estimates the value
of an **afterstate**, the position immediately after one of its own moves, and it chooses the move whose
afterstate it values most. The value function is an **n-tuple network**: 200 fixed patterns of eight board
cells each, whose contents (empty, yellow, red, or empty and reachable by the next move) form an index into a
table of $$4^8=65{,}536$$ weights. The network adds up the addressed weights of all patterns, once on the
board and once on its mirror image, and squashes the sum with $$\tanh$$:

\begin{equation}
V(s) = \tanh\Bigl(\sum_{m=1}^{200} \Bigl(W_{p,m}\bigl[T_m(s)\bigr] + W_{p,m}\bigl[T_m(\text{mirror}(s))\bigr]\Bigr)\Bigr),
\label{eq:ntuple}
\end{equation}

where $$T_m(s)$$ is the table index of pattern $$m$$ and $$p$$ the player to move, since each pattern has one
table per player. The value $$V(s)$$ is from Yellow's point of view. This gives
$$2\cdot 200\cdot 65{,}536 = 26{,}214{,}400$$ weights, of which, however, only about 8% can ever become non-zero: most combinations of eight cells cannot occur on a Connect-4 board because
of gravity, as the
[side post on realisable n-tuple states]({% post_url 2026-08-06-counting-realisable-ntuple-states %}) derives.

The agent learns by self-play on $$B=50{,}000$$ boards at once. In every training step, it makes one move on
each board, with probability $$\varepsilon=0.1$$ a random one, restarts the games which have ended, and
performs one gradient step. The targets are truncated $$\lambda$$-returns with $$\lambda=0.7$$ and the
notebook parameter $$n=5$$ ({% include series_link.liquid series="connect4-rl" part=5 text="part 5" %}). In this
implementation, the furthest bootstrap is $$n+1=6$$ moves ahead. The targets bootstrap from a target network
that follows the trained network as an exponential moving average with $$\tau=0.15$$ ({% include series_link.liquid series="connect4-rl" part=6 text="part 6" %}). Transitions after
exploratory moves are not used for updates unless they ended a game. The optimizer is Adam with a learning rate
of $$3\cdot10^{-4}$$ which decays slowly towards $$10^{-6}$$ (to about $$2.3\cdot10^{-4}$$ after 25,000 steps),
and gradients are clipped at a norm of 0.1. A training run consists of 25,000 steps, which amounts to about
1.25 billion moves and, estimated from the logged fraction of finished boards, about 42 million completed
games (41.0 to 42.2 million per run).

I call this combination of settings the recipe of this post. A section further below varies two of them, the
speed of the target network and the exploration, to show how much the results depend on them.

<br>

## How the Agent Is Evaluated

The opponents are BitBully configurations of increasing strength
({% include series_link.liquid series="connect4-search" part=9 text="search series, part 9" %}): searches
limited to a depth of 1, 2, 4 and 8 moves without an opening book, depths 8 and 10 with the 8-ply book, depth
16 with the 12-ply book, and BitBully at full strength with the 12-ply book with distances and unlimited depth,
which plays perfectly. All of them choose randomly among equally good moves, and a player making random moves
serves as a sanity check. Against full-strength BitBully, the evaluation additionally uses the values
$$\varepsilon_{\text{opp}}\in\{0.1, 0.2, 0.3\}$$: with this probability the opponent replaces its search move by
a random move which does not allow an immediate win of the other side. This is a mild form of weakening,
since even the random moves never walk into a loss in one move, and it is the "slightly weakened" opponent of
the second-player results below.

Every evaluation plays 50 games per opponent, side and $$\varepsilon_{\text{opp}}$$, with the learning agent
choosing its moves greedily, i.e. without exploration. The agent evaluated here also applies a one-move
tactical rule before consulting its network: it takes an immediately winning move if there is one, and it
avoids moves after which the opponent could win immediately. Everything beyond that single move comes from the
learned values. To score a move, the agent reverses the network value's sign when playing Red, multiplies
by 100 and truncates towards zero. I report the **win rate** $$W/N$$ and, where draws matter, the full distribution of wins,
draws and losses; the **score** $$(W-L)/N$$, which the training notebook logs, is not a win rate, since 95 wins
and 5 losses in 100 games give a win rate of 95% but a score of 0.90. Means over the ten runs come with a 95%
bootstrap confidence interval, obtained by resampling the runs; the games within one run describe that
particular agent and are not independent training runs. With 50 games, a single evaluation has a sampling
standard deviation of about three percentage points at a win rate of 95%, which accounts for much of the
jitter of the thin lines in the first figure.

<br>

## Moving First and Moving Second

The next figure shows the outcome of the final evaluations after 25,000 steps, pooled over the ten runs, so
that every bar represents 500 games. As the first player, the agents win between 93% and 98% of the games
against every search opponent, and against full-strength BitBully they win 483 of the 500 games, with 11 draws
and 6 losses. Somewhat surprisingly, the weakest searches are not the easiest opponents: against the
depth-2 and depth-8 searches without a book, the agents lose 31 and 26 of 500 games, more than against the
perfect player. A plausible explanation is that these searches choose moves which a strong player would not
make and which therefore lead into positions that self-play produced less often, but I have not examined this
further. As the second player, the agents win 88% to 98% of the games against all depth-limited searches up
to depth 10 with the 8-ply book, and against depth 16 with the 12-ply book they still win 291 of 500 games
(58%) and lose 203. Against full-strength BitBully, the agent loses every game as the second player, which is
what the theory of the game demands.

{% include figure.liquid
   path="assets/img/2026-08-27-near-perfect-connect4-in-five-minutes/final-outcomes.png"
   alt="Final outcomes: 96.6 percent wins against perfect play when moving first, and no wins when moving second."
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="100%"
   caption="Wins, draws and losses of the trained agents after 25,000 steps, pooled over the ten runs (500 games per bar), when the agent moves first (left) and second (right). The opponents are ordered from random moves to BitBully at full strength, which plays perfectly; against it, the second player cannot win."
%}

The second-player side becomes interesting when full-strength BitBully is allowed to err, which the next
figure shows as a function of $$\varepsilon_{\text{opp}}$$. With $$\varepsilon_{\text{opp}}=0.1$$, the agents
win 48.8% of the games as the second player, with 0.2 already 85.8%, and with 0.3 90.2%. An opponent that
replaces only one in ten of its moves by a random non-losing move therefore gives away about half of its
games against the trained agent, and one that does so for one move in five loses the large majority. As the
first player, the agents win between 95.8% and 99.2% of the games regardless of
$$\varepsilon_{\text{opp}}$$, which is expected: the opponent is on the losing side from the first move anyway,
and random moves only weaken its defence further.

{% include figure.liquid
   path="assets/img/2026-08-27-near-perfect-connect4-in-five-minutes/win-rate-vs-opponent-epsilon.png"
   alt="Second-player win rate rises from zero to 90.2 percent as the probability of a random opponent move increases to 0.3."
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="85%"
   caption="Win rate after training against full-strength BitBully, which replaces its search move by a random non-losing move with probability ε. Dots: the ten runs (50 games each), lines: their mean with a 95% bootstrap confidence interval."
%}

<br>

## What "Five Minutes" Includes

The notebook evaluates the agent every 1,000 steps, and each of these evaluations plays 1,200 games (50 per
opponent, side and $$\varepsilon_{\text{opp}}$$). An evaluation takes 20.7 seconds on average (16 to 24
seconds), and the 25 evaluations of a run add up to about half of its running time. The logger of the training
notebook does not measure them separately, but it writes two records at every evaluation step with times
relative to the same start: the training metrics immediately before the evaluation and the arena results
immediately after it. The difference between the two is the length of the evaluation pause, including the
logging and the time needed to copy and save the model between those timestamps. Subtracting all earlier pauses from the
elapsed time gives the training time at every step:

```python
def evaluation_pauses(rep: Repeat) -> dict[int, float]:
    """Duration (s) of every arena evaluation.

    At an evaluation step, the logger writes the metrics row first and runs the arena right
    afterwards; both rows carry the time elapsed since the same start. Their difference is
    the time for which training was paused.
    """
    t_metrics = {m["step"]: m["training_elapsed_s"] for m in rep.metrics}
    return {a["step"]: a["training_elapsed_s"] - t_metrics[a["step"]] for a in rep.arena}


def training_time(rep: Repeat) -> dict[int, float]:
    """Training-only time (s) at every evaluation step: elapsed time minus all earlier pauses."""
    t_metrics = {m["step"]: m["training_elapsed_s"] for m in rep.metrics}
    times, paused = {}, 0.0
    for step, pause in sorted(evaluation_pauses(rep).items()):
        times[step] = t_metrics[step] - paused
        paused += pause
    return times
```

By construction, the training time and all pauses of a run add up to the time of its last evaluation record.
The clock starts after model and optimizer initialization. The training time includes the compilation of
the network by `torch.compile` at the beginning, which makes the first 1,000 steps about four seconds slower
than the following ones, and the logging of metrics outside the evaluation pauses, and it excludes
installation, the evaluations and everything after the last training step. The next figure shows how the
17.3 minutes of a run (17.0 to 17.4 minutes) divide into training and evaluation.

{% include figure.liquid
   path="assets/img/2026-08-27-near-perfect-connect4-in-five-minutes/training-vs-evaluation-time.png"
   alt="Run durations split almost equally between training and evaluation pauses, each averaging 8.6 minutes."
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="85%"
   caption="Duration of the ten training runs on an NVIDIA A100, split into training (8.6 minutes on average) and the 25 evaluation pauses every 1,000 steps (8.6 minutes on average)."
%}

All runs used an NVIDIA A100 (SXM4, 40 GB) in Google Colab, which the training utilized only moderately; in my experience a
smaller GPU is sufficient as well, although I have not measured how much longer it takes. Five minutes are
therefore not a limit of the hardware but a statement about how quickly this recipe reaches near-perfect play.

<br>

## How Much Do the Settings Matter?

All training runs so far used the same settings, and it is fair to ask how much the results depend on them. Two
settings are natural candidates. The target network determines how quickly the targets follow what the agent has
just learned, and the exploration determines which positions the agent gets to see at all. I therefore trained
two variants of the recipe, ten runs each, with everything else unchanged. The first one updates its target
network three times more slowly, with $$\tau=0.05$$ instead of 0.15. The second keeps $$\tau=0.15$$ but
explores more at the beginning and less at the end: $$\varepsilon$$ decreases linearly from 0.2 to 0.02 over
the 25,000 steps, and its targets look further ahead, with $$\lambda=0.75$$ and $$n=8$$ (up to nine moves). Both variants ran on
the same type of GPU and were evaluated in the same way as the recipe; the appendix lists their settings. All
ten runs of every recipe enter the comparison. To reduce the noise of single evaluations of 50 games, the right
half of the next figure pools, for each run, the last five of its 25 evaluations, at steps 21,000 to 25,000,
i.e. 250 games per run and condition, or 2,500 per recipe and condition.

{% include figure.liquid
   path="assets/img/2026-08-27-near-perfect-connect4-in-five-minutes/recipe-comparison.png"
   alt="Three recipes reach similar first-player win rates; the decaying-exploration variant is weaker as the second player."
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="100%"
   caption="The recipe of this post compared with two variants, ten runs each. Left: mean win rate against full-strength BitBully when moving first, over the training time without evaluations, with 95% bootstrap confidence bands. Right: win rates at the end of training, pooling for each run its last five evaluations at steps 21,000 to 25,000 (250 games per run and condition); small dots are the ten individual runs, large dots their mean with a 95% bootstrap confidence interval. The colours are the same in both panels."
%}

The faster target network of the recipe gives the agents a head start. Averaged over the first five evaluations of each run,
at steps 1,000 to 5,000, which cover the first 1.8 minutes of training, the agents of the recipe win 73.7% of their games as the first player, and
those with $$\tau=0.05$$ win 66.6%; the difference of 7.1 percentage points has a 95% confidence interval from 2.0
to 12.2 points. Individual evaluations are noisier than this average: after 4,000 steps, the recipe is ahead with
93% against 78%, but after 3,000 steps the slower variant was slightly ahead. From step 5,000 on, the two curves
run side by side, and at the end of training the agents cannot be told apart. Both win about 96% of their games
as the first player, and the slower variant is even slightly ahead as the second player, for example against the
depth-16 search with 64% against 59%, with overlapping confidence intervals. Over all 22 conditions against
BitBully, the score $$(W-L)/N$$ of the last five evaluations, averaged over the ten runs, is 0.752 (0.740–0.764) for the recipe and 0.759
(0.751–0.766) for the slower variant. The larger $$\tau$$ thus buys a faster start rather than a stronger agent,
which is exactly what matters for a training time of a few minutes.

As the first player, the variant with decaying exploration ends at the same level, 96% against perfect play,
but it gets there later: at the first evaluation it is ahead, with 55% after 1,000 steps, then its mean stays around
70% until step 5,000 and exceeds 90% only after 8,000 steps, or 2.7 minutes. At the five-minute mark, all three
recipes win about 95% as the first player. As the second player, however, the variant is clearly weaker. Against
full-strength BitBully with $$\varepsilon_{\text{opp}}=0.1$$, 0.2 and 0.3 it wins 41%, 78% and 83% of the games,
where the recipe wins 48%, 85% and 89%, and its overall score is 0.719 (0.697–0.741). The runs also differ
more from each other: in the final evaluation alone, the overall score of the weakest run is 0.49. Since this
variant changes several settings at once, these runs alone do not show which of them is responsible.

Before the runs of this post, I had run 37 experiments with the same notebook in earlier sweeps, again with ten
runs each. They used earlier revisions of the code, and their evaluation lacked the weakened opponents,
so they are less precise than the comparison above, but they answer this question. In all eight comparisons of
a decaying with a constant exploration and otherwise identical settings, the decaying exploration made the agents
weaker as the second player, whereas a longer horizon of the targets alone made hardly any difference. For an
agent that is to play both sides, the constant $$\varepsilon=0.1$$ of the recipe is therefore the better choice.
Beyond that, the sweeps show a recipe that is robust within wide limits: $$\tau$$ between 0.05 and 0.25 and
gradient clipping at any norm between 0.1 and 1, or none at all, made no consistent difference to the final
level, and 100,000 instead of 50,000 boards did not make the agents stronger. The training reacted sensitively
only to the learning rate: with $$10^{-3}$$ instead of $$3\cdot10^{-4}$$, the agents became clearly weaker,
above all as the first player. The appendix summarises the sweeps.

All three recipes need about the same time for their 25,000 steps: 8.6, 8.5 and 8.4 minutes on average, so
the longer horizon of the targets does not make the training of the second variant noticeably slower.

Within the range tried here, the settings thus decide how quickly the agents become near-perfect first players
and how well they play the second side, but not whether they become near-perfect first players at all.

<br>

## Then and Now

The idea itself is not new. In 2012, we showed that temporal difference learning with n-tuple systems can
learn Connect-4 from self-play alone {% cite Thill12 ThillBA12 --file thesis %}, and in the following years I
added eligibility traces and step-size adaptation {% cite Thill14 ThillMA15 --file thesis %}. At that time, a
Java agent with 70 tuples needed between 350,000 and about 1.6 million training games to beat a Minimax
opponent in 80% of the evaluation games, which took between half an hour and 1.7 hours on a single core of a
laptop CPU, evaluations included, and it reached about 90–94% after ten million games
{% cite ThillMA15 --file thesis %}. The opponent was a
different one, and so was the evaluation protocol, so the win rates are not directly comparable. The agents
of that time processed about 12,000 to 16,000 games per minute; a training run of this post plays about
42 million games in 8.6 minutes, that is roughly 4.8 million per minute. The older timings include evaluations,
whereas the current training time excludes them, so this is only a rough throughput comparison. The difference
in throughput lies less in the algorithm than in playing tens of thousands of games at once on hardware
built for exactly this kind of parallel arithmetic.

<br>

## Playing Against the Agent

The agent in the widget above and in the release below is one of the ten trained agents. I chose it
with a separate tournament of 200 games per opponent, side and $$\varepsilon_{\text{opp}}$$, and then evaluated
it once more on fresh games, so that the choice does not inflate its results; the appendix describes the
selection and lists all its results. Moving first against perfect play, it won 182 of the 200 fresh games and
drew the other 18, without a single loss.

The weights of the selected agent are available from the release
[ntuple-agent-v1](https://github.com/MarkusThill/techdays26/releases/tag/ntuple-agent-v1) of techdays26, as a zip
archive (9.5 MB) with the file `connect4-ntuple-agent.pt` (105 MB unpacked, SHA-256
`b84b954820842b1f71983f91d1bac28cbe8fb652eeb4ea44afb1586eb6af8f1c`).
With techdays26 installed as described in its README (clone the repository and run `pip install -e .[lab2]` in
it), the agent runs on the CPU and plays against BitBully:

```python
from bitbully import BitBully, Board
from techdays26.td_agent import TDConnect4AgentTorch

agent = TDConnect4AgentTorch(model_path="connect4-ntuple-agent.pt")  # runs on the CPU

board = Board()  # empty board, Yellow (the first player) to move
print(agent.score_all_moves(board))  # score per legal column
print(agent.best_move(board))  # the agent's move

# Play a few moves against BitBully at full strength
bitbully = BitBully(opening_book="12-ply-dist")
for _ in range(4):
    board.play(agent.best_move(board))
    board.play(bitbully.best_move(board))
print(board)
```

On the empty board, the agent rates the centre column highest, with a score of 29, and the columns next to it
with −19. In a Jupyter notebook, BitBully's GUI lets you play against the agent yourself, or watch it play
against BitBully, as in the Lab 2 notebooks:

```python
%matplotlib ipympl
from bitbully.gui_c4 import GuiC4

agents = {"N-tuple agent": agent, "BitBully (perfect)": BitBully(opening_book="12-ply-dist")}
GuiC4(agents=agents, autoplay=True).get_widget()
```

The in-browser version near the beginning of this post is the same agent. Its weights file is small enough for a web
page because it stores only the 2,150,326 weights of states that can actually occur on a board, in an order
which the [side post on realisable n-tuple states]({% post_url 2026-08-06-counting-realisable-ntuple-states %})
derives.

<br>

## Limitations

The results describe one recipe, one set of 200 tuples and one board size, evaluated against one family of
opponents. Near-perfect is not perfect: as the first player the agents still draw 11 and lose 6 of 500 games
against full-strength BitBully, and the one-move tactical rule of the evaluated agent is a small piece
of built-in knowledge, although everything beyond a single move is learned. Fifty games per evaluation are
enough to follow the learning curve but leave a sampling uncertainty of a few percentage points per point,
which the ten runs average out only partly. Some depth-limited matchups also varied substantially between
evaluation sessions for the same agent, for reasons not yet examined; the selection appendix gives the details.
Finally, the n-tuple network is tailored to the $$7\times 6$$
board: its patterns, and with them all learned weights, would have to be recreated for a different board,
even though the training recipe itself would carry over.

<br>

## Source Code

- **Training notebook** — `lab2/1_train_ntuple_net.ipynb` in
  [techdays26](https://github.com/MarkusThill/techdays26/blob/c18a0b5f3f2a3fdc48fec5c8872c698ac647dc49/lab2/1_train_ntuple_net.ipynb),
  at the commit used for the runs of this post
- **Results of the training runs** — configuration, training metrics every 100 steps, all evaluation results
  as CSV files and the selection tournament, for the recipe and both variants, with a description of every column:
  [`assets/data/2026-08-27-near-perfect-connect4-in-five-minutes`](https://github.com/MarkusThill/MarkusThill.github.io/tree/master/assets/data/2026-08-27-near-perfect-connect4-in-five-minutes)
  in the source of this blog; all figures and numbers of this post are computed from these files
- **Raw output of the training runs** — the same results as written by the notebook, plus the text logs and the
  final weights of every run, in Google Drive folders:
  [recipe of this post](https://drive.google.com/drive/folders/1DlRfofqm-_Lw6pM9Wh518m_ZjbeiGfuY?usp=sharing),
  [slower target network](https://drive.google.com/drive/folders/1WDT20CJJlLN1gia7THRk3o9piUQPhIyq?usp=sharing),
  [decaying exploration](https://drive.google.com/drive/folders/1P9dSZbrMgoGBSHaQC4_Gs9uOTOU-SJm5?usp=sharing)
- **Analysis and figures of this post** — `tools/connect4_rl/connect4_results.py`,
  `make_connect4_results_figures.py`, `make_connect4_comparison_figures.py` and the selection tournament
  `select_strongest.py` in the
  [source of this blog](https://github.com/MarkusThill/MarkusThill.github.io/tree/master/tools/connect4_rl)
- **BitBully** — [GitHub](https://github.com/MarkusThill/BitBully)
  · [PyPI](https://pypi.org/project/bitbully/)

<br>

## Appendix: Settings of the Training Runs

All ten runs used the training notebook `lab2/1_train_ntuple_net.ipynb` of techdays26 at commit
[`c18a0b5`](https://github.com/MarkusThill/techdays26/tree/c18a0b5f3f2a3fdc48fec5c8872c698ac647dc49), started
one after another in the same Google Colab session. The runs share all settings and the same 200 tuples, and
differ only in the random numbers of self-play. The notebook logs its configuration together with the hardware
and the software versions (`params.json` in the results above):

| Hardware and software |                                                                                   |
| --------------------- | --------------------------------------------------------------------------------- |
| GPU                   | NVIDIA A100-SXM4-40GB (Google Colab)                                              |
| techdays26            | version 0.0.5, commit `c18a0b5`                                                   |
| Python, PyTorch       | 3.13.15, 2.11.0+cu128                                                             |
| BitBully              | as installed with techdays26 0.0.5 (0.0.75 or later; not logged, the latest release was 0.0.79) |
| Evaluation            | in parallel worker processes, one per CPU core of the Colab machine minus one      |

<br>

The settings of the notebook, with the names of its variables, are as follows. At this commit, the defaults
of the notebook differ from them in $$B=20{,}000$$ and $$\tau=0.05$$ and do not save the final weights; the
current version of the notebook uses the settings of this post as its defaults.

| Notebook variable                         | Value                  | Meaning                                                                                                   |
| ----------------------------------------- | ---------------------- | --------------------------------------------------------------------------------------------------------- |
| `n_steps`                                 | 25,000                 | Training steps per run; one move on every board and one gradient step                                     |
| `n_repeats`                               | 10                     | Independent runs with the same settings                                                                   |
| `B`                                       | 50,000                 | Boards played in parallel                                                                                 |
| `epsilon`                                 | 0.1                    | Probability of a random move on each board and in each step                                               |
| `use_non_losing`                          | `False`                | Self-play chooses among all legal moves, including those that allow an immediate loss                     |
| `lam`, `n_truncate`                       | 0.7, 5                 | Truncated $$\lambda$$-return; `n_truncate=5` gives a lookahead of up to six moves                                               |
| `use_target_net`, `tau`                   | `True`, 0.15           | Bootstrap values from a target network, updated as $$\theta^- \leftarrow (1-\tau)\,\theta^- + \tau\,\theta$$ |
| `use_online_net_for_action`               | `True`                 | The trained network, not the target network, chooses the self-play moves                                  |
| `lr_initial`, `lr_final`, `gamma`         | $$3\cdot10^{-4}$$, $$10^{-6}$$, 0.99999 | Learning rate $$\alpha_t = \alpha_{\text{final}} + (\alpha_{\text{initial}}-\alpha_{\text{final}})\,\gamma^t$$ after $$t$$ steps; $$2.34\cdot10^{-4}$$ at the end |
| `optimizer_betas`, `optimizer_eps`, `optimizer_weight_decay` | (0.9, 0.999), $$10^{-8}$$, 0 | Adam                                                                  |
| `use_gradient_clipping`, `gradient_clip_max_norm` | `True`, 0.1    | The gradient is clipped to a global L2 norm of 0.1                                                         |
| `use_torch_compile`                       | `True`                 | Network and target network are compiled with `torch.compile`                                              |
| `batch_afterstates`                       | automatic (`True` on the GPU) | The afterstates of all legal moves of all boards are evaluated in a single forward pass           |
| `n_evaluate`                              | 1,000                  | Evaluation every 1,000 steps                                                                              |
| `save_snapshot_steps`                     | [25,000]               | The weights are saved after the last step                                                                 |

<br>

The two variants in the section on how much the settings matter differ from these settings only as follows:

| Notebook variable | This post | Slower target network | Decaying exploration              |
| ----------------- | --------: | --------------------: | --------------------------------: |
| `tau`             | 0.15      | 0.05                  | 0.15                              |
| `epsilon`         | 0.1       | 0.1                   | 0.2, decreasing linearly to 0.02  |
| `lam`             | 0.7       | 0.7                   | 0.75                              |
| `n_truncate`      | 5         | 5                     | 8                                 |

<br>

For the decaying exploration, the training loop uses $$\varepsilon_t = 0.2 + (0.02-0.2)\,t/25{,}000$$ in step
$$t$$ instead of the constant `epsilon`, and the logged `epsilon` is the start value. The variants ran with
techdays26 commit [`2972567`](https://github.com/MarkusThill/techdays26/tree/29725676fb875802ee86e3f5685c6339af57414e),
which differs from `c18a0b5` only in the defaults of the notebook and in the package metadata, on the same GPU
type with the same software versions. Their results are in the subfolders `variant-slow-target` and
`variant-decaying-epsilon` of the results folder above.

The network consists of 200 tuples of eight cells, four states per cell, and two tables of 65,536 weights per
tuple, one for each player to move. Every tuple is also applied to the mirrored board, and the output is
squashed by $$\tanh$$; the training minimises the mean squared TD error. All weights start at zero.
The logged `total_params` in `params.json` counts only one player's tables (13,107,200); the network has
twice as many weights.

The evaluation plays 50 games per pairing, side and $$\varepsilon_{\text{opp}}$$, i.e. 1,200 games per
evaluation: 24 pairings of the learned agent, playing greedily, with the eight BitBully configurations and the
random player on either side, and with full-strength BitBully at $$\varepsilon_{\text{opp}}\in\{0.1,0.2,0.3\}$$
on either side. BitBully breaks ties between equally good moves at random in all configurations:

| Opponent                   | Search depth | Opening book                   |
| -------------------------- | -----------: | ------------------------------ |
| `bitbully-1ply` … `-8ply`  | 1, 2, 4, 8   | none                           |
| `bitbully-8-ply-book8ply`  | 8            | 8-ply                          |
| `bitbully-10-ply-book8ply` | 10           | 8-ply                          |
| `bitbully-16ply-book12ply` | 16           | 12-ply with distances          |
| `bitbully-full-strength`   | unlimited    | 12-ply with distances          |

<br>

Moves are limited to 4 seconds and the thinking time of a game to 45 seconds; both limits are checked after a
move, and exceeding one loses the game. This happened in 8 of the 300,000 evaluation games of the ten runs of
the recipe, and in 7 and 2 games of the two variants, all of them against full-strength BitBully with
$$\varepsilon_{\text{opp}}=0.1$$ or 0.3, in evaluations between steps 1,000 and 23,000; the logs do not record
which side exceeded the limit. None of these games belongs to the final evaluations or to the learning curves
against the unweakened opponent. Three of them, one per recipe, fall into the last five evaluations used for the
comparison of the recipes, where they change the pooled win rates by less than 0.05 percentage points. No game
was lost by an illegal move or an error.

<br>

## Appendix: Earlier Sweeps

Between April and July 2026, before the runs of this post, I ran 37 experiments with the training notebook in
several sweeps, each with ten runs and almost all with 25,000 steps; some of them repeat the same settings. They used earlier revisions of the code,
did not record the GPU, and their evaluation did not yet include the weakened opponents with
$$\varepsilon_{\text{opp}}>0$$. Their summary keeps only the final evaluation of every opponent and side, as
mean and standard deviation over the ten runs. Even the unchanged settings of that time, with 20,000 boards and
$$\tau=0.05$$, varied between sweeps: as the first player between 0.92 and 0.95 and as the second between 0.70
and 0.82, in terms of the mean score $$(W-L)/N$$ against the eight BitBully opponents as the first player and
against the seven depth-limited ones as the second player, since against perfect play the second player always
loses. Only comparisons with otherwise identical settings are therefore meaningful, and small differences should
not be over-interpreted. The next table lists the changes in these scores for the settings discussed in the main
text.

| Change, with all other settings equal                              | Comparisons | First player   | Second player  |
| ------------------------------------------------------------------ | ----------: | -------------: | -------------: |
| $$\varepsilon$$ decreasing linearly to 0.02 instead of constant 0.1 | 8           | −0.05 to 0.00  | −0.21 to −0.02 |
| Learning rate $$10^{-3}$$ instead of $$3\cdot10^{-4}$$             | 3           | −0.21 to −0.14 | −0.18 to 0.00  |
| $$\tau=0.10$$, 0.15 or 0.25 instead of 0.05                        | 3           | −0.01 to +0.01 | −0.03 to +0.01 |
| 100,000 instead of 50,000 boards                                   | 2           | −0.01 to +0.01 | −0.04 to −0.02 |
| $$\lambda=0.75$$, $$n=8$$ instead of 0.7 and 5                     | 1           | −0.01          | −0.01          |

<br>

The decaying exploration started at 0.2 in seven of the comparisons and at 0.1, decreasing to 0.01, in the
eighth. Gradient clipping at a norm of 0.25, 0.5 or 1.0, or no clipping at all, gave scores within the range of
the unchanged settings, and once slightly above it.

The sweeps were originally ranked by a different measure: the first-player score over all opponents, averaged
over all evaluations of a run. It rewards a fast start and ignores the second side, and by this measure settings
with decaying exploration rank among the best, although all of them are weaker second players. The comparison in
the main text therefore looks at both sides and at the end of training. The complete summary of the sweeps,
which also contains the runs of this post, is `earlier-sweeps.json` in the results folder above.

<br>

## Appendix: Selection of the Released Agent

The ten runs end with agents of similar, but not identical, strength, and 50 games per condition are too few
to rank them. To choose one agent for release, I therefore let each of the ten final agents play a larger
tournament with the same 24 conditions as the training evaluations (every opponent, both sides, and the
$$\varepsilon_{\text{opp}}$$ values against full-strength BitBully), but with 200 games per condition, i.e.
4,800 games per agent. The agents are ranked by their mean score $$(W-L)/N$$ over the 22 conditions against
BitBully, each condition with the same weight. The games against random moves are left out, since every agent
won all of them. The score counts a draw as better than a loss, and the average over both sides and all
opponents favours an agent that plays well everywhere over one that excels in a single matchup.

| Run       |     1 |     0 |     3 |     7 |     4 |     9 |     5 |     8 |     6 |     2 |
| --------- | ----: | ----: | ----: | ----: | ----: | ----: | ----: | ----: | ----: | ----: |
| Criterion | 0.793 | 0.791 | 0.777 | 0.772 | 0.770 | 0.769 | 0.758 | 0.750 | 0.737 | 0.736 |

<br>

Run 1 came out first, just ahead of run 0. Assuming independent games, the criterion of one agent has a
standard error of about 0.006, so these two cannot be told apart, and "strongest" here means the winner of this
tournament rather than an agent that is provably better than run 0. The spread over all ten agents, from 0.736
to 0.793, is larger than this noise, so the runs do end with agents of somewhat different strength. Choosing the
best of ten noisy measurements favours an agent that was lucky, so the selected agent then played the entire
tournament once more, on fresh games with a different seed. Its criterion on these games is 0.793 again, and
the selection has not inflated it noticeably. The evaluation setup does not explicitly seed BitBully's
separate tie-breaking generators. The next table shows its results on the fresh games.

| Opponent                              | Agent moves first: W / D / L | Agent moves second: W / D / L |
| ------------------------------------- | ---------------------------: | ----------------------------: |
| Random moves                          | 200 / 0 / 0                  | 200 / 0 / 0                   |
| Depth 1                               | 200 / 0 / 0                  | 192 / 4 / 4                   |
| Depth 2                               | 191 / 3 / 6                  | 192 / 8 / 0                   |
| Depth 4                               | 196 / 0 / 4                  | 162 / 0 / 38                  |
| Depth 8                               | 196 / 1 / 3                  | 194 / 0 / 6                   |
| Depth 8, 8-ply book                   | 196 / 1 / 3                  | 197 / 1 / 2                   |
| Depth 10, 8-ply book                  | 197 / 2 / 1                  | 197 / 2 / 1                   |
| Depth 16, 12-ply book                 | 194 / 4 / 2                  | 179 / 19 / 2                  |
| Full strength                         | 182 / 18 / 0                 | 0 / 0 / 200                   |
| Full strength, $$\varepsilon_{\text{opp}}=0.1$$ | 195 / 4 / 1        | 104 / 22 / 74                 |
| Full strength, $$\varepsilon_{\text{opp}}=0.2$$ | 197 / 1 / 2        | 144 / 16 / 40                 |
| Full strength, $$\varepsilon_{\text{opp}}=0.3$$ | 198 / 0 / 2        | 183 / 11 / 6                  |

<br>

Moving first against the perfect player, the selected agent did not lose any of the 200 games, and it won 182
of them (91%); the other 18 ended in a draw. This is below the 192 wins of the same agent in the selection
tournament, a difference at the edge of what the sampling noise of 200 games explains, and below the 96.6% of the
ten runs at the end of training. As the second player, the agent is remarkably strong against the depth-16 search
with the 12-ply book, which it beats in 179 of 200 games; in its last training evaluation it won 44 of 50 of
these games, whereas the ten runs together won only 58%. Among the depth-limited searches, on the other hand,
the depth-4 search is the most successful against it and wins 38 of 200 games as the first player. That result is less stable than the others: the same
agent lost 36 of 200 of these games in the selection tournament, but only 1 of 50 in its last training
evaluation, and between 1 and 16 of 200 in repetitions on my computer. The results against the depth-limited
searches evidently vary between evaluation sessions more than independent games would, and I have not
examined why. For the ranking above, this means that its standard error is, if anything, too optimistic.

<br>

## References

<div class="publications">
{% bibliography --file thesis --cited --group_by none %}
</div>
