---
layout: post
title: "Building Intelligent Agents for Connect-4&#58; Move Ordering"
modified: 2026-06-23T09:00:51+01:00
categories: [programming]
description: "How the two solvers combine centre-first priorities, threat counts and parity heuristics, and how non-losing move generation removes branches before they reach alpha-beta."
tags: [Connect-4, AI, tree-search, alpha-beta, minimax, transposition tables, opening databases, move ordering, bitboards]
thumbnail: assets/img/2026-02-12-connect-4-move-ordering/possibleChains.png
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-02-12T09:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
series: connect4-search
series_part: 4
---

{% include series_connect4.liquid %}

The previous post was concerned with making each individual operation as fast as possible.
This one deals with the considerably more rewarding question of how to perform far fewer of
them.

In order to achieve the highest possible efficiency of the alpha-beta algorithm, a good move
ordering is necessary. In contrast to the Minimax algorithm, which has to examine all nodes of
the search tree, the alpha-beta algorithm can prune large parts of the tree if the best moves
are tried out early on. The reason for this is that both players always try to maximize their
own result and to minimize the result of the opponent. The closer the current results come to
the game-theoretic values, the more subtrees can be cut off, since they no longer contribute
to the determination of the exact values.

<!--more-->

In my experience this is where the largest improvements in a Connect-4 solver are to be found.
Before making technical optimizations to the program, before adding hash tables and before
computing a database, one should first try to improve the move ordering, since it offers much
more potential.

<br>

## The Effect of Move Ordering

Consider a game tree with branching factor $$b$$ which is searched to depth $$d$$. Minimax
visits $$b^d$$ leaf nodes, and alpha-beta with the worst possible move ordering visits the
same number. With a perfect ordering, in which the best move is always tried first, only

$$
b^{\lceil d/2 \rceil} + b^{\lfloor d/2 \rfloor} - 1 \approx 2\,b^{d/2}
$$

leaf nodes have to be examined, which is essentially the square root of the original effort.
For Connect-4 with $$b \approx 7$$, a search to depth 20 would thus drop from
$$7^{20} \approx 8 \cdot 10^{16}$$ to roughly
$$2 \cdot 7^{10} \approx 5.6 \cdot 10^{8}$$ nodes. No amount of instruction-level tuning can
compete with a change of eight orders of magnitude.

The catch, of course, is that knowing the best move is precisely the problem we are trying to
solve in the first place. Move ordering is therefore always a heuristic, and it comes with a
budget, since time spent on deciding what to search first is time which is not spent on
searching.

This budget is not uniform across the tree. Cutoffs near the root remove larger subtrees, and
since comparatively few nodes occur at these levels, sophisticated and relatively expensive
procedures for move ordering are conceivable there. Deeper in the tree the situation reverses:
the nodes are overwhelmingly numerous and each individual cutoff saves very little, so the
computing time per node has to be minimized. For this reason both of my agents divide the
search into stages. BitBully uses the full threat-counting sort while `depth < 20`, a lighter
`findThreats()` pass at depths 20 and 21, and the static priority scan alone from depth 22.

<br>

## Simple Move Ordering

Generally speaking, it can be said that moves in the central columns of the board are usually
preferable, and there is a concrete reason for this: a cell in the centre can be part of more
potential chains of four than a cell at the edge.

{% include figure.liquid
   path="assets/img/2026-02-12-connect-4-move-ordering/possibleChains.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="40%"
   caption="Number of four-in-a-row lines passing through each cell. The centre-column cell d3 sits on 13 of them; the corner a1 on just 3. This does not determine the best move in a concrete position, but it provides a useful prior for a centre-first ordering."
%}

Of the 69 possible chains of four on a Connect-4 board, of which 21 are vertical, 24
horizontal and 24 diagonal, a central cell is part of roughly four times as many as a corner
cell. BitBully encodes this observation directly in six `constexpr` priority classes. Note
that these classes refer to cells rather than to columns, so that the middle rows of the middle
column receive the highest priority:

```cpp
static constexpr TBitBoard BB_MOVES_PRIO1 = getMask({29, 30});
static constexpr TBitBoard BB_MOVES_PRIO2 = getMask({31, 21, 20, 28, 38, 39});
static constexpr TBitBoard BB_MOVES_PRIO3 = getMask({40, 32, 22, 19, 27, 37});
static constexpr TBitBoard BB_MOVES_PRIO4 = getMask({47, 48, 11, 12});
// ... and two more, working outward to the corners
```

Decoding with the layout from the last post (`bit = col * 9 + row`), `BB_MOVES_PRIO1` is
$$\{29, 30\}$$ = column 3, rows 2 and 3 — dead centre. Picking the next move is then a walk
down the priority list, taking the first class that intersects the candidate set:

```cpp
[[nodiscard]] static TBitBoard nextMove(TBitBoard allMoves) {
  for (const auto p : BB_MOVES_PRIO_LIST) {
    if (const TBitBoard pvMv = allMoves & p) {
      allMoves = pvMv;
      break;
    }
  }
  return lsb(allMoves);
}
```

In the worst case this requires six AND operations, without any sorting and without
allocations. Since it does not contain any dynamic elements, it can be implemented very
efficiently, and it is therefore the ordering used deep in the tree, where the computing time
per node is what matters. To date, no further measures have been successful in improving the
second stage of the move ordering, mainly because cutoffs in these levels do not save enough
nodes to compensate for the additional effort.

<br>

## Preferring Moves which generate Threats

Near the root we can afford to look at what a move actually does. Especially in the early and
middle phase of a game it is important for the players to build up threats, since if one of the
two players succeeds in doing so, the other may eventually be forced to make a move which loses
the game. BitBully's `sortMoves` therefore scores every candidate by the number of threats the
player would have after making it, that is, by the number of still-empty cells which would then
complete a chain of four, and feeds these scores into a small priority queue:

```cpp
MoveList Board::sortMoves(TBitBoard moves) const {
  MoveList mvList;
  const TBitBoard ownThreats = winningPositions(m_bActivePTokens, false);

  while (moves) {
    const auto mv = nextMove(moves);

    // How many threats (direct and indirect) will I have after this move?
    const auto threats =
        winningPositions(m_bActivePTokens ^ mv, true) & ~(m_bAllTokens ^ mv);
    auto numThreats = static_cast<int>(uint64_t_popcnt(threats));

    // Usually avoid moving under your own threat -- the opponent
    // just neutralises it on the next ply.
    if (ownThreats & (mv << 1)) numThreats--;

    mvList.insert(mv, numThreats);
    moves ^= mv;
  }
  return mvList;
}
```

Two details of this function are worth pausing on. The expression
`winningPositions(...) & ~(m_bAllTokens ^ mv)` counts only threat cells which are still empty.
They may be directly playable or still floating above other empty cells; `sortMoves()` includes
both classes. The AND with the complement of the occupancy filters occupied cells out with one
further bitwise operation, without an additional loop or allocation.

The second detail is the line `if (ownThreats & (mv << 1)) numThreats--`. Shifting a move mask
up by one bit lands on the cell directly above it, and if one of our own threats sits there,
then playing this move would allow the opponent to neutralize the threat on the next ply. Such
moves are therefore sorted to the back. A genuine piece of Connect-4 strategy is thus expressed
in one shift, one AND and one decrement.

#### A Priority Queue for seven Elements

The class `MoveList` is deliberately not a heap. With at most seven moves, the asymptotic
advantage of a heap loses against the constant factor of a simple insertion sort:

```cpp
void insert(const TBitBoard move, const int score) {
  int pos = size++;
  for (; pos && m_arrayPrioQueue[pos - 1].score >= score; --pos)
    m_arrayPrioQueue[pos] = m_arrayPrioQueue[pos - 1];
  m_arrayPrioQueue[pos].move = move;
  m_arrayPrioQueue[pos].score = score;
}

inline TBitBoard pop() {
  return size ? m_arrayPrioQueue[--size].move : UINT64_C(0);
}
```

This is a fixed seven-element array on the stack without any allocation, and `pop()` runs in
constant time. The `>=` in the loop condition preserves the insertion order among equal scores,
so that the centre-first ordering from the previous section survives as a tie-break inside the
threat-based ordering. Two heuristics are thus combined in a single data structure.

Note that CFour also contains a class called `MoveList`, but it is a rather different thing:
a move history used for undoing moves, not a priority queue. The 2012 agent sorts its moves
inside `AlphaBetaAgent` itself.

<br>

## Odd and Even Threats

We now come to the part which is genuinely specific to Connect-4, and which in my experience is
the reason why a naive agent eventually stops improving.

However, not all threats of a player are equally useful. Since the players alternate and the
tokens stack up from the bottom, control of the cells underneath a threat can determine who
eventually has to occupy its row. This is a conditional zugzwang argument, not a rule that the
first player literally occupies every odd row and the second player every even one.

Victor Allis has elaborated on this topic in detail in his master's thesis
{% cite Allis88 --file thesis %}. The rules he sets up are so complex and abstract, however,
that it is very difficult to transfer them to move ordering directly. Since a move ordering
does not have to provide the optimal move sequence in all cases anyway, both engines use rough
priorities which cover many common situations. They should be read as heuristics rather than
as sufficient conditions for the outcome:

1. Moves which add a useful odd-row threat are usually worth examining early.
2. The first player benefits particularly from odd threats in the standard parity strategy.
3. The second player may also benefit from even threats, provided that the supporting cells
   and the opponent's odd threats do not reverse the move order.

In a bit board these priorities amount to a single AND against a constant. CFour uses the row
parity masks in its evaluation function. BitBully also provides `findOddThreats()`, shown
below, although the current `negamax()` does not call it:

{% tabs parity %}

{% tab parity C++ (BitBully) %}

```cpp
Board::TBitBoard Board::findOddThreats(TBitBoard moves) {
  constexpr auto ODD_ROWS = getRowMask(2) | getRowMask(4);
  auto threats = winningPositions(m_bActivePTokens, true) & ~m_bAllTokens;
  const auto curNumThreats = uint64_t_popcnt(threats & ODD_ROWS);

  auto threatMoves = UINT64_C(0);
  while (moves) {
    const auto mv = lsb(moves);
    threats = winningPositions(m_bActivePTokens ^ mv, true) & ~(m_bAllTokens ^ mv);
    if (uint64_t_popcnt(threats & ODD_ROWS) > curNumThreats) {
      threatMoves ^= mv;   // this move adds a new odd threat
    }
    moves ^= mv;
  }
  return threatMoves;
}
```

{% endtab %}

{% tab parity Java (CFour) %}

```java
protected static final long EVENROWS = 0x15555555555L;
protected static final long ODDROWS  = 0xA28A28A28AL;

// From the one-threat case in AlphaBetaAgent.evaluate():
if (threatsP2 != 0) {
    if ((threatsP2 & EVENROWS) != 0L)
        return -500;
    return 0;
}
if ((threatsP1 & ODDROWS) != 0L)
    return 500;
return 0;
```

{% endtab %}

{% endtabs %}

Domain knowledge which would amount to a thicket of nested loops over a two-dimensional array
thus becomes a mask and a bit count. In my view this is the actual argument in favour of bit
boards: not merely that the individual operations are fast, but that the appropriate
abstractions become cheap enough to be used everywhere.

<br>

## Moves which are never generated

All the techniques described so far reorder the candidate moves. The next one removes some of
them entirely.

If the opponent threatens to win immediately, then almost every move loses on the spot. Once
an immediate win for the side to move has already been handled, BitBully can filter such losing
replies out during move generation. This precondition matters:
`generateNonLosingMoves()` is not a general replacement for checking one's own winning move.
Inside the recursive search it holds because the parent never generates a move which leaves an
immediate win unanswered; the root is checked separately.

```cpp
[[nodiscard]] TBitBoard generateNonLosingMoves() const {
  TBitBoard moves = legalMovesMask();
  const TBitBoard threats = /* opponent's winning cells */;

  if (const TBitBoard directThreats = threats & moves) {
    // We cannot neutralise more than one direct threat -- two means we lost.
    moves = directThreats & (directThreats - 1) ? UINT64_C(0) : directThreats;
  }
  // Never place a stone directly underneath an opponent threat.
  return moves & ~(threats >> 1);
}
```

Three bit tricks are combined in these six lines. The expression
`directThreats & (directThreats - 1)` is the classical test for whether more than one bit is
set. Under the precondition above, if the opponent has two immediate winning cells, we can
block at most one of them, so the position is already lost and the set of moves becomes empty.
If there is exactly one direct threat, then `moves` collapses to precisely that cell, which
means that the reply is forced and the branching factor at this node drops from seven to one.
Finally, `threats >> 1` shifts every threat of the opponent down by one cell, and the AND with
the complement removes exactly those moves which would place a token underneath one of the
opponent's winning cells.

An empty result is not an error here. It simply means that every reply loses, so that the
caller can return a loss without searching anything at all.

#### Exact Values without any Search

The same idea can be taken one step further. Some positions are already decided, and this can
be proven rather cheaply:

```cpp
[[nodiscard]] TBitBoard doubleThreat(const TBitBoard moves) const {
  const TBitBoard ownThreats = winningPositions(m_bActivePTokens, false);
  const TBitBoard otherThreats =
      winningPositions(m_bActivePTokens ^ m_bAllTokens, true);
  return moves & (ownThreats >> 1) & (ownThreats >> 2) & ~(otherThreats >> 1);
}
```

The expression `(ownThreats >> 1) & (ownThreats >> 2)` finds a move which has two of the
player's own threats stacked directly on top of it. If a token is placed there, the opponent
has to block the lower threat, which immediately exposes the upper one. This is a forced win,
and the exact value follows from the move count alone as `(movesLeft - 1) / 2`, without
expanding a single subtree.

One caveat is worth mentioning, since it cost me some debugging time while writing this post:
the double-threat test has to be applied to the non-losing moves, not to all legal moves. A
move can create a very attractive double threat and still lose, simply because it allows the
opponent to win first. BitBully performs the two steps in the correct order, first calling
`generateNonLosingMoves()` and only then `doubleThreat(moves)`.

The legacy CFour agent has one further reduction. If its explicit symmetry check finds that the
position equals its reflection at the middle axis, the move loop examines only the first four
columns, since the remaining three lead to mirror images with identical values. The check is
not free (it constructs mirrored bit boards), and the pinned BitBully move loop does not apply
this particular pruning rule.

<br>

## Trying the Move Ordering out

The rules described above are easier to follow on a concrete position than in prose, so the
following widget applies them live. For every legal move it shows the score which
`sortMoves()` would assign, that is, the number of threats present after the move and after the
correction for moving under one's own threat, together with the centre-first priority class of
the target cell. The table is sorted exactly the way `MoveList` would pop the moves.

<link rel="stylesheet" href="{{ '/assets/css/connect4-widgets.css' | relative_url }}" />

<div class="c4bb" data-c4-ordering></div>

<script src="{{ '/assets/js/connect4-core.js' | relative_url }}"></script>
<script src="{{ '/assets/js/connect4-ordering.js' | relative_url }}"></script>

The three example buttons show the situations discussed above. In the *forced reply* position
the opponent has exactly one immediate threat, so `generateNonLosingMoves()` collapses the move
set to a single cell and the branching factor at this node drops from seven to one. In the
*double threat* position one move has two of the player's own winning cells stacked above it,
which `doubleThreat()` recognises without expanding any subtree at all. And in the *already
lost* position the opponent has two immediate threats, only one of which can be blocked, so the
move generator returns an empty bit board and the search can report a loss immediately.

It is also worth switching the odd-row highlighting on and off. The dashed cells are rows 3 and
5 counting from the bottom, the rows which are particularly valuable to the first player in
the standard parity strategy. The highlighting is a heuristic cue; it does not say who must
occupy every such cell in an arbitrary continuation.

<br>

## Generating the Source Code

The threat detection of the 2012 engine consists of roughly 2000 lines of machine-generated,
fully unrolled branch tests, selected by cell and with the masks inlined as hexadecimal
literals. For reasons of efficiency and in order to avoid errors, this source code was not
written by hand but generated automatically by a second program:

```java
/**
 * The method findThreat (the source) was generated with this program,
 * because its source-code is very long. It can be chosen if findThreats
 * or findOddThreats is generated.
 */
public class GenerateSource extends ConnectFour {
    /** All four-rows, with the exception of the vertical ones */
    long fourRows[] = { 0x1041040000L, 0x41041000L, /* ... 48 masks ... */ };

    public static void main(String[] args) {
        new GenerateSource().createMethod(false);
    }
}
```

The same pattern appears several more times in the project, for instance in a small C++ tool
which generates the Zobrist key tables of part 5, and in the pipeline which produces the
opening books of part 6.

The reasoning behind this is worth making explicit, since it is a genuine engineering decision
rather than a hack. Whenever the required code is very long, completely mechanical, and at the
same time so performance-critical that loops and table lookups measured too slowly in the
target implementation, writing it by hand is both slower and considerably more error-prone
than writing the program which writes it. The generator comprises about 200 readable lines,
while its output consists of 2000 unreadable ones, and only the former has to be reviewed.

The approach has its price as well, of course. Generated code cannot be edited, only
regenerated, and if the generator is lost, the artefact becomes a fossil. It is therefore
advisable to keep the generator in the repository, which is the reason why
`GenerateSource.java` is still there some fourteen years later.

<br>

## Historical Measurements of the Move Ordering

Neither of the two engines contains a switch which would turn its move ordering off, so there
is unfortunately no clean ablation which could be run against them, and a reimplementation
would only measure the reimplementation. What does exist, however, are the measurements which
were taken while the 2012 agent was being developed on a Pentium-4, where each technique was
added to a working solver and the effect was recorded:

- **Threat-based ordering near the root** — preferring moves that create a threat, with the
  odd/even rules deciding which threats count — **halved the average search time**. This was
  the largest improvement recorded in those development notes, and the reason the two-stage
  structure exists at all.
- **The stacked-threat and double-threat shortcuts**, which return an exact score instead of
  expanding a subtree, were worth a further **~20%**.

Both numbers originate from the same source and should be read for what they are, namely
measurements of one engine on one machine in 2012 rather than universal constants. For
absolute claims, the whole-engine benchmarks of part 8 are the ones to rely on, since there
BitBully is compared against an independent reference solver on identical positions and with
the appropriate statistics.

The durable part is the theoretical argument at the beginning of this post. Under perfect
ordering, alpha-beta moves from the $$b^d$$ worst case towards the $$b^{d/2}$$ best case. The
measured heuristic does not automatically attain that bound, but the gap explains why it is
worth spending substantial effort on the question of which of seven columns should be searched
first.

<br>

## Summary

Each node is now cheap to process and there are considerably fewer of them. The search,
however, still re-derives the same positions over and over again, since Connect-4 reaches
identical boards through many different move sequences and none of the techniques described so
far notices this.

The next post therefore deals with remembering what has already been computed, and with the
somewhat surprising fact that the more recent engine does without the hashing scheme on which
the 2012 one was built.

<br>

## Source Code

Pinned to the commits this post was written against:

- **BitBully** — [`Board.cpp`](https://github.com/MarkusThill/BitBully/blob/50c45ff72113655b79878cf1022771298c449d84/src/Board.cpp)
  (`sortMoves`, `findThreats`, `findOddThreats`),
  [`Board.h`](https://github.com/MarkusThill/BitBully/blob/50c45ff72113655b79878cf1022771298c449d84/src/Board.h)
  (`generateNonLosingMoves`, `doubleThreat`, `nextMove`),
  [`MoveList.h`](https://github.com/MarkusThill/BitBully/blob/50c45ff72113655b79878cf1022771298c449d84/src/MoveList.h)
- **CFour** — [`GenerateSource.java`](https://github.com/MarkusThill/Connect-Four/blob/2a58844594ac022846385dd3ddc8bbbf0a26eae5/CFour/src/miscellaneous/GenerateSource.java),
  [`NumFourRows.java`](https://github.com/MarkusThill/Connect-Four/blob/2a58844594ac022846385dd3ddc8bbbf0a26eae5/CFour/src/miscellaneous/NumFourRows.java),
  [`AlphaBetaAgent.java`](https://github.com/MarkusThill/Connect-Four/blob/2a58844594ac022846385dd3ddc8bbbf0a26eae5/CFour/src/c4/AlphaBetaAgent.java)

BitBully in general: [GitHub](https://github.com/MarkusThill/BitBully) · [PyPI](https://pypi.org/project/bitbully/) · [Docs](https://markusthill.github.io/BitBully/) · [project page]({{ 'projects/0_bitbully/' | absolute_url }})

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
