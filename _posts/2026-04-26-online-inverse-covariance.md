---
layout: post
title: "Online Estimation&#58; Updating the Inverse Covariance Matrix"
modified:
categories: [math, stats, ML]
description: "Deriving Woodbury and Sherman-Morrison updates for the scatter matrix step by step, handling the singular startup phase explicitly, and verifying the reported covariance and precision with Python and R."
tags: [online estimation, covariance, inverse covariance, Woodbury, Sherman-Morrison, Mahalanobis, data streams, math, python, R]
thumbnail: assets/img/2026-online-estimation/inverse-initialization.png
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-04-26T10:00:00+02:00
pretty_table: false
related_posts: true
series: online-estimation
series_part: 7
---

{% include series_online_estimation.liquid %}

In practice one often needs the inverse of a covariance matrix rather than the covariance itself,
the Mahalanobis distance being the obvious example. In a fully online setting, recomputing that
inverse for every arriving observation is expensive, since inverting a $$d\times d$$ matrix costs
about $$O(d^3)$$, only slightly less in the more elaborate algorithms. Appendix B.2.2.1 of my
thesis {% cite thill2022machine --file thesis %} shows that this is avoidable in two senses: the
covariance itself need never be formed if only its inverse is wanted, and the inverse can be
updated incrementally. The tools are the Woodbury identity
{% cite woodbury1950inverting --file thesis %} for batches and its Sherman-Morrison specialization
{% cite sherman1950adjustment --file thesis %} for a single observation, and the results below are
stated for the general weighted, exponentially decaying estimator.

Both identities require an existing inverse to update, which means that handling the first
observations is part of the algorithm rather than an implementation detail to be papered over. That
turns out to be where the practical difficulty lies, and this article spends as much space on
initialization as on the identities themselves.

<!--more-->

<br>

## From Scatter to Covariance and Precision

We now write $$\bar{\mathbf{M}}_n$$ in place of $$\bar{\mathbf{M}}^{(n)}$$, moving the superscript
to the index as the thesis does at this point, so that inverses can be written without ambiguity.
If the covariance estimate is $$\bar{\boldsymbol{\Sigma}}_n=\bar{\mathbf{M}}_n/c_n$$ for a positive
scalar $$c_n$$, then

$$
\bar{\boldsymbol{\Sigma}}_n^{-1}=c_n\bar{\mathbf{M}}_n^{-1},
$$

where $$c_n=W_n$$ gives the population normalization and $$c_n=W_n-W_n^{(2)}/W_n$$ the
reliability-weight correction. Note that scaling the inverse requires **multiplication** by
$$c_n$$ rather than division, which is easy to get backwards when switching between the two
normalizations. It is also worth stating that the inverse of an unbiased covariance estimate is not
generally an unbiased estimate of the population precision; unbiasedness does not survive matrix
inversion, and nothing in this article claims that it does.

<br>

## The Batch Update in Matrix Form

The scatter recurrence from the fourth article is a sum of $$\mu$$ outer products, and writing it
as a single matrix product is what exposes its low-rank structure. For an incoming batch of size
$$\mu$$, define the two $$\mu\times d$$ matrices

$$
\mathbf{D}_n=
\begin{pmatrix}\boldsymbol{\Delta}_k&\boldsymbol{\Delta}_{k+1}&\cdots&\boldsymbol{\Delta}_n\end{pmatrix}^T,
\qquad
\boldsymbol{\mathcal{X}}_n=
\begin{pmatrix}\mathbf{x}_k-\bar{\mathbf{x}}_n&\mathbf{x}_{k+1}-\bar{\mathbf{x}}_n&\cdots&
\mathbf{x}_n-\bar{\mathbf{x}}_n\end{pmatrix}^T,
$$

where $$k=n-\mu+1$$ and $$\boldsymbol{\Delta}_i=\mathbf{x}_i-\bar{\mathbf{x}}_{n-\mu}$$ as before.
The first collects the residuals against the old mean as its rows and the second those against the
new mean, so that

$$
\begin{aligned}
\bar{\mathbf{M}}_n
&=\lambda\bar{\mathbf{M}}_{n-\mu}+\sum_{i=k}^n\boldsymbol{\Delta}_i(\mathbf{x}_i-\bar{\mathbf{x}}_n)^T\\
&=\lambda\bar{\mathbf{M}}_{n-\mu}+\mathbf{D}_n^T\mathbf{I}\,\boldsymbol{\mathcal{X}}_n,
\end{aligned}
$$

in which the product $$\mathbf{D}_n^T\boldsymbol{\mathcal{X}}_n$$ has size $$d\times d$$, as
required, while its inner dimension is only $$\mu$$. The identity matrix is written explicitly
because it is what plays the role of $$\mathbf{C}$$ below. For arbitrary incoming weights, replace
$$\boldsymbol{\mathcal{X}}_n$$ by $$\operatorname{diag}(w'_k,\ldots,w'_n)\boldsymbol{\mathcal{X}}_n$$.

<br>

## Applying the Woodbury Identity

For compatible matrices possessing the needed inverses, the Woodbury identity reads

$$
\begin{equation}
(\mathbf{A}+\mathbf{U}\mathbf{C}\mathbf{V})^{-1}
=\mathbf{A}^{-1}-\mathbf{A}^{-1}\mathbf{U}
\big(\mathbf{C}^{-1}+\mathbf{V}\mathbf{A}^{-1}\mathbf{U}\big)^{-1}
\mathbf{V}\mathbf{A}^{-1}.
\label{eq:woodbury}
\end{equation}
$$

The expression inside the inner inverse contains the **product**
$$\mathbf{V}\mathbf{A}^{-1}\mathbf{U}$$. The thesis prints a plus sign where the second
multiplication belongs, giving $$\mathbf{C}^{-1}+\mathbf{V}\mathbf{A}^{-1}+\mathbf{U}$$, which is
not even dimensionally defined for the rectangular batch matrices above, since
$$\mathbf{V}\mathbf{A}^{-1}$$ is $$\mu\times d$$ while $$\mathbf{U}$$ is $$d\times\mu$$. The
specialized batch update which the thesis then derives already carries the correct product, so this
is a typographical slip in the statement of the general identity rather than an error in the
result. With

$$
\mathbf{A}=\lambda\bar{\mathbf{M}}_{n-\mu},\qquad
\mathbf{U}=\mathbf{D}_n^T,\qquad
\mathbf{C}=\mathbf{I}_\mu,\qquad
\mathbf{V}=\boldsymbol{\mathcal{X}}_n,
$$

substitution into \eqref{eq:woodbury} gives, using $$\mathbf{A}^{-1}=\lambda^{-1}\bar{\mathbf{M}}_{n-\mu}^{-1}$$
in three places,

$$
\begin{aligned}
\bar{\mathbf{M}}_n^{-1}
&=\frac{1}{\lambda}\bar{\mathbf{M}}_{n-\mu}^{-1}
-\frac{1}{\lambda^2}\bar{\mathbf{M}}_{n-\mu}^{-1}\mathbf{D}_n^T
\left(\mathbf{I}_\mu^{-1}+\frac{1}{\lambda}\boldsymbol{\mathcal{X}}_n
\bar{\mathbf{M}}_{n-\mu}^{-1}\mathbf{D}_n^T\right)^{-1}
\boldsymbol{\mathcal{X}}_n\bar{\mathbf{M}}_{n-\mu}^{-1}\\
&=\frac{1}{\lambda}\bar{\mathbf{M}}_{n-\mu}^{-1}
-\frac{1}{\lambda}\bar{\mathbf{M}}_{n-\mu}^{-1}\mathbf{D}_n^T
\left(\lambda\mathbf{I}_\mu+\boldsymbol{\mathcal{X}}_n
\bar{\mathbf{M}}_{n-\mu}^{-1}\mathbf{D}_n^T\right)^{-1}
\boldsymbol{\mathcal{X}}_n\bar{\mathbf{M}}_{n-\mu}^{-1}.
\end{aligned}
$$

The step between the two lines pulls a factor $$\lambda$$ out of the inner inverse: writing
$$\mathbf{B}=\boldsymbol{\mathcal{X}}_n\bar{\mathbf{M}}_{n-\mu}^{-1}\mathbf{D}_n^T$$, we have
$$\big(\mathbf{I}+\lambda^{-1}\mathbf{B}\big)^{-1}
=\big(\lambda^{-1}(\lambda\mathbf{I}+\mathbf{B})\big)^{-1}
=\lambda\big(\lambda\mathbf{I}+\mathbf{B}\big)^{-1}$$, and that factor cancels one of the two
powers of $$\lambda$$ in front. Writing $$\mathbf{P}_{\mathrm{old}}=\bar{\mathbf{M}}_{n-\mu}^{-1}$$
and collecting, the update is

$$
\bar{\mathbf{M}}_n^{-1}
=\frac{1}{\lambda}\left[\mathbf{P}_{\mathrm{old}}
-\mathbf{P}_{\mathrm{old}}\mathbf{D}_n^T
\big(\lambda\mathbf{I}_\mu+\boldsymbol{\mathcal{X}}_n\mathbf{P}_{\mathrm{old}}\mathbf{D}_n^T\big)^{-1}
\boldsymbol{\mathcal{X}}_n\mathbf{P}_{\mathrm{old}}\right].
$$

The inner system has dimension $$\mu$$ rather than $$d$$, which is the entire point of the
exercise, and in code one should solve that system rather than explicitly forming its inverse.
Since an inverse still has to be computed somewhere, the identity is only worth using when the
batch size $$\mu$$ is appreciably smaller than the dimension $$d$$ of the observations.

<br>

## The Single-Observation Specialization

For $$\mu=1$$ the inner system is scalar, and the Woodbury identity reduces to the
Sherman-Morrison formula,

$$
(\mathbf{A}+\mathbf{u}\mathbf{v}^T)^{-1}
=\mathbf{A}^{-1}-\frac{\mathbf{A}^{-1}\mathbf{u}\mathbf{v}^T\mathbf{A}^{-1}}
{1+\mathbf{v}^T\mathbf{A}^{-1}\mathbf{u}}.
$$

Reading the fully online scatter recurrence
$$\bar{\mathbf{M}}_n=\lambda\bar{\mathbf{M}}_{n-1}+\boldsymbol{\Delta}_n(\mathbf{x}_n-\bar{\mathbf{x}}_n)^T$$
as $$\mathbf{A}+\mathbf{u}\mathbf{v}^T$$, we identify

$$
\mathbf{A}=\lambda\bar{\mathbf{M}}_{n-1},\qquad
\mathbf{u}=\boldsymbol{\Delta}_n,\qquad
\mathbf{v}=\mathbf{x}_n-\bar{\mathbf{x}}_n,
$$

and substituting $$\mathbf{A}^{-1}=\lambda^{-1}\bar{\mathbf{M}}_{n-1}^{-1}$$ gives a numerator
carrying $$\lambda^{-2}$$ and a denominator
$$1+\lambda^{-1}\mathbf{v}^T\bar{\mathbf{M}}_{n-1}^{-1}\mathbf{u}
=\lambda^{-1}\big(\lambda+\mathbf{v}^T\bar{\mathbf{M}}_{n-1}^{-1}\mathbf{u}\big)$$. One power of
$$\lambda$$ cancels between them, leaving

$$
\bar{\mathbf{M}}_n^{-1}
=\frac{1}{\lambda}\left[
\bar{\mathbf{M}}_{n-1}^{-1}-
\frac{\bar{\mathbf{M}}_{n-1}^{-1}\boldsymbol{\Delta}_n
(\mathbf{x}_n-\bar{\mathbf{x}}_n)^T\bar{\mathbf{M}}_{n-1}^{-1}}
{\lambda+(\mathbf{x}_n-\bar{\mathbf{x}}_n)^T\bar{\mathbf{M}}_{n-1}^{-1}\boldsymbol{\Delta}_n}
\right].
$$

The two matrix-vector products should be computed first and only then combined into an outer
product. This is worth saying because a left-associated sequence of matrix multiplications, which
is what one gets by transcribing the formula naively, quietly introduces a dense matrix-matrix
multiplication into what should be an $$O(d^2)$$ update, and the resulting implementation can be
slower than simply calling a solver.

<br>

## The Update Rules in Summary

Processed in this order, a batch running from $$k=n-\mu+1$$ to $$n$$ gives

$$
\begin{aligned}
W_n&=\lambda W_{n-\mu}+\mu,\\
W_n^{(2)}&=\lambda^2W_{n-\mu}^{(2)}+\mu,\\
\boldsymbol{\Delta}_i&=\mathbf{x}_i-\bar{\mathbf{x}}_{n-\mu},\\
\bar{\mathbf{x}}_n&=\bar{\mathbf{x}}_{n-\mu}+\frac{\sum_{i=k}^n\boldsymbol{\Delta}_i}{W_n},\\
\bar{\mathbf{M}}_n&=\lambda\bar{\mathbf{M}}_{n-\mu}+\mathbf{D}_n^T\boldsymbol{\mathcal{X}}_n,\\
\bar{\mathbf{M}}_n^{-1}&=\frac{1}{\lambda}\bar{\mathbf{M}}_{n-\mu}^{-1}
-\frac{1}{\lambda}\bar{\mathbf{M}}_{n-\mu}^{-1}\mathbf{D}_n^T
\big(\lambda\mathbf{I}_\mu+\boldsymbol{\mathcal{X}}_n\bar{\mathbf{M}}_{n-\mu}^{-1}\mathbf{D}_n^T\big)^{-1}
\boldsymbol{\mathcal{X}}_n\bar{\mathbf{M}}_{n-\mu}^{-1},\\
\bar{\boldsymbol{\Sigma}}_n&=\frac{\bar{\mathbf{M}}_n}{W_n},\qquad
\bar{\boldsymbol{\Sigma}}_n^{-1}=W_n\bar{\mathbf{M}}_n^{-1},
\end{aligned}
$$

and for the fully online case $$\mu=1$$, $$k=n$$, these simplify to

$$
\begin{aligned}
W_n&=\lambda W_{n-1}+1,\\
W_n^{(2)}&=\lambda^2W_{n-1}^{(2)}+1,\\
\boldsymbol{\Delta}_n&=\mathbf{x}_n-\bar{\mathbf{x}}_{n-1},\\
\bar{\mathbf{x}}_n&=\bar{\mathbf{x}}_{n-1}+\frac{\boldsymbol{\Delta}_n}{W_n},\\
\bar{\mathbf{M}}_n&=\lambda\bar{\mathbf{M}}_{n-1}+\boldsymbol{\Delta}_n(\mathbf{x}_n-\bar{\mathbf{x}}_n)^T,\\
\bar{\mathbf{M}}_n^{-1}&=\frac{1}{\lambda}\left[\bar{\mathbf{M}}_{n-1}^{-1}
-\frac{\bar{\mathbf{M}}_{n-1}^{-1}\boldsymbol{\Delta}_n(\mathbf{x}_n-\bar{\mathbf{x}}_n)^T
\bar{\mathbf{M}}_{n-1}^{-1}}
{\lambda+(\mathbf{x}_n-\bar{\mathbf{x}}_n)^T\bar{\mathbf{M}}_{n-1}^{-1}\boldsymbol{\Delta}_n}\right],\\
\bar{\boldsymbol{\Sigma}}_n&=\frac{\bar{\mathbf{M}}_n}{W_n},\qquad
\bar{\boldsymbol{\Sigma}}_n^{-1}=W_n\bar{\mathbf{M}}_n^{-1}.
\end{aligned}
$$

Both summaries use the population normalization in the last line; for an unbiased covariance use
the reliability-weight denominator $$W_n-W_n^{(2)}/W_n$$ instead, and remember to multiply rather
than divide when converting the inverse. Both squared-weight recurrences carry the previous **sum
of squared weights** on their right-hand side, which is the missing superscript noted in the fourth
article.

<br>

## An Inverse cannot be Initialized Independently

A centered sample scatter has rank at most $$\min(d,n-1)$$, so in 300 dimensions a first batch of
10 to 19 observations is necessarily singular, and no choice of solver repairs it. Since the
identities above update an existing inverse rather than producing one, the first few observations
need an explicit decision.

Setting the scatter to zero while setting its inverse to $$c\mathbf{I}$$ is not such a decision,
because those two matrices are not a matrix and its inverse in any sense: their product is zero
rather than the identity. Subsequent Woodbury updates then track the inverse of a scatter carrying
an implicit initial ridge $$c^{-1}\mathbf{I}$$, whose remaining contribution after $$t$$ forgetting
updates is $$\lambda^tc^{-1}\mathbf{I}$$. The difficulty is not the ridge itself, which is a
perfectly reasonable thing to want, but that the reported covariance does not include it, so the
maintained inverse and the reported covariance describe two different matrices.

{% include figure.liquid
   path="assets/img/2026-online-estimation/inverse-initialization.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="85%"
   alt="Diagnostic plot of an implicit ridge mismatch, and the rank bound for a high-dimensional setup"
   caption="Left: diagnostic run exposing the implicit-ridge mismatch. An implementation that initializes the scatter to zero and its inverse to a scaled identity is fed a seeded small-variance dataset. After enough observations, the maintained inverse differs from the reported unregularized covariance's actual inverse by about 21.9 percent, but agrees with the inverse of the scatter plus the implicit initial ridge. Right: the rank bound. A centered scatter from n observations in d dimensions has rank at most min(d, n-1), so in 300 dimensions the scatter remains singular until at least 301 observations have arrived, and no inverse exists before that. [SVG version](/assets/img/2026-online-estimation/inverse-initialization.svg)." %}

There are two defensible choices, and the important thing is to make one of them explicitly:

- **Warm up from zero scatter.** Accumulate observations until the scatter is positive definite and
  sufficiently well conditioned, initialize its inverse by a direct solve, and only then update it
  incrementally.
- **Use a declared regularized scatter.** Initialize $$\bar{\mathbf{M}}_0=\rho\mathbf{I}$$ together
  with $$\bar{\mathbf{M}}_0^{-1}=\rho^{-1}\mathbf{I}$$, state whether that ridge decays, and report
  the covariance corresponding to the regularized scatter rather than to an unregularized one.

The Python implementation uses warm-up, initializing the inverse only after a Cholesky check and a
declared condition limit of $$10^{10}$$. The adapted
[R example]({{ site.baseurl }}/assets/code/2026-online-estimation/inverse-covariance.R) illustrates
the second choice with $$\rho=0.01$$ and hence an initial inverse of $$100\mathbf{I}$$; initializing
both matrices to $$0.01\mathbf{I}$$, which is the natural-looking but inconsistent choice, gives a
product of $$10^{-4}\mathbf{I}$$. Forgetting does hide such a discrepancy after a long run, but the
early estimates then do not describe the same matrix, so the script compares the maintained inverse
against the inverse of the same regularized scatter throughout rather than only at the end. Its
regularized covariance is not labeled an unbiased sample covariance.

<br>

## Verifying the Covariance that is Actually Reported

Run the following beside
[online_estimation.py]({{ site.baseurl }}/assets/code/2026-online-estimation/online_estimation.py):

```python
import numpy as np
from online_estimation import IncrementalMoments

rng = np.random.default_rng(20260426)
X = .01*rng.normal(size=(40, 4))
state = IncrementalMoments(4, track_inverse=True)
state.update(X[:4])
assert state.scatter_inverse is None
for batch in np.array_split(X[4:], 6):
    state.update(batch)
reference_cov = np.cov(X, rowvar=False)
reference_precision = np.linalg.solve(reference_cov, np.eye(4))
np.testing.assert_allclose(state.covariance(), reference_cov, atol=1e-12)
np.testing.assert_allclose(state.precision(), reference_precision, rtol=1e-9)
np.testing.assert_allclose(state.covariance() @ state.precision(), np.eye(4), atol=1e-9)
```

With forgetting enabled, the reference must be an explicitly weighted one rather than `np.cov(X)`
without weights, which otherwise produces a comparison that can only fail for reasons unrelated to
the update. The [companion notebook](/blog/2025/online-batch-estimate-cov-mu/) checks variable
batches and scales, inverse residuals, symmetry, startup, and the no-forgetting limit, across 450
inverse comparisons whose maximum relative error is about $$1.97\cdot10^{-13}$$ and whose maximum
covariance-times-precision residual is about $$1.50\cdot10^{-12}$$.

<br>

## Cost and Numerical Limits

A batch update still requires matrix products in addition to the smaller solve, at an approximate
cost of $$O(d^2\mu+d\mu^2+\mu^3)$$, so whether it is actually faster depends on the dimensions, the
implementation and the hardware. A small batch can certainly help, but $$\mu<d$$ on its own
guarantees nothing, and the timings in the notebook are machine-specific for exactly this reason.

The identities are exact algebraically, while repeated inverse updates accumulate floating-point
error, and the two statements are not in conflict. In a long-running system it is worth monitoring
conditioning and residuals and refactoring the inverse when necessary. Symmetrizing a result can
remove small roundoff asymmetries but cannot repair a genuinely singular estimate, and when only a
few Mahalanobis scores are needed, applying a Cholesky solve may well be preferable to storing a
full inverse at all.

This completes the path from ordinary sample statistics through weighted batches, forgetting,
uncertainty of the mean and finally inverse updates. Each stage uses the same mean-and-scatter
state, with the statistical interpretation and the startup conditions kept explicit throughout.

*Source: thesis Appendix B.2.2.1. The general Woodbury identity is stated with the product
$$\mathbf{V}\mathbf{A}^{-1}\mathbf{U}$$ inside the inner inverse, and the inverse initialization is
made consistent with the scatter it is supposed to invert.*

<br>

## References

<div class="publications">
{% bibliography --file thesis --cited --group_by none %}
</div>
