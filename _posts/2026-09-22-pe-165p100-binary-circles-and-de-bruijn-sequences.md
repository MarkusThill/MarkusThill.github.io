---
layout: post
title: "Binary Circles, Hamiltonian Cycles and de Bruijn Sequences"
modified:
categories: [mathematics, algorithms, programming]
description: "A small combinatorial puzzle about circular binary words whose windows are all distinct turns out to be a question about Hamiltonian cycles in de Bruijn graphs. I count the arrangements, sum their numeric encodings up to a word length of 64 bits, and end with the multiplication trick that uses such a word to locate a set bit."
tags: [de-bruijn, graph-theory, hamiltonian-cycles, eulerian-circuits, combinatorics, backtracking, bit-twiddling, python, c]
thumbnail: assets/img/2026-09-22-binary-circles-de-bruijn/circles-n3.svg
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-09-22T12:00:00+02:00
pretty_table: true
related_posts: true
tabs: true
images:
  compare: false
  slider: false
---

Some time ago I worked through a small combinatorial exercise about binary digits arranged in a
circle, and I recently came across the notebook again while looking for something else. The
exercise itself is quickly stated and can be solved in a few lines of Python, but the object it
produces has a name, a literature going back to the nineteenth century, and at least one
application that I have used in completely unrelated code. That combination seemed worth a post:
the puzzle is the excuse, and the structure behind it is the actual subject.

The plan is to first state the problem, then translate it into a question about walks in a directed
graph, count the solutions with a classical theorem, and finally push the enumeration as far as my
machine allows. Along the way we will see that the numbers produced by the puzzle have a good deal
of internal structure, most of which is visible in the positions of the ones alone.

<!--more-->

<br>
## The Problem

Take $$2^N$$ binary digits and arrange them in a circle. Reading clockwise and starting at any of
the $$2^N$$ positions yields a window of $$N$$ consecutive digits, so such a circle offers exactly
$$2^N$$ windows, which is also the number of distinct binary strings of length $$N$$. The question
is whether the digits can be chosen so that all these windows are pairwise distinct. If they can,
then by a counting argument every one of the $$2^N$$ strings of length $$N$$ occurs exactly once,
including the window consisting of $$N$$ zeros. Note that the length $$2^N$$ is the largest one for
which distinctness is possible at all, since a circle of length $$L$$ has $$L$$ windows and these
can only be pairwise distinct if $$L \le 2^N$$.

For $$N = 3$$ there are two such circles, if we regard arrangements that differ only by a rotation
as the same. Their windows, read clockwise from the position of the all-zero window, are
$$000, 001, 010, 101, 011, 111, 110, 100$$ in the first case and
$$000, 001, 011, 111, 110, 101, 010, 100$$ in the second.

Since each valid circle contains the all-zero window exactly once, we can use that window as a
canonical starting point and encode the circle as a plain binary number: begin at the first digit
of the all-zero window, walk clockwise, and read the $$2^N$$ digits as the binary representation of
an integer, most significant bit first. The encoding is well defined precisely because the starting
point is unique, and it identifies all rotations of the same circle with each other. For $$N = 3$$
the two arrangements become

$$
\begin{align}
00010111_2 &= 23,\\
00011101_2 &= 29.
\end{align}
$$

{% include figure.liquid loading="eager"
   path="assets/img/2026-09-22-binary-circles-de-bruijn/circles-n3.svg"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="85%"
   caption="The two circles of eight binary digits whose 3-digit clockwise windows are pairwise distinct. The three highlighted digits form the all-zero window, which occurs exactly once in every valid circle and therefore serves as the starting point of the encoding. Reading clockwise from there gives 00010111 and 00011101, that is 23 and 29." %}

Writing $$S(N)$$ for the sum of the encodings of all valid circles of length $$2^N$$, we thus have
$$S(3) = 23 + 29 = 52$$. The quantity I originally wanted was $$S(5)$$, which needs circles of
$$32$$ digits, and as we will see the same program also reaches $$S(6)$$ with a bit of patience.

<br>
## A Graph on the Windows

The condition that all windows are distinct is a global one, and it is not obvious how to search
for such circles directly. It becomes much more tractable once we stop thinking about the circle
and start thinking about the *transition* from one window to the next. If the current window is the
$$N$$-bit string $$v$$, then the next window clockwise is obtained by shifting $$v$$ one position
to the left, which discards its leading bit, and appending the next digit $$b$$ of the circle, for
example

$$
00101 \;\xrightarrow{\;b\,=\,1\;}\; 01011.
$$

Accordingly, we can define a directed graph whose $$2^N$$ vertices are the $$N$$-bit strings and
which has an edge from $$v$$ to $$u$$ whenever $$u$$ can be reached from $$v$$ in this way, that is,
whenever the last $$N-1$$ bits of $$v$$ agree with the first $$N-1$$ bits of $$u$$. Every vertex
then has exactly two outgoing edges (for the two possible choices of $$b$$) and, by the same
argument applied backwards, exactly two incoming edges, so the graph has $$2^{N+1}$$ edges in
total. The two strings $$0\dots0$$ and $$1\dots1$$ carry a self-loop, since shifting them and
appending the appropriate bit reproduces them.

In this language a valid circle is a closed walk that visits every vertex exactly once, in other
words a **Hamiltonian cycle**. The digits of the circle are simply the labels of the traversed
edges, and the encoding defined above is the concatenation of the leading bits of the visited
vertices, starting at the all-zero vertex.

{% include figure.liquid loading="eager"
   path="assets/img/2026-09-22-binary-circles-de-bruijn/debruijn-graph-n3.svg"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="80%"
   caption="The graph on all 3-bit windows. An edge leads from one window to the next if the latter can be obtained by shifting and appending a bit, which gives two outgoing and two incoming edges per vertex, including a self-loop at 000 and at 111. The highlighted cycle visits every vertex exactly once and corresponds to the circle 00010111; the second solution for N = 3 runs through the same graph and differs from it in four of its eight edges." %}

<br>
## Hamiltonian Cycles, Eulerian Circuits and de Bruijn Sequences

The graph just constructed is the **de Bruijn graph** $$B(2,N)$$, and the circular words we are
after are the binary **de Bruijn sequences** of order $$N$$. They are named after Nicolaas de Bruijn
{% cite deBruijn46 --file thesis %}, although the binary case had already been settled by Flye
Sainte-Marie almost fifty years earlier {% cite FlyeSainteMarie1894 --file thesis %}, a fact that
was apparently forgotten in the meantime and only rediscovered later.

Searching for Hamiltonian cycles is in general an unpleasant business, but here there is a way
around it. If we instead take the $$(N-1)$$-bit strings as vertices and let every $$N$$-bit string
be an *edge* (from its first $$N-1$$ bits to its last $$N-1$$ bits), we obtain the smaller graph
$$B(2,N-1)$$, and the requirement that every $$N$$-bit string occurs exactly once turns into the
requirement that every edge is traversed exactly once. Hamiltonian cycles in $$B(2,N)$$ therefore
correspond one to one with **Eulerian circuits** in $$B(2,N-1)$$, which is just the statement that
$$B(2,N)$$ is the line graph of $$B(2,N-1)$$. Since $$B(2,N-1)$$ is connected and every vertex has
as many incoming as outgoing edges, Eulerian circuits are guaranteed to exist, and hence so are the
circles we are looking for. Unlike the Hamiltonian problem, the Eulerian one is easy: a circuit can
be built greedily in linear time, and it can also be *counted*.

<br>
## How many Circles there are

The counting is done by the BEST theorem, named after de Bruijn, van Aardenne-Ehrenfest, Smith and
Tutte {% cite TutteSmith41 --file thesis %}{% cite AardenneEhrenfest51 --file thesis %}. It states
that in a connected digraph in which every vertex has equal in- and out-degree, the number of
Eulerian circuits, counted up to their starting point and therefore with exactly the identification
of rotations that our encoding performs, equals the number of spanning arborescences rooted at an
arbitrary fixed vertex, multiplied by $$\prod_v (\deg v - 1)!$$. For $$B(2,N-1)$$ every out-degree is two, so all factorials
are $$1! = 1$$ and the count reduces to the number of arborescences alone, which in turn is a
determinant of a reduced Laplacian by the matrix-tree theorem. For Eulerian digraphs that number
does not depend on the chosen root, so the determinant can be taken at the most convenient vertex.

Carrying this out for the binary case gives

$$
\begin{equation}
M(N) = 2^{\,2^{N-1}-N}
\label{eq:count}
\end{equation}
$$

circles of length $$2^N$$, so $$M(3) = 2$$, $$M(4) = 16$$, $$M(5) = 2048$$ and already
$$M(6) = 2^{26} = 67{,}108{,}864$$. Rather than trusting the formula, I computed the determinant
with exact rational arithmetic and compared it with the number of circles found by brute force:

```python
def arborescences(m):
    """Spanning arborescences of B(2,m) rooted at vertex 0, by the matrix-tree theorem."""
    N = 1 << m
    idx = [v for v in range(N) if v != 0]
    pos = {v: i for i, v in enumerate(idx)}
    M = [[Fraction(0)] * len(idx) for _ in idx]
    for v in idx:
        M[pos[v]][pos[v]] = Fraction(2)
        for bit in (0, 1):
            u = ((v << 1) | bit) & (N - 1)
            if u != 0:
                M[pos[v]][pos[u]] -= 1
    # ... Gaussian elimination, returns the determinant as an integer
```

Both numbers agree for all orders up to $$N = 5$$, which is as far as the enumeration is cheap. The
growth is doubly exponential, and the consequence for the rest of this post is that $$N = 6$$ with
its $$67$$ million circles is roughly where an exhaustive enumeration stops being comfortable:
$$M(7)$$ is already $$2^{57}$$, or about $$1.4 \cdot 10^{17}$$.

<br>
## A depth-first Search over the Windows

The search itself is a textbook backtracking over the graph. We start at the all-zero vertex,
repeatedly shift in a $$0$$ or a $$1$$, refuse any window that has been visited before, and record
a solution whenever all $$2^N$$ vertices have been used. My first version stored the visited
windows as strings, which is slow but has the advantage that the search reads like the problem
statement (the enclosing function that supplies `n_bits` is omitted here):

```python
def search(last_substring, sequence, solutions):
    """Recursively extend a sequence with previously unseen substrings."""
    depth = len(sequence)

    # A complete sequence contains every possible n-bit substring once.
    if depth == 2**n_bits:
        solutions.append(sequence)
        return

    # Towards the end, only zeros are allowed so that the sequence
    # closes back onto the initial all-zero substring.
    bits = ("0", "1") if depth < 2**n_bits - n_bits + 1 else ("0",)

    for bit in bits:
        # Shift the current substring left and append the next bit.
        new_substring = last_substring[1:] + bit

        # Every n-bit substring may occur only once.
        if new_substring in sequence:
            continue

        search(new_substring, sequence + [new_substring], solutions)
```

The one part of this that deserves an explanation is the restriction of the alphabet near the end.
A walk that has visited all vertices is not yet a solution: it also has to close, that is, the last
vertex must have an edge back to the all-zero vertex. Only $$10\cdots0$$ has such an edge, and
working backwards, the vertex before it must be $$\ast10\cdots0$$, the one before that
$$\ast\ast10\cdots0$$, and so on. All of these end in a zero, hence the last $$N-1$$ edges of any
solution carry the label $$0$$. Seen from the circle rather than from the graph, this is not an
extra insight at all: those $$N-1$$ digits are the ones that wrap around the end of the word and
coincide with the leading zeros of the all-zero window, so they were fixed from the very beginning.
Hard-coding them merely saves the search from rediscovering the same fact $$2^{N-1}$$ times.

<br>
## Accumulating the Number during the Search

Collecting all solutions and converting them afterwards is wasteful, since the only thing we want
is a sum. It is cheaper to build the value along the way: whenever a new window is appended, its
leading bit is the next digit of the circular word, so the running value only has to be shifted
once and combined with that bit. The visited set also no longer needs to be rebuilt at every node
and can be maintained by adding and removing single elements:

```python
def solve(n_bits: int) -> int:
    size = 1 << n_bits
    start = "0" * n_bits
    cutoff = size - n_bits + 1
    seen: set[str] = {start}
    total = 0

    def dfs(last_substring: str, depth: int, value: int) -> None:
        nonlocal total

        if depth == size:
            total += value
            return

        bits = ("0", "1") if depth < cutoff else ("0",)

        for bit in bits:
            new_substring = last_substring[1:] + bit
            if new_substring in seen:
                continue

            seen.add(new_substring)
            dfs(new_substring, depth + 1, (value << 1) | (new_substring[0] == "1"))
            seen.remove(new_substring)   # undo the choice when backtracking

    dfs(start, 1, 0)
    return total
```

On my rather elderly notebook (an Intel Core i7-3520M at 2.9 GHz, CPython 3.10) the first version
takes between $$0.18$$ and $$0.27$$ seconds for $$N = 5$$ and the second between $$0.09$$ and
$$0.11$$ seconds, measured over three runs each. The factor of roughly two is pleasant but not
dramatic, and both are far below the threshold where it would be worth thinking about.

What the runtimes hide is how effective the pruning is. Counting the nodes of the search tree gives
$$23$$ nodes for $$N = 3$$, $$354$$ for $$N = 4$$ and $$92{,}636$$ for $$N = 5$$, against $$2$$,
$$16$$ and $$2048$$ solutions respectively. For $$N = 5$$ that is about $$45$$ nodes per solution
while every solution is already $$32$$ vertices deep, so the overwhelming majority of the visited
nodes lie on paths that do lead somewhere. A dead end can only occur when both successors of the
current window have already been used, and for $$N = 5$$ this happens at $$11{,}562$$ of the
$$92{,}636$$ nodes, so roughly one node in eight is a wasted branch.

<br>
## The same Search in C with a 64-Bit visited Set

For $$N = 6$$ the $$67$$ million solutions are out of reach for CPython, but the problem has a
property that makes a C implementation particularly compact: as long as $$N \le 6$$, the number of
windows is at most $$64$$, so the entire set of visited windows fits into a single `uint64_t`. The
test whether a window has been seen is then one shift and one AND, and marking and unmarking a
window is a single OR and AND-NOT. The state of the search is held in four constants that are set
once in `main` and three variables that change while the search runs:

```c
static int n_bits;              /* window width n, between 2 and 6         */
static int n_windows;           /* 2^n windows, the vertices of the graph  */
static int window_mask;         /* 2^n - 1, cuts the shift register to n   */
static int forced_zeros_from;   /* from here on, only a 0 may be appended  */

static uint64_t used;           /* bit i is set if window i is in the walk */
static unsigned __int128 sum_of_circles;
static uint64_t n_circles, n_nodes;
```

For the largest case that this program handles, $$N = 6$$, these hold `n_bits` $$= 6$$,
`n_windows` $$= 64$$, `window_mask` $$= 63$$ and `forced_zeros_from` $$= 59$$, while `used` starts
out as $$1$$, because the walk begins on the all-zero window, which is window number $$0$$. The
recursion itself carries three arguments and is called as `dfs(0, 1, 0)`:

```c
static void dfs(int window, int placed, uint64_t digits) {
  n_nodes++;
  if (placed == n_windows) {    /* all windows used, the circle is complete */
    sum_of_circles += digits;
    n_circles++;
    return;
  }

  /* The last n-1 digits of every circle are the zeros that wrap around. */
  int max_digit = (placed >= forced_zeros_from) ? 0 : 1;

  for (int digit = 0; digit <= max_digit; digit++) {
    /* shift the window one position on and append the new digit */
    int next_window = ((window << 1) | digit) & window_mask;

    if (used >> next_window & 1) continue;          /* window already taken */
    used |= (uint64_t)1 << next_window;

    /* the digit dropped by the shift is the next digit of the circle */
    dfs(next_window, placed + 1,
        (digits << 1) | (uint64_t)(next_window >> (n_bits - 1)));

    used &= ~((uint64_t)1 << next_window);          /* undo when backtracking */
  }
}
```

#### The three Arguments and what they hold

The argument `window` is the window the walk currently stands on, stored as the integer that its
$$N$$ digits form, so for $$N = 5$$ it is a number between $$0$$ and $$31$$. The argument `placed`
counts how many windows have been placed so far, including the all-zero window the search starts
on, and therefore runs from $$1$$ up to `n_windows`. The argument `digits` is the part of the
circular word that is already determined, again read as a binary number, and the invariant is that
after `placed` windows it holds the first `placed` digits of the circle. When the first branch of
the function is taken, `digits` consequently contains the complete encoding of a valid circle and
can be added to the sum without any conversion.

The visited set `used` is a global rather than a fourth argument, because it is the only piece of
state that has to be undone when the recursion returns. The other three unwind by themselves, since
each stack frame keeps its own copy.

#### The Window as a Shift Register

The line

```c
int next_window = ((window << 1) | digit) & window_mask;
```

performs the transition of the graph in three operations. Shifting left moves the window one
position clockwise, the OR appends the new digit at the right end, and the AND with `window_mask`
discards the digit that has been pushed out at the left end. This is precisely the edge relation
described earlier, namely that the last $$N-1$$ digits of `window` are the first $$N-1$$ digits of
`next_window`. The window therefore behaves exactly like a shift register of width $$N$$ that is
clocked once per digit of the circle.

Because `next_window` is itself a number below $$2^N \le 64$$, it can serve directly as a bit index
into `used`. The test `used >> next_window & 1` parses as `(used >> next_window) & 1` and asks
whether that window is already part of the walk, the OR marks it before descending, and the AND with
the complement clears it again once the branch is exhausted. The casts to `uint64_t` in the two
marking lines are not cosmetic: for $$N = 6$$ the shift count reaches $$63$$, and shifting a plain
`int` that far is undefined behaviour, so leaving the cast out would produce a bug that only shows
up in the largest case.

#### Why the leading Bit of the new Window is the next Digit

The digit that the search chooses in the loop is *not* the next digit of the answer, since it
belongs to a window further ahead in the circle. The digit that is finished at this moment is the
one that falls off at the left, which is the leading bit of the new window, obtained as
`next_window >> (n_bits - 1)`. Put differently, the digits discarded by the shift register, in the
order in which they are discarded, are the circular word itself, and this is why one shift and one
OR are enough to maintain `digits`. Writing the first of the two solutions for $$N = 3$$ as
$$w_0w_1\dots w_7 = 00010111$$, the first four steps run as follows:

| `placed` | `window` | corresponds to | leading bit | `digits` |
|---:|---:|:--|---:|---:|
| 1 | `000` | $$w_0w_1w_2$$ | | `0` |
| 2 | `001` | $$w_1w_2w_3$$ | $$w_1 = 0$$ | `00` |
| 3 | `010` | $$w_2w_3w_4$$ | $$w_2 = 0$$ | `000` |
| 4 | `101` | $$w_3w_4w_5$$ | $$w_3 = 1$$ | `0001` |

#### The forced Zeros and the missing Closure Test

The assignment `int max_digit = (placed >= forced_zeros_from) ? 0 : 1;` lets the loop run over both
digits during the ordinary part of the search and over the digit $$0$$ alone during the last $$N-1$$
steps. As discussed above, those digits are the ones that wrap around the end of the word onto the
leading zeros of the all-zero window, so they were fixed before the search started.

This also explains why the function never tests whether the walk closes. After $$N-1$$ forced zeros
the final window ends in $$N-1$$ zeros, and since the all-zero window has been taken since the very
first step, that window can only be $$10\cdots0$$, which does have an edge back to the start. Should
one of the forced steps run into a window that is already in use, the branch dies at the `continue`
and never reaches `placed == n_windows`. Arriving at the terminal case is therefore equivalent to
having found a closed circle, and no separate check is needed.

#### Range of the Accumulator and Measurements

The accumulator needs some care. A circle of $$64$$ digits whose first six digits are zero encodes a
number below $$2^{58}$$, and summing $$2^{26}$$ such numbers can reach $$2^{84}$$, so
`sum_of_circles` is declared as an `unsigned __int128` and printed digit by digit, since there is no
format specifier for it. With `gcc -O2` on the same machine, the run for $$N = 5$$ finishes in about
a millisecond, and the run for $$N = 6$$ visits $$5{,}504{,}163{,}339$$ nodes and takes between
$$58$$ and $$86$$ seconds over three runs, depending on what else the machine was doing at the
time, which corresponds to something between $$64$$ and $$95$$ million nodes per second on a single
core. The results are

| $$N$$ | digits $$2^N$$ | circles $$M(N)$$ | $$S(N)$$ |
|---:|---:|---:|---:|
| 2 | 4 | 1 | 3 |
| 3 | 8 | 2 | 52 |
| 4 | 16 | 16 | 51,504 |
| 5 | 32 | 2,048 | 209,110,240,768 |
| 6 | 64 | 67,108,864 | 14,617,787,158,279,466,864,345,088 |

and the values of $$M(N)$$ obtained by counting agree with \eqref{eq:count} in every case, which is
a reassuring cross-check on both the formula and the search. The Python and the C program produce
identical node counts and identical sums for $$N \le 5$$.

<br>
## Where the Ones sit in the Circle

Since the encoding is a positional number, the sum $$S(N)$$ can be written as

$$
\begin{equation}
S(N) = \sum_{i=0}^{L-1} c_i \, 2^{\,L-1-i}, \qquad L = 2^N,
\label{eq:positions}
\end{equation}
$$

where $$c_i$$ is the number of circles that carry a one at position $$i$$. These counts are worth
looking at, because several of them are fixed by the problem alone. The first $$N$$ digits are the
all-zero window, so $$c_0 = \dots = c_{N-1} = 0$$. The digit at position $$N$$ must be a one,
because otherwise the window starting at position $$1$$ would be a second all-zero window, hence
$$c_N = M(N)$$. The same argument applied to the window that starts at the last position, which
reads $$w_{L-1}0\cdots0$$ after wrapping around, forces the last digit to be a one as well, so
$$c_{L-1} = M(N)$$. Finally, every circle contains exactly $$2^{N-1}$$ ones, since the ones are in
bijection with the windows that begin with a one.

{% include figure.liquid loading="eager"
   path="assets/img/2026-09-22-binary-circles-de-bruijn/position-counts-n5.svg"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="95%"
   caption="For N = 5, the number of the 2048 circles that carry a one at each of the 32 positions. The first five positions are zero by construction, positions 5 and 31 are one in every circle, and the remaining counts are symmetric with respect to the dashed axis, which is a consequence of the fact that reversing a circle produces another valid circle." %}

The plot shows a clear symmetry, and the reason is that reversing a circular word preserves the
property we are interested in: reading the windows backwards turns every window into its reverse,
and distinct windows stay distinct. Reversal does move the all-zero window, however, so the reversed
word has to be rotated back into canonical form. If the original word is $$w_0 w_1 \dots w_{L-1}$$
with $$w_0 = \dots = w_{N-1} = 0$$, the canonical reversal is
$$w'_j = w_{(N-1-j) \bmod L}$$, which maps position $$i$$ to position $$(N-1-i) \bmod L$$. The
counts must therefore satisfy $$c_i = c_{N-1-i \bmod L}$$, which for $$i \ge N$$ is exactly the
palindrome visible in the figure, with the axis at $$i = (N+L-1)/2$$. For $$N = 4$$ the counts are
small enough to print,

$$
(c_i)_{i=0,\dots,15} = (0,0,0,0,\;16,8,10,13,6,11,11,6,13,10,8,16),
$$

and the palindrome from position $$4$$ onwards is easy to check by eye. Complementing all digits is
a second symmetry of the same kind, and both were verified against the enumerated solutions for all
$$N \le 5$$, as was identity \eqref{eq:positions}. The counts do not, unfortunately, seem to follow
a pattern that would let one compute $$S(N)$$ without enumerating the circles: apart from the fixed
positions and the symmetry, the numbers $$1120, 1368, 1260, 1100, \dots$$ for $$N = 5$$ look
thoroughly irregular to me.

<br>
## The smallest and the largest Circle

Two of the circles can be written down without any search. The smallest encoding is the
lexicographically least de Bruijn sequence, and it is obtained by concatenating, in lexicographic
order, all Lyndon words over $$\{0,1\}$$ whose length divides $$N$$ {% cite Fredricksen78 --file thesis %}.
A Lyndon word is a word that is strictly smaller than all of its own rotations, and Duval's
algorithm generates the required ones in a few lines. For $$N = 5$$ the Lyndon words are

$$
0,\; 00001,\; 00011,\; 00101,\; 00111,\; 01011,\; 01111,\; 1,
$$

and their concatenation is $$00000100011001010011101011011111$$, that is $$73{,}743{,}071$$, which
is indeed the smallest value the enumeration produces. The largest encoding, $$131{,}913{,}257$$,
is produced by the opposite greedy rule: start at the all-zero window and always append a one if the
resulting window has not been used yet. Both rules were checked against the full enumeration for
$$N \le 5$$. It is tempting to guess that the largest circle is simply the reverse of the smallest
one, which is true for $$N = 3$$, where $$23$$ and $$29$$ are reverses of each other, but it already
fails for $$N = 4$$ and $$N = 5$$.

<br>
## An Application: finding the Position of a set Bit

The reason I remembered these words at all is that they show up in bit manipulation. Suppose a
$$64$$-bit variable has exactly one bit set and we want its index. In an earlier post on
[bit-twiddling tricks](/blog/2024/soa-few-bit-twiddling-tricks/) I used a divide-and-conquer routine
for this, which narrows the position down in six steps. There is an alternative that needs one
multiplication, one shift and one table lookup {% cite Leiserson98 --file thesis %}, and its magic
constant is precisely a de Bruijn word of order six. Taking the smallest such word from the previous
section, $$0000001000011000101000111001001011001101001111010101110110111111$$, gives the constant
`0x0218a392cd3d5dbf`, and the routine becomes

```c
static const uint64_t DEBRUIJN64 = 0x0218a392cd3d5dbfULL;
static int index64[64];

static void init_table(void) {
  for (int k = 0; k < 64; k++)
    index64[(DEBRUIJN64 << k) >> 58] = k;
}

static int bit_pos(uint64_t x) {   /* x must have exactly one bit set */
  return index64[(x * DEBRUIJN64) >> 58];
}
```

#### The same Trick in eight Bits

The $$64$$-bit constant is unreadable, so it is easier to watch the mechanism in the small case,
with the order-3 word $$00010111$$ from the beginning of this post as an eight-bit constant and the
topmost three bits kept after each shift:

| $$k$$ | the constant shifted left by $$k$$ | top three bits |
|---:|:--|---:|
| 0 | `00010111` | `000` |
| 1 | `00101110` | `001` |
| 2 | `01011100` | `010` |
| 3 | `10111000` | `101` |
| 4 | `01110000` | `011` |
| 5 | `11100000` | `111` |
| 6 | `11000000` | `110` |
| 7 | `10000000` | `100` |

The right-hand column runs through all eight three-bit patterns without repeating one, and this is
no accident: those patterns are the eight windows of the circle, read in the order in which they
occur. Shifting left by $$k$$ moves the window that starts at position $$k$$ to the top of the
register, and since the windows of a de Bruijn word are pairwise distinct, the topmost bits are a
fingerprint that identifies the shift amount uniquely.

One detail is worth pausing on, since it explains why the constant has to be in the canonical form
that the puzzle uses. A shift is not a rotation, and it pulls in zeros from the right instead of
the digits that wrap around the circle. For $$k = 6$$ the genuine circular window would be
$$w_6w_7w_0 = 110$$ while the register contains $$w_6w_70 = 110$$, and for $$k = 7$$ the circular
window $$w_7w_0w_1 = 100$$ meets the register's $$w_700 = 100$$. Both agree because the word begins
with $$N$$ zeros, so the zeros entering from the right are exactly the digits that would have
wrapped. Any de Bruijn word normalised the way the encoding of this post normalises it, that is,
starting at its all-zero window, therefore serves as a constant, whereas an arbitrary rotation of
one does not.

#### Building the Table and reading it back

`init_table` walks that table forward once and stores each shift amount under its fingerprint. The
shift by $$58 = 64 - 6$$ keeps the topmost six bits, which is the window width belonging to a
$$64$$-bit constant, and because all $$64$$ fingerprints are distinct, the loop fills all $$64$$
slots of `index64` without a single collision. The array is thus a perfect hash table that is
constructed rather than searched for.

The function `bit_pos` then inverts that map. If `x` has exactly one bit set, say bit $$k$$, then
`x * DEBRUIJN64` is the same thing as `DEBRUIJN64 << k`, because multiplying by $$2^k$$ is a left
shift by $$k$$ positions. The topmost six bits of the product are therefore the fingerprint that
`init_table` has already filed under $$k$$, and the lookup hands $$k$$ back. The multiplication is
the entire trick: it performs a shift whose amount is not known in advance, which is precisely the
quantity we are looking for.

#### A worked Example

Let the bit in question be bit $$10$$, so that `x` is $$2^{10} =$$ `0x400`. While the table was
built, the iteration $$k = 10$$ computed `DEBRUIJN64 << 10 = 0x628e4b34f576fc00`, whose top six bits
are `011000`, that is $$24$$, and it therefore set `index64[24] = 10`. At lookup time,
`bit_pos(0x400)` multiplies $$2^{10}$$ by the constant, arrives at the same
`0x628e4b34f576fc00`, shifts it right by $$58$$ to obtain $$24$$ again, and reads `index64[24]`,
which is $$10$$.

The product overflows, and the overflow is needed rather than tolerated: $$2^{10}$$ times the
constant does not fit into $$64$$ bits, and reducing it modulo $$2^{64}$$ discards exactly those
bits that a shift would have pushed out of the register. C defines this wraparound for unsigned
arithmetic, which is why both the constant and the argument are `uint64_t`; with a signed type the
same code would be undefined behaviour.

#### Practical Remarks

The routine insists on exactly one bit being set, and the usual way to arrange that is to call it
as `bit_pos(v & -v)`, since `v & -v` isolates the lowest set bit of `v`, so that the two together
count the trailing zeros. Whether this is faster than the divide-and-conquer version depends on the
machine, as it trades six dependent steps for one multiplication, one shift and one cached load,
and on anything recent one would use a compiler intrinsic such as `__builtin_ctzll` instead, which
maps to a single instruction. What I find appealing is that the enumeration above is not only a
puzzle solver but also a generator for these constants: the table produced from its smallest
solution is correct for all $$64$$ positions, which I verified by running `bit_pos` on every power
of two.

<br>
## Limitations and open Ends

The main limitation is the doubly exponential growth. Every step from $$N$$ to $$N+1$$ squares the
number of circles, so $$S(7)$$ would require about $$1.4 \cdot 10^{17}$$ of them. Assuming a
similar number of search nodes per circle as for $$N = 6$$, that is roughly $$10^{19}$$ nodes, and
even at the fastest rate measured above it would keep a single core busy for a few thousand years.
The bitset trick also stops at $$N = 6$$, since $$128$$ windows no longer fit into a machine word.
Neither is a real obstacle for the original question, but it does mean that $$S(N)$$ is, as far as
I can see, only accessible by enumeration, whereas the *number* of circles $$M(N)$$ has the closed
form \eqref{eq:count}. I spent a while looking for a way to compute the position counts $$c_i$$
directly, for instance by counting Eulerian circuits that use a given edge at a given step, but did
not find anything that beats enumeration; if such a method exists, it would immediately give
$$S(7)$$ and beyond.

A second open end concerns the symmetries. Reversal and complementation both act on the set of
circles, and for $$N \le 5$$ neither has a fixed point apart from the trivial case $$N = 2$$. The
orbits of these two involutions would halve or quarter the work of an enumeration, but only if one
could decide cheaply which representative to keep, and the canonical rotation that the encoding
requires makes that less straightforward than it sounds.

<br>
## Source Code

The notebook this post grew out of contains the two Python versions shown above. The C enumerator,
the matrix-tree cross-check, the Lyndon word construction, the bit-scan test and the scripts that
produce the figures are kept next to the sources of this site in `tools/debruijn/`. All numbers
quoted in this post come from running exactly that code on the machine described above.

<br>
## References

<div class="publications">
{% bibliography --file thesis --cited --group_by none %}
</div>

<br>

**Related posts:** The routine for locating a single set bit, and a few other techniques for working
with bit fields, are discussed in [A few Bit-Twiddling Tricks](/blog/2024/soa-few-bit-twiddling-tricks/).
For another exhaustive search that only became feasible after the state was packed into machine
words, see [Solving Peg Solitaire](/blog/2024/solving-peg-solitaire/).
