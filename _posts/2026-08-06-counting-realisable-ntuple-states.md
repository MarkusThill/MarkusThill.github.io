---
layout: post
title: "Counting the Realisable States of an N-Tuple"
modified: 2026-08-06T09:00:51+01:00
categories: [ML, math]
description: "Most entries of an n-tuple table can never be addressed on a Connect-4 board, because gravity forbids the patterns they describe. A column-by-column count, a closed form, a check against ten trained agents, and a ranking that stores a trained network without any indices."
tags: [n-tuple networks, combinatorics, reinforcement learning, Connect-4, math, python]
thumbnail: assets/img/2026-08-06-counting-realisable-ntuple-states/realisable-states-cartoon.webp
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-08-06T09:00:51+01:00
pretty_table: false
related_posts: true
---

The Connect-4 agent of the {% include series_link.liquid series="connect4-rl" part=7 text="reinforcement-learning series" %}
evaluates positions with an n-tuple network: 200 patterns of eight board cells each, and for every pattern a
table with one weight per possible content of its cells. Each cell can be empty, yellow, red, or empty and
reachable by the next move, so a table has $$4^8 = 65{,}536$$ entries, and with one table per pattern and
player the network has 26,214,400 weights. After training, however, fewer than one in ten of them is different
from zero. This is not a sign of incomplete training. Most entries describe patterns that can never appear on
a Connect-4 board, because stones cannot float in mid-air, and the training simply never addresses them.

How many entries can actually occur is a nice little counting problem, which I first worked out in my
Bachelor thesis {% cite ThillBA12 --file thesis %} with a recursion over the rows of a column. In this post I
derive the count again, in a closed form that is a little easier to read, check it against ten agents trained
for {% include series_link.liquid series="connect4-rl" part=9 text="part 9 of the series" %}, and then turn
the count into a ranking. The ranking numbers the possible patterns of a tuple consecutively, so that a trained
network can be stored as a plain list of weights without any indices, which shrinks the file of the agent from
105 MB to 7.9 MB and makes it small enough to be played against in the browser.

<!--more-->

## Notation

Rows and columns are counted from zero, rows from the bottom; in the figures, columns carry the letters a to g
and rows the numbers 1 to 6.

| Symbol                  | Type     | Description                                                                                                  |
| ----------------------- | -------- | ------------------------------------------------------------------------------------------------------------ |
| $$N$$                   | integer  | Number of cells of an n-tuple, here $$N = 8$$                                                                 |
| $$s_i$$                 | 0 … 3    | State of the $$i$$-th cell of the tuple: 0 empty, 1 yellow, 2 red, 3 empty and reachable                      |
| $$T$$                   | integer  | Table index of the tuple's state, $$T=\sum_{i=0}^{N-1} s_i\,4^i$$                                             |
| $$r_1<\dots<r_k$$       | rows     | Rows of the $$k$$ tuple cells within one column                                                               |
| $$g_j$$                 | integer  | Number of rows directly below $$r_j$$ which the tuple does not sample: $$g_1=r_1$$, $$g_j=r_j-r_{j-1}-1$$     |
| $$C(r_1,\dots,r_k)$$    | integer  | Number of realisable states of the tuple cells of one column                                                   |
| $$S(x,y)$$              | integer  | The recursion of the Bachelor thesis for column $$x$$, from row $$y$$ upwards                                  |
| $$R$$                   | integer  | Number of realisable states of a tuple, the product of its column counts                                       |

<br>

## Tuples, Cell States and Table Indices

An n-tuple network, introduced by Bledsoe and Browning for character recognition
{% cite Bledsoe59 --file thesis %} and brought to board games by Lucas {% cite Lucas08 --file thesis %},
describes a position by many small patterns. A tuple is a fixed list of $$N$$ cells; the states of these cells
form a number in base 4,

\begin{equation}
T = \sum_{i=0}^{N-1} s_i\,4^i,
\label{eq:index}
\end{equation}

which selects one weight of the tuple's table, and the value of a position is the sum of the selected weights
of all tuples, squashed by $$\tanh$$. The Connect-4 agent uses four states per cell rather than three: an empty
cell is marked as reachable if the next stone in its column would land there. In my Bachelor thesis, this fourth
state raised the success rate of the agent against a perfect opponent from about 81% to 91%
{% cite ThillBA12 --file thesis %}. It is also what makes the counting below a little more interesting, since the
reachable cell of a column is determined by the stones below it.

The first panel of the next figure shows a state of one of the agent's tuples that can occur in a game. The
other three show states that cannot, each for a different reason: a stone above an empty cell, two landing
cells in one column, and an empty cell in the bottom row that is not reachable. Every one of them has its
entry in the table, and none of them is ever addressed.

{% include figure.liquid
   path="assets/img/2026-08-06-counting-realisable-ntuple-states/tuple-states.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="100%"
   caption="Four states of the same eight-cell tuple of the Connect-4 agent (dashed cells). Only the first can occur on a board. The crossed cell makes the other three impossible: a stone above an empty cell, a second reachable cell above the first one, and an empty bottom cell, which is always reachable."
%}

<br>

## Counting a Single Column

The key observation is that the constraints act column by column. Within a column, the stones fill the rows from
the bottom; the first free row is reachable, and every row above it is empty. Nothing links one column to
another except the order in which stones were played, which the tuple does not see. The realisable states of a
tuple are therefore all combinations of one realisable state per column, and their number is the product of
the column counts,

\begin{equation}
R = \prod_{\text{columns } x} C\bigl(\text{rows of the tuple in column } x\bigr).
\label{eq:product}
\end{equation}

For one column, let the tuple sample the rows $$r_1<\dots<r_k$$. Consider how many of these cells are filled.
If all $$k$$ of them are, each can be yellow or red, which gives $$2^k$$ states. If only the lowest $$j-1$$ are
filled, for some $$j\le k$$, they can be coloured in $$2^{j-1}$$ ways, all sampled cells above $$r_j$$ are
empty, and the cell in row $$r_j$$ itself is either reachable, if the stones reach exactly up to it, or empty,
if the column ends lower. The latter requires at least one unsampled row between the filled cells and
$$r_j$$, i.e. $$g_j>0$$, where $$g_j$$ counts the unsampled rows directly below $$r_j$$. Summing over the
cases yields

\begin{equation}
C(r_1,\dots,r_k) = 2^k + \sum_{j=1}^{k} 2^{j-1}\,\bigl(1 + [\,g_j > 0\,]\bigr),
\label{eq:column}
\end{equation}

where $$[\,\cdot\,]$$ is 1 if the condition holds and 0 otherwise. A few special cases make the formula
tangible. A single cell has 4 states, or 3 in the bottom row, where an empty cell is always reachable. Cells
stacked from the bottom without gaps have $$g_j=0$$ throughout, which gives $$2^k+2^k-1=2^{k+1}-1$$ states. A
column sampled completely therefore has $$2^7-1=127$$ states, which agrees with a direct count: a column with
$$h$$ stones can be coloured in $$2^h$$ ways, and $$\sum_{h=0}^{6}2^h=127$$. In code, the closed form is a short
loop:

```python
def count_column(rows: list[int]) -> int:
    """Realisable states of the sampled rows of one column, in closed form.

    With the sampled rows r_1 < ... < r_k, the lowest j of them can be filled (2**j colourings); the next
    one is then either reachable, or empty if at least one unsampled row lies below it (for j = 0: if it
    is not in the bottom row). With j = k all sampled cells are filled.
    """
    r = sorted(rows)
    total = 2 ** len(r)
    for j in range(len(r)):
        gap = r[j] if j == 0 else r[j] - r[j - 1] - 1  # unsampled rows directly below r_{j+1}
        total += 2**j * (1 + (gap > 0))
    return total
```

The Bachelor thesis arrives at the same numbers with a recursion that walks down a column from the top
{% cite ThillBA12 --file thesis %}. With $$p(x,y)=1$$ if the tuple samples row $$y$$ of column $$x$$ and
$$p(x,y)=0$$ otherwise, and $$z(y)$$ the number of non-filled states a sampled cell can have in row $$y$$ (1 in
the bottom row, 2 above), it reads

\begin{equation}
S(x,6)=1,\qquad S(x,y) = S(x,y+1)\,\bigl(p(x,y)+1\bigr) + p(x,y)\,\bigl(z(y)-2\,p(x,y+1)\bigr),
\label{eq:recursion}
\end{equation}

and $$S(x,0)$$ is the count of column $$x$$. An unsampled row leaves the count unchanged. A sampled cell is
either filled, in two colours, with any of the $$S(x,y+1)$$ states above it, or it is not filled, in $$z(y)$$
ways, with all sampled cells above it empty. The correction $$-2\,p(x,y+1)$$ removes the two states in which a
filled cell lies directly below a sampled cell that is empty but not reachable. The recursion is well suited to
an algorithm, whereas the closed form \eqref{eq:column} shows the structure directly:

```python
def count_recursive(tuple_bits: list[int]) -> int:
    """Number of realisable states: product over columns of the thesis recursion S(x, 0)."""
    rows_by_col: dict[int, set[int]] = {}
    for col, row in cells(tuple_bits):
        rows_by_col.setdefault(col, set()).add(row)
    total = 1
    for rows in rows_by_col.values():
        S = 1  # S(x, 6) = 1
        for y in range(N_ROWS - 1, -1, -1):
            p, p_above = int(y in rows), int(y + 1 in rows)
            z = 1 if y == 0 else 2  # non-filled states possible in row y
            S = S * (p + 1) + p * (z - 2 * p_above)
        total *= S
    return total
```

Both agree, and they also agree with a brute-force enumeration of every stack height and colouring, for all 63
possible sets of sampled rows in a column and for all 200 tuples of the agent.

#### A Worked Example

The tuple of the figure above samples the cells a1, b1, b2, c1, c2, c3, d2 and d4. Column a contributes a single
bottom cell with 3 states, and columns b and c contribute two and three cells stacked from the bottom, with
$$2^3-1=7$$ and $$2^4-1=15$$ states. Column d samples rows 2 and 4 (in the zero-based notation, $$r_1=1$$ and
$$r_2=3$$); both have an unsampled row directly below them, $$g_1=g_2=1$$, so that equation \eqref{eq:column}
gives $$2^2 + 1\cdot 2 + 2\cdot 2 = 10$$ states. The tuple can therefore take $$3\cdot7\cdot15\cdot10=3{,}150$$
states, 4.8% of the 65,536 entries of its table.

<br>

## An Upper Bound, and What Training Needs

The count treats every column on its own, and it still includes states in which the tuple sees a complete four
in a row. Such a state belongs to a finished game, and since finished positions are never evaluated during
training, their weights keep their initial value of zero, as the thesis already noted. For the 200 tuples of the
agent, 15,170 of the 1,075,163 realisable states per player contain such a four, which leaves 1,059,993
states that training can actually reach. Other constraints between columns, such as the number of stones of each
colour, cannot be checked from the few cells of a tuple, so even this number is an upper bound for what a real
game can produce; the trained agents below suggest that it is a tight one.

The next figure shows the count for all 200 tuples. The realisable share of a table ranges from 1,024 of 65,536
entries (1.6%) to 32,768 (50%), with a median of 4,096, and over all tuples it is 8.2%. What matters most is
how many columns a tuple spans. The largest counts belong to tuples that spread their eight cells over six or
seven columns, mostly one cell per column above the bottom row, where a single cell can take all four states.
The smallest belong to tuples that stack four or five cells in each of only two columns. The thesis found a similar picture for
randomly generated tuples: for random walks of eight cells, fewer than 8% of the states are realisable on
average {% cite ThillBA12 --file thesis %}.

{% include figure.liquid
   path="assets/img/2026-08-06-counting-realisable-ntuple-states/realisable-per-tuple.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="100%"
   caption="Left: realisable share of the 65,536 entries for each of the 200 tuples of the Connect-4 agent, sorted; the horizontal line marks the share over all tuples (8.2%). Right: share of the non-terminal realisable states (those without a four in a row inside the tuple) whose weight is non-zero after training, averaged over the ten agents of part 9, in the same order."
%}

<br>

## What Training Visits

Ten agents trained for part 9 of the series, each on about 42 million self-play games, allow a direct check of
all this. In every one of the ten networks, no weight outside the realisable set is non-zero, and no weight of
a state with a four in a row either, exactly as the count predicts. Of the 1,059,993 non-terminal realisable
states per player, the agents visited between 99.4% and 99.6%. For 51 of the 200 tuples, all ten agents visited every
such state, and the least-covered tuple still reached 94% on average. Within the limits of the count, training
therefore explores practically everything the board allows, and the zero weights of a trained network are almost
entirely explained by gravity and by finished games.

<br>

## From Counting to Ranking

Counting column by column also yields a numbering. If the realisable states of every column are listed in a
fixed order, a state of the whole tuple is a choice of one entry per column, and its position in the list of all
realisable tuple states can be written as a mixed-radix number: the digit of a column is the position of its
state in the column's list, and the base of that digit is the column's count. This rank is a bijection between
the realisable table indices of a tuple and the numbers $$0,\dots,R-1$$, and both directions take one pass over
the columns:

```python
    def rank(self, index: int) -> int:
        """Rank of a realisable table index (KeyError if the index is not realisable)."""
        return sum(self._digit[k][self.partial(index, c)] * self.strides[k] for k, c in enumerate(self.columns))

    def unrank(self, rank: int) -> int:
        index = 0
        for k, c in enumerate(self.columns):
            digit, rank = divmod(rank, self.strides[k])
            index += c.partials[digit]
        return index
```

Here `partial(index, c)` extracts the part of the table index that belongs to the cells of column `c`, and
`strides` are the products of the counts of the following columns. For every tuple of the agent,
`rank(unrank(r)) == r` holds for all realisable ranks, and indices of impossible states are rejected.

The ranking makes the storage of a trained network straightforward. Instead of all 26,214,400 weights, only
the $$2\cdot1{,}075{,}163 = 2{,}150{,}326$$ weights of realisable states are written, in rank order, and a reader
of the file recomputes the rank from a position instead of looking up an index. With 32-bit floats this takes
8.6 MB, 7.9 MB after compression, compared with 105 MB for the checkpoint, and nothing is lost: the in-browser
version of the agent in part 9 is built exactly this way, and in 7,447 test positions from self-play it computes
the same move scores and chooses the same moves as the original Python agent. Half precision would halve the file
again and still chooses the same moves, but 118 of the 45,286 move scores in these positions change by one point;
eight-bit weights shrink the file to 1.6 MB but change the move in 2.1% of the positions. I therefore kept the
exact version. Dropping the 15,170 four-in-a-row states per player as well would save only another 1.4%.

<br>

## Source Code

- **Counting and ranking** — `tools/connect4_rl/realisable_states.py` in the
  [source of this blog](https://github.com/MarkusThill/MarkusThill.github.io/tree/master/tools/connect4_rl),
  with the export of the weights (`export_ntuple_weights.py`) and the figures of this post
  (`make_realisable_states_figures.py`)
- **The recursion in the training repository** — appendix "Realisable LUT Configurations" of
  `lab2/0_problem_illustration.ipynb` in [techdays26](https://github.com/MarkusThill/techdays26)
- **CFour's counter** —
  [`CountRealizableStates.java`](https://github.com/MarkusThill/Connect-Four/blob/2a58844594ac022846385dd3ddc8bbbf0a26eae5/CFour/src/miscellaneous/CountRealizableStates.java)

<br>

## References

<div class="publications">
{% bibliography --file thesis --cited --group_by none %}
</div>
