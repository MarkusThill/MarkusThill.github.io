---
layout: post
title: "Building Intelligent Agents for Connect-4&#58; First Steps"
modified: 2025-07-04T09:00:51+01:00
categories: [Programming]
description: "How a Java Connect-4 agent from 2012 led to the C++/Python solver BitBully, why the game is small enough to solve but large enough to make search engineering matter, and what this series will cover."
tags: [Connect-4, AI, tree-search, alpha-beta, minimax, transposition tables, opening databases, move ordering, bitboards]
thumbnail: assets/img/project_bitbully/c4-3.png
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-01-01T09:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
series: connect4-search
series_part: 1
# related_publications: true
---

{% include series_connect4.liquid %}


I first worked seriously on *Connect-4* in 2012, when I wrote the Java framework
[CFour](https://github.com/MarkusThill/Connect-Four) for experiments with tree search,
temporal-difference learning and Monte Carlo tree search. More recently I returned to the
perfect-playing part of that project and wrote [BitBully](https://github.com/MarkusThill/BitBully),
a C++ solver with Python bindings. The two programs are separated by roughly thirteen years,
which makes their different solutions to the same small game rather instructive.

This series documents the tree-search route from a plain Minimax procedure to the complete
solver. Connect-4 is a convenient subject for this because its rules fit on a few lines and the
game can still be solved to the end, while its game tree is much too large for an
unstructured exhaustive search. The old learning agents will return near the end of the
series, but the immediate question is how far careful representation, ordering, caching and
precomputation can take an exact search.

<!--more-->

<br>

## Board Games as AI Problems

Strategic board games have long been used as comparatively clean AI problems. Their rules and
goals are fixed, the state is usually discrete and fully observable, and an experiment can be
repeated under exactly the same conditions. At the same time, games such as chess, Go and
Connect-4 have state and action spaces large enough that a successful program still needs
something more interesting than enumerating moves without a plan. Planning, adversarial search,
pattern recognition and learning can therefore be studied without first having to model an
uncertain physical environment.

A historical curiosity is the so-called *Mechanical Turk*, built in 1769 by the Hungarian
inventor Wolfgang von Kempelen in the Habsburg Monarchy. Claimed to be an automated
chess-playing machine, it captivated audiences across Europe, until it was later revealed that a
human operator was hidden inside. Much later, during World War II, Konrad Zuse described a
[chess program in his own programming language *Plankalkül*](https://zuse-z1.zib.de/simulations/plankalkuel/chess/applet/applet.html);
the original version checked the legality of moves rather than evaluating them.

Milestones like IBM’s *Deep Blue* defeating world champion Garry Kasparov in 1997 showcased
the potential of highly optimized search, leveraging custom hardware to evaluate about 200
million positions per second. Search and learning have since been combined in many different
ways, but they still answer rather different questions.

Tree search and learning approach these games from rather different directions. A search
program derives a value from the rules by examining continuations, whereas a reinforcement
learning agent estimates values from experience and may share what it has learned across
positions through its function approximator. The latter can reduce the need for
position-specific search, but it does not remove the choices involved in representing the
state or constructing the learner. This series takes the first route and pushes classical tree
search until the game is solved perfectly; the {% include series_link.liquid part=9 text="final part" %}
then explains how the resulting solver can serve as a reference for the learning agents.


## Connect-4

*Connect-4* is a two-player game, typically played with the colours *Yellow* and *Red*, on a
vertical grid of seven columns and six rows. The board is empty at the start, and the first
player selects one of the seven columns.

Because the discs are dropped from above, a token occupies the lowest empty row of the selected
column. A column containing six tokens is no longer a legal choice. The players alternate until
one of them forms a connected line of four tokens or the board is full.

The four aligned discs may be:

- horizontal,
- vertical, or
- diagonal in either direction.

If neither player forms such a line before all 42 cells are filled, the game is drawn. The
following position is one example from a game between two of the agents discussed in this
series:

{% include figure.liquid
   path="assets/img/2026-01-01-connect-4-introduction-and-tree-search-algorithms/C4-example-position.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="50%"
   caption="Typical *Connect-4* position, created during a match of a temporal difference learning agent (Yellow) against a perfect-playing Minimax agent (Red), with Minimax as the next player to move. Both types of agents will be described in later posts. For the given position, Minimax is under zugzwang and will eventually lose the game; however, the defeat can be delayed as far as possible."
%}


Connect-4 has a state-space complexity of approximately
$$4.5 \cdot 10^{12}$$ distinct positions {% cite Edelkamp08 --file thesis %} and a game-tree
complexity around $$10^{21}$$ {% cite Allis94 --file thesis %}. These figures rule out a
direct enumeration of the game tree and make the representation and pruning methods used by
an exact solver consequential.

The first known solution was independently discovered by Allen {% cite Allen89 --file thesis %}
and Allis {% cite Allis88 --file thesis %} in 1988. They *weakly solved* the game,
demonstrating that, assuming perfect play from both players, Yellow can force a win by placing
her first token in the centre column.

In 1993, Tromp {% cite Tromp93 --file thesis %}{% cite Allis94 --file thesis %} went further and
*strongly solved* the game by computing the game-theoretic values of the positions at eight
plies. The publicly available machine-learning dataset, donated to UCI in 1995
{% cite Tromp95 --file thesis %}, is a subset of this work: it contains 67,557 unfinished and
unforced positions rather than the complete database.

> **Note:** Forced positions can be omitted from a solver's book because the search can derive
> the forced reply directly. For the other omitted class, in which the game still continues, I
> later added 19,336 positions where Red (the player who has just moved at eight plies) has a
> threat that Yellow can neutralize.

The complete computation took approximately 40,000 CPU hours (about 4.5 years on a single
processor of that period).

The table below shows the legacy counter's count at each ply and its cumulative sum. With 12
tokens placed, for example, that cumulative count is still about $$2.5 \cdot 10^5$$ times
smaller than the broader legal-position count for the complete game (the latter is taken from
{% cite Edelkamp08 --file thesis %}). The two conventions begin to differ at seven plies, as
explained immediately below the table.

The table was generated with the legacy Java
[`CountPositionsC4`](https://github.com/MarkusThill/Connect-Four/blob/2a58844594ac022846385dd3ddc8bbbf0a26eae5/CFour/src/miscellaneous/CountPositionsC4.java)
counter from the appendix. BitBully also has a
[Python enumeration interface](https://github.com/MarkusThill/BitBully?tab=readme-ov-file#further-usage-examples-for-bitbully-core),
but, as explained below, it follows a broader convention after six plies.


Plies |	Legacy Leaf Count |	Legacy Cumulative Count
0 |	1 |	1
1 |	7 |	8
2 |	49 |	57
3 |	238 |	295
4 |	1,120 |	1,415
5 |	4,263 |	5,678
6 |	16,422 |	22,100
7 |	53,955 |	76,055
8 |	181,597 |	257,652
9 |	534,085 |	791,737
10 |	1,602,480 |	2,394,217
11 |	4,231,877 |	6,626,094
12 |	11,477,673 |	18,102,767
$$\vdots $$ |	$$\vdots $$ |	$$\vdots$$
42 |	? |	$$4,531,985,219,092 \approx 4.5 \times 10^{12}$$ (broader convention)

[OEIS A212693](https://oeis.org/A212693) gives the corresponding counts under a broader
position convention. The two sequences agree through six plies; from seven plies onwards, the
Java counter applies a solver-oriented cutoff. As soon as its ordered move loop encounters an
immediate winning move, it returns from the whole node: it neither records the winning child
nor explores the siblings which follow it. The current BitBully enumerator and A212693 continue
through those branches, which is why they give 54,859 rather than 53,955 positions at seven
plies, for example.

<br>

## A Connect-4 Agent Based on Tree-Search Techniques
### Summary of the Upcoming Blog Posts

The 2012 agent began as a simple **Minimax** search and was gradually extended until it could
play perfectly. BitBully retains most of the same ideas, although the representation and the
root search driver have changed. Showing both versions is useful here, since it separates the
general techniques from choices that only happened to work well in one implementation.

For *Connect-4*, we benefit from **Tromp’s 8-ply opening database**, which I further extended
with the neutralizable threat positions described above. Additionally, I generated a
**Huffman-encoded opening database** for positions with **exactly 12 tokens**, storing both the
expected outcome and the precise number of moves remaining until the end of the game (under
perfect play).

The core **Minimax search** is enhanced with several techniques, each of which gets its own
instalment later in the series:

- **Alpha-Beta Pruning**: {% include series_link.liquid part=2 text="part 2" %}
- **Move Ordering**, **threat detection** and **symmetry exploitation**: {% include series_link.liquid part=4 text="part 4" %}
- **Zobrist Hashing**, **two-stage transposition tables** and **enhanced transposition cutoffs (ETC)**: {% include series_link.liquid part=5 text="part 5" %}
- **Opening databases** and their Huffman encoding: {% include series_link.liquid part=6 text="part 6" %}
- **MTD(f)** and **null-window search**, the drivers that sit on top of alpha-beta: {% include series_link.liquid part=7 text="part 7" %}
- **Verification and benchmarking**, including independent checks and paired measurements:
  {% include series_link.liquid part=8 text="part 8" %}

### Bit-board Representation

Both agents use **bitboards** as their main board representation. Conceptually, two sets of 42
bits identify the cells occupied by the two players, although the C++ implementation stores
the occupied cells and the active player's cells instead of one board per colour. The
advantage is not that every operation automatically becomes faster, but that the important
ones can be expressed through a small number of whole-word shifts and masks. {% include series_link.liquid part=3 text="Part 3" %}
works through both layouts, including the guard bits deliberately left unused by the modern
C++ engine.

### Historical and Current Runtime Measurements

The historical Java agent solved the empty board on a Pentium-4 in under four minutes,
without an opening book and with its default transposition tables of roughly 25 MB. In the
later paired benchmark, BitBully required a mean of 197.5 seconds on a Fujitsu
LIFEBOOK N532 from 2012, again without an opening book, while the reference solver required
386.3 seconds under the same test setup. These figures come from different programs and
machines, so they are context rather than a direct generational comparison; the full
methodology and the less favourable benchmark rows are given in
{% include series_link.liquid part=8 text="part 8" %}.

<br>

{% tabs log %}

{% tab log Python/C++ %}

## The C++/Python Solver BitBully

**BitBully** is the more recent, perfect-playing implementation. Its C++ core contains the
bitboard, threat-based move ordering, direct-mapped transposition table and the MTD(f) and
null-window drivers described in this series. The high-level Python wrapper adds a convenient
board interface and loads the distance-annotated 12-ply book by default, while still allowing
the book to be disabled for a search-only solve. The source and package are available on
[GitHub](https://github.com/MarkusThill/BitBully), [PyPI](https://pypi.org/project/bitbully/)
and in the [API documentation](https://markusthill.github.io/BitBully); there is also a short
[project page]({{ 'projects/0_bitbully/' | absolute_url }}).

{% endtab %}

{% tab log Java %}

## Connect-4 Java Framework

The earlier [Java repository](https://github.com/MarkusThill/Connect-Four) is broader than the
solver alone. In addition to `AlphaBetaAgent`, it contains the graphical application and the
temporal-difference and Monte Carlo tree-search agents for which the framework was originally
useful. Its search code is considerably longer and less convenient to reuse than BitBully's,
but it preserves the experiments and source-generation utilities from 2012 and is therefore
the better source for the historical parts of this series.

{% endtab %}

{% endtabs %}

<br>

## Counting Positions on the Connect-4 Board with up to 12 Plies

{% tabs count %}

{% tab count Python %}

```python
from bitbully import bitbully_core as bbc

b = bbc.Board()  # empty board
board_list_3ply = b.allPositions(3, True)  # All positions with exactly 3 tokens
len(board_list_3ply)  # should be 238 according to https://oeis.org/A212693
```

{% endtab %}

{% tab count Java %}

```java

package miscellaneous;

import java.util.Arrays;
import java.util.HashSet;
import c4.ConnectFour;

/**
 * * Always do 3 runs for counting the positions. First, count all positions
 * with a yellow stone in the left-bottom-corner, then with a red stone, and
 * last run when left-bottom-corner is empty. This is done, because the Hashset
 * can be reset after each run, and doesn't need that much memory.
 *
 * @author Markus Thill
 *
 */
public class CountPositionsC4 extends ConnectFour {
	private int maxDepth = 6;
	private boolean countAll = false;
	private long count = 0;
	HashSet<LongArr> hs = new HashSet<LongArr>(16777216);

	private static final long MASK = 0x20000000000L;
	int run = 0;

	private void tree(int depth, int player) {
		if (depth == maxDepth || countAll) {

			boolean putElement = false;
			switch (run) {
			case 0: // yellow stone in bottom-left corner
				putElement = (fieldP1 & MASK) == MASK;
				break;
			case 1: // red stone in bottom-left corner
				putElement = (fieldP2 & MASK) == MASK;
				break;
			case 2: // no stone in bottom-left corner
				putElement = ((fieldP1 | fieldP2) & MASK) == 0x0L;
				break;

			}

			if (putElement) {
				LongArr key = new LongArr(fieldP1, fieldP2);
				if (hs.add(key)) {
					count++;
					if ((count & 0xFFFFL) == 0xFFFFL) {
						System.out.println("Count until now: " + count);
						System.gc();
					}
				}
			}
			if (depth == maxDepth)
				return;
		}

		int moves[] = generateMoves(player, true);
		for (int i = 0; moves[i] != -1; i++) {
			if (canWin(moves[i]))
				return;
			putPiece(player, moves[i]);
			tree(depth + 1, player == PLAYER1 ? PLAYER2 : PLAYER1);
			removePiece(player, moves[i]);
		}
	}

	/**
	 * @param toPly
	 *            number of plys, for which number positions are calculated
	 * @param countAll
	 *            count all positions, not only leaf-nodes
	 */
	public void countPositions(int toPly, boolean countAll) {
		resetBoard();
		hs.clear();
		maxDepth = toPly;
		count = 0;
		this.countAll = countAll;

		for (run = 0; run < 3; run++) {
			resetBoard();
			hs.clear();
			maxDepth = toPly;
			tree(0, PLAYER1);
		}

		if (!countAll)
			System.out.println("Number of different positions for exactly "
					+ maxDepth + " stones: " + count + "");

		else
			System.out.println("Number of different positions with 0 to "
					+ maxDepth + " stones: " + count + "");
	}

	/**
	 * @param plyRange
	 *            number of plys (range), for which number positions are
	 *            calculated
	 * @param countAll
	 *            count all positions, not only leaf-nodes
	 */
	public void countPositions(int[] plyRange, boolean countAll) {
		for (int i = plyRange[0]; i <= plyRange[1]; i++)
			countPositions(i, countAll);
	}

	private class LongArr {
		private long arr[];

		LongArr(long val1, long val2) {
			arr = new long[] { val1, val2 };
		}

		public int hashCode() {
			return Arrays.hashCode(arr);
		}

		public boolean equals(Object obj) {
			LongArr o = (LongArr) obj;
			return Arrays.equals(arr, o.arr);
		}
	}

	public static void main(String[] args) {
		CountPositionsC4 cp = new CountPositionsC4();
		cp.countPositions(0, false);
		// cp.countPositions(new int[]{0,9},false);
	}
}

```

{% endtab %}

{% endtabs %}

<br>

## References

<div class="publications">
{% bibliography --file thesis --cited --group_by none %}
</div>
