---
layout: post
title: Derivation of a Weighted Recursive Linear Least Squares Estimator
modified:
categories: [math, stats, ML]
description: "Deriving a weighted recursive least squares estimator for batches of observations, with exponential forgetting and multiple outputs, together with its single-observation special case."
tags: [Least Squares, Regression, Weighted Least Squares, RLS, online estimation, Woodbury, Sherman-Morrison]
thumbnail: assets/img/2026-09-23-derivation-of-a-weighted-recursive-least-squares-estimator/weighted-rls-thumbnail.webp
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-09-23T00:00:00+02:00
related_posts: true
---

In this post, we derive an incremental version of the [weighted least squares estimator]({% post_url 2026-09-20-the-weighted-least-squares-algorithm %}). In practice, the well-known recursive least squares (RLS) filter is often used to learn a linear function in a fully online setting. The RLS filter processes one observation at a time and uses exponentially decaying weights in order to be able to adapt to new concepts.

Here, we derive a similar, but slightly more general, incremental version of the weighted least squares estimator. Specifically, we will derive a multivariate variant for batches (with a batch size $$\mu \geq 1$$), with individual observation weights and exponential forgetting of older batches. This is beneficial in setups which do not have to be fully online (batch processing usually allows us to reduce the computation time if parallelization is supported) or in situations where the amount of data is too large to be processed in a single batch. The classic single-observation RLS filter then follows as a special case at the end.

<!--more-->

## Notation

The following table summarizes the symbols used throughout this post. Vectors are written in bold lowercase, matrices in bold uppercase and scalars in regular font. Unless stated otherwise, vectors are column vectors, and the input vectors appear as rows of the design matrices.

| Symbol                                                            | Type                   | Description                                                                                                                                           |
| ----------------------------------------------------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| $$n$$                                                             | scalar                 | Number of observations processed so far                                                                                                               |
| $$k$$                                                             | scalar                 | Number of features, i.e. entries of an input vector (including a constant entry if we want an intercept)                                              |
| $$m$$                                                             | scalar                 | Number of outputs (target variables)                                                                                                                  |
| $$\mu$$                                                           | scalar                 | Batch size, i.e. the number of observations in an incoming batch, $$\mu\geq1$$                                                                        |
| $$M$$                                                             | scalar                 | Number of batches processed so far                                                                                                                    |
| $$\mathbf{X}_n$$                                                  | matrix                 | Design matrix with the first $$n$$ input vectors as rows, $$\mathbf{X}_n\in\mathbb{R}^{n\times k}$$                                                   |
| $$\mathbf{y}_n$$                                                  | vector                 | Targets of the first $$n$$ observations, $$\mathbf{y}_n\in\mathbb{R}^{n}$$                                                                            |
| $$\mathbf{W}_n$$                                                  | matrix                 | Diagonal matrix with the current (possibly decayed) weights of the first $$n$$ observations, $$\mathbf{W}_n\in\mathbb{R}^{n\times n}$$                |
| $$\mathbf{X}_\mu$$                                                | matrix                 | Input vectors of the incoming batch as rows, $$\mathbf{X}_\mu\in\mathbb{R}^{\mu\times k}$$                                                            |
| $$\mathbf{y}_\mu$$, $$\mathbf{Y}_\mu$$                            | vector, matrix         | Targets of the incoming batch for one or $$m$$ outputs, $$\mathbf{y}_\mu\in\mathbb{R}^{\mu}$$, $$\mathbf{Y}_\mu\in\mathbb{R}^{\mu\times m}$$          |
| $$\mathbf{W}_\mu$$                                                | matrix                 | Diagonal matrix with the positive weights of the incoming batch, $$\mathbf{W}_\mu\in\mathbb{R}^{\mu\times\mu}$$                                       |
| $$\mathbf{X}^{[j]}$$, $$\mathbf{W}^{[j]}$$, $$\mathbf{y}^{[j]}$$  | matrix, matrix, vector | Inputs, incoming weights and targets of batch $$j$$ in the objective                                                                                  |
| $$\mathbf{x}_{n+1}$$, $$y_{n+1}$$, $$w_{n+1}$$                    | vector, scalar, scalar | Input vector, target and positive weight of a single new observation, $$\mathbf{x}_{n+1}\in\mathbb{R}^{k}$$                                           |
| $$\boldsymbol{\theta}_n$$                                         | vector                 | Coefficient vector after $$n$$ observations, $$\boldsymbol{\theta}_n\in\mathbb{R}^{k}$$                                                               |
| $$\boldsymbol{\Theta}_n$$                                         | matrix                 | Coefficient matrix for $$m$$ outputs, $$\boldsymbol{\Theta}_n\in\mathbb{R}^{k\times m}$$                                                              |
| $$\lambda$$                                                       | scalar                 | Forgetting factor, $$0<\lambda\leq1$$                                                                                                                 |
| $$\lambda_n$$                                                     | scalar                 | Forgetting factor of the current update: $$1$$ for the first batch and $$\lambda$$ afterwards                                                         |
| $$\rho$$                                                          | scalar                 | Initial regularization (ridge) coefficient, $$\rho>0$$                                                                                                |
| $$\rho_n$$                                                        | scalar                 | Current ridge coefficient, which decays together with the old observations                                                                            |
| $$\mathbf{I}$$                                                    | matrix                 | Identity matrix, $$\mathbf{I}\in\mathbb{R}^{k\times k}$$ unless indicated otherwise (e.g. $$\mathbf{I}_\mu$$)                                         |
| $$\mathbf{G}_n$$                                                  | matrix                 | Weighted transposed design matrix, $$\mathbf{G}_n=\mathbf{X}_n^T\mathbf{W}_n\in\mathbb{R}^{k\times n}$$                                               |
| $$\mathbf{A}_n$$                                                  | matrix                 | Regularized weighted normal matrix, $$\mathbf{A}_n=\mathbf{G}_n\mathbf{X}_n+\rho_n\mathbf{I}\in\mathbb{R}^{k\times k}$$                               |
| $$\mathbf{b}_n$$                                                  | vector                 | Weighted right-hand side, $$\mathbf{b}_n=\mathbf{G}_n\mathbf{y}_n\in\mathbb{R}^{k}$$, so that $$\boldsymbol{\theta}_n=\mathbf{A}_n^{-1}\mathbf{b}_n$$ |
| $$\mathbf{e}_\mu$$, $$\mathbf{E}_\mu$$                            | vector, matrix         | Prediction errors of the incoming batch for one or $$m$$ outputs, computed before the update                                                          |
| $$\boldsymbol{\Delta}_\mu$$                                       | matrix                 | Gain matrix of the batch update, $$\boldsymbol{\Delta}_\mu\in\mathbb{R}^{k\times\mu}$$                                                                |
| $$e_{n+1}$$, $$\boldsymbol{\delta}_{n+1}$$                        | scalar, vector         | Prediction error and gain vector of the single-observation update, $$\boldsymbol{\delta}_{n+1}\in\mathbb{R}^{k}$$                                     |
| $$E_M(\boldsymbol{\theta})$$                                      | function               | Weighted and regularized least squares objective after $$M$$ batches                                                                                  |

## Forgetting and the Initial Regularization

We assume positive diagonal entries in each incoming weight matrix $$\mathbf{W}_\mu$$ and $$\rho>0$$, so that the inverses used below exist. Furthermore, the initial ridge decays together with the old observations. This keeps the recursion below simple: a fixed ridge would instead give $$\mathbf{A}_{n+\mu}=\lambda_n\mathbf{A}_n+\mathbf{X}_\mu^T\mathbf{W}_\mu\mathbf{X}_\mu+(1-\lambda_n)\rho\mathbf{I}$$, and the additional full-rank term would prevent the low-rank update of the inverse that we derive below.

For batches of size $$\mu$$, let $$n$$ count the observations already processed. The first batch does not decay the prior, and all subsequent batches use the chosen forgetting factor $$0<\lambda\leq1$$ (decaying the prior already in the first update would be equally valid and would merely replace $$\rho$$ by $$\lambda\rho$$). With $$\rho_n$$ denoting the current ridge coefficient, this means

$$
\begin{equation}
\lambda_n=
\begin{cases}
1,&n=0,\\
\lambda,&n>0,
\end{cases}
\qquad
\rho_0=\rho,\qquad
\rho_{n+\mu}=\lambda_n\rho_n,\qquad
\mathbf{A}_0=\rho\mathbf{I},\quad
\mathbf{b}_0=\mathbf{0},\quad
\boldsymbol{\theta}_0=\mathbf{0}.
\label{eq:rls-initialization}
\end{equation}
$$

After $$M\geq1$$ batches, $$n=M\mu$$ and $$\rho_n=\rho\lambda^{M-1}$$. If $$\mathbf{X}^{[j]}$$, $$\mathbf{W}^{[j]}$$ and $$\mathbf{y}^{[j]}$$ denote the inputs, incoming weights and targets of batch $$j$$, the objective being minimized is therefore

$$
\begin{equation}
E_M(\boldsymbol{\theta})
=\frac12\sum_{j=1}^{M}\lambda^{M-j}
\big(\mathbf{X}^{[j]}\boldsymbol{\theta}-\mathbf{y}^{[j]}\big)^T
\mathbf{W}^{[j]}
\big(\mathbf{X}^{[j]}\boldsymbol{\theta}-\mathbf{y}^{[j]}\big)
+\frac12\rho\lambda^{M-1}\boldsymbol{\theta}^T\boldsymbol{\theta}.
\label{eq:rls-objective}
\end{equation}
$$

The regularizer covers all coefficients, including the intercept if one is present, and remains constant for $$\lambda=1$$. For $$\lambda<1$$, a batch recomputation used to check an implementation must include the decayed ridge as well as the decayed observation weights.

## The Weighted Least Squares Formulation

We start with the closed-form solution of the weighted least squares estimator for a fixed dataset and a ridge coefficient $$\rho$$:

$$
\begin{align}
  \boldsymbol{\theta} = \big(\mathbf{X}^T \mathbf{W} \mathbf{X} + \rho \mathbf{I}\big)^{-1} \mathbf{X}^T \mathbf{W} \mathbf{y},
\end{align}
$$

where $$\mathbf{X}$$ is a matrix containing $$n$$ inputs of length $$k$$ as row vectors, $$\mathbf{W}$$ is a diagonal weight matrix, carrying a weight for each of the $$n$$ observations, $$\mathbf{y}$$ is an $$n$$-dimensional target vector with one value for each input vector (as we will see later, we can easily extend our derivation to multi-dimensional outputs, where we would instead use a matrix $$\mathbf{Y}$$). The term $$\rho \mathbf{I}$$ (regularization factor and identity matrix) is the so-called regularizer, which is used to prevent overfitting.

Since we have $$n$$ observations, we can also slightly modify the above equation to indicate the current iteration. Here the current ridge coefficient is $$\rho_n$$, following the convention above:

$$
\begin{align}
  \boldsymbol{\theta}_n =& \big(\overbrace{\underbrace{ \mathbf{X}_n^T \mathbf{W}_n }_{=\mathbf{G}_n} \mathbf{X}_n + \rho_n \mathbf{I} }^{=\mathbf{A}_n}\big)^{-1}\overbrace{ \underbrace{\mathbf{X}_n^T \mathbf{W}_n}_{=\mathbf{G}_n} \mathbf{y}_n }^{=\mathbf{b}_n} \label{eq:rls-batch-weightedRLS}
  = \big(\overbrace{\mathbf{G}_n \mathbf{X}_n + \rho_n \mathbf{I} }^{=\mathbf{A}_n}\big)^{-1}\overbrace{ \mathbf{G}_n \mathbf{y}_n }^{=\mathbf{b}_n}
  = \mathbf{A}_n^{-1} \mathbf{b}_n,\\

  & \boldsymbol{\theta}_n \in \mathbb{R}^{k},
  \ \mathbf{X}_n \in \mathbb{R}^{n \times k},
  \ \mathbf{W}_n \in \mathbb{R}^{n \times n},
  \  \mathbf{I} \in \mathbb{R}^{k \times k},
  \  \rho_n \in \mathbb{R},
  \ \mathbf{y}_n \in \mathbb{R}^{n} \nonumber\\
& \mathbf{G}_n \in \mathbb{R}^{k \times n}, \ \mathbf{A}_n \in \mathbb{R}^{k \times k}, \ \mathbf{b}_n \in \mathbb{R}^{k}. \nonumber
\end{align}
$$

## Appending a New Batch

If a new batch of $$\mu$$ observation pairs $$\mathbf{X}_{\mu} \in \mathbb{R}^{\mu \times k}, \ \mathbf{y}_{\mu} \in \mathbb{R}^\mu$$ arrives, some of the above matrices and vectors change as follows (the others remain unchanged):

$$
\begin{align}
  \ \mathbf{X}_{n+\mu} = \begin{bmatrix} \mathbf{X}_n \\ \mathbf{X}_{\mu} \end{bmatrix},
  \ \mathbf{W}_{n+\mu} = \begin{bmatrix} \lambda_n  \mathbf{W}_n & \mathbf{0} \\ \mathbf{0}^T & \mathbf{W}_{\mu} \end{bmatrix},
  \ \mathbf{y}_{n+\mu} = \begin{bmatrix} \mathbf{y}_{n} \\ \mathbf{y}_{\mu} \end{bmatrix}, \label{eq:rls-batch-newpoint}
\end{align}
$$

where

  $$\mathbf{X}_{n+\mu} \in \mathbb{R}^{(n+\mu) \times k}, \ \mathbf{W}_{n+\mu} \in \mathbb{R}^{(n+\mu) \times (n+\mu)}, \ 0<\lambda_n\leq1, \ \mathbf{W}_{\mu} \in \mathbb{R}^{\mu \times \mu}, \ \mathbf{y}_{n+\mu} \in \mathbb{R}^{n+\mu}$$.

Here, $$\lambda_n$$ is the forgetting factor of the current update: it is $$1$$ for the first batch and $$\lambda$$ thereafter. Thus, forgetting is applied once per incoming batch, and the old weights and the current ridge coefficient are both multiplied by this factor. Now let us insert the definitions in Eq. $$\eqref{eq:rls-batch-newpoint}$$ into Eq. $$\eqref{eq:rls-batch-weightedRLS}$$:

$$
\begin{align}
  \boldsymbol{\theta}_{n+\mu} &= \Bigg(
    \overbrace{
    \underbrace{
    \begin{bmatrix} \mathbf{X}_n \\ \mathbf{X}_{\mu} \end{bmatrix}^T
    \begin{bmatrix} \lambda_n \mathbf{W}_n & \mathbf{0} \\ \mathbf{0}^T & \mathbf{W}_{\mu} \end{bmatrix}
    }_{=\mathbf{G}_{n+\mu}}
    \begin{bmatrix} \mathbf{X}_n \\ \mathbf{X}_{\mu} \end{bmatrix}
    + \rho_{n+\mu} \mathbf{I}
    }^{=\mathbf{A}_{n+\mu}}
    \Bigg)^{-1}
    \overbrace{
    \underbrace{
    \begin{bmatrix} \mathbf{X}_n \\ \mathbf{X}_{\mu} \end{bmatrix}^T
    \begin{bmatrix} \lambda_n \mathbf{W}_n & \mathbf{0} \\ \mathbf{0}^T & \mathbf{W}_{\mu} \end{bmatrix}
    }_{=\mathbf{G}_{n+\mu}}
    \begin{bmatrix} \mathbf{y}_{n} \\ \mathbf{y}_{\mu} \end{bmatrix}
    }^{=\mathbf{b}_{n+\mu}} \nonumber \\
    &=
    \Bigg(
    \overbrace{
    \mathbf{G}_{n+\mu}
    \begin{bmatrix} \mathbf{X}_n \\ \mathbf{X}_{\mu} \end{bmatrix}
    + \rho_{n+\mu} \mathbf{I}
    }^{=\mathbf{A}_{n+\mu}}
    \Bigg)^{-1}
    \overbrace{
    \mathbf{G}_{n+\mu}
    \begin{bmatrix} \mathbf{y}_{n} \\ \mathbf{y}_{\mu} \end{bmatrix}
    }^{=\mathbf{b}_{n+\mu}}
    =
    \mathbf{A}_{n+\mu}^{-1}
    \mathbf{b}_{n+\mu}, \label{eq:rls-batch-phi}
\end{align}
$$

where we identify:

$$
\begin{align}
\mathbf{G}_{n+\mu} &= \begin{bmatrix} \mathbf{X}_n \\ \mathbf{X}_{\mu} \end{bmatrix}^T \begin{bmatrix} \lambda_n \mathbf{W}_n & \mathbf{0} \\ \mathbf{0}^T & \mathbf{W}_{\mu} \end{bmatrix} \in \mathbb{R}^{k \times (n+\mu)} \label{eq:rls-batch-Gnp1}
,\\
\mathbf{A}_{n+\mu} &= \mathbf{G}_{n+\mu} \begin{bmatrix} \mathbf{X}_n \\ \mathbf{X}_{\mu} \end{bmatrix} + \rho_{n+\mu} \mathbf{I} \in \mathbb{R}^{k \times k} \label{eq:rls-batch-Ap1}
,\\
\mathbf{b}_{n+\mu} &= \mathbf{G}_{n+\mu} \begin{bmatrix} \mathbf{y}_{n} \\ \mathbf{y}_{\mu} \end{bmatrix} \in \mathbb{R}^{k}. \label{eq:rls-batch-Bp1}
\end{align}
$$

## Expanding the Weighted Design Matrix

Now let us expand equation $$\eqref{eq:rls-batch-Gnp1}$$:

$$
\begin{align*}
\mathbf{G}_{n+\mu} &= \begin{bmatrix} \overbrace{\mathbf{X}_n}^{n \times k} \\ \underbrace{\mathbf{X}_{\mu}}_{\mu \times k} \end{bmatrix}^T
\begin{bmatrix} \overbrace{\lambda_n \mathbf{W}_n}^{n \times n} & \overbrace{\mathbf{0}}^{n \times \mu} \\ \underbrace{\mathbf{0}^T}_{\mu \times n} & \underbrace{\mathbf{W}_{\mu}}_{\mu \times \mu} \end{bmatrix}
 =
\begin{bmatrix} \overbrace{\mathbf{X}_n^T}^{k \times n} & \overbrace{\mathbf{X}_{\mu}^T}^{k \times \mu} \end{bmatrix}
\begin{bmatrix} \overbrace{\lambda_n \mathbf{W}_n}^{n \times n} & \overbrace{\mathbf{0}}^{n \times \mu} \\ \underbrace{\mathbf{0}^T}_{\mu \times n} & \underbrace{\mathbf{W}_{\mu}}_{\mu \times \mu} \end{bmatrix}
\nonumber \\ &=
\begin{bmatrix}  \lambda_n\mathbf{X}_n^T  \mathbf{W}_n + \mathbf{X}_{\mu}^T \mathbf{0}^T & \mathbf{X}_n^T \mathbf{0} +  \mathbf{X}_{\mu}^T \mathbf{W}_{\mu} \end{bmatrix}
=
\begin{bmatrix}  \lambda_n \mathbf{X}_n^T \mathbf{W}_n  & \mathbf{X}_{\mu}^T \mathbf{W}_{\mu} \end{bmatrix}
\\ &=
\begin{bmatrix} \underbrace{\lambda_n \mathbf{G}_{n} }_{k \times n} & \underbrace{ \mathbf{X}_{\mu}^T \mathbf{W}_{\mu}}_{k\times \mu} \end{bmatrix} \in \mathbb R^{k \times (n+\mu)}.
\end{align*}
$$

## Updating the Normal Matrix

In the next step, let us evaluate $$\mathbf{A}_{n+\mu}$$ from Eq. $$\eqref{eq:rls-batch-Ap1}$$:

$$
\begin{align}
\mathbf{A}_{n+\mu}
&= \mathbf{G}_{n+\mu} \begin{bmatrix} \mathbf{X}_n \\ \mathbf{X}_{\mu} \end{bmatrix} + \rho_{n+\mu} \mathbf{I} \\
&= \begin{bmatrix} \underbrace{\lambda_n \mathbf{G}_n}_{k\times n} & \underbrace{\mathbf{X}_{\mu}^T \mathbf{W}_{\mu}}_{k\times\mu} \end{bmatrix}
\begin{bmatrix} \overbrace{\mathbf{X}_n}^{n\times k} \\ \underbrace{\mathbf{X}_{\mu}}_{\mu\times k} \end{bmatrix} + \rho_{n+\mu} \mathbf{I} \\
&= \lambda_n \mathbf{G}_n \mathbf{X}_n + \mathbf{X}_{\mu}^T \mathbf{W}_{\mu}\mathbf{X}_{\mu}
+ \underbrace{\rho_{n+\mu}}_{=\lambda_n\rho_n}\mathbf{I} \\
&= \lambda_n\underbrace{\big(\mathbf{G}_n\mathbf{X}_n+\rho_n\mathbf{I}\big)}_{=\mathbf{A}_n}
+ \mathbf{X}_{\mu}^T\mathbf{W}_{\mu}\mathbf{X}_{\mu} \\
&= \lambda_n\underbrace{\mathbf{A}_n}_{k\times k}
+ \underbrace{\mathbf{X}_{\mu}^T\mathbf{W}_{\mu}\mathbf{X}_{\mu}}_{k\times k},
\qquad \mathbf{A}_0=\rho\mathbf{I},\quad \lambda_0=1.
\end{align}
$$

## Updating the Inverse with the Woodbury Identity

Since we have to compute the inverse of $$\mathbf{A}_{n+\mu}$$, it might be helpful to find an incremental formulation, since the inverse is costly to compute. In this case, the Woodbury matrix identity {% cite woodbury1950inverting --file thesis %} helps:

$$
\begin{align}
(\mathbf{A} + \mathbf{U}\mathbf{C}\mathbf{V})^{-1} = \mathbf{A}^{-1} - \mathbf{A}^{-1}\mathbf{U} (\mathbf{C}^{-1} + \mathbf{V}\mathbf{A}^{-1}\mathbf{U})^{-1}\mathbf{V}\mathbf{A}^{-1}.
\end{align}
$$

This gives us:

$$
\begin{align}
\mathbf{A}_{n+\mu}^{-1} &= (\lambda_n\mathbf{A}_n)^{-1} - \overbrace{(\lambda_n\mathbf{A}_n)^{-1} \mathbf{X}_{\mu}^T
\big(\mathbf{W}_{\mu}^{-1} + \mathbf{X}_{\mu} (\lambda_n\mathbf{A}_n)^{-1} \mathbf{X}_{\mu}^T \big)^{-1}}^{=\boldsymbol{\Delta}_\mu} \mathbf{X}_{\mu} (\lambda_n\mathbf{A}_n)^{-1} \nonumber \\
&=  (\lambda_n\mathbf{A}_n)^{-1} - \boldsymbol{\Delta}_\mu \mathbf{X}_{\mu} (\lambda_n\mathbf{A}_n)^{-1},  \label{eq:rls-batch-Ap1inv}
\end{align}
$$

with:

$$
\begin{align}
\boldsymbol{\Delta}_\mu &= (\lambda_n\mathbf{A}_n)^{-1} \mathbf{X}_{\mu}^T
\big(\mathbf{W}_{\mu}^{-1} + \mathbf{X}_{\mu} (\lambda_n\mathbf{A}_n)^{-1} \mathbf{X}_{\mu}^T \big)^{-1} \in \mathbb{R}^{k \times \mu} \label{eq:rls-batch-deltaa} \\
&= \mathbf{A}_n^{-1} \mathbf{X}_{\mu}^T \big(\lambda_n \mathbf{W}_{\mu}^{-1} + \mathbf{X}_{\mu} \mathbf{A}_n^{-1} \mathbf{X}_{\mu}^T \big)^{-1}
\end{align}
$$

## Updating the Weighted Target Vector

Then, we expand Eq. $$\eqref{eq:rls-batch-Bp1}$$:

$$
\begin{align}
\mathbf{b}_{n+\mu} &= \mathbf{G}_{n+\mu} \begin{bmatrix} \mathbf{y}_{n} \\ \mathbf{y}_{\mu} \end{bmatrix}
= \begin{bmatrix} \underbrace{\lambda_n\mathbf{G}_{n}}_{k \times n} & \underbrace{\mathbf{X}_{\mu}^T \mathbf{W}_{\mu}}_{k\times\mu} \end{bmatrix}
   \begin{bmatrix} \overbrace{\mathbf{y}_{n}}^{n\times 1} \\ \underbrace{\mathbf{y}_{\mu}}_{\mu\times 1} \end{bmatrix}\\
&= \lambda_n\mathbf{G}_{n} \mathbf{y}_{n} + \mathbf{X}_{\mu}^T \mathbf{W}_{\mu}  \mathbf{y}_{\mu}
= \lambda_n\underbrace{\mathbf{b}_{n}}_{k\times 1} + \underbrace{\mathbf{X}_{\mu}^T \mathbf{W}_{\mu} \mathbf{y}_{\mu} }_{k\times 1} \label{eq:rls-batch-Bp1new}
\end{align}
$$

## Expanding the Parameter Update

Now let us insert the results of $$\eqref{eq:rls-batch-Ap1inv}$$ and $$\eqref{eq:rls-batch-Bp1new}$$ into Eq. $$\eqref{eq:rls-batch-phi}$$ and then simplify the expression:

$$
\begin{align}
  \boldsymbol{\theta}_{n+\mu} &= \mathbf{A}_{n+\mu}^{-1} \mathbf{b}_{n+\mu} \\
  &=\Big[(\lambda_n\mathbf{A}_n)^{-1} - \boldsymbol{\Delta}_\mu \mathbf{X}_{\mu} (\lambda_n\mathbf{A}_n)^{-1} \Big] \Big[\lambda_n \mathbf{b}_{n} + \mathbf{X}_{\mu}^T \mathbf{W}_{\mu} \mathbf{y}_{\mu} \Big] \\
	&= \underbrace{\mathbf{A}_n^{-1} \mathbf{b}_{n}}_{\boldsymbol{\theta}_{n}} + (\lambda_n\mathbf{A}_n)^{-1} \mathbf{X}_{\mu}^T \mathbf{W}_{\mu} \mathbf{y}_{\mu} - \boldsymbol{\Delta}_\mu \mathbf{X}_{\mu} \underbrace{\mathbf{A}_n^{-1} \mathbf{b}_{n}}_{\boldsymbol{\theta}_{n}} - \boldsymbol{\Delta}_\mu \mathbf{X}_{\mu} (\lambda_n\mathbf{A}_n)^{-1} \mathbf{X}_{\mu}^T \mathbf{W}_{\mu} \mathbf{y}_{\mu} \\
	&= \boldsymbol{\theta}_{n} + \Big[(\lambda_n\mathbf{A}_n)^{-1} - \boldsymbol{\Delta}_\mu \mathbf{X}_{\mu} (\lambda_n\mathbf{A}_n)^{-1} \Big] \mathbf{X}_{\mu}^T \mathbf{W}_{\mu} \mathbf{y}_{\mu}  - \boldsymbol{\Delta}_\mu \mathbf{X}_{\mu} \boldsymbol{\theta}_{n}
	\label{eq:rls-batch-areWeDone}
\end{align}
$$

## Rearranging the Gain Matrix

Although we did a few rearrangements, it seems like Eq. $$\eqref{eq:rls-batch-areWeDone}$$ cannot be simplified further. However, we can find a more compact solution if we look closer at Eq. $$\eqref{eq:rls-batch-deltaa}$$:

$$
\begin{align}
\boldsymbol{\Delta}_\mu &= (\lambda_n\mathbf{A}_n)^{-1} \mathbf{X}_{\mu}^T \big(\mathbf{W}_{\mu}^{-1} + \mathbf{X}_{\mu} (\lambda_n\mathbf{A}_n)^{-1} \mathbf{X}_{\mu}^T \big)^{-1} \\
\boldsymbol{\Delta}_\mu \big(\mathbf{W}_{\mu}^{-1} + \mathbf{X}_{\mu} (\lambda_n\mathbf{A}_n)^{-1} \mathbf{X}_{\mu}^T \big) &= (\lambda_n\mathbf{A}_n)^{-1} \mathbf{X}_{\mu}^T \\
\boldsymbol{\Delta}_\mu \mathbf{W}_{\mu}^{-1} + \boldsymbol{\Delta}_\mu \mathbf{X}_{\mu} (\lambda_n\mathbf{A}_n)^{-1} \mathbf{X}_{\mu}^T &= (\lambda_n\mathbf{A}_n)^{-1} \mathbf{X}_{\mu}^T \\
\boldsymbol{\Delta}_\mu \mathbf{W}_{\mu}^{-1} &= \big[(\lambda_n\mathbf{A}_n)^{-1} - \boldsymbol{\Delta}_\mu \mathbf{X}_{\mu} (\lambda_n\mathbf{A}_n)^{-1} \big] \mathbf{X}_{\mu}^T  \label{eq:rls-batch-delta-simple}
\end{align}
$$

Interestingly, we can find the right-hand side of Eq. $$\eqref{eq:rls-batch-delta-simple}$$ also in Eq. $$\eqref{eq:rls-batch-areWeDone}$$. If we use the above relation, we can therefore simplify $$\eqref{eq:rls-batch-areWeDone}$$ significantly:

$$
\begin{align}
\boldsymbol{\theta}_{n+\mu} &= \boldsymbol{\theta}_{n} + \boldsymbol{\Delta}_\mu \mathbf{W}_{\mu}^{-1} \mathbf{W}_{\mu} \mathbf{y}_{\mu}  - \boldsymbol{\Delta}_\mu \mathbf{X}_{\mu} \boldsymbol{\theta}_{n} \\
&= \boldsymbol{\theta}_{n} + \boldsymbol{\Delta}_\mu \mathbf{y}_{\mu}  - \boldsymbol{\Delta}_\mu \mathbf{X}_{\mu} \boldsymbol{\theta}_{n} \\
&= \boldsymbol{\theta}_{n} + \boldsymbol{\Delta}_\mu \Big( \mathbf{y}_{\mu}  - \mathbf{X}_{\mu} \boldsymbol{\theta}_{n} \Big) \\
&= \boldsymbol{\theta}_{n} + \boldsymbol{\Delta}_\mu \mathbf{e}_\mu,
\end{align}
$$

where $$\mathbf{e}_{\mu}$$ is the prediction error:

$$
\begin{align}
\mathbf{e}_\mu = \mathbf{y}_{\mu}  - \mathbf{X}_{\mu} \boldsymbol{\theta}_{n}.
\end{align}
$$

This means that the update rule performs a step in the parameter space, which is given by the gain matrix $$\boldsymbol{\Delta}_\mu$$ and scaled by the prediction errors $$\mathbf{e}_\mu$$ of the new batch. Large prediction errors can produce a large step, but its size also depends on the gain, and contributions from different observations can cancel. For example, two identical input rows with equal weights and opposite residuals produce no coefficient update, however large those residuals are. If the current model already predicts all targets of the new batch without error, the parameter vector remains unaltered.

## Summary for a Single Output

We can summarize our findings for the single-output case with a positive diagonal weight matrix $$\mathbf{W}_{\mu}$$ as follows:

$$
\begin{align}
\mathbf{e}_\mu &= \mathbf{y}_{\mu}  - \mathbf{X}_{\mu} \boldsymbol{\theta}_{n}\\
\boldsymbol{\Delta}_\mu &= \mathbf{A}_n^{-1} \mathbf{X}_{\mu}^T \big(\lambda_n \mathbf{W}_{\mu}^{-1} + \mathbf{X}_{\mu} \mathbf{A}_n^{-1} \mathbf{X}_{\mu}^T \big)^{-1}\\
\boldsymbol{\theta}_{n+\mu} &= \boldsymbol{\theta}_{n} + \boldsymbol{\Delta}_\mu \mathbf{e}_\mu \\
\mathbf{A}_{n+\mu}^{-1} &= (\lambda_n\mathbf{A}_n)^{-1} - \boldsymbol{\Delta}_\mu \mathbf{X}_{\mu} (\lambda_n\mathbf{A}_n)^{-1}
\end{align}
$$

where

$$
\begin{align*}
&0<\lambda_n\leq1,\quad
\mathbf{e}_\mu,\mathbf{y}_\mu\in\mathbb R^\mu,\quad
\boldsymbol{\theta}_n,\boldsymbol{\theta}_{n+\mu}\in\mathbb R^k,\\
&\mathbf{X}_\mu\in\mathbb R^{\mu\times k},\quad
\boldsymbol{\Delta}_\mu\in\mathbb R^{k\times\mu},\quad
\mathbf{A}_n,\mathbf{A}_{n+\mu}\in\mathbb R^{k\times k},\quad
\mathbf{W}_\mu\in\mathbb R^{\mu\times\mu},\\
&\mathbf{A}_0=\rho\mathbf{I},\quad
\mathbf{A}_0^{-1}=\rho^{-1}\mathbf{I},\quad
\lambda_0=1,\quad
\boldsymbol{\theta}_0=\mathbf 0.
\end{align*}
$$

## Multivariate Batch Recursive Least Squares Algorithm

Extending the above equations to the multivariate case with $$m$$ dimensions is straightforward. We simply have to replace some vectors with matrices. Furthermore, for a simple setup with exponentially decaying weights we use the same forgetting convention with $$0<\lambda\leq1$$ and set $$\mathbf{W}_{\mu}=\mathbf{I}_\mu$$. Hence, the final multivariate batch RLS algorithm can be described as follows:

$$
\begin{align}
\mathbf{E}_\mu &= \mathbf{Y}_{\mu}  - \mathbf{X}_{\mu} \boldsymbol{\Theta}_{n}\\
\boldsymbol{\Delta}_\mu &= \mathbf{A}_n^{-1} \mathbf{X}_{\mu}^T \big(\lambda_n \mathbf{I}_\mu + \mathbf{X}_{\mu} \mathbf{A}_n^{-1} \mathbf{X}_{\mu}^T \big)^{-1}\\
\boldsymbol{\Theta}_{n+\mu} &= \boldsymbol{\Theta}_{n} + \boldsymbol{\Delta}_\mu \mathbf{E}_\mu \\
\mathbf{A}_{n+\mu}^{-1} &= \frac{1}{\lambda_n}\mathbf{A}_n^{-1} - \frac{1}{\lambda_n}\boldsymbol{\Delta}_\mu \mathbf{X}_{\mu}\mathbf{A}_n^{-1}
\end{align}
$$

where

$$
\begin{align*}
&0<\lambda_n\leq1,\quad
\mathbf{E}_\mu,\mathbf{Y}_\mu\in\mathbb R^{\mu\times m},\quad
\boldsymbol{\Theta}_n,\boldsymbol{\Theta}_{n+\mu}\in\mathbb R^{k\times m},\\
&\mathbf{X}_\mu\in\mathbb R^{\mu\times k},\quad
\boldsymbol{\Delta}_\mu\in\mathbb R^{k\times\mu},\quad
\mathbf{A}_n^{-1},\mathbf{A}_{n+\mu}^{-1}\in\mathbb R^{k\times k},\\
&\mathbf{A}_0^{-1}=\rho^{-1}\mathbf{I},\quad
\lambda_0=1,\quad
\boldsymbol{\Theta}_0=\mathbf 0_{k\times m}.
\end{align*}
$$

## The Single-observation Special Case

The classic RLS filter processes one observation at a time. For $$\mu=1$$, the incoming batch consists of a single input vector $$\mathbf{x}_{n+1}$$ with target $$y_{n+1}$$ and positive weight $$w_{n+1}$$, so that $$\mathbf{X}_\mu=\mathbf{x}_{n+1}^T$$, $$\mathbf{y}_\mu=y_{n+1}$$ and $$\mathbf{W}_\mu=w_{n+1}$$. The matrix that has to be inverted in the gain then reduces to the scalar $$\lambda_n w_{n+1}^{-1}+\mathbf{x}_{n+1}^T\mathbf{A}_n^{-1}\mathbf{x}_{n+1}$$, and the Woodbury identity reduces to the Sherman-Morrison formula {% cite sherman1950adjustment --file thesis %}, so that no matrix has to be inverted at all. If we multiply the numerator and the denominator of the gain by $$w_{n+1}$$, the gain matrix becomes the vector $$\boldsymbol{\delta}_{n+1}$$, and the update reads:

$$
\begin{align}
e_{n+1} &= y_{n+1}-\mathbf{x}_{n+1}^T\boldsymbol{\theta}_n,\\
\boldsymbol{\delta}_{n+1} &= \frac{w_{n+1}\mathbf{A}_n^{-1}\mathbf{x}_{n+1}}{\lambda_n+w_{n+1}\mathbf{x}_{n+1}^T\mathbf{A}_n^{-1}\mathbf{x}_{n+1}},\\
\boldsymbol{\theta}_{n+1} &= \boldsymbol{\theta}_n+\boldsymbol{\delta}_{n+1}e_{n+1},\\
\mathbf{A}_{n+1}^{-1} &= \frac{1}{\lambda_n}\Big(\mathbf{A}_n^{-1}-\boldsymbol{\delta}_{n+1}\mathbf{x}_{n+1}^T\mathbf{A}_n^{-1}\Big),
\end{align}
$$

with $$\mathbf{A}_0^{-1}=\rho^{-1}\mathbf{I}$$ and $$\boldsymbol{\theta}_0=\mathbf{0}$$. With unit weights and $$\lambda_n=\lambda$$, these are the familiar equations of the exponentially weighted RLS filter, and without forgetting, $$\lambda=1$$, the denominator of the gain simplifies to $$1+w_{n+1}\mathbf{x}_{n+1}^T\mathbf{A}_n^{-1}\mathbf{x}_{n+1}$$. Note that the prediction error and the gain are both computed from the previous state, before the coefficients or the inverse are replaced. Also, $$\lambda_n$$ appears twice, in the denominator of the gain and in the scaling of the inverse, which is easy to overlook when translating the equations into code.

Several outputs are handled as in the multivariate batch algorithm above. The new observation then comes with one target per output, collected in the row vector $$\mathbf{Y}_\mu\in\mathbb{R}^{1\times m}$$, and the coefficients form the matrix $$\boldsymbol{\Theta}_n\in\mathbb{R}^{k\times m}$$. Since the gain does not depend on the targets, $$\boldsymbol{\delta}_{n+1}$$ and $$\mathbf{A}_{n+1}^{-1}$$ are computed exactly as for a single output, and the complete single-observation update for $$m$$ outputs reads

$$
\begin{align}
\mathbf{E}_\mu &= \mathbf{Y}_\mu-\mathbf{x}_{n+1}^T\boldsymbol{\Theta}_n,\\
\boldsymbol{\delta}_{n+1} &= \frac{w_{n+1}\mathbf{A}_n^{-1}\mathbf{x}_{n+1}}{\lambda_n+w_{n+1}\mathbf{x}_{n+1}^T\mathbf{A}_n^{-1}\mathbf{x}_{n+1}},\\
\boldsymbol{\Theta}_{n+1} &= \boldsymbol{\Theta}_n+\boldsymbol{\delta}_{n+1}\mathbf{E}_\mu,\\
\mathbf{A}_{n+1}^{-1} &= \frac{1}{\lambda_n}\Big(\mathbf{A}_n^{-1}-\boldsymbol{\delta}_{n+1}\mathbf{x}_{n+1}^T\mathbf{A}_n^{-1}\Big),
\end{align}
$$

with $$\boldsymbol{\Theta}_0=\mathbf{0}_{k\times m}$$. The row vector $$\mathbf{E}_\mu\in\mathbb{R}^{1\times m}$$ contains the prediction errors of all outputs, and the coefficient update is the outer product of the gain vector with this row. Hence, every column of $$\boldsymbol{\Theta}$$ is corrected in the same direction $$\boldsymbol{\delta}_{n+1}$$, scaled by the prediction error of its own output. Since the gain and the update of $$\mathbf{A}^{-1}$$ are shared by all outputs, additional outputs reuse these computations. The full single-observation update costs $$O(k^2+km)$$, with $$O(km)$$ storage for the coefficients, so the extra cost is small when the number of outputs is small compared with the number of features.

## Python Implementation and Notebook

To make the equations above more tangible, I wrote a [Jupyter notebook]({{ '/assets/jupyter/MarkusThill.github.io-jupyter/2026_09_23_weighted_recursive_least_squares.ipynb.html' | relative_url }}) that turns them into Python code step by step. It starts with the single-observation update from the previous section, implemented line by line with unit weights and without forgetting, and then adds one ingredient after the other: the initial regularization, observation weights, forgetting, batches of observations and several outputs. Each step is motivated by a small synthetic example, and after each step the recursive estimate is compared with the direct weighted least squares solution, which it reproduces up to rounding errors after every single update. The notebook only needs NumPy and Matplotlib and can be opened directly in Google Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MarkusThill/MarkusThill.github.io-jupyter/blob/main/2026_09_23_weighted_recursive_least_squares.ipynb)

{% include figure.liquid
   path="assets/img/2026-09-23-derivation-of-a-weighted-recursive-least-squares-estimator/weighted-rls-streaming-fit.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="100%"
   caption="Noisy observations of a line arrive one after another. Left: the fitted line after 2, 5, 20 and 200 observations. Right: the estimated intercept and slope as functions of the number of observations. These coefficients were computed by refitting after every observation; the recursion reproduces them up to rounding errors without storing the data."
%}

Two practical aspects, which do not follow from the derivation itself, are also examined in the notebook. First, the initial regularization should be neither too large, since it holds the first estimates back, nor extremely small, since the huge entries of $$\mathbf{A}_0^{-1}=\rho^{-1}\mathbf{I}$$ then amplify the rounding errors of the first updates. Second, with forgetting, the inverse is divided by $$\lambda_n$$ in every update. If an implementation computes $$\mathbf{A}_n^{-1}\mathbf{x}_{n+1}$$ once and reuses it in place of $$\mathbf{x}_{n+1}^T\mathbf{A}_n^{-1}$$ (which is only equivalent for an exactly symmetric matrix), the asymmetric part of the rounding errors grows by the factor $$1/\lambda$$ in every update, and in the notebook the estimates become useless after a few hundred updates with $$\lambda=0.95$$. Replacing $$\mathbf{A}^{-1}$$ by its symmetric part after every update removes this problem at almost no cost. This restores symmetry, but does not guarantee positive definiteness or prevent cancellation with poorly scaled or ill-conditioned inputs. Scaling the features helps; the notebook also includes a QR-based appendix that avoids forming the normal matrix or its inverse. Its examples focus on single precision, although QR can also help difficult double-precision problems.

The notebook ends with a small class, `WeightedRLS`, which is also available as a [Python module]({{ '/assets/code/2026-09-23-derivation-of-a-weighted-recursive-least-squares-estimator/weighted_rls.py' | relative_url }}), together with [tests and a short description]({{ '/assets/code/2026-09-23-derivation-of-a-weighted-recursive-least-squares-estimator/README.md' | relative_url }}). It implements the batch equations for one or several outputs, with positive observation weights, forgetting and the first-update convention $$\lambda_0=1$$, and it symmetrizes $$\mathbf{A}^{-1}$$ after every update. The method `update` processes one batch (or a single observation) and returns the prediction errors computed before the update, `fit` processes a whole data set in batches, and `predict` evaluates the model. Without forgetting, batches give exactly the same result as single observations, and moderate batch sizes are considerably faster; very large batches become slower again, since the $$\mu\times\mu$$ matrix in the gain has to be inverted. The batch-size benchmark uses the generic batch routine even for $$\mu=1$$, including a $$1\times1$$ inverse, so its speedup is relative to that implementation; the specialized single-observation update has less overhead. The most common setup in practice, however, uses single observations, unit weights and a forgetting factor slightly below one, for example to predict a signal from its own past values while its dynamics change slowly:

{% include figure.liquid
   path="assets/img/2026-09-23-derivation-of-a-weighted-recursive-least-squares-estimator/weighted-rls-signal-prediction.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="100%"
   caption="One-step-ahead prediction of a noisy oscillation whose frequency increases slowly over 3,000 steps, with the two previous values as inputs. Left: the last 80 steps and the predictions with a forgetting factor of 0.99. Middle: the first estimated coefficient, which lags further and further behind the true value without forgetting. Right: the mean squared prediction error of the last 100 steps, which stays close to the noise variance with a forgetting factor of 0.99."
%}

Since the gain matrix and $$\mathbf{A}^{-1}$$ do not depend on the targets, several outputs share these computations, with the additional prediction and coefficient-update work growing linearly in the number of outputs. The notebook illustrates this with a closed curve whose two coordinates are learned jointly from noisy points, using sines and cosines of the curve parameter as inputs.

{% include figure.liquid
   path="assets/img/2026-09-23-derivation-of-a-weighted-recursive-least-squares-estimator/weighted-rls-multi-output.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="100%"
   caption="Both coordinates of a heart-shaped curve are learned jointly from noisy points that arrive one at a time, with nine inputs (a constant and the sines and cosines of the curve parameter up to the fourth harmonic). The joint estimate agrees with separate fits for each coordinate, with batch updates and with the direct least squares solution."
%}

## References

<div class="publications">
{% bibliography --file thesis --cited --group_by none %}
</div>

**Related posts:** [The Weighted Linear Least Squares Algorithm]({% post_url 2026-09-20-the-weighted-least-squares-algorithm %}); [Online Estimation: Exponential Forgetting]({% post_url 2026-03-15-exponentially-weighted-estimation %}); [Online Estimation: Updating the Inverse Covariance Matrix]({% post_url 2026-04-26-online-inverse-covariance %}).
