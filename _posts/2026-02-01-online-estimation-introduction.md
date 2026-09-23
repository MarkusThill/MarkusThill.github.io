---
layout: post
title: "Online Estimation&#58; Learning from a Changing Data Stream"
modified:
categories: [math, stats, ML]
description: "Why streaming anomaly detection needs incremental statistics, and how this series connects means, covariances, forgetting and inverse updates back to Appendix B.2 of my PhD thesis."
tags: [online estimation, covariance, data streams, anomaly detection, forgetting factor, math]
thumbnail: assets/img/2026-online-estimation/stats.jpg
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-02-01T10:00:00+01:00
pretty_table: true
related_posts: true
series: online-estimation
series_part: 1
---

{% include series_online_estimation.liquid %}

A sensor does not wait for us to collect a complete dataset. It sends another measurement, then
another, while the system being monitored may quietly change its operating conditions. If we want
to decide whether the next measurement is unusual, we need a description of normal behavior which
can be updated as the measurements arrive, and which does not require us to keep every observation
we have ever seen. That requirement sounds like an engineering compromise, but as we will see it
costs surprisingly little: most of the statistics we care about can be maintained exactly, one
observation at a time.

This was one of the recurring problems during my PhD work, and Appendix B.2 of my thesis
{% cite thill2022machine --file thesis %} develops the incremental updates behind it. The detection
methods in that thesis differ considerably from one another, but several of them need the same
statistical building blocks: an estimated mean, an estimated covariance, and sometimes the inverse
covariance. The appendix derives all three in one place, and this series follows those derivations
step by step rather than quoting their results.

We will begin with ordinary sample statistics, introduce weights and forgetting, and then derive
updates which process several observations at once. Each article carries the algebra through in
full, since the intermediate steps are where the subtleties live. R and Python examples accompany
the derivations, and a companion notebook provides the reproducible simulations and numerical
comparisons.

<!--more-->

<br>

## What an Online Estimator Has to Retain

Suppose each incoming observation is a vector $$\mathbf{x}_n\in\mathbb{R}^d$$. A monitoring
application might use its coordinates to represent several sensor readings, prediction errors, or
features extracted from a time window. The mean $$\bar{\mathbf{x}}_n$$ describes the center of the
observations, and the covariance $$\bar{\boldsymbol{\Sigma}}_n$$ describes variation within each
coordinate as well as dependence between coordinates. Recomputing both quantities from all previous
observations is unnecessary, since we can instead retain a mean, a scatter matrix, and a few scalar
weight sums. Each new observation changes this state, which uses $$O(d^2)$$ space regardless of how
many observations have arrived; updating the full covariance for one observation takes $$O(d^2)$$
arithmetic.

The crucial point, and the one which makes the whole exercise worthwhile, is that incremental
processing does not by itself imply an approximation. If the observations and their weights are the
same, the derived updates reproduce the corresponding full-data statistics in exact arithmetic.
Floating-point rounding still matters, of course, and it matters considerably more for inverse
matrices than for the mean, which is why the last article in the series spends some time on
conditioning and on when an inverse may be formed at all.

<br>

## The Connection to Anomaly Detection

In the SORAD setting of the thesis, prediction errors provide the information about unexpected
behavior. Estimating the recent mean and variance of those errors lets the detector account for
the error distribution rather than relying on a fixed scale chosen once at the start, which is
useful precisely because the scale of the errors is usually not known in advance. The online
DWT-MLEAD setting uses multivariate features and Gaussian modeling instead, and here the
covariance matters because an unusual combination of otherwise ordinary feature values can be
informative in itself. A common measure of departure from an estimated center is the squared
Mahalanobis distance,

$$
D^2(\mathbf{x})=(\mathbf{x}-\bar{\mathbf{x}})^T
\bar{\boldsymbol{\Sigma}}^{-1}(\mathbf{x}-\bar{\mathbf{x}}).
$$

This expression accounts for covariance between coordinates, and it also explains why the final
article considers updating an inverse rather than only a covariance. The inverse exists only when
the estimated covariance is nonsingular, and a stream's first few observations generally do not
provide enough information for that. It is worth noting that the estimation formulas are building
blocks rather than a complete anomaly detector: choosing when to score an observation, whether to
incorporate a suspected anomaly into the model, and how to calibrate a decision threshold all
remain part of the detection method.

<br>

## The Cost of Remembering Everything

A factory may change production mode, a machine may age, and a sensor's normal range may depend on
its environment. In such situations an average of the entire history increasingly describes a
mixture of past conditions, and the longer the estimator runs, the less any single one of those
conditions is represented. Giving more weight to recent observations offers a way to adapt.
Exponential forgetting is particularly convenient here: each update multiplies every old weight by
the same factor $$\lambda$$, with $$0<\lambda\leq1$$, so that although every historical weight
changes, we can update the estimates using only the stored state.

This creates a tradeoff which runs through the rest of the series. A long memory reduces random
fluctuations in a stationary setting, while a short memory responds more quickly to a change. We
will make one aspect of this tradeoff precise by measuring the covariance of the estimated mean,
which is a different quantity from the estimated covariance of the observations and is easy to
confuse with it. Mini-batches add another choice on top of this, since forgetting once per batch
and forgetting once per observation use different notions of elapsed time. I will keep that
distinction explicit throughout, and show how a batch can reproduce the observation-by-observation
calculation exactly when that is what we want.

<br>

## Notation and Route through the Series

The notation follows the thesis. In particular, $$\mu$$ denotes **batch size** rather than a
population mean, which is a slightly unusual convention and worth stating clearly at the outset.
Where a population mean is needed we write it as $$\boldsymbol{\mu}_X$$.

| Symbol | Meaning |
| --- | --- |
| $$\mathbf{x}_i$$ | An observed column vector in $$\mathbb{R}^d$$ |
| $$\boldsymbol{\Delta}_n$$ | Deviation of the new observation from the current mean, $$\mathbf{x}_n-\bar{\mathbf{x}}_{n-1}$$ |
| $$\bar{\mathbf{x}}_n$$ | Estimated mean after $$n$$ observations |
| $$\boldsymbol{\mu}_X$$ | Population mean (to avoid confusion with the batch size $$\mu$$) |
| $$\bar{\mathbf{M}}^{(n)}$$ | Unnormalized scatter matrix |
| $$\boldsymbol{\Delta}\bar{\mathbf{M}}^{(n)}$$ | Scatter increment at step $$n$$ |
| $$\bar{\boldsymbol{\Sigma}}_n$$ | Estimated covariance, with normalization stated explicitly |
| $$\boldsymbol{\Sigma}$$ | Population covariance |
| $$w'_i$$, $$w_i$$ | Unnormalized and normalized observation weights |
| $$W_n$$, $$W_n^{(2)}$$ | Sum of weights and sum of squared weights |
| $$\mu$$ | Batch size (not a population mean) |
| $$\lambda$$ | Forgetting factor, $$0<\lambda\leq1$$ |
| $$\boldsymbol{\sigma}_j$$ | Sum of the observations in batch $$j$$ |
| $$\boldsymbol{\mathcal{X}}_n$$ | Centered data matrix for the current batch |
| $$\mathbf{D}_n$$ | Deviation matrix whose rows are the $$\boldsymbol{\Delta}_i$$ of the batch |
| $$\mathbf{P}_n$$ | Inverse scatter $$\bar{\mathbf{M}}_n^{-1}$$, when it exists |
| $$\rho$$ | Regularization parameter for the initial scatter |
| $$n_{\mathrm{mem}}$$ | Effective sample size giving the same covariance of the mean under the stated IID assumptions |

The arithmetic identities require neither Gaussian observations nor independence, which is one
reason the derivations are shorter than one might expect. Statistical statements about unbiasedness
and sampling uncertainty do require assumptions, and I will state them where they enter. This
matters particularly for time series, since temporal dependence does not disappear simply because
an estimator happens to be updated online.

The next article starts with the ordinary mean and covariance. The weighted derivation which
follows it then gives a common foundation for both mini-batches and forgetting, and the two
articles on uncertainty and memory explain how to interpret the resulting estimates before we turn
to inverse updates at the end.

<br>

## Code and Companion Notebook

The [Python companion notebook](/blog/2025/online-batch-estimate-cov-mu/) contains the complete
experiments and is rendered as its own post. The
[example README]({{ site.baseurl }}/assets/code/2026-online-estimation/README.md) lists the Python
and R scripts, their dependencies, and the reproducible figures used throughout the series.

*The derivations follow Appendix B.2 of the thesis, together with the thesis introduction,
SORAD §4.2.3 and online DWT-MLEAD §5.3.2. The corrections applied to the thesis appendix and to
the accompanying code are recorded in the editorial review shipped alongside the examples.*

<br>

## References

<div class="publications">
{% bibliography --file thesis --cited --group_by none %}
</div>
