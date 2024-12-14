---
layout: post
title: "Efficient Computation of Sparse Fibonacci Subsequences"
modified:
categories: 
tags: [math, fibonacci, sequences]
description: "The Fibonacci sequence is a cornerstone of mathematics, defined by its elegant recurrence relation. While traditionally computed iteratively or recursively, obtaining specific terms like the 1000th or 2000th number seems to require calculating all preceding terms. But is this really necessary?  

In this post, we explore a powerful technique to compute arbitrary Fibonacci terms directly — bypassing the need for sequential computation. We’ll also tackle an exciting challenge: efficiently finding one thousand Fibonacci numbers modulo a given value, corresponding to every 10th prime greater than a trillion.  
"
thumbnail: assets/img/fibonacci-rabbits.webp
giscus_comments: true
featured: False
share:
date: 2024-12-13 01:16:00
---

The Fibonacci sequence is defined as:  
$$F_0 = 0, \ F_1 = 1,$$ and $$F_n = F_{n-1} + F_{n-2}$$ for $$n > 1$$.

The first few elements of the sequence are:  
$$
0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, \ldots
$$

Using the classical recurrence relation above, we need to know all preceding elements of the series up to $$n-1$$ in order to obtain $$F_n$$. For example, to compute $$F_{10} = 55$$, we first calculate $$F_9 = 34$$ and $$F_8 = 21$$, which themselves depend on earlier values in the sequence.

Here, we aim to explore the possibility of generating an arbitrary subsequence of the Fibonacci sequence without the need to calculate all preceding terms. For example, we may be interested in computing only $$F_{100}$$, $$F_{555}$$, $$F_{1000}$$, and $$F_{2000}$$. Is it possible to compute these specific terms directly, without generating the entire sequence up to $$F_{2000}$$?  
As we will see, this is indeed possible.

In the example below, we attempt to find one thousand Fibonacci numbers modulo $m$ for every 10th prime number greater than $$10^{15}$$:

$$
S = \{F_{p_{10k}} \bmod m \mid p_{10k} \text{ is the } 10k\text{-th prime number such that } p_{10k} > 10^{15}, \, 0 \leq k < 1000 \}.
$$

Follow along in the Jupyter notebook below:

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
{% assign jupyter_path = "assets/jupyter/MarkusThill.github.io-jupyter/2024_12_14_pe_204p100_fibo_subsequences.ipynb" | relative_url %}
{% capture notebook_exists %}{% file_exists assets/jupyter/MarkusThill.github.io-jupyter/2024_12_14_pe_204p100_fibo_subsequences.ipynb %}{% endcapture %}
{% if notebook_exists == "true" %}
{% jupyter_notebook jupyter_path %}
{% else %}
<p>Sorry, the notebook you are looking for does not exist.</p>
{% endif %}
</div>
{:/nomarkdown}