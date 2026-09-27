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
retrace this recursion step by step, from a small example to the general rule, and then solve it for a closed
form that shows the structure of the count directly. I check the count against ten agents trained for
{% include series_link.liquid series="connect4-rl" part=9 text="part 9 of the series" %}, and then turn the
count into a ranking. The ranking numbers the possible patterns of a tuple consecutively, so that a trained
network can be stored as a plain list of weights without any indices, which shrinks the file of the agent from
105 MB to 7.9 MB and makes it small enough to be played against in the browser.

<!--more-->

## Notation

Rows and columns are counted from zero, rows from the bottom; in the figures, columns carry the letters a to g
and rows the numbers 1 to 6.

| Symbol               | Type     | Description                                                                                                      |
| -------------------- | -------- | ---------------------------------------------------------------------------------------------------------------- |
| $$N$$                | integer  | Number of cells of an n-tuple, here $$N = 8$$                                                                    |
| $$s_i$$              | 0 … 3    | State of the $$i$$-th cell of the tuple: 0 empty, 1 yellow, 2 red, 3 empty and reachable                         |
| $$T$$                | integer  | Table index of the tuple's state, $$T=\sum_{i=0}^{N-1} s_i\,4^i$$                                                |
| $$x$$, $$y$$         | integers | Column $$x\in\{0,\dots,6\}$$ and row $$y\in\{0,\dots,5\}$$ of a cell                                             |
| $$h$$                | 0 … 6    | Height of a column, the number of stones in it                                                                   |
| $$p(x,y)$$           | 0 or 1   | 1 if the tuple samples the cell $$(x,y)$$, 0 otherwise; $$p(x,6)=0$$                                             |
| $$z(y)$$             | 1 or 2   | Number of states without a stone that a sampled cell in row $$y$$ can take: 1 in the bottom row, 2 above         |
| $$S(x,y)$$           | integer  | Number of realisable states of the sampled cells of column $$x$$ in the rows $$y,\dots,5$$; $$S(x,6)=1$$         |
| $$k$$                | integer  | Number of sampled cells in one column                                                                            |
| $$r_1<\dots<r_k$$    | rows     | Rows of the sampled cells in one column                                                                          |
| $$g_j$$              | integer  | Number of unsampled rows directly below $$r_j$$: $$g_1=r_1$$, $$g_j=r_j-r_{j-1}-1$$                              |
| $$C_j$$              | integer  | Number of realisable states of the sampled cells in the rows $$r_j,\dots,r_k$$, i.e. $$S(x,r_j)$$; $$C_{k+1}=1$$ |
| $$d_j$$              | integer  | Term added by the sampled row $$r_j$$ in the recursion $$C_j=2\,C_{j+1}+d_j$$                                    |
| $$C(r_1,\dots,r_k)$$ | integer  | Number of realisable states of one column, $$C=C_1=S(x,0)$$                                                      |
| $$[\,\cdot\,]$$      | 0 or 1   | 1 if the condition in the brackets holds, 0 otherwise                                                            |
| $$R$$                | integer  | Number of realisable states of a tuple, the product of its column counts                                         |

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

## Counting Column by Column

The key observation is that the constraints act column by column. Within a column, the stones fill the rows from
the bottom; the first free row is reachable, and every row above it is empty. Nothing links one column to
another except the order in which stones were played, which the tuple does not see. The realisable states of a
tuple are therefore all combinations of one realisable state per column, and their number is the product of
the column counts,

\begin{equation}
R = \prod_{\text{columns } x} C\bigl(\text{rows of the tuple in column } x\bigr),
\label{eq:product}
\end{equation}

where a column without any cell of the tuple contributes a factor of 1.

A single column is described completely by its height $$h$$, the number of stones in it, and by the colours of
these stones. The stones occupy the rows $$0,\dots,h-1$$, the row $$h$$ is reachable (unless the column is full),
and all rows above it are empty. A sampled cell in row $$y$$ therefore holds a stone if $$y<h$$, is reachable if
$$y=h$$, and is empty if $$y>h$$. Counting heights and colourings is not the same as counting the states of the
tuple, however, because the tuple sees only its own cells, and different columns can look the same to it. The
tuple of the figure above, which serves as the example in the rest of this post, samples the cells a1, b1, b2,
c1, c2, c3, d2 and d4. In its column d, which contains d2 and d4, the heights 4, 5 and 6 all produce the same
four states, since both cells hold a stone in each case and the stones in d5 and d6 are not seen. The next
figure lists all states of the columns c and d of this tuple. Column c, which samples the three bottom cells,
has 15 of them, and column d has 10, out of $$4^3=64$$ and $$4^2=16$$ table entries.

{% include figure.liquid
   path="assets/img/2026-08-06-counting-realisable-ntuple-states/column-states.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="100%"
   caption="All realisable states of two columns of the example tuple, grouped by the number of stones in the sampled cells (dashed); the rows 5 and 6, which neither column samples, are left out. In column c, every sampled cell lies directly on top of the one below it, so the lowest cell without a stone is always reachable. In column d, the unsampled cells d1 and d3 below the sampled ones may be free as well, so the lowest sampled cell without a stone can also be empty, which doubles the first two groups."
%}

<br>

## A Recursion over the Rows of a Column

Listing all states works for two columns, but it quickly becomes tedious, and it does not explain the numbers.
In my Bachelor thesis I therefore counted the states with a recursion {% cite ThillBA12 --file thesis %}, and I
derived it there from a worked example, a tuple with exactly the cells of the one above, before stating it in
general. I follow the same path here.

#### Walking down a Column

The idea is to walk through a column from the top to the bottom and to keep a running count of the states of the
sampled cells seen so far. The direction of the walk is what makes this easy. When the walk reaches a cell, the
count for the cells above it is already known, and the only question is which of these states can lie on top of
the new cell. Since gravity acts downwards, the answer depends only on the content of the new cell and on
whether the cell directly above it belongs to the tuple, but not on anything further down.

Column d shows most of what can happen. Above d4 there is nothing to count yet, which we express as a count of 1,
the single state in which the tuple sees no cell at all. The first sampled cell, d4, can hold a stone of either
colour, be reachable, or be empty, which gives 4 states. The cell d3 does not belong to the tuple and leaves the
count unchanged. A yellow or red stone in d2 can then be combined with every one of the 4 states of d4: the
column may end with this stone, so that d3 is reachable and d4 empty, it may end in d3, which makes d4 reachable,
or it may continue beyond d4 with a stone of either colour. This gives $$2\cdot4=8$$ states. If d2 holds no
stone, d4 is necessarily empty, and d2 itself is reachable if the column ends in d1, or empty if the column
holds no stone at all, which adds 2 states. Finally, d1 is not sampled, and column d ends with a count of 10.

Column c differs in one detail. Its top cell c3 again contributes 4 states. A stone in c2, however, can no longer
be combined with all of them, because c3 lies directly on top of it and then either holds a stone or is
reachable, but cannot be empty without being reachable. One of the 4 states is thus excluded, and a stone in c2
gives $$2\cdot(4-1)=6$$ states. Without a stone, c2 is reachable or empty, with c3 empty in both cases, so that
c2 and c3 together have 8 states. The same argument excludes one state for a stone in c1, the one with c2 empty
but not reachable, which leaves $$2\cdot(8-1)=14$$ states. Without a stone, c1 can only be reachable, since it
lies in the bottom row, where every empty cell is reachable. Column c therefore has $$14+1=15$$ states. The
columns a and b follow in the same way, and the next table summarises the walk for the whole tuple.

| Row $$y$$ | Column a            | Column b                | Column c                 | Column d             |
| --------- | ------------------- | ----------------------- | ------------------------ | -------------------- |
| 5         | 1                   | 1                       | 1                        | 1                    |
| 4         | 1                   | 1                       | 1                        | 1                    |
| 3         | 1                   | 1                       | 1                        | d4: $$2\cdot1+2=4$$  |
| 2         | 1                   | 1                       | c3: $$2\cdot1+2=4$$      | 4                    |
| 1         | 1                   | b2: $$2\cdot1+2=4$$     | c2: $$2\cdot(4-1)+2=8$$  | d2: $$2\cdot4+2=10$$ |
| 0         | a1: $$2\cdot1+1=3$$ | b1: $$2\cdot(4-1)+1=7$$ | c1: $$2\cdot(8-1)+1=15$$ | 10                   |

<br>

Each entry is the count after the walk has passed the row $$y$$ (the cell names count the rows from 1, as in the
figures), and rows without a cell of the tuple repeat the entry above them. The bottom row holds the column counts, and with equation \eqref{eq:product} the tuple can take
$$3\cdot7\cdot15\cdot10=3{,}150$$ states, 4.8% of the 65,536 entries of its table.

#### The Rule for a single Row

The example already contains every case that can occur. To write the rule down in general, let $$p(x,y)$$ be 1 if
the tuple samples the cell $$(x,y)$$ and 0 otherwise, with $$p(x,6)=0$$ above the board, and let $$S(x,y)$$ be the
number of states that the sampled cells of column $$x$$ in the rows $$y,\dots,5$$ can show, taken over all
heights and colourings. The walk starts with $$S(x,6)=1$$, and a row that is not sampled changes nothing,
$$S(x,y)=S(x,y+1)$$. For a sampled row, the states split into three kinds according to the content of the cell
$$(x,y)$$:

- **A stone.** The cell holds a yellow or red stone, so the column has at least $$y+1$$ stones. Every state that
  the cells above can show at all can also appear on top of this stone, with a single exception: if the cell
  $$(x,y+1)$$ belongs to the tuple, it cannot be empty without being reachable, since the stone below makes it
  either reachable or occupied. In this excluded state all sampled cells above $$(x,y+1)$$ are empty as well, so
  it is exactly one state. If $$(x,y+1)$$ does not belong to the tuple, nothing is excluded, because the state in
  which all sampled cells above are empty arises when the column ends with the stone in row $$y$$. This gives
  $$2\,\bigl(S(x,y+1)-p(x,y+1)\bigr)$$ states.
- **Reachable.** The column ends directly below the cell, $$h=y$$, and all sampled cells above it are empty,
  which is one state.
- **Empty.** The column ends further down, $$h<y$$, which is possible only above the bottom row. Again all
  cells above are empty, which gives one state for $$y\ge1$$ and none for $$y=0$$.

With $$z(y)$$ the number of states without a stone, $$z(0)=1$$ and $$z(y)=2$$ for $$1\le y\le5$$, this yields the
recursion

$$
\begin{equation}
S(x,y) =
\begin{cases}
1, & y = 6,\\
S(x,y+1), & y<6 \text{ and } p(x,y)=0,\\
2\,\bigl(S(x,y+1)-p(x,y+1)\bigr) + z(y), & y<6 \text{ and } p(x,y)=1,
\end{cases}
\label{eq:recursion-cases}
\end{equation}
$$

and the count of column $$x$$ in equation \eqref{eq:product} is $$S(x,0)$$. The entries of the table above are
exactly these steps. Using $$p(x,y)$$ as a switch between the last two cases, $$S(x,y) = \bigl(1-p(x,y)\bigr)\,
S(x,y+1) + p(x,y)\,\bigl[2\,\bigl(S(x,y+1)-p(x,y+1)\bigr)+z(y)\bigr]$$, and multiplying out gives the recursion in
a single line for $$y<6$$,

\begin{equation}
S(x,y) = S(x,y+1)\,\bigl(1+p(x,y)\bigr) + p(x,y)\,\bigl(z(y)-2\,p(x,y+1)\bigr).
\label{eq:recursion}
\end{equation}

This form needs no case distinction and translates directly into code, which multiplies the column counts as in
equation \eqref{eq:product}:

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

In the thesis I derived the rule for three cell states as well, i.e. without the distinction between reachable
and empty cells. The recursion is then simpler: a cell without a stone has a single state, also in the bottom
row, and nothing is excluded above a stone, since the cell directly above a stone, if it holds no stone itself,
is simply empty. Every
sampled row thus contributes the step $$S(x,y)=2\,S(x,y+1)+1$$, and walking down a column with $$k$$ sampled cells
produces a Horner scheme, which is a geometric series,

\begin{equation}
2\,\bigl(\cdots 2\,(2\cdot1+1)+1\cdots\bigr)+1 = 1+2+\dots+2^k = 2^{k+1}-1.
\label{eq:three}
\end{equation}

With three states, the count of a column depends only on the number of its sampled cells and not on their
positions. With four states this is no longer the case: column d has 7 states with three cell states but 10 with
four, whereas column c has 15 in both cases.

<br>

## A Closed Form for a Column

#### Unrolling the Recursion

The four-state recursion can be solved in the same way as the three-state one, as long as we keep track of the
additional terms. Since rows without a cell of the tuple change nothing, only the $$k$$ sampled rows
$$r_1<\dots<r_k$$ of a column matter. Let $$C_j=S(x,r_j)$$ denote the count of the sampled cells in the rows
$$r_j,\dots,r_k$$, and $$C_{k+1}=1$$ the count above the topmost one, so that $$C=C_1$$ is the count of the
column. Between two sampled rows the count does not change, hence $$S(x,r_j+1)=C_{j+1}$$, and the cell
$$(x,r_j+1)$$ belongs to the tuple exactly if the next sampled row lies directly above, i.e. if $$g_{j+1}=0$$.
For the sampled rows, equation \eqref{eq:recursion-cases} thus becomes a recursion over $$j$$,

\begin{equation}
C_j = 2\,C_{j+1} + d_j, \qquad d_j = z(r_j) - 2\,[\,g_{j+1}=0\,],
\label{eq:linear}
\end{equation}

where the bracket is 0 for $$j=k$$, since no sampled cell lies above the topmost one. Walking down the column
means unrolling this recursion from the top, and every step doubles everything collected so far:

$$
C_1 = d_1 + 2\,C_2 = d_1 + 2\,d_2 + 4\,C_3 = \dots = d_1 + 2\,d_2 + \dots + 2^{k-1} d_k + 2^k\,C_{k+1},
$$

that is,

\begin{equation}
C = 2^k + \sum_{j=1}^{k} 2^{j-1}\,d_j.
\label{eq:unrolled}
\end{equation}

The cell $$r_j$$ enters with the weight $$2^{j-1}$$, the number of ways to colour the $$j-1$$ sampled cells below
it. For three cell states, $$d_j=1$$, and equation \eqref{eq:unrolled} is the geometric series of equation
\eqref{eq:three}.

For four states, we insert $$d_j$$. Its first part, $$z(r_j)$$, equals 2 except for a cell in the bottom row. Only
the lowest cell can lie there, and it does so exactly if $$g_1=r_1=0$$, so that $$z(r_1)=2-[\,g_1=0\,]$$ and
$$z(r_j)=2$$ for $$j\ge2$$. The second part, $$-2\,[\,g_{j+1}=0\,]$$, is a correction that the cell $$r_j$$
receives on behalf of the cell above it. Multiplied by the weight $$2^{j-1}$$, it becomes
$$-2^{j}\,[\,g_{j+1}=0\,]$$, and $$2^j$$ is exactly the weight of the cell $$r_{j+1}$$. Shifting the index by one,
the corrections therefore sum to $$-\sum_{j=2}^{k}2^{j-1}\,[\,g_j=0\,]$$, and both parts together give

$$
\sum_{j=1}^{k} 2^{j-1}\,d_j = \sum_{j=1}^{k} 2^{j-1}\,\bigl(2-[\,g_j=0\,]\bigr).
$$

In this sum, a cell in the bottom row and a cell directly on top of another sampled cell are treated alike. This
is plausible, since in both cases no unsampled row lies directly below the cell, so that the cell can only be
reachable if it is the lowest sampled cell without a stone. With $$\sum_{j=1}^{k}2^{j-1}\cdot 2=2^{k+1}-2$$ and $$\sum_{j=1}^{k}2^{j-1}=2^k-1$$, splitting the
cells by whether $$g_j$$ is zero or not finally yields

\begin{equation}
C = 3\cdot2^k - 2 - \sum_{j:\,g_j=0} 2^{j-1} = 2^{k+1} - 1 + \sum_{j:\,g_j>0} 2^{j-1}.
\label{eq:column}
\end{equation}

#### Reading the Closed Form

The first term on the right of equation \eqref{eq:column} is the count for three cell states from equation
\eqref{eq:three}, and the fourth state adds $$2^{j-1}$$ for every sampled cell with at least one unsampled row
directly below it. This can also be seen directly, without the recursion, which is a good check of the
derivation. Let us sort the states of a column by the lowest sampled cell without a stone, say $$r_j$$, as in the
figure above. The $$j-1$$ sampled cells below it hold stones, which can be coloured in $$2^{j-1}$$ ways, and all
sampled cells above it are empty, since the column ends at or below $$r_j$$. The cell $$r_j$$ itself is reachable
if the column ends exactly there, and empty if it ends in one of the $$g_j$$ unsampled rows directly below
$$r_j$$, which requires $$g_j>0$$. With three states, both cases look the same, which is why the three-state count
does not depend on the gaps. Adding the $$2^k$$ states in which all sampled cells hold stones gives

$$
C = 2^k + \sum_{j=1}^{k} 2^{j-1}\,\bigl(1+[\,g_j>0\,]\bigr),
$$

which is equation \eqref{eq:column} again, since $$2^k+\sum_{j=1}^{k}2^{j-1}=2^{k+1}-1$$. In the figure, column c has
no gaps, $$g_1=g_2=g_3=0$$, and its groups contain 1, 2, 4 and 8 states, $$2^4-1=15$$ in total. In column d, both
cells have an unsampled row below them, $$g_1=g_2=1$$, the first two groups double to 2 and 4 states, and together
with the 4 states with two stones the count is $$2^3-1+1+2=10$$.

A few special cases make the formula tangible. A single cell has 4 states, or 3 in the bottom row, where an empty
cell is always reachable. Cells stacked from the bottom without gaps have $$g_j=0$$ throughout and keep the
three-state count $$2^{k+1}-1$$, so that a column sampled completely has $$2^7-1=127$$ states, which agrees with a
direct count: a column with $$h$$ stones can be coloured in $$2^h$$ ways, and $$\sum_{h=0}^{6}2^h=127$$. In general,
the two forms of equation \eqref{eq:column} bound the count of a column with $$k$$ sampled cells from both sides,

\begin{equation}
2^{k+1}-1 \;\le\; C \;\le\; 3\cdot2^k-2,
\label{eq:bounds}
\end{equation}

where the upper bound requires an unsampled row below every sampled cell. Both bounds roughly double with every
further cell in a column, whereas the table grows by a factor of four per cell. One cell above the bottom row
keeps all 4 of its entries, but two cells in one column keep at most 10 of 16, and three at most 22 of 64. This
is the main reason why so few entries of a table are realisable. In code, equation \eqref{eq:column} is a short
loop:

```python
def count_column(rows: list[int]) -> int:
    """Realisable states of the sampled rows of one column, in closed form.

    With the sampled rows r_1 < ... < r_k, the count is 2**(k + 1) - 1, the count for three cell states,
    plus 2**(j - 1) for every r_j with at least one unsampled row directly below it: if r_j is the lowest
    sampled cell without a stone, it can then be reachable or empty.
    """
    r = sorted(rows)
    total = 2 ** (len(r) + 1) - 1
    for j in range(len(r)):
        gap = r[j] if j == 0 else r[j] - r[j - 1] - 1  # unsampled rows directly below r_{j+1}
        if gap > 0:
            total += 2**j
    return total
```

The recursion and the closed form agree with each other, and both agree with a brute-force enumeration of every
stack height and colouring, for all 63 possible sets of sampled rows in a column and for all 200 tuples of the
agent. The recursion is well suited to an algorithm, whereas the closed form shows at a glance where the count
comes from.

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
entries (1.6%) to 32,768 (50%), with a median of 4,096, and over all tuples it is 8.2%. As the bounds
\eqref{eq:bounds} suggest, what matters most is how many columns a tuple spans. The largest counts belong to tuples that spread their eight cells over six or
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
