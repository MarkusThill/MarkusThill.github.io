---
layout: post
title: "Online Estimation&#58; Weighted Observations and Mini-Batches"
modified:
categories: [math, stats, ML]
description: "Carrying the weighted scatter derivation from the thesis through in full, to obtain exact single-observation and mini-batch updates, together with a four-point example which catches an incorrect batch formula."
tags: [online estimation, covariance, data streams, mini-batch, weighted statistics, math, python]
thumbnail: assets/img/2026-online-estimation/thumbnails/weighted-observations.webp
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-03-01T10:00:00+01:00
pretty_table: false
related_posts: true
series: online-estimation
series_part: 3
---

{% include series_online_estimation.liquid %}

Weights let some observations contribute more than others, and mini-batches let an estimator
process several observations in a single update. These sound like two separate features, and one is
tempted to treat them separately, but Appendix B.2.1 of my thesis
{% cite thill2022machine --file thesis %} handles both in one derivation, which is the route I
follow here. No forgetting is applied yet: previously assigned weights stay fixed until the next
article, where the one additional ingredient is that the old weights are allowed to decay.

The algebra is longer than in the unweighted case, and I will write it out line by line rather than
quoting the result. The length is not incidental. A shortened version of this calculation is
exactly where an incorrect mini-batch formula comes from, and a four-element example at the end of
this article distinguishes the right answer from a plausible wrong one using nothing but small
integers.

<!--more-->

<br>

## Weighted Statistics and Their Normalization

For nonnegative unnormalized weights $$w'_i$$ with positive total, define

$$
W_n=\sum_{i=1}^n w'_i,\qquad W_n^{(2)}=\sum_{i=1}^n(w'_i)^2,\qquad
w_i=\frac{w'_i}{W_n},
$$

so that the normalized weights $$w_i$$ sum to one. The weighted arithmetic mean is then

$$
\begin{equation}
\bar{\mathbf{x}}_n=\frac{\sum_{i=1}^n w'_i\mathbf{x}_i}{\sum_{i=1}^n w'_i}
=\frac{\sum_{i=1}^n w'_i\mathbf{x}_i}{W_n}
=\sum_{i=1}^n w_i\mathbf{x}_i,
\label{eq:weighted-mean}
\end{equation}
$$

and the special case $$w_i=1/n$$ recovers the conventional mean. Following Price
{% cite price1972extension --file thesis %}, the weighted scatter matrix and the biased
(population-normalized) weighted covariance are

$$
\bar{\mathbf{M}}^{(n)}=\sum_{i=1}^n w'_i(\mathbf{x}_i-\bar{\mathbf{x}}_n)(\mathbf{x}_i-\bar{\mathbf{x}}_n)^T,
\qquad
\bar{\boldsymbol{\Sigma}}_n=\frac{\bar{\mathbf{M}}^{(n)}}{W_n}.
$$

Which unbiased correction applies depends on what the weights mean, and the two cases are genuinely
different. If the weights are **frequency weights**, so that each $$w'_i$$ counts how many times an
identical observation occurred, then the expanded sample has $$W_n$$ members and its ordinary
sample covariance uses

$$
\begin{equation}
\bar{\boldsymbol{\Sigma}}_n=\frac{\bar{\mathbf{M}}^{(n)}}{W_n-1}.
\label{eq:frequency-unbiased}
\end{equation}
$$

If instead the weights are **reliability weights**, expressing how much importance to attach to
independently observed vectors, then under IID sampling with fixed weights, a common mean and
covariance $$\boldsymbol{\Sigma}$$, the expected scatter is

$$
\mathbb{E}\big[\bar{\mathbf{M}}^{(n)}\big]
=\left(W_n-\frac{W_n^{(2)}}{W_n}\right)\boldsymbol{\Sigma},
$$

so that the unbiased estimate is

$$
\begin{equation}
\bar{\boldsymbol{\Sigma}}_n=
\frac{\bar{\mathbf{M}}^{(n)}}{W_n-W_n^{(2)}/W_n}.
\label{eq:weighted-unbiased}
\end{equation}
$$

One way to see where that expectation comes from is to expand the scatter about the population mean
instead of the estimated one. The expected uncentered weighted sum is then
$$W_n\boldsymbol{\Sigma}$$, while estimating the mean from the same data subtracts
$$W_n\operatorname{Cov}(\bar{\mathbf{X}}_n)=W_n^{(2)}\boldsymbol{\Sigma}/W_n$$, and the fifth
article in this series derives that second relation in detail. Setting every $$w'_i=1$$ gives
$$W_n=W_n^{(2)}=n$$ and both \eqref{eq:frequency-unbiased} and \eqref{eq:weighted-unbiased} collapse
to the familiar $$n-1$$. A reassuring property of \eqref{eq:weighted-unbiased} is that multiplying
every reliability weight by the same positive constant changes neither the mean nor its corrected
covariance, so the overall scale of the weights is genuinely free. Data-dependent weights need
their own bias analysis and are covered by neither expression.

<br>

## Updating the Mean for a Batch

Let $$\mu$$ be the number of new observations and $$k=n-\mu+1$$ the index of the first of them, so
that the batch runs from $$k$$ to $$n$$ and $$\bar{\mathbf{x}}_{n-\mu}$$ is the mean before it
arrives. The scalar sums are updated first,

$$
W_n=W_{n-\mu}+\sum_{i=k}^n w'_i,\qquad
W_n^{(2)}=W_{n-\mu}^{(2)}+\sum_{i=k}^n(w'_i)^2,
$$

after which we split the numerator of \eqref{eq:weighted-mean} into old and new observations and
work towards an increment:

$$
\begin{aligned}
\bar{\mathbf{x}}_n
&=\frac{W_{n-\mu}\bar{\mathbf{x}}_{n-\mu}+\sum_{i=k}^n w'_i\mathbf{x}_i}{W_n}\\
&=\frac{\left(W_n-\sum_{i=k}^n w'_i\right)\bar{\mathbf{x}}_{n-\mu}
+\sum_{i=k}^n w'_i\mathbf{x}_i}{W_n}\\
&=\bar{\mathbf{x}}_{n-\mu}
+\frac{-\sum_{i=k}^n w'_i\bar{\mathbf{x}}_{n-\mu}+\sum_{i=k}^n w'_i\mathbf{x}_i}{W_n}\\
&=\bar{\mathbf{x}}_{n-\mu}
+\frac{\sum_{i=k}^n w'_i\big(\mathbf{x}_i-\bar{\mathbf{x}}_{n-\mu}\big)}{W_n}\\
&=\bar{\mathbf{x}}_{n-\mu}+\sum_{i=k}^n\frac{w'_i}{W_n}\boldsymbol{\Delta}_i,
\end{aligned}
$$

where the second line uses $$W_{n-\mu}=W_n-\sum_{i=k}^n w'_i$$, and

$$
\begin{equation}
\boldsymbol{\Delta}_i=\mathbf{x}_i-\bar{\mathbf{x}}_{n-\mu}.
\label{eq:delta-batch}
\end{equation}
$$

Every residual in \eqref{eq:delta-batch} uses the same mean, namely the one from **before the
batch**. This is worth emphasizing because an implementation which updates the mean inside the loop
over the batch will silently compute something else. Rearranging the first line also gives an
identity we will need twice below,

$$
\begin{equation}
W_n\bar{\mathbf{x}}_n=W_{n-\mu}\bar{\mathbf{x}}_{n-\mu}+\sum_{i=k}^n w'_i\mathbf{x}_i,
\qquad\text{equivalently}\qquad
\bar{\mathbf{x}}_{n-\mu}=\frac{W_n\bar{\mathbf{x}}_n-\sum_{i=k}^n w'_i\mathbf{x}_i}{W_{n-\mu}}.
\label{eq:mean-identities}
\end{equation}
$$

<br>

## Expanding the Weighted Scatter Matrix

As in the unweighted case, we first remove all reference to the previous state by expanding the
outer product, keeping both cross terms until the sums are taken:

$$
\begin{aligned}
\bar{\mathbf{M}}^{(n)}
&=\sum_{i=1}^n w'_i(\mathbf{x}_i-\bar{\mathbf{x}}_n)(\mathbf{x}_i-\bar{\mathbf{x}}_n)^T\\
&=\sum_{i=1}^n w'_i\left[\mathbf{x}_i\mathbf{x}_i^T-\mathbf{x}_i\bar{\mathbf{x}}_n^T
-\bar{\mathbf{x}}_n\mathbf{x}_i^T+\bar{\mathbf{x}}_n\bar{\mathbf{x}}_n^T\right]\\
&=\sum_{i=1}^n w'_i\mathbf{x}_i\mathbf{x}_i^T
-\left(\sum_{i=1}^n w'_i\mathbf{x}_i\right)\bar{\mathbf{x}}_n^T
-\bar{\mathbf{x}}_n\left(\sum_{i=1}^n w'_i\mathbf{x}_i\right)^T
+\left(\sum_{i=1}^n w'_i\right)\bar{\mathbf{x}}_n\bar{\mathbf{x}}_n^T\\
&=\sum_{i=1}^n w'_i\mathbf{x}_i\mathbf{x}_i^T
-W_n\bar{\mathbf{x}}_n\bar{\mathbf{x}}_n^T
-W_n\bar{\mathbf{x}}_n\bar{\mathbf{x}}_n^T
+W_n\bar{\mathbf{x}}_n\bar{\mathbf{x}}_n^T\\
&=\sum_{i=1}^n w'_i\mathbf{x}_i\mathbf{x}_i^T-W_n\bar{\mathbf{x}}_n\bar{\mathbf{x}}_n^T,
\end{aligned}
$$

where the fourth line uses $$\sum_i w'_i\mathbf{x}_i=W_n\bar{\mathbf{x}}_n$$ from
\eqref{eq:weighted-mean} in both cross terms. The increment of the scatter over the new batch is
then obtained by subtracting the same expression evaluated at $$n-\mu$$:

$$
\begin{aligned}
\boldsymbol{\Delta}\bar{\mathbf{M}}^{(n)}
&=\bar{\mathbf{M}}^{(n)}-\bar{\mathbf{M}}^{(n-\mu)}\\
&=\sum_{i=1}^{n} w'_i\mathbf{x}_i\mathbf{x}_i^T-W_n\bar{\mathbf{x}}_n\bar{\mathbf{x}}_n^T
-\sum_{i=1}^{n-\mu} w'_i\mathbf{x}_i\mathbf{x}_i^T
+W_{n-\mu}\bar{\mathbf{x}}_{n-\mu}\bar{\mathbf{x}}_{n-\mu}^T\\
&=\sum_{i=k}^{n} w'_i\mathbf{x}_i\mathbf{x}_i^T
-W_n\bar{\mathbf{x}}_n\bar{\mathbf{x}}_n^T
+W_{n-\mu}\bar{\mathbf{x}}_{n-\mu}\bar{\mathbf{x}}_{n-\mu}^T.
\end{aligned}
$$

<br>

## Simplifying the Increment

Only the two mean identities \eqref{eq:mean-identities} are needed from here on. We substitute the
first into the term carrying $$W_n\bar{\mathbf{x}}_n$$, and the second into the **right-hand**
factor of the term carrying $$W_{n-\mu}\bar{\mathbf{x}}_{n-\mu}$$, leaving the left-hand factor
alone:

$$
\begin{aligned}
\boldsymbol{\Delta}\bar{\mathbf{M}}^{(n)}
={}&\sum_{i=k}^{n} w'_i\mathbf{x}_i\mathbf{x}_i^T
-W_n\frac{W_{n-\mu}\bar{\mathbf{x}}_{n-\mu}+\sum_{i=k}^n w'_i\mathbf{x}_i}{W_n}\bar{\mathbf{x}}_n^T\\
&+W_{n-\mu}\bar{\mathbf{x}}_{n-\mu}
\left(\frac{W_n\bar{\mathbf{x}}_n-\sum_{i=k}^n w'_i\mathbf{x}_i}{W_{n-\mu}}\right)^T.
\end{aligned}
$$

The two normalization factors cancel, which is the point of writing the identities in that
particular pair of forms:

$$
\begin{aligned}
\boldsymbol{\Delta}\bar{\mathbf{M}}^{(n)}
={}&\sum_{i=k}^{n} w'_i\mathbf{x}_i\mathbf{x}_i^T
-\left(\sum_{i=k}^n w'_i\mathbf{x}_i\right)\bar{\mathbf{x}}_n^T
-W_{n-\mu}\bar{\mathbf{x}}_{n-\mu}\bar{\mathbf{x}}_n^T\\
&+W_n\bar{\mathbf{x}}_{n-\mu}\bar{\mathbf{x}}_n^T
-\bar{\mathbf{x}}_{n-\mu}\left(\sum_{i=k}^n w'_i\mathbf{x}_i\right)^T.
\end{aligned}
$$

The third and fourth terms differ only in their scalar factor and can be collected, and the
resulting factor is precisely the total incoming weight:

$$
\begin{aligned}
\boldsymbol{\Delta}\bar{\mathbf{M}}^{(n)}
={}&\sum_{i=k}^{n} w'_i\mathbf{x}_i\mathbf{x}_i^T
-\sum_{i=k}^n w'_i\mathbf{x}_i\bar{\mathbf{x}}_n^T
+\big(W_n-W_{n-\mu}\big)\bar{\mathbf{x}}_{n-\mu}\bar{\mathbf{x}}_n^T
-\bar{\mathbf{x}}_{n-\mu}\sum_{i=k}^n w'_i\mathbf{x}_i^T\\
={}&\sum_{i=k}^{n} w'_i\mathbf{x}_i\mathbf{x}_i^T
-\sum_{i=k}^n w'_i\mathbf{x}_i\bar{\mathbf{x}}_n^T
+\left(\sum_{i=k}^{n} w'_i\right)\bar{\mathbf{x}}_{n-\mu}\bar{\mathbf{x}}_n^T
-\bar{\mathbf{x}}_{n-\mu}\sum_{i=k}^n w'_i\mathbf{x}_i^T.
\end{aligned}
$$

Every term is now a sum over the same index range, so all four can be placed under one summation
sign and factored:

$$
\begin{aligned}
\boldsymbol{\Delta}\bar{\mathbf{M}}^{(n)}
&=\sum_{i=k}^{n}\left(w'_i\mathbf{x}_i\mathbf{x}_i^T
-w'_i\mathbf{x}_i\bar{\mathbf{x}}_n^T
+w'_i\bar{\mathbf{x}}_{n-\mu}\bar{\mathbf{x}}_n^T
-w'_i\bar{\mathbf{x}}_{n-\mu}\mathbf{x}_i^T\right)\\
&=\sum_{i=k}^{n}\left(w'_i\mathbf{x}_i\big(\mathbf{x}_i^T-\bar{\mathbf{x}}_n^T\big)
-w'_i\bar{\mathbf{x}}_{n-\mu}\big(\mathbf{x}_i^T-\bar{\mathbf{x}}_n^T\big)\right)\\
&=\sum_{i=k}^{n} w'_i\big(\mathbf{x}_i-\bar{\mathbf{x}}_{n-\mu}\big)
\big(\mathbf{x}_i-\bar{\mathbf{x}}_n\big)^T\\
&=\sum_{i=k}^{n} w'_i\boldsymbol{\Delta}_i\big(\mathbf{x}_i-\bar{\mathbf{x}}_n\big)^T.
\end{aligned}
$$

The weighted batch update is therefore

$$
\begin{equation}
\bar{\mathbf{M}}^{(n)}=\bar{\mathbf{M}}^{(n-\mu)}+
\sum_{i=k}^n w'_i\boldsymbol{\Delta}_i(\mathbf{x}_i-\bar{\mathbf{x}}_n)^T.
\label{eq:weighted-batch-scatter}
\end{equation}
$$

The same asymmetry as in the unweighted case survives every line of this: each first residual uses
the old mean while each second residual uses the new one. Setting $$\mu=1$$ gives the weighted
online update, setting every $$w'_i=1$$ gives the ordinary batch update, and doing both at once
recovers the recurrence of the previous article. Starting from an empty state, the first mean is
simply the weighted batch mean and this same recurrence produces its scatter, so no special case is
needed for the very first batch.

<br>

## The Update Rules in Summary

Collecting the results, a new batch running from $$k=n-\mu+1$$ to $$n$$ is processed in this order:

$$
\begin{aligned}
W_n&=W_{n-\mu}+\sum_{i=k}^n w'_i,\\
W_n^{(2)}&=W_{n-\mu}^{(2)}+\sum_{i=k}^n (w'_i)^2,\\
\boldsymbol{\Delta}_i&=\mathbf{x}_i-\bar{\mathbf{x}}_{n-\mu},\\
\bar{\mathbf{x}}_n&=\bar{\mathbf{x}}_{n-\mu}+\sum_{i=k}^n\frac{w'_i}{W_n}\boldsymbol{\Delta}_i,\\
\bar{\mathbf{M}}^{(n)}&=\bar{\mathbf{M}}^{(n-\mu)}
+\sum_{i=k}^n w'_i\boldsymbol{\Delta}_i(\mathbf{x}_i-\bar{\mathbf{x}}_n)^T,\\
\bar{\boldsymbol{\Sigma}}_n&=\frac{\bar{\mathbf{M}}^{(n)}}{W_n}.
\end{aligned}
$$

The last line is the population normalization; for an unbiased estimate use
\eqref{eq:frequency-unbiased} or \eqref{eq:weighted-unbiased} according to what the weights mean.
The order matters in exactly one place, namely that all $$\boldsymbol{\Delta}_i$$ must be formed
before the mean is advanced.

<br>

## A Batch Check which Catches a Wrong Formula

For the two scalar batches $$(0,2)$$ and $$(4,6)$$ with unit weights, the old mean and scatter are
$$1$$ and $$2$$. The new mean is $$3$$, so \eqref{eq:weighted-batch-scatter} gives

$$
\bar M^{(4)}=2+(4-1)(4-3)+(6-1)(6-3)=2+3+15=20,
$$

which is the full-data answer computed directly, and matches the running example from the previous
article. A mini-batch expression carrying a factor $$(n+\mu-1)$$ instead of the two distinct means
gives 12 for the same four numbers. Since both values are small integers, the discrepancy needs no
numerical interpretation at all, and a check of this kind costs nothing to run.

The NumPy implementation accepts arbitrary nonnegative incoming weights. Run the following beside
[online_estimation.py]({{ site.baseurl }}/assets/code/2026-online-estimation/online_estimation.py):

```python
import numpy as np
from online_estimation import IncrementalMoments, direct_moments

X = np.array([[0., 0.], [2., 1.], [4., -1.], [6., 3.]])
weights = np.array([1., 2., .5, 3.])
state = IncrementalMoments(2)
state.update(X[:2], weights[:2])
state.update(X[2:], weights[2:])
mean, scatter = direct_moments(X, weights)
denominator = weights.sum() - (weights @ weights)/weights.sum()
np.testing.assert_allclose(state.mean, mean)
np.testing.assert_allclose(state.covariance(), scatter/denominator)
```

The [companion notebook](/blog/2025/online-batch-estimate-cov-mu/) extends this comparison to
variable batch sizes and to forgetting, with 480 weighted-prefix checks whose maximum relative
covariance error is about $$1.15\cdot10^{-15}$$. The general point is that batching changes how the
calculation is organized without needing to change the statistical estimate at all. In the next
article we let the old weights decay, while retaining exactly the same structure of update.

*Source: thesis Appendix B.2.1, equations `recursive-mean` through `DeltaMWeightFinal`. The two
cross terms are kept separate until their sums are taken, rather than compressed into a factor of
two.*

<br>

## References

<div class="publications">
{% bibliography --file thesis --cited --group_by none %}
</div>
