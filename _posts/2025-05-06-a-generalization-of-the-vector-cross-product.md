---
layout: post
title: "Beyond 3D: Generalizing the Vector Cross Product"
modified: 2025-05-06T20:33:46+02:00
categories:
description: "Imagine you are working in three-dimensional space and have two directions. You want to find a third direction that is perpendicular to both of them. In this setting, there's a well-known solution: the cross product. When applied to the two original directions, it produces a new one that is exactly orthogonal to both."
tags: [vectors, cross product, high dimensions, generalization, multi dimensionality]
thumbnail: 
giscus_comments: true
toc:
  beginning: true
share:
date: 2025-05-06T20:33:46+02:00
pretty_table: true
related_posts: true
---

\\(
   \def\matr#1{\mathbf #1}
   \def\tp{\mathsf T}
\\)

Imagine you have two 3-dimensional vectors, $$\vec a$$ and $$\vec b$$, and you want to compute a third vector that is orthogonal to both. In three dimensions, this is straightforward: the cross product $$\vec a \times \vec b$$ produces exactly such a vector. It is defined by the familiar formula:

$$
\vec a \times \vec b =
\begin{pmatrix}
a_2b_3 - a_3b_2 \\
a_3b_1 - a_1b_3 \\
a_1b_2 - a_2b_1 \\
\end{pmatrix}.
$$

In two dimensions, the situation is slightly different. Given a single vector $$\vec a$$, its orthogonal counterpart can be obtained via a simple linear transformation:

$$
\begin{pmatrix}
a_1 \\
a_2 \\
\end{pmatrix}
\mapsto
\begin{pmatrix}
a_2 \\
-a_1 \\
\end{pmatrix}
$$

It's easy to verify that the dot product of these two vectors is zero, confirming orthogonality.

But what happens in higher dimensions? How would you define a cross product in 5 dimensions—or even in 100? Is there a generalization of the cross product that still yields a vector orthogonal to a given set of input vectors?


<!--more-->

As it turns out, computing a generalized cross product in higher dimensions is not as difficult as it might seem. In an $$n$$-dimensional space, $$\mathbb{R}^n$$, the generalized cross product takes $$n - 1$$ input vectors, each of length $$n$$. These vectors must be pairwise linearly independent—otherwise, the result will be the zero vector. This condition ensures that the cross product spans the space orthogonal to all input vectors. Hence, we have a set of vectors

$$
\vec u_1 =\begin{pmatrix}
u_{11} \\
u_{21} \\
\vdots \\
u_{n1}
\end{pmatrix},
\vec u_2= \begin{pmatrix}
u_{12} \\
u_{22} \\
\vdots \\
u_{n2}
\end{pmatrix},
\cdots,
\vec u_{n-1} = \begin{pmatrix}
u_{1(n-1)} \\
u_{2(n-1)} \\
\vdots \\
u_{n(n-1)}
\end{pmatrix}.
$$

Let us write the cross product as:

$$
{⨉}_{j=1}^{n-1} \vec u_j = \vec u_1 \times \vec u_2 \times \cdots \times \vec u_{n-1}
$$

Now let us arrange all vectors $$\vec u_1 \cdots \vec u_{n-1}$$ in a matrix. Additionally, we add a standard basis vector $$\vec e_i$$ for dimension $$i$$ as a first column in the matrix:

$$
\matr U^i =  \begin{bmatrix}
 \vec e_i & \vec u_1 & \cdots & \vec u_{n-1}
\end{bmatrix} =

\begin{bmatrix}
\mathbf e_1 & u_{11} & \cdots & u_{1(n-1)}\\
\mathbf e_2 & u_{21} & \cdots & u_{2(n-1)}\\
\vdots & \vdots & \ddots & \vdots\\
\mathbf e_n & u_{n1} & \cdots & u_{n(n-1)}
\end{bmatrix}
$$

The standard basis vector $$\vec e_i$$ has magnitude 1 and points along the $$i$$‑th coordinate axis. By inserting $$\vec e_i$$ as the first column in our matrix, we obtain a slightly different matrix $$\matr U^i$$ for each dimension $$i$$.

The generalized cross product can then be expressed in terms of determinants. While we won't go into the full derivation here, the key idea is that each component of the resulting vector corresponds to the determinant of one of these matrices. Specifically, the $$i$$‑th component of the cross product is given by:

$$
\Big({⨉}_{j=1}^{n-1} \vec u_j \Big ) _ {i} = \mbox{det}(\matr U_i) = |\matr U_i|
$$

Overall, we receive a vector in the following form:

$$
{⨉}_{j=1}^{n-1} \vec u_j  =
\begin{pmatrix}
  \mbox{det}(\matr U_1) \\
  \mbox{det}(\matr U_2) \\
  \vdots \\
  \mbox{det}(\matr U_n) \\
\end{pmatrix}
$$

Since the first column of $$\matr U_i$$ contains only a single nonzero entry (a 1 in row $$i$$), the determinant can be efficiently computed using Laplace expansion along the first column. This reduces the computation to a single minor, making the process both simple and elegant.

Let’s illustrate this with our initial example using the vectors:

$$
\vec a =\begin{pmatrix}
a_{1} \\
a_{2} \\
a_3
\end{pmatrix},
\vec b =\begin{pmatrix}
b_{1} \\
b_{2} \\
b_3
\end{pmatrix}.
$$

We first create the matrix $$\matr U_i$$, which is:

$$
\matr U_i  =\begin{bmatrix}
\mathbf e_1 & a_{1} & b_{1}\\
\mathbf e_2 & a_{2} & b_{2}\\
\mathbf e_3 & a_3 & b_3
\end{bmatrix}.
$$

Then, we can compute the first element of the cross product vector for axis $$i=1$$:

$$
\begin{align*}
\mbox{det}(\matr U_1) &=
\begin{vmatrix}
\mathbf 1 & a_{1} & b_{1}\\
\mathbf 0 & a_{2} & b_{2}\\
\mathbf 0 & a_3 & b_3
\end{vmatrix} \\
& =
1 \cdot \begin{vmatrix}
 a_{2} & b_{2}\\
 a_3 & b_3
\end{vmatrix} -
0 \cdot \begin{vmatrix}
 a_{1} & b_{1}\\
 a_3 & b_3
\end{vmatrix} +
0 \cdot  \begin{vmatrix}
 a_{1} & b_{1}\\
 a_{2} & b_{2}
\end{vmatrix} \\
& =
a_2 b_3 - a_3 b_2
.
\end{align*}
$$

For the other two axis $$i=2$$ and $$i=3$$ we follow the same procedure and get:

$$
\begin{align*}
\mbox{det}(\matr U_2) &=
\begin{vmatrix}
\mathbf 0 & a_{1} & b_{1}\\
\mathbf 1 & a_{2} & b_{2}\\
\mathbf 0 & a_3 & b_3
\end{vmatrix} \\
& =
0 \cdot \begin{vmatrix}
 a_{2} & b_{2}\\
 a_3 & b_3
\end{vmatrix} -
1 \cdot \begin{vmatrix}
 a_{1} & b_{1}\\
 a_3 & b_3
\end{vmatrix} +
0 \cdot  \begin{vmatrix}
 a_{1} & b_{1}\\
 a_{2} & b_{2}
\end{vmatrix} \\
& =
a_3 b_1 - a_1 b_3
\end{align*}
$$

$$
\begin{align*}
\mbox{det}(\matr U_3) &=
\begin{vmatrix}
\mathbf 0 & a_{1} & b_{1}\\
\mathbf 0 & a_{2} & b_{2}\\
\mathbf 1 & a_3 & b_3
\end{vmatrix} \\
& =
0 \cdot \begin{vmatrix}
 a_{2} & b_{2}\\
 a_3 & b_3
\end{vmatrix} -
0 \cdot \begin{vmatrix}
 a_{1} & b_{1}\\
 a_3 & b_3
\end{vmatrix} +
1 \cdot  \begin{vmatrix}
 a_{1} & b_{1}\\
 a_{2} & b_{2}
\end{vmatrix} \\
& =
a_1 b_2 - a_2 b_1
.
\end{align*}
$$

Summarizing the previous results, we receive for the cross product $$\vec a \times \vec b $$:

$$
\vec a \times \vec b =
\begin{pmatrix}
  \mbox{det}(\matr U_1) \\
  \mbox{det}(\matr U_2) \\
  \mbox{det}(\matr U_3) \\
\end{pmatrix}
=
\begin{pmatrix}
  a_2 b_3 - a_3 b_2 \\
  a_3 b_1 - a_1 b_3 \\
  a_1 b_2 - a_2 b_1 \\
\end{pmatrix}
$$

which is exactly the same as we have already noted in the beginning.


Note that the base R function `crossprod()` does not compute the vector cross product as discussed in this post—it actually returns the matrix product $$A^\top B$$. To compute the generalized cross product in arbitrary dimensions, I provide a custom R function below that implements the determinant-based method described above.

{% highlight R %}
opX <- function(...) {
  u <- list(...)
  #
  # check length of all vectors
  #
  len <- unlist(lapply(u, length))
  if(!all(len == len[1])) stop("All vectors must be of same length!")
  len <- len[1]
  #
  # Check, if correct number of vectors is provided
  #
  if(length(u) != (len - 1) ) stop("For vector length ",len," you have to provide ",len-1, " vectors!")
  U <- do.call(cbind, u)

  #
  # Compute the determinants based on the minors of U and Laplace's formula
  # The determinants form the new vector which is the result of the cross-product
  #
  sapply(1:len, function(i) (-1)^(i + 1) * det(as.matrix(U[-i,])))
}

#
# Run an example
#
a <- c(1,2,3,4)
b <- c(5,6,7,8)
c <- c(9,10,-11,12)

print(opX(a,b,c))

#
# Check the orthogonality property
#
print(t(a) %*% opX(a,b,c))
print(t(b) %*% opX(a,b,c))
print(t(c) %*% opX(a,b,c))
{% endhighlight %}
<!--- %* -->
