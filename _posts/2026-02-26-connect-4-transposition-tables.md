---
layout: post
title: "Building Intelligent Agents for Connect-4&#58; Transposition Tables"
modified: 2026-06-30T09:00:51+01:00
categories: [Programming]
description: "Why the same Connect-4 position keeps reappearing in the search tree, how Zobrist hashing exploits three properties of the exclusive OR, and why the more recent solver manages without it entirely."
tags: [Connect-4, AI, tree-search, alpha-beta, minimax, transposition tables, opening databases, move ordering, bitboards, zobrist hashing]
thumbnail: assets/img/project_bitbully/c4-3.png
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-02-26T09:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
series: connect4-search
series_part: 5
---

{% include series_connect4.liquid %}

Starting from an empty board, the move sequence `3, 4, 2, 5` reaches exactly the same position
as `2, 5, 3, 4`. A plain alpha-beta search does not remember this and may therefore search
overlapping parts of the continuation more than once.

Using transposition tables (hash tables) is another way to speed up the tree search. They are
mainly used to avoid multiple analyses of individual positions, and thus of whole subtrees,
during the search. In games with many transpositions this can save a substantial number of
nodes, but the actual benefit depends on the game, table size, replacement policy and search
order; it has to be measured rather than assumed.

<!--more-->

This post describes how such a table is built, and also covers a small surprise: the 2012
engine is based on Zobrist hashing, which is one of the best-known techniques in game
programming, while the more recent engine does without it entirely.

<br>

## Permutations of Move Sequences

In many games, changes in the order of moves within a move sequence often lead to the same
position. The different arrangements of a move sequence can also be referred to as
permutations, whereby a permutation represents a bijective mapping of a set of moves onto
itself. The individual permutations can be generated using a finite number of transpositions,
where a transposition is defined as a permutation which exchanges exactly two elements with
each other.

It should be noted that not all permutations of a move sequence necessarily lead to the same
position. Individual permutations may contain impossible moves or might result in other states.
In a chess game, for example, it is not possible to move a piece to a square which is already
occupied by another piece of the same player, and this could happen with certain changes in the
move sequence. Furthermore, a single transposition in which a move of one player is swapped
with a move of the opponent results in an illegal move sequence, since two moves of the same
player would follow each other directly. It is therefore better to keep the moves of each
player in separate move lists.

But even then, not all permutations of the separate move sequences necessarily lead to
identical states. In the game of Connect-4 this is prevented by the gravity rule of the game,
and in the case of chess or checkers, for example, by the capturing moves. Tic-Tac-Toe and
Gomoku, on the other hand, are games for which all permutations of a move sequence, each
treated separately for both players, lead to the same position provided that the reordered
sequence remains legal and does not end the game earlier. Connect-4 sits just below these,
which is to say that it is permutable enough for transpositions to be very common, and this is
exactly what makes a transposition table worthwhile.

<br>

## A Hash Method according to Albert L. Zobrist

In order to cache a position, a key is required. Since under certain circumstances several
million nodes of the search tree are examined per second, a particular efficiency of the hash
method is necessary. Therefore, a function is sought which maps a state of the game to a hash
value without any special effort. Albert L. Zobrist already introduced such a procedure in 1970
{% cite Zobrist70 --file thesis %}. It is particularly suitable for board games, is nowadays
widely used in chess programming, and it is also what CFour relies on.

The central operation for Zobrist hashing is the bitwise exclusive OR, with which random
numbers are combined to obtain a fixed-width position hash. In general, a list of random
numbers is created, each of which corresponds to a piece at a certain position, and a separate
set is needed for each player. The number of required random numbers can therefore be
described as the number of players times the number of piece types per player times the number
of fields, where certain special moves may have to be encoded separately. For Connect-4 this
amounts to

$$
N_\text{random} = \underbrace{2}_{\text{players}} \times \underbrace{42}_{\text{cells}} = 84
$$

random values, which the 2012 project generated with a small dedicated C++ tool and pasted
into the source code as `rnd[2][42]`. When a token is added, the current hash is simply updated
by XOR-ing it with the corresponding random number.

```java
public static long toZobrist(long f1, long f2) {
    long zobristKey = 0L;
    for (int i = 0; i < 7; i++) {
        for (int j = 0; j < 6; j++) {
            int stelle = 41 - (i * 6 + j);
            long temp = (1L << stelle);
            if      ((f1 & temp) == temp) zobristKey ^= rnd[0][i * 6 + j];
            else if ((f2 & temp) == temp) zobristKey ^= rnd[1][i * 6 + j];
            else break;                       // gravity: nothing above an empty cell
        }
    }
    return zobristKey;
}
```

The scheme works because of three basic properties of the exclusive OR, and it is worth
spelling out which property buys which feature.

The first is that XOR is associative and commutative, so that
$$(x \oplus y) \oplus z = x \oplus (y \oplus z)$$ and $$x \oplus y = y \oplus x$$ hold.
Consequently, the sequence of the individual moves is not relevant for the construction of the
hash, and permutations of a move sequence lead to the same hash if the resulting positions are
identical. This is precisely the property we need here, since recognizing reordered move
sequences is the entire point of the exercise.

The second is that $$x \oplus x = 0$$, which allows a piece to be removed from the hash again by
XOR-ing its random number a second time. To move a piece, it is first removed from the hash and
then reinserted elsewhere, which requires two XOR operations. This makes the hash incrementally
modifiable. During ordinary recursive descent in Connect-4, where a move only ever adds a
token, the carried key is updated with one XOR. CFour still recomputes root keys and mirrored
keys with `toZobrist(...)` where they are needed.

The third property is that XOR preserves a uniform distribution when the random inputs are
independent and at least one of them is uniformly distributed over the $$n$$-bit words. This is
by no means the case for all operations; a bitwise AND, for instance, drives every bit towards
zero and would pile all positions onto a handful of hash values.

I find this combination rather elegant, and for chess it is close to indispensable, since a
chess position requires considerably more than 64 bits to write down and the incremental hash
is therefore a convenient compact signature. A further remark should be made, though: Zobrist
hashes are not unique, as the mapping of the game states to the set of hash values is not
injective. In the game of Connect-4, occasional errors could indeed be observed when 32-bit
hashes were used. With 64-bit hashes no more errors appeared, although they cannot be excluded
in principle.

<br>

## When Zobrist Hashing is not needed

This brings us to the somewhat surprising part. BitBully computes no Zobrist key at all, stores
no tables of random numbers, and updates nothing incrementally. Instead, it simply uses:

```cpp
[[nodiscard]] uint64_t uid() const { return m_bActivePTokens + m_bAllTokens; }
```

As described in part 3, this single addition already produces an exact key which identifies the
position together with the player to move uniquely, so there is nothing left for a Zobrist hash
to compress. Zobrist hashing is useful when a larger state needs a compact, incrementally
maintained signature. A Connect-4 position, in a suitable encoding, already fits into 64 bits.

What is still required is a good distribution of the values, since the `uid()` values are far
from being uniformly distributed and using their low bits directly as a table index would lead
to considerable clustering. BitBully therefore mixes the state through David Stafford's Mix13
finalizer, which is a three-step avalanche function:

```cpp
[[nodiscard]] static uint64_t hash(uint64_t x) {
  x = (x ^ (x >> 30)) * UINT64_C(0xbf58476d1ce4e5b9);
  x = (x ^ (x >> 27)) * UINT64_C(0x94d049bb133111eb);
  x = x ^ (x >> 31);
  return x;
}
```

Each step mixes the high bits into the low ones by means of the shift and the XOR, and then
diffuses them across the whole word by means of the odd multiplier. After three rounds,
flipping a single input bit changes about half of the output bits, which is exactly the
behaviour one wants from a table index. BitBully keeps the exact key and the index hash
separate: the table index applies this finalizer to each of the two bit boards and combines the
results, `hash(hash(m_bActivePTokens) ^ (hash(m_bAllTokens) << 1))`, while the raw `uid()` is
what the entry stores to verify a hit.

The honest generalization is therefore that Zobrist hashing earns its keep whenever the state
does not fit into a machine word, or whenever the incremental update represents a real saving.
For Connect-4 with a Tromp-style position code neither of the two applies, and the 84 random
constants together with the per-node bookkeeping can simply be omitted.

<br>

## Sizing and Indexing the Table

The table is an array of $$2^k$$ slots, and the reason for the power of two is a small
arithmetic identity:

$$
x \bmod 2^k = x \mathrel{\&} (2^k - 1)
$$

A modulo becomes a single AND — the same trick, in the same setting, that I worked through in
[A few Bit-Twiddling Tricks]({% post_url 2024-12-11-soa-few-bit-twiddling-tricks %}). Compilers
commonly make this replacement when the divisor is a compile-time constant. Here, however,
`tableSize` is a runtime value, so its power-of-two invariant may not be visible to the
compiler. In BitBully the whole lookup is one line:

```cpp
inline Entry* get(const Board& b) {
  return &table[b.hash() & (tableSize - 1)];
}
```

<br>

## Visualising Transpositions

The chain from position to table slot is easier to appreciate when the numbers can be watched
while they change, so the following widget maintains a miniature transposition table of 64
slots which deliberately survives board resets. Playing `3, 4, 2, 5`, resetting the board, and
then playing `2, 5, 3, 4` (the two buttons do exactly this) reaches the same position along two
different paths. The second arrival is reported as a table hit, which is the entire effect this
post is about. The readout also shows the avalanche at work: a single
move typically changes only a handful of bits in `uid()`, while the hash computed from the
position flips around half of its 64 bits, and the highlighted digits make this directly
visible.

<link rel="stylesheet" href="{{ '/assets/css/connect4-widgets.css' | relative_url }}" />

<div class="c4bb" data-c4-hash></div>

<script src="{{ '/assets/js/connect4-core.js' | relative_url }}"></script>
<script src="{{ '/assets/js/connect4-hash.js' | relative_url }}"></script>

With only 64 slots, collisions appear rather quickly, and it is worth producing one on purpose
by simply playing on for a while. A red slot then holds two different positions, which is
precisely the situation in which the stored `uid` decides between a genuine hit and a false
one. The current BitBully source defaults to $$2^{22}$$ slots rather than $$2^{6}$$, so
collisions are far rarer there; the historical benchmark reported in part 8 used a
$$2^{20}$$-slot build. As with the widgets of the previous posts, the JavaScript is a
transcription of the C++ shown above and is checked against the real engine by
`tools/connect4/check_widget.mjs`.

<br>

## Design of the Transposition Tables

This is the part which is rather easy to get subtly wrong. A naive table stores a mapping from
positions to values, but an alpha-beta search does not always compute an exact value. Whenever
it prunes, all it learns is a bound, that is, the information that the value is at least or at
most as good as a certain number. Caching such a bound as though it were an exact value
corrupts the search.

Each entry in a transposition table therefore consists of several elements, one of which
records which of the three cases applies:

```cpp
struct Entry {
  enum NodeType {
    NONE  = 0,   ///< Empty slot.
    EXACT = 1,   ///< Exact score (PV node).
    LOWER = 2,   ///< Lower bound (fail-high cut node).
    UPPER = 3    ///< Upper bound (fail-low all node).
  };
  uint64_t b;           ///< Position UID -- to detect hash collisions.
  NodeType flag{NONE};
  int value;
  int8_t searchDepth{0};  ///< Remaining budget when stored; INT8_MAX = full search.
};
```

The four fields have four rather distinct purposes. The field `value` holds the value or the
bound, and `flag` records which of the two it is. The classification follows directly from
where the value ended up relative to the original window: at or below the incoming alpha it is
an upper bound and the node has failed low, at or above beta it is a lower bound and the node
has failed high, and strictly between the two it is exact. The field `searchDepth` records how
much search the value is worth, since a value obtained from a shallow, depth-limited search
must not be reused to answer a deeper question, where `INT8_MAX` marks a complete search.
Finally, the field `b` holds the `uid()` of the position, so that a lookup can distinguish a
genuine hit from two different positions which happen to land in the same slot.

For each node, the system first checks whether an entry exists in the corresponding
transposition table. If this is the case, the search can in many cases be interrupted at this
point and the corresponding value returned. Otherwise the search continues as usual and the
result for the node is inserted into the table afterwards. On a hit the three cases are used
differently: an exact value can be returned immediately, a lower bound raises alpha, and an
upper bound lowers beta. If this collapses the window, the node is finished without a single
move having been searched.

```cpp
if (ttEntry->flag == TranspositionTable::Entry::EXACT) {
  return ttEntry->value;
} else if (ttEntry->flag == TranspositionTable::Entry::LOWER) {
  alpha = std::max(alpha, ttEntry->value);
} else if (ttEntry->flag == TranspositionTable::Entry::UPPER) {
  beta = std::min(beta, ttEntry->value);
}
if (alpha >= beta) return ttEntry->value;
```

#### Dealing with Collisions

Since a table index uses only the low $$k$$ bits of the mixed hash, different exact keys can
select the same slot even when their full 64-bit hashes differ. Such table-index collisions
cannot be avoided, but there are some strategies for dealing with them. For the 2012 project
only linear probing was tested, and since it did not reduce the runtime, already existing
entries are simply overwritten in the case of a collision. BitBully also tried an experimental
guard which kept an existing exact entry for a node closer to the root when a colliding
position lay more than 16 plies deeper. The relevant notion of depth here is the ply distance
from the root, so that a node closer to the root is one with more work still remaining below
it, rather than the remaining budget of a depth-limited search. The block remains commented
out with the verdict "Does not help!" attached to it.

Storing the `uid` alongside the value is what makes the always-replace strategy safe, since a
wrong slot is detected rather than silently believed. It is worth noting that the residual risk
is real but rather different in the two designs. CFour stores a 64-bit Zobrist key, so two
positions with identical keys cannot be distinguished at all, whereas BitBully stores the exact
`uid()`, which is not a hash value in the first place. The table of BitBully can therefore
never return a wrong entry, only a miss.

<br>

## Three further Refinements

#### Probing on even Plies, Cutting on odd ones

BitBully does not consult the table in every node, but splits the nodes according to the parity
of the remaining move count:

```cpp
if (b.movesLeft() > 6 && b.movesLeft() % 2 == 0) {
  // normal transposition-table probe
} else if (depth < 22 && b.movesLeft() % 2) {
  // Enhanced Transposition Cutoff instead
}
```

Positions with an even number of remaining moves and positions with an odd number belong to
disjoint halves of the tree, and storing both classes in one table increases the pressure on
it. Restricting the stores to one parity therefore reduces the number of distinct keys which
compete for the available slots. This is the same reasoning which led to the two-stage
transposition table of the 2012 agent, where the separation brought significant runtime
advantages mainly because entries for nodes near the root are not overwritten by the far more
numerous ones from deep in the tree.

#### Enhanced Transposition Cutoffs

On the odd plies, BitBully does something slightly cleverer than a plain probe. Instead of
asking whether the current position is already known, it asks whether any of its successors is
known, and it does so before recursing into any of them:

```cpp
auto etcMoves = b.legalMovesMask();
while (etcMoves) {
  auto mv = b.nextMove(etcMoves);
  auto bETC = b.playBitMaskOnCopy(mv);
  auto etcEntry = transpositionTable.get(bETC);

  if (etcEntry->b == bETC.uid() && etcEntry->searchDepth >= remainingBudget &&
      etcEntry->flag != TranspositionTable::Entry::LOWER &&
      -etcEntry->value >= beta) {
    return -etcEntry->value;      // cutoff without searching anything
  }
  etcMoves ^= mv;
}
```

The pay-off here is asymmetric, and that is precisely the point. A normal probe only helps if
this exact node has been seen before, whereas an enhanced transposition cutoff helps if any one
of up to seven successors has been seen before, and a single hit ends the node immediately.
Seven cheap table lookups against the cost of recursing into a subtree is a good trade near the
root, which is why the technique is restricted to `depth < 22`.

#### Exploiting Symmetries

A position and its mirror image along the middle column have the same value, so a miss on the
position itself is worth a second lookup on its mirror image:

```cpp
if (b.movesLeft() > 20) {
  const auto bMirror = b.mirror();
  auto ttEntryMirror = transpositionTable.get(bMirror);
  // ... same EXACT / LOWER / UPPER handling as above
}
```

It is worth asking how much this actually saves. Every position which is not self-symmetric
pairs up with a distinct mirror image, so identifying the two collapses the space by very
nearly one half:

| Stones on board | Distinct positions | After mirror dedup | Saved |
| ---: | ---: | ---: | ---: |
| 4 | 1,120 | 568 | 49.3% |
| 5 | 4,263 | 2,144 | 49.7% |
| 6 | 16,422 | 8,231 | 49.9% |
| 7 | 54,859 | 27,473 | 49.9% |
| 8 | 184,275 | 92,244 | 49.9% |

<details markdown="1">
<summary>How this was measured, and a note on the counts</summary>

Enumerated with `Board::allPositions(n, exactly=True)`, keeping `min(uid, mirror.uid)` as the
representative of each mirror pair. Reproduce with `tools/connect4/bench_tt_size.py`.

These counts agree with the current [OEIS A212693](https://oeis.org/A212693) values for every
row shown. The smaller seven- and eight-ply figures quoted in
{% include series_link.liquid part=1 text="part 1" %} (53,955
and 181,597) come from its legacy Java `CountPositionsC4` counter: it stops expanding a
position as soon as the side to move has an immediate winning move. `Board::allPositions` and
the current OEIS use the broader legal-position count represented here. The
mirror-deduplication ratio is computed consistently from that latter set.

</details>

Incidentally, the self-symmetric positions which account for the missing 0.1% are not merely a
rounding error. They are also exactly those positions in which the move generator can skip
three of the seven columns, as mentioned in part 4. The 2012 agent tracks them explicitly with
an `isSymmetric()` test and, rather more interestingly, with a `symPossible()` test which asks
whether a symmetry could still arise later in the subtree.

The mirror lookup is switched off once `movesLeft <= 20`. Symmetric positions become
increasingly rare as the board fills up, and beyond that point the additional lookup costs more
than it returns.

<br>

## The Search with Transposition Tables

With the table in place, the following node counts can be observed across the game, where
BitBully solves random positions to their full game-theoretic value with the opening books
disabled:

| Stones on board | Nodes per solve | Time per solve |
| ---: | ---: | ---: |
| 10 | 3,266,438 | 321 ms |
| 12 | 485,006 | 73 ms |
| 14 | 119,933 | 21 ms |
| 16 | 62,225 | 11 ms |
| 18 | 17,757 | 3.5 ms |
| 20 | 4,046 | 1.0 ms |

<details markdown="1">
<summary>How this was measured</summary>

40 random legal positions per ply (`Board.random_board(forbid_direct_win=True)`), transposition
table and node counter reset before each solve, opening book explicitly disabled so the search
does the work. Reproduce with `tools/connect4/bench_tt_size.py`.

</details>

The sampled positions with 20 tokens therefore required roughly four thousand searched nodes
on average. The size of an exhaustive continuation tree depends strongly on the position, so
the measured node count is the more useful quantity here.

The upper end of the table is the more interesting one, however. With ten tokens on the board a
solve still costs about a third of a second and roughly three million nodes, and the effort
grows further towards the empty board. Further search refinements may reduce that cost, but an
opening database attacks it more directly by replacing some of the search with a lookup. That
is the subject of the next post.

<br>

## Source Code

Pinned to the commits this post was written against:

- **BitBully** — [`TranspositionTable.h`](https://github.com/MarkusThill/BitBully/blob/50c45ff72113655b79878cf1022771298c449d84/src/TranspositionTable.h),
  [`BitBully.h`](https://github.com/MarkusThill/BitBully/blob/50c45ff72113655b79878cf1022771298c449d84/src/BitBully.h)
  (the probe / ETC / mirror block inside `negamax`),
  [`Board.h`](https://github.com/MarkusThill/BitBully/blob/50c45ff72113655b79878cf1022771298c449d84/src/Board.h) (`uid`, `hash`)
- **CFour** — [`AlphaBetaAgent.java`](https://github.com/MarkusThill/Connect-Four/blob/2a58844594ac022846385dd3ddc8bbbf0a26eae5/CFour/src/c4/AlphaBetaAgent.java)
  (`toZobrist`, `isSymmetric`, `symPossible`, the two-stage tables), and the Zobrist key
  generator under
  [`srcCPP/Generate Zobrist Keys`](https://github.com/MarkusThill/Connect-Four/tree/2a58844594ac022846385dd3ddc8bbbf0a26eae5/CFour/srcCPP/Generate%20Zobrist%20Keys)

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
