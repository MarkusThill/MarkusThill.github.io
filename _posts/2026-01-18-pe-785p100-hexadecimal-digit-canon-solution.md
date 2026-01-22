---
layout: post
title: "The Hexadecimal Digit Canon Challenge: Solution"
modified:
categories: [programming, algorithms, mathematics]
description: ""
tags: [combinatorics, discrete-math, algorithms, optimization, python]
thumbnail:
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-01-20T20:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
images:
  compare: false
  slider: false
---

In the Hexadecimal Canon, every number is first stripped of all insignificant zeros and reordered into its most "pure" form. The value of a number is not what it looks like at first glance, but what remains after this canonical purification.

All numbers in this problem are written in **base 16 (hexadecimal)**. The available digits are

$$
0,1,2,3,4,5,6,7,8,9,\text{A},\text{B},\text{C},\text{D},\text{E},\text{F},
$$

with $$\text{A}=10,\dots,\text{F}=15.$$

<br>

### The Digit–Canonical Function

For any **positive hexadecimal integer** $$d > 0$$, define the function $$f(d)$$ as follows:

1. Write $$d$$ in hexadecimal.
2. Sort its hexadecimal digits in **ascending order**.
3. Remove **all zero digits**.
4. Interpret the remaining digits again as a hexadecimal number.

Since $d > 0$, removing zero digits always leaves at least one hexadecimal digit.

<br>

### Examples

- **Example 1:**
  $$d = \texttt{0x3A04}$$. 
  Digits: $$3, A, 0, 4.$$ Sorted: $$0, 3, 4, A.$$  Remove zeros → $$3, 4, A$$.
  Result: $$f(\texttt{0x3A04}) = \texttt{0x34A}$$

- **Example 2**
  $$d = \texttt{0xF102}$$. Digits: $$F, 1, 0, 2$$. Sorted: $$0, 1, 2, F$$. Remove zeros → $$1, 2, F$$. Result: $$f(\texttt{0xF102}) = \texttt{0x12F}$$

- **Example 3**
  $$d = \texttt{0x800}$$. Digits: $$8, 0, 0$$. Sorted: $$0, 0, 8$$. Remove zeros → $$8$$. Result: $$f(\texttt{0x800}) = \texttt{0x8}$$

- **Example 4:**  $d = \texttt{0xA11B0}$. Digits: $A,1,1,B,0$. Sorted: $0,1,1,A,B$.  Remove zeros → $1,1,A,B$. Result: $f(\texttt{0xA11B0}) = \texttt{0x11AB}$.

<br>

### The Cumulative Sum

Let $$S(n)$$ denote the sum of $$f(d)$$ over **all positive hexadecimal integers with at most $$n$$ hexadecimal digits**.

For example:
- For $$n = \texttt{0x1}$$, the result is
  $$
  S(\texttt{0x1}) = \texttt{0x78}
  $$
- For $$n = \texttt{0x3}$$, the result is
  $$
  S(\texttt{0x3}) = \texttt{0x4077C0}
  $$

> **Important:** All values of $$S(n)$$ are to be reported **in hexadecimal notation**.

<br>
## Challenge Levels 🏅

Compute $$S(n)$$ for the following four difficulty tiers:

| Tier | Value of $$n$$ (hexadecimal) | Your Result (hexadecimal) |
|------|------------------------------|---------------------------|
| 🎗 Warm-up | $$n = \; \texttt{0x5}$$ | $$S(n) = \;\_\_\_\_\_\_\_\_\_\_\_\_$$ |
| 🥉 Bronze | $$n = \; \texttt{0xA}$$ | $$S(n) = \;\_\_\_\_\_\_\_\_\_\_\_\_$$ |
| 🥈 Silver | $$n = \; \texttt{0xAA}$$ | $$S(n) = \;\_\_\_\_\_\_\_\_\_\_\_\_\, \, $$ (first & last 10 hex digits) |
| 🥇 Gold | $$n = \; \texttt{0xAAA}$$ | $$S(n) \equiv \;\_\_\_\_\_\_\_\_\_\_\_\_  \pmod{\texttt{0x1FFFFFFFFFFFFFFF}} $$ |

<br> 

For the **silver** medal, report **only** the **first 10** and **last 10** hexadecimal digits of $$S(n)$$.  
Here, "first 10" means the first 10 digits of the standard hexadecimal representation of $$S(n)$$, and "last 10" means the last 10 digits (equivalently $$S(n) \bmod 16^{10}$$). The problem is designed so that **neither part has leading zeros**, and both substrings consist of exactly 10 hexadecimal digits.

For the **gold** medal, report your hexadecimal answer **modulo** $$\texttt{0x1FFFFFFFFFFFFFFF}.$$

<br>

---

## Solution Sketch
### A first (naive) implementation

Before attempting any optimizations, it is helpful to translate the problem statement **as literally as possible** into code. The following implementation does exactly that: it follows the definition of the function $$f(d)$$ and the cumulative sum $$S(n)$$ step by step, without attempting to reduce the computational cost.
The core idea is straightforward:
- Enumerate **all positive integers $$d$$** with at most $$n$$ digits in the chosen base (8, 10, or 16).
- For each $$d$$:
  - Convert it to its digit representation in that base,
  - Sort the digits in ascending order,
  - Remove all zeros,
  - Interpret the remaining digits again as a number to obtain $$f(d)$$.
- Accumulate the sum of all $$f(d)$$ values to obtain $$S(n)$$.

This approach has several important characteristics:
- Conceptual clarity: Each operation in the code mirrors the mathematical definition directly, making it easy to reason about correctness.
- Generality: The same implementation works unchanged for base 8, base 10, and base 16, which is useful for experimentation and cross-checking small cases.
- Very poor scalability:
  The number of values that must be processed grows as $$\text{base}^n$$. Even for modest values of $$n$$, this results in an enormous number of iterations, rendering the method impractical for the actual challenge.
- Reference value generation: Despite its inefficiency, the naive solution plays an important role: it provides trustworthy results for small $$n$$, which can later be used to validate faster, more sophisticated approaches.

In the next sections, we will keep this implementation as a correctness baseline and progressively replace the brute-force enumeration by more efficient combinatorial and dynamic-programming techniques.

For $$n = 3$$, we can already confirm the result obtained above:

```python
from __future__ import annotations

# We only need very lightweight helpers here; this is intentionally a
# *naive* reference implementation that favors clarity over performance.


def _format_base(d: int, base: int) -> str:
    """Return the base-`base` representation of `d` as a string.

    We restrict ourselves to bases 8, 10, and 16:
      - base 8  -> octal digits 0–7
      - base 10 -> decimal digits 0–9
      - base 16 -> hexadecimal digits 0–9, a–f

    The returned string uses lowercase letters for hexadecimal digits.
    """
    if base == 10:
        # Decimal needs no special formatting
        return str(d)
    if base == 8:
        # Python's built-in octal formatter
        return format(d, "o")
    if base == 16:
        # Python's built-in hexadecimal formatter (lowercase)
        return format(d, "x")

    # Any other base is deliberately rejected to keep the code simple
    raise ValueError(f"Unsupported base={base}. Use one of: 8, 10, 16.")


def f_of_d(d: int, base: int) -> int:
    """Compute f(d) in the given base.

    This follows the problem definition *literally*:

      1) Write d in the chosen base.
      2) Sort the digits in ascending order.
      3) Remove all zero digits.
      4) Interpret the remaining digits again as a number in that base.

    Example (base 16):
      d = 0x3A04  -> "3a04"
      digits     -> ["3", "a", "0", "4"]
      sorted     -> ["0", "3", "4", "a"]
      no zeros   -> ["3", "4", "a"]
      result     -> int("34a", 16)
    """
    # Convert d to a string in the given base
    s = _format_base(d, base)

    # Remove all '0' digits, because f(d) discards them by definition.
    # The result is a list of digit *characters*.
    digits_no_zero = [ch for ch in s if ch != "0"]

    # Sort remaining digits in ascending order.
    #
    # Important subtlety:
    # - For base 8 and 10, lexicographic order equals numeric order.
    # - For base 16, Python uses characters '0'–'9','a'–'f', and their
    #   lexicographic order also matches numeric digit order.
    digits_no_zero.sort()

    # There is always at least one non-zero digit:
    # any representation of a positive integer contains at least one
    # non-zero digit in any base.
    canonical_str = "".join(digits_no_zero)

    # Convert back to an integer, interpreting the string in the same base
    return int(canonical_str, base)


def S_naive(
    n: int,
    base: int,
    debug_target: int | None = None,
) -> tuple[int, list[int], int, int]:
    """Naively compute S(n) by brute force.

    We enumerate *all* positive integers d with at most n digits in the
    given base, i.e.

        1 <= d < base**n

    For each such d, we compute f(d) and accumulate the sum.

    This function is intentionally slow and is meant only as:
      - a correctness reference
      - a debugging / sanity-check tool

    Returns:
      total:
          The value of S(n) as a Python integer.
      debug_hits:
          All d such that f(d) == debug_target (empty if debug_target is None).
      num_values:
          Total number of integers d that were enumerated.
      num_distinct:
          Number of distinct values taken by f(d).
    """
    if n <= 0:
        raise ValueError("n must be a positive integer.")
    if base not in (8, 10, 16):
        raise ValueError("base must be one of: 8, 10, 16.")

    # All positive integers with <= n digits in base `base` satisfy
    #   1 <= d < base**n
    upper_exclusive = base**n

    debug_hits: list[int] = []

    # Track which f(d) values we have seen so far
    seen: set[int] = set()

    total = 0           # running sum S(n)
    num_distinct = 0    # number of distinct f(d) values

    for d in range(1, upper_exclusive):
        # Compute f(d) directly from the definition
        f_d = f_of_d(d, base)

        # Add contribution to the total sum
        total += f_d

        # Count distinct f(d) values (purely diagnostic)
        if f_d not in seen:
            seen.add(f_d)
            num_distinct += 1

        # Optional debugging hook:
        # record which original d map to a particular f(d)
        if debug_target is not None and f_d == debug_target:
            debug_hits.append(d)

    # Number of values enumerated (purely diagnostic)
    num_values = upper_exclusive - 1

    return total, debug_hits, num_values, num_distinct


def format_answer(x: int, base: int) -> str:
    """Format the final answer in the requested output base.

    This is useful because the *internal* computation uses Python integers,
    but the puzzle statement asks for answers written in base 8/10/16.
    """
    if base == 10:
        return str(x)
    if base == 8:
        return format(x, "o")
    if base == 16:
        # Uppercase hex looks nicer and is common in math puzzles
        return format(x, "X")
    raise ValueError(f"Unsupported base={base}.")


# ---------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------

base = 16          # choose 8, 10, or 16
n = 0x3              # compute S(n)

# Set to an integer (in base-10) to see which d map to that f(d),
# or set to None to disable debugging.
debug_target = 0xDF

ans, debug_hits, num_values, num_distinct = S_naive(
    n=n,
    base=base,
    debug_target=debug_target,
)

print("num_values   =", num_values)
print("num_distinct =", num_distinct)
print("debug_hits   =", len(debug_hits))
print("S(n)         =", format_answer(ans, base))
```

Output:
```text
num_values   = 4095
num_distinct = 815
debug_hits   = 6
S(n)         = 4077C0
```

If we change $n$ in above code to `0x5`, we already earn our first award (🎗 Warm-up):

```text
num_values   = 1048575
num_distinct = 15503
debug_hits   = 20
S(n)         = 286D8F92C0
```

<br>

*Counting Distinct Values: Naive Approach*

As a small extension of the previous brute-force method, the following code counts how many **distinct values of $$f(d)$$** appear when considering all numbers with at most $$n$$ digits in a given base (8, 10, or 16).

The implementation again mirrors the definition directly:
for each $$n$$, it iterates over all integers
$$
1 \le d < \text{base}^n,
$$
computes $$f(d)$$, and inserts the result into a set to track distinct outcomes.

This approach is useful for exploration, for example to observe how the number of distinct canonical digit strings grows with $$n$$. However, it suffers from the same fundamental limitation as the full sum computation:

- The runtime grows as $$\Theta(\text{base}^n)$$.
- Even for moderate values of $$n$$, the total number of iterations becomes prohibitively large.
- The method is therefore **unsuitable for large inputs** and serves only as a reference and sanity-check tool.

In the next step, we will replace this exhaustive enumeration by a purely combinatorial counting argument that avoids iterating over individual numbers altogether.


```python
def distinct_counts_by_n(max_n: int, base: int) -> list[tuple[int, int]]:
    """Return [(n, num_distinct_for_S(n))] for n = 1..max_n.

    num_distinct_for_S(n) counts the number of distinct f(d) values
    among all d with at most n digits in the given base, i.e.

        1 <= d < base**n
    """
    results: list[tuple[int, int]] = []

    for n in range(1, max_n + 1):
        upper_exclusive = base**n
        distinct: set[int] = set()

        for d in range(1, upper_exclusive):
            distinct.add(f_of_d(d, base))

        results.append((n, len(distinct)))

    return results


# --------------------------------------------------
# Example: observe growth for small n
# --------------------------------------------------

base = 16  # choose 8, 10, or 16

for n, cnt in distinct_counts_by_n(max_n=5, base=base):
    print(f"n={n}  num_distinct={cnt}")
```

Output:
```text
n=1  num_distinct=15
n=2  num_distinct=135
n=3  num_distinct=815
n=4  num_distinct=3875
n=5  num_distinct=15503
```


<br>

*Counting Distinct Values: Closed Form*

We fix a base $$b \in \{8,10,16\}$$ with digits $$0,1,\dots,b-1$$. For a number $$d$$ with exactly $$m$$ digits in base $$b$$, let

$$
c_i = \#\text{occurrences of digit } i \quad (i=0,1,\dots,b-1),
\qquad
\sum_{i=0}^{b-1} c_i = m.
$$

Recall that $$f(d)$$ sorts digits and removes zeros. So the output is determined only by the non-zero multiplicities

$$
(c_1,\dots,c_{b-1}),
\qquad
k := \sum_{i=1}^{b-1} c_i = m - c_0,
$$

where $$k$$ is the number of non-zero digits that survive.

The goal is to count how many distinct outputs $$f(d)$$ can take among all $$d$$ with at most $$n$$ digits.

Fix an integer $k \ge 1$. We now count how many **distinct outputs** $f(d)$ are possible when exactly $k$ non-zero digits survive after removing zeros.
Since $f(d)$ sorts digits in ascending order and discards all zeros, every output
$f(d)$ with $k$ digits is a **nondecreasing sequence**

$$
1 \le d_1 \le d_2 \le \cdots \le d_k \le b-1.
$$

Equivalently, each output corresponds to a multiset of size $k$ chosen from the $(b-1)$ non-zero digits $\{1,2,\dots,b-1\}$.

This is precisely the combinatorial notion of a combination with replacement:
- we choose $k$ elements,
- from $(b-1)$ distinct types,
- repetitions are allowed,
- and order does not matter.

A standard result in combinatorics states that the number of combinations with replacement of size $k$ from $N$ distinct elements is

$$
\binom{N + k - 1}{k}.
$$

Here $N = b-1$, so the number of distinct values of $f(d)$ with exactly $k$ non-zero digits is

$$
\binom{(b-1) + k - 1}{k}
=
\binom{k + b - 2}{k}
=
\binom{k + b - 2}{\,b-2\,}.
$$

Now allow all possible values of $k$. For numbers $d$ with **at most $n$ digits**, the number of non-zero digits satisfies

$$
1 \le k \le n,
$$

because removing zeros can only decrease the digit count, and at least one non-zero digit must remain.

Therefore, the total number of distinct outputs of $f(d)$ is

$$
\sum_{k=1}^{n} \binom{k + b - 2}{b - 2}.
$$

This sum has a closed form via the hockey-stick identity:

$$
\sum_{k=0}^{n} \binom{k + b - 2}{b - 2}
=
\binom{n + b - 1}{b - 1}.
$$

Subtracting the $k=0$ term (which equals $\binom{b-2}{b-2}=1$ and corresponds to the invalid empty output), we obtain

$$
\boxed{
\#\{\text{distinct } f(d) \text{ for } \le n \text{ digits}\}
=
\binom{n + b - 1}{b - 1} - 1
}
$$


*Special Cases*

- Base $b=10$ (decimal):
  $$
  \binom{n+9}{9}-1
  $$

- Base $b=8$ (octal):
  $$
  \binom{n+7}{7}-1
  $$

- Base $b=16$ (hexadecimal):
  $$
  \binom{n+15}{15}-1
  $$

This explains why the number of distinct values grows only polynomially in $n$, even though the total number of $n$-digit numbers grows exponentially.


```python
from __future__ import annotations

from math import comb


def num_distinct_closed_form(n: int, base: int) -> int:
    """Number of distinct f(d) values among all positive integers with <= n digits in `base`.

    Key idea:
      For a fixed digit-length k, the value f(d) is determined solely by how many times
      each *non-zero* digit appears (zeros are discarded).

      Let b = base. The non-zero digits are {1, 2, ..., b-1}.
      For length k we count solutions to

          c_1 + c_2 + ... + c_{b-1} = k,  with c_i >= 0,

      i.e. the number of multisets of size k drawn from (b-1) symbols:

          C(k + (b-1) - 1, (b-1) - 1) = C(k + b - 2, b - 2).

      Summing over k = 1..n gives:

          sum_{k=1..n} C(k + b - 2, b - 2)
          = C(n + b - 1, b - 1) - 1

      (The "-1" removes the k=0 case corresponding to the empty multiset.)
    """
    if n <= 0:
        return 0
    if base not in (8, 10, 16):
        raise ValueError("base must be one of 8, 10, 16.")

    # Closed form: C(n + base - 1, base - 1) - 1
    return comb(n + base - 1, base - 1) - 1


def print_distinct_table(n_max: int, base: int) -> None:
    """Print a small table of num_distinct for n=1..n_max."""
    print(f"Base = {base}")
    for n in range(1, n_max + 1):
        print(f"n={n:2d}  num_distinct={num_distinct_closed_form(n, base)}")


# --------------------------------------------------
# Example usage
# --------------------------------------------------

for base in (16, ): # could also add other bases like 8 or 10
    print_distinct_table(n_max=20, base=base)
    print()
```


```text
Base = 16
n= 1  num_distinct=15
n= 2  num_distinct=135
n= 3  num_distinct=815
n= 4  num_distinct=3875
n= 5  num_distinct=15503
n= 6  num_distinct=54263
n= 7  num_distinct=170543
n= 8  num_distinct=490313
n= 9  num_distinct=1307503
n=10  num_distinct=3268759
n=11  num_distinct=7726159
n=12  num_distinct=17383859
n=13  num_distinct=37442159
n=14  num_distinct=77558759
n=15  num_distinct=155117519
n=16  num_distinct=300540194
n=17  num_distinct=565722719
n=18  num_distinct=1037158319
n=19  num_distinct=1855967519
n=20  num_distinct=3247943159
```

The key takeaway is that the number of distinct values of $f(d)$ grows only polynomially in $n$, even though the total number of $n$-digit numbers grows exponentially.

For example, in base $16$ and $n=10$, the number of distinct values is

$$
\binom{10 + 16 -1}{16-1}-1 = 3268759,
$$

which is small enough to explicitly generate all distinct values of length up to
10 in practice.

This observation will allow us, in the next section, to replace brute-force enumeration over all numbers by a much more efficient enumeration over all distinct $f(d)$ values.


<br>

### Computing $S(n)$ by enumerating distinct $f(d)$ values (and their multiplicities)

The definition of $f(d)$ is "sort digits ascending and remove zeros".  
This means that many different numbers $d$ collapse to the same value $f(d)$: any
permutation of the non-zero digits and any placement of zeros produces the same
sorted, zero-free output.

The key idea of the algorithm is therefore:
> Do not iterate over all $d < b^n$.  Instead, iterate only over the distinct outputs $f(d)$ and count how many original numbers map to each of them.

This splits the problem into two conceptually clean parts.

*1) Enumerating all distinct outputs $f(d)$*

A value $f(d)$ is exactly a finite **nondecreasing digit string** over the alphabet
$\{1,2,\dots,b-1\}$.

Equivalently, each distinct output corresponds to a sequence

$$
1 \le d_1 \le d_2 \le \cdots \le d_k \le b-1,
\qquad 1 \le k \le n,
$$

where $k$ is the number of non-zero digits.

The algorithm generates these sequences via a FIFO queue:

- start with all one-digit sequences $1,2,\dots,b-1$,
- repeatedly append digits $\ge$ the current last digit (to preserve sorting),
- stop extending once the length reaches $n$.

Each distinct value of $f(d)$ is generated exactly once.


*2) Counting how many numbers map to a fixed $f_d$*

Fix one distinct output $f_d$ and let:

- $k$ be the number of non-zero digits in $f_d$,
- $c_i$ be the number of occurrences of digit $i$ in $f_d$ for $i=1,\dots,b-1$.

Now consider all original numbers $d$ that map to this fixed $f_d$.


*(a) Permuting the non-zero digits*

Ignoring zeros for the moment, the number of distinct permutations of the $k$
non-zero digits with multiplicities $(c_1,\dots,c_{b-1})$ is

$$
\frac{k!}{\prod_{i=1}^{b-1} c_i!}.
$$

This counts all ways the non-zero digits can appear relative to each other.

*(b) Inserting zeros without creating leading zeros*

Let $c_0$ denote the number of zeros inserted.  
Then the total digit length of $d$ is

$$
m = k + c_0,
\qquad 1 \le m \le n.
$$

Because $d$ must be an $m$-digit number, its leading digit cannot be zero.

Among the $m$ digit positions, this means:

- position 1 must contain a non-zero digit,
- the remaining $m-1$ positions are free to hold zeros.

So the number of valid ways to place $c_0$ identical zeros is

$$
\binom{m-1}{c_0}
=
\binom{k+c_0-1}{c_0}.
$$

*3) Combining both contributions*

For a fixed $f_d$, the total number of original numbers $d$ mapping to it is

$$
\left(\frac{k!}{\prod_{i=1}^{b-1} c_i!}\right)
\cdot
\sum_{c_0=0}^{n-k} \binom{k+c_0-1}{c_0}.
$$

Since each such $d$ contributes the same value $f_d$ to the sum, the total
contribution of this class is

$$
f_d \times \text{multiplicity}(f_d).
$$

Instead of iterating over all $b^n$ numbers, we only iterate over the distinct
values of $f(d)$, whose number grows like

$$
\binom{n+b-1}{b-1}.
$$

This reduces an exponential problem to a polynomial one and makes it feasible to explicitly enumerate all distinct outputs, for example, up to $S(0xA)$, laying the groundwork for the even more efficient methods developed next.

```python
from __future__ import annotations

import math
from collections import Counter, deque
from collections.abc import Iterable


def S(n: int, base: int, fmt: str) -> int:
    """Compute S(n) by enumerating distinct f(d) values and counting multiplicities.

    Structure (kept the same):
      1) Enumerate all distinct values of f(d) among numbers with <= n digits.
         Each such value is a nondecreasing sequence of non-zero digits (1..base-1).
      2) For each distinct output f_d, count how many original numbers d (with <= n digits)
         map to it, by:
           - counting multiset permutations of the k non-zero digits
           - inserting z zeros for z = 0..(n-k), while forbidding a leading zero

    Args:
        n: Maximum number of digits of d (in base `base`).
        base: Base b (e.g. 8, 10, 16).
        fmt: Python `format` specifier matching the base:
            - base=10 -> "d"
            - base=16 -> "x" (or "X")
            - base=8  -> "o"

    Returns:
        S(n) as an exact integer.
    """
    # -------------------------------------------------------------------------
    # Phase 1: enumerate all distinct f(d) values for numbers with <= n digits.
    #
    # A value f(d) is just the sorted non-zero digits of d. Therefore it is
    # fully determined by a nondecreasing digit string over {1,2,...,base-1}.
    # We generate all such strings of length 1..n with a FIFO queue (BFS).
    # -------------------------------------------------------------------------
    max_value_exclusive = base**n  # any integer with >= n digits in base `base` is >= base**n

    fifo: deque[int] = deque(range(1, base))  # seed with all 1-digit non-zero values
    all_f_values: list[int] = []

    while fifo:
        f_d = fifo.popleft()
        all_f_values.append(f_d)

        # Try to extend by one digit (append in base `base`).
        new_prefix = base * f_d
        if new_prefix >= max_value_exclusive:
            continue  # already length n, cannot extend further

        last_digit = f_d % base
        for next_digit in range(last_digit, base):
            fifo.append(new_prefix + next_digit)

    # Optional sanity check (if available).
    assert len(all_f_values) == num_distinct_closed_form(n, base)

    # -------------------------------------------------------------------------
    # Helper: multiset permutations count = k! / prod_i c_i!
    # where c_i are multiplicities of equal digits in the k-digit string f_d.
    # -------------------------------------------------------------------------
    def multinomial_coefficient(k: int, counts: Iterable[int]) -> int:
        denom = 1
        for c in counts:
            denom *= math.factorial(c)
        return math.factorial(k) // denom

    # -------------------------------------------------------------------------
    # Phase 2: sum contributions.
    #
    # For a fixed distinct f_d:
    #   - let k be its length (number of non-zero digits)
    #   - perms_nonzero counts how many different permutations of those k digits exist
    #
    # Now fix z zeros to insert (0 <= z <= n-k). The final length is L = k+z.
    # Constraint: d must be an L-digit number, so its first digit cannot be 0.
    #
    # Therefore we choose the z zero-positions among the remaining L-1 slots:
    #
    #   interleave_zeros(k, z) = C(L-1, z) = C(k+z-1, z).
    # -------------------------------------------------------------------------
    total = 0

    for f_d in all_f_values:
        f_d_str = format(f_d, fmt)  # base-appropriate digit string
        k = len(f_d_str)

        # Multiplicities of digits within f_d (e.g. "11227" -> counts [2,1,1,1]).
        counts = Counter(f_d_str).values()

        # Number of distinct permutations of these k digits.
        perms_nonzero = multinomial_coefficient(k, counts)

        multiplicity = 0
        for z in range(0, n - k + 1):
            # Ways to insert z zeros into total length L=k+z without leading zero:
            # choose z positions among the last (L-1) positions.
            interleave_zeros = math.comb(k + z - 1, z) if z > 0 else 1

            multiplicity += perms_nonzero * interleave_zeros

        total += f_d * multiplicity

    return total


# Example usage: compute S(n) for hexadecimal numbers
for n_test in (3, 5, 0xA):
    value = S(n_test, base=16, fmt="x")
    print(f"S(0x{format_answer(n_test, base)}) in base 16 = 0x{format_answer(value, base)}")
```

```text
S(0x3) in base 16 = 0x4077C0
S(0x5) in base 16 = 0x286D8F92C0
S(0xA) in base 16 = 0x12C698E48B4FC2A01358
```

This solution would already win us the Bronze 🥉 medal.


### From Brute Force to Digit Dynamics: Building a Much Faster Solution

Fix a base $b$ ($b=16$) and a digit-count vector

$$
(c_0,c_1,\dots,c_{b-1}),
\qquad
\sum_{i=0}^{b-1} c_i = m,
\qquad
k := \sum_{i=1}^{b-1} c_i = m - c_0.
$$

So $m$ is the total number of digits, $c_0$ is the number of zeros, and $k$ is the
number of non-zero digits (the ones that survive in $f(d)$).

*Step 1: Count all permutations of the multiset of digits*

If we ignore the "no leading zero" rule, then the number of distinct permutations
of the multiset containing:

- $c_0$ zeros,
- $c_1$ ones,
- $\dots$,
- $c_{b-1}$ digits $(b-1)$,

is the standard multinomial count

$$
N_{\text{all}}
=
\frac{m!}{c_0!\,c_1!\cdots c_{b-1}!}.
$$

*Step 2: Subtract permutations that start with zero*

A permutation is invalid if its first digit is $0$.

To count those, we **fix** one zero in the leading position. That consumes one of the $c_0$ zeros, leaving:

- $c_0 - 1$ zeros to permute in the remaining $m-1$ positions,
- and the same $c_1,\dots,c_{b-1}$ non-zero counts.

Hence the number of invalid permutations is

$$
N_{\text{lead0}}
=
\frac{(m-1)!}{(c_0-1)!\,c_1!\cdots c_{b-1}!}.
$$

So the number of valid $m$-digit numbers (no leading zero) with these digit counts is

$$
N_{\text{valid}}
=
N_{\text{all}} - N_{\text{lead0}}
=
\frac{m!}{c_0!\,\prod_{i=1}^{b-1} c_i!}
-
\frac{(m-1)!}{(c_0-1)!\,\prod_{i=1}^{b-1} c_i!}.
$$


*Step 3: Factor out common terms*

Both terms share $(m-1)!$ and $\prod_{i=1}^{b-1} c_i!$:

$$
N_{\text{valid}}
=
\frac{(m-1)!}{\prod_{i=1}^{b-1} c_i!}
\left(
\frac{m}{c_0!}
-
\frac{1}{(c_0-1)!}
\right).
$$

Now rewrite the second fraction using $(c_0-1)! = \frac{c_0!}{c_0}$, i.e.

$$
\frac{1}{(c_0-1)!}
=
\frac{c_0}{c_0!}.
$$

Substitute:

$$
\frac{m}{c_0!} - \frac{1}{(c_0-1)!}
=
\frac{m}{c_0!} - \frac{c_0}{c_0!}
=
\frac{m-c_0}{c_0!}.
$$

But $m - c_0$ is exactly $k$ (the number of non-zero digits). Therefore:

$$
N_{\text{valid}}
=
\frac{(m-1)!}{\prod_{i=1}^{b-1} c_i!}
\cdot
\frac{k}{c_0!}.
$$

So we have the clean intermediate form

$$
N_{\text{valid}}
=
\frac{(m-1)! \, k}{c_0! \, \prod_{i=1}^{b-1} c_i!}.
$$

---

*Step 4: Express $c_0!$ via $m$ and $k$*

Since $c_0 = m-k$, we can rewrite

$$
c_0! = (m-k)!.
$$

Plugging this in yields the closed form:

$$
\begin{align}
\boxed{
N_{\text{valid}}
=
\frac{(m-1)! \, k}{(m-k)! \, \prod_{i=1}^{b-1} c_i!}
}.
\end{align}
$$

This is exactly the number of base-$b$ $m$-digit integers (no leading zeros) whose digit multiplicities are $(c_0,c_1,\dots,c_{b-1})$.


<br>
*Grouping by one fixed $f_d$ and summing over all lengths $m \le n$*

Fix one particular non-zero multiplicity vector

$$
(c_1,c_2,\dots,c_{b-1}),
\qquad
k := \sum_{i=1}^{b-1} c_i,
$$

and let $f(c_1,\dots,c_{b-1})$ denote the corresponding sorted "zero-free" value, i.e. the number whose base-$b$ digit multiset contains digit $i$ exactly $c_i$ times.

Our goal is to compute $S(n)$, i.e. the sum of $f(d)$ over all positive integers $d$
with at most $n$ digits.  
Every $d$ that maps to this fixed vector contributes exactly the same value
$f(c_1,\dots,c_{b-1})$ to the sum.

So the contribution of this class is

$$
f(c_1,\dots,c_{b-1}) \cdot \Big(\text{number of } d \text{ with } \le n \text{ digits that map here}\Big).
$$

*Why we sum over $m = k,\dots,n$*

Once zeros are removed, exactly $k$ digits remain. If the original number has $m$ digits and contains $c_0$ zeros, then

$$
m = c_0 + k \quad\Longleftrightarrow\quad c_0 = m-k.
$$

- The smallest possible length is $m=k$, corresponding to $c_0=0$ (no zeros at all).
- Larger $m$ are possible by inserting zeros, i.e. $c_0 \ge 0$.
- Since we only consider numbers with at most $n$ digits, we must have $m \le n$.

Therefore the valid range is exactly

$$
m = k, k+1, \dots, n.
$$


From the previous section, the number of valid $m$-digit numbers (no leading zero)
with digit counts $(c_0,c_1,\dots,c_{b-1})$ is

$$
N_{\text{valid}}(m; c_1,\dots,c_{b-1})
=
\frac{(m-1)!\,k}{(m-k)!\,\prod_{i=1}^{b-1} c_i!},
\qquad\text{where } c_0=m-k.
$$

Multiplying this by the common value $f(c_1,\dots,c_{b-1})$ gives the total
contribution for this fixed $(c_1,\dots,c_{b-1})$ at length $m$:

$$
f(c_1,\dots,c_{b-1})
\cdot
\frac{(m-1)!\,k}{(m-k)!\,\prod_{i=1}^{b-1} c_i!}.
$$

Now sum over all allowed lengths $m=k,\dots,n$:

$$
\sum_{m=k}^{n}
f(c_1,\dots,c_{b-1})
\cdot
\frac{(m-1)!\,k}{(m-k)!\,\prod_{i=1}^{b-1} c_i!}.
$$

Factor out the terms that do not depend on $m$. This is the desired intermediate form:

$$
\begin{align}
\boxed{
k \, \frac{f(c_1,\dots,c_{b-1})}{\prod_{i=1}^{b-1} c_i!}
\;\cdot\;
\sum_{m=k}^{n} \frac{(m-1)!}{(m-k)!}
}.
\end{align}
$$


Define the purely length-dependent factor

$$
\begin{align}
A(k) := \sum_{m=k}^{n} \frac{(m-1)!}{(m-k)!}.
\end{align}
$$

For the fixed non-zero multiplicity pattern, define

$$
\begin{align}
B(k; c_1,\dots,c_{b-1})
:=
\frac{f(c_1,\dots,c_{b-1})}{\prod_{i=1}^{b-1} c_i!}.
\end{align}
$$

Then the contribution of this single pattern becomes

$$
\begin{align}
k \cdot A(k) \cdot B(k; c_1,\dots,c_{b-1}).
\end{align}
$$

In the next step, we will sum $B(k; c_1,\dots,c_{b-1})$ over all choices of
$(c_1,\dots,c_{b-1})$ with $c_1+\cdots+c_{b-1}=k$, to obtain a quantity that
depends only on $k$.

Recall the pattern-dependent factor

$$
B(k; c_1,\dots,c_{b-1})
=
\frac{f(c_1,\dots,c_{b-1})}{\prod_{i=1}^{b-1} c_i!},
\qquad
\text{where } \sum_{i=1}^{b-1} c_i = k.
$$

For a fixed $k$, we now sum this over **all** nonnegative integer vectors
$(c_1,\dots,c_{b-1})$ with total weight $k$ and define

$$
\begin{align}
\boxed{
B(k)
:=
\sum_{\substack{c_1+\cdots+c_{b-1}=k \\ c_i \ge 0}}
\frac{f(c_1,\dots,c_{b-1})}{\prod_{i=1}^{b-1} c_i!}
}.
\end{align}
$$

This $B(k)$ depends only on $k$ (and the base $b$), because the sum ranges over
*all* digit-multiplicity patterns of size $k$.

With this definition, the full sum over all numbers with at most $n$ digits can be written as

$$
\begin{align}
\boxed{
S(n)
=
\sum_{k=1}^{n}
k \cdot A(k) \cdot B(k).
}
\end{align}
$$

*Intuition for what $B(k)$ represents*

For each fixed $k$:

- the constraint $c_1+\cdots+c_{b-1}=k$ enumerates all possible **multisets of $k$ non-zero digits**
  (equivalently, all distinct values of $f(d)$ of length $k$),
- the factor $1/\prod c_i!$ is the "multiset correction" coming from the multinomial counting,
- and $f(c_1,\dots,c_{b-1})$ is the actual numeric value contributed by that multiset.

So $B(k)$ is a weighted sum over all distinct outputs of $f(d)$ having exactly $k$
digits, capturing "how large those $f(d)$ values are on average" under the natural
weights induced by the multinomial coefficients.

In the next step we will show how to compute $B(k)$ efficiently without enumerating
all $(c_1,\dots,c_{b-1})$ patterns explicitly.

<br>

### Computing $B(k)$ efficiently (DP)

Recall the definition (base $b$):

$$
B(k)
=
\sum_{\substack{c_1+\cdots+c_{b-1}=k \\ c_i\ge 0}}
\frac{f(c_1,\dots,c_{b-1})}{\prod_{i=1}^{b-1} c_i!},
$$

where $f(c_1,\dots,c_{b-1})$ is the base-$b$ integer whose digit multiset contains
digit $i$ exactly $c_i$ times, written in sorted order.

A direct sum over all integer vectors $(c_1,\dots,c_{b-1})$ is expensive.
The key trick is that the weight $\frac{1}{\prod c_i!}$ **factorizes over digits**,
so we can build $B(k)$ by processing digits one-by-one with a small DP.



*1) Separate "weights" from "values"*

Introduce two sequences (indexed by length):

- $W[t]$ = total weight of all patterns of total length $t$:

  $$
  W[t] := \sum_{\substack{c_1+\cdots+c_{b-1}=t \\ c_i\ge 0}} \frac{1}{\prod_{i=1}^{b-1} c_i!}.
  $$

- $B[t]$ = the weighted sum of values (this is exactly what we want when $t=k$):

  $$
  B[t] := \sum_{\substack{c_1+\cdots+c_{b-1}=t \\ c_i\ge 0}}
  \frac{f(c_1,\dots,c_{b-1})}{\prod_{i=1}^{b-1} c_i!}.
  $$

So $B(k)$ is just $B[k]$.

We will compute both arrays up to $t=n$.

---

<br>

**<Worked Example: Why we need the weight $W[t]$>**

Assume we are working in base $10$ for simplicity, and that at some DP stage we have the following weighted sum for patterns of length $t$:

$$
B[t]
=
\frac{1122}{2!\,2!}
+
\frac{1112}{3!\,1!}.
$$

This means we have two different digit-multiplicity patterns of length $t$,
each contributing its numeric value divided by the product of factorials of its
digit counts.

Now suppose we want to **append two copies of digit $3$**, i.e. we append the suffix
``33``. For any old value $x$, this transforms the number as

$$
x \;\longmapsto\; x\cdot 10^2 + 33.
$$

Because we are appending $c=2$ identical digits, this choice carries the weight
factor $1/2!$.

So the contribution to $B[t+2]$ is

$$
B[t+2]
=
\frac{1}{2!}
\left(
\frac{1122\cdot 10^2 + 33}{2!\,2!}
+
\frac{1112\cdot 10^2 + 33}{3!\,1!}
\right).
$$

Split the sum into the "old value" part and the "new suffix" part:

$$
\begin{aligned}
B[t+2]
&=
\frac{1}{2!}
\Bigg(
10^2
\left(
\frac{1122}{2!\,2!}
+
\frac{1112}{3!\,1!}
\right)
+
33
\left(
\frac{1}{2!\,2!}
+
\frac{1}{3!\,1!}
\right)
\Bigg).
\end{aligned}
$$

Now observe:

- The first parenthesis is exactly $B[t]$.
- The second parenthesis is the same sum **without the numeric values**.
  This motivates defining the *weight*

$$
W[t]
=
\frac{1}{2!\,2!}
+
\frac{1}{3!\,1!}.
$$

With this notation, the update becomes

$$
\boxed{
B[t+2]
=
\frac{1}{2!}
\left(
10^2\,B[t] + 33\,W[t]
\right).
}
$$

In base $b$, appending $c$ copies of digit $d$:

- shifts old values by $b^c$,
- adds the suffix
  $$
  d\,(1+b+\dots+b^{c-1}) = d\,\frac{b^c-1}{b-1},
  $$
- and introduces the weight factor $1/c!$.

Thus the general update rule is

$$
\boxed{
B[t+c]
\;\leftarrow\;
B[t+c] + 
\left(
B[t]\cdot b^c
+
W[t]\cdot d\cdot\frac{b^c-1}{b-1}
\right)\cdot \frac{1}{c!}.
}
$$

This illustrates precisely why the auxiliary array $W[t]$ is needed: the constant suffix contribution must be multiplied by the **total weight** of all patterns of length $t$, not by their individual numeric values.

**</ End of Example>**


*2) Process digits incrementally*

Think of the pattern $(c_1,\dots,c_{b-1})$ as being constructed digit-by-digit. When we are currently processing digit $d$ (where $d\in\{1,\dots,b-1\}$), we choose how many times it appears: $c \ge 0$.

This choice contributes a factor $\frac{1}{c!}$ to the weight. That is why the factorials are so convenient: they make the contribution of each
digit independent and multiplicative.

Suppose we have already processed digits $1,2,\dots,d-1$, and we have aggregated:

- $W[t]$: total weight for patterns of length $t$ using only digits $< d$,
- $B[t]$: total weighted value sum for the same patterns.

Now we extend these patterns by appending digit $d$ exactly $c$ times.


*3) How does appending digit $d$ change the numeric value?*

Let $x$ be the existing sorted digit string (using digits $< d$) of length $t$. If we append $c$ copies of digit $d$, the new sorted string is:

$$
x \;\Vert\; \underbrace{dd\cdots d}_{c\text{ times}}.
$$

Interpreting strings as base-$b$ integers:

- Appending $c$ digits multiplies the old value by $b^c$.
- Then we add the value of the suffix consisting of $c$ copies of digit $d$.

That suffix has value:

$$
d \cdot (b^{c-1} + b^{c-2} + \cdots + b + 1)
=
d \cdot \frac{b^c - 1}{b - 1}.
$$

Let us denote the repunit-like factor

$$
R_c := 1 + b + b^2 + \cdots + b^{c-1} = \frac{b^c - 1}{b - 1}.
$$

Then the update rule for a single pattern is:

$$
f_{\text{new}} = f_{\text{old}} \cdot b^c + d \cdot R_c.
$$


*4) Translate this into DP updates for $W$ and $B$*

When we add $c$ copies of digit $d$:

- The total length increases from $t$ to $t+c$.
- Every existing pattern of length $t$ contributes a weight factor $\frac{1}{c!}$.

So the weight update is:

$$
W_{\text{new}}[t+c] \;\leftarrow\; W_{\text{new}}[t+c] +  W_{\text{old}}[t]\cdot \frac{1}{c!}.
$$

For the value-weighted sum, we take the old aggregated sum $B_{\text{old}}[t]$ and apply the value transform:

- The part coming from old values gets multiplied by $b^c$.
- The part coming from the new suffix is $d\cdot R_c$, multiplied by the total weight
  of old patterns $W_{\text{old}}[t]$.

So:

$$
B_{\text{new}}[t+c]
\;\leftarrow\; B_{\text{new}}[t+c] +
\left( B_{\text{old}}[t]\cdot b^c \;+\; W_{\text{old}}[t]\cdot d\cdot R_c \right)\cdot \frac{1}{c!}.
$$

Initialization is:

$$
W[0]=1,\quad B[0]=0,
$$

representing the empty pattern of length $0$ with weight $1$.

After processing all digits $d=1,\dots,b-1$, the array entry $B[k]$ equals the desired
$B(k)$.


*5) Final assembly: $S(n)=\sum_{k=1}^n k\cdot A(k)\cdot B(k)$*

Separately, we define

$$
A(k) := \sum_{m=k}^{n} \frac{(m-1)!}{(m-k)!}.
$$

Then, from the earlier derivation,

$$
S(n)
=
\sum_{k=1}^{n}
k \cdot A(k) \cdot B(k).
$$

So the entire computation reduces to:

1. compute $A(1),\dots,A(n)$ (length-only factor),
2. compute $B(1),\dots,B(n)$ via the digit-by-digit DP above,
3. combine them in the final sum.

This avoids explicit enumeration of all $(c_1,\dots,c_{b-1})$ patterns while still
producing exactly the same $B(k)$ values.

```python
from __future__ import annotations

import math
from fractions import Fraction


def S(n: int, base: int) -> int:
    """Compute S(n) exactly using the A(k) / B(k) decomposition (rational DP).

    We use the identity

        S(n) = sum_{k=1..n}  k * A(k) * B(k),

    where

        A(k) = sum_{m=k..n} (m-1)! / (m-k)!,

    and B(k) is the weighted sum over all digit-multiplicity patterns
    (c_1, ..., c_{base-1}) with sum c_i = k:

        B(k) = sum_{c_1+...+c_{base-1}=k}  f(c_1,...,c_{base-1}) / prod_i c_i!.

    Instead of enumerating all (c_1,...,c_{base-1}), we compute B(k) via a DP
    over digits d = 1..base-1, maintaining two arrays:

      - W[t] = sum_{patterns of length t}  1 / prod c_i!
      - B[t] = sum_{patterns of length t}  f(pattern) / prod c_i!

    Both W and B are Fractions to keep the derivation exact.
    """
    # -------------------------------------------------------------------------
    # 1) Compute A[k] for k=1..n:
    #
    #    A(k) = sum_{m=k..n} (m-1)! / (m-k)!
    #
    # This quantity depends only on lengths, not on digit composition.
    # We store A[0]=0 unused for convenience.
    # -------------------------------------------------------------------------
    A: list[Fraction] = [Fraction(0, 1)] * (n + 1)

    for k in range(1, n + 1):
        # Sum over total lengths m (total digits, including zeros).
        # Note: (m-1)!/(m-k)! is an integer, but we keep Fraction for uniformity.
        for m in range(k, n + 1):
            A[k] += Fraction(math.factorial(m - 1), math.factorial(m - k))

    # -------------------------------------------------------------------------
    # 2) Compute B[k] for k=0..n via DP over digits d=1..base-1.
    #
    # DP state after processing digits 1..(d-1):
    #   W[t] = sum_{c_1+...+c_{d-1}=t}  1 / (c_1! ... c_{d-1}!)
    #   B[t] = sum_{c_1+...+c_{d-1}=t}  f(c_1,...,c_{d-1}) / (c_1! ... c_{d-1}!)
    #
    # Initialization (no digits chosen yet):
    #   - empty pattern of length 0 has weight 1
    #   - its value-sum is 0 (there is no number yet)
    # -------------------------------------------------------------------------
    W: list[Fraction] = [Fraction(0, 1)] * (n + 1)
    B: list[Fraction] = [Fraction(0, 1)] * (n + 1)
    W[0] = Fraction(1, 1)

    # Process each possible non-zero digit exactly once.
    for d in range(1, base):
        newW: list[Fraction] = [Fraction(0, 1)] * (n + 1)
        newB: list[Fraction] = [Fraction(0, 1)] * (n + 1)

        # We may append digit d exactly c times, where c >= 0.
        # If current non-zero length is t, then t+c must be <= n.
        for t in range(0, n + 1):
            if W[t] == 0 and B[t] == 0:
                # Small skip: no patterns of this length exist in the current DP state.
                continue

            for c in range(0, n - t + 1):
                # Each digit multiplicity contributes the factor 1/c!
                coef = Fraction(1, math.factorial(c))

                # Appending c digits to the right in base `base` multiplies by base^c.
                p_base = base**c

                # The suffix consisting of c copies of digit d has value:
                #   d * (1 + base + base^2 + ... + base^(c-1))
                # The geometric sum factor is:
                #   rep = (base^c - 1) / (base - 1)
                # Example (base 16): c=2 => rep = 1 + 16 = 0x11
                rep = (p_base - 1) // (base - 1)

                # Weight update:
                #   W_new[t+c] += W[t] * (1/c!)
                newW[t + c] += W[t] * coef

                # Value-sum update:
                #
                # For each old pattern/value x of length t:
                #   new_value = x * base^c + d * rep
                #
                # Aggregating over all patterns of length t:
                #   B[t] aggregates sum(x / weight_den)
                #   W[t] aggregates sum(1 / weight_den)
                #
                # Thus:
                #   B_new[t+c] += (B[t] * base^c + W[t] * d * rep) * (1/c!)
                newB[t + c] += (B[t] * p_base + W[t] * d * rep) * coef

        W, B = newW, newB

    # Now B[k] equals the desired B(k) after processing digits 1..base-1.

    # -------------------------------------------------------------------------
    # 3) Assemble S(n) = sum_{k=1..n} k * A[k] * B[k]
    # -------------------------------------------------------------------------
    total = Fraction(0, 1)
    for k in range(1, n + 1):
        total += k * A[k] * B[k]

    # The math guarantees the result is an integer.
    return int(total)


# Example usage: compute S(n) for hexadecimal numbers
# Example usage: compute S(n) for hexadecimal numbers
for n_test in (3, 5, 0xA, 0xAA):
    value = S(n_test, base=16)
    print(f"S(0x{format_answer(n_test, base)}) in base 16 = 0x{format_answer(value, base)}")
```

Output:

```text
S(0x3) in base 16 = 0x4077C0
S(0x5) in base 16 = 0x286D8F92C0
S(0xA) in base 16 = 0x12C698E48B4FC2A01358
S(0xAA) in base 16 = 0x26F887F38798EE82871999ED23144B390724614ECAF1D11BF47A1ECBE23E8CE07533AFFEACBFE440346B4335A5A30FCDE3A3DB92E838CB57FE2B4FA6795EA57ABD4FCFB80DB43E6001A7153FD484ACD473AFCDF93BEA247F908BE8B05F836C118486D59BB38D2349DAE0CAE1D7040F1B27CE2D2E45F0520D9EF0285FDF9BA9CBF46A2420B1DA749B761D2A9EFB8EC37F04D580D1210F929386720E61EF28351655758C184BF42958
```

This is already good enough to secure the silver 🥈 medal (although the code does run a few seconds already).


<br>

---

### Eliminating Fractions: Scaling away the Factorial Denominators

The DP we derived for $B(k)$ used rational weights of the form $1/c!$, which naturally
led to `Fraction` arithmetic:

- $W[t]$ aggregated $\sum 1/\prod c_i!$ over all patterns of length $t$,
- $B[t]$ aggregated $\sum f(\mathbf c)/\prod c_i!$ over the same patterns.

This is mathematically clean but computationally expensive, because `Fraction` objects constantly normalize numerators/denominators via gcd. The key observation is that all denominators are factorials and therefore we can remove them by a global scaling.


*1) Define integer-scaled DP arrays*

Define scaled (integer) versions of the DP states by multiplying by $t!$:

$$
\widetilde{W}[t] := t!\,W[t],
\qquad
\widetilde{B}[t] := t!\,B[t].
$$

Intuition:

- Every term contributing to $W[t]$ looks like $1/\prod c_i!$.
- Multiplying by $t!$ converts this into the multinomial coefficient
  $t!/\prod c_i!$, which is an integer.
- Same for $B[t]$: each value gets multiplied by the same integer weight.

So $\widetilde{W}[t]$ and $\widetilde{B}[t]$ can be maintained using pure integers.

Initialization becomes

$$
\begin{align*}
\widetilde{W}[0] = 1 \qquad W[0] = 1, \\
\widetilde{B}[0] = 0 \qquad B[0] = 0.
\end{align*}
$$



*2) Start from the rational DP update*

From the previous derivation, when processing digit $d$ and choosing multiplicity $c$,
we had for each $t$:

$$
W_{\text{new}}[t+c] \;\leftarrow \; W_{\text{new}}[t+c] + W[t]\cdot \frac{1}{c!},
$$

and

$$
B_{\text{new}}[t+c]
\;\leftarrow\; B_{\text{new}}[t+c] + 
\left(B[t]\cdot b^c + W[t]\cdot d\cdot R_c \right)\cdot \frac{1}{c!},
\qquad
R_c := \frac{b^c-1}{b-1}.
$$

Now multiply the whole update for index $t+c$ by $(t+c)!$ to convert it to the scaled variables.


*3) Derive the integer coefficient*

For the weight update:

$$
\widetilde{W}_{\text{new}}[t+c] := (t+c)!\,W_{\text{new}}[t+c].
$$

$$
\widetilde{W}_{\text{new}}[t+c]
\;\leftarrow\;
\widetilde{W}_{\text{new}}[t+c]
\;+\;
(t+c)!\,W[t]\cdot \frac{1}{c!}.
$$


Substitute $W[t] = \widetilde{W}[t]/t!$ (since our sequence gets longer we have to correct the factor by dividing through $t!$ and multiplying with $(t+c)!$):

$$
\begin{align}
\widetilde{W}_{\text{new}}[t+c]
\; \leftarrow\; \widetilde{W}_{\text{new}}[t+c] +
(t+c)!\,\frac{\widetilde{W}[t]}{t!}\cdot \frac{1}{c!}
=
\widetilde{W}[t]\cdot \frac{(t+c)!}{t!\,c!}.
\end{align}
$$

But

$$
\frac{(t+c)!}{t!\,c!} = \binom{t+c}{c}.
$$

So the scaled weight update is:

$$
\boxed{
\widetilde{W}_{\text{new}}[t+c]
\; \leftarrow\; \widetilde{W}_{\text{new}}[t+c] + 
\widetilde{W}[t]\cdot \binom{t+c}{c}.
}
$$


*4) Derive the integer update for $\widetilde{B}$*

Start from the rational update and multiply by $(t+c)!$:

$$
\widetilde{B}_{\text{new}}[t+c]
\; \leftarrow \; \widetilde{B}_{\text{new}}[t+c] + 
(t+c)!\left(B[t]\cdot b^c + W[t]\cdot d\cdot R_c\right)\frac{1}{c!}.
$$

Substitute $B[t]=\widetilde{B}[t]/t!$ and $W[t]=\widetilde{W}[t]/t!$:

$$
\widetilde{B}_{\text{new}}[t+c]
\; \leftarrow \; \widetilde{B}_{\text{new}}[t+c] + 
\frac{(t+c)!}{t!\,c!}\left(\widetilde{B}[t]\cdot b^c + \widetilde{W}[t]\cdot d\cdot R_c\right).
$$

Again the prefactor is $\binom{t+c}{c}$, so:

$$
\boxed{
\widetilde{B}_{\text{new}}[t+c]
\; \leftarrow \; \widetilde{B}_{\text{new}}[t+c] + 
\left(\widetilde{B}[t]\cdot b^c + \widetilde{W}[t]\cdot d\cdot R_c\right)\binom{t+c}{c}.
}
$$

*5) Recovering $B(k)$ and assembling $S(n)$*

By definition,

$$
\widetilde{B}[k] = k!\,B(k).
$$

So whenever the final formula requires $B(k)$, we can use

$$
B(k) = \frac{\widetilde{B}[k]}{k!}.
$$

The overall decomposition remains

$$
S(n) = \sum_{k=1}^{n} k\cdot A(k)\cdot B(k),
$$

so substituting $B(k)=\widetilde{B}[k]/k!$ yields the integer-friendly form

$$
\boxed{
S(n) = \sum_{k=1}^{n} k\cdot A(k)\cdot \frac{\widetilde{B}[k]}{k!}.
}
$$

This is exactly why the last line in the reference code divides by `factorial(k)`.


*Why this is faster*

- All intermediate DP values are integers (or later, integers modulo $M$).
- We avoid gcd reductions and normalization inherent to fractions (`Fraction` class in Python 3).
- The only "division" left is by $k!$ at the very end, which can be handled either
  exactly (since the expression is guaranteed to be an integer) or, for the modular
  version, via modular inverses.

This turns the elegant but slow rational DP into a practical integer DP that is
ready to be upgraded to the final modulo-$M$ computation.


```python
from __future__ import annotations

import math


def S(n: int, base: int) -> int:
    """Compute S(n) exactly using the integer-scaled DP (no Fractions).

    We use the decomposition
        S(n) = sum_{k=1..n} k * A(k) * B(k),

    but compute B(k) via scaled integers:
        B_scaled[k] = k! * B(k).

    DP meaning (after processing digits 1..d):
      - W_scaled[t] = t! * sum_{patterns length t} 1 / prod c_i!
      - B_scaled[t] = t! * sum_{patterns length t} f(pattern) / prod c_i!

    The digit-extension update (append digit d exactly c times) becomes integer-only:
        coef = C(t+c, c)
        W_scaled_new[t+c] += W_scaled[t] * coef
        B_scaled_new[t+c] += (B_scaled[t] * base^c + W_scaled[t] * d * rep(c)) * coef

    where rep(c) = (base^c - 1)/(base - 1) = 1 + base + ... + base^(c-1).

    Finally, since B_scaled[k] = k! * B(k), we have:
        S(n) = sum_{k=1..n} k * A(k) * B_scaled[k] / k!

    The division is exact by construction.
    """
    # -------------------------------------------------------------------------
    # 1) Precompute A[k] = sum_{m=k..n} (m-1)!/(m-k)!   (pure integers)
    # -------------------------------------------------------------------------
    A = [0] * (n + 1)
    for k in range(1, n + 1):
        # (m-1)!/(m-k)! = (m-k)(m-k+1)...(m-1) is an integer rising product of length (k-1).
        for m in range(k, n + 1):
            A[k] += math.factorial(m - 1) // math.factorial(m - k)

    # -------------------------------------------------------------------------
    # 2) Compute scaled B via DP over digits d=1..base-1.
    #
    # W_scaled[0]=1 represents the empty pattern (length 0) with weight 1.
    # B_scaled[0]=0 because the empty pattern has value 0.
    # -------------------------------------------------------------------------
    W_scaled = [0] * (n + 1)
    B_scaled = [0] * (n + 1)
    W_scaled[0] = 1

    for d in range(1, base):  # digits 1..9 (base10), 1..7 (base8), 1..15 (base16), ...
        newW = [0] * (n + 1)
        newB = [0] * (n + 1)

        # For each existing length t, we may add c copies of digit d, keeping total <= n.
        for t in range(0, n + 1):
            if W_scaled[t] == 0 and B_scaled[t] == 0:
                continue

            for c in range(0, n - t + 1):
                # coef = (t+c)!/(t! c!) = C(t+c, c)
                # This is exactly the scaling factor that removes the 1/c! fractions
                # after we multiply everything by (t+c)!.
                coef = math.comb(t + c, c)

                # Appending c digits shifts old values by base^c.
                p_base = base**c

                # Value of suffix "ddd...d" (c times) in base `base`:
                # d * (1 + base + ... + base^(c-1)) = d * ((base^c - 1)/(base - 1))
                rep = (p_base - 1) // (base - 1)

                # Update weights (scaled): only depends on how many patterns we had at length t.
                newW[t + c] += W_scaled[t] * coef

                # Update value-sums (scaled):
                # - old aggregated values shift by base^c
                # - plus the suffix contribution, scaled by the total weight mass W_scaled[t]
                newB[t + c] += (B_scaled[t] * p_base + W_scaled[t] * d * rep) * coef

        W_scaled, B_scaled = newW, newB

    # -------------------------------------------------------------------------
    # 3) Assemble S(n) using B_scaled[k] = k! * B(k)
    # -------------------------------------------------------------------------
    ans = 0
    for k in range(1, n + 1):
        ans += k * A[k] * B_scaled[k] // math.factorial(k)

    return ans


# Example usage: compute S(n) for hexadecimal numbers
for n_test in (3, 5, 0xA, 0xAA):
    value = S(n_test, base=16)
    print(f"S(0x{format_answer(n_test, base)}) in base 16 = 0x{format_answer(value, base)}")
```

Also here, we get the same output as before (but faster):

```text
S(0x3) in base 16 = 0x4077C0
S(0x5) in base 16 = 0x286D8F92C0
S(0xA) in base 16 = 0x12C698E48B4FC2A01358
S(0xAA) in base 16 = 0x26F887F38798EE82871999ED23144B390724614ECAF1D11BF47A1ECBE23E8CE07533AFFEACBFE440346B4335A5A30FCDE3A3DB92E838CB57FE2B4FA6795EA57ABD4FCFB80DB43E6001A7153FD484ACD473AFCDF93BEA247F908BE8B05F836C118486D59BB38D2349DAE0CAE1D7040F1B27CE2D2E45F0520D9EF0285FDF9BA9CBF46A2420B1DA749B761D2A9EFB8EC37F04D580D1210F929386720E61EF28351655758C184BF42958
```

Also, let us compute the values for $S(n) \bmod \mbox{0x1FFFFFFFFFFFFFFF}$:

```python
mod = 0x1FFFFFFFFFFFFFFF
for n_test in (3, 5, 0xA, 0xAA):
    value = S(n_test, base=16) % mod
    print(f"S(0x{format_answer(n_test, base)}) in base 16 = 0x{format_answer(value, base)}")
```

Result:

```text
S(0x3) in base 16 = 0x4077C0
S(0x5) in base 16 = 0x286D8F92C0
S(0xA) in base 16 = 0x18E48B4FC2A0A98C
S(0xAA) in base 16 = 0x6CFD29A04AFAB77
```

<br>

---

### Modular Solution – Part I: Using Modular Inverses (Intentionally Unoptimized)

Up to this point, we have derived exact formulas for  

$$
S(n) = \sum_{k=1}^{n} k \cdot A(k) \cdot B(k),
$$

where

$$
A(k) = \sum_{m=k}^{n} \frac{(m-1)!}{(m-k)!}
\quad\text{and}\quad
B(k) = \sum_{\substack{c_1+\cdots+c_{b-1}=k}} \frac{f(c_1,\dots,c_{b-1})}{\prod_{i=1}^{b-1} c_i!}.
$$

All previous formulations were exact (integer or rational).  
However, for the actual problem we only need the result modulo a fixed integer $M = \mbox{0x1FFFFFFFFFFFFFFF}$.   This allows us to switch to modular arithmetic and drastically reduce both memory usage and runtime.

*1. Replacing division by modular inverses*

In modular arithmetic, division by a number $x$ is replaced by multiplication with its modular inverse $x^{-1}$, defined by

$$
x \cdot x^{-1} \equiv 1 \pmod{M}.
$$

If $M$ is prime, then every $x \not\equiv 0 \pmod{M}$ has an inverse, and Fermat’s little theorem gives the explicit formula
$$
x^{-1} \equiv x^{M-2} \pmod{M}.
$$

This is exactly what we need, because all denominators in our formulas are of the form
- factorials $c!$ and $(m-k)!$,
- the constant factor $b-1$,

and for a prime modulus $M > n$, none of these are divisible by $M$.


*2. Modular form of $A(k)$*

The quantity

$$
A(k) = \sum_{m=k}^{n} \frac{(m-1)!}{(m-k)!}
$$

contains only factorial ratios.

Modulo $M$, we compute each term as

$$
\frac{(m-1)!}{(m-k)!}
\equiv
(m-1)! \cdot \bigl((m-k)!\bigr)^{-1}
\pmod{M}.
$$

Thus $A(k)$ can be accumulated term-by-term using modular factorials and modular
inverses.

*3. Modular DP for $B(k)$*

Recall the digit-based DP for computing $B(k)$, which tracks two sequences:
- $W[t]$: total "weight mass" of patterns of length $t$,
- $B[t]$: weighted sum of values of those patterns.

In the exact (rational) formulation, each extension by $c$ copies of a digit introduces a factor $1/c!$. Modulo $M$, this becomes multiplication by the modular inverse $(c!)^{-1}$.

When appending $c$ copies of digit $d$, the numeric transformation is

$$
x \longmapsto x \cdot b^c + d \cdot \frac{b^c - 1}{b - 1}.
$$

Both divisions are handled via modular inverses:

$$
\frac{1}{c!} \equiv (c!)^{-1} \pmod{M},
\qquad
\frac{1}{b-1} \equiv (b-1)^{-1} \pmod{M}.
$$

As a result, the DP updates for $W$ and $B$ carry over unchanged in structure;
only every division is replaced by a multiplication with the corresponding inverse
modulo $M$.


*4. Final modular assembly*

Once $A(k)$ and $B(k)$ have been computed modulo $M$, the final sum is
assembled as

$$
S(n) \equiv \sum_{k=1}^{n} k \cdot A(k) \cdot B(k) \pmod{M}.
$$

All operations are now modular, and no exact rational arithmetic is needed.



*5. Validity of the approach*

This modular formulation is mathematically sound provided that

- $M$ is prime, and
- $M > n$.

Under these conditions, every factorial and constant appearing in a denominator has a modular inverse, so all divisions are well-defined. For the given problem, the modulus $\mbox{0x1FFFFFFFFFFFFFFF}$ is prime (a so-called [Mersenne prime](https://en.wikipedia.org/wiki/Mersenne_prime) with the value $2^{61}-1$) and much larger than $n = 18$, so the modular approach applies without restriction.

At this point, we already have a fully correct modular solution.  In the next section, we will refine it further by reducing redundant computations and improving performance, leading to the final optimized implementation.

```python
from __future__ import annotations

import math
from sympy import totient


def S(n: int, base: int, mod: int) -> int:
    """Compute S(n) modulo `mod` using the modular A(k)/B(k) decomposition.

    This is the modular analogue of the integer-scaled DP:

        S(n) = sum_{k=1..n} k * A(k) * B(k)  (mod mod)

    where
        A(k) = sum_{m=k..n} (m-1)! / (m-k)!,
    and B(k) is obtained via a digit-DP over digits 1..(base-1).

    Modular inverses are computed using Euler's theorem:
        a^{-1} ≡ a^{φ(mod)-1} (mod mod),
    which requires gcd(a, mod) = 1 for all inverted values.
    """

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    phi_mod = int(totient(mod))

    def inv_mod(a: int) -> int:
        """Modular inverse using Euler's theorem (assumes gcd(a, mod) = 1)."""
        return pow(a % mod, phi_mod - 1, mod)

    def factorial_mod(m: int) -> int:
        """Compute m! modulo mod (naive O(m))."""
        acc = 1
        for i in range(1, m + 1):
            acc = (acc * i) % mod
        return acc

    # -------------------------------------------------------------------------
    # 1) Compute A(k) = sum_{m=k..n} (m-1)! / (m-k)!   (mod mod)
    # -------------------------------------------------------------------------
    A = [0] * (n + 1)

    for k in range(1, n + 1):
        for m in range(k, n + 1):
            numerator = factorial_mod(m - 1)
            denominator = factorial_mod(m - k)
            A[k] = (A[k] + numerator * inv_mod(denominator)) % mod

    # -------------------------------------------------------------------------
    # 2) Compute B(k) via digit DP (fraction-style, but done modulo mod)
    #
    # W[t] = sum of weights for patterns of length t
    # B[t] = weighted sum of values for patterns of length t
    # -------------------------------------------------------------------------
    W = [0] * (n + 1)
    B = [0] * (n + 1)

    W[0] = 1  # empty pattern has weight 1
    inv_base_minus_1 = inv_mod(base - 1)

    for d in range(1, base):  # digits 1..(base-1)
        newW = [0] * (n + 1)
        newB = [0] * (n + 1)

        for t in range(0, n + 1):
            if W[t] == 0 and B[t] == 0:
                continue

            for c in range(0, n - t + 1):
                # coef = 1 / c!  (mod mod)
                coef = inv_mod(factorial_mod(c))

                # base^c mod mod (shift old values)
                p_base = pow(base, c, mod)

                # rep(c) = (base^c - 1) / (base - 1)
                rep = (p_base - 1) * inv_base_minus_1 % mod

                # Update weights
                newW[t + c] = (newW[t + c] + W[t] * coef) % mod

                # Update value sums
                shifted_old = (B[t] * p_base) % mod
                suffix_part = (W[t] * d * rep) % mod
                newB[t + c] = (newB[t + c] + (shifted_old + suffix_part) * coef) % mod

        W, B = newW, newB

    # -------------------------------------------------------------------------
    # 3) Assemble final answer
    # -------------------------------------------------------------------------
    ans = 0
    for k in range(1, n + 1):
        ans = (ans + (k * A[k] % mod) * B[k]) % mod

    return ans


# Example usage: compute S(n) for hexadecimal numbers
base = 16
mod = 0x1FFFFFFFFFFFFFFF
for n_test in (3, 5, 0xA, 0xAA):
    value = S(n_test, base=base, mod=mod)
    print(f"S(0x{format_answer(n_test, base)}) in base 16 = 0x{format_answer(value, base)}")
```

If we compare the output to the above result (mod 0x1FFFFFFFFFFFFFFF) we see that our modular approach is correct. However, it is still fairly slow. In fact, it is slower than the approach above where we eliminated the fractions.

Output:

```text
S(0x3) in base 16 = 0x4077C0
S(0x5) in base 16 = 0x286D8F92C0
S(0xA) in base 16 = 0x18E48B4FC2A0A98C
S(0xAA) in base 16 = 0x6CFD29A04AFAB77
```







---

<br>

### Modular Solution – Part II: Practical Optimizations (Caching & Precomputation)

The modular DP from Part I is already mathematically clean, but a direct implementation can still be slow if we repeatedly recompute the same building blocks inside the inner loops. The biggest cost drivers are:

- factorials $c! \bmod M$,
- modular inverses $(c!)^{-1} \bmod M$,
- powers $b^c \bmod M$,
- and the geometric sum $$R_c = \frac{b^c-1}{b-1} \pmod M.$$

Since $n$ is fixed (and small compared to $M$), all of these quantities depend only on
$c \in \{0,\dots,n\}$ and can be precomputed once.

Below is a summary of the optimizations performed.


*1) Precompute factorials once: $i! \bmod M$*

Instead of recomputing factorials in $O(i)$ repeatedly, we precompute the array

$$
\texttt{fact}[i] \equiv i! \pmod M
\qquad (0 \le i \le n)
$$

via the recurrence

$$
\texttt{fact}[0]=1,\qquad \texttt{fact}[i]=\texttt{fact}[i-1]\cdot i \pmod M.
$$

This turns many factorial evaluations from "loop work" into an $O(1)$ lookup.



*2) Precompute inverse factorials in $O(n)$ (only one expensive exponentiation)*

The naive modular approach computed $(c!)^{-1}$ by an exponentiation for every $c$.
Instead, we compute all inverse factorials with only **one** exponentiation.

First compute

$$
\texttt{inv_fact}[n] \equiv (n!)^{-1} \equiv (n!)^{M-2} \pmod M
$$

(using Fermat since $M$ is prime), then use the backward recurrence

$$
\texttt{inv_fact}[i-1] = \texttt{inv_fact}[i]\cdot i \pmod M.
$$

This works because

$$
(i-1)!^{-1} = (i!)^{-1}\cdot i.
$$

As a result, the frequent coefficient
$$
\frac{1}{c!} \pmod M
$$
becomes a simple lookup $\texttt{inv_fact}[c]$.

*3) Precompute $b^c \bmod M$ for all $c \le n$*

Inside the DP, we repeatedly need the shift factor $b^c$.
We precompute

$$
\texttt{pow_base}[c] \equiv b^c \pmod M
$$

using

$$
\texttt{pow_base}[0]=1,\qquad \texttt{pow_base}[c]=\texttt{pow_base}[c-1]\cdot b \pmod M.
$$

This removes all repeated modular exponentiations from the inner loop.


*4) Precompute the geometric repunit factor $R_c$*

The appended suffix of $c$ copies of digit $d$ uses

$$
R_c = 1 + b + \cdots + b^{c-1} = \frac{b^c-1}{b-1}.
$$

We compute $(b-1)^{-1} \bmod M$ once:

$$
(b-1)^{-1} \equiv (b-1)^{M-2} \pmod M,
$$

and then precompute

$$
\texttt{rep}[c] \equiv (b^c-1)\cdot (b-1)^{-1} \pmod M.
$$

So the suffix contribution in the DP,
$$
d\cdot R_c,
$$
becomes a fast lookup-and-multiply.


*5) Reuse cached values in the DP inner loops*

After precomputations, the DP update for each $(t,c)$ only uses:

- $\texttt{inv_fact}[c]$ for $1/c!$,
- $\texttt{pow_base}[c]$ for $b^c$,
- $\texttt{rep}[c]$ for $(b^c-1)/(b-1)$,

and does only $O(1)$ modular multiplications/additions.

This preserves the same DP logic, but removes the "hidden" heavy costs
(exponentiation, factorial loops, repeated inverses) from the hot path.


*6) Faster computation of $A(k)$ via cached factorials*

Similarly,

$$
A(k) = \sum_{m=k}^{n} \frac{(m-1)!}{(m-k)!}
\equiv
\sum_{m=k}^{n} (m-1)!\cdot ((m-k)!)^{-1} \pmod M
$$

becomes

$$
A(k) \equiv \sum_{m=k}^{n} \texttt{fact}[m-1]\cdot \texttt{inv_fact}[m-k] \pmod M,
$$

again turning factorial and inverse computations into array lookups.

All optimizations are "mechanical" (precompute and reuse), but together they remove
nearly all expensive operations from the inner loops.

- no repeated factorial loops,
- no repeated modular exponentiation inside the DP,
- no repeated modular inverse computation per iteration,
- only cheap modular arithmetic in the hot path.


```python
from __future__ import annotations

from sympy import totient


def S(n: int, base: int, mod: int) -> int:
    """Compute S(n) modulo `mod` using the modular A(k)/B(k) decomposition.

    Same logic as above version, but faster by caching:
      - factorials (0!..n!) modulo mod
      - inverse factorials via pow(fact[n], phi-1) and downward recurrence
      - powers base^c modulo mod for c=0..n
      - rep(c) = (base^c - 1)/(base-1) modulo mod for c=0..n

    NOTE: This assumes all inverses exist (e.g. mod is prime and mod > n, or at
    least gcd(denominator, mod)=1 for all denominators we invert).
    """
    phi_mod = int(totient(mod))

    # ---------------------------------------------------------------------
    # Precompute factorials and inverse factorials up to n
    # ---------------------------------------------------------------------
    fact = [1] * (n + 1)      # fact[i] = i! mod mod
    for i in range(1, n + 1):
        fact[i] = (fact[i - 1] * i) % mod

    # inv_fact[i] = (i!)^{-1} mod mod, computed in O(n) using one pow() + recurrence
    inv_fact = [1] * (n + 1)
    inv_fact[n] = pow(fact[n], phi_mod - 1, mod)  # (n!)^{-1}
    for i in range(n, 0, -1):
        # (i-1)!^{-1} = i!^{-1} * i
        inv_fact[i - 1] = (inv_fact[i] * i) % mod

    # Also cache (base-1)^{-1} mod mod, used in rep(c)
    inv_base_minus_1 = pow(base - 1, phi_mod - 1, mod)

    # ---------------------------------------------------------------------
    # Precompute powers and rep(c) for c=0..n
    # ---------------------------------------------------------------------
    pow_base = [1] * (n + 1)  # pow_base[c] = base^c mod mod
    for c in range(1, n + 1):
        pow_base[c] = (pow_base[c - 1] * base) % mod

    # rep[c] = (base^c - 1)/(base-1) mod mod
    rep = [0] * (n + 1)
    for c in range(0, n + 1):
        rep[c] = (pow_base[c] - 1) * inv_base_minus_1 % mod

    # coef[c] = 1/c! mod mod  (used very frequently in the DP)
    inv_c_fact = inv_fact  # alias to make intent clearer

    # ---------------------------------------------------------------------
    # 1) Compute A(k) = sum_{m=k..n} (m-1)! / (m-k)!   (mod mod)
    #    => (m-1)! * ((m-k)!)^{-1}
    # ---------------------------------------------------------------------
    A = [0] * (n + 1)
    for k in range(1, n + 1):
        acc = 0
        for m in range(k, n + 1):
            acc = (acc + fact[m - 1] * inv_fact[m - k]) % mod
        A[k] = acc

    # ---------------------------------------------------------------------
    # 2) Compute B(k) via digit DP (fraction-style, modulo arithmetic)
    # ---------------------------------------------------------------------
    W = [0] * (n + 1)
    B = [0] * (n + 1)
    W[0] = 1

    for d in range(1, base):
        newW = [0] * (n + 1)
        newB = [0] * (n + 1)

        for t in range(0, n + 1):
            wt = W[t]
            bt = B[t]
            if wt == 0 and bt == 0:
                continue

            # Append c copies of digit d, with 0 <= c <= n-t
            for c in range(0, n - t + 1):
                coef = inv_c_fact[c]         # 1/c!
                p = pow_base[c]              # base^c
                r = rep[c]                   # (base^c - 1)/(base-1)

                idx = t + c

                # newW[idx] += W[t] * coef
                newW[idx] = (newW[idx] + wt * coef) % mod

                # newB[idx] += (B[t] * base^c + W[t] * d * rep(c)) * coef
                shifted_old = (bt * p) % mod
                suffix_part = (wt * d) % mod
                suffix_part = (suffix_part * r) % mod
                newB[idx] = (newB[idx] + (shifted_old + suffix_part) * coef) % mod

        W, B = newW, newB

    # ---------------------------------------------------------------------
    # 3) Assemble final answer: sum_{k=1..n} k * A[k] * B[k]
    # ---------------------------------------------------------------------
    ans = 0
    for k in range(1, n + 1):
        ans = (ans + (k * A[k] % mod) * B[k]) % mod

    return ans


# Example usage (kept close to yours)
base = 16
mod  = 0x1FFFFFFFFFFFFFFF
for n_test in (3, 5, 0xA, 0xAA):
     value = S(n_test, base=base, mod=mod)
     print(f"S(0x{format_answer(n_test, base)}) in base 16 = 0x{format_answer(value, base)}")
```

```text
S(0x3) in base 16 = 0x4077C0
S(0x5) in base 16 = 0x286D8F92C0
S(0xA) in base 16 = 0x18E48B4FC2A0A98C
S(0xAA) in base 16 = 0x6CFD29A04AFAB77
```

Also, now we can finally compute $S(0xAAA)$ (although it might also need a minute or so):

```python
value = S(0xAAA, base=base, mod=mod)
print(f"S(0xAAA) in base 16 = 0x{format_answer(value, base)}")
```

Output:

```text
S(0xAAA) in base 16 = 0x103528902352939
```

which finally earns us the Gold!!! 🥇 medal 🎉🥳!

While there is still some room for further optimization, we stop here, as the final solution already runs in feasible time. Additional speed-ups are left to the interested reader.