---
layout: post
title: "On a Curious Prefix-Sum Problem"
modified:
categories: [programming, algorithms, mathematics]
description: "A deceptively simple recurrence leads to an unexpected challenge when computing its prefix sums. Solving it efficiently requires looking at the problem from a different angle."
tags: [recurrence-relations, prefix-sums, discrete-math, algorithms, optimization, python]
thumbnail: assets/img/2026-01-10-math-thumbnail.png
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-01-10T15:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
images:
  compare: false
  slider: false
---

<br>
## Problem Description

You are given a sequence of numbers defined by a simple-looking recurrence.

The sequence starts with a single initial value $$a_1$$.  Three fixed constants $$q$$, $$r$$, and $$t$$ determine how all further values are generated.

For every integer $$n \ge 1$$, the sequence is defined by

$$
\begin{aligned}
a_{2n}   &= q\,a_n, \\
a_{2n+1} &= r\,a_n + t\,a_{n+1},
\end{aligned}
$$

where:

- $$a_n$$ denotes the value of the sequence at position $$n$$,
- $$q$$ controls how values at even indices are produced,
- $$r$$ and $$t$$ control how values at odd indices depend on earlier terms.

From this sequence, define the **prefix sum**

$$
S(N) = a_1 + a_2 + a_3 + \dots + a_N,
$$

which represents the sum of the first $$N$$ sequence values.

For small values of $$N$$, computing $$S(N)$$ is straightforward: one can generate the sequence term by term and keep a running sum.

Now comes the riddle:

> Suppose $$N$$ is so large that iterating from $$1$$ to $$N$$ is completely
> infeasible—think of values like $$10^{12}$$, $$10^{15}$$, or even larger.  
>  
> Is it still possible to compute the exact value of $$S(N)$$, and if so, how?

At first glance, the task seems impossible: the definition of $$S(N)$$ involves
$$N$$ terms, and $$N$$ may be astronomically large.

The challenge is to uncover a hidden structure in the recurrence that makes this computation feasible without ever touching most of the terms involved.

Before diving into the solution, here is a brief roadmap of how we will approach the problem:

1. We first analyze the recurrence algebraically and derive closed relations for the prefix sums.
2. These relations reveal a binary self-similarity that allows us to reduce large indices recursively.
3. We then translate this structure into an efficient $O(\log N)$ algorithm.
4. Finally, we implement the method in code, verify it against a naive solution, and demonstrate its power on enormous values of $N$.


<br>
## Formal Problem Statement

Let $(a_n)_{n\ge 1}$ be a sequence defined by constants
$$a_1,q,r,t \in \mathbb{R} \;(\text{or } \mathbb{Z})$$
and the recurrence
$$
\begin{aligned}
a_{2n}   &= q\,a_n, \\
a_{2n+1} &= r\,a_n + t\,a_{n+1},
\qquad (n \ge 1).
\end{aligned}
$$

Define the prefix sums
$$
S(n) := \sum_{k=1}^{n} a_k,
\qquad S(0):=0.
$$

> **Problem.** Compute $$S(N)$$ for a given $$N \ge 1$$.


Throughout this discussion, "exact" means exact arithmetic with respect to the chosen number system. In particular:

- If $a_1,q,r,t$ are integers, then all values of $a_n$ and $S(N)$ are integers,
  and the algorithm computes them exactly using arbitrary-precision arithmetic.
- If floating-point values are used instead, the algorithm still applies, but
  the result is subject to the usual floating-point rounding behavior.

<br>
## From the Recurrence to Prefix-Sum Relations

We now turn to the key analytical step: translating the defining recurrence of the sequence into corresponding recurrences for its prefix sums.

Throughout this section, let $(a_n)_{n\ge 1}$ be defined by the parity-dependent rules

$$
\begin{aligned}
a_{2n}   &= q\,a_n, \\
a_{2n+1} &= r\,a_n + t\,a_{n+1},
\end{aligned}
\qquad (n\ge 1),
$$

with a fixed initial value $$a_1$$.

Define the prefix sums, with the convention $$S(0):=0$$, by

$$
S(n) := \sum_{k=1}^{n} a_k.
$$

The central objective is to express $$S(2n)$$ and $$S(2n+1)$$ in terms of *smaller
indices*, involving only $$S(n)$$, $$S(n-1)$$, and a small amount of local sequence
information. This is precisely what will later allow an efficient algorithm.

---

<br>
## Deriving a Formula for $$S(2n)$$

Because the recurrence defining $(a_n)$ distinguishes between even and odd indices, it is natural to analyze the prefix sums by separating contributions from even and odd positions.

We begin directly from the definition:

$$
S(2n)
= \sum_{k=1}^{2n} a_k.
$$

Since the recurrence distinguishes between even and odd indices, it is natural to
split the sum accordingly:

$$
S(2n)
= \sum_{k=1}^{n} a_{2k}
\;+\;
\sum_{k=0}^{n-1} a_{2k+1}.
$$

<br>
### Even-index contribution

Using the recurrence $$a_{2k}=q\,a_k$$, the even part simplifies immediately:

$$
\sum_{k=1}^{n} a_{2k}
= \sum_{k=1}^{n} q\,a_k
= q \sum_{k=1}^{n} a_k
= q\,S(n).
$$

<br>
### Odd-index contribution

For the odd indices, first separate the base term:

$$
\sum_{k=0}^{n-1} a_{2k+1}
= a_1 + \sum_{k=1}^{n-1} a_{2k+1}.
$$

For $$k \ge 1$$, substitute the recurrence $$a_{2k+1}=r\,a_k+t\,a_{k+1}$$:

$$
\sum_{k=1}^{n-1} a_{2k+1}
= r\sum_{k=1}^{n-1} a_k
\;+\;
t\sum_{k=1}^{n-1} a_{k+1}.
$$

Both sums can be rewritten in terms of prefix sums:

$$
\sum_{k=1}^{n-1} a_k = S(n-1),
\qquad
\sum_{k=1}^{n-1} a_{k+1}
= \sum_{j=2}^{n} a_j
= S(n)-a_1.
$$

Combining these expressions gives

$$
\sum_{k=0}^{n-1} a_{2k+1}
= a_1 + rS(n-1) + t\bigl(S(n)-a_1\bigr)
= rS(n-1) + tS(n) + (1-t)a_1.
$$

<br>
### Combining both parts

Adding the even and odd contributions yields the closed recurrence

$$
S(2n)
= qS(n) + rS(n-1) + tS(n) + (1-t)a_1
= (q+t)S(n) + rS(n-1) + (1-t)a_1.
$$

Notably, $$S(2n)$$ depends only on prefix sums at smaller indices and a constant
term determined by $$a_1$$.

---

<br>
## Deriving a Formula for $$S(2n+1)$$

The odd case follows immediately from the definition:

$$
S(2n+1) = S(2n) + a_{2n+1}.
$$

Substituting the recurrence for $$a_{2n+1}$$ gives

$$
S(2n+1) = S(2n) + r\,a_n + t\,a_{n+1}.
$$

Inserting the expression for $$S(2n)$$ obtained above leads to

$$
S(2n+1)
= (q+t)S(n) + rS(n-1) + (1-t)a_1
\;+\;
r\,a_n + t\,a_{n+1}.
$$

---

<br>
## Summary of the Induced Prefix-Sum Recurrences

We have derived the following identities for all $$n \ge 1$$:

$$
\begin{aligned}
S(2n)   &= (q+t)\,S(n) + r\,S(n-1) + (1-t)\,a_1, \\
S(2n+1) &= (q+t)\,S(n) + r\,S(n-1) + (1-t)\,a_1
          \;+\;
          r\,a_n + t\,a_{n+1}.
\end{aligned}
$$

The key observation is the asymmetry between the two cases:

- The **even** prefix sum $$S(2n)$$ closes purely in terms of prefix sums.
- The **odd** prefix sum $$S(2n+1)$$ additionally depends on the local pair
  $$(a_n,a_{n+1})$$.

This structure is exactly what enables an efficient algorithm.

---

<br>
## A Binary-State Algorithm for Computing $$S(N)$$

The identities above suggest a strategy based on repeatedly halving the index.
Instead of summing $$N$$ terms, we process the binary representation of $$N$$ and
update a constant-size state at each step.



<br>
### State Representation

At any stage, we maintain the state

$$
\bigl(S(n-1),\; S(n),\; a_n,\; a_{n+1}\bigr),
$$

which contains precisely the information required to compute
$$S(2n),\; S(2n+1)$$ and the next sequence values.

The initial state corresponds to $$n=1$$:

$$
\bigl(S(0), S(1), a_1, a_2\bigr)
= \bigl(0,\; a_1,\; a_1,\; q\,a_1\bigr),
$$

since $$a_2=a_{2\cdot 1}=q\,a_1$$.



<br>
### Binary Decomposition of the Index

Write the target index $$N$$ in binary:

$$
N = (1 b_{k-1} b_{k-2} \dots b_0)_2.
$$

The leading $$1$$ initializes the state at $$n=1$$.
Each subsequent bit determines the transition:

- bit $$0$$ corresponds to $$n \mapsto 2n$$,
- bit $$1$$ corresponds to $$n \mapsto 2n+1$$.

Processing the bits from left to right repeatedly reduces the problem size by a
factor of two.



<br>
### Precomputation Step

From the current state, compute the quantities

$$
\begin{aligned}
S(2n)   &= (q+t)S(n) + rS(n-1) + (1-t)a_1, \\
S(2n+1) &= S(2n) + r\,a_n + t\,a_{n+1},
\end{aligned}
$$

as well as the sequence values

$$
\begin{aligned}
a_{2n}   &= q\,a_n, \\
a_{2n+1} &= r\,a_n + t\,a_{n+1}, \\
a_{2n+2} &= q\,a_{n+1}.
\end{aligned}
$$

All of these depend only on the current state and can be computed in constant time.



<br>
### Even Transition (bit $$0$$)

If the next bit is $$0$$, update $$n \mapsto 2n$$. The new state is

$$
\bigl(S(2n)-a_{2n},\; S(2n),\; a_{2n},\; a_{2n+1}\bigr),
$$
using the identity $$S(2n-1)=S(2n)-a_{2n}$$.



<br>
### Odd Transition (bit $$1$$)

If the next bit is $$1$$, update $$n \mapsto 2n+1$$. The new state is

$$
\bigl(S(2n),\; S(2n+1),\; a_{2n+1},\; a_{2n+2}\bigr).
$$



<br>
### Termination and Result

After all binary digits of $$N$$ have been processed, the maintained index equals
$$n=N$$. The desired prefix sum is therefore $$S(N)$$.

---

<br>
### Interpretation

The entire computation runs in $$O(\log N)$$ time.
Only a constant-size state is maintained, and each binary digit of $$N$$ triggers
a single constant-time update.

The apparent necessity of summing $$N$$ terms disappears once the binary
self-similarity of the recurrence is made explicit.

---

<br>
## From Theory to Code

### A Naive Reference Implementation

Before turning to the optimized algorithm, it is useful to establish a simple
baseline.

For small values of $$N$$, the most straightforward approach is to **explicitly
generate the sequence** using its defining recurrence and then compute the prefix
sums by a single pass over the resulting list. While this method runs in
$$O(N)$$ time and quickly becomes infeasible for large $$N$$, it has two important
roles:

- it makes the recurrence concrete and easy to experiment with, and  
- it serves as a reliable **reference implementation** for verifying the
  correctness of the optimized method later on.

The following code implements this direct approach.


```python
from __future__ import annotations

from typing import Sequence


def build_sequence_naive(N: int, a1: int, q: int, r: int, t: int) -> list[int]:
    """Build a[1..N+1] for the parity recurrence (naive O(N) reference).

    Recurrence:
        a_{2n}   = q * a_n
        a_{2n+1} = r * a_n + t * a_{n+1}

    We compute up to a_{N+1} so that the step for odd indices (2n+1) can safely
    reference a_{n+1} for all n needed.

    Args:
        N: Target maximum index (must satisfy N >= 1).
        a1: Initial value a_1.
        q, r, t: Recurrence constants.

    Returns:
        A list `a` of length N+2 using 1-based indexing:
            - a[0] is unused (kept as 0),
            - a[k] == a_k for k = 1..N+1.
    """
    if N < 1:
        raise ValueError("N must be >= 1")

    # 1-based array: keep index 0 unused for clarity.
    # We compute up to N+1 because the recurrence needs a_{n+1}.
    a = [0] * (N + 2)
    a[1] = a1

    # Fill values in increasing n. Each step writes a_{2n} and a_{2n+1}.
    # The upper bound ensures we don't write beyond N+1.
    for n in range(1, (N + 1) // 2 + 1):
        a[2 * n] = q * a[n]
        a[2 * n + 1] = r * a[n] + t * a[n + 1]

    return a


def prefix_sums_naive(a: Sequence[int]) -> list[int]:
    """Compute prefix sums S(k) = sum_{i=1}^k a_i from a 1-based sequence.

    Args:
        a: 1-based sequence array with a[0] unused.

    Returns:
        1-based prefix sums array S with:
            - S[0] = 0,
            - S[k] = sum_{i=1}^k a[i].
    """
    S = [0] * len(a)
    running = 0
    for i in range(1, len(a)):
        running += a[i]
        S[i] = running
    return S
```

The first function, `build_sequence_naive`, constructs the sequence values
$$a_1,a_2,\dots,a_{N+1}$$ directly from the recurrence by iterating over all
indices up to $$N$$.
The second function, `prefix_sums_naive`, then computes the prefix sums
$$S(k)=\sum_{i=1}^k a_i$$ in a single linear pass.

Together, these two routines implement the most direct solution to the problem:
explicit sequence generation followed by explicit summation.
This approach is simple and transparent, but its runtime grows linearly with
$$N$$, which makes it unsuitable for very large inputs.

The following example demonstrates how the naive implementation can be used for
moderate values of $$N$$. We generate the sequence, inspect the first few terms,
and finally compute the prefix sum $$S(N)$$.

```python
N = 10_000
a1 = 2
q, r, t = -11, 22, -33

a = build_sequence_naive(N=N, a1=a1, q=q, r=r, t=t)

# Show the first few terms a_1..a_20 (ignore a[0]).
print(a[1:21])

# Prefix sums S(k) = sum_{i=1}^k a_i in O(N).
S = prefix_sums_naive(a)

# This is S(N).
print("S(N):", S[N])
```

In this example, we fix concrete values for the parameters $$a_1$$, $$q$$, $$r$$,
and $$t$$, and choose a moderately large bound $$N = 10\,000$$.
The sequence is first generated explicitly up to index $$N+1$$ using the naive
construction.

Printing the first few terms provides a quick sanity check that the recurrence
is applied as expected.
Afterwards, the prefix sums are computed in linear time, and the final value
$$S(N)$$ is obtained by a simple array lookup.

For values of $$N$$ on this scale, this approach works well and is easy to
understand—but it already hints at why a different strategy is needed when
$$N$$ becomes much larger.

Before moving on to the optimized algorithm, it is helpful to *see* what this
recurrence produces.

The following plot shows the sequence values $$a_n$$ and their corresponding
prefix sums $$S(n)$$ for a fixed choice of parameters and a moderate range of
indices. Even at this scale, the behavior is far from simple: the sequence
oscillates, changes magnitude rapidly, and the prefix sums reflect a complex
accumulation of these effects.

This visual complexity hints at why a naive summation strategy quickly becomes
unwieldy—and why exploiting the structure of the recurrence is essential.

<br>
{% include figure.liquid loading="eager" path="assets/img/2026-01-10-pe-818p100-generalized-parity-recurrence/2026-01-10-pe-818p100-generalized-parity-recurrence.png" class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="95%"
caption="The parity-defined sequence $a_n$ (top) and its prefix sums $S(n)$ (bottom) for fixed parameters. Even at moderate sizes, the behavior is highly irregular." %}

<br> 
### An Optimized Prefix-Sum Algorithm

The naive approach makes the difficulty of the problem clear: explicitly
generating the sequence and summing its terms requires time proportional to
$$N$$, which quickly becomes infeasible.

We now turn to an optimized algorithm that avoids this bottleneck entirely.
Instead of iterating over all indices up to $$N$$, the method exploits the
parity-based structure of the recurrence derived earlier.

The key idea is to process the binary representation of $$N$$ from left to right,
maintaining only a **constant-size state** that contains just enough information
to update the prefix sum when the index is doubled or incremented by one.
At each step, the problem size is effectively cut in half.

At a high level, the algorithm can be summarized as follows:

```text
initialize state at n = 1
for each remaining binary digit of N (left to right):
    precompute S(2n), S(2n+1), a_{2n}, a_{2n+1}, a_{2n+2}
    if bit == 0:
        update state to n = 2n
    else:
        update state to n = 2n + 1
return S(N)
```

The full implementation below is a direct and faithful translation of this idea.

As a result, the number of operations grows only with the number of binary digits
of $$N$$, making it possible to compute $$S(N)$$ even for astronomically large
values of $$N$$.
The following implementation is a direct translation of the derivation above into
code.

```python
from __future__ import annotations


def prefix_sum_a(
    N: int,
    a1: int | float,
    q: int | float,
    r: int | float,
    t: int | float,
) -> int | float:
    """Compute the prefix sum S(N) for a parity-defined recurrence in O(log N).

    We consider a sequence $(a_n)_{n\\ge 1}$ defined by constants $q, r, t$:

    $$
    \\begin{aligned}
    a_{2n}   &= q\\,a_n, \\\\
    a_{2n+1} &= r\\,a_n + t\\,a_{n+1},
    \\end{aligned}
    \\qquad (n\\ge 1),
    $$

    with given initial value $a_1 = a1$.

    The associated prefix sums are

    $$
    S(n) = \\sum_{k=1}^{n} a_k, \\qquad S(0)=0.
    $$

    Using the derived identities

    $$
    S(2n)   = (q+t)\\,S(n) + r\\,S(n-1) + (1-t)\\,a_1,
    $$
    $$
    S(2n+1) = S(2n) + r\\,a_n + t\\,a_{n+1},
    $$

    we can compute $S(N)$ by walking through the binary representation of $N$
    and maintaining the constant-size state

        (S(n-1), S(n), a_n, a_{n+1})

    which is updated according to whether the next binary digit corresponds to
    $n \\mapsto 2n$ (bit 0) or $n \\mapsto 2n+1$ (bit 1).

    Args:
        N:
            Target index (must satisfy N >= 1).
        a1:
            Initial value $a_1$ of the sequence.
        q:
            Constant in the even-index recurrence $a_{2n} = q\\,a_n$.
        r:
            Constant in the odd-index recurrence $a_{2n+1} = r\\,a_n + t\\,a_{n+1}$.
        t:
            Constant in the odd-index recurrence $a_{2n+1} = r\\,a_n + t\\,a_{n+1}$.

    Returns:
        The prefix sum $S(N) = \\sum_{k=1}^{N} a_k$.

    Raises:
        ValueError: If N < 1.

    Notes:
        - This implementation is numerically and type-wise "honest": it supports
          `int` and `float` (and mixtures thereof) and returns `int | float`.
        - Runtime is O(log N) and memory usage is O(1).
    """
    # Guard against invalid input: the sequence is defined for N >= 1.
    if N < 1:
        raise ValueError("N must be >= 1")

    # Process the binary digits of N from left to right.
    # The leading '1' corresponds to n = 1, which we encode in the initial state,
    # so we iterate over the remaining digits only.
    bits = format(N, "b")
    tail_bits = bits[1:]

    # Maintain the state at the current index n:
    #
    #   S_nm1 = S(n-1) = sum_{k=1}^{n-1} a_k
    #   S_n   = S(n)   = sum_{k=1}^{n}   a_k
    #   a_n   = a_n
    #   a_np1 = a_{n+1}
    #
    # Initialize at n = 1:
    #   S(0) = 0
    #   S(1) = a1
    #   a_1  = a1
    #   a_2  = q * a1
    S_nm1: int | float = 0
    S_n: int | float = a1
    a_n: int | float = a1
    a_np1: int | float = q * a1

    # Update the state for each remaining bit.
    for ch in tail_bits:
        # Precompute prefix sums at doubled indices:
        #
        #   S(2n)   = (q+t) S(n) + r S(n-1) + (1-t) a1
        #   S(2n+1) = S(2n) + r a_n + t a_{n+1}
        #
        # These are computed unconditionally; which one we "land on" depends on
        # the next binary digit.
        S_2n = r * S_nm1 + (q + t) * S_n + (1 - t) * a1
        S_2np1 = S_2n + r * a_n + t * a_np1

        if ch == "1":
            # Bit 1: n -> 2n + 1
            #
            # Sequence updates:
            #   a_{2n+1} = r a_n + t a_{n+1}
            #   a_{2n+2} = q a_{n+1}
            new_a_n = r * a_n + t * a_np1
            new_a_np1 = q * a_np1

            # Prefix sum updates:
            #   S((2n+1)-1) = S(2n)
            #   S(2n+1)     = S_2np1
            S_nm1, S_n = S_2n, S_2np1
        else:
            # Bit 0: n -> 2n
            #
            # Sequence updates:
            #   a_{2n}   = q a_n
            #   a_{2n+1} = r a_n + t a_{n+1}
            new_a_n = q * a_n
            new_a_np1 = r * a_n + t * a_np1

            # Prefix sum updates:
            #   S(2n)   = S_2n
            #   S(2n-1) = S(2n) - a_{2n}
            S_nm1, S_n = S_2n - new_a_n, S_2n

        # Advance the sequence state.
        a_n, a_np1 = new_a_n, new_a_np1

    # After all bits have been processed, S_n = S(N).
    return S_n
```

The function `prefix_sum_a` computes the prefix sum $$S(N)$$ without ever
constructing the full sequence.

It walks through the binary digits of $$N$$ and maintains the four values
$$\bigl(S(n-1), S(n), a_n, a_{n+1}\bigr)$$ as its internal state.
For each bit, the state is updated according to whether the index transition is
$$n \mapsto 2n$$ or $$n \mapsto 2n+1$$, using the closed-form recurrences derived
earlier.

Because each binary digit of $$N$$ triggers only a constant amount of work, the
overall runtime is proportional to the bit-length of $$N$$.
This allows exact prefix sums to be computed for values of $$N$$ that are far
beyond the reach of any direct summation approach.


As a quick sanity check, we can compare the naive result (computed by explicitly
building the sequence and its prefix sums) with the optimized function.
For a moderate value of $$N$$ both methods are feasible, so they should agree
exactly.

```python
# Compare naive approach with optimized code for a (small) N.
slow = S[N]
fast = prefix_sum_a(N, a1, q, r, t)

print("naive S(N):", slow)
print("fast  S(N):", fast)
assert slow == fast, "Mismatch between naive and optimized result!"
```

To further increase confidence in the implementation, we can perform a full
verification on a small range of indices.
For a fixed, moderately sized bound $$N$$, the naive method allows us to compute
all prefix sums $$S(1), S(2), \dots, S(N)$$ explicitly.

The following loop compares these reference values against the optimized
algorithm for *every* index up to $$N$$.
If the derivation and implementation are correct, all results must match exactly.

```python
# Verify that the optimized O(log n) algorithm matches the naive result
# for all n <= N.

for n in range(1, N + 1):
    fast = prefix_sum_a(n, a1, q, r, t)
    slow = S[n]

    if fast != slow:
        raise AssertionError(
            f"Mismatch at n={n}: "
            f"fast={fast}, slow={slow}"
        )

print(f"Verification passed: optimized and naive prefix sums match for all n <= {N}.")
```

<br>
### Demonstrating the Power of the Optimized Algorithm

The true strength of the approach becomes apparent when we push it far beyond the
range where any naive method could possibly work.

Since the optimized algorithm performs one constant-time update per binary digit
of $$N$$, its runtime depends only on the **bit-length** of $$N$$, not on $$N$$
itself. This makes it feasible to compute prefix sums for indices that are
astronomically large.

The following example evaluates $$S(N)$$ for a selection of increasingly large
values of $$N$$—ranging from millions to numbers with dozens of digits. Even the
so-called "worst-case" bit patterns, where all binary digits are equal to one, are
handled just as easily.


```python
# Demonstration: huge N is easy with the O(log N) method.

a1 = 2
q, r, t = -11, 22, -33

test_Ns = [
    10**6,
    10**9,
    10**12,
    10**15,
    10**18,
    (1 << 60) - 1,   # ~1.15e18 (all 1-bits, "worst-case" bit-pattern)
    (1 << 80) - 1,
    10**30,          # absurdly large, still fine
]

for N in test_Ns:
    S_N = prefix_sum_a(N, a1, q, r, t)
    print(f"N={N:<32}  bits={N.bit_length():>3}  S(N)={S_N}")
```

This final demonstration highlights the central takeaway: once the hidden
structure of the recurrence is exposed, computing a sum of $$N$$ terms no longer
requires work proportional to $$N$$—only to the number of bits needed to write
$$N$$ down.


<br>
## Summary

We started with a simple recurrence that defines a sequence by splitting
indices into even and odd cases. While computing individual terms is easy, the task
of summing the first $$N$$ terms quickly becomes infeasible when $$N$$ is large.

By carefully analyzing how the recurrence behaves under index doubling, we derived
closed formulas for the prefix sums $$S(2n)$$ and $$S(2n+1)$$. These relations reveal
a hidden binary structure: prefix sums at large indices can be expressed entirely in
terms of much smaller ones, together with a small amount of local state.

This insight leads directly to an efficient algorithm that processes the binary
representation of $$N$$ and maintains only a constant-size state. As a result,
the prefix sum $$S(N)$$ can be computed exactly in time proportional to the number
of bits of $$N$$, rather than to $$N$$ itself.

The contrast between the naive and optimized implementations highlights a recurring
theme in algorithmic mathematics: once the right structure is identified, problems
that initially appear intractable can often be solved with surprising efficiency.
