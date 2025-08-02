---
layout: post
title: "Short Notes: Understanding Euclid’s GCD Algorithm"
modified: 2025-08-03
categories: [Math, Algorithms, Programming]
description: "A concise walkthrough of why Euclid’s Algorithm correctly computes the greatest common divisor (GCD), using basic properties of divisibility and remainders."
tags: [gcd, euclids-algorithm, number-theory, mathematics, proofs]
thumbnail:
giscus_comments: true
toc:
  beginning: true
share: true
date: 2025-08-03
pretty_table: false
related_posts: true
tabs: true
# related_publications: true
---

# Introduction
Euclid’s Algorithm is one of the oldest and most elegant procedures in mathematics. Dating back over two millennia, it provides an efficient method to compute the greatest common divisor (GCD) of two integers — the largest number that divides both without a remainder.

But why does this algorithm work? What makes repeatedly replacing a pair $(a, b)$ with $(b, a \bmod b)$, eventually lead us to the GCD?

In this short note, we take a closer look at the mathematical foundation behind Euclid’s Algorithm. Through a simple but rigorous argument, we’ll see how divisibility and the properties of remainders come together to justify the algorithm’s correctness.

<br>
# A (fairly) Informal Proof

We aim to show that for integers $a, b \in \mathbb{Z}$ with $b \ne 0$, the greatest common divisor satisfies:

$$
\gcd(a, b) = \gcd(b, a \bmod b).
$$

Let $d = \gcd(a, b)$. By definition:

- $d \mid a$
- $d \mid b$

Since $d \mid a$ and $d \mid b$, it also divides any linear combination of $a$ and $b$, in particular:

$$
\begin{align}
a &= qb + r \quad \text{for some } q \in \mathbb{Z}, \, 0 \le r < |b| \\
r &= a - qb = a \bmod b.
\end{align}
$$

So $d \mid r$, and of course $d \mid b$ by assumption.

Now let:

$$
\begin{align}
d' = \gcd(b,r).
\end{align}
$$

Since $d'$ divides both $b$ and $r$, it must also divide any linear combination of them, and in particular, it divides $a = qb + r$:

$$
\begin{align}
d' \mid r+qb = a.
\end{align}
$$

And since $d' \mid a$ and $d' \mid b$, meaning $d'$ is a common divisor of $a$ and $b$, it follows that

$$
\begin{align}
d' \le d,
\end{align}
$$


since $d$ is the greatest common divisor of $a$ and $b$, so $d'$ has to be less or equal.
Conversely, we already showed that $d \mid b$ and $d \mid r$, so $d$ is a common divisor of $b$ and $r$, implying:

$$
\begin{align}
d \le d',
\end{align}
$$

which leads us to the conclusion:

$$
\begin{align}
d &= d' \\
\gcd(a,b) &= \gcd(b,r) \\
\gcd(a,b) &= \gcd(b, a \bmod b).
\end{align}
$$

(In other words: we know that $d' = \gcd(b, r) \le d$ and we know that $d \mid b$ and also $d \mid r$. But $d$ cannot be larger than the already defined GCD of $b$ and $r$, $d' = \gcd(b, r)$, hence $\Rightarrow d'=d$).

This identity is the key to **Euclid’s Algorithm**, which recursively applies:

$$
\begin{align}
\gcd(a, b) = \gcd(b, a \bmod b),
\end{align}
$$

until the second argument becomes zero, at which point $\gcd(a, 0) = \| a \|$ (by definition).

<br>
# Implementation in Python

To translate the mathematical idea into code, we can use a simple recursive function that mirrors the structure of the proof:

```python
def gcd(a: int, b: int) -> int:
    """
    Computes the greatest common divisor (GCD) of a and b using Euclid's Algorithm.
    """
    if b == 0:
        return abs(a)  # GCD is always non-negative
    return gcd(b, a % b)
```

Alternatively, an iterative version avoids recursion and may be more efficient in practice:

```python
def gcd_iterative(a: int, b: int) -> int:
    """
    Iterative version of Euclid's Algorithm.
    """
    while b != 0:
        a, b = b, a % b
    return abs(a)
```

Both versions rely on the identity $\gcd(a, b) = \gcd(b, a \bmod b)$.

<br>
# Worked Example: GCD of 252 and 105

To illustrate how Euclid’s Algorithm works in practice, let’s compute:

$$
\gcd(252, 105)
$$

We apply the rule $\gcd(a, b) = \gcd(b, a \bmod b)$ repeatedly:

1. $\gcd(252, 105)$  
   $252 \bmod 105 = 42$  
   So, $\gcd(252, 105) = \gcd(105, 42)$

2. $\gcd(105, 42)$  
   $105 \bmod 42 = 21$  
   So, $\gcd(105, 42) = \gcd(42, 21)$

3. $\gcd(42, 21)$  
   $42 \bmod 21 = 0$  
   So, $\gcd(42, 21) = 21$

We stop here since the remainder is 0, and the last non-zero value is the GCD. Therefore:

$$
\gcd(252, 105) = 21
$$

This example illustrates how the algorithm quickly reduces the problem to a simpler one through successive remainders. You can cross-check the result by running one of the GCD functions above in your Python IDE.
