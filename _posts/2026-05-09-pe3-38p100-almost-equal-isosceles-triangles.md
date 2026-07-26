---
layout: post
title: "Almost-Equal Isosceles Triangles: When Height Nearly Matches Base"
modified:
categories: [math, number-theory]
description: "An exploration of a curious class of integer-sided isosceles triangles whose height differs from the base by exactly one. What begins as a simple geometric question quickly leads to Pell equations and elegant recurrences."
tags: [number-theory, pell-equations, diophantine, geometry, python]
thumbnail: assets/img/2026-05-09-almost-equal-isosceles-triangles/isosceles_triangle.svg
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-05-09T12:00:00+02:00
pretty_table: true
related_posts: true
tabs: true
images:
  compare: false
  slider: false
---

We are looking for isosceles triangles whose side lengths are all integers and whose height differs from the base by exactly one unit. At first glance, such a restrictive condition seems unlikely to admit more than a handful of solutions—if any at all. As we will see, however, these triangles are intimately connected to one of the most beautiful Diophantine equations in number theory: the Pell equation.

Consider an isosceles triangle with two equal legs of length $$L$$ and a base of length $$b$$. Let $$h$$ denote its height. Since the altitude from the apex bisects the base, it divides the triangle into two congruent right triangles, each with hypotenuse $$L$$, one leg of length $$b/2$$, and the other equal to the height $$h$$. Applying the Pythagorean theorem immediately gives

$$
h = \sqrt{L^2 - \left(\frac{b}{2}\right)^2}.
$$

{% include figure.liquid 
   path="assets/img/2026-05-09-almost-equal-isosceles-triangles/isosceles_triangle.svg" 
   class="img-fluid rounded z-depth-1 imgcenter" 
   zoomable=true  
   width="50%" 
   caption="An isosceles triangle with equal legs $L$, base $b$, and altitude $h$. The height bisects the base, creating two congruent right triangles." 
%}

For most choices of integer side lengths, the height $$h$$ is irrational. Even when the height happens to be an integer, there is usually no simple relationship between $$h$$ and the base $$b$$. In this article, we investigate a much stronger condition: we require the height and the base to differ by exactly one unit,

$$
h = b \pm 1.
$$

<!--more-->

At first glance, one might expect such triangles to be exceedingly rare, or perhaps not to exist at all. But a short search reveals a first example almost immediately:

| $$b$$ | $$L$$ | $$h$$ | Relation |
|:---:|:---:|:---:|:---:|
| 16 | 17 | 15 | $$h = b - 1$$ |

Here, the two legs have length $$L = 17$$, the base is $$b = 16$$, and the height evaluates to

$$
h = \sqrt{17^2 - 8^2}
  = \sqrt{225}
  = 15
  = b - 1.
$$

Thus, the height is an integer and differs from the base by exactly one.

Searching further reveals another solution—but it is already much larger:

| $$b$$ | $$L$$ | $$h$$ | Relation |
|:---:|:---:|:---:|:---:|
| 16 | 17 | 15 | $$h = b - 1$$ |
| 272 | 305 | 273 | $$h = b + 1$$ |

This time, the height exceeds the base by one. Notice how rapidly the numbers have grown: the equal sides increased from 17 to 305, while the base jumped from 16 to 272.

Even these two examples raise several natural questions. Is this rapid growth merely coincidental, or do the solutions follow a hidden pattern? More fundamentally, are there infinitely many such triangles, and if so, how can we generate them efficiently?

Searching for larger examples by brute force quickly becomes impractical. Instead, we seek an algebraic description of all such triangles. By translating the geometric constraint $$h = b \pm 1$$ into a Diophantine equation, we will arrive at a generalized Pell equation. This algebraic viewpoint not only explains the examples above but also provides a systematic way to generate infinitely many more.

Our approach consists of four steps:

1. Translate the geometric constraint $$h = b \pm 1$$ into a generalized Pell equation.
2. Derive a recurrence that generates all solutions using the closely related classical Pell equation.
3. Implement the algorithm in Python, including a Pell equation solver based on continued fractions.
4. Generate and verify the resulting family of triangles.


## Deriving the Pell Equation

To understand these triangles algebraically, we eliminate the height $h$ using the condition that it differs from the base by exactly one unit. Our goal is to transform the resulting equation into a well-studied Diophantine equation that we can solve systematically.

We begin with the Pythagorean relation for the right triangle formed by the altitude:

$$
\begin{align}
\left(\frac{b}{2}\right)^2 + h^2 = L^2.
\end{align}
$$

Instead of repeatedly writing $h=b\pm1$, we introduce the parameter

$$
\varepsilon \in \{-1,+1\},
$$

and write

$$
h = b + \varepsilon.
$$

Thus, $\varepsilon=-1$ corresponds to $h=b-1$, while $\varepsilon=+1$ corresponds to $h=b+1$. Since $\varepsilon^2=1$, substituting this expression for the height gives

$$
\begin{align}
\frac{1}{4}b^2 + (b + \varepsilon)^2 &= L^2 \nonumber \\
\frac{1}{4}b^2 + b^2 + 2\varepsilon b + \varepsilon^2 &= L^2 \nonumber \\
\frac{5}{4}b^2 + 2\varepsilon b + 1 - L^2 &= 0.
\end{align}
$$

Multiplying through by four removes the denominator:

$$
\begin{align}
5b^2 + 8\varepsilon b + 4 - 4L^2 &= 0.
\label{eq:dioph}
\end{align}
$$

Our goal is to transform this quadratic equation into the standard form of a Pell equation. We first divide by five so that the coefficient of $b^2$ becomes one, making it straightforward to complete the square:

$$
\begin{align}
b^2 + \frac{8}{5}\varepsilon b + \frac{4}{5} - \frac{4}{5}L^2 &= 0 \nonumber \\
\left(b + \frac{4}{5}\varepsilon\right)^2 - \frac{16}{25} + \frac{4}{5} - \frac{4}{5}L^2 &= 0.
\end{align}
$$

Multiplying through by 25 gives

$$
\begin{align}
\left(5b + 4\varepsilon\right)^2 - 16 + 20 - 20L^2 &= 0 \nonumber \\
\left(5b + 4\varepsilon\right)^2 + 4 - 20L^2 &= 0.
\end{align}
$$

The expression $5b+4\varepsilon$ now appears naturally as a perfect square, suggesting the substitution

$$
x = 5b + 4\varepsilon.
$$

This transforms the equation into

$$
\begin{align}
x^2 - 20L^2 = -4.
\label{eq:pell}
\end{align}
$$

This is a **generalized Pell equation**, i.e., an equation of the form

$$
x^2 - DL^2 = N,
$$

with $D=20$ and $N=-4$. Much is known about equations of this form, and we will exploit this structure to generate infinitely many solutions.

As a sanity check, let us verify that our previously discovered triangle satisfies the equation. For $b=16$, $L=17$, and $\varepsilon=-1$, we obtain

$$
x = 5 \cdot 16 - 4 = 76,
$$

and indeed

$$
76^2 - 20 \cdot 17^2 = 5776 - 5780 = -4.
$$

Finding one solution is encouraging, but it does not tell us how to obtain the next one. The key observation is that generalized Pell equations are closely related to the classical Pell equation, whose solutions possess a remarkable multiplicative structure.


## Generating New Solutions from Known Ones

We have transformed the original geometric problem into the generalized Pell equation

$$
x^2 - DL^2 = N,
$$

which, in our case, has the specific values $D=20$ and $N=-4$. We already know one non-trivial solution,

$$
(x_0,L_0)=(76,17).
$$

The remaining challenge is to generate additional solutions without solving the equation from scratch each time.

### Representing Pell Solutions Algebraically

The key idea is to associate each pair $(x,L)$ with the expression

$$
x+L\sqrt{D}.
$$

Its **conjugate** is obtained by changing the sign of the square-root term:

$$
\overline{x+L\sqrt{D}}=x-L\sqrt{D}.
$$

We define the **norm** of $x+L\sqrt{D}$ as the product of the expression and its conjugate:

$$
\begin{align}
\operatorname{Norm}(x+L\sqrt{D})
&=(x+L\sqrt{D})(x-L\sqrt{D}) \nonumber\\
&=x^2-DL^2.
\end{align}
$$

The norm is therefore exactly the left-hand side of the Pell equation. In particular, if $(x,L)$ satisfies

$$
x^2-DL^2=N,
$$

then the associated expression $x+L\sqrt{D}$ has norm $N$.

The crucial property is that the norm of a product equals the product of the individual norms. To see this, let $\alpha$ and $\beta$ be two expressions of this form. Since conjugation distributes over multiplication,

$$
\overline{\alpha\beta}
=
\overline{\alpha}\,\overline{\beta}.
$$

Therefore,

$$
\begin{align}
\operatorname{Norm}(\alpha\beta)
&=(\alpha\beta)\overline{\alpha\beta} \nonumber\\
&=(\alpha\beta)(\overline{\alpha}\,\overline{\beta}) \nonumber\\
&=(\alpha\overline{\alpha})(\beta\overline{\beta}) \nonumber\\
&=\operatorname{Norm}(\alpha)\operatorname{Norm}(\beta).
\end{align}
$$

This is what is meant by saying that **norms are multiplicative**.

Consequently, if $\alpha$ has norm $N$ and $\beta$ has norm $1$, then

$$
\operatorname{Norm}(\alpha\beta)
=
\operatorname{Norm}(\alpha)\operatorname{Norm}(\beta)
=
N\cdot1
=
N.
$$

Thus, multiplying a solution of the generalized Pell equation by a solution of the classical Pell equation preserves the value $N$ and produces another solution of the generalized equation.

### Deriving the Recurrence

More precisely, suppose we have

- one solution $(x_k,L_k)$ of the generalized Pell equation

  $$
  x^2-DL^2=N,
  $$

- and one solution $(u,v)$ of the classical Pell equation

  $$
  u^2-Dv^2=1.
  $$

We associate these solutions with

$$
\begin{align}
\alpha &= x_k+L_k\sqrt{D},\\
\beta &= u+v\sqrt{D}.
\end{align}
$$

Their product is

$$
\begin{align}
\alpha\beta
&=(x_k+L_k\sqrt{D})(u+v\sqrt{D}) \nonumber\\
&=x_ku+x_kv\sqrt{D}+uL_k\sqrt{D}+DL_kv \nonumber\\
&=(ux_k+DvL_k)+(vx_k+uL_k)\sqrt{D}.
\end{align}
$$

Comparing the integer part and the coefficient of $\sqrt{D}$ gives the new pair

$$
\begin{align}
x_{k+1} &= ux_k+DvL_k, \nonumber\\
L_{k+1} &= vx_k+uL_k.
\end{align}
$$

The recurrence can also be written in matrix form:

$$
\begin{pmatrix}
x_{k+1}\\
L_{k+1}
\end{pmatrix}
=
\begin{pmatrix}
u & Dv\\
v & u
\end{pmatrix}
\begin{pmatrix}
x_k\\
L_k
\end{pmatrix}.
$$

### Verifying the Construction Directly

The norm argument already proves that the new pair satisfies the generalized Pell equation. Nevertheless, it is useful to verify the result directly from the recurrence.

Using

$$
x_{k+1}=ux_k+DvL_k
$$

and

$$
L_{k+1}=vx_k+uL_k,
$$

we obtain

$$
\begin{align}
x_{k+1}^2-DL_{k+1}^2
&=(ux_k+DvL_k)^2-D(vx_k+uL_k)^2 \nonumber\\
&=u^2x_k^2+2uDv x_kL_k+D^2v^2L_k^2 \nonumber\\
&\quad-Dv^2x_k^2-2Duvx_kL_k-Du^2L_k^2.
\end{align}
$$

The mixed terms cancel:

$$
2uDv x_kL_k-2Duvx_kL_k=0.
$$

Factoring the remaining terms gives

$$
\begin{align}
x_{k+1}^2-DL_{k+1}^2
&=x_k^2(u^2-Dv^2)-DL_k^2(u^2-Dv^2) \nonumber\\
&=(x_k^2-DL_k^2)(u^2-Dv^2).
\end{align}
$$

Using the two equations satisfied by the original pairs,

$$
x_k^2-DL_k^2=N
$$

and

$$
u^2-Dv^2=1,
$$

we finally obtain

$$
x_{k+1}^2-DL_{k+1}^2
=
N\cdot1
=
N.
\qquad\square
$$

This direct calculation is the coordinate form of the norm identity

$$
\operatorname{Norm}(\alpha\beta)
=
\operatorname{Norm}(\alpha)\operatorname{Norm}(\beta).
$$

The strategy is now clear. We first need to find the **fundamental solution** of the classical Pell equation

$$
u^2-20v^2=1.
$$

Once this solution is known, the recurrence above transforms any solution of

$$
x^2-20L^2=-4
$$

into another one. Starting from the initial solution

$$
(x_0,L_0)=(76,17),
$$

we can repeatedly apply the recurrence to generate further almost-equal isosceles triangles.

> **Note.**
> For readers interested in the general theory of Pell equations and continued fractions, a useful introduction can be found in [this video series](https://www.youtube.com/watch?v=s5RQj_Jcs0U&list=PLsT0BEyocS2L25-tI-XUrWOJVvf4N3Ivq&t=0s).


## Solving Pell's Equation with Continued Fractions

In the previous section, we derived a recurrence that turns one solution of the generalized Pell equation

$$
x^2-20L^2=-4
$$

into another. However, the recurrence still requires one missing ingredient: a solution $(u,v)$ of the related classical Pell equation

$$
\begin{align}
u^2-20v^2=1.
\label{eq:classical-pell}
\end{align}
$$

More specifically, we need its **fundamental solution**, meaning the solution with the smallest positive value of $u$. Continued fractions provide a systematic way to find it.

### Continued Fractions

A continued fraction represents a real number as a sequence of nested integer parts:

$$
a_0+\cfrac{1}{a_1+\cfrac{1}{a_2+\cfrac{1}{a_3+\cdots}}}.
$$

This is written more compactly as

$$
[a_0;\,a_1,a_2,a_3,\ldots].
$$

The integers $a_0,a_1,a_2,\ldots$ are called the **coefficients** of the continued fraction.

For square roots of non-square integers, the coefficients eventually repeat. In fact, their continued fractions are periodic. For our problem,

$$
\begin{align}
\sqrt{20}=[4;\,\overline{2,8}]
          =[4;\,2,8,2,8,2,8,\ldots].
\label{eq:sqrt20-cf}
\end{align}
$$

Let us briefly see where these coefficients come from.

The integer part of $\sqrt{20}\approx4.4721$ is

$$
a_0=\lfloor\sqrt{20}\rfloor=4.
$$

We subtract this integer part and invert the remainder:

$$
\frac{1}{\sqrt{20}-4}
=
\frac{\sqrt{20}+4}{20-16}
=
\frac{\sqrt{20}+4}{4}
\approx2.118.
$$

Its integer part is therefore $a_1=2$. Subtracting $2$ and inverting again gives

$$
\begin{align}
\frac{1}{
\frac{\sqrt{20}+4}{4}-2
}
&=
\frac{1}{
\frac{\sqrt{20}-4}{4}
} \nonumber\\
&=
\frac{4}{\sqrt{20}-4}
=
\sqrt{20}+4
\approx8.472.
\end{align}
$$

Thus, $a_2=8$. After subtracting $8$, the remainder is once again $\sqrt{20}-4$, so the same calculation repeats. This explains the period $\overline{2,8}$ in Eq. $\eqref{eq:sqrt20-cf}$.

### Convergents

By truncating a continued fraction after finitely many coefficients, we obtain a rational approximation called a **convergent**.

The first few convergents of $\sqrt{20}$ are

$$
\begin{array}{lcll}
[4]
&=&
\dfrac{4}{1}
&=4.000,\\[10pt]

[4;\,2]
&=&
4+\dfrac{1}{2}
=
\dfrac{9}{2}
&=4.500,\\[10pt]

[4;\,2,8]
&=&
4+\cfrac{1}{2+\cfrac{1}{8}}
=
\dfrac{76}{17}
&\approx4.4706.
\end{array}
$$

As more coefficients are included, the convergents approach

$$
\sqrt{20}\approx4.4721.
$$

But why should good rational approximations to $\sqrt{20}$ help us solve Pell's equation?

### Why Pell Solutions Approximate $\sqrt{D}$

Consider the classical Pell equation

$$
u^2-Dv^2=1.
$$

Factoring the left-hand side as a difference of squares gives

$$
(u-v\sqrt{D})(u+v\sqrt{D})=1.
$$

Since $u+v\sqrt{D}$ is positive, we can divide by it:

$$
u-v\sqrt{D}
=
\frac{1}{u+v\sqrt{D}}.
$$

Dividing once more by $v$ yields

$$
\begin{align}
\frac{u}{v}-\sqrt{D}
=
\frac{1}{v(u+v\sqrt{D})}.
\label{eq:pell-approximation}
\end{align}
$$

Equation $\eqref{eq:pell-approximation}$ proves an important one-way implication:

> Every solution $(u,v)$ of the Pell equation produces an exceptionally good rational approximation $u/v$ to $\sqrt D$.

Indeed, since $u/v\approx\sqrt D$, the denominator on the right-hand side satisfies

$$
v(u+v\sqrt D)\approx2\sqrt D,v^2,
$$

so

$$
\left|\frac uv-\sqrt D\right|
\approx
\frac{1}{2\sqrt D,v^2}.
$$

This error is of order $1/v^2$, which is characteristic of the unusually accurate approximations produced by continued-fraction convergents. A standard theorem therefore implies that every Pell solution $u/v$ must occur among the convergents of $\sqrt D$.

However, the approximation argument alone does not guarantee that an arbitrary convergent satisfies

$$
u^2-Dv^2=1.
$$

A convergent may instead produce another small residual. For example, when $D=20$,

$$
4^2-20\cdot1^2=-4,
$$

even though $4/1$ is a convergent of $\sqrt{20}$.

The guarantee that a convergent with residual $1$ eventually appears comes from the periodicity of the continued fraction of $\sqrt D$. For every positive non-square integer $D$, the periodic continued fraction of $\sqrt D$ contains the fundamental Pell solution: it appears after one period when the period length is even, and after two periods when the period length is odd.

Thus, the two ideas play different roles:

$$
\text{Pell solution}
\Longrightarrow
\text{exceptionally good approximation}
\Longrightarrow
\text{continued-fraction convergent},
$$

while periodicity guarantees that one of those convergents actually satisfies the Pell equation.

A more detailed statement of this theorem and the general convergent algorithm are given in [Appendix A](#appendix-a-continued-fractions-and-pells-equation).

### Finding the Fundamental Solution for $D=20$

For our problem, we test the first convergents of $\sqrt{20}$:

| Convergent | Fraction $\frac{p_k}{q_k}$ | Pell residual $p_k^2-20q_k^2$ |
|:---:|:---:|:---:|
| $[4]$ | $\frac{4}{1}$ | $4^2-20\cdot1^2=-4$ |
| $[4;\,2]$ | $\frac{9}{2}$ | $9^2-20\cdot2^2=1$ |
| $[4;\,2,8]$ | $\frac{76}{17}$ | $76^2-20\cdot17^2=-4$ |

The second convergent already gives residual $1$:

$$
9^2-20\cdot2^2
=
81-80
=
1.
$$

Therefore, the fundamental solution of Eq. $\eqref{eq:classical-pell}$ is

$$
(u,v)=(9,2).
$$

The third convergent is also noteworthy:

$$
76^2-20\cdot17^2=-4.
$$

Thus, $(76,17)$ is exactly the generalized-Pell solution corresponding to our first non-degenerate triangle. In this particular problem, the continued fraction of $\sqrt{20}$ therefore reveals both the classical Pell multiplier $(9,2)$ and our initial generalized-Pell solution $(76,17)$.

### Returning to the Triangle Recurrence

We can now substitute

$$
D=20,\qquad u=9,\qquad v=2
$$

into the recurrence derived in the previous section:

$$
\begin{align}
x_{k+1}
&=ux_k+DvL_k \nonumber\\
&=9x_k+40L_k,
\label{eq:specific-x-recurrence}\\[6pt]
L_{k+1}
&=vx_k+uL_k \nonumber\\
&=2x_k+9L_k.
\label{eq:specific-l-recurrence}
\end{align}
$$

Starting from

$$
(x_0,L_0)=(76,17),
$$

the next Pell solution is

$$
\begin{align}
x_1
&=9\cdot76+40\cdot17 \nonumber\\
&=684+680 \nonumber\\
&=1364,
\end{align}
$$

and

$$
\begin{align}
L_1
&=2\cdot76+9\cdot17 \nonumber\\
&=152+153 \nonumber\\
&=305.
\end{align}
$$

To recover the triangle, recall the substitution introduced when deriving the generalized Pell equation:

$$
x=5b+4\varepsilon,
\qquad
\varepsilon\in\{-1,+1\}.
$$

Since

$$
1364=5\cdot272+4,
$$

we have $\varepsilon=+1$ and therefore

$$
b=272,
\qquad
h=b+\varepsilon=273.
$$

This reproduces the second triangle from the introduction:

$$
(b,L,h)=(272,305,273).
$$

The continued fraction has therefore supplied exactly the missing multiplier needed by our recurrence. From this point onward, no further continued-fraction calculations are required: repeatedly applying Eqs. $\eqref{eq:specific-x-recurrence}$ and $\eqref{eq:specific-l-recurrence}$ generates the remaining triangles.



## Implementation in Python

We already know that the fundamental solution of the classical Pell equation

$$
u^2-20v^2=1
$$

is

$$
(u,v)=(9,2).
$$

For our specific triangle problem, we could therefore hard-code these two values. However, implementing the continued-fraction method gives us a reusable solver for the classical Pell equation

$$
u^2-Dv^2=1
$$

for any positive non-square integer $D$.

The implementation follows the two recurrences introduced earlier:

1. The variables $m$, $d$, and $a$ generate the coefficients of the periodic continued fraction of $\sqrt{D}$.
2. The variables $p$ and $q$ generate its convergents.

After computing each convergent $p/q$, we test whether

$$
p^2-Dq^2=1.
$$

The first pair satisfying this equation is the fundamental solution $(u,v)$. The general theory in [Appendix A](#appendix-a-continued-fractions-and-pells-equation) guarantees that this search terminates.

### Computing the Fundamental Pell Solution

The continued-fraction coefficients are generated by the update rules

$$
\begin{align}
m_{k+1} &= d_ka_k-m_k,\\
d_{k+1} &= \frac{D-m_{k+1}^2}{d_k},\\
a_{k+1} &= \left\lfloor
\frac{a_0+m_{k+1}}{d_{k+1}}
\right\rfloor,
\end{align}
$$

where

$$
a_0=\lfloor\sqrt{D}\rfloor.
$$

At the same time, the numerators and denominators of the convergents are updated using

$$
\begin{align}
p_k &= a_kp_{k-1}+p_{k-2},\\
q_k &= a_kq_{k-1}+q_{k-2}.
\end{align}
$$

The following function combines both recurrences:

```python
from math import isqrt


def solve_pell(D: int) -> tuple[int, int]:
    """Return the fundamental solution (u, v) of u^2 - D*v^2 = 1."""

    if D <= 0:
        raise ValueError("D must be a positive integer.")

    a0 = isqrt(D)
    if a0 * a0 == D:
        raise ValueError("D must not be a perfect square.")

    # State used to generate the continued-fraction coefficients of sqrt(D).
    m, d, a = 0, 1, a0

    # Initial values for the convergent recurrence.
    p_prev2, p_prev1 = 0, 1
    q_prev2, q_prev1 = 1, 0

    while True:
        # Current convergent p/q = [a0; a1, ..., ak].
        p = a * p_prev1 + p_prev2
        q = a * q_prev1 + q_prev2

        # The first convergent with residual 1 is the fundamental solution.
        if p * p - D * q * q == 1:
            return p, q

        p_prev2, p_prev1 = p_prev1, p
        q_prev2, q_prev1 = q_prev1, q

        # Generate the next continued-fraction coefficient.
        m = d * a - m
        d = (D - m * m) // d
        a = (a0 + m) // d
```

For our problem, we call the solver with $D=20$:

```python
D = 20
u, v = solve_pell(D)

print(f"Fundamental solution of u^2 - {D}*v^2 = 1: ({u}, {v})")
print(f"Verification: {u}^2 - {D}*{v}^2 = {u * u - D * v * v}")
```

This produces

```text
Fundamental solution of u^2 - 20*v^2 = 1: (9, 2)
Verification: 9^2 - 20*2^2 = 1
```

Thus, the implementation recovers the multiplier

$$
(u,v)=(9,2)
$$

that we derived from the continued fraction of $\sqrt{20}$.

### Recovering a Triangle from a Pell Solution

The recurrence generates pairs $(x,L)$ satisfying

$$
x^2-20L^2=-4.
$$

To convert such a pair back into a triangle, recall the substitution used when deriving the generalized Pell equation:

$$
x=5b+4\varepsilon,
\qquad
\varepsilon\in\{-1,+1\},
$$

with

$$
h=b+\varepsilon.
$$

Solving the first equation for $b$ gives

$$
b=\frac{x-4\varepsilon}{5}.
$$

The correct value of $\varepsilon$ can be determined from the residue of $x$ modulo $5$:

- If $x\equiv1\pmod5$, then $\varepsilon=-1$.
- If $x\equiv4\pmod5$, then $\varepsilon=+1$.

The conversion can therefore be implemented directly:

```python
def pell_solution_to_triangle(
    x: int,
    L: int,
) -> tuple[int, int, int]:
    """Convert a Pell solution (x, L) into a triangle (b, L, h)."""

    if x % 5 == 1:
        epsilon = -1
    elif x % 5 == 4:
        epsilon = 1
    else:
        raise ValueError("The Pell solution does not encode a valid triangle.")

    b = (x - 4 * epsilon) // 5
    h = b + epsilon

    # Verify the original geometric conditions.
    assert b % 2 == 0
    assert h * h + (b // 2) ** 2 == L * L
    assert abs(h - b) == 1

    return b, L, h
```

The assertions verify the conditions from which the Pell equation was originally derived:

- the base is even, so the altitude bisects it into two integer lengths;
- the Pythagorean relation holds;
- the height and base differ by exactly one.

### Generating the Triangle Solutions

With the fundamental solution $(u,v)$ available, we repeatedly apply the recurrence

$$
\begin{align}
x_{k+1} &= ux_k+DvL_k,\\
L_{k+1} &= vx_k+uL_k.
\end{align}
$$

For $D=20$ and $(u,v)=(9,2)$, this is the concrete recurrence

$$
\begin{align}
x_{k+1} &= 9x_k+40L_k,\\
L_{k+1} &= 2x_k+9L_k.
\end{align}
$$

We begin with the generalized-Pell solution

$$
(x_0,L_0)=(76,17),
$$

which corresponds to the triangle

$$
(b,L,h)=(16,17,15).
$$

The complete generator is:

```python
def generate_triangles(count: int) -> list[tuple[int, int, int]]:
    """Generate the first `count` almost-equal isosceles triangles."""

    if count < 0:
        raise ValueError("count must be non-negative.")

    D = 20
    u, v = solve_pell(D)

    # Initial solution:
    # b=16, L=17, h=15, epsilon=-1, and x=5*16-4=76.
    x, L = 76, 17

    triangles = []

    for _ in range(count):
        triangles.append(pell_solution_to_triangle(x, L))

        # Apply the Pell recurrence.
        x, L = (
            u * x + D * v * L,
            v * x + u * L,
        )

    return triangles
```

We can now generate and display as many solutions as desired:

```python
for k, (b, L, h) in enumerate(generate_triangles(20), start=1):
    relation = "h = b - 1" if h < b else "h = b + 1"
    print(f"{k:>2}. b={b}, L={L}, h={h}  ({relation})")
```

The first few lines are

```text
 1. b=16, L=17, h=15  (h = b - 1)
 2. b=272, L=305, h=273  (h = b + 1)
 3. b=4896, L=5473, h=4895  (h = b - 1)
 4. b=87840, L=98209, h=87841  (h = b + 1)
 5. b=1576240, L=1762289, h=1576239  (h = b - 1)
```

The implementation mirrors the mathematical construction directly:

1. `solve_pell` finds the norm-$1$ multiplier $(u,v)$.
2. The Pell recurrence generates a new pair $(x,L)$.
3. `pell_solution_to_triangle` reverses the substitution
   $$
   x=5b+4\varepsilon
   $$
   and recovers $(b,L,h)$.
4. The assertions verify that every generated result satisfies the original geometric conditions.


### Alternative: A Direct Recurrence for the Triangle Variables

The Pell variables are useful for deriving the solution, but they are not strictly necessary once the recurrence is known. We can eliminate $x_k$ and obtain a recurrence that acts directly on the geometric variables $b_k$ and $L_k$.

Recall the substitution

$$
x_k=5b_k+4\varepsilon_k,
\qquad
\varepsilon_k\in\{-1,+1\},
$$

where

$$
h_k=b_k+\varepsilon_k.
$$

We also derived the Pell recurrence

$$
\begin{align}
x_{k+1}&=9x_k+40L_k,\\
L_{k+1}&=2x_k+9L_k.
\end{align}
$$

We now substitute $x_k=5b_k+4\varepsilon_k$ into these equations.

First, for the leg length,

$$
\begin{align}
L_{k+1}
&=2x_k+9L_k \nonumber\\
&=2(5b_k+4\varepsilon_k)+9L_k \nonumber\\
&=10b_k+9L_k+8\varepsilon_k.
\label{eq:direct-l-recurrence}
\end{align}
$$

To recover the recurrence for the base, we first determine how $\varepsilon_k$ changes. Reducing the recurrence for $x_k$ modulo $5$ gives

$$
x_{k+1}
\equiv
9x_k
\equiv
-x_k
\pmod 5.
$$

Because $x_k=5b_k+4\varepsilon_k$, we also have

$$
x_k\equiv4\varepsilon_k\pmod5.
$$

It follows that the sign alternates:

$$
\begin{align}
\varepsilon_{k+1}=-\varepsilon_k.
\label{eq:epsilon-alternation}
\end{align}
$$

Using this relation, the next Pell variable can be written as

$$
x_{k+1}
=
5b_{k+1}+4\varepsilon_{k+1}
=
5b_{k+1}-4\varepsilon_k.
$$

On the other hand, substituting $x_k=5b_k+4\varepsilon_k$ into the Pell recurrence gives

$$
\begin{align}
x_{k+1}
&=9x_k+40L_k \nonumber\\
&=9(5b_k+4\varepsilon_k)+40L_k \nonumber\\
&=45b_k+36\varepsilon_k+40L_k.
\end{align}
$$

Equating the two expressions for $x_{k+1}$,

$$
5b_{k+1}-4\varepsilon_k
=
45b_k+36\varepsilon_k+40L_k,
$$

and solving for $b_{k+1}$ yields

$$
\begin{align}
b_{k+1}
=
9b_k+8L_k+8\varepsilon_k.
\label{eq:direct-b-recurrence}
\end{align}
$$

Together, Eqs. $\eqref{eq:direct-b-recurrence}$, $\eqref{eq:direct-l-recurrence}$, and $\eqref{eq:epsilon-alternation}$ give the direct recurrence

$$
\boxed{
\begin{aligned}
b_{k+1}&=9b_k+8L_k+8\varepsilon_k,\\
L_{k+1}&=10b_k+9L_k+8\varepsilon_k,\\
\varepsilon_{k+1}&=-\varepsilon_k.
\end{aligned}
}
$$

Starting from

$$
(b_0,L_0,\varepsilon_0)=(16,17,-1),
$$

the next values are

$$
\begin{align}
b_1
&=9\cdot16+8\cdot17-8
=272,\\
L_1
&=10\cdot16+9\cdot17-8
=305,\\
\varepsilon_1
&=1.
\end{align}
$$

Therefore,

$$
h_1=b_1+\varepsilon_1=273,
$$

and we recover the second triangle

$$
(b_1,L_1,h_1)=(272,305,273).
$$

This recurrence can be implemented without explicitly storing the Pell variable $x$:

```python
def generate_triangles_direct(
    count: int,
) -> list[tuple[int, int, int]]:
    """Generate triangles directly from (b, L, epsilon)."""

    if count < 0:
        raise ValueError("count must be non-negative.")

    b, L, epsilon = 16, 17, -1
    triangles = []

    for _ in range(count):
        h = b + epsilon
        triangles.append((b, L, h))

        b, L, epsilon = (
            9 * b + 8 * L + 8 * epsilon,
            10 * b + 9 * L + 8 * epsilon,
            -epsilon,
        )

    return triangles
```

The direct recurrence is convenient for generating triangles, but it does not replace the Pell derivation: its coefficients come directly from the Pell multiplier $(u,v)=(9,2)$. In other words, the Pell equation explains **why** the recurrence has this form and why it continues to produce valid solutions.

A specialized quadratic Diophantine equation solver, such as the [Alpertron solver](https://www.alpertron.com.ar/QUAD.HTM), can also produce affine recurrence relations for the original equation

$$
5b^2+8\varepsilon b+4-4L^2=0.
$$

Such a solver is useful as an independent check or for exploring similar equations. Here, however, deriving the recurrence from the Pell construction keeps the coefficients transparent and connects the alternative method directly to the rest of the article.


## Results

The first 15 non-degenerate triangles generated by the recurrence are shown below. Each row has been verified against the original geometric conditions

$$
h^2+\left(\frac{b}{2}\right)^2=L^2
$$

and

$$
|h-b|=1.
$$

| # | $$b$$ | $$L$$ | $$h$$ | Relation |
|:---:|---:|---:|---:|:---:|
| 1 | 16 | 17 | 15 | $$h = b - 1$$ |
| 2 | 272 | 305 | 273 | $$h = b + 1$$ |
| 3 | 4,896 | 5,473 | 4,895 | $$h = b - 1$$ |
| 4 | 87,840 | 98,209 | 87,841 | $$h = b + 1$$ |
| 5 | 1,576,240 | 1,762,289 | 1,576,239 | $$h = b - 1$$ |
| 6 | 28,284,464 | 31,622,993 | 28,284,465 | $$h = b + 1$$ |
| 7 | 507,544,128 | 567,451,585 | 507,544,127 | $$h = b - 1$$ |
| 8 | 9,107,509,824 | 10,182,505,537 | 9,107,509,825 | $$h = b + 1$$ |
| 9 | 163,427,632,720 | 182,717,648,081 | 163,427,632,719 | $$h = b - 1$$ |
| 10 | 2,932,589,879,120 | 3,278,735,159,921 | 2,932,589,879,121 | $$h = b + 1$$ |
| 11 | 52,623,190,191,456 | 58,834,515,230,497 | 52,623,190,191,455 | $$h = b - 1$$ |
| 12 | 944,284,833,567,072 | 1,055,742,538,989,025 | 944,284,833,567,073 | $$h = b + 1$$ |
| 13 | 16,944,503,814,015,856 | 18,944,531,186,571,953 | 16,944,503,814,015,855 | $$h = b - 1$$ |
| 14 | 304,056,783,818,718,320 | 339,945,818,819,306,129 | 304,056,783,818,718,321 | $$h = b + 1$$ |
| 15 | 5,456,077,604,922,913,920 | 6,100,080,207,560,938,369 | 5,456,077,604,922,913,919 | $$h = b - 1$$ |

As predicted by the recurrence

$$
\varepsilon_{k+1}=-\varepsilon_k,
$$

the solutions alternate between $h=b-1$ and $h=b+1$.

The values also grow extremely quickly. The ratio $L_{k+1}/L_k$ approaches the Pell multiplier

$$
9+2\sqrt{20}
=
9+4\sqrt{5}
\approx17.944.
$$

Thus, each leg length is approximately 18 times larger than the previous one. This growth factor is not accidental: in the next section, we will see that it equals $\phi^6$ and reflects a deeper connection to Fibonacci and Lucas numbers.

Because the recurrence uses only exact integer arithmetic, it can generate arbitrarily many further solutions without introducing numerical approximation errors.



## Connection to Fibonacci and Lucas Numbers

The growth factor of approximately $18$ is not a numerical coincidence. The family generated above has an exact description in terms of Fibonacci and Lucas numbers, and the Pell multiplier turns out to be the sixth power of the golden ratio.

Let

$$
\phi=\frac{1+\sqrt5}{2}
$$

denote the golden ratio. We write the Fibonacci numbers as $F_n$ and the Lucas numbers as $\operatorname{Luc}_n$ to avoid confusing the Lucas sequence with the triangle leg $L$.

### The Lucas–Fibonacci Identity

Fibonacci and Lucas numbers satisfy the identity

$$
\begin{align}
\operatorname{Luc}_n^2-5F_n^2=4(-1)^n.
\label{eq:lucas-fibonacci-identity}
\end{align}
$$

Our generalized Pell equation is

$$
x^2-20L^2=-4.
$$

Since $20=4\cdot5$, we can rewrite it as

$$
\begin{align}
x^2-5(2L)^2=-4.
\label{eq:pell-fibonacci-form}
\end{align}
$$

Comparing Eq. $\eqref{eq:pell-fibonacci-form}$ with the Lucas–Fibonacci identity in Eq. $\eqref{eq:lucas-fibonacci-identity}$ suggests the identification

$$
x=\operatorname{Luc}_n,
\qquad
2L=F_n.
$$

This is more than a convenient guess—the correspondence is **exact**, which is what ultimately makes our family of triangles complete. A classical result states that, up to sign, the only integer solutions of

$$
a^2-5c^2=\pm4
$$

are the Lucas–Fibonacci pairs $(a,c)=(\operatorname{Luc}_n,F_n)$ with $n\ge0$. They are generated by powers of the golden ratio through the identity $\operatorname{Luc}_n+F_n\sqrt5=2\phi^n$, and because $\phi$ and its conjugate $\tfrac{1-\sqrt5}{2}$ multiply to $-1$, each such pair satisfies $a^2-5c^2=4(-1)^n$. Applied to $x^2-5(2L)^2=-4$, this shows that **every** integer solution has the form $x=\operatorname{Luc}_n$ and $2L=F_n$: the identification thus discards nothing, and the family we are about to enumerate is exhaustive.

Therefore,

$$
\begin{align}
L=\frac{F_n}{2}.
\label{eq:leg-fibonacci}
\end{align}
$$

For the right-hand side of Eq. $\eqref{eq:lucas-fibonacci-identity}$ to equal $-4$, the index $n$ must be odd. In addition, $L$ is an integer only when $F_n$ is even.

The Fibonacci sequence is even precisely at indices divisible by $3$. Combining both conditions gives

$$
n\equiv3\pmod6.
$$

Thus,

$$
n=3,9,15,21,27,\ldots
$$

The first admissible index, $n=3$, gives

$$
\operatorname{Luc}_3=4,
\qquad
F_3=2,
$$

and hence

$$
(x,L)=(4,1).
$$

Using the substitution

$$
x=5b+4\varepsilon,
$$

this corresponds to $b=0$ with $\varepsilon=1$. It is therefore the degenerate solution rather than a genuine triangle.

The non-degenerate family begins at $n=9$. Writing

$$
n=6k+9,
\qquad
k=0,1,2,\ldots,
$$

we obtain the exact formulas

$$
\begin{align}
\boxed{
x_k=\operatorname{Luc}_{6k+9},
\qquad
L_k=\frac{F_{6k+9}}{2}.
}
\label{eq:pell-fibonacci-formulas}
\end{align}
$$

### Verification

The first few indices reproduce the Pell variables and leg lengths found earlier:

| $k$ | $n=6k+9$ | $\operatorname{Luc}_n=x_k$ | $F_n$ | $L_k=F_n/2$ |
|:---:|:---:|---:|---:|---:|
| $0$ | $9$  | $76$      | $34$      | $17$ |
| $1$ | $15$ | $1{,}364$ | $610$     | $305$ |
| $2$ | $21$ | $24{,}476$ | $10{,}946$ | $5{,}473$ |
| $3$ | $27$ | $439{,}204$ | $196{,}418$ | $98{,}209$ |

Thus, every leg length in the generated family is half a Fibonacci number, while the corresponding Pell variable is a Lucas number. Both sequences are sampled every six indices:

$$
9,15,21,27,\ldots
$$

### Closed Forms for the Complete Triangle

The sign variable alternates according to

$$
\varepsilon_k=(-1)^{k+1}.
$$

Since

$$
x_k=5b_k+4\varepsilon_k,
$$

we can solve for the base:

$$
\begin{align}
b_k
&=\frac{x_k-4\varepsilon_k}{5} \nonumber\\
&=\frac{\operatorname{Luc}_{6k+9}+4(-1)^k}{5}.
\end{align}
$$

The height is

$$
\begin{align}
h_k
&=b_k+\varepsilon_k \nonumber\\
&=\frac{\operatorname{Luc}_{6k+9}-(-1)^k}{5}.
\end{align}
$$

Therefore, the complete family of non-degenerate triangles generated by the recurrence has the closed form

$$
\begin{align}
\boxed{
\begin{aligned}
b_k&=\frac{\operatorname{Luc}_{6k+9}+4(-1)^k}{5},\\[4pt]
L_k&=\frac{F_{6k+9}}{2},\\[4pt]
h_k&=\frac{\operatorname{Luc}_{6k+9}-(-1)^k}{5},
\end{aligned}
\qquad
k=0,1,2,\ldots
}
\label{eq:triangle-closed-forms}
\end{align}
$$

For $k=0$, these formulas give

$$
(b_0,L_0,h_0)=(16,17,15),
$$

and for $k=1$ they give

$$
(b_1,L_1,h_1)=(272,305,273).
$$

### Why the Growth Factor Is $\phi^6$

The connection to the growth factor follows directly from the Binet identities

$$
\operatorname{Luc}_n=\phi^n+\psi^n,
$$

and

$$
F_n=\frac{\phi^n-\psi^n}{\sqrt5},
$$

where

$$
\psi=\frac{1-\sqrt5}{2}.
$$

Adding $\operatorname{Luc}_n$ and $F_n\sqrt5$ gives

$$
\begin{align}
\operatorname{Luc}_n+F_n\sqrt5
&=
\left(\phi^n+\psi^n\right)
+
\left(\phi^n-\psi^n\right) \nonumber\\
&=
2\phi^n.
\label{eq:lucas-fibonacci-binet-combination}
\end{align}
$$

For the indices $n=6k+9$, Eq. $\eqref{eq:pell-fibonacci-formulas}$ gives

$$
\begin{align}
x_k+L_k\sqrt{20}
&=
\operatorname{Luc}_{6k+9}
+
\frac{F_{6k+9}}{2}\sqrt{20} \nonumber\\
&=
\operatorname{Luc}_{6k+9}
+
F_{6k+9}\sqrt5 \nonumber\\
&=
2\phi^{6k+9}.
\label{eq:pell-solution-binet}
\end{align}
$$

Advancing from $k$ to $k+1$ increases the Fibonacci and Lucas index by $6$. Therefore,

$$
\begin{align}
\frac{x_{k+1}+L_{k+1}\sqrt{20}}
{x_k+L_k\sqrt{20}}
&=
\frac{2\phi^{6(k+1)+9}}
{2\phi^{6k+9}} \nonumber\\
&=
\phi^6.
\end{align}
$$

A direct calculation shows that

$$
\begin{align}
\phi^6
&=
\left(\frac{1+\sqrt5}{2}\right)^6 \nonumber\\
&=
9+4\sqrt5 \nonumber\\
&=
9+2\sqrt{20}.
\label{eq:phi-six-pell-multiplier}
\end{align}
$$

This is exactly the Pell multiplier obtained from the fundamental solution $(u,v)=(9,2)$:

$$
u+v\sqrt{20}
=
9+2\sqrt{20}.
$$

The six-step jump in the Fibonacci and Lucas indices and the Pell recurrence are therefore two descriptions of the same multiplication.

For the leg lengths alone,

$$
\frac{L_{k+1}}{L_k}
=
\frac{F_{6k+15}}{F_{6k+9}}
\longrightarrow
\phi^6
=
9+4\sqrt5
\approx17.944.
$$

For the first two non-degenerate triangles,

$$
\frac{305}{17}
\approx17.941,
$$

which is already very close to the limiting factor. The solutions do not merely grow by “roughly 18”: their exponential growth is governed by the sixth power of the golden ratio.



### Summary

What began as a geometric question about integer-sided isosceles triangles led through generalized Pell equations and continued fractions to an unexpected connection with Fibonacci and Lucas numbers. The leg lengths are given by

$$
L_k=\frac{F_{6k+9}}{2},
$$

while the corresponding Pell variables are

$$
x_k=\operatorname{Luc}_{6k+9}.
$$

The indices therefore advance as $9,15,21,\ldots$, increasing by six with each new triangle. This also explains the rapid growth of the solutions: their asymptotic growth factor is

$$
\phi^6=9+4\sqrt5,
$$

which is exactly the multiplier arising from the fundamental Pell solution. The golden ratio thus enters the problem not through a familiar geometric construction, but through the arithmetic of quadratic irrationalities.




## Appendix A: Continued Fractions and Pell's Equation

This appendix collects the general facts about continued fractions that underlie the method used above. They are useful for implementing a general Pell solver, but they are not required to follow the triangle construction itself.

### Computing Convergents Efficiently

Suppose

$$
\alpha=[a_0;\,a_1,a_2,\ldots].
$$

Its convergents are written as

$$
\frac{p_k}{q_k}
=
[a_0;\,a_1,\ldots,a_k].
$$

Instead of evaluating each nested fraction from scratch, the numerators and denominators can be generated recursively:

$$
\begin{align}
p_k &= a_kp_{k-1}+p_{k-2},\\
q_k &= a_kq_{k-1}+q_{k-2},
\end{align}
$$

with initial values

$$
p_{-2}=0,\qquad p_{-1}=1,
$$

and

$$
q_{-2}=1,\qquad q_{-1}=0.
$$

For example, the coefficients of $\sqrt{20}$ begin as

$$
4,2,8,2,8,\ldots
$$

and produce

| $k$ | $a_k$ | $p_k$ | $q_k$ | $\frac{p_k}{q_k}$ |
|:---:|:---:|---:|---:|:---:|
| $0$ | $4$ | $4$ | $1$ | $\frac41$ |
| $1$ | $2$ | $9$ | $2$ | $\frac92$ |
| $2$ | $8$ | $76$ | $17$ | $\frac{76}{17}$ |
| $3$ | $2$ | $161$ | $36$ | $\frac{161}{36}$ |

### Locating the Fundamental Pell Solution

Let $D$ be a positive non-square integer and write

$$
\sqrt{D}
=
[a_0;\,\overline{a_1,\ldots,a_s}],
$$

where $s$ is the period length.

A standard result from continued-fraction theory states that the fundamental solution of

$$
u^2-Dv^2=1
$$

is obtained from a convergent of $\sqrt{D}$:

- If $s$ is even, the fundamental solution is given by

  $$
  \frac{u}{v}
  =
  [a_0;\,a_1,\ldots,a_{s-1}].
  $$

- If $s$ is odd, the period must be used twice:

  $$
  \frac{u}{v}
  =
  [a_0;\,a_1,\ldots,a_s,a_1,\ldots,a_{s-1}].
  $$

For $\sqrt{20}$, the periodic part is

$$
\overline{2,8},
$$

so the period length is $s=2$, which is even. Therefore,

$$
\frac{u}{v}
=
[4;\,2]
=
\frac92,
$$

giving

$$
(u,v)=(9,2).
$$

This parity rule guarantees that the continued-fraction algorithm terminates after at most two periods when solving the classical Pell equation.

### What the Main Article Uses

The triangle construction relies only on the following facts:

1. The continued fraction of $\sqrt{20}$ is

   $$
   [4;\,\overline{2,8}].
   $$

2. Its convergent

   $$
   [4;\,2]=\frac92
   $$

   satisfies

   $$
   9^2-20\cdot2^2=1.
   $$

3. Therefore, $(u,v)=(9,2)$ can be used as the norm-$1$ multiplier in the recurrence.

The more general theory explains why this procedure works for every classical Pell equation, while the main text only needs its concrete application to $D=20$.



## Appendix B: Matrix Diagonalization and the Growth Factor

The Fibonacci and Lucas identities give the most direct explanation of the closed forms and the factor $\phi^6$. The same growth can also be understood from the linear-algebraic structure of the Pell recurrence.

The recurrence for $(x_k,L_k)$ is

$$
\begin{pmatrix}
x_{k+1}\\
L_{k+1}
\end{pmatrix}
=
M
\begin{pmatrix}
x_k\\
L_k
\end{pmatrix},
$$

where

$$
\begin{align}
M=
\begin{pmatrix}
9&40\\
2&9
\end{pmatrix}.
\label{eq:pell-recurrence-matrix}
\end{align}
$$

Starting from

$$
\mathbf v_0=
\begin{pmatrix}
76\\
17
\end{pmatrix},
$$

the $k$-th solution is

$$
\mathbf v_k
=
\begin{pmatrix}
x_k\\
L_k
\end{pmatrix}
=
M^k\mathbf v_0.
$$

### Eigenvalues

The eigenvalues of $M$ satisfy

$$
\det(M-\lambda I)=0.
$$

Using Eq. $\eqref{eq:pell-recurrence-matrix}$,

$$
\begin{align}
\det
\begin{pmatrix}
9-\lambda&40\\
2&9-\lambda
\end{pmatrix}
&=
(9-\lambda)^2-80 \nonumber\\
&=
0.
\end{align}
$$

Therefore,

$$
(9-\lambda)^2=80,
$$

and the two eigenvalues are

$$
\begin{align}
\lambda_1=9+4\sqrt5,
\qquad
\lambda_2=9-4\sqrt5.
\label{eq:pell-matrix-eigenvalues}
\end{align}
$$

They satisfy

$$
\lambda_1\lambda_2=1,
$$

which reflects the determinant

$$
\det M=81-80=1.
$$

Moreover,

$$
\lambda_1=\phi^6
$$

and

$$
\lambda_2=\phi^{-6}.
$$

### Eigenvectors and Diagonalization

For $\lambda_1=9+4\sqrt5$, an eigenvector is

$$
\mathbf w_1=
\begin{pmatrix}
2\sqrt5\\
1
\end{pmatrix},
$$

because

$$
M\mathbf w_1
=
(9+4\sqrt5)\mathbf w_1.
$$

Similarly, for $\lambda_2=9-4\sqrt5$, an eigenvector is

$$
\mathbf w_2=
\begin{pmatrix}
-2\sqrt5\\
1
\end{pmatrix}.
$$

Thus, we may define

$$
P=
\begin{pmatrix}
2\sqrt5&-2\sqrt5\\
1&1
\end{pmatrix}
$$

and

$$
\Lambda=
\begin{pmatrix}
\lambda_1&0\\
0&\lambda_2
\end{pmatrix}.
$$

Since the two eigenvalues are distinct, $P$ is invertible and

$$
M=P\Lambda P^{-1}.
$$

Consequently,

$$
\begin{align}
M^k
=
P
\begin{pmatrix}
\lambda_1^k&0\\
0&\lambda_2^k
\end{pmatrix}
P^{-1}.
\label{eq:matrix-power-diagonalization}
\end{align}
$$

### Asymptotic Growth

Decompose the initial vector into the two eigendirections:

$$
\mathbf v_0
=
c_1\mathbf w_1+c_2\mathbf w_2.
$$

Applying $M^k$ gives

$$
\begin{align}
\mathbf v_k
=
c_1\lambda_1^k\mathbf w_1
+
c_2\lambda_2^k\mathbf w_2.
\label{eq:eigenvector-solution}
\end{align}
$$

Because

$$
\lambda_2
=
9-4\sqrt5
\approx0.0557,
$$

we have

$$
\lambda_2^k\longrightarrow0.
$$

The second term in Eq. $\eqref{eq:eigenvector-solution}$ therefore becomes exponentially small, while the first term grows like

$$
\lambda_1^k
=
\phi^{6k}.
$$

Hence,

$$
x_k\sim C_x\phi^{6k},
\qquad
L_k\sim C_L\phi^{6k}
$$

for positive constants $C_x$ and $C_L$. In particular,

$$
\frac{L_{k+1}}{L_k}
\longrightarrow
\lambda_1
=
\phi^6.
$$

The matrix analysis therefore reaches the same conclusion as the Binet identities: the dominant eigenvalue of the Pell recurrence is precisely the sixth power of the golden ratio.


**Related posts:** For a closed-form derivation of the Fibonacci sequence via the Z-transform, see [Deriving a Closed-Form Solution of the Fibonacci Sequence](/blog/2024/fibonacci-closed/). The matrix exponentiation technique used to compute Fibonacci numbers at arbitrary indices is explored in [Efficient Computation of Sparse Fibonacci Subsequences](/blog/2024/fibo-subsequences/). The [eigendecomposition](/blog/2024/eigendecomposition/) underlying the growth-factor analysis is derived there in detail. Another Diophantine problem — the Monkey and Coconut Problem — is solved in [The Monkey and Coconut Problem](/blog/2024/the-sailors-problem/).
