---
layout: post
title: "Short Notes: Gradient of the Softmax Function for the Cross-Entropy Loss"
modified:
categories: [stats, ML, math]
description: The softmax function in neural networks ensures outputs sum to one and are within [0,1]. Here's how to compute its gradients when the cross-entropy loss is applied.
tags: softmax cross-entropy gradient backprop
giscus_comments: true
share:
date: 2024-05-03T19:29:40+02:00
---

In practice, the so-called softmax function is often used for the last layer of a neural network when several output units are required. Its purpose is to squash all outputs into the range of $$[0,1]$$ in a way that they sum up to one. This is particularly useful in classification tasks, where each output represents the probability of the input vector belonging to a specific class. When training the neural network weights using the classical backpropagation algorithm, it's necessary to compute the gradient of the loss function. In the following, we demonstrate how to compute the gradient of a softmax function for the cross-entropy loss, assuming the softmax function is utilized in the output layer of the neural network.

<!--more-->

The softmax function for a unit $$z_j$$ is defined as:

$$
\begin{eqnarray*}
o_j = \frac{\mbox{e}^{z_j}}{\sum_k \mbox{e}^{z_k}},
\end{eqnarray*}
$$

where $$k$$ iterates over all output units.
The cross-entropy loss for a softmax unit with $$p$$ output units $$o_j$$ and targets $$y^*_j$$ is defined as:

$$
\begin{eqnarray*}
E=-\sum_j^{p} y^*_j\cdot \mbox{log}(o_j).
\end{eqnarray*}
$$

In order to compute the gradient of $$E$$ with respect to $$z_i$$, we can start with:

$$
\begin{align}
\frac{\partial E}{\partial z_i}&=- \sum_j^{p} y^*_j\cdot  \frac{\partial}{\partial z_i}\mbox{log}(o_j) \nonumber \\
&=- \sum_{j \neq i}^{p} y^*_j\cdot  \frac{\partial}{\partial z_i}\mbox{log}(o_j) - y^*_i\cdot  \frac{\partial}{\partial z_i}\mbox{log}(o_i).
\label{eq:partialSoftmax}
\end{align}
$$

Now we compute both partial derivatives of $$o_j$$ and $$o_i$$, which lead to different results:

$$
\begin{align}
  \frac{\partial}{\partial z_i} o_j &= \frac{\partial}{\partial z_i} \frac{\mbox{e}^{z_j}}{\sum_k \mbox{e}^{z_k}}\nonumber \\
  &= \mbox{e}^{z_j} \frac{\partial}{\partial z_i} \Bigg(\sum_k \mbox{e}^{z_k} \Bigg)^{-1} \nonumber \\
  &= -\mbox{e}^{z_j} \Bigg(\sum_k \mbox{e}^{z_k} \Bigg)^{-2} \mbox{e}^{z_i} \nonumber \\
  &= -o_j \cdot o_i,
  \label{eq:partialOj}
\end{align}
$$

and

$$
\begin{align}
  \frac{\partial}{\partial z_i} o_i &= \frac{\partial}{\partial z_i} \frac{\mbox{e}^{z_i}}{\sum_k \mbox{e}^{z_k}} \nonumber \\
  &= \frac{\mbox{e}^{z_i}}{\sum_k \mbox{e}^{z_k}} + \mbox{e}^{z_i}\frac{\partial}{\partial z_i} \frac{1}{\sum_k \mbox{e}^{z_k}} \nonumber \\
  &= \frac{\mbox{e}^{z_i}}{\sum_k \mbox{e}^{z_k}} - \mbox{e}^{z_i} \Big(\sum_k \mbox{e}^{z_k}\Big)^{-2} \mbox{e}^{z_i} \nonumber \\
  &= o_i - o_i^2.
  \label{eq:partialOi}
\end{align}
$$

We can simplify Eq. \eqref{eq:partialSoftmax} with these two partial derivatives:

$$
\begin{align}
\frac{\partial E}{\partial z_i}&=-\sum_{j \neq i}^{p} y^*_j\cdot  \frac{\partial}{\partial z_i}\mbox{log}(o_j) - y^*_i\cdot  \frac{\partial}{\partial z_i}\mbox{log}(o_i) \nonumber \\
&= -\sum_{j \neq i}^{p} y^*_j \frac{1}{o_j} \frac{\partial}{\partial z_i}o_j - y^*_i \frac{1}{o_i} \frac{\partial}{\partial z_i}o_i.
\label{eq:partialSoftmax2}
\end{align}
$$

Finally, we insert \eqref{eq:partialOj} and \eqref{eq:partialOi} into \eqref{eq:partialSoftmax2}:

$$
\begin{align*}
\frac{\partial E}{\partial z_i}
&= \sum_{j \neq i}^{p} y^*_j \frac{1}{o_j} o_j \cdot o_i - y^*_i \frac{1}{o_i} (o_i - o_i^2)\\
&= \sum_{j \neq i}^{p} y^*_j   o_i - y^*_i  (1 - o_i)\\
&= o_i\sum_{j \neq i}^{p} y^*_j    - y^*_i   + y^*_i  o_i \\
&= o_i \underbrace{\sum_{j =1}^{p} y^*_j }_{=1}   - y^*_i  \\
&= o_i  - y^*_i.
\end{align*}
$$
