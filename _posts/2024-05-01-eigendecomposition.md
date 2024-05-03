---
layout: post
title: "Short Notes: The Eigendecomposition"
discription: 
modified:
categories: math
description: The derivation of the eigendecomposition is surprisingly simple. Read more here!
tags: code eigendecomposition python
thumbnail: 
giscus_comments: true
featured: False
share:

date: 2024-05-01 09:16:00
---

A vector $$\mathbf{v}_i \in \mathbb{C}^{n}$$ is called the $$i$$-th eigenvector of a matrix $$\mathbf{A} \in \mathbb{R}^{n \times n}$$, if it satisfies the simple equation 

$$
\begin{align}
    \mathbf{A} \mathbf{v}_i = \lambda_i \mathbf{v}_i,  \label{eq:eigvalues}
\end{align}
$$

for a scalar value $$\lambda_i \in \mathbb{C}$$, called an eigenvalue. (Assuming the matrix $$\mathbf{A}$$ is real-valued, the eigenvalues and eigenvectors might still be complex.)
Let us further assume that the $$n$$ eigenvectors of matrix $$\mathbf{A}$$ are linearly independent.

We can now 'horizontally' stack the eigenvectors into a matrix $$\mathbf{Q} \in \mathbb{C}^{n \times n}$$:

$$
\begin{align}
    \mathbf{Q} = \big[\mathbf{v}_1, \mathbf{v}_2, \ldots, \mathbf{v}_n \big].  \label{eq:Q}
\end{align}
$$

Multiplying $$\mathbf{A}$$ with $$\mathbf{Q}$$ gives us:

$$
\begin{align}
    \mathbf{A}\mathbf{Q} = \big[\mathbf{A}\mathbf{v}_1, \mathbf{A}\mathbf{v}_2, \ldots, \mathbf{A}\mathbf{v}_n \big].  \label{eq:AQ}
\end{align}
$$

If we compare Eq. \eqref{eq:AQ} with Eq. \eqref{eq:eigvalues}, we can see that:

$$
\begin{align}
    \mathbf{A}\mathbf{Q} = \big[\lambda_1\mathbf{v}_1, \lambda_2\mathbf{v}_2, \ldots, \lambda_n\mathbf{v}_n \big].  \label{eq:AQ_2}
\end{align}
$$

If we now define a diagonal matrix carrying the eigenvalues $$\lambda_i$$ as

$$
\begin{align}
    \mathbf{\Lambda} = 
        \begin{bmatrix}
            \lambda_1 & 0 & \ldots & 0\\
            0 & \lambda_2 & \ldots & 0 \\
            \vdots & \vdots & \ddots & \vdots \\
            0 & 0 & \ldots & \lambda_n
        \end{bmatrix}, \label{eq:Lambda}
\end{align}
$$

we see that

$$
\begin{align}
    \mathbf{Q}\mathbf{\Lambda} = \big[\lambda_1\mathbf{v}_1, \lambda_2\mathbf{v}_2, \ldots, \lambda_n\mathbf{v}_n \big]  \label{eq:AQ_3}
\end{align}
$$

which is equal to Eq. \eqref{eq:AQ_2}:

$$
\begin{align}
    \mathbf{Q}\mathbf{\Lambda} = \mathbf{A}\mathbf{Q}.  \label{eq:AQ_4}
\end{align}
$$

One final rearrangement -- post-multiplying Eq. \eqref{eq:AQ_4} with $$\mathbf{Q}^{-1}$$ -- and we are done:

$$
\begin{align}
    \mathbf{A} = \mathbf{Q}\mathbf{\Lambda}\mathbf{Q}^{-1}.  \label{eq:eigendecomposition}
\end{align}
$$

Eq. \eqref{eq:eigendecomposition} is also called the eigendecomposition of matrix $$\mathbf{A}$$.


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
{% assign jupyter_path = "assets/jupyter/MarkusThill.github.io-jupyter/2024_05_01_eigendecomposition_example.ipynb" | relative_url %}
{% capture notebook_exists %}{% file_exists assets/jupyter/MarkusThill.github.io-jupyter/2024_05_01_eigendecomposition_example.ipynb %}{% endcapture %}
{% if notebook_exists == "true" %}
{% jupyter_notebook jupyter_path %}
{% else %}

<p>Sorry, the notebook you are looking for does not exist.</p>
{% endif %}
</div>
{:/nomarkdown}