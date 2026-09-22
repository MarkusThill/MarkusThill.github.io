---
layout: post
title: "Building Intelligent Agents for Connect-4&#58; Opening Databases"
modified: 2026-07-07T09:00:51+01:00
categories: [Programming]
description: "How the 8- and 12-ply opening books encode millions of solved positions in compact fixed-width records, and how the original database pipeline is used by BitBully today."
tags: [Connect-4, AI, tree-search, alpha-beta, minimax, transposition tables, opening databases, move ordering, bitboards, huffman coding]
thumbnail: assets/img/2026-03-12-connect-4-opening-databases/huffman.png
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-03-12T09:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
series: connect4-search
series_part: 6
---

{% include series_connect4.liquid %}

As with many other games, the course and outcome of a game of Connect-4 already depends
on the opening phase. The first player, for example, has to place the first token in the middle
column in order to win the game, since in all other cases only a draw is reached or the game is
even lost. For this reason a strong player must be able to control the opening in order to
avoid mistakes and punish an opponent's mistakes immediately. Often,
however, it is very difficult to analyze the positions of the opening phase, because a high
search depth is necessary to determine the exact game-theoretic values. The previous post ended
on exactly this observation: with ten tokens on the board, a complete solve still costs
roughly three million nodes and about a third of a second.

<!--more-->

In order to master the opening phase, many programs therefore use opening books, which are
usually created with a high computational effort. These can typically give the program an
advantage and save a lot of computing time during the opening. For games like Connect-4 there
is another advantage: during the course of the game the state space decreases further and
further, so that after leaving the opening book individual positions can often be correctly
evaluated without further assistance and in acceptable time.

<br>

## The 8-ply and the 12-ply Database

Tromp computed his extensive eight-ply database in 1993
{% cite Tromp93 --file thesis %}{% cite Allis94 --file thesis %}; a subset was donated to the
UCI repository in 1995 {% cite Tromp95 --file thesis %}. His original Connect-4 page at
[tromp.github.io/c4/c4.html](https://tromp.github.io/c4/c4.html) is still online and well worth
reading for the historical context. The calculation was carried out on Sun and SGI workstations
at [CWI](https://www.cwi.nl/) and lasted about 40,000 hours of CPU time, which corresponds to
roughly four and a half years of single-machine time. Tromp used the full result to strongly
solve the game and made a subset of 67,557 unfinished and unforced positions with eight tokens
publicly available. In this subset, positions which are identical after mirroring along the
middle column are only present in one variant. Of these positions, 44,473 (65.8%) lead to a win
of the first player, 16,635 (24.6%) to a defeat and 6,449 (9.5%) to a draw.

The public subset has one gap for direct book lookup, however, and this gap is rather
instructive. It omits positions with at least one immediate threat for either player. Positions
with an immediate threat for the player who is moving next do not have to be included, since
that player will win the game in the next ply anyway. However, positions with an immediate
threat for the player who has just moved can be neutralized in the next ply and the game is then
continued, so these are ordinary positions which merely look dramatic. A total of 19,336 such
positions were absent from the public subset. I analyzed them with an early version of my
alpha-beta agent on a Pentium-4 computer in about two weeks, extending the 8-ply book's direct
lookup coverage to 86,893 positions.

The 8-ply database has a further and somewhat subtler drawback which is not immediately
obvious: all of its positions contain scores for a win, loss or draw, but no statement can be
made as to how far victories or defeats are away from the current position. The first player can
force a win from the empty board, but an individual book position may still be a win, loss or
draw. Once several moves have the same outcome, what a strong program also needs to know is how
quickly that outcome occurs. These distances are particularly important for the second player
in order to prevent early defeats, and without them an alpha-beta agent often has to search
beyond the limits of the opening book in order to avoid bad moves for the trailing player.

For this reason, and in order to achieve further runtime advantages, I decided to compute a
second opening database, this time with 4,200,899 stored positions with twelve tokens. This is
the set of entries covered by the distance-annotated book, not the set of all legal twelve-token
positions. Here too, identical positions after mirroring at the middle column were only stored
in one variant, which leads to significant savings in memory and computing time. The individual
positions were then analyzed and the theoretical result including the distance to the end of
the game was determined. The computation was again carried out on a Pentium-4 computer and took
about three weeks. Furthermore, a 10-ply database was created along the way, which is not really
used in the project.

<br>

## Compressing the Databases with suitable Representations

Since the individual databases contain many positions, a suitable coding of the individual
positions has to be found which minimizes the required memory. The coding of a game state in
$$2 \times 42$$ bits, as described in part 3, does not seem to make sense here, since the
12-ply database with its 4,200,899 positions alone would require about 50 MB of memory, which
in 2012 was not a file one would casually ship.

A better encoding can be found by taking advantage of the fact that all positions in a database
contain the same and comparatively small number of tokens. The following observation is
important here: above an empty field there can only be further empty fields. For a unique
description of a position it is therefore sufficient to list the tokens of both players for
each column in a defined order, without the empty fields being relevant at all. Only the
columns have to be separated from each other.

In addition to the two possible tokens, only a separator character is thus needed to achieve a
unique encoding, and this leaves an alphabet of three symbols. The actual encoder below emits a
separator after each of the seven columns. At twelve plies there are six stones of each colour
but seven separators, so the separator is the most frequent of the three symbols. According to
Huffman's rule, the most frequent symbol receives the shortest code word, and the separator is
therefore assigned the code word of length one.

{% include figure.liquid
   path="assets/img/2026-03-12-connect-4-opening-databases/huffman.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="35%"
   caption="The three-symbol code: one bit for the column separator (TR), two bits each for the two stone colours (S1, S2). A prefix code, so no delimiters are needed between symbols."
%}

To encode a position, one proceeds as follows. The columns are evaluated from left to right and
the cells within the columns from bottom to top, and depending on the configuration of the
respective field the corresponding code word is appended to the current sequence. If an empty
field is reached, the code word for the separator is appended and the next column is processed.
Strictly speaking the separator of the last column carries no information, since the sequence
simply ends there. If it is omitted, a twelve-token position has six separators, tied with the
six stones of each colour, and needs
$$12 \times 2 + 6 \times 1 = 30$$ bits, which leaves two spare bits in a four-byte word,
exactly enough for the win/loss/draw value, and a position with eight tokens needs
$$8 \times 2 + 6 = 22$$ bits plus two for the value, so that it fits into exactly three bytes.

The implementation shown below is slightly more relaxed about this and simply emits one
separator after every column, followed by a final padding bit. This occupies precisely the two
trailing bits that the accounting above assigns to the value, so the result is the same width
in both readings: 24 bits for an eight-token position and 32 bits for a twelve-token one. The
convenience is that the encoder does not need a special case for the last column and the key
always ends on a byte boundary.

{% include figure.liquid
   path="assets/img/2026-03-12-connect-4-opening-databases/encodingExample.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="50%"
   caption="An eight-stone position encoded in 24 bits (3 bytes): `0 10 11 10 0 0 11 10 11 10 11 0 0 0 11`. The final two bits are the value — here, a win for the first player."
%}

Two details make this work. The player who moves does not need to be encoded, as he can be
determined from the position itself. In the two outcome-only books, the result occupies the two
low padding bits of the 24- or 32-bit position word, so an on-disk record is one packed integer
which sorts by position and carries its answer along with it. The distance-aware 12-ply book
retains the padded 32-bit key and stores its signed value in a separate fifth byte.

Both engines implement the same encoding, and it may be instructive to look at it in three
languages:

{% tabs huffman %}

{% tab huffman C++ (BitBully) %}

```cpp
[[nodiscard]] int toHuffman() const {
  // Only defined for an even number of tokens, and at most 12 stones.
  if (m_movesLeft < 30 || m_movesLeft & 1) return 0;
  int huff = INT64_C(0);

  for (int i = 0; i < N_COLUMNS; ++i) {
    auto all    = m_bAllTokens    >> (i * COLUMN_BIT_OFFSET);
    auto active = m_bActivePTokens >> (i * COLUMN_BIT_OFFSET);
    for (int j = 0; j < N_ROWS && (all & 1); j++) {
      huff <<= 2;                     // two bits per stone
      huff |= (active & 1) ? 2 : 3;   // 10b for one colour, 11b for the other
      all >>= 1;
      active >>= 1;
    }
    huff <<= 1;                       // a single 0 bit ends the column
  }
  // 12 * 2 + 7 = 31 bits so far
  return huff << 1;                   // pad to a full byte
}
```

Note how the bit board layout pays off once more here. After shifting by
`i * COLUMN_BIT_OFFSET`, the expression `all & 1` walks a column from the bottom upwards
without any index arithmetic, and the loop terminates at the first empty cell, since gravity
guarantees that all remaining cells of the column are empty as well.

{% endtab %}

{% tab huffman Java (CFour) %}

```java
protected int fieldToHuffman(long f1, long f2, boolean mirrored) {
    int temp = 0;
    // 0 -> no further stones in this column (1 bit)
    // 2 -> stone of the player to move      (2 bits)
    // 3 -> stone of the opponent            (2 bits)
    int i   = (mirrored ? 6 : 0);
    int inc = mirrored ? -1 : 1;
    for (; (mirrored && i >= 0) || (!mirrored && i < 7); i += inc) {
        for (int j = 0; j < colHeight[i]; j++) {
            long mask = (mirrored ? getMask((6 - i), j) : getMask(i, j));
            if ((f1 & mask) != 0L)      { temp <<= 2; temp |= 3; }
            else if ((f2 & mask) != 0L) { temp <<= 2; temp |= 2; }
        }
        temp <<= 1;              // a single 0 bit ends the column
    }
    return temp << 1;            // pad to a full byte
}
```

Two differences worth noting. The inner loop runs to `colHeight[i]` — the 2012 encoder reads
the height array that BitBully does without, which is why its loop needs no "stop at the first
empty cell" test. The `mirrored` flag does not itself reflect the supplied bit boards: callers
first pass the results of `getMirroredField(...)`, and the flag then selects the reverse
column traversal and matching mask coordinates for those already mirrored fields.

{% endtab %}

{% tab huffman Python %}

```python
# The reference decoder in bitbully-databases, condensed:
bits = ["0b"]
for c in range(cols):                       # columns left to right
    for r in reversed(range(rows)):         # rows bottom to top
        v = board[r][c]
        if v == 0:
            bits.append("0")                # end-of-column separator
            break
        bits.append("10" if v == 1 else "11")
        if r == 0:
            bits.append("0")                # full column still gets a separator
bits.append("0")                            # pad
value = int("".join(bits), 2)
```

{% endtab %}

{% endtabs %}

#### Encoding the Value and the Distance

Five bytes are reserved for the 12-ply database with the respective distances to the end of the
game, whereby the fifth byte contains the value. The following representation is used for it:

$$
v_i = \begin{cases}
100 - d & \text{first player wins in } d \text{ moves} \\
0 & \text{draw} \\
d - 100 & \text{first player loses in } d \text{ moves}
\end{cases}
$$

The sign thus indicates the outcome and the magnitude indicates the speed, both in a single
signed byte. Since a faster win maps to a larger number, the ordinary logic of picking the
maximum automatically prefers quick wins and slow losses, without any special cases being
necessary.

#### Not storing the most common Answer

One further detail is only visible in the shipped files, and I find it rather satisfying. Under
perfect play the first player wins most positions, and the two books without distances exploit
this by not storing these wins at all. A lookup which misses is therefore not an error, but
simply the answer that the first player wins, so that only the minority outcomes actually cost
any bytes:

| Book | Entries stored | Bytes/entry | File size | vs. byte-aligned 2×42-bit |
| --- | ---: | ---: | ---: | ---: |
| 8-ply | 34,515 | 3 | 0.10 MB | 3.7× |
| 12-ply | 1,735,945 | 4 | 6.94 MB | 2.8× |
| 12-ply-dist | 4,200,899 | 5 | 21.00 MB | 2.4× |

The 12-ply book stores 1,735,945 entries, whereas the distance-annotated version of the same
set of positions stores 4,200,899 of them: the outcome-only book simply omits the roughly 59%
which are wins for the first player. Combining this with the Huffman coding and the mirror deduplication, the
distance-annotated twelve-ply book fits into 21 MB, or into about 7 MB if one can live without
the distances.

Sampling the books directly gives the following distribution of outcomes from the perspective
of the player to move:

| Book | Win | Loss | Draw |
| --- | ---: | ---: | ---: |
| 8-ply | 59.5% | 29.9% | 10.6% |
| 12-ply | 53.0% | 38.7% | 8.3% |
| 12-ply-dist | 55.6% | 37.2% | 7.2% |

<details markdown="1">
<summary>How this was measured</summary>

3000 random legal positions per book (8 or 12 stones, `forbid_direct_win=True`), looked up
through the pure-Python decoder in `bitbully-databases`. File sizes and entry counts come from
the packaged `.dat` files. The byte-aligned baseline uses 11 bytes for the two 42-bit boards;
their four spare bits also hold the outcome in the two books without distances. The distance
book needs a twelfth byte for its signed value. Reproduce with
`tools/connect4/book_stats.py`.

Beware the board orientation when reproducing this: `bitbully` hands you a column-major
`arr[col][row]` with row 0 at the bottom, while the decoder wants row-major `board[row][col]`
with row 0 at the **top**. Getting it wrong produces a clean, plausible, entirely wrong answer
(every lookup simply misses).

</details>

<br>

## Watching the Encoder run

The encoding is best understood by watching it emit one symbol at a time. The following widget
walks `toHuffman()` step by step: the columns are processed from left to right and the cells
within a column from bottom to top, every token contributes two bits, and a single `0` bit
terminates each column. The cell currently being encoded is outlined on the board.

<link rel="stylesheet" href="{{ '/assets/css/connect4-widgets.css' | relative_url }}" />

<div class="c4bb" data-c4-huffman></div>

<script src="{{ '/assets/js/connect4-core.js' | relative_url }}"></script>
<script src="{{ '/assets/js/connect4-huffman.js' | relative_url }}"></script>

The two buttons for random positions are the interesting ones, since they produce exactly the
kind of entry the databases contain. A position with eight tokens comes out at 22 bits plus two
for the value, which fits into three bytes, and one with twelve tokens comes out at 30 bits,
which leaves two spare bits in a four-byte word. In both cases a naive dump of the two bit
boards would have required eleven bytes.

<br>

## Looking up a Position

The transposition table of part 5 is a hash table because it is written to constantly during
the search. An opening book is the opposite case: it is written once and then only read, and
this changes which data structure is appropriate.

BitBully therefore loads the book into a sorted `std::vector` of key-value tuples and performs
a binary search on it. This requires no hashing, collision handling, load factor or rehashing.
The compact fixed-width records describe the on-disk format: the pinned loader reads and
decodes the complete file into tuples, so its in-memory representation can be wider and it is
not memory-mapped directly from disk.

The lookup itself first tries the position and then its mirror image, which is what allows the
book to store only one representative of each symmetric pair:

```cpp
auto p = b.toHuffman();
int val = binarySearch(p);
if (val != NONE_VALUE) {
  return convertValue(val, b);
}

p = b.mirror().toHuffman();
val = binarySearch(p);
if (!m_withDistances && val == NONE_VALUE) {
  val = 1;  // omitted from the outcome-only books: player 1 wins
} else if (val == NONE_VALUE) {
  // Immediate player-1 wins are omitted from the distance book.
  return (b.movesLeft() + 1) / 2;
}
assert(val != NONE_VALUE);
return convertValue(val, b);
```

The function `convertValue` translates the `100 - distance` encoding of the book into the
solver's own score convention based on the remaining moves, which is the subject of the next
post. The search itself consults the book at exactly one place, namely when the number of
tokens reaches the depth of the book:

```cpp
if (isBookLoaded() && b.countTokens() == m_openingBook->getNPly()) {
  return m_openingBook->getBoardValue(b);
}
```

This amounts to one book-horizon comparison per node. Once the horizon is reached, one
logarithmic lookup — and, after a miss, a second one for the mirror image — replaces the entire
remaining subtree.

<br>

## Computing four Million Positions

The databases did not appear out of nowhere, of course. The 2012 repository still contains the
whole pipeline in the form of a set of small, single-purpose C++ Builder projects under
`srcCPP/Databases/`:

1. **create positions** — enumerate candidate positions with exactly $$n$$ stones.
2. **remove duplicate Positions** — collapse mirror-image pairs, halving the work that follows.
3. **sort database** — put the entries in key order so lookups can binary-search.
4. **convert to binary database** — pack from a working format into fixed-width records.
5. **convert to huffman** — apply the encoding above.
6. **convert to Huffman - 12Ply with Distance** — the same, keeping the distance byte.

This is a batch pipeline of tiny programs, each of which does exactly one thing and which
communicate through files. Nothing about it is particularly sophisticated, and in my experience
that is rather the point, since a three-week computation is much easier to survive when it can
be restarted at step four.

The validation step is the one which I would recommend copying. To validate the results
obtained, an 8-ply database was created from the 12-ply database and compared with the existing
database of John Tromp on the positions covered by both. Two databases, computed by different
people with different programs about a decade apart and agreeing on their shared entries, are
about as strong a correctness argument as this kind of artefact admits, and we will come back to
this idea in part 8.

<br>

## Using the Databases today

Both databases are still in service today. They ship as the separate
[bitbully-databases](https://github.com/MarkusThill/bitbully-databases) package, which is also
documented [here](https://markusthill.github.io/bitbully-databases/) and described on its own
[project page]({{ 'projects/1_bitbully_databases/' | absolute_url }}). The pure-Python decoder
in it requires neither a compiler nor NumPy, which makes it the most readable specification of
the format that currently exists:

```python
import bitbully_databases as bbd

# board[row][col], row 0 at the top, 1 = first player, 2 = second player
board = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 1, 0, 2, 0, 0, 0],
    [0, 2, 0, 1, 0, 2, 0],
    [0, 1, 0, 2, 0, 1, 0],
    [0, 2, 0, 1, 0, 2, 0],
]

value = bbd.BitBullyDatabases("12-ply-dist").get_book_value(board)
print(value)                 # 71
print(f"player 1 wins in {100 - value} moves")
```

The high-level Python `BitBully` wrapper used for the measurements below loads the
distance-annotated 12-ply book by default, and its effect is quite substantial:

| Solving a 10-stone position | Nodes | Time |
| --- | ---: | ---: |
| Without opening book | 1,829,633 | 204.63 ms |
| With 12-ply book | 21 | 0.07 ms |

<details markdown="1">
<summary>How this was measured</summary>

40 random legal 10-stone positions, transposition table reset before each solve, `mtdf`
in both cases; the only difference is whether `reset_book()` was called. The without-book
row differs from the corresponding row of the node-count table in part 5 because it is a
different random sample of positions. Reproduce with `tools/connect4/book_stats.py`.

The comparison flatters the book somewhat — at ten stones the search is only two plies from
the book's horizon, so the book answers almost immediately. The honest way to read it is: the
book converts the hardest remaining part of the game into a lookup.

</details>

The sampled positions thus averaged about 21 nodes where the no-book run averaged more than
1.8 million. The three weeks of Pentium-4 time which were spent in 2012 have been amortised
over the subsequent uses of the database.

<br>

## Summary

We now have a representation, a move ordering, a memoisation of already computed values and a
precomputation of the opening phase. What is left is the component sitting on top of all of
this, namely the driver which decides with which windows the search is called, together with
the score convention which makes the whole scheme cohere. This is the subject of the next post,
and it is also the part which the 2012 engine never really got right.

<br>

## Source Code

Pinned to the commits this post was written against:

- **BitBully** — [`OpeningBook.h`](https://github.com/MarkusThill/BitBully/blob/50c45ff72113655b79878cf1022771298c449d84/src/OpeningBook.h),
  [`Board.h`](https://github.com/MarkusThill/BitBully/blob/50c45ff72113655b79878cf1022771298c449d84/src/Board.h) (`toHuffman`)
  · [GitHub](https://github.com/MarkusThill/BitBully) · [PyPI](https://pypi.org/project/bitbully/)
  · [Docs](https://markusthill.github.io/BitBully/)
  · [project page]({{ 'projects/0_bitbully/' | absolute_url }})
- **bitbully-databases** — [`bitbully_databases.py`](https://github.com/MarkusThill/bitbully-databases/blob/662de45918370bf0e76a8c6bb17a16b996551111/src/bitbully_databases/bitbully_databases.py)
  · [GitHub](https://github.com/MarkusThill/bitbully-databases)
  · [PyPI](https://pypi.org/project/bitbully-databases/)
  · [Docs](https://markusthill.github.io/bitbully-databases/)
  · [Python API](https://markusthill.github.io/bitbully-databases/python/)
  · [project page]({{ 'projects/1_bitbully_databases/' | absolute_url }})
- **John Tromp** — [original Connect-4 page](https://tromp.github.io/c4/c4.html)
  and [`Connect4.java`](https://tromp.github.io/c4/Connect4.java)
- **CFour** — [`Book.java`](https://github.com/MarkusThill/Connect-Four/blob/2a58844594ac022846385dd3ddc8bbbf0a26eae5/CFour/src/openingBook/Book.java)
  and the database pipeline under
  [`srcCPP/Databases`](https://github.com/MarkusThill/Connect-Four/tree/2a58844594ac022846385dd3ddc8bbbf0a26eae5/CFour/srcCPP/Databases)

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
