---
layout: post
title: "Online and Batch-Incremental Estimation of Covariance Matrices and Means in Python"
modified:
categories: [programming,math,stats]
description: "Learn how to estimate the mean, covariance, and inverse covariance matrices in an online or batch-incremental fashion. This post explains the theory behind forgetting factors and effective memory, provides Python implementations for both online and batch estimators, and investigates their accuracy and efficiency through experiments and visualizations."
tags: [math]
thumbnail: "assets/img/2025_09_26_mu_cov_batch_online.png"
giscus_comments: true
toc:
  beginning: true
share: true
date: 2025-09-26T10:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
images:
  compare: false
  slider: false
---

> Estimating the mean and covariance matrix of a dataset is a cornerstone of multivariate statistics and machine learning. While batch (offline) methods are straightforward when all data is available at once, many modern applications require online or streaming estimation — where data arrives sequentially, potentially at very high rates, and storing all past samples is infeasible.
> In this Jupyter Notebook below, we explore fully online and batch-incremental estimators for the mean and covariance matrix, including their inverses. We look at how these algorithms work, why they are useful, and how they can adapt to non-stationary data through a forgetting factor. Importantly, these approaches allow us to update estimates efficiently without recomputing matrix inverses from scratch.
> The goal is to provide both the mathematical background and practical insights for applying online covariance and mean estimation in real-world scenarios such as anomaly detection, adaptive systems, and streaming analytics.

<!--- Move to CSS  --->
<style>
  .jupyter-child-ext {
  width: 112%;
  position: relative;
  left: calc(-10%);
}
</style>

{::nomarkdown}
<div class="jupyter-child-ext">
{% assign jupyter_path = "assets/jupyter/MarkusThill.github.io-jupyter/2025_09_27_online_estimate_cov_mu.ipynb" | relative_url %}
{% capture notebook_exists %}{% file_exists assets/jupyter/MarkusThill.github.io-jupyter/2025_09_26_mahalanobis.ipynb %}{% endcapture %}
{% if notebook_exists == "true" %}
{% jupyter_notebook jupyter_path %}
{% else %}
<p>Sorry, the notebook you are looking for does not exist.</p>
{% endif %}
</div>
{:/nomarkdown}
