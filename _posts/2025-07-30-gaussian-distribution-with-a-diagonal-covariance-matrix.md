---
layout: post
title: "Short Notes: The Multivariate Gaussian Distribution With a Diagonal Covariance Matrix"
modified: 2025-07-30T20:00:51+01:00
categories: [math, statistics]
description: "This post explores how a multivariate Gaussian distribution simplifies when the covariance matrix is diagonal. By breaking down the math, we show how the density function factorizes into a product of independent univariate Gaussians—making both interpretation and computation more tractable."
tags: [multivariate-gaussian, diagonal-covariance, probability-distribution]
thumbnail: assets/img/gaussian_cartoon.png
giscus_comments: true
#toc:
#  beginning: true
share: true
date: 2025-07-30T20:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
# related_publications: true
---

When the off-diagonal entries of a covariance matrix are negligible, it's often convenient to use an alternative representation of a multivariate Gaussian distribution. In such cases, we can assume the covariance matrix is diagonal, allowing the mean and variance to be estimated independently for each dimension. This simplification leads to a factorized form of the multivariate density function as a product of univariate Gaussians, as shown below.

<!--more-->

Assume we are given a diagonal covariance matrix of the form:

$$
\Sigma =
\begin{pmatrix}
\sigma_1^2 & 0 & \cdots & 0 \\
0 & \sigma_2^2 & \cdots & 0 \\
\vdots & \vdots & \ddots & \vdots \\
0 & 0 & \cdots & \sigma_k^2 \\
\end{pmatrix}.
$$

The density function of a multivariate Gaussian distribution is given by:

$$
f_x(x_1, \ldots, x_k) = \frac{\exp\left(-\frac{1}{2} (\vec{x} - \vec{\mu})^T \Sigma^{-1} (\vec{x} - \vec{\mu})\right)}{\sqrt{(2\pi)^k |\Sigma|}}.
$$

Let us define:

$$
\vec{y} = \vec{x} - \vec{\mu}.
$$

Then the expression becomes:

$$
f_x(x_1, \ldots, x_k) = \frac{\exp\left(-\frac{1}{2} \vec{y}^T \Sigma^{-1} \vec{y}\right)}{\sqrt{(2\pi)^k |\Sigma|}}.
$$

Recall that the inverse of a diagonal matrix is simply the reciprocal of its diagonal elements:

$$
\Sigma^{-1} =
\begin{pmatrix}
\sigma_1^2 & 0 & \cdots & 0 \\
0 & \sigma_2^2 & \cdots & 0 \\
\vdots & \vdots & \ddots & \vdots \\
0 & 0 & \cdots & \sigma_k^2 \\
\end{pmatrix}^{-1}
=
\begin{pmatrix}
\frac{1}{\sigma_1^2} & 0 & \cdots & 0 \\
0 & \frac{1}{\sigma_2^2} & \cdots & 0 \\
\vdots & \vdots & \ddots & \vdots \\
0 & 0 & \cdots & \frac{1}{\sigma_k^2}
\end{pmatrix}.
$$

Substituting this back into the expression:

$$
f_x(x_1, \ldots, x_k) = \frac{\exp\left(-\frac{1}{2} \left( \frac{y_1^2}{\sigma_1^2} + \frac{y_2^2}{\sigma_2^2} + \cdots + \frac{y_k^2}{\sigma_k^2} \right) \right)}{\sqrt{(2\pi)^k |\Sigma|}}.
$$

The determinant of a diagonal matrix is the product of its diagonal entries:

$$
|\Sigma| =
\begin{vmatrix}
\sigma_1^2 & 0 & \cdots & 0 \\
0 & \sigma_2^2 & \cdots & 0 \\
\vdots & \vdots & \ddots & \vdots \\
0 & 0 & \cdots & \sigma_k^2 \\
\end{vmatrix}
= \sigma_1^2 \cdot \sigma_2^2 \cdots \sigma_k^2.
$$

Putting it all together:

$$
\begin{align}
f_x(x_1, \ldots, x_k)
&= \frac{\exp\left(-\frac{1}{2} \left( \sum_{i=1}^k \frac{y_i^2}{\sigma_i^2} \right) \right)}{\sqrt{(2\pi)^k \prod_{i=1}^k \sigma_i^2}} \\
&= \prod_{i=1}^k \frac{\exp\left( -\frac{y_i^2}{2\sigma_i^2} \right)}{\sqrt{2\pi \sigma_i^2}} \\
&= \prod_{i=1}^k \frac{\exp\left( -\frac{(x_i - \mu_i)^2}{2\sigma_i^2} \right)}{\sqrt{2\pi \sigma_i^2}} \\
&= f_1(x_1) \cdot f_2(x_2) \cdots f_k(x_k).
\end{align}
$$

This shows that under the assumption of a diagonal covariance matrix, the multivariate Gaussian density factorizes into a product of independent univariate Gaussian densities.
