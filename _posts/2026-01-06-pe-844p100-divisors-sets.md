---
layout: post
title: "Summing Non-Isolated Divisors Across All Subsets"
modified:
categories: [programming,math]
description: "A step-by-step combinatorial derivation of an efficient algorithm to compute S(n): the total sum of subset elements that divide another element in the same subset, with fast modular support."
tags: [combinatorics, number-theory, divisibility, powerset, optimization, python]
thumbnail: assets/img/2026-01-06-math-thumbnail.png
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-01-06T10:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
images:
  compare: false
  slider: false
---

<br>
## Problem Description

Take the numbers from $$1$$ up to some number $$n$$ and consider **all possible subsets**
of these numbers.

Inside any chosen subset, some numbers may be *isolated* while others are *connected*
to the rest of the set by divisibility:

- A number is **isolated** if it does **not** divide any other *different* number in the subset.
- A number is **non-isolated** if it divides at least one other element of the same subset.

For each subset, we add up all **non-isolated** numbers.  
Finally, we sum these values over **all** subsets of $$\{1,2,\dots,n\}$$.

Our task is to compute the same quantity for a very large value of $$n$$ (e.g., $$10^{12}$$), and report the
answer modulo a given number.

<br>
### Examples

- Subset $$A=\{2,3\}$$  
  Neither number divides the other, so both are isolated.  
  Contribution: $$0$$

- Subset $$A=\{2,4\}$$  
  The number $$2$$ divides $$4$$, so $$2$$ is non-isolated.  
  The number $$4$$ does not divide any other element.  
  Contribution: $$2$$

- Subset $$A=\{1,3,6\}$$  
  The number $$1$$ divides both $$3$$ and $$6$$.  
  The number $$3$$ divides $$6$$.  
  All except $$6$$ are non-isolated.  
  Contribution: $$1 + 3 = 4$$

- Subset $$A=\{5\}$$  
  A single element cannot divide another *distinct* element.  
  Contribution: $$0$$

<br>
### More Formal Problem Description

Let $$A$$ be a finite subset of the positive integers.

An element $$x \in A$$ is included in the sum for $$A$$ if there exists another element
$$y \in A$$ with $$y \neq x$$ such that
$$
x \mid y.
$$

Define the function

$$
f(A) = \sum_{\substack{x \in A \\ \exists\, y \in A,\; y \neq x,\; x \mid y}} x,
$$

that is, the sum of all elements of $$A$$ that divide at least one other element of $$A$$.

For a positive integer $$n$$, define

$$
S(n) = \sum_{A \subseteq \{1,2,\dots,n\}} f(A),
$$

where the sum ranges over all subsets of $$\{1,2,\dots,n\}$$.

---

<br>
## A Straightforward Baseline Solution

The code below implements a straight-forward, brute-force solution that follows the problem definition literally: it explicitly enumerates all subsets of $$\{1,\dots,n\}$$, checks within each subset which elements divide at least one other element, sums those elements, and finally aggregates the result over all subsets. While this approach is easy to understand and closely mirrors the mathematical definition of $$S(n)$$, it quickly becomes infeasible, as we will see below.


```python
from __future__ import annotations

from itertools import combinations


def powerset(A: set[int]) -> list[set[int]]:
    """Return all subsets of A with size >= 2 (since size 0/1 cannot contribute)."""
    items = list(A)
    return [set(c) for r in range(2, len(items) + 1) for c in combinations(items, r)]


def f(A: set[int]) -> int:
    """Sum of all x in A that divide at least one other (distinct) element of A."""
    total = 0
    for x in A:
        if any((y % x == 0) for y in A - {x}):
            total += x
    return total


def S(n: int) -> int:
    """Naively compute S(n) by enumerating all subsets of {1, ..., n}."""
    universe = set(range(1, n + 1))
    return sum(f(A) for A in powerset(universe))


n = 11
result = S(n)

print("Solution:", result)
assert result == 9855  # expected answer
```

**What this code does**

The goal is to compute $$S(n)$$, defined as follows:

1. Consider **all subsets** $$A \subseteq \{1,2,\dots,n\}$$.
2. For each subset $$A$$, compute $$f(A)$$:
   - For every $$x \in A$$, check whether there exists a *different* element $$y \in A$$ such that $$x \mid y$$.
   - If such a $$y$$ exists, then $$x$$ is counted **once** (even if it divides multiple elements).
   - Sum all counted $$x$$ values to obtain $$f(A)$$.
3. Sum $$f(A)$$ over all subsets $$A$$ to get $$S(n)$$.

**How the functions map to this definition**

- `powerset(A)`  
  Generates all subsets of `A` with size at least 2.  
  (Subsets of size 0 or 1 cannot contribute to $$f(A)$$, because there is no *distinct* second element to be divisible by.)

- `f(A)`  
  Implements the rule “sum all elements that divide at least one other distinct element in the subset”.
  The line
  ```python
  any((y % x == 0) for y in A - {x})
  ```
  checks whether  $$x$$ divides at least one other element $$y$$ in the subset.

- `S(n)`
  Builds the universe set  
  $$\{1, \dots, n\}$$, enumerates all relevant subsets, applies $$f$$ to each, and sums the results.

The snippet runs this for $$n = 11$$ and verifies the known value $$S(11) = 9855$$.

<br>
### The above Code is slow
However, this becomes infeasible quickly. Here is why:

1. The number of subsets explodes exponentially.
  The set  $$\{1,2,\dots,n\}$$ has $$2^n$$ subsets in total. **TODO: Explain why...**
  Even though the code skips subsets of size 0 and 1, the count is still essentially $$2^n - (n + 1),$$ which is still exponential growth.
  Concrete sizes:
  - $$n = 20 \Rightarrow 2^{20} = 1{,}048{,}576$$ subsets (about one million)
  - $$n = 30 \Rightarrow 2^{30} \approx 1.07 \cdot 10^9$$ subsets (about a billion)
  - $$n = 40 \Rightarrow 2^{40} \approx 1.10 \cdot 10^{12}$$ subsets (a trillion)
  So just looping over all subsets becomes impossible very quickly.

2. Each subset also has internal work.
  For each subset $$A$$, the function $$f(A)$$ performs nested checks:
  - It loops over each $$x \in A$$.
  - For each $$x$$, it scans the other elements $$A \setminus \{x\}$$ until it finds a multiple.
  In the worst case (when few divisibility relations exist), this is roughly quadratic in the subset size: $$\text{work per subset} \sim O(|A|^2).$$
  So the total runtime behaves roughly like: 
  $$
  \sum_{A \subseteq \{1,\dots,n\}} O(|A|^2),
  $$
  which is exponential overall, with a large constant factor coming from the inner checks.


3. Memory usage can also become a bottleneck.
  The function `powerset(...)` returns a full `list[set[int]]` of *all* subsets at once.  
  This means the program stores every subset in memory before it even starts summing.
  For moderately large $$n$$, this alone can exhaust available RAM, independent of runtime.

This code is a simple and functioning baseline, but it is fundamentally limited because it performs an exhaustive enumeration over roughly $$2^n$$ subsets and then does additional work inside each subset. That exponential growth is why values like $$S(20)$$ already become slow, and why computing $$S(10^{12})$$ requires a completely different, non-enumerative approach. 

In the  following, we will attempt to find an efficient approach, step-by-step.

---

<br>
## From Brute Force to a Combinatorial Viewpoint

The brute-force approach mirrors the definition of $$S(n)$$ directly, but its
exponential complexity makes it unsuitable for large values of $$n$$.
To make progress, we need to rethink *what* we are counting and *how* we count it.

This section takes a first step in that direction by changing perspective.
Instead of iterating over all subsets and computing their contributions one by one,
we begin to analyze the problem **element-wise**: we fix a single number $$x$$ and ask
how often it contributes across all subsets.
This shift lays the groundwork for a fully combinatorial formulation that avoids
explicit subset enumeration.

<br>
### Counting Contributions per Element (Still Brute Force)

```python
# Try different values of n and x to see how many subsets a single x contributes to
# for n=11 and x=3, expected: 768 subsets
n = 11
x = 3

universe = set(range(1, n + 1))
subsets = powerset(universe)

count_contributing_subsets = 0
for A in subsets:
    contributes = (x in A) and any((y != x) and (y % x == 0) for y in A)
    if contributes:
        count_contributing_subsets += 1

print(f"{x} contributes in {count_contributing_subsets} subsets of { {1,...,{n}} }. In total 2^n-(n+1)={len(subsets)} subsets.")
```
*Expected output:*
```text
3 contributes in 768 subsets of {1,...,11}. In total 2^n-(n+1)=2036 subsets.
```


**What this computation is counting**

The idea is to **fix a single value** $$x$$ and ask:

Among all subsets $$A \subseteq \{1,2,\dots,n\}$$, in how many of them does $$x$$ actually *contribute* to the overall sum $$S(n)$$?

An element $$x$$ contributes to a subset $$A$$ exactly when:

1. $$x \in A$$, and  
2. there exists some *other* element $$y \in A$$ with $$y \neq x$$ such that  
   $$
   x \mid y.
   $$

In words: the subset must contain $$x$$ **and** at least one *distinct multiple* of $$x$$.

**Why this is useful for a combinatorial approach**

The naive brute-force approach computes $$S(n)$$ by iterating over all subsets and
summing contributions inside each subset.

Here we flip the perspective:

- Instead of asking "what is the contribution of this subset?",  
- we ask "in how many subsets does this particular $$x$$ contribute?".

If we can count the number of subsets where $$x$$ contributes, then the total
contribution of $$x$$ to $$S(n)$$ is simply:

$$
x \cdot \#\{A \subseteq \{1,\dots,n\} : x \in A \text{ and } \exists\, y \in A,\ y \neq x,\ x \mid y\}.
$$

Summing this quantity over all $$x \in \{1,\dots,n\}$$ reconstructs $$S(n)$$, but in a way
that is much more amenable to mathematical counting arguments (and avoids enumerating
all subsets explicitly).

**About the "total number of subsets" mentioned**

The enumeration in this experiment typically ignores subsets of size 0 or 1, because such
subsets can never contain a pair of distinct elements where one divides the other.
So the total number of considered subsets is

$$
2^n - (n+1),
$$

i.e. all subsets minus the empty set and the $$n$$ singletons.

<br>
### Counting Contributing Subsets via Binomial Coefficients

Having identified how often a fixed element $$x$$ contributes across all subsets,
we now replace explicit subset enumeration by a counting argument based on
binomial coefficients.  
The code below implements this idea in a direct and still-naive form, preparing the
ground for a fully closed-form combinatorial solution.

```python
from __future__ import annotations


def factorial(n: int) -> int:
    """Compute n! for n >= 0 (naive iterative implementation)."""
    assert n >= 0
    fac = 1
    for i in range(1, n + 1):
        fac *= i
    return fac


def choose(n: int, k: int) -> int:
    """Compute the binomial coefficient 'n choose k' (naive implementation)."""
    assert 0 <= k <= n
    return factorial(n) // (factorial(n - k) * factorial(k))

n = 11
x = 3

# We want to count how many subsets A ⊆ {1,...,n} satisfy:
#   (1) x ∈ A, and
#   (2) there exists some y ∈ A with y ≠ x and x | y.
#
# In other words: A must contain x and at least one *distinct multiple* of x.

# Count the multiples of x in {1,...,n}, excluding x itself.
# Multiples of x are: x, 2x, 3x, ..., floor(n/x)*x.
# That is floor(n/x) many multiples total, and removing x leaves:
num_multiples_of_x_excluding_x = n // x - 1

# Partition the universe {1,...,n} into:
#   - the required element {x}
#   - the "good" elements: multiples of x (excluding x), from which we must pick ≥ 1
#   - the "free" elements: all remaining numbers (not equal to x and not a multiple of x),
#     from which we may pick any amount (including 0)
m = num_multiples_of_x_excluding_x               # "good" pool size
r = n - m - 1                                    # "free" pool size (everything else)

# Now count subsets by two independent choices:
#   - choose i >= 1 elements from the m "good" multiples (to ensure x divides something)
#   - choose j >= 0 elements from the r "free" elements (arbitrary)
#
# Each pair (i, j) yields: choose(m, i) * choose(r, j) subsets,
# and we always include x itself (so x ∈ A is guaranteed).
#
# This is still a brute-force sum over i and j, but it avoids enumerating subsets A.

# Sanity check targets for (n=11):
#   x=1 -> 1023
#   x=2 -> 960
#   x=3 -> 768
count_contributing_subsets = 0
for i in range(1, m + 1):            # must pick at least one multiple of x
    ways_pick_multiples = choose(m, i)
    for j in range(0, r + 1):        # may pick any number of remaining elements
        ways_pick_rest = choose(r, j)
        count_contributing_subsets += ways_pick_multiples * ways_pick_rest

print(f"{x} contributes in {count_contributing_subsets} subsets of { {1,...,{n}} }. In total 2^n-(n+1)={2**n-(n+1)} subsets.")
```

*Expected output:*
```text
3 contributes in 768 subsets of {1,...,11}. In total 2^n-(n+1)=2036 subsets.
```

This code counts, for fixed values of $$n$$ and $$x$$, how many subsets  $$A \subseteq \{1,\dots,n\}$$ satisfy the condition that **$$x$$ contributes** to the sum $$S(n)$$, without explicitly enumerating all subsets.

The helper functions

- `factorial(n)` computes $$n!$$,
- `choose(n, k)` computes the binomial coefficient $$ \binom{n}{k}, $$
  which counts the number of ways to choose $$k$$ elements from a set of size $$n$$.
  These are used as basic counting primitives.

A subset $$A$$ contributes for a given $$x$$ if and only if:

1. $$x \in A$$, and
2. $$A$$ contains at least one *distinct multiple* of $$x$$.

To exploit this structure, the set $$\{1,\dots,n\}$$ is partitioned into three disjoint parts:

- the fixed element $$\{x\}$$, which must always be included,
- the set of *multiples of* $$x$$ greater than $$x$$ itself,
- all remaining elements, which are neither equal to $$x$$ nor divisible by $$x$$.

If there are $$m$$ multiples of $$x$$ larger than $$x$$ and $$r$$ remaining elements, then
every contributing subset is uniquely determined by:
- choosing at least one element from the $$m$$ multiples, and
- choosing any number of elements from the $$r$$ remaining elements.

For a fixed choice of:
- $$i \ge 1$$ multiples of $$x$$, and
- $$j \ge 0$$ remaining elements,

there are

$$
\binom{m}{i} \cdot \binom{r}{j}
$$

distinct subsets, and each of them automatically contains $$x$$.

The double loop over $$i$$ and $$j$$ sums these contributions, effectively counting all
subsets in which $$x$$ contributes, but without ever listing the subsets themselves.

This approach still performs explicit summation, but it has replaced subset enumeration
by pure combinatorial counting.
It demonstrates how the contribution of a single element $$x$$ can be expressed in terms
of binomial coefficients, a small step toward deriving a closed-form expression for
$$S(n)$$.

<br>
### Element-Wise Computation of $$S(n)$$ via Combinatorial Counting

Building on the contribution-counting idea for a fixed element $$x$$, the following
implementation assembles the full value of $$S(n)$$ by summing the weighted
contributions of all $$x \in \{1,\dots,n\}$$.
While still computationally naive, it avoids explicit subset enumeration and makes
the underlying combinatorial structure of the problem explicit.

```python
from __future__ import annotations


def S(n: int) -> int:
    """Compute S(n) via element-wise combinatorial counting (still naive)."""
    total = 0

    for x in range(1, n + 1):
        # Number of multiples of x in {1,...,n}, excluding x itself
        m = n // x - 1

        # Number of remaining elements (neither x nor a multiple of x)
        r = n - m - 1

        # Count how many subsets A ⊆ {1,...,n} make x contribute
        count_contributing_subsets = 0

        # Choose at least one multiple of x
        for i in range(1, m + 1):
            ways_pick_multiples = choose(m, i)

            # Choose any number of remaining elements
            for j in range(0, r + 1):
                ways_pick_rest = choose(r, j)
                count_contributing_subsets += ways_pick_multiples * ways_pick_rest

        # Each such subset contributes x exactly once
        total += x * count_contributing_subsets

    return total

n = 11
S(n) # should be 9855
```
*Expected output:*
```text
9855
```

This function computes $$S(n)$$ by summing the contributions of each individual
element $$x \in \{1,\dots,n\}$$ separately, rather than iterating over all subsets.

For a fixed value of $$x$$, the code counts how many subsets $$A \subseteq \{1,\dots,n\}$$ satisfy the condition that $$x$$ contributes, i.e. that $$A$$ contains $$x$$ and at least one other element divisible by $$x$$. This is done by partitioning the universe into multiples of $$x$$ and all remaining elements, and then counting valid subsets using binomial coefficients.

Once the number of contributing subsets for $$x$$ has been determined, it is multiplied by $$x$$ itself, since each such subset contributes exactly $$x$$ to the overall sum. Summing this quantity over all $$x$$ reconstructs $$S(n)$$.

With this element-wise counting approach, we can already evaluate $$S(n)$$ for
moderately larger values of $$n$$ than before. For example, we can compute $$S(20):$$
```python
S(20)
```
*Expected output:*
```text
18626559
```

And even $$S(200)$$:
```python
S(200)
```
*Expected output:*
```text
2664683200606651329234017512985870589238327005040580368858611711
```

These results confirm the correctness of the combinatorial reformulation and
demonstrate a significant improvement over the original subset enumeration (try it yourself for different small values of $$n$$ and compare with our initial naive solution).

Nevertheless, the implementation still performs explicit summations for each $$x \in \{1,\dots,n\}$$ and relies on repeated evaluations of binomial coefficients. As a result, the runtime grows too quickly, and the method becomes impractical for large values of $$n$$—in particular for the target value $$n = 10^{14}$$.
A further simplification to closed-form expressions is therefore required.

---

<br>
## Step-by-Step Combinatorial Simplifications
### First Simplification: Collapsing the Inner Sum

As a first optimization, we focus on the innermost loop of the combinatorial
expression.
By recognizing that the sum over all binomial coefficients corresponding to the "free" elements does not depend on how many multiples of $$x$$ are chosen, this inner summation can be factored out and simplified. This reduces redundant computation and reveals a familiar combinatorial pattern that will be exploited further in the next steps.

```python
from __future__ import annotations


def S(n: int) -> int:
    """Compute S(n) via element-wise combinatorial counting (inner sum simplified)."""
    total = 0

    for x in range(1, n + 1):
        # m = number of multiples of x in {1,...,n}, excluding x itself
        m = n // x - 1

        # r = number of remaining elements (neither x nor a multiple of x)
        r = n - m - 1

        # Precompute the inner sum over j (still written as a sum here).
        # This counts all ways to choose any subset of the r "free" elements.
        sum_over_rest = sum(choose(r, j) for j in range(0, r + 1))

        count_contributing_subsets = 0
        for i in range(1, m + 1):  # must pick at least one multiple of x
            ways_pick_multiples = choose(m, i)
            count_contributing_subsets += ways_pick_multiples * sum_over_rest

        # Each contributing subset adds x exactly once
        total += x * count_contributing_subsets

    return total

assert S(11) == 9855
assert S(20) == 18626559
assert S(200) == 2664683200606651329234017512985870589238327005040580368858611711
```

<br>
### Second Simplification: Replacing the Inner Binomial Sum by a Power of Two

The inner sum over the "free" elements counts all ways to choose an arbitrary subset from a pool of size $$r$$. In combinatorial terms, this is exactly the size of a power set:

$$
\sum_{j=0}^{r} \binom{r}{j} = 2^{r}.
$$

Using the notation from above, we have:
- $$m = \left\lfloor \frac{n}{x} \right\rfloor - 1$$ (multiples of $$x$$ larger than $$x$$),
- $$r = n - m - 1$$ (all remaining “free” elements).

The inner sum runs over all possible choices of elements from the $$r$$ "free" elements.
For each fixed $$j$$, the binomial coefficient $$\binom{r}{j}$$ counts the number of subsets of size exactly $$j$$.
Summing over all values of $$j$$ therefore counts **all subsets** of a set with $$r$$ elements.

Equivalently, each of the $$r$$ elements can be either included or excluded independently, giving $$2 \cdot 2 \cdots 2 = 2^{r}$$ possible subsets.

Another intuitive way to see this identity is through a binary encoding: Consider the $$r$$ "free" elements and fix an ordering of them.
Any subset of these elements can be represented by a binary string of length $$r$$:
the $$k$$-th bit is set to $$1$$ if the $$k$$-th element is included in the subset, and set to $$0$$ otherwise.
Each bit has two independent choices (on or off), so the total number of such binary strings is $$2 \cdot 2 \cdots 2 = 2^{r}.$$ This gives a one-to-one correspondence between subsets and binary strings of length $$r$$,
showing that there are exactly $$2^{r}$$ subsets.
Grouping these subsets by the number of bits set to $$1$$ recovers the binomial sum:
there are $$\binom{r}{j}$$ binary strings with exactly $$j$$ ones, and summing over
$$j = 0,\dots,r$$ yields

$$
\sum_{j=0}^{r} \binom{r}{j} = 2^{r}.
$$

which in code becomes a single exponentiation. This removes an entire loop and makes the structure of the count much clearer: for each valid choice of at least one multiple of $$x$$, the remaining elements can be included or excluded independently, giving $$2^{r}$$ possibilities.

```python
from __future__ import annotations


def S(n: int) -> int:
    """Compute S(n) via element-wise combinatorial counting (inner sum = power of 2)."""
    total = 0

    for x in range(1, n + 1):
        # m = number of multiples of x in {1,...,n}, excluding x itself
        m = n // x - 1

        # r = number of remaining elements (neither x nor a multiple of x)
        r = n - m - 1

        # All subsets of the r "free" elements: sum_{j=0}^r C(r,j) = 2^r
        sum_over_rest = 2**r

        count_contributing_subsets = 0
        for i in range(1, m + 1):  # must pick at least one multiple of x
            ways_pick_multiples = choose(m, i)
            count_contributing_subsets += ways_pick_multiples * sum_over_rest

        # Each contributing subset adds x exactly once
        total += x * count_contributing_subsets

    return total


assert S(11) == 9855
assert S(20) == 18626559
assert S(200) == 2664683200606651329234017512985870589238327005040580368858611711
```

<br>
### Third Simplification: Factoring the Independent Choices

In this step, we make the independence of the two combinatorial choices explicit.
The selection of multiples of $$x$$ and the selection of the remaining elements are handled separately: we first sum over all nonempty choices of multiples of $$x$$, and only then multiply once by the number of possible choices for the remaining elements.
This removes another unnecessary dependency inside the loop and brings the expression closer to a closed-form count.

```python
from __future__ import annotations


def S(n: int) -> int:
    """Compute S(n) via element-wise combinatorial counting (factor out 2^r).

    Improvement vs. the previous version:
      - We no longer multiply by 2^r inside the i-loop.
      - Instead, we first compute the i-sum: sum_{i=1..m} C(m,i),
        and only then multiply once by 2^r.
    """
    total = 0

    for x in range(1, n + 1):
        # m = number of multiples of x in {1,...,n}, excluding x itself
        m = n // x - 1

        # r = number of remaining elements (neither x nor a multiple of x)
        r = n - m - 1

        # Count ways to pick at least one element from the m "good" multiples:
        #   sum_{i=1..m} C(m, i)
        count_nonempty_multiple_choices = 0
        for i in range(1, m + 1):
            count_nonempty_multiple_choices += choose(m, i)

        # Independent choices for the r "free" elements:
        #   sum_{j=0..r} C(r, j) = 2^r
        count_free_choices = 2**r

        # Each valid subset contributes x exactly once
        total += x * count_nonempty_multiple_choices * count_free_choices

    return total


assert S(11) == 9855
assert S(20) == 18626559
assert S(200) == 2664683200606651329234017512985870589238327005040580368858611711
```

<br>
### Fourth Simplification: Eliminating the Final Inner Sum

At this stage, both remaining summations can be replaced by closed-form expressions.
The number of ways to select at least one multiple of $$x$$ becomes $$2^{m}-1$$, while the number of ways to select any subset of the remaining elements is $$2^{r}$$. This removes all inner loops and yields a compact formula for the contribution of each $$x$$, bringing the computation of $$S(n)$$ close to its final combinatorial form.


```python
from __future__ import annotations


def S(n: int) -> int:
    """Compute S(n) via element-wise combinatorial counting (closed form for both sums).

    Improvement vs. the previous version:
      - The sum over i = 1..m of C(m, i) is replaced by its closed form 2^m - 1.
      - Together with the already simplified factor 2^r, this removes the inner loop
        entirely.
    """
    total = 0

    for x in range(1, n + 1):
        # m = number of multiples of x in {1,...,n}, excluding x itself
        m = n // x - 1

        # r = number of remaining elements (neither x nor a multiple of x)
        r = n - m - 1

        # Number of nonempty choices of multiples of x:
        #   sum_{i=1..m} C(m, i) = 2^m - 1
        count_nonempty_multiple_choices = 2**m - 1

        # Number of choices for the remaining "free" elements:
        #   sum_{j=0..r} C(r, j) = 2^r
        count_free_choices = 2**r

        # Each valid subset contributes x exactly once
        total += x * count_nonempty_multiple_choices * count_free_choices

    return total


assert S(11) == 9855
assert S(20) == 18626559
assert S(200) == 2664683200606651329234017512985870589238327005040580368858611711
```

<br>
### Fifth Simplification: Collapsing the Expression into a Single Power Difference

In this final simplification step, the remaining combinatorial factors are combined
algebraically. The product $$(2^{m} - 1)\cdot 2^{r}$$ is rewritten as a difference of two powers of two, yielding a compact expression for the number of subsets in which a given element $$x$$ contributes.
As a result, the contribution of each $$x$$ can now be computed in constant time, leaving only a single loop over $$x \in \{1,\dots,n\}$$. 

```python
from __future__ import annotations


def S(n: int) -> int:
    """Compute S(n) via a closed-form contribution per element x."""
    total = 0

    for x in range(1, n + 1):
        # m = number of multiples of x in {1,...,n}, excluding x itself
        m = n // x - 1

        # Using:
        #   (2^m - 1) * 2^r
        # with r = n - m - 1,
        # this simplifies algebraically to:
        #   2^(n-1) - 2^r
        contribution_count = 2**(n - 1) - 2**(n - m - 1)

        # Each such subset contributes x exactly once
        total += x * contribution_count

    return total

assert S(11) == 9855
assert S(20) == 18626559
assert S(200) == 2664683200606651329234017512985870589238327005040580368858611711
```

<br>
### Sixth Simplification: Reusing the Global Power Term

In this step, we observe that the term $$2^{\,n-1}$$ is independent of $$x$$ and can be computed once and reused for all iterations. Only the subtraction term $$2^{\,n-m-1}$$ depends on $$x$$ through the number of
multiples of $$x$$.

This change does not alter the mathematical structure of the formula, but it removes redundant recomputation and clarifies the separation between the global contribution shared by all elements and the correction term specific to each $$x$$. The result is a cleaner and slightly more efficient implementation of the final closed-form expression for $$S(n)$$.

```python
from __future__ import annotations


def S(n: int) -> int:
    """Compute S(n) using a shared power-of-two term."""
    total = 0

    # This term does not depend on x and can be reused
    base_power = 2**(n - 1)

    for x in range(1, n + 1):
        # m = number of multiples of x in {1,...,n}, excluding x itself
        m = n // x - 1

        # Contribution count for x:
        #   2^(n-1) - 2^(n-m-1)
        contribution_count = base_power - 2**(n - m - 1)

        # Each such subset contributes x exactly once
        total += x * contribution_count

    return total
```

---

<br>
## Grouping Values of $$x$$ by Constant Quotients

In the previous formula, the contribution of each element $$x$$ depends on the value  

$$
m = \left\lfloor \frac{n}{x} \right\rfloor - 1,
$$

rather than on $$x$$ itself.
A closer inspection reveals that this quantity remains constant over large contiguous
ranges of $$x$$. The following code illustrates this phenomenon by grouping values of $$x$$ according to the same value of $$m$$. Making this structure explicit is the key to the next optimization step, where we replace the loop over individual $$x$$ by a loop over ranges with identical combinatorial behavior.

```python
from __future__ import annotations

n = 100
q = 50  # number of x-values per printed row

total = 0
base_power = 2**(n - 1)

current_m = None
row = []

for x in range(1, n + 1):
    # m = number of multiples of x in {1,...,n}, excluding x itself
    m = n // x - 1

    contribution_count = base_power - 2**(n - m - 1)
    total += x * contribution_count

    # Collect (x, m) pairs for printing
    if current_m is None:
        current_m = m

    if m != current_m or len(row) == q:
        print(f"m = {current_m}: ", row)
        row = []
        current_m = m

    row.append(x)

# print remaining row
if row:
    print(f"m = {current_m}: ", row)

```
*Output*:
```text
m = 99:  [1]
m = 49:  [2]
m = 32:  [3]
m = 24:  [4]
m = 19:  [5]
m = 15:  [6]
m = 13:  [7]
m = 11:  [8]
m = 10:  [9]
m = 9:  [10]
m = 8:  [11]
m = 7:  [12]
m = 6:  [13, 14]
m = 5:  [15, 16]
m = 4:  [17, 18, 19, 20]
m = 3:  [21, 22, 23, 24, 25]
m = 2:  [26, 27, 28, 29, 30, 31, 32, 33]
m = 1:  [34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
m = 0:  [51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]
```

This output groups values of $$x$$ by the value of

$$
m = \left\lfloor \frac{n}{x} \right\rfloor - 1
$$

for $$n = 100$$. For small values of $$x$$, the quotient $$\left\lfloor \frac{n}{x} \right\rfloor$$ changes rapidly, so each value of $$x$$ tends to produce a distinct value of $$m$$. As $$x$$ increases, the quotient varies more slowly, and the same value of $$m$$ applies to increasingly large ranges of $$x$$.

This is why the early groups contain only one element (for example, $$x = 1$$ gives $$m = 99$$), while later groups grow wider and wider. In particular, once $$x > \frac{n}{2}$$, we have $$\left\lfloor \frac{n}{x} \right\rfloor = 1$$, so $$m = 0$$ and all remaining values of $$x$$ fall into a single large group.

This behavior reflects a general property of integer division and is the reason why the final summation over $$x$$ can be optimized by iterating over ranges with constant $$m$$ rather than over individual values of $$x$$.

Below you find a small helper snippet that makes the structure behind the quantity $$m = \left\lfloor \frac{n}{x} \right\rfloor - 1$$ explicit.

```python
# Explore ranges of x for which
#     m = floor(n / x) - 1
# is constant.

n = 100

# Fix a value of m
m = 2

# We want all x such that:
#     floor(n / x) - 1 = m
# ⇔  floor(n / x) = m + 1
#
# This inequality is equivalent to:
#     m + 1 ≤ n / x < m + 2
#
# Solving for x gives:
#     n / (m + 2) < x ≤ n / (m + 1)

left = n // (m + 2) + 1   # smallest integer x satisfying n/x < m+2
right = n // (m + 1)     # largest integer x satisfying n/x ≥ m+1

x_range = range(left, right + 1)
x_range # should match the result obtained above
```
*Output*:
```test
range(26, 34) 
```

By fixing a value of $$m$$ and solving the corresponding inequality for $$x$$, we can explicitly determine all values of $$x$$ for which the combinatorial contribution depends on the same parameter $$m$$.
The resulting interval shows that many consecutive values of $$x$$ share identical behavior, especially for larger $$x$$.

This observation is crucial for a further optimization: instead of summing contributions for each $$x$$ individually, we can group values of $$x$$ with the same $$m$$ and handle their total contribution in one step.

<br>
### Summing Contributions over Ranges of $$x$$

Having identified that the quantity  

$$
m = \left\lfloor \frac{n}{x} \right\rfloor - 1
$$

remains constant over contiguous intervals of $$x$$, we can now exploit this structure directly in the computation of $$S(n)$$.
Instead of iterating over each value of $$x$$ individually, the following code groups together all $$x$$ sharing the same $$m$$ and accumulates their contributions in bulk. This marks a decisive shift from element-wise summation to interval-wise aggregation.

```python
from __future__ import annotations


def S(n: int) -> int:
    """Compute S(n) by grouping x-values with the same m = n//x - 1 (range batching).

    Conceptually unchanged vs. the previous closed-form version:
      - We still use that each x contributes: x * (2^(n-1) - 2^(n-m-1)).
      - The only change in viewpoint is that we do not iterate over every x in 1..n.
        Instead, we iterate over values of m and add the contributions of *ranges* of x
        where m is constant.

    Note:
      - This is still not fully optimized: the summation sum(range(...)) is a bit slow
        and will be replaced later by an O(1) arithmetic-series formula.
    """
    total = 0
    base_power = 2 ** (n - 1)

    # -------------------------------------------------------------------------
    # Phase 1: Iterate over possible m-values and find intervals [x_left, x_right]
    # such that for all x in that interval:
    #     m = floor(n / x) - 1
    #
    # Solving floor(n/x) = m+1 gives:
    #     n/(m+2) < x <= n/(m+1)
    # Hence:
    #     x_left  = floor(n/(m+2)) + 1
    #     x_right = floor(n/(m+1))
    # -------------------------------------------------------------------------
    last_left = 1
    last_right = 1

    for m in range(0, n):
        x_left = n // (m + 2) + 1
        x_right = n // (m + 1)

        # Once the interval collapses to a single x, we stop the batching phase
        # and handle the remaining small x-values individually.
        if x_left == x_right:
            last_left = x_left
            last_right = x_right
            break

        # For this entire interval, m is constant, so the contribution factor is constant.
        contribution_count = base_power - 2 ** (n - m - 1)

        # Sum contributions over all x in [x_left, x_right]:
        #   sum_{x=x_left..x_right} x * contribution_count
        # = (sum of x over the interval) * contribution_count
        #
        # Still computed "naively" as in your snippet (we'll optimize this later).
        total += sum(range(x_left, x_right + 1)) * contribution_count

    # -------------------------------------------------------------------------
    # Phase 2: Handle the remaining x-values individually.
    #
    # The batching above stops when x_left == x_right, i.e. the next interval has
    # length 1. From that point downward, intervals are tiny, so we just compute
    # x * factor directly for x = x_left, x_left-1, ..., 1.
    # -------------------------------------------------------------------------
    assert last_left == last_right
    for x in range(last_left, 0, -1):
        m = n // x - 1
        contribution_count = base_power - 2 ** (n - m - 1)
        total += x * contribution_count

    return total

assert S(11) == 9855
assert S(20) == 18626559
assert S(200) == 2664683200606651329234017512985870589238327005040580368858611711
assert S(2000) % 1234567891234567891234567891 == 156208504659765295659151493
assert S(2*10**5) % 1234567891234567891234567891 == 617453040502786108363224072
```

Note that we can now also compute $$S(2000)$$ or $$S(2 \cdot 10^5)$$ in feasible time. However, larger values of $$n$$ are still hard for our approach.

<br>
### Replacing Interval Summation by a Closed-Form Formula

In this optimization step, we eliminate the remaining inner summation over intervals of $$x$$ by using the closed-form formula for an arithmetic series.
Once values of $$x$$ are grouped by a constant value of

$$
m = \left\lfloor \frac{n}{x} \right\rfloor - 1,
$$

their total contribution can be computed in constant time.
This removes all residual linear work inside the main loop and yields an efficient, fully combinatorial implementation of $$S(n)$$.

```python
from __future__ import annotations


def S(n: int) -> int:
    """Compute S(n) using range batching + O(1) arithmetic-series interval sums.

    We use the closed-form per-element contribution:
        x * (2^(n-1) - 2^(n-m-1)),
    where
        m = n//x - 1
    is constant over contiguous ranges of x.

    Compared to the previous batching version:
      - we compute powers via pow(2, k),
      - and replace sum(range(x_left, x_right+1)) by the O(1) interval sum formula.
    """
    total = 0
    base_power = pow(2, n - 1)

    # Phase 1: iterate over m-values and aggregate whole x-intervals at once
    stop_x = 1
    for m in range(0, n):
        # Interval of x where floor(n/x) - 1 == m:
        #   n/(m+2) < x <= n/(m+1)
        x_left = n // (m + 2) + 1
        x_right = n // (m + 1)

        if x_left == x_right:
            stop_x = x_left
            break

        # Constant factor for all x in this interval (depends only on m)
        contribution_count = base_power - pow(2, n - m - 1)

        # Sum_{x=x_left..x_right} x  (arithmetic series, computed in O(1))
        sum_x_interval = (x_left + x_right) * (x_right - x_left + 1) // 2

        total += sum_x_interval * contribution_count

    # Phase 2: handle the remaining small x-values individually
    for x in range(stop_x, 0, -1):
        m = n // x - 1
        contribution_count = base_power - pow(2, n - m - 1)
        total += x * contribution_count

    return total

assert S(11) == 9855
assert S(20) == 18626559
assert S(200) == 2664683200606651329234017512985870589238327005040580368858611711
assert S(2000) % 1234567891234567891234567891 == 156208504659765295659151493
assert S(2*10**5) % 1234567891234567891234567891 == 617453040502786108363224072
```

<br>
### Optimized Implementation with Optional Modulus

We now arrive at a optimized version of the algorithm that combines all previous
combinatorial insights.
By batching values of $$x$$ with identical $$m = \left\lfloor \frac{n}{x} \right\rfloor - 1,$$ using closed-form arithmetic-series sums, and supporting fast modular exponentiation, the computation of $$S(n)$$ becomes feasible even for very large values of $$n$$.

This implementation allows the use of an optional modulus to keep intermediate values
manageable. When a modulus is provided, all arithmetic is performed modulo that value; otherwise, the exact (and potentially enormous) integer result is computed. The remaining runtime depends mainly on the number of distinct values of $$m$$, which grows on the order of $$O(\sqrt{n})$$, making this approach scalable to inputs far beyond what brute-force methods could handle.

```python
from __future__ import annotations


def S(n: int, modulus: int | None = None) -> int:
    """Compute S(n) using range batching and closed-form interval sums.

    This version supports an optional modulus:
      - If `modulus` is None, all computations are done with exact integers.
      - If `modulus` is given, all arithmetic is performed modulo `modulus`.

    Core idea (unchanged):
      - Each x contributes: x * (2^(n-1) - 2^(n-m-1)),
        where m = n//x - 1.
      - Values of x are grouped into intervals where m is constant.
      - Contributions over each interval are summed using the arithmetic series formula.
    """
    total = 0

    # Precompute the global power term (modular or exact)
    if modulus is None:
        base_power = pow(2, n - 1)
    else:
        base_power = pow(2, n - 1, modulus)

    # ------------------------------------------------------------------
    # Phase 1: batch ranges of x where m = floor(n/x) - 1 is constant
    # ------------------------------------------------------------------
    stop_x = 1
    for m in range(0, n):
        # All x satisfying floor(n/x) - 1 = m lie in:
        #   n/(m+2) < x <= n/(m+1)
        x_left = n // (m + 2) + 1
        x_right = n // (m + 1)

        if x_left == x_right:
            stop_x = x_left
            break

        # Contribution factor for this whole interval
        if modulus is None:
            contribution_count = base_power - pow(2, n - m - 1)
        else:
            contribution_count = base_power - pow(2, n - m - 1, modulus)
            contribution_count %= modulus

        # Sum of x over the interval [x_left, x_right]
        interval_sum = (x_left + x_right) * (x_right - x_left + 1) // 2
        if modulus is not None:
            interval_sum %= modulus

        total += interval_sum * contribution_count
        if modulus is not None:
            total %= modulus

    # ------------------------------------------------------------------
    # Phase 2: handle the remaining small x-values individually
    # ------------------------------------------------------------------
    for x in range(stop_x, 0, -1):
        m = n // x - 1

        if modulus is None:
            contribution_count = base_power - pow(2, n - m - 1)
            total += x * contribution_count
        else:
            contribution_count = base_power - pow(2, n - m - 1, modulus)
            total += x * contribution_count
            total %= modulus

    return total

assert S(11) == 9855
assert S(20) == 18626559
assert S(200) == 2664683200606651329234017512985870589238327005040580368858611711
assert S(2000, 1234567891234567891234567891) == 156208504659765295659151493
assert S(2*10**5, 1234567891234567891234567891) == 617453040502786108363224072
assert S(2*10**10, 1234567891234567891234567891) == 481424271854145029777746921
```

Now, also solutions for $$S(2 \cdot 10^{10})$$ can be computed without problems (considering a modulus which is sufficiently small). Computing $$S(10^{14}, 1234567891)$$ still needs around 2-3 minutes.