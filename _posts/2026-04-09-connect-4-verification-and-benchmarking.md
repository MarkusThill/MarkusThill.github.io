---
layout: post
title: "Building Intelligent Agents for Connect-4&#58; Verification and Benchmarking"
modified: 2026-07-21T09:00:51+01:00
categories: [programming]
description: "How independent opening-book answers, mirror invariants and driver agreement provide evidence of correctness, followed by a paired timing comparison with stated statistical assumptions."
tags: [Connect-4, AI, tree-search, alpha-beta, minimax, benchmarking, wilcoxon, testing, transposition tables, opening databases, bitboards]
thumbnail: assets/img/project_bitbully/c4-1.png
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-04-09T09:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
series: connect4-search
series_part: 8
---

{% include series_connect4.liquid %}

In the course of this series the alpha-beta search has reached an enormous scope. Every post so
far has added a technique which is individually plausible and collectively rather worrying:
precomputed masks, machine-generated branch trees, a move generator which deliberately omits
moves, a table which overwrites its own entries, a search which returns bounds instead of
values, and depth-gated heuristics which behave one way above ply 20 and differently below it.

Any one of these can be subtly wrong in a way which only shows up as a wrong game-theoretic
value deep in a rare position. This post therefore deals with the two questions which follow
from this, namely how one can gather convincing evidence that the program is correct, and how
one can show that a change has actually made it faster.

<!--more-->

Both questions are harder than they look, and in my experience the answers are the most
transferable material of the whole series, since they have very little to do with Connect-4
itself.

<br>

## Limits of Direct Test Cases

The obvious approach of writing down a number of positions together with their expected values
is incomplete here, and for three reasons.

The first is that the coverage of such tests is limited. Many of the methods used apply only to
specific situations during the search and are therefore situational by construction.
Enhanced transposition cutoffs only fire on odd plies below depth 22, the mirror lookup only
runs while more than 20 moves remain, and the double-threat shortcut only triggers when two of
one's own threats happen to be stacked on top of each other. A handful of hand-picked positions
will exercise none of these paths, and a bug in any of them corrupts a small and rather
unpredictable slice of the search space.

The second reason is that independent oracles are scarce. For most software a result can be
checked by hand, but the game-theoretic value of an arbitrary Connect-4 position with ten
tokens is not something which can be verified by inspection. Tromp's eight-ply book supplies
one useful exception later in this post, but it covers only a particular slice of the state
space.

The third reason is the one which bites hardest, namely that faster is not the same as better.
A change which demonstrably reduces the node count can still be slower, because avoiding the
saved nodes costs more than visiting them would have. Furthermore, a change which helps
enormously on one class of positions can hurt on another, so that a single benchmark position
tells us essentially nothing. As I noted back in 2012:

> Changes to the source code can often have a positive effect on runtime performance in many
> situations, but not in others. Therefore, it is often not possible to make a statement about
> whether a modification actually causes a speed-up, even if significant node savings can be
> observed.

<br>

## Four Practical Checks

#### Making the Program disagree with itself

Part 7 left us with three drivers, namely `mtdf`, `negamax` and `null_window`, all of which sit
on top of the same recursive search. They probe with completely different sequences of
alpha-beta windows, which means that they visit different nodes, take different cutoffs and
populate the transposition table differently. Nevertheless they have to return the same number.

This is a useful consistency check, since the three exploration orders exercise the shared
machinery differently. It is not an independent oracle, however, and a deterministic bug in
that machinery can still make all three drivers return the same wrong answer.

#### Exploiting a Symmetry of the Game

A position and its mirror image have the same value. This makes symmetry a useful invariant,
even though BitBully also exploits it in its transposition lookups: solving both orientations
from freshly cleared tables can still expose asymmetric board operations or lookup handling.

```python
agent.reset_transposition_table()
score = agent.mtdf(board)
agent.reset_transposition_table()
mirrored_score = agent.mtdf(board.mirror())
assert score == mirrored_score
```

This is essentially property-based testing, and the general recipe is worth stating explicitly:
one looks for a transformation of the input under which the output has to remain invariant, and
then applies it to a large number of random inputs. It is not necessary to know the correct
answer, only that two computations have to produce the same one.

#### Checking the Units and not only the Value

The score convention of part 7 packs an outcome and a distance into a single integer, and
`score_to_moves_left` unpacks it again. The result has stronger sanity constraints than merely
fitting onto the board. A positive score means that the player to move wins after an odd number
of plies, a negative score means a loss after an even number, and a draw fills the remaining
cells. A parity slip in the XOR described there could sail past a simple range check, but it
fails this invariant immediately.

#### Comparing against an External Oracle

The three checks described above share one weakness, namely that they all compare the program
against itself. A symmetric, parity-preserving bug in a shared function such as
`Board::winningPositions` could make all three drivers return the same wrong value while still
passing the mirror and score-unit checks.

The most direct way to address this is to compare against an independently produced answer.
John Tromp computed an 8-ply opening database in 1993
{% cite Tromp93 --file thesis %}{% cite Allis94 --file thesis %}, and its public subset was
donated in 1995 {% cite Tromp95 --file thesis %}, long before BitBully. Those entries are
therefore particularly useful for comparison. The packaged 8-ply book used here, however, also
contains 19,336 positions analyzed by an earlier version of my own alpha-beta agent, as
described in [part 6]({% post_url 2026-03-12-connect-4-opening-databases %}). It is therefore
only partly independent: it is a useful regression oracle, but comparisons against the added
entries cannot serve as independent validation. The procedure is to take a random position
with eight tokens, to solve it with the opening book explicitly disabled so that the search
actually does the work, and to compare the result against the book:

```python
agent = bb.BitBully()
agent.reset_book()          # do not consult the thing you are checking against
db = bbd.BitBullyDatabases("8-ply")

searched  = agent.mtdf(board)
from_book = db.get_book_value(to_row_major(board))
assert sign(searched) == sign(from_book)
```

The call to `reset_book()` is the essential part of this exercise, since with the book loaded
the search would simply answer from the book and the test would compare the database against
itself.

#### Results of the four Checks

| Check | Positions | Failures |
| --- | ---: | ---: |
| `mtdf` = `negamax` = `null_window` | 300 | 0 |
| `score(b)` = `score(mirror(b))` | 300 | 0 |
| Score sign, distance and remaining-cell parity agree | 300 | 0 |
| Search vs. packaged 8-ply book | 400 | 0 |

<details markdown="1">
<summary>How this was run</summary>

Random legal positions (`forbid_direct_win=True`), 16 stones for the first three checks and
8 stones for the book comparison. The book is disabled in the solver for every check, and the
transposition table is cleared before each solve so that one driver or orientation cannot
inherit another one's result. The script exits non-zero on any failure, so it works as a
regression test. Reproduce with `tools/connect4/verify.py`.

</details>

<br>

## A Paired Benchmarking Method

With these correctness checks in place, we can turn to the second question, namely whether a
version B is actually faster than a version A.

Solve times in Connect-4 are rather unpleasant data. They span more than four orders of
magnitude over the course of the game and vary strongly even within a single ply count, since
some positions resolve within microseconds while others are several orders of magnitude more
expensive. The resulting distribution has a long right tail; in the table below the standard
deviations are consistently larger than the means, which illustrates this quite well.

This makes several obvious analyses fragile. A single outlier can move an unpaired mean
considerably, a paired t-test would require the distribution of the paired differences to be
approximately normal, and running each solver on different positions adds variance which can
swamp the effect one is trying to measure.

Four design decisions address this. The first is to pair the samples, that is, to run both
solvers on the identical position and to compare within the pair. The difficulty of a position
is by far the largest source of variance, and pairing controls that common input effect so that
the analysis compares two numbers measured on the same input. The second is to control the
state by resetting the transposition table before every single solve, since otherwise the
second solver inherits a table which the first one has already warmed up and consequently looks
artificially good. The third is to alternate the measurement order so that one driver does not
systematically benefit from always running first or second. The fourth is to gate the whole
comparison on correctness: both solvers have to return the same value, and the run aborts if
they do not, since a faster wrong answer is not a result. This sounds obvious, but it is exactly
the check which catches supposed optimizations that quietly break a cutoff condition.

On top of this, a statistical test is needed which does not require normally distributed
differences. The Wilcoxon signed-rank test ranks the paired differences by magnitude and asks
whether the positive and negative ranks are balanced. It is designed for paired data and bounds
the influence of the largest observations through ranking. Interpreting it as a test of a
single location shift still assumes that the distribution of paired differences is reasonably
symmetric, so it is not assumption-free.

- $$H_0$$: the paired timing differences are centred on zero.
- $$H_1$$: the paired timing differences favour MTD(f).
- The $$p$$-value is the probability, **under $$H_0$$**, of obtaining a test statistic at least
  this extreme. Small $$p$$ means the advantage is consistent, not that it is large.

Applying that machinery to MTD(f) versus plain wide-window negamax:

| Stones | Repeats | MTD(f) [s] | Negamax [s] | Speed-up | $$p$$-value | Significant |
| ---: | ---: | :--- | :--- | ---: | ---: | :---: |
| 12 | 40 | 0.03491 ± 0.04237 | 0.04851 ± 0.05633 | 1.39× | 2.7e-06 | ✓ |
| 14 | 80 | 0.02669 ± 0.04417 | 0.04318 ± 0.09975 | 1.62× | 5.5e-05 | ✓ |
| 16 | 150 | 0.00955 ± 0.02142 | 0.01107 ± 0.02199 | 1.16× | 1.2e-11 | ✓ |
| 18 | 250 | 0.00280 ± 0.00506 | 0.00354 ± 0.00668 | 1.26× | 3.6e-11 | ✓ |
| 20 | 400 | 0.00096 ± 0.00195 | 0.00110 ± 0.00225 | 1.14× | 4.2e-13 | ✓ |
| 22 | 600 | 0.00043 ± 0.00084 | 0.00049 ± 0.00102 | 1.13× | 9.2e-13 | ✓ |

<details markdown="1">
<summary>How this was measured</summary>

Both drivers on the same random position, table reset before each, measurement order
alternated, score equality asserted, one-sided Wilcoxon signed-rank test via
`scipy.stats.wilcoxon`. Repeat counts rise with ply because individual solves get cheaper.
Reproduce with `tools/connect4/bench_paired.py`.

</details>

The ratios of the mean times range from 1.13 to 1.62, while the paired rank test finds a
consistent shift at every ply. These are related but different summaries: the ratio of means
describes total average workload and is especially sensitive to expensive positions, whereas
the Wilcoxon test ranks within-position differences. Note again how the standard deviations
dwarf the means, which illustrates the heavy tail mentioned above.

All of these arguments are easier to believe when the raw pairs are actually looked at, so the
following figure draws every one of the 1520 paired measurements behind the table:

{% include figure.liquid
   path="assets/img/2026-04-09-connect-4-verification-and-benchmarking/paired-timings.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="100%"
   caption="The raw data behind the table above. <b>Left:</b> every position solved by both drivers, one dot per pair, on logarithmic axes. The solve times span more than four orders of magnitude, which is the input variance that motivates pairing, while most dots lie just below the diagonal. <b>Right:</b> the same pairs as a per-position ratio. The median position is about 5.6% faster under MTD(f), and negamax wins on roughly 30% of the positions. The mean-based speed-up factors of 1.13–1.62 in the table are larger because expensive positions dominate a mean. A rank-based test provides a useful complementary summary of this picture. Generated by <code>tools/connect4/make_paired_figure.py</code> from the same run as the table."
%}

One caveat applies to every table of this kind: with a sufficiently large number of repeats,
even a very small consistent difference can become statistically significant. A very small
$$p$$-value therefore provides evidence against a centred difference under the stated
assumptions; it does not say that the effect is large. The speed-up column should be read for
the size of the effect and the $$p$$-value column for the consistency of the paired differences,
and one should never be read without the other.

<br>

## Comparison against a Reference Solver

The same basic paired design was used to compare BitBully against
[Pascal Pons' solver](https://github.com/PascalPons/connect4), which is a well-known and
genuinely strong reference implementation. The following numbers originate from the BitBully
repository rather than from the harness used for this post, since the baseline is a separate
C++ program. It uses the same core paired design: identical positions, opening books disabled
for both solvers, transposition tables reset, correctness asserted, and a paired Wilcoxon test.
The pinned benchmark driver always times BitBully first and the reference solver second, so the
counterbalanced order is an additional safeguard of the new MTD(f)-versus-negamax experiment
above rather than a feature of the historical comparison.

| Stones | Repeats | BitBully [s] | Baseline [s] | Speed-up | $$p$$-value | Significant |
| ---: | ---: | :--- | :--- | ---: | ---: | :---: |
| 0 (empty board) | 25 | 197.50 ± 7.85 | 386.32 ± 17.40 | 1.96× | 3.0e-08 | ✓ |
| 4 | 500 | 11.06 ± 13.00 | 15.51 ± 20.87 | 1.40× | 2.3e-37 | ✓ |
| 6 | 1000 | 2.158 ± 2.875 | 3.283 ± 4.690 | 1.52× | 5.3e-92 | ✓ |
| 8 | 1000 | 0.527 ± 0.648 | 0.820 ± 1.242 | 1.56× | 3.4e-62 | ✓ |
| 12 | 1000 | 0.049 ± 0.076 | 0.060 ± 0.118 | 1.23× | 3.7e-03 | ✓ |
| 14 | 2000 | 0.0176 ± 0.0286 | 0.0180 ± 0.0325 | 1.02× | 1.0 | ✗ |
| 16 | 2000 | 0.0065 ± 0.0131 | 0.0060 ± 0.0136 | 0.93× | 1.0 | ✗ |

The results show three distinct regimes, and the last one is the most interesting.

From the empty board up to about six tokens we are dealing with the hardest positions of the
game, where the branching factor is maximal and the solver has to explore a large fraction of
the tree. On the empty board itself BitBully requires just under 200 seconds against the 386
seconds of the baseline, which is very nearly a factor of two, and at four and six tokens
factors of 1.4 to 1.5 remain. This is the regime in which move ordering, pruning and the
search drivers all pay off at the same time.

Between roughly eight and twelve tokens a consistent advantage of about 1.2 to 1.6 remains,
which is still statistically significant, but the absolute saving collapses from minutes to
milliseconds. Improving from 0.8 s to 0.5 s matters considerably less than shaving three
minutes off an empty-board solve, even though the ratio is similar.

Beyond about 14 tokens the measured advantage disappears, and at 16 tokens BitBully is
nominally even slower. Both solvers finish these sampled positions within milliseconds, so
fixed overhead and timing noise matter increasingly. This experiment therefore provides no
evidence of a BitBully advantage in those rows, and in my opinion the honest thing is to
publish them anyway.

Two caveats which the BitBully README states should be repeated here, since a benchmark without
its caveats is closer to marketing than to measurement. The benchmark report records a
$$2^{20}$$-entry BitBully table against the baseline's default $$2^{24}$$ entries, which favours
the baseline. The pinned BitBully source now defaults to $$2^{22}$$ entries, so $$2^{20}$$
describes that historical benchmark build rather than the current default. The comparison also
measures wall-clock solve time only, rather than node counts or memory consumption.

For some historical context: searching from the empty board took the 2012 Java agent under
four minutes on a Pentium-4 computer to find out that the move into the middle column is the
best possible one, using its default transposition tables of roughly 25 MB and no opening book
at all. The more recent C++ benchmark reports just under 200 seconds on a Fujitsu LIFEBOOK
N532 from 2012. Since these are different programs measured on different machines, they provide
historical context rather than a controlled speed-up factor.

<br>

## Some general Conclusions

Almost none of the above is really specific to Connect-4, and the following points seem to me
to be the ones worth carrying over to other projects:

- One should test against something which one has not written oneself. Self-consistency checks
  cannot find a bug in an assumption which everything shares, and a single independently
  produced answer is worth a great many internal assertions.
- Where the expected output cannot be computed, it is often still possible to name a
  transformation which the output has to survive, and to test that instead.
- If the dominant source of variance is the input rather than the treatment, then comparing on
  identical inputs controls much of this variance at little cost.
- The statistics have to match the data. With heavy-tailed timings, paired rank-based tests can
  be more informative than an unpaired comparison of means; their assumptions and estimand
  should nevertheless be stated.
- The rows in which one loses should be published as well. In my view the rows from 14 tokens
  onwards are the most credible part of the benchmark table, precisely because they show no
  advantage at all.

<br>

## Summary

The solver is now complete, and there is substantially better evidence for its correctness.
One post remains, which collects the techniques that did not fit anywhere else, gives an
accounting of what each of them actually bought, and finally turns to the question which this
whole series has been circling around, namely that of a perfect player which has learned
nothing at all.

<br>

## Source Code

Pinned to the commit this post was written against:

- **BitBully** — [`main.cpp`](https://github.com/MarkusThill/BitBully/blob/50c45ff72113655b79878cf1022771298c449d84/src/main.cpp)
  (benchmark driver),
  [`notebooks/c4_analyze_runtimes.ipynb`](https://github.com/MarkusThill/BitBully/blob/50c45ff72113655b79878cf1022771298c449d84/notebooks/c4_analyze_runtimes.ipynb)
- **Baseline** — [PascalPons/connect4](https://github.com/PascalPons/connect4). BitBully was
  inspired by the solvers of [Pascal Pons](https://github.com/PascalPons/connect4) and
  [John Tromp](https://tromp.github.io/c4/Connect4.java); the oracle used above is Tromp's
  [8-ply database](https://tromp.github.io/c4/c4.html), redistributed in
  [bitbully-databases](https://markusthill.github.io/bitbully-databases/).

The verification and paired MTD(f) benchmark used for this post are implemented locally in
`tools/connect4/verify.py` and `tools/connect4/bench_paired.py`.

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
