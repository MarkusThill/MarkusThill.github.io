---
layout: post
title: "Building Intelligent Agents for Connect-4&#58; MTD(f) and Null-Window Search"
modified: 2026-07-14T09:00:51+01:00
categories: [programming]
description: "How a distance-aware score supplies game-derived bounds, and how MTD(f) and a binary null-window driver reconstruct exact values from narrow alpha-beta probes."
tags: [Connect-4, AI, tree-search, alpha-beta, minimax, mtdf, null-window, transposition tables, opening databases, move ordering, bitboards]
thumbnail: assets/img/project_bitbully/c4-2.png
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-03-26T09:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
series: connect4-search
series_part: 7
---

{% include series_connect4.liquid %}

Part 2 introduced the alpha-beta search as a recursive function which takes a window
$$[\alpha, \beta]$$, but it quietly left two questions unanswered. The first is which window
should be used at the root, where nothing is known yet. The second is what exactly the number
returned by the search is supposed to mean, since a win is a win and it is not obvious why one
win should be worth more than another.

<!--more-->

As it turns out, both questions have the same answer, and getting it right makes a
considerable difference between a solver which merely works and one which is fast. This is also
the part which the 2012 engine never really solved.

<br>

## Choosing a meaningful Score Convention

The naive convention assigns $$+1$$ for a win, $$0$$ for a draw and $$-1$$ for a loss. It is
correct and sufficient for determining the game-theoretic outcome, but it is limited in
practice for two reasons.

The first one is rather practical. From the empty standard board, the first player can force a
win under perfect play, so an agent which only knows that it wins has no way of choosing between
winning immediately and winning in twenty moves. Much worse, a losing agent has no way of
preferring to lose slowly. This matters more than one might think: against a fallible opponent,
a long resistance is an opportunity to be handed a mistake, whereas an immediate defeat is not.
The 8-ply database of the previous post has exactly this weakness, which is why the 12-ply one
stores distances as well.

The second reason is the more interesting one. BitBully scores a position as

$$
\text{score} = \pm\left(\left\lfloor \frac{\text{movesLeft}}{2} \right\rfloor + 1\right)
$$

where `movesLeft` denotes the number of cells still unoccupied at the moment the game ends,
that is, the number of moves by which the game finishes early. The sign gives the outcome and
the magnitude gives the speed, and since a faster win
corresponds to a larger number, the ordinary logic of maximizing the score prefers quick wins
and slow losses without any special cases.

Reading the value back out is a small parity puzzle, since whether the winning token falls on
an even or an odd ply depends on who is to move:

```cpp
static int scoreToMovesLeft(const int score, const Board& b) noexcept {
  if (score == 0) return b.movesLeft();                 // draw: board fills up
  const int p = (b.movesLeft() + 1) % 2;                // whose turn is it
  const int sgnScore = score < 0 ? 1 : 0;
  const int absScore = score < 0 ? -score : score;
  const int mvFinalLeft = 2 * (absScore - 1) + (sgnScore ^ p);
  return b.movesLeft() - mvFinalLeft;
}
```

The expression `sgnScore ^ p` is the essential part here, since an XOR of the two parities
decides whether the additional ply has to be added or not.

<br>

## Bounds which the Game itself provides

The actual benefit of this convention goes considerably beyond the convenience of the scoring
itself. Since the score is derived from `movesLeft`, the position bounds its own value before a
single move has been generated. The player to move cannot win sooner than the next move and
cannot lose sooner than the opponent's following reply:

$$
-\left\lfloor \frac{\text{movesLeft}}{2} \right\rfloor
\;\le\; \text{score} \;\le\;
\left\lfloor \frac{\text{movesLeft} + 1}{2} \right\rfloor
$$

The upper endpoint corresponds to an immediate win. BitBully checks that case separately at the
root; once it has been ruled out, the earliest remaining win is on the player's following turn,
which tightens the upper bound to
$$\left\lfloor(\text{movesLeft} - 1) / 2\right\rfloor$$. With this precondition, the search can
intersect the tighter bounds with its incoming window, and sometimes the window closes on the
spot:

```cpp
if (!depth && b.canWin()) {
  return (b.movesLeft() + 1) / 2;
}

if (alpha >= (b.movesLeft() + 1) / 2) {
  // We cannot do better than alpha any more: every extra move played
  // means a later win, which means a lower score.
  return alpha;
}

// The opponent cannot win on the next move, so the score has a floor:
if (const int min = -b.movesLeft() / 2; alpha < min) {
  alpha = min;
  if (alpha >= beta) return alpha;
}
if (const int max = (b.movesLeft() - 1) / 2; beta > max) {
  beta = max;
  if (alpha >= beta) return beta;
}
```

After the immediate-win check, the bound clamps require only three comparisons without any move
generation and without any recursion, and they produce a cutoff whenever the incoming
expectations already lie outside what the position can possibly deliver. This is pruning which
is derived purely from the shape of the game, and it is only available because the score
actually means something. With a convention of $$\{-1, 0, +1\}$$ there would be no similarly
useful distance-dependent tightening of the bounds.

<br>

## Pruning with Narrow Windows

We now come to the driver itself. The relationship which can be exploited here is quite simple:
the narrower the window, the more the alpha-beta search prunes. A wide window forces the search
to determine an exact value, whereas a narrow one allows it to stop as soon as it knows that
the value lies outside.

If this idea is pushed to its limit, one arrives at the null window, which is also called a
zero-width or scout window, where $$\beta = \alpha + 1$$. Since the scores are integers, no
value can lie strictly between the two bounds, so a single probe cannot establish exactness
from its window alone. A fail-soft implementation may happen to return the exact score
numerically (and may find an exact transposition-table entry), but the probe itself only
establishes on which side of the boundary the truth lies:

- returns $$\le \alpha$$ → the true score is **at most** $$\alpha$$
- returns $$> \alpha$$ → the true score is **at least** $$\alpha + 1$$

This turns the question of what the value is into a simple yes/no question, and it is
considerably cheaper, since every node receives the tightest possible window from above.

At first glance this looks like a bad trade, since we wanted a number and obtained a single
bit. The essential insight is that the number can be reconstructed from a handful of such
bits.

<br>

## The MTD(f) Driver

The MTD(f) algorithm {% cite Plaat94 --file thesis %} does exactly this. An upper and a lower
bound are maintained, a null window probe is repeatedly performed at the current guess, and
each probe moves whichever of the two bounds it refutes. As soon as the bounds meet, the
current guess is the answer.

```cpp
int mtdf(const Board& b, const int firstGuess, const int maxDepth = -1) noexcept {
  auto g = firstGuess;
  int upperBound = INT32_MAX;
  int lowerBound = INT32_MIN;

  while (lowerBound < upperBound) {
    const auto beta = std::max(g, lowerBound + 1);
    g = negamax(b, beta - 1, beta, 0, maxDepth);
    if (g < beta) upperBound = g;      // failed low  -> g is an upper bound
    else          lowerBound = g;      // failed high -> g is a lower bound
  }
  return g;
}
```

These are eleven lines, and the entire search is a null-window search from top to bottom. The
name stands for Memory-enhanced Test Driver, and the memory part of it is not decoration: each
probe re-searches essentially the same tree with a slightly different boundary, and without a
transposition table which carries the work forward this would be ruinous. MTD(f) and the
techniques of part 5 therefore belong together.

The parameter `firstGuess` is where the actual leverage lies. Each iteration costs a full
null-window search, so the number of iterations corresponds to the number of times the tree is
re-searched. A good guess, obtained for instance from a shallower search, from the previous
move in the same game, or from an opening book, can reduce this to two or three iterations,
whereas a poor one can require more probes. Since BitBully uses the fail-soft result `g`
directly as the next bound, an individual probe may nevertheless jump across several score
units rather than moving only one step.

#### An Alternative based on Binary Search

BitBully contains a second driver which attacks the same problem by bisection rather than by
iteration:

```cpp
int nullWindow(const Board& b, const int maxDepth = -1) noexcept {
  int min = -b.movesLeft() / 2;
  int max = (b.movesLeft() + 1) / 2;

  while (min < max) {
    int mid = min + (max - min) / 2;
    if      (mid <= 0 && min / 2 < mid) mid = min / 2;
    else if (mid >= 0 && max / 2 > mid) mid = max / 2;
    int r = negamax(b, mid, mid + 1, 0, maxDepth);
    if (r <= mid) max = r;
    else          min = r;
  }
  return min;
}
```

It is worth noting where `min` and `max` are initialized from, namely from the free bounds
derived above. The two lines which adjust `mid` are also interesting: a plain bisection would
probe the arithmetic midpoint, whereas this code prevents a midpoint close to zero from
remaining there while a much larger outer bound is still open. It replaces such a midpoint
with half of the relevant negative or positive bound (for example, the initial interval
$$[-21,21]$$ probes at $$-10$$ rather than at zero). This is a small empirical bias away from
zero on top of an otherwise ordinary binary search.

#### A Note on Iterative Deepening

The conventional way of obtaining a good first guess is iterative deepening, where one searches
to depth one, uses the result to seed the search at depth two, and so on. It is standard
practice in chess programming and would appear to be a natural fit here as well.

In connection with transposition tables it is also possible to optimize the move ordering using
iterative deepening. In this project, however, iterative deepening is not used for the
alpha-beta search, as it could not achieve any runtime advantages. This is worth stating
plainly, since it contradicts the general advice, and the reason for it is specific to
Connect-4. Chess programs need iterative deepening because they cannot search to the end and
have to return something when the clock runs out. A Connect-4 solver searches to the terminal
nodes, so the intermediate iterations are pure overhead unless their move ordering pays for
itself, and with the threat-based ordering of part 4 already in place there was not enough
left to recover.

<br>

## Evaluation at the Search Horizon

Everything described so far assumes a complete solve. If the depth is capped, for instance in
order to obtain a weaker opponent or a faster analysis, then the search reaches a horizon and
needs a value for a position which it has not resolved.

The classical answer to this is a static evaluation function, and the 2012 engine does contain
one, which we will look at in part 9. The answer of BitBully is cheaper and, in my opinion,
rather elegant: the game is simply played out using the heuristics which are available
anyway.

```cpp
static int rollout(Board b) noexcept {
  int ply = 0;
  while (true) {
    if (b.canWin()) {
      const int score = (b.movesLeft() + 1) / 2;
      return (ply % 2 == 0) ? score : -score;
    }
    if (!b.movesLeft()) return 0;

    auto moves = b.generateNonLosingMoves();
    if (!moves) {
      const int score = -(b.movesLeft() / 2);
      return (ply % 2 == 0) ? score : -score;
    }
    b = b.playBitMaskOnCopy(Board::nextMove(moves));
    ply++;
  }
}
```

Both sides play according to the centre-first heuristic of part 4, restricted to the non-losing
moves. This does not amount to a strong player, but it terminates after at most 42 steps, it
never blunders into an immediate loss, and, which is the essential point, it returns a value in
the same units as the real search, so that no calibration is necessary. The alternating
negation via `ply % 2` converts the value back to the point of view of the root.

The whole procedure thus reuses machinery which was built for other purposes, and there is no
evaluation function which would have to be written, tuned or gotten wrong.

<br>

## Comparing the three Drivers

The three drivers sit on top of the same `negamax` function and must therefore return identical
values. The following measurements use thirty random positions per ply, with the opening book
disabled and the transposition table cleared before each solve:

| Stones | MTD(f) nodes | Negamax nodes | Null-window nodes | MTD(f) time |
| ---: | ---: | ---: | ---: | ---: |
| 12 | 640,895 | 813,712 | 699,986 | 66.4 ms |
| 14 | 119,037 | 149,675 | 124,740 | 16.2 ms |
| 16 | 69,480 | 91,583 | 70,280 | 9.4 ms |
| 18 | 31,787 | 37,026 | 36,541 | 4.6 ms |
| 20 | 9,169 | 11,186 | 11,068 | 1.5 ms |
| 22 | 1,505 | 1,635 | 1,727 | 0.3 ms |

<details markdown="1">
<summary>How this was measured</summary>

30 random legal positions per ply (`forbid_direct_win=True`), `reset_book()` so the search
does the work, transposition table and node counter reset before every single solve. All three
drivers are asserted to return the same score on every position — the assertion is the real
point of the experiment. Reproduce with `tools/connect4/bench_drivers.py`.

</details>

MTD(f) wins everywhere, by roughly 8 to 24% in terms of nodes compared to plain negamax with a
wide window. The binary-search variant usually lies in between, and the MTD(f) advantage is
generally larger on the earlier positions with larger trees, although the trend is not
monotonic.

The more valuable output of this experiment, however, is the assertion which did not fire.
Three drivers which use three different sequences of windows and therefore explore genuinely
different parts of the tree agree on every single position. This is a useful internal
consistency check, although it cannot expose a bug which all three drivers share. That
distinction is precisely the subject of the next post.

<br>

## Convergence of MTD(f)

Since the machinery of this post consists of an ordinary negamax plus a handful of short
driver loops, it is small enough to be reimplemented in the browser, and the following widget
contains exactly that: a JavaScript transcription of the search — the free bounds, a
transposition table and the threat-based move ordering of part 4, though without the parity,
ETC and mirror refinements of part 5 — with all three drivers racing on the same random
position. The probe log is the interesting part. Each bar shows the interval of scores which
is still possible after a null-window probe, and the true value is pinned down by a handful of
yes/no questions rather than computed in a single pass.

<link rel="stylesheet" href="{{ '/assets/css/connect4-widgets.css' | relative_url }}" />

<div class="c4bb" data-c4-search></div>

<script src="{{ '/assets/js/connect4-core.js' | relative_url }}"></script>
<script src="{{ '/assets/js/connect4-search.js' | relative_url }}"></script>

The node counts reported here should not be compared with the table above, since the browser
solver lacks several refinements of the real engine and accordingly visits more nodes; a solve
with 16 stones can therefore take a moment. The agreement of the three drivers, however, is
the same invariant as in the measurement above, and the transcription itself is checked
against BitBully — including the returned scores on random endgame positions — by
`tools/connect4/check_widget.mjs`, in the same way as the widgets of the earlier posts.

<br>

## Summary

At this point the engine is complete. It consists of a bit board representation, a threat-based
move ordering, a transposition table with symmetry lookups and enhanced cutoffs, twelve plies
of precomputed openings, and an MTD(f) driver on top of all of it.

This leaves one question which should make anyone slightly nervous. The historical Java agent
grew to roughly seven thousand lines, part of them machine-generated, while the shorter C++
solver concentrates much of the same complexity into bit-board expressions. How can one be
sure that either is actually correct?

<br>

## Source Code

Pinned to the commit this post was written against:

- **BitBully** — [`BitBully.h`](https://github.com/MarkusThill/BitBully/blob/50c45ff72113655b79878cf1022771298c449d84/src/BitBully.h)
  (`mtdf`, `nullWindow`, `negamax`, `rollout`, `scoreToMovesLeft`)
  · [solver API documentation](https://markusthill.github.io/BitBully/solver/)
  · [GitHub](https://github.com/MarkusThill/BitBully) · [PyPI](https://pypi.org/project/bitbully/)
  · [project page]({{ 'projects/0_bitbully/' | absolute_url }})

```python
import bitbully as bb

agent = bb.BitBully()
board, _ = bb.Board.random_board(n_ply=14, forbid_direct_win=True)

assert agent.mtdf(board) == agent.negamax(board) == agent.null_window(board)
print("score:", agent.mtdf(board))
print("moves until the game ends:", agent.score_to_moves_left(agent.mtdf(board), board))
```

<br>

## References

<div class="publications">
{% bibliography --file thesis --cited --group_by none %}
</div>

---

*Several paragraphs of this post are adapted from my
[Master's thesis](http://www.gm.fh-koeln.de/~konen/research/PaperPDF/MT-Thill2015-final.pdf),
a translation of my
[Bachelor thesis](http://www.gm.fh-koeln.de/ciopwebpub/Theses.d/Thill12.d/BA-Thill-2012.pdf),
and [some earlier project work](http://www.gm.fh-koeln.de/ciopwebpub/Thil12a.d/Thill12a.pdf).*
