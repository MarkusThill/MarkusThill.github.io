---
layout: post
title: "Hexadecimal Digit Canon"
modified:
categories: [programming, algorithms, mathematics]
description: ""
tags: [combinatorics, discrete-math, algorithms, optimization, python]
thumbnail:
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-01-17T15:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
images:
  compare: false
  slider: false
---


All numbers in this problem are written in **base 16 (hexadecimal)**.  
The available digits are

$$
0,1,2,3,4,5,6,7,8,9,\text{A},\text{B},\text{C},\text{D},\text{E},\text{F},
$$

with $$\text{A}=10,\dots,\text{F}=15.$$

<br>
### The digit–canonical function

For any **positive hexadecimal integer** $$d$$, define the function $$f(d)$$ as follows:

1. Write $$d$$ in hexadecimal.
2. Sort its hexadecimal digits in **ascending order**.
3. Remove **all zero digits**.
4. Interpret the remaining digits again as a hexadecimal number.

<br>
### Examples

- **Example 1:**
  $$d = \texttt{3A04}$$. 
  Digits: $$3, A, 0, 4.$$ Sorted: $$0, 3, 4, A.$$  Remove zeros → $$3, 4, A$$.
  Result: $$f(\texttt{3A04}) = \texttt{34A}$$

- **Example 2**
  $$d = \texttt{F102}$$. Digits: $$F, 1, 0, 2$$. Sorted: $$0, 1, 2, F$$. Remove zeros → $$1, 2, F$$. Result: $$f(\texttt{F102}) = \texttt{12F}$$

- **Example 3**
  $$d = \texttt{800}$$. Digits: $$8, 0, 0$$. Sorted: $$0, 0, 8$$. Remove zeros → $$8$$. Result: $$f(\texttt{800}) = \texttt{8}$$

<br>
### The Cumulative Sum

Let $$S(n)$$ denote the sum of $$f(d)$$ over **all positive hexadecimal integers with at most $$n$$ hexadecimal digits**.

> **Important:**  
> All values of $$S(n)$$ are to be reported **in hexadecimal notation**.

For example:
- For $$n = 1$$, the result is
  $$
  S(1) = \boxed{\;\;\;\;\;\;\;\;\;\;\;\;}
  $$
- For $$n = 5$$, the result is
  $$
  S(5) = \boxed{\;\;\;\;\;\;\;\;\;\;\;\;}
  $$

*(These example values will be provided later.)*


<br>
## Challenge Levels 🏅

Compute $$S(n)$$ for the following four difficulty tiers:

| Tier | Value of $$n$$ | Your Result |
|------|----------------|-------------|
| 🟦 Warm-up | $$n = \;\_\_\_\_$$ | $$S(n) = \;\_\_\_\_$$ |
| 🥉 Bronze | $$n = \;\_\_\_\_$$ | $$S(n) = \;\_\_\_\_$$ |
| 🥈 Silver | $$n = \;\_\_\_\_$$ | $$S(n) = \;\_\_\_\_$$ |
| 🥇 Gold | $$n = \;\_\_\_\_$$ | $$S(n) \bmod 42F7A7A9 = \;\_\_\_\_$$ |

For the **gold** level, report your hexadecimal answer **modulo**

$$
\boxed{\texttt{42F7A7A9}}.
$$



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
n = 3              # compute S(n)

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

<br>
#### Counting Distinct Values (Naive Approach)

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
### Counting Distinct Values: Closed form

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


#### Special cases

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

## Computing $S(n)$ by enumerating distinct $f(d)$ values (and their multiplicities)

The definition of $f(d)$ is “sort digits ascending and remove zeros”.  
This means that many different numbers $d$ collapse to the same value $f(d)$: any
permutation of the non-zero digits and any placement of zeros produces the same
sorted, zero-free output.

The key idea of the algorithm is therefore:
> Do not iterate over all $d < b^n$.  Instead, iterate only over the distinct outputs $f(d)$ and count how many original numbers map to each of them.

This splits the problem into two conceptually clean parts.

### 1) Enumerating all distinct outputs $f(d)$

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


### 2) Counting how many numbers map to a fixed $f_d$

Fix one distinct output $f_d$ and let:

- $k$ be the number of non-zero digits in $f_d$,
- $c_i$ be the number of occurrences of digit $i$ in $f_d$ for $i=1,\dots,b-1$.

Now consider all original numbers $d$ that map to this fixed $f_d$.


#### (a) Permuting the non-zero digits

Ignoring zeros for the moment, the number of distinct permutations of the $k$
non-zero digits with multiplicities $(c_1,\dots,c_{b-1})$ is

$$
\frac{k!}{\prod_{i=1}^{b-1} c_i!}.
$$

This counts all ways the non-zero digits can appear relative to each other.

#### (b) Inserting zeros without creating leading zeros

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

---

### 3) Combining both contributions

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

This solution would already win us the Bronze 🥉 medal 🚀.


## TODO: Towards a faster solution: Write a better title here

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

If we ignore the “no leading zero” rule, then the number of distinct permutations
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
- the factor $1/\prod c_i!$ is the “multiset correction” coming from the multinomial counting,
- and $f(c_1,\dots,c_{b-1})$ is the actual numeric value contributed by that multiset.

So $B(k)$ is a weighted sum over all distinct outputs of $f(d)$ having exactly $k$
digits, capturing “how large those $f(d)$ values are on average” under the natural
weights induced by the multinomial coefficients.

In the next step we will show how to compute $B(k)$ efficiently without enumerating
all $(c_1,\dots,c_{b-1})$ patterns explicitly.

<br>

## Computing $B(k)$ efficiently (DP)

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
