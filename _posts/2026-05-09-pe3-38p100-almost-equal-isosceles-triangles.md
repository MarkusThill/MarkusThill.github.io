---
layout: post
title: "[Draft] Almost-Equal Isosceles Triangles: When Height Nearly Matches Base"
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
<!--- TODO: Check the usage of $n$. There seem to be some collisions -->

Consider an isosceles triangle with two equal legs of length $$L$$ and a base of length $$b$$. Drawing the altitude from the apex to the base bisects it into two right triangles, each with hypotenuse $$L$$, one leg of length $$b/2$$, and the other equal to the height $$h$$. From the Pythagorean theorem, the height is determined by

$$
h = \sqrt{L^2 - \left(\frac{b}{2}\right)^2}.
$$

{% include figure.liquid 
   path="assets/img/2026-05-09-almost-equal-isosceles-triangles/isosceles_triangle.svg" 
   class="img-fluid rounded z-depth-1 imgcenter" 
   zoomable=true  
   width="50%" 
   caption="An isosceles triangle with equal legs \(L\), base \(b\), and altitude \(h\). The height bisects the base, creating two congruent right triangles." 
%}

For most choices of integer side lengths, the height $$h$$ is irrational. Even when it does happen to be an integer, there is typically no simple relationship between $$h$$ and the base $$b$$. But what if we demand something very specific: that the height and the base are *almost equal* -- differing by exactly one?

$$
h = b \pm 1
$$

<!--more-->

At first glance, one might expect such triangles to be exceedingly rare, or perhaps not to exist at all. But a short search reveals a first example almost immediately:

| $$b$$ | $$L$$ | $$h$$ | Relation |
|:---:|:---:|:---:|:---:|
| 16 | 17 | 15 | $$h = b - 1$$ |

Here, the two legs have length $$L = 17$$, the base is $$b = 16$$, and the height evaluates to $$h = \sqrt{17^2 - 8^2} = \sqrt{225} = 15 = b - 1$$. A perfect integer, off from the base by exactly one.

Continuing the search, a second -- considerably larger -- solution appears:

| $$b$$ | $$L$$ | $$h$$ | Relation |
|:---:|:---:|:---:|:---:|
| 16 | 17 | 15 | $$h = b - 1$$ |
| 272 | 305 | 273 | $$h = b + 1$$ |

This time, the height *exceeds* the base by one. Notice how the numbers have grown: the legs jumped from 17 to 305, and the base from 16 to 272. Is there a pattern behind this rapid growth? Are there infinitely many such triangles?

To understand where these solutions come from and whether infinitely many exist, we need to translate the geometric constraint into algebra. As we will see, this leads straight to a classical object in number theory: the **Pell equation**.

In the remainder of this post, we will:

1. Derive a Pell equation from the geometric constraint $$h = b \pm 1$$
2. Show how new solutions can be generated algebraically from known ones
3. Implement the solution in Python, including a Pell equation solver based on continued fractions
4. Tabulate the family of solutions and verify the results


## Deriving the Pell Equation

We start from the Pythagorean relation for the right triangle formed by the altitude:

$$
\begin{align}
\left(\frac{b}{2}\right)^2 + h^2 = L^2
\end{align}
$$

Replacing the height $$h$$ with $$h = b \pm 1$$:

$$
\begin{align}
\frac{1}{4}b^2 + (b \pm 1)^2 &= L^2 \nonumber \\
\frac{1}{4}b^2 + b^2 \pm 2b + 1 - L^2 &= 0 \nonumber \\
\frac{5}{4}b^2 \pm 2b + 1 - L^2 &= 0 \nonumber \\
5b^2 \pm 8b + 4 - 4L^2 &= 0 \label{eq:dioph}
\end{align}
$$

To bring this into a recognizable form, we complete the square in $$b$$. Dividing by 5:

$$
\begin{align}
b^2 \pm \frac{8}{5}b + \frac{4}{5} - \frac{4}{5}L^2 &= 0 \nonumber \\
\left(b \pm \frac{4}{5}\right)^2 - \frac{16}{25} + \frac{4}{5} - \frac{4}{5}L^2 &= 0
\end{align}
$$

Multiplying through by 25:

$$
\begin{align}
\left(5b \pm 4\right)^2 - 16 + 20 - 20L^2 &= 0 \nonumber \\
\left(5b \pm 4\right)^2 + 4 - 20L^2 &= 0
\end{align}
$$

With the substitution $$x = 5b \pm 4$$, this becomes:

$$
\begin{align}
x^2 - 20L^2 = -4 \label{eq:pell}
\end{align}
$$

This is a **generalized Pell equation**. Here, we use $$x = 5b - 4$$ when the height is one less than the base ($$h = b - 1$$), and $$x = 5b + 4$$ when the height is one more ($$h = b + 1$$). We can verify our known solution: for $$b = 16$$, $$L = 17$$, $$h = b - 1 = 15$$, we get $$x = 5 \cdot 16 - 4 = 76$$, and indeed $$76^2 - 20 \cdot 17^2 = 5776 - 5780 = -4$$.

But how do we generate more solutions?


## Generating New Solutions from Known Ones

One can show that if we have:

- one solution $$(x_n, L_n)$$ of the generalized Pell equation $$x^2 - D \cdot L^2 = n$$, and
- one solution $$(x', L')$$ of the classical Pell equation $$x'^2 - D \cdot L'^2 = 1$$,

then we can produce a *new* solution of $$x^2 - D \cdot L^2 = n$$ using the following multiplicative construction. Define:

$$
\begin{align}
\alpha &= x_n + L_n \sqrt{D} \\
\beta &= x' + L' \sqrt{D}
\end{align}
$$

Their product is:

$$
\begin{align}
\alpha \cdot \beta &= (x_n + L_n\sqrt{D})(x' + L'\sqrt{D}) \nonumber \\
&= x_n x' + x_n L'\sqrt{D} + x' L_n\sqrt{D} + L_n L' D \nonumber \\
&= (x_n x' + L_n L' D) + (x_n L' + x' L_n)\sqrt{D}
\end{align}
$$

Reading off the integer and irrational parts, the new solution is:

$$
\begin{align}
x_{n+1} &= x_n x' + L_n L' D \nonumber \\
L_{n+1} &= x_n L' + x' L_n
\end{align}
$$

Or, more compactly, in matrix form:

$$
\begin{pmatrix} x_{n+1} \\ L_{n+1} \end{pmatrix} = \begin{pmatrix} x' & L'D \\ L' & x' \end{pmatrix} \begin{pmatrix} x_n \\ L_n \end{pmatrix}
$$

**Proof.** We verify that the new pair $$(x_{n+1}, L_{n+1})$$ satisfies $$x^2 - DL^2 = n$$:

$$
\begin{align}
x_{n+1}^2 - D \cdot L_{n+1}^2 &= (x_n x' + L_n L' D)^2 - D(x_n L' + x' L_n)^2 \nonumber \\
&= x_n^2 x'^2 + 2x_n x' L_n L' D + L_n^2 L'^2 D^2 \nonumber \\
&\quad - D x_n^2 L'^2 - 2D x_n L' x' L_n - D x'^2 L_n^2
\end{align}
$$

The cross terms $$2x_n x' L_n L' D$$ cancel, and factoring the remaining four terms:

$$
\begin{align}
&= x_n^2(x'^2 - DL'^2) - DL_n^2(x'^2 - DL'^2) \nonumber \\
&= (x_n^2 - DL_n^2)\underbrace{(x'^2 - DL'^2)}_{= \, 1} = n \qquad \square
\end{align}
$$

So the strategy is clear: we need to find the fundamental solution of the classical Pell equation $$x'^2 - 20 L'^2 = 1$$, and then repeatedly apply the matrix recurrence starting from our initial solution $$(x_0, L_0) = (76, 17)$$.

A good explanation of solving the generalized Pell equation can also be found in [this video series](https://www.youtube.com/watch?v=s5RQj_Jcs0U&list=PLsT0BEyocS2L25-tI-XUrWOJVvf4N3Ivq&t=0s).


## Solving Pell's Equation with Continued Fractions

The remaining piece of the puzzle is finding the fundamental solution $$(x', L')$$ of the classical Pell equation $$x'^2 - 20 L'^2 = 1$$. The standard method uses **continued fractions**, which we briefly introduce here.

### What is a Continued Fraction?

A continued fraction is a way of representing a number as a sequence of integer "layers":

$$
a_0 + \cfrac{1}{a_1 + \cfrac{1}{a_2 + \cfrac{1}{a_3 + \cdots}}}
$$

This is written compactly as $$[a_0;\, a_1, a_2, a_3, \ldots]$$. The integers $$a_0, a_1, a_2, \ldots$$ are called the **coefficients** of the continued fraction. Every real number has a continued fraction expansion; for rational numbers it terminates, while for irrational numbers it goes on forever.

What makes continued fractions special for our purposes is a remarkable property of square roots: the continued fraction of $$\sqrt{D}$$ (for any non-square integer $$D$$) is always **periodic**. For example:

$$
\sqrt{20} = [4;\, \overline{2, 8}] = [4;\, 2, 8, 2, 8, 2, 8, \ldots]
$$

The first coefficient $$a_0 = 4 = \lfloor\sqrt{20}\rfloor$$ is just the integer part of $$\sqrt{20} \approx 4.472$$. After that, the sequence $$2, 8$$ repeats forever (indicated by the overline).

### Convergents: Rational Approximations

By truncating a continued fraction after a finite number of terms and "folding it up," we obtain a rational number called a **convergent**. Each convergent is the best possible rational approximation to the original number for its denominator size.

For $$\sqrt{20} = [4;\, \overline{2, 8}]$$, the first few convergents are computed by evaluating successively longer prefixes:

$$
\begin{array}{lcll}
[4]       &=& \dfrac{4}{1}  &= 4.000 \\[10pt]
[4;\, 2]     &=& 4 + \dfrac{1}{2} = \dfrac{9}{2}  &= 4.500 \\[10pt]
[4;\, 2, 8]  &=& 4 + \cfrac{1}{2 + \cfrac{1}{8}} = \dfrac{76}{17} &\approx 4.471
\end{array}
$$

Each convergent $$\frac{p_k}{q_k}$$ gets closer and closer to $$\sqrt{20}$$. In practice, the evaluation is done from right to left: start with the last coefficient, invert, add the previous coefficient, invert, and so on.

### The Connection to Pell's Equation

Why would continued fractions help solve $$x^2 - Dy^2 = 1$$? The connection runs through the idea of *good rational approximations*. Let us build it up step by step.

#### Step 1: Pell Solutions are Good Approximations to $$\sqrt{D}$$

Pell's equation $$x^2 - Dy^2 = 1$$ can be factored using the difference of squares:

$$
(x - y\sqrt{D})(x + y\sqrt{D}) = 1
$$

Now think about what this says. The second factor $$(x + y\sqrt{D})$$ is always a positive number. If $$x$$ and $$y$$ are both positive and not tiny, this factor is large. But the product of the two factors must equal exactly 1, so the first factor must be very small to compensate:

$$
x - y\sqrt{D} = \frac{1}{x + y\sqrt{D}}
$$

For example, if $$x = 9$$ and $$y = 2$$ (our solution for $$D = 20$$), the second factor is $$9 + 2\sqrt{20} \approx 17.94$$, so the first factor is $$1/17.94 \approx 0.056$$. Indeed, $$9 - 2\sqrt{20} \approx 0.056$$.

Dividing both sides by $$y$$:

$$
\frac{x}{y} - \sqrt{D} = \frac{1}{y(x + y\sqrt{D})}
$$

The right-hand side is tiny, which means $$\frac{x}{y}$$ is very close to $$\sqrt{D}$$. In our example: $$\frac{9}{2} = 4.5$$, while $$\sqrt{20} \approx 4.472$$. Close!

So we have established: **any solution $$(x, y)$$ of Pell's equation gives a rational number $$\frac{x}{y}$$ that is very close to $$\sqrt{D}$$.**


#### Step 2: The Best Approximations are Convergents

There is a classical theorem in number theory that says: the *best* rational approximations to any irrational number are exactly the **convergents** of its continued fraction. "Best" here means that no other fraction with a smaller-or-equal denominator gets closer to the target.

Since Pell solutions produce excellent approximations to $$\sqrt{D}$$ (as we just showed in Step 1), they must appear among the convergents of the continued fraction of $$\sqrt{D}$$.

This gives us a search strategy: compute convergents $$\frac{p_0}{q_0}, \frac{p_1}{q_1}, \frac{p_2}{q_2}, \ldots$$ of $$\sqrt{D}$$ one by one, and check each pair $$(p_k, q_k)$$ against $$p_k^2 - D q_k^2 = 1$$. If a convergent satisfies this, we have found the fundamental solution.

But will the search actually succeed? Could it be that we keep checking convergents forever and never hit $$+1$$? Let us see why that cannot happen.


#### Step 3: Convergents Always Have a Small Pell Residual

Define the **Pell residual** of a convergent $$\frac{p_k}{q_k}$$ as the integer

$$
r_k = p_k^2 - D \cdot q_k^2.
$$

If $$r_k = 1$$ for some $$k$$, we have a Pell solution. But what can we say about $$r_k$$ in general?

Using the factoring trick again:

$$
r_k = p_k^2 - D \cdot q_k^2 = \underbrace{(p_k - q_k\sqrt{D})}_{\text{first factor}} \cdot \underbrace{(p_k + q_k\sqrt{D})}_{\text{second factor}}
$$

Let us estimate each factor separately.

**First factor.** Since $$\frac{p_k}{q_k} \approx \sqrt{D}$$, we have $$p_k \approx q_k\sqrt{D}$$, so the difference $$p_k - q_k\sqrt{D}$$ is close to zero. How close? A standard result about continued fractions gives a precise bound:

$$
\left|p_k - q_k\sqrt{D}\right| < \frac{1}{q_{k+1}}
$$

where $$q_{k+1}$$ is the denominator of the *next* convergent (which is always larger than $$q_k$$).

**Second factor.** Since $$p_k \approx q_k\sqrt{D}$$, the sum $$p_k + q_k\sqrt{D}$$ is approximately $$q_k\sqrt{D} + q_k\sqrt{D} = 2q_k\sqrt{D}$$. For a precise upper bound, we can use the fact that consecutive convergents satisfy $$q_k < q_{k+1}$$ and $$p_k < p_{k+1} < q_{k+1}\sqrt{D} + 1$$, which gives $$p_k + q_k\sqrt{D} < 2q_{k+1}\sqrt{D}$$.

**Combining both.** Multiplying the bounds:

$$
|r_k| = |p_k - q_k\sqrt{D}| \cdot (p_k + q_k\sqrt{D}) < \frac{1}{q_{k+1}} \cdot 2q_{k+1}\sqrt{D} = 2\sqrt{D}
$$

The $$q_{k+1}$$ cancels — this is why the bound depends only on $$D$$, not on which convergent we pick.

So the residual is always bounded:

$$
|p_k^2 - D \cdot q_k^2| < 2\sqrt{D}
$$

For $$D = 20$$, this gives 

$$
\begin{align*}
\big|r_k| < 2\sqrt{20} \approx 8.9
\end{align*}.
$$

Since $$r_k$$ is always an integer, the only possible values are $$\{-8, -7, \ldots, -1, 0, 1, \ldots, 7, 8\}$$ — at most 17 distinct values.


#### Step 4: Why $$+1$$ Must Appear

**Goal.** We want to show that among the convergents of $$\sqrt{D}$$, there is always one whose numerator $$p_k$$ and denominator $$q_k$$ satisfy $$p_k^2 - Dq_k^2 = 1$$ exactly. This is what makes the continued fraction method a *guaranteed* algorithm for solving Pell's equation, not just a heuristic.

**The pigeonhole argument.** We have established two facts:

1. The continued fraction of $$\sqrt{D}$$ is periodic, so it produces **infinitely many** convergents $$\frac{p_0}{q_0}, \frac{p_1}{q_1}, \frac{p_2}{q_2}, \ldots$$
2. Each convergent's Pell residual $$r_k = p_k^2 - Dq_k^2$$ lies in a **finite** set (at most $$2\lfloor 2\sqrt{D} \rfloor + 1$$ distinct integer values).

Infinitely many convergents, but only finitely many possible residuals — by the pigeonhole principle, some residual value $$r$$ must occur at least twice. That is, there exist two *different* convergents $$i \ne j$$ with

$$
p_i^2 - Dq_i^2 = r \qquad \text{and} \qquad p_j^2 - Dq_j^2 = r.
$$

**Combining two convergents with the same residual.** We now show that from these two convergents we can construct a solution to $$X^2 - DY^2 = 1$$. The idea is to *divide* one by the other, which causes the shared residual $$r$$ to cancel.

To each convergent, associate the expression $$\alpha_k = p_k + q_k\sqrt{D}$$. Its **conjugate** is $$\bar{\alpha}_k = p_k - q_k\sqrt{D}$$, and their product is:

$$
\alpha_k \cdot \bar{\alpha}_k = (p_k + q_k\sqrt{D})(p_k - q_k\sqrt{D}) = p_k^2 - Dq_k^2 = r_k
$$

This product $$\alpha_k \cdot \bar{\alpha}_k$$ is just the Pell residual $$r_k$$, written in factored form. Now consider the ratio of $$\alpha_i$$ and $$\alpha_j$$. We multiply by the conjugate of the denominator:

$$
\frac{\alpha_i}{\alpha_j} = \frac{p_i + q_i\sqrt{D}}{p_j + q_j\sqrt{D}} \cdot \frac{p_j - q_j\sqrt{D}}{p_j - q_j\sqrt{D}} = \frac{(p_i + q_i\sqrt{D})(p_j - q_j\sqrt{D})}{\underbrace{p_j^2 - Dq_j^2}_{= \, r}}
$$

The denominator is $$r_j = r$$. We expand the numerator:

$$
(p_i + q_i\sqrt{D})(p_j - q_j\sqrt{D}) = \underbrace{(p_i p_j - D q_i q_j)}_{A} + \underbrace{(q_i p_j - p_i q_j)}_{B} \cdot \sqrt{D}
$$

Dividing by $$r$$, the ratio has the form $$X + Y\sqrt{D}$$ with:

$$
X = \frac{p_i p_j - D q_i q_j}{r} = \frac{A}{r}, \qquad Y = \frac{q_i p_j - p_i q_j}{r} = \frac{B}{r}
$$

**Computing the residual of the new pair.** We want to show $$X^2 - DY^2 = 1$$. Recall from the difference-of-squares factoring that for *any* two numbers $$X, Y$$:

$$
X^2 - DY^2 = (X + Y\sqrt{D})(X - Y\sqrt{D})
$$

So if we can figure out what $$X + Y\sqrt{D}$$ and $$X - Y\sqrt{D}$$ are, we can compute $$X^2 - DY^2$$ without ever squaring $$X$$ and $$Y$$ individually.

We already know $$X + Y\sqrt{D}$$: it is exactly the ratio we computed above,

$$
X + Y\sqrt{D} = \frac{\alpha_i}{\alpha_j} = \frac{p_i + q_i\sqrt{D}}{p_j + q_j\sqrt{D}}.
$$

What about $$X - Y\sqrt{D}$$? Since $$X$$ and $$Y$$ are specific real numbers (defined by the formulas above), the expression $$X - Y\sqrt{D}$$ is obtained by simply flipping the sign on the $$\sqrt{D}$$ term. This is the same as replacing every $$\sqrt{D}$$ with $$-\sqrt{D}$$ in the ratio, which gives:

$$
X - Y\sqrt{D} = \frac{p_i - q_i\sqrt{D}}{p_j - q_j\sqrt{D}} = \frac{\bar{\alpha}_i}{\bar{\alpha}_j}
$$

Now we multiply them:

$$
\begin{align}
X^2 - DY^2 &= (X + Y\sqrt{D})(X - Y\sqrt{D}) \nonumber \\
&= \frac{\alpha_i}{\alpha_j} \cdot \frac{\bar{\alpha}_i}{\bar{\alpha}_j} = \frac{\alpha_i \cdot \bar{\alpha}_i}{\alpha_j \cdot \bar{\alpha}_j} = \frac{r_i}{r_j} = \frac{r}{r} = 1
\end{align}
$$

Since both convergents have the same residual $$r$$, the ratio is exactly 1. So $$(X, Y)$$ solves $$X^2 - DY^2 = 1$$ — the classical Pell equation.

**What this proves — and what remains.** The argument above shows that $$X^2 - DY^2 = 1$$ as real numbers. But we defined $$X = A/r$$ and $$Y = B/r$$, and there is no guarantee yet that $$r$$ divides $$A$$ and $$B$$ — so $$X$$ and $$Y$$ might be fractions rather than integers. Also, the pair $$(X, Y)$$ was constructed by combining two convergents — it is not itself necessarily a convergent of $$\sqrt{D}$$. We address both points in turn.

**Integrality.** To ensure $$r \mid A$$ and $$r \mid B$$, we sharpen the pigeonhole step. Since there are infinitely many convergents but only finitely many residual values, in fact some residual $$r$$ occurs *infinitely* often (not just twice). Among these infinitely many convergents, each also carries a pair of residue classes 

$$
\begin{equation*}
(p_k \bmod |r|, \; q_k \bmod |r|), 
\end{equation*}
$$

which takes at most $$\left\lvert r  \right\rvert ^2$$ values. By a second application of pigeonhole, two of them — $$(p_i, q_i)$$ and $$(p_j, q_j)$$ — must satisfy:

$$
p_i \equiv p_j \pmod{|r|}, \qquad q_i \equiv q_j \pmod{|r|}
$$

With these congruences, divisibility follows immediately:

$$
A = p_ip_j - Dq_iq_j \equiv p_i^2 - Dq_i^2 = r \equiv 0 \pmod{|r|}
$$

$$
B = q_ip_j - p_iq_j \equiv q_ip_i - p_iq_i = 0 \pmod{|r|}
$$

So $$X$$ and $$Y$$ are genuine integers, and $$(X, Y)$$ is a solution to Pell's equation in positive integers.

**The algorithm terminates.** We have now proved that a Pell solution exists. By Step 1, any such solution $$(X, Y)$$ satisfies $$X/Y \approx \sqrt{D}$$ with exceptional precision; by Step 2, the best rational approximations to $$\sqrt{D}$$ are exactly its convergents. Therefore $$X/Y$$ must appear as some convergent $$p_k/q_k$$, which means that convergent directly has residual $$+1$$. Our algorithm — computing convergents one by one and checking $$p_k^2 - Dq_k^2 = 1$$ — is guaranteed to find it.

For $$D = 20$$, the algorithm succeeds immediately: the convergent $$[4;\, 2] = \frac{9}{2}$$ gives $$9^2 - 20 \cdot 2^2 = 1$$.


### Worked Example: $$\sqrt{20}$$

Let us see the full picture for our problem. The continued fraction of $$\sqrt{20}$$ is $$[4;\, \overline{2, 8}]$$, and for each convergent we compute the fraction, its decimal value, and the Pell residual:

| Convergent | $$\frac{p_k}{q_k}$$ | Decimal | $$p_k^2 - 20 \cdot q_k^2$$ |
|:---:|:---:|:---:|:---:|
| $$[4]$$ | $$\frac{4}{1}$$ | $$4.000$$ | $$16 - 20 = -4$$ |
| $$[4;\, 2]$$ | $$\frac{9}{2}$$ | $$4.500$$ | $$81 - 80 = 1$$ |
| $$[4;\, 2, 8]$$ | $$\frac{76}{17}$$ | $$4.471$$ | $$5776 - 5780 = -4$$ |
| $$[4;\, 2, 8, 2]$$ | $$\frac{161}{36}$$ | $$4.472$$ | $$25921 - 25920 = 1$$ |
| $$[4;\, 2, 8, 2, 8]$$ | $$\frac{1364}{305}$$ | $$4.472$$ | $$1860496 - 1860500 = -4$$ |
| $$[4;\, 2, 8, 2, 8, 2]$$ | $$\frac{2889}{646}$$ | $$4.472$$ | $$8346321 - 8346320 = 1$$ |

As predicted, $$\lvert p_k^2 - 20 \cdot q_k^2 \rvert$$ stays small (always 4 or 1, well below the bound $$2\sqrt{20} \approx 8.9$$). The residuals alternate between $$-4$$ and $$+1$$ with perfect regularity, reflecting the period-2 structure of the continued fraction. The decimal values oscillate around $$\sqrt{20} \approx 4.4721$$, converging rapidly.

Already at the second convergent we hit $$9^2 - 20 \cdot 2^2 = 1$$, so $$(x', L') = (9, 2)$$ is the fundamental solution.

Notice also the third row: $$(76, 17)$$ satisfies $$x^2 - 20L^2 = -4$$, which is precisely the initial solution of *our* generalized Pell equation from Eq. \eqref{eq:pell}. This is not a coincidence. The same reasoning from Step 1 applies: any solution of $$x^2 - Dy^2 = n$$ with small $$\lvert n \rvert$$ gives a good rational approximation $$x/y \approx \sqrt{D}$$, since

$$
\frac{x}{y} - \sqrt{D} = \frac{n}{y(x + y\sqrt{D})}
$$

which is tiny whenever $$\lvert n \rvert$$ is small relative to the denominator. So such solutions must also appear among the convergents. In particular, we never needed to *guess* the initial solution $$(76, 17)$$ — scanning the convergents of $$\sqrt{20}$$ would have found it automatically, right alongside the classical Pell solution $$(9, 2)$$.

More generally, for any generalized Pell equation $$x^2 - Dy^2 = n$$ where $$\lvert n \rvert < 2\sqrt{D}$$, solutions (if they exist) can be found by the same continued fraction search. The bound from Step 3 guarantees that $$n$$ is within the range of possible convergent residuals, and our algorithm can simply check for $$r_k = n$$ in addition to $$r_k = 1$$.

Conversely, the convergent residuals also tell us when an equation has *no* solution. Since the continued fraction of $$\sqrt{D}$$ is periodic with some period $$s$$, the residual sequence $$r_0, r_1, r_2, \ldots$$ is eventually periodic with the same period. So one only needs to examine the first $$s + 1$$ convergents (one full period plus the initial term) to see every residual value that will ever occur. If a particular $$n$$ with $$\lvert n \rvert < 2\sqrt{D}$$ does not appear among these residuals, the equation $$x^2 - Dy^2 = n$$ has no integer solution. For $$D = 20$$, the period is $$s = 2$$ and the residuals cycle as $$-4, 1, -4, 1, \ldots$$ — so among all integers $$n$$ with $$\lvert n \rvert < 2\sqrt{20} \approx 8.9$$, only $$n = -4$$ and $$n = 1$$ yield solvable equations. For instance, $$x^2 - 20y^2 = -5$$ has no solution (which can also be confirmed by noting that $$x^2 \equiv 15 \pmod{20}$$ has no solution, since 15 is not a quadratic residue mod 20).


## Implementation in Python

### Solving the Classical Pell Equation via Continued Fractions

With the theory in place, we turn to implementation. The central routine is `cont_fraction_sqrt`, which computes the coefficients $$[a_0;\, a_1, a_2, \ldots]$$ of the continued fraction of $$\sqrt{n}$$.

#### How the Algorithm Works

Recall from the definition that a continued fraction is built by repeating three operations: given a number $$x_k > 1$$, (1) extract its integer part $$a_k = \lfloor x_k \rfloor$$, (2) subtract to get the fractional remainder $$x_k - a_k$$, and (3) invert to obtain the next number $$x_{k+1} = 1/(x_k - a_k)$$. This produces $$x_k = a_k + 1/x_{k+1}$$, which is exactly one layer of the continued fraction.

Let us trace what happens when we apply this to $$\sqrt{n}$$.

**First step.** We start with $$x_0 = \sqrt{n}$$. The integer part is $$a_0 = \lfloor\sqrt{n}\rfloor$$. Subtracting and inverting:

$$
x_1 = \frac{1}{\sqrt{n} - a_0}
$$

This involves an irrational denominator, so we rationalize by multiplying by $$(\sqrt{n} + a_0)/(\sqrt{n} + a_0)$$:

$$
x_1 = \frac{\sqrt{n} + a_0}{(\sqrt{n})^2 - a_0^2} = \frac{\sqrt{n} + a_0}{n - a_0^2}
$$

Notice the form: $$x_1 = (\sqrt{n} + m_1) / d_1$$ with $$m_1 = a_0$$ and $$d_1 = n - a_0^2$$. So after just one step, the tail of the continued fraction is a ratio involving $$\sqrt{n}$$ plus an integer, divided by another integer.

**The key observation** is that this form is preserved at every subsequent step. If the current tail is

$$
x_k = \frac{\sqrt{n} + m_k}{d_k}
$$

then extracting, subtracting, inverting, and rationalizing will produce $$x_{k+1} = (\sqrt{n} + m_{k+1})/d_{k+1}$$ for new integers $$m_{k+1}, d_{k+1}$$. The integers $$m_k$$ and $$d_k$$ always satisfy the invariant $$d_k \mid (n - m_k^2)$$, which guarantees that $$d_{k+1}$$ comes out as a positive integer (rather than a fraction).

Let us work through the general step to derive the update formulas.

At each step, we extract the next coefficient $$a_k$$ and update $$(m_k, d_k)$$:

**1. Extract the integer part:**

$$
a_k = \left\lfloor \frac{\sqrt{n} + m_k}{d_k} \right\rfloor = \left\lfloor \frac{a_0 + m_k}{d_k} \right\rfloor
$$

where $$a_0 = \lfloor\sqrt{n}\rfloor$$. (The second equality holds because $$\sqrt{n}$$ and $$a_0$$ share the same fractional part behavior under the divisibility invariant.)

**2. Compute the remainder and take its reciprocal.** After subtracting $$a_k$$, the remainder is:

$$
\frac{\sqrt{n} + m_k}{d_k} - a_k = \frac{\sqrt{n} + m_k - a_k d_k}{d_k} = \frac{\sqrt{n} - (a_k d_k - m_k)}{d_k}
$$

Setting $$m_{k+1} = a_k d_k - m_k$$, the reciprocal of this remainder is:

$$
\frac{d_k}{\sqrt{n} - m_{k+1}}
$$

**3. Rationalize the denominator.** Multiplying numerator and denominator by $$(\sqrt{n} + m_{k+1})$$:

$$
\frac{d_k(\sqrt{n} + m_{k+1})}{n - m_{k+1}^2} = \frac{\sqrt{n} + m_{k+1}}{(n - m_{k+1}^2)/d_k}
$$

Setting $$d_{k+1} = (n - m_{k+1}^2) / d_k$$, we arrive at:

$$
\frac{\sqrt{n} + m_{k+1}}{d_{k+1}}
$$

This has the same form as the starting expression, so we can repeat the process. The three update rules are:

$$
m_{k+1} = a_k d_k - m_k, \qquad d_{k+1} = \frac{n - m_{k+1}^2}{d_k}, \qquad a_{k+1} = \left\lfloor\frac{a_0 + m_{k+1}}{d_{k+1}}\right\rfloor
$$

**Why $$d_{k+1}$$ is always a positive integer.** The formula $$d_{k+1} = (n - m_{k+1}^2)/d_k$$ involves a division, so we should verify that it always produces a positive integer.

*Integer:* We need to show that $$d_k \mid (n - m_k^2)$$ holds for all $$k \geq 0$$. We prove this by induction.

**Base case.** The algorithm starts with $$m_0 = 0$$ and $$d_0 = 1$$. Since every integer is divisible by 1, we have $$d_0 \mid (n - m_0^2)$$ trivially. After the first iteration, $$m_1 = a_0$$ and $$d_1 = n - a_0^2$$, so $$d_1 \mid (n - m_1^2)$$ holds as well ($$n - a_0^2 = d_1$$ divides itself).

**Inductive step.** Assume that $$d_k \mid (n - m_k^2)$$ holds at step $$k$$. We show it carries over to step $$k+1$$, i.e., that $$d_k \mid (n - m_{k+1}^2)$$ (which makes $$d_{k+1}$$ an integer) and then $$d_{k+1} \mid (n - m_{k+1}^2)$$ (which is the invariant at step $$k+1$$).

1. Since $$m_{k+1} = a_k d_k - m_k$$, the term $$a_k d_k$$ is a multiple of $$d_k$$, so $$m_{k+1} \equiv -m_k \pmod{d_k}$$. Squaring both sides: $$m_{k+1}^2 \equiv m_k^2 \pmod{d_k}$$. Therefore $$n - m_{k+1}^2 \equiv n - m_k^2 \pmod{d_k}$$.
2. By the inductive hypothesis, $$n - m_k^2 \equiv 0 \pmod{d_k}$$.

Combining: $$n - m_{k+1}^2 \equiv 0 \pmod{d_k}$$, so the division $$d_{k+1} = (n - m_{k+1}^2)/d_k$$ produces an integer. And since $$d_{k+1} \cdot d_k = n - m_{k+1}^2$$, we also have $$d_{k+1} \mid (n - m_{k+1}^2)$$, establishing the invariant at step $$k+1$$. $$\square$$

*Positive:* Since $$a_k = \lfloor(\sqrt{n} + m_k)/d_k\rfloor$$ and $$\sqrt{n}$$ is irrational, the floor is strictly less than the value: $$a_k < (\sqrt{n} + m_k)/d_k$$. Rearranging gives $$m_{k+1} = a_k d_k - m_k < \sqrt{n}$$, and therefore $$n - m_{k+1}^2 > 0$$. Since $$d_k > 0$$ as well, the quotient $$d_{k+1}$$ is positive.

Since both $$m_k$$ and $$d_k$$ are bounded (one can show they stay below $$\sqrt{n}$$ and $$2\sqrt{n}$$ respectively), there are only finitely many possible states $$(m_k, d_k)$$. Eventually a state must repeat, at which point the coefficients begin to cycle — this is how the algorithm detects the period.

```python
from math import isqrt


def cont_fraction_sqrt(n, max_coeffs=100):
    """Compute the periodic continued fraction expansion of sqrt(n).
    Returns (coefficients, period_length), or (None, 0) for perfect squares.
    """
    a0 = isqrt(n)
    if a0 * a0 == n:
        return None, 0

    coeffs = [a0]
    seen = {}
    m, d, a = 0, 1, a0

    for i in range(max_coeffs):
        m = d * a - m           # m_{k+1} = a_k * d_k - m_k
        d = (n - m * m) // d    # d_{k+1} = (n - m_{k+1}^2) / d_k
        a = (a0 + m) // d       # a_{k+1} = floor((a0 + m_{k+1}) / d_{k+1})
        state = (m, d)
        if state in seen:
            return coeffs, i - seen[state]
        seen[state] = i
        coeffs.append(a)

    return coeffs, None


def evaluate_continued_fraction(coeffs):
    """Evaluate [a0; a1, a2, ...] and return (numerator, denominator)."""
    num, den = 1, 0
    for a in reversed(coeffs):
        num, den = den, num
        num += a * den
    return num, den


def solve_pell(d):
    """Find the fundamental solution (x, y) of x^2 - d*y^2 = 1
    using the continued fraction expansion of sqrt(d).
    """
    coeffs, period = cont_fraction_sqrt(d)
    if coeffs is None:
        return None, None

    extended = coeffs + coeffs[1:] * 2
    for i in range(1, len(extended) + 1):
        x, y = evaluate_continued_fraction(extended[:i])
        if x * x - d * y * y == 1:
            return x, y

    return None, None
```

For our problem, $$D = 20$$. The continued fraction of $$\sqrt{20}$$ is $$[4; \overline{2, 8}]$$ with period 2, and the algorithm finds the fundamental solution $$(x', L') = (9, 2)$$:

```python
D = 20
xp, yp = solve_pell(D)
print(f"Fundamental solution of x'^2 - {D}*y'^2 = 1: ({xp}, {yp})")
print(f"Verification: {xp}^2 - {D}*{yp}^2 = {xp**2 - D * yp**2}")
```

```
Fundamental solution of x'^2 - 20*y'^2 = 1: (9, 2)
Verification: 9^2 - 20*2^2 = 1
```

### Computing the Triangle Solutions

With the fundamental solution in hand, we repeatedly apply the matrix recurrence to generate as many triangle solutions as desired. For each generated pair $$(x, L)$$, we recover $$b$$ by checking which of $$(x + 4)/5$$ or $$(x - 4)/5$$ yields an integer:

```python
n_solutions = 20  # increase to generate more solutions

# Initial solution: b=16, L=17, h=b-1=15, giving x = 5*16 - 4 = 76
x, L = 76, 17

solutions = []
for _ in range(n_solutions):
    if (x + 4) % 5 == 0:
        b = (x + 4) // 5
        h = b - 1
    else:
        b = (x - 4) // 5
        h = b + 1
    solutions.append((b, L, h))

    # Apply the recurrence: (x, L) -> (x*xp + L*yp*D, x*yp + L*xp)
    x, L = x * xp + L * yp * D, x * yp + L * xp

# Display
for i, (b, L, h) in enumerate(solutions, 1):
    rel = "h = b - 1" if h == b - 1 else "h = b + 1"
    print(f"{i:>2}. b={b}, L={L}, h={h}  ({rel})")
```

### Alternative: Direct Recurrence Relations

An alternative approach avoids the continued fraction machinery entirely. The quadratic Diophantine equation $$5b^2 \pm 8b + 4 - 4L^2 = 0$$ can be fed into a [specialized solver](https://www.alpertron.com.ar/QUAD.HTM), which produces affine recurrence relations that act directly on $$(b, L)$$:

```python
def solver(b, L, cb, cL, n_runs=30):
    """Apply an affine recurrence to generate L values."""
    result = []
    for _ in range(n_runs):
        b, L = (cb[0]*b + cb[1]*L + cb[2],
                cL[0]*b + cL[1]*L + cL[2])
        if b > 0 and L > 0:
            result.append(L)
    return result

all_L = sorted(
    solver(0,  1, (-9, -8, -8), (-10, -9, -8)) +
    solver(0,  1, (-9,  8, -8), ( 10, -9,  8)) +
    solver(0, -1, (-9, -8,  8), (-10, -9,  8)) +
    solver(0, -1, (-9,  8,  8), ( 10, -9, -8))
)[:n_solutions]
```

The four calls correspond to the four solution families of the two equations ($$\pm$$ in Eq. \eqref{eq:dioph}) with two sign choices each. This method is more compact but treats the recurrence coefficients as given rather than derived.


## Results

The first 15 solutions, sorted by $$L$$:

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

The solutions alternate between $$h = b - 1$$ and $$h = b + 1$$, with the numbers growing rapidly — each successive $$L$$ is roughly 18 times the previous one. By increasing `n_solutions`, the code can generate arbitrarily many solutions in this family.


## Connection to Fibonacci and Lucas Numbers

The factor of "roughly 18" is not a coincidence — it is $$\phi^6$$, where $$\phi = (1+\sqrt{5})/2$$ is the golden ratio. In fact, the entire solution family is intimately connected to Fibonacci and Lucas numbers.

### The Link Through the Lucas–Fibonacci Identity

Recall the classical identity relating Lucas numbers $$\mathcal{L}_n$$ and Fibonacci numbers $$F_n$$:

$$
\mathcal{L}_n^2 - 5 F_n^2 = 4(-1)^n
$$

Now compare this with our generalized Pell equation $$x^2 - 20y^2 = -4$$. Rewriting the latter by factoring $$20 = 4 \cdot 5$$:

$$
x^2 - 5(2y)^2 = -4
$$

Matching terms with the Lucas–Fibonacci identity (for odd $$n$$, where the right-hand side is $$-4$$):

$$
x = \mathcal{L}_n, \qquad 2y = F_n \quad \Longrightarrow \quad y = \frac{F_n}{2}
$$

For $$y$$ to be an integer, we need $$F_n$$ to be even. Fibonacci numbers are even precisely when $$n \equiv 0 \pmod{3}$$. Combined with the requirement that $$n$$ be odd (for the $$-4$$ sign), we need:

$$
n \equiv 3 \pmod{6}
$$

That is, $$n = 9, 15, 21, 27, 33, \ldots$$ (skipping $$n = 3$$ which gives the degenerate solution with $$b = 0$$).

### Verification

Let us check the first few cases against known Fibonacci and Lucas numbers:

| $$n$$ | $$\mathcal{L}_n$$ | $$F_n$$ | $$y = F_n/2$$ | Matches $$L$$ in table? |
|:---:|:---:|:---:|:---:|:---:|
| 9 | 76 | 34 | 17 | $$\checkmark$$ |
| 15 | 1364 | 610 | 305 | $$\checkmark$$ |
| 21 | 24476 | 10946 | 5473 | $$\checkmark$$ |
| 27 | 439204 | 196418 | 98209 | $$\checkmark$$ |

Every leg length in the solution table is half a Fibonacci number, and the corresponding Pell variable $$x$$ is a Lucas number — both taken at indices $$9, 15, 21, 27, \ldots$$

### Why the Growth Factor is $$\phi^6$$

Recall that each new solution is obtained by multiplying the previous one by the recurrence matrix:

$$
M = \begin{pmatrix} 9 & 40 \\ 2 & 9 \end{pmatrix}
$$

(using $$x' = 9$$, $$L' = 2$$, $$D = 20$$). The $$k$$-th solution is given by $$M^k \mathbf{v}_0$$, where $$\mathbf{v}_0 = (x_0, L_0)^T$$ is the initial solution. To understand the growth, we diagonalize $$M$$.

The eigenvalues satisfy $$\det(M - \lambda I) = (9 - \lambda)^2 - 80 = 0$$, giving:

$$
\lambda_1 = 9 + 4\sqrt{5}, \qquad \lambda_2 = 9 - 4\sqrt{5}
$$

Since $$M$$ has two distinct eigenvalues, it admits a diagonalization $$M = P \Lambda P^{-1}$$ with $$\Lambda = \mathrm{diag}(\lambda_1, \lambda_2)$$. Raising to the $$k$$-th power becomes trivial:

$$
M^k = P \begin{pmatrix} \lambda_1^k & 0 \\ 0 & \lambda_2^k \end{pmatrix} P^{-1}
$$

The key observation is that $$\lambda_2 = 9 - 4\sqrt{5} \approx 0.056$$, so $$\lvert \lambda_2 \rvert < 1$$. As $$k$$ grows, $$\lambda_2^k \to 0$$ exponentially fast, leaving only the $$\lambda_1^k$$ term:

$$
\begin{pmatrix} x_k \\ L_k \end{pmatrix} = M^k \mathbf{v}_0 \;\approx\; \lambda_1^k \cdot P \begin{pmatrix} 1 \\ 0 \end{pmatrix} (P^{-1} \mathbf{v}_0)_1
$$

In other words, both $$x_k$$ and $$L_k$$ grow asymptotically as $$\lambda_1^k$$, and the ratio $$L_{k+1}/L_k \to \lambda_1$$ rapidly. We can identify $$\lambda_1$$ directly with a power of the golden ratio:

$$
\phi^6 = \left(\frac{1+\sqrt{5}}{2}\right)^6 = (2 + \sqrt{5})^2 = 9 + 4\sqrt{5} = \lambda_1
$$

So the ratio $$L_{k+1}/L_k \to \phi^6 \approx 17.944$$, and the convergence is fast: already at the first step, $$L_2/L_1 = 305/17 \approx 17.941$$, which differs from $$\phi^6$$ only in the third decimal place (because $$\lambda_2^1 \approx 0.056$$ is already negligible). The solutions do not merely grow "roughly" by 18 — they grow by the sixth power of the golden ratio, a reflection of the Fibonacci/Lucas structure underlying the problem.

### Summary

What began as a geometric curiosity about isosceles triangles led through Pell equations and continued fractions to a surprising endpoint: the leg lengths of these triangles are Fibonacci numbers (divided by 2) at arithmetic-progression indices, the substitution variables are Lucas numbers at those same indices, and the explosive growth of solutions is governed by $$\phi^6$$. The golden ratio, often encountered in geometry through pentagons and spirals, appears here through a completely different door — the arithmetic of quadratic irrationals.
