---
layout: post
title: "Implementing the Mahalanobis Distance in Python"
modified:
categories: [programming,math,stats]
description: "A hands-on Jupyter Notebook implementation of the Mahalanobis distance in Python. Covers theory, multiple implementations (NumPy, JAX, TensorFlow, SciPy), benchmarking on low- and high-dimensional data, visualizations, and its connection to the Chi-square distribution for anomaly detection."
tags: [math]
thumbnail: "assets/img/mahalanobis-zca-whitening.png"
giscus_comments: true
toc:
  beginning: true
share: true
date: 2025-09-24T10:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
images:
  compare: false
  slider: false
---


> Below you will find a Jupyter Notebook that explores the Mahalanobis distance in depth.  
> It begins with the theoretical foundations and practical applications, followed by multiple Python implementations (NumPy, JAX, TensorFlow, SciPy) to ensure correctness and compare performance.  
> The notebook validates these implementations, benchmarks them across low- and high-dimensional datasets, and illustrates the geometric intuition behind the Mahalanobis distance through visualizations and whitening transformations.  
> Finally, it demonstrates the close connection to the Chi-square distribution and applies the method to a simple anomaly detection task.  
>
> The aim is to provide both a solid theoretical understanding and practical tools for applying the Mahalanobis distance in real-world scenarios.

👉 A more theoretical discussion of the Mahalanobis distance and its connection to the Chi-square distribution can be found **[here]({% post_url 2025-09-25-mahalanobis-distance %})**.


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
{% assign jupyter_path = "assets/jupyter/MarkusThill.github.io-jupyter/2025_09_26_mahalanobis.ipynb" | relative_url %}
{% capture notebook_exists %}{% file_exists assets/jupyter/MarkusThill.github.io-jupyter/2025_09_26_mahalanobis.ipynb %}{% endcapture %}
{% if notebook_exists == "true" %}
{% jupyter_notebook jupyter_path %}
{% else %}

<p>Sorry, the notebook you are looking for does not exist.</p>
{% endif %}
</div>
{:/nomarkdown}
