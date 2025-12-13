---
layout: post
title: "Yet another Neural Networks Introduction: Feed Forward Networks and the Backpropagation Algorithm"
modified: 2025-08-01T09:00:51+01:00
categories: [Math, Neural Nets]
description: "A few notes on the backprop algorithm"
tags: []
thumbnail: 
giscus_comments: true
toc:
  beginning: true
share: true
date: 2025-08-01T09:00:51+01:00
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

Each layer $\ell$ consists of $d_\ell$ so-called neurons, where
$\vec{x} \in \mathbb{R}^{\din}$ denotes the input vector and $d_L$
denotes the output dimension of the network. In Figure 1, neurons are depicted
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
\sigma \Bigg( \sum_{j=1}^{d_{(\ell-1)}} {w_{i,j}^{(\ell)} \cdot a_j^{(\ell-1)} + b_i^{(\ell)}} \Bigg)
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

where

$$
\begin{align}
\vec a^{(\ell)}, \vec z^{(\ell)}, \vec b^{(\ell)} &\in \mathbb{R}^{d_\ell}, \\
\Wmatr^{(\ell)} &\in \mathbb{R}^{d_\ell \times d_{\ell-1}}, \\
\vec a^{(\ell-1)} &\in \mathbb{R}^{d_{\ell-1}}.
\label{eq:activation4}
\end{align}
$$

**TODO:** Continue from here....
It is also possible to pass a matrix consisting of $M$ examples (input vectors) $\vec{x}_i$ through the network, where

$$
\begin{eqnarray}
X = \big( \vec{x}_1\  \vec{x}_2\  \ldots\  \vec{x}_M \big) \\
X \in \mathbb{R}^{\din \times M}.
\label{eq:input-matrix}
\end{eqnarray}
$$
This is commonly referred to as batching a set of individual samples. A matrix holding a set of sample vectors is called a batch.

**TODO**: Add a note that it is also common, to stack the input vectors vertically, each row representing an example.

For each example a separate activation vector $\vec{a}_i^\ell$ will be generated, which can be placed in a matrix:

$$
\begin{eqnarray}
Z^\ell =  \begin{pmatrix} b^\ell & \Wmatr^{\ell}  \end{pmatrix} \begin{pmatrix} \vec{1}^\top \\ A^{\ell-1}  \end{pmatrix}\\
A^\ell = \sigma(Z^\ell)
\label{eq:input-matrix1}
\end{eqnarray}
$$

Note, that the bias-vector is included into the weight matrix. For example, with $A^0=X$ we get:

$$
\begin{eqnarray}
A^1 = \sigma \Bigg( \begin{pmatrix} b^1 & \Wmatr^1  \end{pmatrix} \begin{pmatrix} \vec{1}^\top \\ X  \end{pmatrix} \Bigg) 
\in \mathbb{R}^{d_1 \times (\din+1)} \cdot \mathbb{R}^{(\din+1) \times M} = \mathbb{R}^{d_1 \times M}
\label{eq:input-matrix2}
\end{eqnarray}
$$

## The Backpropagation Algorithm
In order to train the model a suitable, differentiable, error function $E(\mathbb{\Wmatr})$ is required, where $\mathbb{\Wmatr}$ is set of all weights (including the bias weights) of the neural network. A popular function is the mean-squared error, so that:

$$
\begin{eqnarray}
E = \frac{1}{M} \sum_{m=1}^M { \left\| \vec{y}_m^* - \vec{o}_m \right\|^2 }\\
\vec{y}_m^*, \vec{o}_m \in \mathbb{R}^{P \times 1}
\label{eq:mse}
\end{eqnarray}
$$

where $y_m^*$ is the true output vector and $\vec{o}_m=\vec{a}^L$ is the predicted output vector with in total $P$ outputs.

{% include figure.liquid 
   path=  "assets/img/2025-08-02-neural-nets-and-backprop/fig3.png" 
   class="img-fluid rounded z-depth-1 imgcenter" 
   zoomable=true 
   width="70%"  
   caption="Zoom into the neural network."  
%}

One can use a gradient descent approach in order to minimize the error $E$. This requires computing the partial derivatives of $E$ with respect to all weights in $\mathbb{W}$. Due to the layered structure of the neural network, this is not trivial. Fig. 3 illustrates the problem for a specific weight $w_{ij}^\ell$. Assume we want to compute the partial derivate for this weight:

$$
\begin{eqnarray}
\frac{\partial}{\partial w_{ij}^\ell} E = \frac{\partial E}{\partial z_i^\ell} \frac{\partial z_i^\ell}{\partial w_{ij}^\ell} \label{eq:partial1}
\end{eqnarray}
$$

Since

$$
\begin{eqnarray}
\frac{\partial z_i^\ell}{\partial w_{ij}^\ell} = a_j^{\ell-1},\label{eq:partial2}
\end{eqnarray}
$$

we can simplify \eqref{eq:partial1} to

$$
\begin{eqnarray}
\frac{\partial}{\partial w_{ij}^\ell} E 
=  \frac{\partial E}{\partial z_i^\ell} a_j^{\ell-1}
\label{eq:partial3}
\end{eqnarray}
$$
The remaining partial derivative cannot be evaluated that easily. However, we can derive a recursive expression using the chain rule for partial derivatives. Remember the following rule:

$$
\begin{eqnarray}
z=f(x,y), \ x=g(t), \ y=h(t)\\
\frac{d z}{d t}
=  \frac{\partial z}{\partial x} \frac{d x}{d t}
+  \frac{\partial z}{\partial y} \frac{d y}{d t}
\label{eq:cahinrule1}
\end{eqnarray}
$$

Consider the following example:

$$
\begin{align}
z&=\mbox{sin}(x^2+y^2), \ x=e^t, \ y=t^2\\
\frac{\partial z}{\partial x} &= 2x\cdot \mbox{cos}(x^2+y^2)\\
\frac{\partial z}{\partial y} &= 2y\cdot \mbox{cos}(x^2+y^2)\\
\frac{d x}{d t} &= e^t\\
\frac{d y}{d t} &= 2t\\
\frac{d z}{d t} &= 2x\cdot \mbox{cos}(x^2+y^2) e^t 
+ 2y\cdot \mbox{cos}(x^2+y^2) 2t\\
&= 2\mbox{cos}(x^2+y^2)(x\cdot e^t + 2yt)\\
&= 2\mbox{cos}(e^{2t}+t^4) (e^{2t} + 2t^3)
\end{align}
$$

Using the direct method we retrieve:

$$
\begin{align}
z&=\mbox{sin}(e^{2t}+t^4)\\
\frac{d z}{d t} 
&= \mbox{cos}(e^{2t}+t^4) (2 e^{2t} + 4t^3)
\end{align}
$$

Similarly, the following applies, assuming that $\vec{t}$ is a vector rather than a scalar and $\vec{x}$ is a vector as well:

$$
\begin{align}
z=f(\vec{x}), \ x=g(\vec{t})\\
\frac{\partial z}{\partial t_i}
&=  \frac{\partial z}{\partial x_1} \frac{\partial x_1}{\partial t_i}
+ \frac{\partial z}{\partial x_2} \frac{\partial x_2}{\partial t_i}+ \cdots\\
&= \sum_{j} {\frac{\partial z}{\partial x_j} \frac{\partial x_j}{\partial t_i}}
\label{eq:cahinrule2}
\end{align}
$$

We can use this relation, to compute the partial derivative $\frac{\partial E}{\partial z_i^\ell}$ in \eqref{eq:partial3} in a recursive manner.
Note that in Fig. 3 the terms $z_k^{\ell+1}$ can be expressed as functions $z_k^{\ell+1}(\ldots, z_i^\ell, \ldots)$.
Assuming that $z_k^{\ell+1}$ were free parameters such as the weights in $\mathbb{W}$, then one could also imagine the error function as function of these parameters, i.e., $E=E\big(\ldots,z_k^{\ell+1}(\ldots, z_i^\ell, \ldots)\ldots\big)$.

Let us now compute the partial derivative $\frac{\partial E}{\partial z_i^\ell}$ from \eqref{eq:partial3} (see Fig. 3):

$$
\begin{align}
\frac{\partial E}{\partial z_i^\ell} 
&= \frac{\partial E}{\partial z_1^{\ell+1}} \frac{\partial z_1^{\ell+1}}{\partial z_i^\ell} 
+ \frac{\partial E}{\partial z_2^{\ell+1}} \frac{\partial z_2^{\ell+1}}{\partial z_i^\ell} + \cdots \\
&= \sum\limits_k^{d_{\ell+1}} {\frac{\partial E}{\partial z_k^{\ell+1}} \frac{\partial z_k^{\ell+1}}{\partial z_i^\ell}}\\
&= \sum\limits_k^{d_{\ell+1}} \frac{\partial E}{\partial z_k^{\ell+1}} \sigma'(z_i^\ell) w_{ki}^{\ell+1},
\label{eq:cahinrule3}
\end{align}
$$

where $\sigma'$ is the outer derivative of the activation $\sigma$. Note the recursive structure of \eqref{eq:cahinrule3} which can be re-written as:

$$
\begin{eqnarray}
\delta_i^\ell &= \frac{\partial E}{\partial z_i^\ell}\\
\delta_i^\ell &= \sum\limits_k^{d_{\ell+1}} \delta_k^{\ell+1}  \sigma'(z_i^\ell) w_{ki}^{\ell+1}
\label{eq:cahinrule4}
\end{eqnarray}
$$

For the output-layer $\ell=L$ one typically receives the following expression for $\delta_i^L$ (Cross-entropy loss should deliver the same results with $\sigma=logsig$): 

$$
\begin{align}
\delta_i^L &= \frac{\partial E}{\partial z_i^L} \\
&= \frac{\partial}{\partial z_i^L} {\frac{1}{2} (y_i^* - a_i^L)^2}\\
&= \frac{\partial}{\partial z_i^L} {\frac{1}{2} \big(y_i^* - \sigma(z_i^L)\big)^2}\\
&= \big(y_i^* - \sigma(z_i^L)\big) \frac{\partial}{\partial z_i^L} {\big(y_i^* - \sigma(z_i^L)\big)}\\
&= -\big(y_i^* - \sigma(z_i^L)\big) \sigma'(z_i^L) \\
&= (a_i^L - y_i^*)\sigma'(z_i^L) \\
\delta^L &= (\vec{a}^L- \vec{y}^*) \otimes \sigma'(\vec{z}^L),
\label{eq:cahinrule5}
\end{align}
$$

where the second row already shows the vector representation and "$\otimes$" represents the hadamard product.
Also \eqref{eq:cahinrule4} can be written in the more compact vector form with:

$$
\begin{eqnarray}
\vec\delta^\ell &\in \mathbb{R}^{d_\ell \times 1}\\
\vec\delta^{\ell+1} &\in \mathbb{R}^{d_{\ell+1} \times 1}\\
\Wmatr^{\ell+1} & \in \mathbb{R}^{d_{\ell+1} \times d_{\ell}}
\label{eq:cahinrule6}
\end{eqnarray}
$$

Note, that in \eqref{eq:cahinrule4} we sum over the first index of $w_{ki}^{\ell+1}$. This means that we have to compute the transpose of $\Wmatr^{\ell+1}$, which then delivers:

$$
\begin{eqnarray}
(\Wmatr^{\ell+1})^\top & \in \mathbb{R}^{d_{\ell} \times d_{\ell+1}} \\
(\Wmatr^{\ell+1})^\top \cdot \vec\delta^{\ell+1} &\in \mathbb{R}^{d_{\ell} \times d_{\ell+1}} \cdot \mathbb{R}^{d_{\ell+1} \times 1} = \mathbb{R}^{d_{\ell} \times 1}
\label{eq:cahinrule7}
\end{eqnarray}
$$

Finally, we get -- with vector $z^\ell$:<d-footnote>Using the denominator layout convention.</d-footnote>

$$
\begin{eqnarray}
\delta^\ell = \frac{\partial E}{\partial \vec z^\ell}
= (\Wmatr^{\ell+1})^\top \cdot \delta^{\ell+1} \otimes \sigma'(z_i^\ell)
\label{eq:cahinrule8}
\end{eqnarray}
$$

Remember Eq. \eqref{eq:partial3} which was:

<aside><p> \footnote{Note that we cannot directly update the weights of a layer; we have to first compute $\delta^\ell$ for the remaining layers. Otherwise, the adjusted weights change $\delta^\ell$ of previous layers.}</p> </aside>

$$
\begin{eqnarray}
\frac{\partial}{\partial w_{ij}^\ell} E 
=  \frac{\partial E}{\partial z_i^\ell} a_j^{\ell-1} = \delta_i^\ell a_j^{\ell-1}
\label{eq:finalbackprop}
\end{eqnarray}
$$

Since \textcolor[rgb]{1,0,0}{(Note that bias weights are not included...)}

$$
\begin{eqnarray}
\Wmatr^\ell, \frac{\partial E}{\partial W^\ell} \in \mathbb{R}^{d_\ell \times d_{\ell-1}} \label{eq:finalbackprop1}\\
\vec a^{\ell-1} \in \mathbb{R}^{d_{\ell-1} \times 1},
\end{eqnarray}
$$

if we apply \eqref{eq:cahinrule8} to \eqref{eq:finalbackprop} we have to transpose vector $a^{\ell-1}$ in order to meet the dimensions of $\frac{\partial E}{\partial \Wmatr^\ell}$ in Eq. \eqref{eq:finalbackprop1}:

$$
\begin{eqnarray}
\frac{\partial E}{\partial \Wmatr^\ell} =\vec \delta^\ell \cdot (\vec a^{\ell-1})^\top \in \mathbb{R}^{d_\ell \times 1} \cdot \mathbb{R}^{1 \times d_{\ell-1}}= \mathbb{R}^{d_\ell \times d_{\ell-1}}
\label{eq:finalbackprop2}
\end{eqnarray}
$$

As before, we can put a batch of training examples in a matrix $X\in \mathbb{R}^{n \times M}$ through the network. In every layer we collect an activation matrix $A^\ell$ until we reach the final output $A^L$. If we want to perform a batch update of the weights we have to sum up the gradients in \eqref{eq:finalbackprop2} for every example. Similar to before, we create a matrix $\Delta^\ell$ which contains the single column vectors $\delta^\ell$ for every training example. This can be done with:

**TODO:** Describe, how to compute $$\Delta^{\ell-1}$$, since this is what we will compute in the backprop method and then return to the previous layer.

$$
\begin{eqnarray}
 Z^\ell \in \mathbb{R}^{d_\ell\times M}\\
(\Wmatr^{\ell+1})^\top  \in \mathbb{R}^{d_{\ell} \times d_{\ell+1}}\\
\Delta^{\ell+1} \in \mathbb{R}^{d_{\ell+1}\times M}\\
\Delta^\ell = \big( \Wmatr^{\ell+1}\big)^\top \cdot \Delta^{\ell+1} \otimes \sigma'(Z^\ell) \\
\Delta^\ell \in \mathbb{R}^{d_{\ell} \times d_{\ell+1}} \cdot \mathbb{R}^{d_{\ell+1}\times M} = \mathbb{R}^{d_{\ell}\times M}\\
\label{eq:matrixBackprop}
\end{eqnarray}
$$ 

However, the derivative $\frac{\partial E}{\partial W^\ell}$ in \eqref{eq:finalbackprop2} should have the same dimensions as before, but sum up the gradients for all examples:

$$
\begin{eqnarray}
\frac{\partial E}{\partial \Wmatr^\ell} &=\sum_{k=1}^{M} \vec \delta_k^\ell \cdot (\vec a_k^{\ell-1})^\top\\
&= \Delta^\ell \cdot \big( A^{\ell-1}\big)^\top \\
\Delta^\ell \cdot \big( A^{\ell-1}\big)^\top \in \mathbb{R}^{d_{\ell}\times M} \cdot \mathbb{R}^{M \times d_{\ell-1}} &= \mathbb{R}^{d_{\ell} \times d_{\ell-1}}
\label{eq:finalbackprop3}
\end{eqnarray}
$$

## Putting Everything Together
1. Forward pass (what to remember?)
2. Compute Loss
3. Compute $\Delta$ for the loss
4. backprop
5. ...

## Practical Considerations
### Weight Initialization