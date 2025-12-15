---
layout: post
title: "Yet another Neural Networks Introduction: Feed Forward Networks and the Backpropagation Algorithm"
modified: 2025-12-13T09:00:51+01:00
categories: [Math, Neural Nets]
description: "A few notes on the backprop algorithm"
tags: []
thumbnail: 
giscus_comments: true
toc:
  beginning: true
share: true
date: 2025-12-13T09:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
# related_publications: true

#authors:
#  - name: Markus Thill
#    url: "https://en.wikipedia.org/wiki/Albert_Einstein"
#    affiliations:
#      name: Private blog post
#
#bibliography: 2018-12-22-distill.bib
#
#toc:
#  - name: Neural Networks
#    subsections:
#      - name: Introduction
#      - name: The Backpropagation Algorithm
---

\\(
\renewcommand{\vec}[1]{\boldsymbol{\mathbf{#1}}}
\def\matr#1{\boldsymbol{\mathbf{#1}}}
\def\Wmatr{\matr{W}}
\newcommand{\din}{\mathord{d_0}}
\newcommand{\batch}{\mathord{N}}
\newcommand{\yhat}{\vec{\hat{y}}}
\\)

**TODO**: matrices bold, vectors bold!
- Intro: The only tricky thing about neural nets is to get the notation straight. At the end, every thing boils down to notation, notation, notation...
- Notation guide: ...
- Put certain posts on medium!
- Animation of Gradient descent here!
- Compare Gradients to JAX
- Take a look at EDX lecture and homework!!
- Talk about other optimizers that take into account gradient and cost, such as fminunc, fmincg, L-BFGS (fmincon in MATLAB, FMINLBFGS in MATALB), ..., online L-BFGS, ..., other online Training algorithms that only require the gradient
- Visualize the first hidden layer of the net (without biases). E.g., for the hand-written digits set, it can be shown what features the different units have learned.
- Add regularization to the implementation of the cost-function. The derivation afterwards is quite simple, since the regularization term for a weight is just dependent on the weight, so that the derivative can be computed in one simple step...
- Describe Gradient Checking...
- Describe **random initialization for breaking the symmetry**. Take a look at the literature
- Softmax output layer with log-liklihood cost
- Second order techniques for optimizing the cost function using the Hessian: See \url{http://neuralnetworksanddeeplearning.com/chap3.html} for an intro.
- Momentum for addreesing the step-size problem
- Step-size adaptation: RProp, IDBD, ...
- Normalizing the input


# Neural Networks

## Notation Guide
$\din$: Dimension of the input vector $\vec x$

## Introduction
- Motivation: Understand the nuts and bolts of neural networks and especially how the neural net is trained using the so-called backpropagation algorithm, which is effectively just some clever & efficient recursive implementation of the gradient descent optimization.
- Neural networks are not really hard to understand. The main problem that many people have, is to get the notation straight. At the end of the end, neural networks are just notation, notation & notation, and less math like multivariate differential calculus.
- Thus, I would recommend to try to work out the notation and math yourself and write down your own understanding of the neural net and come up with an notation that you can understand -> This is what I did!
- Also, I implemented a feedforward neural net from scratch, based on the formulas derived below.
- We will also look at some practical considerations when training neural networks, which are important to make the training work, like weight initialization and gradient checking.

## Classical Feed-Forward Neural Network Architecture

Figure 1 illustrates the general structure of a typical fully connected feed-forward
neural network. The network consists of $L$ feed-forward layers with trainable
weights, starting with the first hidden layer at $\ell = 1$ and ending with the
output layer at $\ell = L$.

In total, the network comprises $L + 1$ layers, since the input is treated as an
additional layer at $\ell = 0$. This input layer does not contain trainable
parameters but serves to provide the input values to the network. The layer at
$\ell = L$ is the output layer, while the layers with indices $1 \le \ell < L$ are
referred to as hidden layers. The input to the network is given by the vector
$\vec{x} = (x_1, x_2, \ldots, x_{\din})^\top \in \mathbb{R}^{\din}$, where $\din$
denotes the input dimension. In the input layer, the components of $\vec{x}$ are
identified with the activations $a_i^{(0)} = x_i$. Throughout this work, a
superscript $(\ell)$ is used to indicate that a quantity is associated with layer
$\ell$.

Each layer $\ell$ consists of $d_\ell$ neurons, where $d_0 = \din$ corresponds to
the input dimension and $d_L$ denotes the output dimension of the network.
 In Figure 1, neurons are depicted
as circles with incoming arrows. A neuron (also referred to as a node or unit) is
the fundamental computational element of a neural network. It receives inputs from
the preceding layer, forms a weighted sum of these inputs, adds a bias term, and
subsequently applies a nonlinear activation function to produce its output. The
output of the $i$-th neuron in layer $\ell$ is typically referred to as the
activation $a_i^{(\ell)}$.

The neurons of adjacent layers are fully connected, meaning that each neuron in
layer $\ell - 1$ is connected to every neuron in layer $\ell$. The weight
$w^{(\ell)}_{i,j}$ denotes the trainable parameter connecting the $j$-th neuron of
layer $\ell - 1$ to the $i$-th neuron of layer $\ell$. Bias terms are associated with
each neuron in layers $\ell \ge 1$. For a given layer $\ell$, the bias term
$b_i^{(\ell)}$ corresponds to the $i$-th neuron and is added to the weighted sum of
its inputs before the activation function is applied.

The activations of the output layer, $a_i^{(L)}$, constitute the network output and
are commonly denoted by $\hat{y}_i$, as indicated in Figure 1.

{% include figure.liquid 
   path=  "assets/img/2025-08-02-neural-nets-and-backprop/fig1.png" 
   class="img-fluid rounded z-depth-1 imgcenter" 
   zoomable=true 
   width="95%"  
   caption="Typical structure of a feed-forward neural network."
%}


Figure 2 illustrates the internal structure of a neuron, including the weighted
summation of its inputs, the addition of a bias term, and the subsequent application
of a (nonlinear) activation function.

{% include figure.liquid 
   path=  "assets/img/2025-08-02-neural-nets-and-backprop/fig2.png" 
   class="img-fluid rounded z-depth-1 imgcenter" 
   zoomable=true 
   width="70%"  
   caption="Representation of a typical neuron in a neural net."  
%}

The neuron receives as inputs the activations 
$$a^{(\ell-1)}_1, a^{(\ell-1)}_2, \ldots, a^{(\ell-1)}_{d_{\ell-1}}$$ 
from all neurons in
the preceding layer $\ell - 1$. Each input activation 
$$a^{(\ell-1)}_j$$
is multiplied by a corresponding trainable weight $w^{(\ell)}_{i,j}$, where the index $i$ denotes
the neuron in the current layer and $j$ denotes the neuron in the previous layer.
These multiplications are indicated by the multiplication symbols ($\times$) in the
diagram.

The weighted inputs are then summed, as represented by the summation node ($\sum$).
In addition, a bias term $b_i^{(\ell)}$, which is specific to the $i$-th neuron in
layer $\ell$, is added to this sum. The resulting quantity,

$$
z_i^{(\ell)} = \sum_{j=1}^{d_{\ell-1}} w^{(\ell)}_{i,j} \, a^{(\ell-1)}_j + b_i^{(\ell)},
$$

is referred to as the pre-activation of the neuron.

Finally, the pre-activation $z_i^{(\ell)}$ is passed through a nonlinear activation
function $\sigma(\cdot)$, producing the output (or activation)

$$
\begin{equation}
a_i^{(\ell)} = \sigma\!\left(z_i^{(\ell)}\right)  = 
\sigma \Bigg( \sum_{j=1}^{d_{\ell-1}} {w_{i,j}^{(\ell)} \cdot a_j^{(\ell-1)} } + b_i^{(\ell)} \Bigg)
\label{eq:activation}
\end{equation}
$$

This activation constitutes the output of the neuron and serves as an input to the
neurons in the subsequent layer $\ell + 1$.

The figure thus highlights the three fundamental steps performed by a neuron during
the forward pass: weighted summation of inputs, addition of a bias term, and
application of a nonlinear activation function.

In matrix form, Eq. \eqref{eq:activation} can be written as

$$
\begin{equation}
\vec a^{(\ell)}
= \sigma\left(\vec z^{(\ell)}\right)
= \sigma\left( \Wmatr^{(\ell)} \vec a^{(\ell-1)} + \vec b^{(\ell)} \right),
\label{eq:activation3}
\end{equation}
$$

where all vectors are interpreted as column vectors:

$$
\begin{align}
\vec a^{(\ell)}, \vec z^{(\ell)}, \vec b^{(\ell)} &\in \mathbb{R}^{d_\ell}, \\
\Wmatr^{(\ell)} &\in \mathbb{R}^{d_\ell \times d_{\ell-1}}, \\
\vec a^{(\ell-1)} &\in \mathbb{R}^{d_{\ell-1}}.
\label{eq:activation4}
\end{align}
$$

The activation function $\sigma(\cdot)$ is applied element-wise to its vector argument.

It is also possible to pass multiple input vectors through the network
simultaneously by stacking them into a matrix. Let

$$\vec{x}_1, \vec{x}_2, \ldots, \vec{x}_\batch$$ 

denote $\batch$ input examples, where $\batch$ is referred to as the batch size. These inputs are arranged
column-wise into the input matrix

$$
\begin{align}
\matr X
&= \big( \vec{x}_1 \ \vec{x}_2 \ \ldots \ \vec{x}_\batch \big), \\
\matr X &\in \mathbb{R}^{\din \times \batch}.
\label{eq:input-matrix}
\end{align}
$$

This procedure is commonly referred to as batching. A matrix containing multiple
input vectors is called a batch.

> In some implementations, input vectors are stacked row-wise, with each row representing one example. Here, we adopt the column-wise convention, which is consistent with the preceding vector notation and the matrix formulations used throughout.

For each input example $\vec{x}_i$, a corresponding activation vector
$\vec{a}_i^{(\ell)}$ is produced at layer $\ell$. These activations can be
collected into the activation matrix

$$
\matr A^{(\ell)}
= \big( \vec a_1^{(\ell)} \ \vec a_2^{(\ell)} \ \ldots \ \vec a_\batch^{(\ell)} \big)
\in \mathbb{R}^{d_\ell \times \batch}.
$$

Using matrix notation, the forward pass for a batch of inputs can be written as

$$
\begin{align}
\matr Z^{(\ell)} &=
\begin{pmatrix}
\vec b^{(\ell)} & \Wmatr^{(\ell)}
\end{pmatrix}
\begin{pmatrix}
\vec{1}^\top \\
\matr A^{(\ell-1)}
\end{pmatrix}, \\
\matr A^{(\ell)} &= \sigma\!\left( \matr Z^{(\ell)} \right),
\label{eq:input-matrix1}
\end{align}
$$

where $\vec{1} \in \mathbb{R}^{\batch}$ denotes a vector of ones.

Note that the inclusion of the bias vector into the weight matrix is a purely notational convenience. From a mathematical perspective, the bias term can equivalently be added as a separate vector after the weighted sum has been computed. By augmenting the input with a constant component equal to one and concatenating the bias vector to the weight matrix, the affine transformation can be written as a single matrix multiplication. Throughout this post, this augmented representation is used where it simplifies the notation, but it does not constitute an additional modeling assumption.

Using the augmented representation and  $\matr A^{(0)}= \matr X$, the affine transformation of the first hidden
layer can be written as

$$
\begin{equation}
\matr A^{(1)}
=
\sigma\!\left(
\begin{pmatrix}
\vec b^{(1)} & \Wmatr^{(1)}
\end{pmatrix}
\begin{pmatrix}
\vec{1}^\top \\
\matr X
\end{pmatrix}
\right).
\label{eq:input-matrix2}
\end{equation}
$$

Here, the augmented weight matrix

$$
\begin{pmatrix}
\vec b^{(1)} & \Wmatr^{(1)}
\end{pmatrix}
\in \mathbb{R}^{d_1 \times (\din + 1)}
$$

is formed by concatenating the bias vector $\vec b^{(1)} \in \mathbb{R}^{d_1}$ and
the weight matrix $\Wmatr^{(1)} \in \mathbb{R}^{d_1 \times \din}$, while the augmented
input matrix

$$
\begin{pmatrix}
\vec{1}^\top \\
\matr X
\end{pmatrix}
\in \mathbb{R}^{(\din + 1) \times \batch}
$$
contains a row of ones and the input batch $\matr X \in \mathbb{R}^{\din \times \batch}$. As a result, the matrix product is well defined and yields

$$
\matr A^{(1)} \in \mathbb{R}^{d_1 \times \batch}.
$$


## The Backpropagation Algorithm

To train the neural network, a suitable differentiable cost (sometimes objective) function $J(\Theta)$ is
required, where $\Theta$ denotes the set of all trainable parameters of the network,
including both the weight matrices and the bias vectors of all layers. Explicitly,
we write

$$
\Theta = \left\{ \Wmatr^{(1)}, \vec b^{(1)}, \Wmatr^{(2)}, \vec b^{(2)}, \ldots,
\Wmatr^{(L)}, \vec b^{(L)} \right\}.
$$

We denote the loss for a single ($n$-th) training example by
$\mathcal{L}(\vec y_n^*, \hat{\vec y_n})$.
A commonly used choice is the mean squared error (MSE) loss, which measures the
prediction error for a single training example. For an individual example $n$, the
loss is defined as

$$
\mathcal{L}_n
= \frac{1}{2}\left\| \vec{y}_n^* - \hat{\vec y}_n \right\|^2,
$$

where $\vec y_n^* \in \mathbb{R}^{d_L}$ denotes the true output vector of the $n$-th
example and $\hat{\vec y}_n = \vec a_n^{(L)} \in \mathbb{R}^{d_L}$ is the corresponding
predicted output of the network.

> **Note.**  
> The factor $\tfrac{1}{2}$ is included purely for convenience. When differentiating
> the squared error, it cancels the factor $2$ arising from the derivative of the
> square and thus simplifies the resulting gradient expressions. Importantly, this
> factor does not affect the location of the minimum of the cost function.

The cost function $J(\Theta)$ is obtained by aggregating the loss over a batch of
$\batch$ training examples. Using the mean squared error, the cost function is given
by

$$
J(\Theta)
= \frac{1}{\batch} \sum_{n=1}^{\batch}
\mathcal{L}_n
= \frac{1}{\batch} \sum_{n=1}^{\batch}
\frac{1}{2}\left\| \vec{y}_n^* - \hat{\vec y}_n \right\|^2.
\label{eq:mse}
$$


In Figure 3, the local structure of two consecutive layers in a feed-forward neural
network is illustrated in a form that is particularly useful for deriving the
backpropagation algorithm. The figure highlights a single neuron $i$ in layer $\ell$,
its pre-activation $z_i^{(\ell)}$, and its activation

$$
a_i^{(\ell)} = \sigma\left(z_i^{(\ell)}\right),
$$

as well as how this activation is propagated forward to all neurons in the subsequent layer $\ell + 1$.

Specifically, the activation $a_i^{(\ell)}$ serves as an input to each neuron in layer $\ell + 1$, where it is multiplied by the corresponding weights $w_{k,i}^{(\ell+1)}$, summed together with the other incoming weighted activations, and combined with the bias terms $b_k^{(\ell+1)}$ to form the pre-activations $z_k^{(\ell+1)}$. This explicit depiction makes clear how a single activation influences multiple downstream neurons and, conversely (as we will see below), how gradients computed at layer $\ell + 1$ will later be propagated backward through the same weighted connections to layer $\ell$.

{% include figure.liquid 
   path=  "assets/img/2025-08-02-neural-nets-and-backprop/fig3.png" 
   class="img-fluid rounded z-depth-1 imgcenter" 
   zoomable=true 
   width="70%"  
   caption="Zoom into the neural network."  
%}

Gradient descent can be used to minimize the cost function $J(\Theta)$. This
requires computing the partial derivatives of $J$ with respect to all trainable
parameters contained in $\Theta$. Due to the layered structure of a neural
network, these derivatives cannot be computed directly in a single step.
Figure 3 illustrates this dependency structure for a specific weight
$w_{i,j}^{(\ell)}$.

At this point, it is convenient to distinguish between the **loss**
$\mathcal{L}(\vec y^*, \hat{\vec y})$ of a single training example and the
**cost function** $J(\Theta)$, which aggregates the loss over a batch of
$\batch$ examples. The derivation of backpropagation is carried out at the
single-sample level, since differentiation is a linear operation. In
particular, if

$$
J(\Theta) = \frac{1}{\batch} \sum_{n=1}^{\batch} \mathcal{L}_n(\Theta),
$$

then the gradient of the cost function is given by

$$
\frac{\partial J}{\partial \Theta}
= \frac{1}{\batch} \sum_{n=1}^{\batch}
\frac{\partial \mathcal{L}_n}{\partial \Theta}.
$$

Thus, the gradient of $J$ is simply the average of the gradients of the
individual losses. For this reason, we first derive the gradients of the
loss for a single training example and later extend the result to a batch
by averaging.

Assume that we want to compute the partial derivative of the loss function
with respect to the weight $w_{i,j}^{(\ell)}$. Since this weight influences
the loss only indirectly through the pre-activation $z_i^{(\ell)}$ of neuron
$i$ in layer $\ell$, the chain rule yields

$$
\begin{align}
\frac{\partial \mathcal{L}}{\partial w_{i,j}^{(\ell)}}
&= \frac{\partial \mathcal{L}}{\partial z_i^{(\ell)}}
   \frac{\partial z_i^{(\ell)}}{\partial w_{i,j}^{(\ell)}}.
\label{eq:partial1}
\end{align}
$$


From the definition of the pre-activation

$$
z_i^{(\ell)} = \sum_{j} w_{i,j}^{(\ell)} a_j^{(\ell-1)} + b_i^{(\ell)},
$$

it follows immediately that

$$
\begin{align}
\frac{\partial z_i^{(\ell)}}{\partial w_{i,j}^{(\ell)}}
= a_j^{(\ell-1)}.
\label{eq:partial2}
\end{align}
$$

Substituting this result into Eq. \eqref{eq:partial1} yields

$$
\begin{align}
\frac{\partial \mathcal{L}}{\partial w_{i,j}^{(\ell)}}
= \frac{\partial \mathcal{L}}{\partial z_i^{(\ell)}} \, a_j^{(\ell-1)}.
\label{eq:partial3}
\end{align}
$$

So far, we have considered the partial derivative of the loss with respect to the
weights $w_{i,j}^{(\ell)}$. An analogous and even simpler expression is obtained
for the bias parameters $b_i^{(\ell)}$.

Since the bias enters the pre-activation additively, we have

$$
\frac{\partial z_i^{(\ell)}}{\partial b_i^{(\ell)}} = 1.
$$

Therefore, by the chain rule,

$$
\begin{align}
\frac{\partial \mathcal{L}}{\partial b_i^{(\ell)}}
&= \frac{\partial \mathcal{L}}{\partial z_i^{(\ell)}}
   \frac{\partial z_i^{(\ell)}}{\partial b_i^{(\ell)}} \\
&= \frac{\partial \mathcal{L}}{\partial z_i^{(\ell)}}.
\end{align}
$$


In summary, we have:

$$
\begin{align}
\frac{\partial \mathcal{L}}{\partial w_{i,j}^{(\ell)}}
&= \frac{\partial \mathcal{L}}{\partial z_i^{(\ell)}} \, a_j^{(\ell-1)}, \\
\frac{\partial \mathcal{L}}{\partial b_i^{(\ell)}}
&= \frac{\partial \mathcal{L}}{\partial z_i^{(\ell)}}.
\end{align}
$$

The remaining partial derivative $\partial \mathcal{L} / \partial z_i^{(\ell)}$ cannot be
evaluated directly. However, it can be expressed recursively by applying the chain
rule, which forms the basis of the backpropagation algorithm.

### Interlude: The Chain Rule and Nested Dependencies

Before deriving the backpropagation algorithm, it is helpful to briefly recall the
chain rule for derivatives, which plays a central role in computing gradients in
neural networks. In particular, neural networks are composed of nested functions,
so changes in a parameter typically affect the output only indirectly through a
sequence of intermediate variables.

Consider a function $z = f(x, y)$ that depends on two intermediate variables
$x$ and $y$, which in turn both depend on a common variable $t$, i.e.

$$
x = g(t), \qquad y = h(t).
$$

In this case, the total derivative of $z$ with respect to $t$ is given by the
chain rule as

$$
\begin{align}
z &= f(x, y), \quad x = g(t), \quad y = h(t), \\
\frac{d z}{d t}
&= \frac{\partial z}{\partial x} \frac{d x}{d t}
 + \frac{\partial z}{\partial y} \frac{d y}{d t}.
\label{eq:chainrule1}
\end{align}
$$

This expression shows that the influence of $t$ on $z$ is obtained by summing all
paths through which $t$ affects the intermediate variables $x$ and $y$.

Consider the composite function

$$
z = \sin(x^2 + y^2), \qquad x = e^t, \qquad y = t^2.
$$

Since $z$ depends on $t$ only through the intermediate variables $x$ and $y$, the
chain rule gives

$$
\begin{align}
\frac{\partial z}{\partial x} &= 2x \cos(x^2 + y^2), \\
\frac{\partial z}{\partial y} &= 2y \cos(x^2 + y^2), \\
\frac{d x}{d t} &= e^t, \\
\frac{d y}{d t} &= 2t.
\end{align}
$$

Therefore, the total derivative of $z$ with respect to $t$ is

$$
\begin{align}
\frac{d z}{d t}
&= 2x   \cos(x^2 + y^2)\,\frac{d x}{d t}
   + 2y  \cos(x^2 + y^2)\,\frac{d y}{d t} \\
&= 2x  \cos(x^2 + y^2)\,e^t
   + 2y   \cos(x^2 + y^2)\,2t \\
&= 2\cos(x^2 + y^2)\left(x\,e^t + 2yt\right) \\
&= 2\cos\left(e^{2t} + t^4\right)\left(e^{2t} + 2t^3\right).
\end{align}
$$


Using direct differentiation, we obtain

$$
\begin{align}
z &= \sin(e^{2t} + t^4), \\
\frac{d z}{d t}
&= \cos(e^{2t} + t^4)\left(2 e^{2t} + 4 t^3\right) \\
&= 2\cos(e^{2t} + t^4)\left(e^{2t} + 2 t^3\right),
\end{align}
$$

which is identical to the result obtained via the chain rule.

Similarly, an analogous form of the chain rule applies when the intermediate
variables are vector-valued. Let $\vec t$ be a vector and let
$z = f(\vec x)$ with $\vec x = g(\vec t)$. Then the partial derivative of $z$
with respect to the $i$-th component of $\vec t$ is given by

$$
\begin{align}
z &= f(\vec{x}), \qquad \vec{x} = g(\vec{t}), \\
\frac{\partial z}{\partial t_i}
&= \frac{\partial z}{\partial x_1} \frac{\partial x_1}{\partial t_i}
 + \frac{\partial z}{\partial x_2} \frac{\partial x_2}{\partial t_i}
 + \cdots \\
&= \sum_{j} \frac{\partial z}{\partial x_j}
              \frac{\partial x_j}{\partial t_i}.
\label{eq:chainrule2}
\end{align}
$$

This expression shows that the influence of a single component $t_i$ on $z$ is
obtained by summing over all paths through which $t_i$ affects the intermediate
variables $\vec x$.

### Backpropagation via the Chain Rule

We can now use the chain rule to compute the partial derivative
$\partial \mathcal{L} / \partial z_i^{(\ell)}$ in Eq. \eqref{eq:partial3} in a recursive
manner. As illustrated in Figure 3, the pre-activations $z_k^{(\ell+1)}$ of the
next layer can be regarded as functions of the pre-activations of the current
layer, in particular of $z_i^{(\ell)}$, i.e.,
$z_k^{(\ell+1)} = z_k^{(\ell+1)}(\ldots, z_i^{(\ell)}, \ldots)$. Consequently, the
loss function depends on $z_i^{(\ell)}$ only indirectly through its influence on
all downstream pre-activations $z_k^{(\ell+1)}$. Formally, one may therefore view
the loss function as a composite function of the form
$\mathcal{L} = \mathcal{L}\big(\ldots, z_k^{(\ell+1)}(\ldots, z_i^{(\ell)}, \ldots), \ldots\big)$, which
naturally leads to a recursive application of the chain rule.


Applying the chain rule, we obtain

$$
\begin{align}
\frac{\partial \mathcal{L}}{\partial z_i^{(\ell)}}
&= \frac{\partial \mathcal{L}}{\partial z_1^{(\ell+1)}}
   \frac{\partial z_1^{(\ell+1)}}{\partial z_i^{(\ell)}}
 + \frac{\partial \mathcal{L}}{\partial z_2^{(\ell+1)}}
   \frac{\partial z_2^{(\ell+1)}}{\partial z_i^{(\ell)}}
 + \cdots \\
&= \sum_{k=1}^{d_{\ell+1}}
   \frac{\partial \mathcal{L}}{\partial z_k^{(\ell+1)}}
   \frac{\partial z_k^{(\ell+1)}}{\partial z_i^{(\ell)}}.
\label{eq:chainrule3}
\end{align}
$$

From the definition

$$
z_k^{(\ell+1)} = \sum_j w^{(\ell+1)}_{k,j} a_j^{(\ell)} + b_k^{(\ell+1)},
\qquad
a_j^{(\ell)} = \sigma\!\left(z_j^{(\ell)}\right),
$$

it follows that

$$
\frac{\partial z_k^{(\ell+1)}}{\partial z_i^{(\ell)}}
= w^{(\ell+1)}_{k,i} \, \sigma'\!\left(z_i^{(\ell)}\right),
$$

where $\sigma'(z)$ denotes the derivative of the activation function
$\sigma(\cdot)$ with respect to its argument.

Substituting this result into Eq. \eqref{eq:chainrule3} yields

$$
\begin{align}
\frac{\partial \mathcal{L}}{\partial z_i^{(\ell)}}
= \sigma'\!\left(z_i^{(\ell)}\right)
  \sum_{k=1}^{d_{\ell+1}}
  w^{(\ell+1)}_{k,i}
  \frac{\partial \mathcal{L}}{\partial z_k^{(\ell+1)}}.
\label{eq:backprop-recursion}
\end{align}
$$


Note the recursive structure of Eq. \eqref{eq:backprop-recursion}. For notational
convenience, we define the error signal (also called the delta term) at neuron $i$
in layer $\ell$ as

$$
\delta_i^{(\ell)} := \frac{\partial \mathcal{L}}{\partial z_i^{(\ell)}}.
$$

With this definition, Eq. \eqref{eq:backprop-recursion} can be written in the
recursive form

$$
\begin{align}
\delta_i^{(\ell)}
&= \sigma'\!\left(z_i^{(\ell)}\right)
   \sum_{k=1}^{d_{\ell+1}}
   w^{(\ell+1)}_{k,i}\, \delta_k^{(\ell+1)}.
\label{eq:chainrule4}
\end{align}
$$





Equation \eqref{eq:chainrule4} can be written in a more compact vector form.
To this end, we introduce the error vectors

$$
\begin{align}
\vec{\delta}^{(\ell)} &\in \mathbb{R}^{d_\ell }, \\
\vec{\delta}^{(\ell+1)} &\in \mathbb{R}^{d_{\ell+1} },
\end{align}
$$

and the weight matrix

$$
\begin{align}
\Wmatr^{(\ell+1)} \in \mathbb{R}^{d_{\ell+1} \times d_\ell}.
\label{eq:chainrule6}
\end{align}
$$

In Eq.\eqref{eq:chainrule4}, the summation is carried out over the index
$k$, which corresponds to the first index of the weight
$w_{k,i}^{(\ell+1)}$. This implies that, in matrix notation, the transpose of
$\Wmatr^{(\ell+1)}$ must be used. Indeed, we have

$$
\begin{align}
(\Wmatr^{(\ell+1)})^\top
&\in \mathbb{R}^{d_\ell \times d_{\ell+1}}, \\
(\Wmatr^{(\ell+1)})^\top \vec{\delta}^{(\ell+1)}
&\in \mathbb{R}^{d_\ell }.
\label{eq:chainrule7}
\end{align}
$$





To see how the transpose arises explicitly, write the weight matrix row-wise as

$$
\Wmatr^{(\ell+1)}
=
\begin{pmatrix}
(\vec w^{(\ell+1)}_{1})^\top \\
(\vec w^{(\ell+1)}_{2})^\top \\
\vdots \\
(\vec w^{(\ell+1)}_{d_{\ell+1}})^\top
\end{pmatrix},
\qquad
\vec w^{(\ell+1)}_{k} \in \mathbb{R}^{d_\ell},
$$

i.e., the $k$-th row contains the incoming weights of neuron $k$ in layer $\ell+1$.
Taking the transpose yields

$$
(\Wmatr^{(\ell+1)})^\top
=
\begin{pmatrix}
\vec w^{(\ell+1)}_{1} &
\vec w^{(\ell+1)}_{2} &
\cdots &
\vec w^{(\ell+1)}_{d_{\ell+1}}
\end{pmatrix}.
$$

Now let

$$
\vec\delta^{(\ell+1)}
=
\begin{pmatrix}
\delta^{(\ell+1)}_{1}\\
\delta^{(\ell+1)}_{2}\\
\vdots\\
\delta^{(\ell+1)}_{d_{\ell+1}}
\end{pmatrix}.
$$

Then the matrix-vector product can be interpreted as a weighted sum of the
(transposed) row vectors:

$$
(\Wmatr^{(\ell+1)})^\top \vec\delta^{(\ell+1)}
=
\sum_{k=1}^{d_{\ell+1}} \vec w^{(\ell+1)}_{k}\,\delta^{(\ell+1)}_{k}.
$$

Looking at the $i$-th component of this vector gives

$$
\big[(\Wmatr^{(\ell+1)})^\top \vec\delta^{(\ell+1)}\big]_i
=
\sum_{k=1}^{d_{\ell+1}} w^{(\ell+1)}_{k,i}\,\delta^{(\ell+1)}_{k},
$$

which is exactly the summation term appearing in Eq. \eqref{eq:chainrule4}.







Using this notation and writing the derivative of the activation function
element-wise, the backpropagation recursion can be expressed as

$$
\begin{align}
\vec{\delta}^{(\ell)}
:= \frac{\partial \mathcal{L}}{\partial \vec z^{(\ell)}}
= \Big( (\Wmatr^{(\ell+1)})^\top \vec{\delta}^{(\ell+1)} \Big)
  \otimes \sigma'\!\left(\vec z^{(\ell)}\right),
\label{eq:chainrule8}
\end{align}
$$

where $\otimes$ denotes the Hadamard (element-wise) product and the derivative
$\sigma'(\cdot)$ is applied component-wise to the vector $\vec z^{(\ell)}$.





**TODO: Continue here!**













Remember Eq. \eqref{eq:partial3} which was:

<aside><p> \footnote{Note that we cannot directly update the weights of a layer; we have to first compute $\delta^\ell$ for the remaining layers. Otherwise, the adjusted weights change $\delta^\ell$ of previous layers.}</p> </aside>

$$
\begin{align}
\frac{\partial}{\partial w_{ij}^\ell} E 
=  \frac{\partial E}{\partial z_i^\ell} a_j^{\ell-1} = \delta_i^\ell a_j^{\ell-1}
\label{eq:finalbackprop}
\end{align}
$$

Since \textcolor[rgb]{1,0,0}{(Note that bias weights are not included...)}

$$
\begin{align}
\Wmatr^\ell, \frac{\partial E}{\partial W^\ell} \in \mathbb{R}^{d_\ell \times d_{\ell-1}} \label{eq:finalbackprop1}\\
\vec a^{\ell-1} \in \mathbb{R}^{d_{\ell-1} },
\end{align}
$$

if we apply \eqref{eq:chainrule8} to \eqref{eq:finalbackprop} we have to transpose vector $a^{\ell-1}$ in order to meet the dimensions of $\frac{\partial E}{\partial \Wmatr^\ell}$ in Eq. \eqref{eq:finalbackprop1}:

$$
\begin{align}
\frac{\partial E}{\partial \Wmatr^\ell} =\vec \delta^\ell \cdot (\vec a^{\ell-1})^\top \in \mathbb{R}^{d_\ell } \cdot \mathbb{R}^{1 \times d_{\ell-1}}= \mathbb{R}^{d_\ell \times d_{\ell-1}}
\label{eq:finalbackprop2}
\end{align}
$$

As before, we can put a batch of training examples in a matrix $X\in \mathbb{R}^{n \times \batch}$ through the network. In every layer we collect an activation matrix $A^\ell$ until we reach the final output $A^L$. If we want to perform a batch update of the weights we have to sum up the gradients in \eqref{eq:finalbackprop2} for every example. Similar to before, we create a matrix $\Delta^\ell$ which contains the single column vectors $\delta^\ell$ for every training example. This can be done with:

**TODO:** Describe, how to compute $$\Delta^{\ell-1}$$, since this is what we will compute in the backprop method and then return to the previous layer.

$$
\begin{align}
 Z^\ell \in \mathbb{R}^{d_\ell\times \batch}\\
(\Wmatr^{\ell+1})^\top  \in \mathbb{R}^{d_{\ell} \times d_{\ell+1}}\\
\Delta^{\ell+1} \in \mathbb{R}^{d_{\ell+1}\times \batch}\\
\Delta^\ell = \big( \Wmatr^{\ell+1}\big)^\top \cdot \Delta^{\ell+1} \otimes \sigma'(Z^\ell) \\
\Delta^\ell \in \mathbb{R}^{d_{\ell} \times d_{\ell+1}} \cdot \mathbb{R}^{d_{\ell+1}\times \batch} = \mathbb{R}^{d_{\ell}\times \batch}\\
\label{eq:matrixBackprop}
\end{align}
$$ 

However, the derivative $\frac{\partial E}{\partial W^\ell}$ in \eqref{eq:finalbackprop2} should have the same dimensions as before, but sum up the gradients for all examples:

$$
\begin{align}
\frac{\partial E}{\partial \Wmatr^\ell} &=\sum_{k=1}^{\batch} \vec \delta_k^\ell \cdot (\vec a_k^{\ell-1})^\top\\
&= \Delta^\ell \cdot \big( A^{\ell-1}\big)^\top \\
\Delta^\ell \cdot \big( A^{\ell-1}\big)^\top \in \mathbb{R}^{d_{\ell}\times \batch} \cdot \mathbb{R}^{\batch \times d_{\ell-1}} &= \mathbb{R}^{d_{\ell} \times d_{\ell-1}}
\label{eq:finalbackprop3}
\end{align}
$$


**TODO: Moved this from an earlier paragraph to here:**


The recursive relation in Eq. \eqref{eq:chainrule4} and Eq. \eqref{eq:chainrule8} expresses the error signal in
layer $\ell$ in terms of the error signals in the subsequent layer $\ell+1$.
Consequently, the recursion must be initialized at the output layer $\ell = L$ and
then evaluated backwards through the network. This backward propagation of error
signals gives rise to the name *backpropagation*.

We therefore begin by computing the error signal for the output layer
$\ell = L$. For the mean squared error (MSE) loss, the error signal of the $i$-th
output neuron is given by

$$
\begin{align}
\delta_i^{(L)}
&:= \frac{\partial \mathcal{L}}{\partial z_i^{(L)}} \\
&= \frac{\partial}{\partial z_i^{(L)}}
   \left[ \frac{1}{2} \big(y_i^* - a_i^{(L)}\big)^2 \right] \\
&= \frac{\partial}{\partial z_i^{(L)}}
   \left[ \frac{1}{2} \big(y_i^* - \sigma(z_i^{(L)})\big)^2 \right] \\
&= -\big(y_i^* - \sigma(z_i^{(L)})\big)\,\sigma'\!\left(z_i^{(L)}\right) \\
&= \big(a_i^{(L)} - y_i^*\big)\,\sigma'\!\left(z_i^{(L)}\right).
\end{align}
$$

> **Remark (Cross-entropy loss).**  
> For the cross-entropy loss in combination with a sigmoid activation function in
> the output layer, the expression for the output-layer error signal simplifies
> considerably. In this case, the derivative of the activation function cancels
> with a corresponding term arising from the derivative of the loss, yielding
> $$\delta_i^{(L)} = a_i^{(L)} - y_i^*.$$
> This simplification is one of the main reasons why the cross-entropy loss is
> commonly preferred over the mean squared error for classification tasks.
> This case is discussed separately in Section **TODO**.

In vector form, this can be written as

$$
\begin{align}
\boldsymbol{\delta}^{(L)}
&= \big(\vec a^{(L)} - \vec y^{*}\big)
  \otimes \sigma'\!\left(\vec z^{(L)}\right) \\
&= \big(\vec \yhat  - \vec y^{*}\big)
  \otimes \sigma'\!\left(\vec z^{(L)}\right)
\label{eq:chainrule5}
\end{align}
$$

where $\otimes$ denotes the Hadamard (element-wise) product.



## Putting Everything Together
1. Forward pass (what to remember?)
2. Compute Loss
3. Compute $\Delta$ for the loss
4. backprop
5. ...

## Practical Considerations
- gradient checking
- SGD vs. mini batches vs. full-batches
- initialization of weights
- local minima

### Weight Initialization