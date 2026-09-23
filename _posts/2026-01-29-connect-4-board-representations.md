---
layout: post
title: "Building Intelligent Agents for Connect-4&#58; Board Representations"
modified: 2026-06-16T09:00:51+01:00
categories: [programming]
description: "How CFour and BitBully encode a Connect-4 position in 64-bit words, and how guard bits, shifts, exact position codes, and generated masks change the operations used by the search."
tags: [Connect-4, AI, tree-search, alpha-beta, minimax, transposition tables, opening databases, move ordering, bitboards]
thumbnail: assets/img/2026-01-29-connect-4-board-representations/thumbnail.png
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-01-29T09:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
series: connect4-search
series_part: 3
---

{% include series_connect4.liquid %}

The representation of the board is an elementary component of the agent. Very large parts of
the program require this data structure as a basis, so special care has to be taken in its
specification. This applies in particular to tree-search procedures such as the alpha-beta
search of the previous post, in which an enormous number of operations are performed on this
data structure. Reducing the search to its most basic operations quickly reveals that only
three of them really matter: performing a move, undoing it, and identifying terminal states.
Since the game tree of Connect-4 contains roughly $$10^{21}$$ leaves
{% cite Allis94 --file thesis %}, even a small inefficiency in any of the three is multiplied
across a large part of the search.

Over the years I have written two Connect-4 engines, roughly thirteen years apart, and they
answer this question rather differently. The 2012 Java framework
[CFour](https://github.com/MarkusThill/Connect-Four) uses one layout, while
[BitBully](https://github.com/MarkusThill/BitBully), the more recent C++ solver with Python
bindings, uses another. Neither of the two is wrong, and in my experience the differences
between them are the most instructive part of the story, so I will show both side by side
throughout this post.

<!--more-->

<br>

## The obvious Representation and its Drawbacks

Probably the simplest representation of the board is achieved in most games by using a one-
or two-dimensional array. For Connect-4, a $$7 \times 6$$ integer matrix would be the natural
choice, with `0` for an empty cell, `1` for Yellow and `2` for Red. For less complex games
such as Tic-Tac-Toe this approach is entirely reasonable, since efficiency is not particularly
important there and the representation simplifies programming in many parts of the program.

For more complex games such as Connect-4, Nine Men's Morris, checkers or chess, such a
representation is often inconvenient. The reason is the search for closed chains of four,
which takes place in practically all nodes of the game tree and can easily become the
bottleneck of an agent. With an array, finding four in a row means walking the grid: for every
cell, in every direction, one has to look three cells ahead. Even when the search is
restricted to the neighbourhood of the stone that was just played, this amounts to dozens of
bounds-checked array accesses per node, and these accesses have to be executed many millions
of times per second.

For this reason both of my agents use so-called bit boards, which have some basic advantages
over simple arrays. The underlying observation is that a cell of the board has three possible
states, but a single bit board only ever has to answer one question at a time. If we ask which
cells are occupied by Yellow, the answer is 42 yes/no bits and therefore fits into a single
64-bit variable; asking the same for Red gives us a second one. Two integers thus describe a
position completely, and the CPU can then process all 42 cells at once with a single bitwise
instruction.

In chess programming, bit boards (often in combination with simple arrays) have been used for
a long time to represent the board. The number of 64 fields on a chessboard makes them
particularly attractive, since most systems today have 64-bit architectures and such variables
can be processed directly with a single CPU instruction. Games like Othello or checkers with
their 64 fields benefit in the same way. Since a bit board does not contain any information
about the type of a piece, only pieces of the same type can be held in one of them; in chess,
for instance, all white pawns could be kept in a 64-bit variable, but the bishops would need
their own bit board. Connect-4 knows only two types of tokens, which is why two bit boards —
one per player — are sufficient here.

The basic operations then become almost trivial. The following listings show the same three
operations — placing a token, taking it back, and testing for a full board — in both engines:

{% tabs basics %}

{% tab basics C++ (BitBully) %}

```cpp
// Place a stone. (The first line switches the side to move; see below.)
void inline playMoveFastBB(const TBitBoard mv) {
  m_bActivePTokens ^= m_bAllTokens;
  m_bAllTokens     ^= mv;            // mv has exactly one bit set
  m_movesLeft--;
}

// Take it back: there is no undo. The search plays on a copy instead.
[[nodiscard]] Board inline playBitMaskOnCopy(const TBitBoard mv) const {
  Board b = *this;
  b.playMoveFastBB(mv);
  return b;
}

// Board full?
[[nodiscard]] inline TMovesCounter movesLeft() const { return m_movesLeft; }
```

{% endtab %}

{% tab basics Java (CFour) %}

```java
// Place a stone in a column: look up the mask, set the bit, bump the height.
public void putPiece(int player, int col) {
    long mask = fieldMask[col][colHeight[col]++];
    if (player == PLAYER1) fieldP1 |= mask;
    else                   fieldP2 |= mask;
}

// Take it back: the same mask, inverted, and drop the height again.
public void removePiece(int player, int col) {
    long mask = ~fieldMask[col][--colHeight[col]];
    if (player == PLAYER1) fieldP1 &= mask;
    else                   fieldP2 &= mask;
}

// Board full? Compare all 42 playable cells in one operation.
public boolean isDraw() {
    return ((fieldP1 | fieldP2) & FIELDFULL) == FIELDFULL;
}
```

{% endtab %}

{% endtabs %}

The method `isDraw` illustrates the flavour of the whole approach rather nicely. `FIELDFULL`
is a constant in which all 42 playable bits are set, so the test compares the entire board in
one operation instead of scanning 42 cells individually.

Placed next to each other, the two listings also reveal two design decisions that will come up
again later. The first concerns how a move is undone. The 2012 engine mutates a single board
and reverses the move on the way back up the tree, which is the standard approach and also the
reason why `putPiece` and `removePiece` have to keep the `colHeight[]` array in step. BitBully
has no undo operation at all: the position is small enough that copying it is cheap, and the
search therefore takes its boards by value. Apart from the runtime argument, this removes the
particular class of bugs in which a faulty undo leaves an ancestor board subtly corrupted
fifteen plies deep in the tree. A faulty transition
can still produce a wrong descendant copy, of course, which is one reason for the checks in
part 8.

The second decision concerns the test for a full board. CFour asks the bit boards themselves,
whereas BitBully asks a counter that it maintains anyway. Both are constant-time operations,
and the interesting observation is simply that the same question has a natural answer in
either representation, which is not something one can say about a $$7 \times 6$$ array.

<br>

## Two Ways to fit 42 Cells into 64 Bits

At this point the two engines part ways. A Connect-4 board has 42 cells and a machine word
offers 64 bits, so there is some room to spare. How this spare room is spent turns out to
matter a great deal.

<div class="row mt-3 align-items-end">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/2026-01-29-connect-4-board-representations/bit-layout-cfour.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/2026-01-29-connect-4-board-representations/bit-layout-bitbully.png" class="img-fluid rounded z-depth-1" zoomable=true %}
    </div>
</div>
<div class="caption">
    The same 42 playable cells in the two layouts, drawn at the same scale. <b>Left:</b> CFour packs the columns into six bits each and uses exactly 42 bits, keeping track of how full each column is in a separate <code>colHeight[]</code> array. <b>Right:</b> BitBully gives every column nine bits, so that three unplayable <i>guard</i> bits sit on top of every stack. The seemingly wasted bits are what make the arithmetic of the following sections possible.
</div>

CFour packs the cells tightly, using `bit = 41 - 6 * col - row` in the coordinates of its
`fieldMask[col][row]` table, so that 42 bits are occupied and 22 remain unused. The direction
in which the bits are numbered is arbitrary; the important property is that every column
occupies six adjacent bits. Since this layout carries no information about how full a column
currently is, the class maintains a parallel `colHeight[]` array which has to be updated on
every move and on every undo.

BitBully deliberately wastes bits and uses `bit = col * 9 + row` instead, reserving rows 6, 7
and 8 of every column as guard bits which are never set during play. At first glance this
looks like a step backwards, since 63 bits are now needed for 42 cells, but the guard bits
turn out to buy a number of things which the dense layout cannot offer.

To be precise about what a position actually costs: the complete state of a BitBully board
consists of the two bit boards plus a small counter of the remaining plies, which `rawState()`
exposes as a triple.

```cpp
struct RawState {
  TBitBoard all_tokens;      ///< Bitboard of all occupied cells.
  TBitBoard active_tokens;   ///< Bitboard of cells held by the side to move.
  TMovesCounter moves_left;  ///< Plies left until the board is full.
};
```

The counter could of course be derived, since it is simply 42 minus the number of set bits in
`all_tokens`, but it is queried so constantly by the search that it is maintained
incrementally instead, with a single decrement per move. As we will see in part 7, the entire
score convention of the solver is derived from it.

<br>

## Generating all legal Moves with a single Addition

Every column has exactly one playable cell, namely the lowest empty one, and finding all seven
of them is probably the most common query in the whole engine. CFour answers it by reading the
`colHeight[]` array, whereas BitBully answers it with a single addition:

```cpp
Board::TBitBoard Board::legalMovesMask() const {
  return (m_bAllTokens + BB_BOTTOM_ROW) & BB_ALL_LEGAL_TOKENS;
}
```

The reason why this works is worth spelling out. `BB_BOTTOM_ROW` has exactly one bit set in
the bottom row of each column. Adding it to the occupancy mask makes the stack of one-bits in
each column carry upwards, and the carry then lands precisely on the lowest empty cell, which
is exactly the legal move we are looking for. The subsequent bitwise AND discards anything
that has spilled over into a guard bit, which is what happens when a column is already full.

Here the guard bits show their first benefit, since they prevent the carry of one column from
leaking into the next one. In a dense 6-bit layout, a full column would carry straight into
its neighbour and corrupt it. Three wasted bits per column therefore buy a branchless
move generator which handles all seven columns at once, and they also make the `colHeight[]`
array unnecessary.

This is a fairly general principle and not a Connect-4 curiosity. If some spare bits are spent
on encoding a boundary, many edge cases stop being special cases. I used the same idea when
[solving peg solitaire]({% post_url 2024-04-26-solving-peg-solitaire %}), where the 41 holes of
the Diamond-41 board leave enough room in a 64-bit variable to encode the boundary of the
board as well, so that checking whether a jump leaves the board becomes an ordinary mask test
instead of several comparisons.

Incidentally, the column heights have not disappeared, they are only derived instead of being
stored. Asking for one requires a mask and a bit count:

```cpp
int Board::getColumnHeight(const int column) const {
  return static_cast<int>(uint64_t_popcnt(m_bAllTokens & getColumnMask(column)));
}
```

This is a recurring theme of the whole post: with a suitable encoding, information that would
otherwise have to be maintained can simply be computed, and maintained state is precisely the
kind that eventually goes stale and disagrees with itself.

{% tabs legal %}

{% tab legal Python %}

```python
import bitbully as bb

board = bb.Board("3341")
print(board.native.legalMovesMask())  # bitboard of the seven playable cells
print(board.legal_moves())            # ... as column indices
print(board.get_column_heights())     # what CFour would have to store explicitly
```

{% endtab %}

{% endtabs %}

<br>

## Encoding the Player to Move away

The second design decision is somewhat subtler. CFour stores `fieldP1` and `fieldP2`, that
is, one bit board per player, while BitBully stores `m_bAllTokens` and `m_bActivePTokens`,
which are all occupied cells and those cells belonging to the player who is to move next.

Both representations carry the same information, since the tokens of the opponent are simply
`m_bActivePTokens ^ m_bAllTokens`, but the second one makes switching the player essentially
free. This is what the first line of `playMoveFastBB` above was doing:

```cpp
m_bActivePTokens ^= m_bAllTokens;  // switch player
```

Combining the mask of the active player with the full occupancy by a bitwise XOR leaves
exactly the tokens of the opponent behind, so the side to move is flipped with a single
instruction. A complete move therefore requires only three operations, without any branching
and without a `player` argument anywhere.

The Java version, in contrast, has to branch on `player` for every placement, every removal
and every win check. Recursive search code written against the BitBully layout also turns out
to be noticeably shorter, since the negamax formulation of the previous post, in which
everything is expressed from the point of view of the player to move, is already the way the
board is stored. Representation and algorithm agree with each other here, which is a pleasant
situation to be in.

<br>

## A whole Position in a single Integer

The transposition tables of part 5 require a key, that is, a number which identifies a
position. The obvious candidate is the pair of bit boards, but this amounts to 128 bits and is
rather awkward to store by the million. BitBully compresses this down to a single value:

```cpp
[[nodiscard]] uint64_t uid() const { return m_bActivePTokens + m_bAllTokens; }
```

A single addition of the two bit boards is sufficient, and the result identifies the position
uniquely. This is the position code used in John Tromp's
[Fhourstones](https://github.com/qu1j0t3/fhourstones) benchmark; his own
[Connect-4 solver](https://tromp.github.io/c4/Connect4.java) is worth a look as well, and we
will meet his opening database again in part 6. The reason the code is injective is easiest to
see one column at a time. A column of height $$h$$ contributes $$2^h - 1$$ to
`m_bAllTokens`, while the active player's subset lies between $$0$$ and $$2^h - 1$$. Their
sum therefore lies in $$[2^h - 1, 2^{h+1} - 2]$$, and these intervals are disjoint for
different heights. Once the height is known, subtracting the occupancy mask recovers the
active player's stones. The nine-bit stride keeps carries from neighbouring columns separate,
so the seven column codes together describe the position and the side to move unambiguously.

```python
>>> import bitbully as bb
>>> b = bb.Board("3341")
>>> all_tokens, active_tokens, moves_left = b.native.rawState()
>>> hex(all_tokens + active_tokens) == hex(b.uid())
True
```

This single integer is the reason why BitBully requires no Zobrist hashing at all, which is a
point the 2012 engine would have found rather surprising, and one which we will come back to
in part 5.

<br>

## Detecting Four in a Row by Shifting

We now come to one of the central operations, which the two engines approach in rather
different ways.

BitBully relies on shifting. If a token has a partner $$2k$$ bits away, and that pair in turn
has a matching pair $$k$$ bits further along, then four tokens are connected. Since the layout
places a fixed bit distance between neighbouring cells in every direction — one vertically,
nine horizontally, and eight and ten for the two diagonals — two shifts and two AND operations
per direction cover the whole board:

```cpp
bool Board::hasWin() const {
  const auto y = m_bActivePTokens ^ m_bAllTokens;   // the player who just moved
  auto x = y & (y << 2);
  if (x & (x << 1)) return true;                    // vertical
  x = y & (y << 2 * COLUMN_BIT_OFFSET);
  if (x & (x << COLUMN_BIT_OFFSET)) return true;    // horizontal
  // ... the same pair of tests for the two diagonals ...
  return false;
}
```

The guard bits prove their worth a third time here, since without them a diagonal shift would
wrap around the edge of the board and produce wins which do not actually exist.

CFour takes a different route. Although `ConnectFour.java` declares a `fourRows[]` table with
the 69 possible chains, that array is not used by the pinned win-checking path. The function
which asks whether a token of `player` would win at a particular cell is instead a generated
42-case `switch`, with the relevant masks inlined as literals. Central cells participate in
more possible chains than edge cells, so their cases contain more tests:

```java
public boolean canWin(int player, int xx, int yy) {
    long x = (player == PLAYER1 ? ~fieldP1 : ~fieldP2);
    int y = (int) x;
    switch (xx * 6 + yy) {
    // ... cases 0 to 17 ...
    case 18:
        if (!((x & 0x20820000000L) != 0 && (x & 0x820020000L) != 0
                && (y & 0x20020800) != 0 && (y & 0x20820) != 0
                && (y & 0x10204) != 0 && (x & 0x4210000000L) != 0))
            return true;
        break;
    // ... cases 19 to 41 ...
    }
    return false;
}
```

Two things are worth noting here. The masks are applied to the inverted bit board, so that
`(x & mask) != 0` means that the corresponding chain still has a gap in it; if every chain
through the cell has a gap, there can be no win, and De Morgan's laws turn the whole test into
a single short-circuiting conjunction. Furthermore, `y = (int) x` truncates the board to 32
bits, so that chains living in the lower half of the board can be tested with cheaper 32-bit
literals. The separate, somewhat misleadingly named `hasWin(player)` asks whether the player
can win on the next move; it switches on the seven column heights and inlines the corresponding
tests for each currently playable cell. Both routines were produced by a generator, which we
will look at properly in part 4.

#### Composing the Operations

The function `winningPositions` does not test whether somebody has already won; `hasWin()` is
the separate test for that. Instead, when `winningPositions` is called on the tokens of the
player to move, it returns every cell which would complete a chain of four, including cells
which nobody can reach yet. If we intersect this result with the mask of legal moves from
above, we obtain the question which the search actually asks in every node:

```cpp
bool Board::canWin() const {
  return winningPositions(m_bActivePTokens, true) & (m_bAllTokens + BB_BOTTOM_ROW);
}
```

In other words, the question whether the current player can win immediately is answered by a
bitwise AND of the threat mask and the reachable cells, with the addition trick from the
previous section appearing inline. Restricting the result further with `& getColumnMask(column)`
answers the same question for one particular column.

In my opinion this composability is the actual dividend of the representation. Each of the
operations described above produces a bit board again, so they can be combined with a bitwise
AND instead of with control flow. Part 4 builds its entire threat detection and move ordering
out of exactly such intersections.

#### A Note on Measurements

It would be tempting at this point to quote a speed-up factor, but one should be careful about
what can honestly be claimed. Timing a throwaway array implementation against a throwaway bit
board implementation would measure the two throwaways rather than this engine, and a ratio
obtained in one programming language says little about another. Instead of a
benchmark, it therefore seems more useful to count what the machine is actually asked to do.

A naive array scan visits up to 42 cells and, for each of them, examines several directions.
An optimized array implementation would instead start at the token just played and inspect
only the lines through that cell, so the exact comparison depends on the implementation. The
bit-board variant nevertheless has a small bounded worst-case cost: two shifts and two AND
operations per direction, so at most eight of each, without bounds checks or per-cell loops.
The scalar C++ routine can return early after any successful direction, so its actual work is
data-dependent even though each direction examines the whole board in parallel.

The effect of the representation does show up in the numbers which are directly measurable,
namely in the whole-engine benchmarks of part 8, where BitBully solves the empty board in
under 200 seconds. Bit boards do not appear as a separate line item there, since they are the
foundation on which everything else rests.

<br>

## Trying the Operations out

Since everything described so far consists of nothing but bitwise operations on two integers,
it is straightforward to reimplement it in the browser, and it seems more instructive to let
the reader watch the two words change than to describe them further. The following widget is a
faithful transcription of the C++ shown above: clicking a column calls the same three
operations as `playMoveFastBB`, the highlighted cells are the result of
`(all + BB_BOTTOM_ROW) & BB_ALL_LEGAL_TOKENS`, and the amber cells are the winning cells
returned by `winningPositions()` for the player to move.

<link rel="stylesheet" href="{{ '/assets/css/connect4-widgets.css' | relative_url }}" />

<div class="c4bb" data-c4-bitboard></div>

<script src="{{ '/assets/js/connect4-core.js' | relative_url }}"></script>
<script src="{{ '/assets/js/connect4-bitboard.js' | relative_url }}"></script>

Two details are worth watching. The legal-move mask always contains exactly one cell per
non-full column, which is the carry landing on the lowest empty cell, and the guard bits above
each column stay grey because the final mask discards any carry into them. It is also worth
noting that the JavaScript has to use `BigInt` rather than ordinary numbers, because the layout
places bits at indices up to 62 while a JavaScript number is a double-precision float and
silently loses integer precision above $$2^{53}$$. The same 64-bit arithmetic which a CPU
performs in a single instruction requires an arbitrary-precision integer type here.

<br>

## Mirroring along the Middle Column

A Connect-4 position and its mirror image along the middle column have the same
game-theoretic value. Exploiting this symmetry roughly halves the effective size of both the
transposition tables of part 5 and the opening books of part 6, and it also allows the search
to skip redundant moves in symmetric positions, as described in part 4.

With bit boards, mirroring is a fixed sequence of column swaps which requires neither loops
nor any per-cell work. In BitBully the function is additionally declared `constexpr`, so that
mirrored constants cost nothing at runtime:

{% tabs mirror %}

{% tab mirror C++ (BitBully) %}

```cpp
auto static constexpr mirrorBitBoard(const TBitBoard x) {
  TBitBoard y{UINT64_C(0)};
  y |= ((x & getColumnMask(6)) >> 6 * COLUMN_BIT_OFFSET);   // 6 <-> 0
  y |= ((x & getColumnMask(0)) << 6 * COLUMN_BIT_OFFSET);
  y |= ((x & getColumnMask(5)) >> 4 * COLUMN_BIT_OFFSET);   // 5 <-> 1
  y |= ((x & getColumnMask(1)) << 4 * COLUMN_BIT_OFFSET);
  y |= ((x & getColumnMask(4)) >> 2 * COLUMN_BIT_OFFSET);   // 4 <-> 2
  y |= ((x & getColumnMask(2)) << 2 * COLUMN_BIT_OFFSET);
  return y | (x & getColumnMask(3));                        // 3 stays put
}
```

{% endtab %}

{% tab mirror Java (CFour) %}

```java
protected long getMirroredField(int player) {
    long temp = (player == PLAYER1 ? fieldP1 : fieldP2);
    long mirroredField = 0L;
    mirroredField |= ((temp & columnMask[0]) >> 36);
    mirroredField |= ((temp & columnMask[1]) >> 24);
    mirroredField |= ((temp & columnMask[2]) >> 12);
    mirroredField |= (temp & columnMask[3]);
    mirroredField |= ((temp & columnMask[4]) << 12);
    mirroredField |= ((temp & columnMask[5]) << 24);
    mirroredField |= ((temp & columnMask[6]) << 36);
    return mirroredField;
}
```

{% endtab %}

{% tab mirror Python %}

```python
import bitbully as bb

b = bb.Board("3341")
print(b)
print(b.mirror())
```

{% endtab %}

{% endtabs %}

Both implementations follow the same idea and differ only in the stride, which is 12 bits per
column pair in the dense Java layout and 18 bits in the 9-bit layout of BitBully. Note also
that the Java version has to be called twice, once for each of the two player bit boards.

<br>

## Odd and Even Rows

Finally, one more pair of constants should be mentioned, which will appear rather unmotivated
here but turns out to be indispensable in the next post:

```java
protected static final long EVENROWS = 0x15555555555L;
protected static final long ODDROWS  = 0xA28A28A28AL;
```

The two masks are not complements of one another, which is worth knowing before decoding them
by hand. `EVENROWS` holds all 21 cells of the second, fourth and sixth row, whereas `ODDROWS`
holds only the 14 cells of the third and fifth row and leaves the bottom row out, so that
seven of the 42 cells belong to neither. BitBully describes the same set of cells as
`getRowMask(2) | getRowMask(4)` in its own layout, so the two engines agree on this point
despite counting their bits in opposite directions.

A considerable part of Connect-4 strategy depends on parity. Since the players alternate and
the tokens stack up from the bottom, a threat in an odd row and a threat in an even row are
worth quite different things, and which of the two is useful depends on whether one is the
first or the second player. Victor Allis has elaborated on this in detail in his master's
thesis {% cite Allis88 --file thesis %}.

For the moment the only relevant observation is that with a bit board the question whether a
player has a threat in an odd row is answered by a single AND against a constant. Domain
knowledge which would require rather fiddly branching logic in an array representation
collapses into one instruction here, and part 4 makes extensive use of this.

<br>

## A small Toolkit of Bit-Twiddling Operations

Four idioms appear again and again in both engines, and all of them are extremely cheap. On
supported compiler and CPU targets, the first two typically lower to dedicated instructions;
BitBully supplies portable loop fallbacks for other targets. The other two require only a
subtraction and a bitwise operation:

| Idiom | What it does |
| --- | --- |
| `popcount(x)` | count set bits — how many stones, how many threats |
| `ctz(x)` | index of the lowest set bit; divided by nine it gives the column |
| `x & -x`, or `~(x-1) & x` | isolate the lowest set bit — pick the next move |
| `x &= x - 1` | clear the lowest set bit — advance to the next one |

The last two are usually combined into the standard way of iterating over a set of moves,
which requires neither a loop counter nor a bounds check nor an array:

```cpp
while (moves) {
  const auto mv = lsb(moves);   // isolate one move
  // ... search it ...
  moves ^= mv;                  // and clear it
}
```

BitBully wraps `popcount` and `ctz` in `uint64_t_popcnt` and `ctz_u64`, picking the compiler
intrinsic that exists (`__builtin_popcountll` on GCC/Clang, `__popcnt64` on MSVC) and falling
back to a portable loop otherwise. Its popcount fallback is a straightforward shift-and-count
loop. For two alternative derivations,
[A few Bit-Twiddling Tricks]({% post_url 2024-12-11-soa-few-bit-twiddling-tricks %}) develops a
`bitCount` which iterates once per set bit and a `bitPos` which locates a single set bit in six
binary-search steps. The same post covers the power-of-two modulo trick that part 5 uses to
index the transposition table.

<br>

## The same Operations on a whole Batch of Boards

There is one further property of this representation which I only came to appreciate much
later, when I needed to simulate a very large number of Connect-4 games at once for a
completely different set of experiments.

The core masks, shifts and additions described above operate on whole words and contain no
loops over individual cells. The scalar `hasWin()` still uses data-dependent early returns, but
its batched counterpart can accumulate a Boolean tensor instead. If the two bit boards are
stored as vectors of $$B$$ integers, the same elementwise expressions describe $$B$$
independent positions without a Python branch for each board.

The following is taken from a batched implementation of the board which I wrote on top of
PyTorch tensors ([`torch_board.py`](https://github.com/MarkusThill/techdays26/blob/0da53a8670703b2c5a3ab118c93497391f945510/src/techdays26/torch_board.py)),
where `all_tokens` and `active_tokens` are `int64` tensors of shape `[B]` rather than plain
integers:

```python
def legal_moves_mask(self) -> torch.Tensor:
    """[B] int64 landing squares (reachable in next move)."""
    dev = self.all_tokens.device
    bottom = torch.full((), self.BB_BOTTOM_ROW, device=dev, dtype=torch.int64)
    all_legal = self._all_legal_mask(dev)
    return (self.all_tokens + bottom) & all_legal


def has_win(self) -> torch.Tensor:
    y = self.active_tokens ^ self.all_tokens  # player who just moved

    x = y & (y << 2)
    win = (x & (x << 1)) != 0

    off = self.COLUMN_BIT_OFFSET

    x = y & (y << (2 * off))
    win |= (x & (x << off)) != 0
    # ... the two diagonals, off - 1 and off + 1
    return win
```

Apart from the tensor bookkeeping, these are character for character the expressions from
earlier in this post. The constants are the same as well, since the layout is the same one
with nine bits per column, and `BB_BOTTOM_ROW` is again the mask with one bit set in the
bottom row of every column. On an empty board the legal-move mask comes out as
`0x40201008040201`, which is exactly the seven bits $$0, 9, 18, \ldots, 54$$.

The idioms for iterating over a set of moves survive the transition unchanged as well:

```python
for _ in range(max_moves):
    mv = m & -m          # extract the lowest set bit (one-hot)
    yield mv
    m = m ^ mv           # and clear it
```

These are the same two operations from the toolkit above, except that `m` now holds one move
set per board and every board advances to its next candidate move at the same time. Recovering
the column from a one-hot mask is also pleasantly direct, since the fixed stride of nine bits
means that an integer division is sufficient:

```python
bit_index = mv.bit_length() - 1
return bit_index // column_bit_offset
```

The point I would like to make here is not really about PyTorch. It is that the decisions taken
at the very beginning (one bit per cell, a fixed stride between neighbouring cells, and guard
bits instead of per-cell bounds checks) also suit batched tensor operations more than a decade
later. The current PyTorch implementation still has ordinary control flow around these
operations, but the board calculations themselves avoid per-board Python loops and early exits.
A $$7 \times 6$$ array representation could also be batched, although it would require a more
substantial rewrite instead of reusing the same shifts and masks.

<br>

## Compile-Time Derivation of the Constants

A further difference between the two engines has nothing to do with algorithms, but rather
with how survivable the source code remains over the years.

Every one of the techniques described above needs constants: row masks, column masks, the
guard mask, the priority cells. In 2012 these were simply written out by hand:

```java
public static final long fieldMask[][] = {
        { 2199023255552L, 1099511627776L, 549755813888L, 274877906944L,
                137438953472L, 68719476736L }, //
        { 34359738368L, 17179869184L, 8589934592L, 4294967296L,
                2147483648L, 1073741824L }, //
        // ... 42 entries in total
protected static final long ODDROWS   = 0xA28A28A28AL;
protected static final long FIELDFULL = 0x3FFFFFFFFFFL;
```

These are 42 decimal literals which no reader can verify by eye, together with a handful of
hexadecimal constants whose correctness one simply has to take on faith. A good part of the
complaints about tedious debugging in my earlier write-ups originates here, since a single
wrong digit in one of these constants shows up as a wrong game-theoretic value fifteen plies
deep in the tree.

BitBully derives several of the bulk masks at compile time from a description of what they are
supposed to mean:

```cpp
static constexpr bool isIllegalBit(const int bitIdx) {
  constexpr int COLUMN_BIT_OFFSET = 9;
  constexpr int N_ROWS = 6;
  constexpr int COLUMNS = 7;
  // past the last column, or in the top three bits of some column
  return bitIdx >= COLUMN_BIT_OFFSET * COLUMNS ||
         (bitIdx % COLUMN_BIT_OFFSET) / N_ROWS;
}

static constexpr uint64_t illegalBitMask() {
  uint64_t bb{UINT64_C(0)};
  for (size_t i = 0; i < CHAR_BIT * sizeof(uint64_t); ++i)
    bb ^= (isIllegalBit(i) ? UINT64_C(1) << i : UINT64_C(0));
  return bb;
}

static constexpr TBitBoard BB_ALL_LEGAL_TOKENS = ~BB_ILLEGAL;
```

Because these functions are `constexpr`, the compiler can fold their results into the literals
used by the runtime code. What changes is that the derivation is readable and reviewable.
This is not a fully parameterized board, however: `isIllegalBit` repeats the stride, row and
column counts locally, and some bottom, top and priority masks still name explicit bit indices.
Changing `Board::N_ROWS` alone would therefore not update the complete layout. The improvement
is narrower but still useful: many opaque bulk literals are replaced with compile-time
derivations, while the remaining semantic index lists are at least visible as such.

<br>

## Advantages and Disadvantages of Bit Boards

Altogether, a number of advantages of bit boards over arrays can be identified for the game of
Connect-4, although not all of them are necessarily transferable to other games:

- Many operations can be carried out more efficiently, since they cover several fields of the
  board at the same time. Examples are the recognition of winning positions and draws, the
  mirroring of positions along the middle column, and the determination of threats.
- Copying the board is cheap, since it consists of two 64-bit bit boards and a small
  moves-left counter.
- The memory requirements are reduced, which is particularly relevant in connection with the
  transposition tables of part 5 and the opening databases of part 6.

However, the use of bit boards also has some disadvantages which should not be neglected:

- High programming effort in the older implementation. Some of CFour's specialized,
  fully-unrolled tests were generated by other programs, since writing them by hand was not
  realistic; the more compact shifting approach shows that this is not an unavoidable property
  of bit boards themselves.
- Poor readability of the source code. An expression such as
  `(m_bAllTokens + BB_BOTTOM_ROW) & BB_ALL_LEGAL_TOKENS` is a rather elegant trick, but it is
  not something one wants to encounter without an accompanying comment.
- Maintenance of the program is difficult and troubleshooting is fault-prone and tedious. If a
  mask is wrong by a single bit, the symptom is a wrong game-theoretic value deep inside the
  tree.
- The surrounding optimized solver can become very long. All in all, nearly 7000 lines of
  source code were needed to realize the Java agent, although much of this length comes from
  its generated search and threat code rather than from the representation alone.

This is a real trade-off, and in my opinion it is only worth making when the operations being
optimized are executed billions of times, which is certainly the case for a perfect-playing
Connect-4 agent, but probably not for most other projects.

The most lasting cost, however, is verification. Once one has a solver of several thousand
lines which is full of machine-generated masks, it becomes surprisingly difficult to convince
oneself that it is actually correct. This question deserves a post of its own, and the answer
turns out to involve a database which somebody else computed (part 8).

<br>

## Summary

A Connect-4 position is now held in two 64-bit integers. From these we obtain the legal moves
with a single addition, a complete move in three operations, a unique position key essentially
for the cost of a few integer operations, the detection of a win with four shift pairs, the
mirrored position with six shifts, and the column heights on demand. The representation
therefore keeps the per-node bookkeeping small enough that the number of searched nodes becomes
the dominant concern.

What runs through all of this is that almost nothing is actually stored. The column heights,
the player to move, the position key and the set of winning cells are all computed from the
same two variables by combining masks, and the individual operations compose with a bitwise
AND in many of the hot paths rather than with per-cell loops. This is what makes the techniques
of the following posts possible in the first place.

The bottleneck is now the sheer number of nodes which have to be visited, and this is a search
problem rather than a representation problem. The next post therefore deals with what is
probably the most effective way of reducing it, namely presenting the most promising moves to
the alpha-beta search first.

<br>

## Source Code

Pinned to the commits this post was written against:

- **BitBully** — [`Board.h`](https://github.com/MarkusThill/BitBully/blob/50c45ff72113655b79878cf1022771298c449d84/src/Board.h)
  and [`Board.cpp`](https://github.com/MarkusThill/BitBully/blob/50c45ff72113655b79878cf1022771298c449d84/src/Board.cpp)
  · [GitHub](https://github.com/MarkusThill/BitBully) · [PyPI](https://pypi.org/project/bitbully/)
  · [Docs](https://markusthill.github.io/BitBully/)
  · [`Board` API documentation](https://markusthill.github.io/BitBully/board/)
  · [getting started](https://markusthill.github.io/BitBully/getting_started/)
  · [project page]({{ 'projects/0_bitbully/' | absolute_url }})
- **CFour** — [`ConnectFour.java`](https://github.com/MarkusThill/Connect-Four/blob/2a58844594ac022846385dd3ddc8bbbf0a26eae5/CFour/src/c4/ConnectFour.java)
  · [GitHub](https://github.com/MarkusThill/Connect-Four)
- **Batched bit boards** — [`torch_board.py`](https://github.com/MarkusThill/techdays26/blob/main/src/techdays26/torch_board.py)
  in the [techdays26](https://github.com/MarkusThill/techdays26) repository

If you would like to try the operations described here on real positions, the easiest way is
the interactive notebook widget, which runs in the browser without any local installation:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MarkusThill/BitBully/blob/master/notebooks/game_widget.ipynb)

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
