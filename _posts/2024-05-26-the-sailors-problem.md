---
layout: post
title: The Monkey and Coconut Problem
modified:
categories: [math, riddles]
description: "Three sailors and a monkey are stranded on a deserted island. They gather a pile of coconuts to divide the next morning. During the night, each sailor wakes up, divides the pile into three parts, gives the extra coconut to the monkey, hides his share, and restacks the remaining coconuts. In the morning, the remaining coconuts are again divided into three parts, with one coconut left over, which is given to the monkey.

The question is: how many coconuts were originally in the pile?"
thumbnail: assets/img/monkey-coconut-problem.webp
giscus_comments: true
toc:
  sidebar: left
date: 2024-05-26
---


Three sailors, stranded on a deserted island with a monkey, gather a pile of coconuts to be divided among themselves the next morning. During the night, one of the sailors wakes up, secretly divides the pile into three equal parts, and finds an extra coconut, which he gives to the monkey. He hides his share and combines the remaining coconuts back into a single heap. Later that night, the second sailor does the same: dividing the pile into three equal parts, giving the leftover coconut to the monkey, hiding his share, and returning the rest to the heap. The third sailor repeats the process in the same manner. 

The next morning, the sailors divide the remaining pile of coconuts into three equal parts, once again finding an extra coconut, which they give to the monkey. 

The question is: how many coconuts were originally in the pile?

Additionally, a general solution should be determined for $$n$$ coconuts, $$k$$ sailors, and $$m$$ monkeys.


<!--more-->

## Derivation

So, let us start writing down the given information in a more mathematical form, but without too much strict math.

To summarize, we have a number of sailors:
$$
\begin{align}
k \in \mathbb{N_+} \backslash \{ 1\}
\end{align}
$$
where  $$\mathbb{N_+}$$ is the set of positive natural numbers, and $$k = 1$$ is excluded since only one sailor is not interesting for this problem.

The number of coconuts collected by the sailors before the night:
$$
\begin{align}
n \in \mathbb{N_+},
\end{align}
$$
which must also be a positive natural number.

Finally, the number of monkeys is given by:
$$
\begin{align}
m \in \mathbb{N_+}, \  m < k,
\end{align}
$$
indicating that there are fewer monkeys than sailors.


The first sailor, who wakes up first, divides the number of coconuts by the number of sailors. He gives the remaining coconuts to the monkeys. This results in $$k$$ shares, each of size $$(n-m)/k$$. The first sailor buries his (stolen) share, leaving behind the following number of coconuts:  
\begin{align}
	n_1 = \frac{n-m}{k}(k-1)=(n-m)\frac{k-1}{k} \label{eq:n1}
\end{align}

The second sailor, who wakes up next, repeats the procedure of the first sailor:
$$
\begin{align}
	n_2 &= (n_1-m)\frac{k-1}{k}=\big((n-m)\frac{k-1}{k} -m  \big) \frac{k-1}{k} \\  
	&= (n-m) \big(\frac{k-1}{k} \big)^2 - m\frac{k-1}{k}
\end{align}
$$

Then, the third sailor wakes up and performs the same process:
$$
\begin{align}
	n_3 &= \Bigg(\bigg((n-m)\frac{k-1}{k}-m\bigg)\frac{k-1}{k} - m\Bigg) \frac{k-1}{k} \\  
	&= (n-m) \Big(\frac{k-1}{k}\Big)^3 - m\Big(\frac{k-1}{k}\Big)^2 - m\frac{k-1}{k}
\end{align}
$$

For the $$i$$-th sailor, where $$1 \leq i \leq k$$, we derive the general recursive rule:
$$
\begin{align}
	n_i = (n_{i-1}-m)\frac{k-1}{k}.
\end{align}
$$

For every sailor, we subtract $$m$$ coconuts from the previous count $$n_{i-1}$$, and then multiply by $$\frac{k-1}{k}$$. This relationship can also be expressed as (for $$i > 1$$):


$$
\begin{align}
	n_i &= (n-m)\bigg(\frac{k-1}{k} \bigg)^i - m\bigg(\frac{k-1}{k} \bigg)^{i-1} - \ldots - m\frac{k-1}{k} \\
	&= (n-m)\bigg(\frac{k-1}{k} \bigg)^i - m\sum_{\substack{j=1 \\ i>1}}^{i-1}\bigg(\frac{k-1}{k} \bigg)^j
\end{align}
$$
For our convenience, we define the initial number of coconuts as $$n_0 = n$$. Hence, we can write $$n_i$$ for all $$0 \leq i\leq k$$ as:
$$
\begin{align}
	n_i=\begin{cases}
		n, & \mbox{for} \ i=0 \\
		(n-m)\bigg(\frac{k-1}{k} \bigg)^i - m\sum\limits_{\substack{j=1 \\ i>1}}^{i-1}\bigg(\frac{k-1}{k} \bigg)^j, & \mbox{else}
	\end{cases}
	\label{eq:iterativeForm}
\end{align}
$$

In order to find an initial amount of coconuts $$n$$, we have to ensure that all $$n_i$$ are dividable by $$k$$ with a remainder of one (which is given to the monkey). Hence, it has to be ensured that:
$$
\begin{align}
	\forall i \in \{ 0, \ldots, k\}: \ n_i \equiv m\mod k
	\label{eq:forallI}
\end{align}
$$
Remember that in the morning, after all $$k$$ sailors have woken up, the remaining coconuts are divided among all sailors. So, as stated above, $$n_k$$ must have a remainder of one when divided by $$k$$. For $$n_0 = n$$, it is sufficient to ensure that $$n$$ is a multiple of $$k$$ plus $$m$$. 

For larger $$i$$, the situation becomes slightly more complex. We need to find an $$n$$ that satisfies Eq. \eqref{eq:iterativeForm} such that Eq. \eqref{eq:forallI} is also satisfied. To achieve this, let us first simplify the complicated expression (assuming $$i > 1$$) in Eq. \eqref{eq:iterativeForm} using the geometric series specified in the Appendix:

$$
\begin{align}
	& \ \ (n-m)\bigg(\frac{k-1}{k} \bigg)^i - m\sum\limits_{\substack{j=1 \\ i>1}}^{i-1}\bigg(\frac{k-1}{k} \bigg)^j \label{eq:probWithSum} \\
	&= (n-m)\bigg(\frac{k-1}{k} \bigg)^i - m\frac{ \Big(\frac{k-1}{k}\Big)^i - \frac{k-1}{k}}{\frac{k-1}{k} - 1} \\
	&= (n-m)\bigg(\frac{k-1}{k} \bigg)^i - m\frac{ \Big(\frac{k-1}{k}\Big)^i - \frac{k-1}{k}}{-\frac{1}{k}} \\
	&= (n-m)\bigg(\frac{k-1}{k} \bigg)^i + mk \bigg(\frac{k-1}{k} \bigg)^i-mk+m \\
	&= (n-m+mk)\bigg(\frac{k-1}{k} \bigg)^i -mk+m. \label{eq:iterativeSimple}
\end{align}
$$

Now we can try to find an $$n$$ that suffices Eq. \eqref{eq:forallI}:

$$
\begin{align}
(n-m+mk)\bigg(\frac{k-1}{k} \bigg)^i -mk+m &\equiv m \mod k \\
(n-m+mk)\bigg(\frac{k-1}{k} \bigg)^i -mk &\equiv 0 \mod k \\
(n-m+mk)\bigg(\frac{k-1}{k} \bigg)^i &\equiv 0 \mod k \label{eq:modulo}
\end{align}
$$

Note that we cannot get rid of the term $$mk$$, since the power of the fraction is smaller than one and not a natural number. The left-hand side of Eq. \eqref{eq:modulo} should hence be a multiple of $$k$$. This can be expressed as:

$$
\begin{align}
	(n-m+mk)\bigg(\frac{k-1}{k} \bigg)^i = r\cdot k,
\end{align}
$$

where for now we choose $$r \in \mathbb{Z}$$ and then solve for $$n$$:

$$
\begin{align}
	(n-m+mk)\bigg(\frac{k-1}{k} \bigg)^i &= r\cdot k \\
	n-m+mk &= r\cdot k \bigg(\frac{k}{k-1} \bigg)^i \\
	n &= r\cdot k \bigg(\frac{k}{k-1} \bigg)^i - mk + m \\
	n &= r\cdot \frac{k^{k+1}}{(k-1)^i} - m(k -1) \label{eq:firstN}.
\end{align}
$$

Although we can now compute different values for $$n$$ according to \eqref{eq:firstN} which will suffice Eq. \eqref{eq:modulo}, we can observe a problem: For example, with $$i=k=3$$ and $$m=r=1$$ we receive a value of $$n=8.125$$, which -- although it suffices Eq. \eqref{eq:modulo} -- is not a natural number. This is due to the fraction in Eq. \eqref{eq:firstN}. However, we show in the Appendix that numerator and denominator are relatively prime to each other, hence, the fraction cannot be reduced. So, in order to obtain a natural number for $$n$$, we can drag the denominator to $$r$$ and assume that $$r$$ is a multiple of it by replacing $$r/(k-1)^i$$ with $$q \in \mathbb{N_+}$$:

$$
\begin{align}
	n &= r\cdot \frac{k^{k+1}}{(k-1)^i} - m(k -1) \\
	&= \frac{r}{(k-1)^i} \cdot k^{k+1} - m(k -1) \\
	&= q \cdot k^{k+1} - m(k -1). \label{eq:finalSolution}
\end{align}
$$

Note that in Eq. \eqref{eq:finalSolution} we have an expression which is independent of $$i$$ and hence fulfills Eq. \eqref{eq:forallI} for all $$i \in \{2, \ldots, k \}$$.


You might have noticed that we actually only solved the problem for $$i > 1$$, since the sum in Eq. \eqref{eq:probWithSum} is only evaluated for $$i > 1$$. However, Eq. \eqref{eq:forallI} requires that the condition holds for all $$i \in \{0, \ldots, k\}$$ -- meaning it must also be satisfied for $$i = 0$$ and $$i = 1$$ -- ensuring that $$n_i \equiv m \mod k$$.

We can directly observe that Eq. \eqref{eq:finalSolution} is a valid solution for the case $$i = 0$$. Furthermore, we can show that the case $$i = 1$$, as specified in Eq. \eqref{eq:n1}, is merely a special case of Eq. \eqref{eq:firstN}, with:

$$
\begin{align}
	(n-m)\frac{k-1}{k} &\equiv m\mod k \\
	\Rightarrow (n-m)\frac{k-1}{k} &= s \cdot k + m \\
	n &= s \cdot k\frac{k}{k-1} + m\frac{k}{k-1} + m \\
	&= \frac{sk^2+mk}{k-1} + m \label{eq:casen1}
\end{align}
$$

and:

$$
\begin{align}
	\frac{sk^2+mk}{k-1} + m &= r\cdot \frac{k^{k+1}}{(k-1)^1} - mk + m \\
	sk^2+mk &= r k^{k+1} - mk(k-1) \\
	sk +m &= rk^k - mk + m \\
	s &= rk^{k-1} - m \in \mathbb{N}.
\end{align}
$$

Hence, if we insert $$s$$ into Eq. \eqref{eq:casen1} we obtain Eq. \eqref{eq:firstN} which then leads to the general solution in Eq. \eqref{eq:finalSolution}.


## Verification
To make sure that we have obtained a correct solution, let us run some simulations where we try many values for $$n=n_0$$ and check if these values correspond to Eq. \eqref{eq:finalSolution}.

{% highlight R %}
# Number of Sailors
k <- 3

# Number of Monkeys on the island
m <- 2

# Range of coconuts to try (1 2 3 ... n_max):
n_max <- 1e6

# There should be less monkeys than sailors
stopifnot(m < k)

# Recursive function simulating the sailors behaviour
divideCocos <- function (n, sailor) {
  if(sailor < 0) return (TRUE)
  if((n %% k) == m) return (divideCocos((n-m) / k * (k - 1), sailor - 1))
  FALSE
}

tryN <- sapply(1:n_max, function(i) divideCocos(i, k))
realN <- which(tryN)

# Compare with formula
formulaNCocos <- function(q, k, m) {
  q*k^(k+1) - m*(k-1)
}
formulaN <- sapply(1:length(realN), formulaNCocos, k, m)

# Check if the simulated results fit to the formula we obtained
anyError <- which(formulaN != realN)
stopifnot(length(anyError) == 0)

cat("Formula appears to be correct!!!\n")
cat("\nSome numbers n that work:", realN[1:min(25, length(realN))])
{% endhighlight %}<!---* -->

We can run this R-script for different settings of sailors and monkeys and check if there are any differences between the simulated results and the formula. In such a case, the formula would be wrong.  
However, after trying several combinations, we can be quite confident that the formula is correct (although the computer simulation is certainly not a real proof). For our initial setup with $$k = 3$$ sailors and $$m = 1$$ monkey, we get the following result with the R script:

{% highlight R %}
Formula appears to be correct!!!
Some numbers n that work: 79 160 241 322 403 484 565 646 727 808 889 970 1051 1132 1213 1294 1375 1456 1537 1618 1699 1780 1861 1942 2023
{% endhighlight %}

# Summary
As we found, it is possible to find a general algebraic solution to the coconut and monkey problem described at the beginning. The number of coconuts that were initially collected, for $$k$$ sailors and $$m$$ monkeys, is given by:

$$
\begin{align}
	n = q \cdot k^{k+1} - m(k -1),
\end{align}
$$

where $$q$$ is a natural number larger than 0, since there are infinitely many solutions.

# Appendix

## Geometric Series
In this appendix we briefly mention several properties of the geometric series which are required for the derivations in other dependencies.
For $$q \neq 1$$ and $$j<N$$ the geometric series can be derived as:

$$
\begin{equation}
\begin{split}
S = q^{j}+q^{j+1}+ \cdots + q^{N-1} \\
qS = q^{j+1} + q^{j+2} + \cdots + q^N \\
qS - S = q^N - q^j \\
S(q-1) = q^N - q^j \\
S = \frac{q^N - q^j}{q-1} = \frac{q^j-q^N}{1-q}
\end{split}
\label{eq:geometricSeries1}
\end{equation}
$$


More generally, the geometric series can be written as:

$$
\begin{equation}
\begin{split}
a_0 \sum_{i=j}^{N-1} {q^i} = a_0 \frac{q^N - q^j}{q-1}
\end{split}
\label{eq:geometricSeries2}
\end{equation}
$$

**Special cases**

If the series starts with $$i=0$$ we retrieve:

$$
\begin{equation}
\begin{split}
a_0 \sum_{i=0}^{N-1} {q^i} = a_0 \frac{1- q^N}{1-q}
\end{split}
\label{eq:geometricSeries2a}
\end{equation}
$$

For $$q=1$$ we obtain:
\begin{equation}
\begin{split}
a_0 \sum_{i=j}^{N-1} {1^i} = a_0 (N-j)
\end{split}
\label{eq:geometricSeries3}
\end{equation}
For an infinite series with $$N=\infty$$, convergence is achieved for values $$|q|<1$$:
\begin{equation}
\begin{split}
a_0 \sum_{i=j}^{\infty} {q^i} = a_0 \frac{q^j}{1-q}
\end{split}
\label{eq:geometricSeries4}
\end{equation}

## Powers of neighbored natural numbers are relatively prime

In this appendix we briefly show that two neighbored natural numbers $$k$$ and $$k+1$$ are relatively prime, as well as their powers. This can be done with a proof by contradiction:
Let us assume that there exists a divisor $$t>1$$ for which:

$$
\begin{align}
k &= q \cdot t\\
k+1 &= r \cdot t
\end{align}
$$

This also implies:
$$
\begin{align}
r > q \\
r - q \geq 1
\end{align}
$$

We can also write:

$$
\begin{align}
q \cdot t + 1 &= r \cdot t \\
 1 &= r \cdot t - q \cdot t \\
 1 &= (r- q) \cdot t  \\
 & \Rightarrow r - q = 1 \wedge t = 1.
\end{align}
$$

Since we required $$t>1$$, we have a contradiction, which means that the two neighbored numbers $$k$$ and $$k+1$$ are relatively prime and a fraction containing these two numbers in the numerator and denominator cannot be reduced. Furthermore, since the prime factorization of $$k$$ and $$k+1$$ returns two disjoint sets of primes $$P_{k}$$ and $$P_{k+1}$$ ($$P_{k} \cap P_{k+1} = \emptyset$$), it can also be trivially shown that the powers $$k^i$$ and $$(k+1)^j$$, with $$i,j \in \mathbb{N_+}$$ are also relatively prime.
