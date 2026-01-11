---
layout: post
title: "Short Notes: Equal Partitions, Products, and Decimal Structure"
modified:
categories: [mathematics, algorithms, number-theory, programming]
description: "We study how splitting an integer into equal parts affects the maximum attainable product and how arithmetic properties of the optimum emerge. In particular, we relate a continuous optimization problem to the decimal structure of the resulting rational values."
tags: [optimization, number-theory, discrete-math, calculus, python, computational-math]
thumbnail: 
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
## Problem

Dividing a fixed quantity into equal parts often leads to interesting trade-offs between the size of each part and the number of factors involved. In this problem, we investigate how such a division influences not only the magnitude of a product, but also its arithmetic properties.

Let $$N \ge 2$$ be a positive integer.  
Suppose $$N$$ is divided into $$k$$ equal real parts, each of size $$r = N/k$$, so that

$$
N = \underbrace{r + r + \cdots + r}_{k\text{ times}}.
$$

Define the corresponding product

$$
P = r^k = \left(\frac{N}{k}\right)^k.
$$

For a fixed value of $$N$$, let $$M(N)$$ denote the **maximum possible value** of $$P$$ over all integers $$k \ge 1$$.


<br>
### Decimal Behavior

A rational number is said to have a **terminating decimal expansion** (also called being *finite in base 10*) if its decimal representation ends after finitely many digits.

For each $$N$$, the value $$M(N)$$ is a rational number, and its decimal expansion may or may not terminate.


<br>
### Non-Termination Weight

Define a function $$W(N)$$ as follows:

- If $$M(N)$$ has a terminating decimal expansion, set $$W(N) = 0$$.
- Otherwise, write $$M(N)$$ in lowest terms and let $$W(N)$$ be the **smallest prime divisor of its denominator**.


<br>
### Task

Compute

$$
\sum_{N = 5}^{10^6} W(N).
$$

<br>
## Solution Sketch
### Step 1: Set up the function

For a fixed positive integer $$N$$ and a (for now) real variable $$k>0$$, define

$$
f(k) = \left(\frac{N}{k}\right)^k.
$$

We will maximize $$f(k)$$ over real $$k$$ first, and later worry about the fact that in the original problem $$k$$ must be an integer.


<br>
### Step 2: Rewrite using exponentials and logarithms

A standard trick is to rewrite powers via the exponential function:

$$
a^k = e^{k\ln(a)}.
$$

So here,

$$
f(k)
= \left(\frac{N}{k}\right)^k
= e^{k\ln\left(\frac{N}{k}\right)}.
$$

Now expand the logarithm:

$$
\ln\left(\frac{N}{k}\right) = \ln(N) - \ln(k).
$$

Therefore,

$$
f(k) = e^{k(\ln N - \ln k)} = e^{k\ln N - k\ln k}.
$$

<br>
### Step 3: Differentiate step by step

Let

$$
g(k) = k\ln\left(\frac{N}{k}\right).
$$

Then

$$
f(k) = e^{g(k)}.
$$

By the chain rule,

$$
f'(k) = e^{g(k)} \cdot g'(k) = f(k)\,g'(k).
$$

So we only need $$g'(k)$$.


Then, start from the expanded form:

$$
g(k) = k(\ln N - \ln k) = k\ln N - k\ln k.
$$

Differentiate term by term:

1) Since $$\ln N$$ is constant (with respect to $$k$$),

$$
\frac{d}{dk}(k\ln N) = \ln N.
$$

2) For $$k\ln k$$ use the product rule:

$$
\frac{d}{dk}(k\ln k)
= \frac{d}{dk}(k)\cdot \ln k + k \cdot \frac{d}{dk}(\ln k)
= 1\cdot \ln k + k\cdot \frac{1}{k}
= \ln k + 1.
$$

Hence

$$
\frac{d}{dk}(-k\ln k) = -(\ln k + 1).
$$

Putting both pieces together:

$$
g'(k)
= \ln N - (\ln k + 1)
= \ln N - \ln k - 1.
$$

Then, plug back into $$f'(k)$$

Recall $$f'(k) = f(k)\,g'(k)$$, so

$$
f'(k)
= \left(\frac{N}{k}\right)^k (\ln N - \ln k - 1).
$$

This matches the structure in the handwritten derivation:
a positive factor $$\left(\frac{N}{k}\right)^k$$ times a bracket term.


<br>
### Step 4: Solve the critical point equation

A maximum (in the continuous setting) occurs at critical points where $$f'(k)=0$$:

$$
\left(\frac{N}{k}\right)^k (\ln N - \ln k - 1) = 0.
$$

The factor $$\left(\frac{N}{k}\right)^k$$ is strictly positive for $$k>0$$, so the only way the product can be zero is

$$
\ln N - \ln k - 1 = 0.
$$

Rearrange:

$$
\ln N - \ln k = 1
\quad\Longleftrightarrow\quad
\ln\left(\frac{N}{k}\right) = 1.
$$

Exponentiate both sides:

$$
\frac{N}{k} = e^1 = e.
$$

Finally solve for $$k$$:

$$
k = \frac{N}{e}.
$$


<br>
#### Conclusion (continuous optimum)

In the continuous version of the problem, $$f(k)=\left(\frac{N}{k}\right)^k$$ is maximized when

$$
k = \frac{N}{e}.
$$

<br>
### Step 5: Restricting to integer values of $$k$$

The previous calculation identifies the maximizer of


$$
f(k) = \left(\frac{N}{k}\right)^k
$$

when $$k$$ is allowed to vary over the positive real numbers. In the original problem, however, the number of parts must be an integer.

Let

$$
k^* = \frac{N}{e}
$$

denote the continuous maximizer. Since $$f(k)$$ is smooth and unimodal around its maximum, its largest value among integer arguments must be attained at one of the two integers closest to $$k^*$$.

Therefore, it suffices to compare the values

$$
k_1 = \lfloor k^* \rfloor,
\qquad
k_2 = \lceil k^* \rceil,
$$

and select the one that yields the larger product.

Equivalently, since the logarithm is strictly increasing, one may compare

$$
k \bigl(\ln N - \ln k\bigr)
$$

for $$k \in \{k_1, k_2\}$$ instead of evaluating the product directly.

The integer value chosen in this way determines the maximizing split and hence the value of $$M(N)$$.


## Implementation Notes

To turn the mathematical reasoning into an efficient program, we proceed in a few clearly separated steps.

For each value of $$N$$, the first task is to determine the integer $$k$$ that maximizes the product

$$
\left(\frac{N}{k}\right)^k.
$$

As shown above, the continuous maximizer lies at $$k^* = N/e$$, so it is sufficient to compare the two nearest integers,

$$
\lfloor k^* \rfloor \quad \text{and} \quad \lceil k^* \rceil.
$$

To avoid numerical overflow, this comparison is carried out in logarithmic form.

Once the optimal integer $$k$$ has been selected, we consider the value

$$
M(N) = \left(\frac{N}{k}\right)^k = \frac{N^k}{k^k}.
$$

Instead of forming this potentially huge rational number explicitly, we analyze its denominator in lowest terms. After cancelling common factors between $$N$$ and $$k$$, the reduced denominator is

$$
\left(\frac{k}{\gcd(N,k)}\right)^k.
$$

This observation allows us to decide whether $$M(N)$$ has a terminating decimal expansion using only elementary number theory: a rational number terminates in base 10 if and only if its reduced denominator has no prime factors other than $$2$$ and $$5$$.

If the decimal expansion terminates, the contribution $$W(N)$$ is zero. Otherwise, the contribution is defined as the smallest prime divisor of the reduced denominator, which can be extracted directly from $$k / \gcd(N,k)$$.

The following code implements these steps and computes the required sum

$$
\sum_{N=5}^{10^6} W(N).
$$

It should complete in less than 10 seconds.


```python
from __future__ import annotations

import math
from math import gcd


def reduce_fraction(numer: int, denom: int) -> tuple[int, int]:
    """Reduce the rational numer/denom to lowest terms.

    Note:
        We only need the reduced denominator for the decimal-termination test
        and for extracting prime factors.
    """
    if denom == 0:
        raise ZeroDivisionError("Denominator must be non-zero.")

    g = gcd(numer, denom)
    return numer // g, denom // g


def is_terminating_decimal_of_rational(numer: int, denom: int) -> bool:
    """Return True iff numer/denom (in lowest terms) has a terminating decimal.

    A rational number terminates in base 10 iff its reduced denominator has
    no prime factors other than 2 and 5.
    """
    _, d = reduce_fraction(numer, denom)

    # Strip all factors of 2 and 5 from the reduced denominator.
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5

    # If nothing remains, the denominator was of the form 2^a * 5^b.
    return d == 1


def smallest_prime_factor(n: int) -> int:
    """
    Return the smallest prime factor of n (for n >= 2).

    Note that this function is pretty slow and should be replaced for large numbers `n`.
    """
    if n < 2:
        raise ValueError("n must be >= 2")

    # Handle 2 quickly, then try odd divisors up to sqrt(n).
    if n % 2 == 0:
        return 2

    p = 3
    while p * p <= n:
        if n % p == 0:
            return p
        p += 2

    # If no divisor up to sqrt(n), n itself is prime.
    return n


def W_of_N(N: int) -> int:
    """Compute the non-termination weight W(N) for the adapted blog problem.

    Recap of the adapted definition:
      1) Choose k (integer) that maximizes f(k) = (N/k)^k.
      2) Let M(N) = (N/k)^k in lowest terms.
      3) If M(N) is a terminating decimal => W(N) = 0.
         Otherwise W(N) is the smallest prime divisor of the reduced denominator.

    Key simplification:
      M(N) = (N/k)^k = N^k / k^k.
      In lowest terms, its denominator is (k / gcd(N, k))^k.
      So the "obstructing" primes come entirely from k after canceling gcd(N, k).
    """
    if N < 2:
        raise ValueError("N must be >= 2")

    # Continuous maximizer from calculus: k* = N/e
    k_star = N / math.e

    # Since k must be an integer, it suffices to check the nearest integers:
    # floor(k*) and ceil(k*). (For N>=2 this never hits k=0.)
    k_candidates = (math.floor(k_star), math.ceil(k_star))

    # Choose the better k by comparing log(f(k)) instead of f(k) directly.
    # This avoids huge numbers because f(k) grows/decays exponentially.
    def log_f(k: int) -> float:
        # For our N range, k is always >= 1, but guard anyway.
        if k <= 0:
            return float("-inf")
        return k * (math.log(N) - math.log(k))

    best_k = max(k_candidates, key=log_f)

    # Reduce (N/best_k)^best_k = N^k / k^k to lowest terms.
    # Cancelling gcd(N, k) once is enough because the denominator becomes:
    #   (k / gcd(N,k))^k
    g = gcd(N, best_k)
    reduced_base_denom = best_k // g  # denominator of (N/k) in lowest terms

    # If reduced_base_denom has only prime factors 2 and 5, then its k-th power does too,
    # hence M(N) is a terminating decimal.
    if is_terminating_decimal_of_rational(N, best_k):
        return 0

    # Otherwise, the smallest "new" prime in the reduced denominator base is exactly the
    # smallest obstructing prime for the full denominator as well (powers don't change
    # the set of prime factors).
    return smallest_prime_factor(reduced_base_denom)


# -----------------------------
# Compute the required sum
# -----------------------------
total = 0
for N in range(5, 1_000_000 + 1):
    total += W_of_N(N)

total
```