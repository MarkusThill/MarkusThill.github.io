---
layout: post
title: The Weighted Linear Least Squares Algorithm
modified:
categories: [math, stats, ML]
description: "In this blog post, we are going to take a look at the so-called weighted linear least squares estimator, which is very similar to the ordinary linear least squares estimator, but with one slight modification: while the ordinary estimator assumes that the errors of all data points have the same variance (which is typically referred to as homoscedasticity) and therefore assigns the same weight to the errors in the objective function, the weighted counterpart allows us to weight every single error individually. This is especially interesting in cases where we are working in a heteroscedastic setting, that is, when the variability in the errors cannot be assumed to be the same."
tags: [Least Squares, Regression, Weighted Least Squares, OLS, WLS]
thumbnail: assets/img/2018-03-13-the-weighted-least-squares-algorithm/stats.jpg
giscus_comments: true
toc:
  beginning: true
share: true
date: 2026-09-20T00:46:46+02:00
---

In this blog post, we are going to take a look at the so-called weighted linear least squares estimator, which is very similar to the ordinary linear least squares estimator, but with one slight modification: while the ordinary estimator assumes that the errors of all data points have the same variance (which is typically referred to as homoscedasticity) and therefore assigns the same weight to the errors in the objective function, the weighted counterpart allows us to weight every single error individually. This is especially interesting in cases where we are working in a heteroscedastic setting, that is, when the variability in the errors cannot be assumed to be the same.

<!--more-->

## The Ordinary Least Squares Estimator

Let us start with the definition of a linear function (a function linear in its parameters):

$$
\begin{align}
y = \theta_0 + \theta_1 \phi_1(x_1, x_2, \ldots x_\ell) + \theta_2 \phi_2(x_1, x_2, \ldots x_\ell) + \ldots + \theta_k \phi_k(x_1, x_2, \ldots x_\ell) \label{eq:linearModel}
\end{align}
$$

where $$\theta_i$$ is the i-th parameter of the linear model ($$\theta_0$$ is the so-called bias) and $$\phi_i$$ returns a scalar which is computed based on the inputs $$x_1, x_2, \ldots x_\ell$$. Since $$y$$ is linear in its parameters $$\theta_i$$, there is no requirement for $$\phi_i$$ to be a linear function. So $$\phi_i$$ could, for example, simply be $$\phi_i=x_i$$, a polynomial, a radial basis function or something completely different. For simplicity, we write equation $$\eqref{eq:linearModel}$$ as follows:

$$
\begin{align}
y &= \theta_0 + \theta_1 \phi_1 + \theta_2 \phi_2 + \ldots + \theta_k \phi_k \\
&= \theta_0 + \sum_{j=1}^{k} \theta_j \phi_j \\
&= \vec{\theta}^{\mathsf{T}} \vec{\phi},
\end{align}
$$

with

$$
\begin{align}
\vec{\phi} = \begin{pmatrix} 1 \\ \phi_1 \\ \vdots \\ \phi_k \end{pmatrix}, \ \ \
\vec{\theta} = \begin{pmatrix} \theta_0 \\ \theta_1 \\ \vdots \\ \theta_k \end{pmatrix}.
 \label{eq:theta}
\end{align}
$$

Now let us assume that we have collected a set of $$n$$ data points $$(\vec{x}^{(1)}, y_*^{(1)}), (\vec{x}^{(2)}, y_*^{(2)}), \ldots (\vec{x}^{(n)}, y_*^{(n)})$$ for which we want to build a linear model.
For the ordinary linear least squares estimator, we determine the parameters $$\theta_i$$ of the linear model by minimizing the sum of squared errors. If we also add an L2 penalty for regularization, we obtain ridge regression, where $$\lambda \geq 0$$ is the regularization parameter. In the following derivation, the penalty includes the intercept $$\theta_0$$ as well as the remaining parameters. Setting $$\lambda=0$$ recovers ordinary least squares:

$$
\begin{align}
E &= \sum_{i=1}^n \big(y^{(i)} - y^{(i)}_*\big)^2 + \lambda \sum_{j=0}^k \theta_j^2 \\
&= \sum_{i=1}^n \big(\theta_0 + \theta_1 \phi_1^{(i)}  + \ldots + \theta_k \phi_k^{(i)} - y^{(i)}_*\big)^2 + \lambda \sum_{j=0}^k \theta_j^2 \label{eq:MSE}
\end{align}
$$

which leads to the well-known equation for ridge regression, provided that the matrix being inverted is nonsingular:

$$
\vec{\theta} = (\mathbf{\Phi}^{\mathsf{T}} \mathbf{\Phi} + \lambda \mathbf{I})^{-1} \mathbf{\Phi}^{\mathsf{T}} \vec{y}_*,
$$

where $$\mathbf{\Phi}$$ is an $$n \times (k+1)$$ matrix:

$$
\begin{align}
\mathbf{\Phi} = \begin{pmatrix}
\big(\vec{\phi}^{(1)}\big)^{\mathsf{T}} \\
\big(\vec{\phi}^{(2)}\big)^{\mathsf{T}} \\
\vdots \\
\big(\vec{\phi}^{(n)}\big)^{\mathsf{T}}
\end{pmatrix}. \label{eq:Phi}
\end{align}
$$

and $$\vec{y}_*$$ is an $$n$$-dimensional vector:

$$
\begin{align}
\vec{y}_* = \begin{pmatrix} y_*^{(1)} \\ y_*^{(2)} \\ \vdots \\ y_*^{(n)} \end{pmatrix}.
\end{align}
$$

### Weighted Least Squares Estimator

Now let us add a tiny change to equation $$\eqref{eq:MSE}$$. We simply introduce a nonnegative weight parameter $$w_i \geq 0$$, with which we can weight the errors of the individual data points (we also add some factors of $$\frac{1}{2}$$ for convenience, which do not change the minimizer):

$$
\begin{align}
E = \frac{1}{2}\sum_{i=1}^n w_i \big(\theta_0 + \theta_1 \phi_1^{(i)}  + \ldots + \theta_k \phi_k^{(i)} - y^{(i)}_*\big)^2 + \frac{1}{2} \lambda \sum_{j=0}^k \theta_j^2
\end{align}
$$

With $$w_i \geq 0$$ and $$\lambda \geq 0$$, the objective is convex, so a zero gradient gives a global minimum. In order to minimize the error $$E$$ defined in the above equation, let us first compute the gradient and set it to zero:

$$
\begin{align}
\frac{\partial E}{\partial \theta_0} &= \sum_{i=1}^n w_i \big(\theta_0 + \theta_1 \phi_1^{(i)}  + \ldots + \theta_k \phi_k^{(i)} - y^{(i)}_*\big) + \lambda \theta_0 = 0\\
\frac{\partial E}{\partial \theta_1} &= \sum_{i=1}^n w_i \big(\theta_0 + \theta_1 \phi_1^{(i)}  + \ldots + \theta_k \phi_k^{(i)} - y^{(i)}_*\big)\phi_1^{(i)} + \lambda \theta_1 = 0\\
\vdots \\
\frac{\partial E}{\partial \theta_k} &= \sum_{i=1}^n w_i \big(\theta_0 + \theta_1 \phi_1^{(i)}  + \ldots + \theta_k \phi_k^{(i)} - y^{(i)}_*\big)\phi_k^{(i)} + \lambda \theta_k = 0\\
\end{align}
$$

Now let us try to vectorize the above equations and bring them into matrix form. First, let us bring all terms with $$-y^{(i)}_*$$ to the other side of the equation:

$$
\begin{align}
\sum_{i=1}^n w_i \big(\theta_0 + \theta_1 \phi_1^{(i)}  + \ldots + \theta_k \phi_k^{(i)} \big) + \lambda \theta_0 &= \sum_{i=1}^n w_i y^{(i)}_*\\
\sum_{i=1}^n w_i \big(\theta_0 + \theta_1 \phi_1^{(i)}  + \ldots + \theta_k \phi_k^{(i)} \big)\phi_1^{(i)} + \lambda \theta_1 &= \sum_{i=1}^n w_i y^{(i)}_* \phi_1^{(i)}\\
\vdots \\
\sum_{i=1}^n w_i \big(\theta_0 + \theta_1 \phi_1^{(i)}  + \ldots + \theta_k \phi_k^{(i)} \big)\phi_k^{(i)} + \lambda \theta_k &= \sum_{i=1}^n w_i y^{(i)}_* \phi_k^{(i)}\\
\end{align}
$$

In the next step, we can specify a vector $$\vec{\theta}$$ as in $$\eqref{eq:theta}$$ and write:

$$
\begin{align}
\begin{bmatrix}
\lambda + \sum_{i=1}^n w_i &  \sum_{i=1}^n w_i \phi_1^{(i)}  & \ldots & \sum_{i=1}^n w_i \phi_k^{(i)} \\
\sum_{i=1}^n w_i \phi_1^{(i)} & \lambda + \sum_{i=1}^n w_i \phi_1^{(i)} \phi_1^{(i)}  & \ldots & \sum_{i=1}^n w_i \phi_k^{(i)} \phi_1^{(i)} \\
\vdots & \vdots & \ddots & \vdots \\
\sum_{i=1}^n w_i \phi_k^{(i)} & \sum_{i=1}^n w_i \phi_1^{(i)} \phi_k^{(i)}  & \ldots & \lambda + \sum_{i=1}^n w_i \phi_k^{(i)} \phi_k^{(i)} \\
\end{bmatrix} \cdot
\begin{bmatrix}
\theta_0 \\
\theta_1 \\
\vdots \\
\theta_k
\end{bmatrix} =
\begin{bmatrix}
\sum_{i=1}^n w_i y^{(i)}_* \\
\sum_{i=1}^n \phi_1^{(i)} w_i y^{(i)}_*  \\
\vdots \\
\sum_{i=1}^n \phi_k^{(i)} w_i y^{(i)}_*
\end{bmatrix} \label{eq:weightedLSMatrix1}
\end{align}
$$

Now, let us again define $$\mathbf{\Phi}$$ in the same way as in $$\eqref{eq:Phi}$$ and introduce an $$n \times n$$ matrix $$\mathbf{W}$$, which contains all weights $$w_i$$ on its diagonal:

$$
\begin{align}
\mathbf{W} =
\begin{bmatrix}
  w_1 & 0 & \ldots & 0 \\
  0 & w_2 & \ldots & 0 \\
  \vdots & \vdots & \ddots & \vdots \\
  0 & 0 & \ldots & w_n
\end{bmatrix}
\end{align}
$$

Comparing the matrix entries, we can now significantly simplify Eq. $$\eqref{eq:weightedLSMatrix1}$$:

$$
\begin{align}
  \big(\mathbf{\Phi}^{\mathsf{T}} \mathbf{W} \mathbf{\Phi} + \lambda \mathbf{I} \big) \vec{\theta} = \mathbf{\Phi}^{\mathsf{T}} \mathbf{W} \vec{y}_*
\end{align}
$$

With the above equation we can finally find the desired parameters of the linear model with weighted squared residuals, provided that $$\mathbf{\Phi}^{\mathsf{T}} \mathbf{W} \mathbf{\Phi} + \lambda \mathbf{I}$$ is invertible. For $$\lambda>0$$, this is guaranteed by the nonnegative weights and our convention of penalizing all parameters. For $$\lambda=0$$, the rows of $$\mathbf{\Phi}$$ with positive weights must span all $$k+1$$ parameter directions; otherwise, the minimizer is not unique and a pseudoinverse can be used to select one. Under the invertibility condition, we obtain:

$$
\begin{align}
  \vec{\theta} = \big(\mathbf{\Phi}^{\mathsf{T}} \mathbf{W} \mathbf{\Phi} + \lambda \mathbf{I} \big)^{-1} \mathbf{\Phi}^{\mathsf{T}} \mathbf{W} \vec{y}_*
\end{align}
$$

Since $$\mathbf{W}$$ is an $$n \times n$$ matrix, in practice we should avoid actually generating this diagonal matrix for large datasets. Instead, for a diagonal $$n \times n$$ weight matrix $$\mathbf{W} = \mbox{diag}(\vec{w})$$ and an $$ (k+1) \times n$$ matrix $$\mathbf{\Psi} = \mathbf{\Phi}^{\mathsf{T}}$$, one could directly use the relation:

$$
\begin{align}
 \mathbf{\Psi} \cdot \mathbf{W} = \mathbf{\Psi} \cdot \mbox{diag}(\vec{w}) =
 \begin{bmatrix}
 w_1 \psi_{1,1} & w_2 \psi_{1,2} & \ldots &w_n \psi_{1,n} \\
 w_1 \psi_{2,1} & w_2 \psi_{2,2} & \ldots &w_n \psi_{2,n} \\
 \vdots & \vdots & \ddots & \vdots \\
 w_1 \psi_{k+1,1} & w_2 \psi_{k+1,2} & \ldots &w_n \psi_{k+1,n} \\
 \end{bmatrix}
\end{align}
$$

Hence, each column simply has to be multiplied by its corresponding weight.

## Example

Let us take a look at a small example: assume we have sampled some data from a stochastic linear function

$$
\begin{align}
f(x) = y(x) + \epsilon(x) = m \cdot x + b + \epsilon(x)
\end{align}
$$

where $$\epsilon(x)$$ is some random noise which we do not know. The data sample could look like this:

{% include figure.liquid
   path="assets/img/2018-03-13-the-weighted-least-squares-algorithm/plot1.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="70%"
   alt="Sampled data points with different spreads around a linear trend."
   caption="A data sample for which we want to fit a linear model." %}

We evaluated each $$x$$ several times and can observe that the noise seems to vary for each value of $$x$$. The linear correlation between the two variables in the plot is quite apparent, although it is not that clear how to fit the line through the data points. For those $$x$$ for which we have a large spread in the observed values, it is difficult to estimate where the line should approximately pass through. Also, outliers might have a large impact on the estimation of the parameters of the linear model. Hence, we can assign weights to each $$x$$ which are higher for those $$x$$ which have a small spread in their values and vice versa. A reasonable weight could be the inverse of the noise variance at each $$x$$ so that we get:

$$
\begin{align}
w_i = \frac{1}{\sigma_{x_i}^2}
\end{align}
$$

where $$\sigma_{x_i}^2$$ is the noise variance at $$x=x_i$$. In the R example, we estimate this variance from the five repeated observations at each $$x$$ and use its reciprocal as the weight for all five observations. Thus, the weights are based on estimated variances rather than the true variances used to generate the data. Both fits use $$\lambda=0$$, so no regularization is applied. Now let us apply both the linear least squares estimator and its weighted version to the collected data and see what happens:

{% include figure.liquid
   path="assets/img/2018-03-13-the-weighted-least-squares-algorithm/plot2.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="70%"
   alt="Unweighted and weighted fitted lines compared with the true line."
   caption="Linear model fits for the dataset. The real curve is represented by the red line. The green line is based on the estimation of the conventional linear least squares estimator and the blue line is the estimate of the weighted linear least squares estimator." %}

As we can see, the estimate of the weighted linear least squares estimator is much closer to the real line than the conventional estimator. Since this might just be a coincidence for this particular dataset, let us repeat the procedure several thousand times. For this, we specify the real line to be

$$
y(x) = x + 2
$$

and set the noise $$\epsilon(x)$$ to be normally distributed with zero mean and a standard deviation $$\sigma_x$$ which is selected randomly with the probabilities $$\mathbb P(\sigma_x=1) = 3/4$$ and $$\mathbb P(\sigma_x=5) = 1/4$$.
In each run, we create a dataset with $$N=55$$ points ($$x\in \{-5,-4, \ldots, 4, 5 \}$$ and 5 points for each $$x$$) and compute the error for the weighted and unweighted linear least squares estimators in the slope $$m$$ and intercept $$b$$. Then we repeat the procedure 10,000 times and sum up the squared errors (SSE) of both estimators for both parameters. The output retained from the original simulation is:

{% highlight R %}
SSE unweighted: b  SSE unweighted: m   SSE weighted: b   SSE weighted: m
          1275.48             124.82            410.00             40.65
{% endhighlight %}

As we can see, for this example, the sum of squared errors of the weighted estimator is about 1/3 of its unweighted counterpart for the intercept $$b$$ and the slope $$m$$. Since both estimators are evaluated over the same 10,000 runs, the ratio of their root mean squared errors (RMSE) is the square root of the corresponding SSE ratio. This gives $$\sqrt{410.00/1275.48} \approx 0.567$$ for the intercept and $$\sqrt{40.65/124.82} \approx 0.571$$ for the slope (approximately $$1/\sqrt{3}$$ in both cases). Finally, let us plot some density estimates for the errors of the two estimators:

{% include figure.liquid
   path="assets/img/2018-03-13-the-weighted-least-squares-algorithm/plot3.png"
   class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="70%"
   alt="Error distributions for the estimated intercept and slope, with 95 percent intervals."
   caption="Density estimates of the errors in the estimations of the intercept $$b$$ and the slope $$m$$ for the unweighted and weighted least squares. The black lines specify the intervals containing 95% of the observed errors." %}

Also, in the above figure, we can see that the weighted estimator generally produces smaller errors, since the curves have sharper spikes around zero. The sources for all reported results can be found in the appendix.

## Appendix

[Download the R source]({{ '/assets/code/2018-03-13-the-weighted-least-squares-algorithm/weightedLSE.R' | relative_url }}).

The table and figures above are retained from the original 2018 post. No random seed is recorded in the original script, so the exact values and sampled points cannot be reproduced from it alone. After loading the script, calling `testWeightedLS(TRUE)` generates a new pair of plots like the first two figures; for a repeatable new run with the same R and package versions, we can call `set.seed(20260920)` before sourcing the script and then make the plotting call. The code below uses `coord_cartesian(xlim = c(-1, 1))` for the density plot so that the full error sample is used when estimating the curves, while only the displayed range is restricted. The historical figures have not been regenerated with this correction.

{% highlight R %}
library(dplyr)
library(reshape2)
library(MASS)
library(ggplot2)

N = 5     # number of points for each x
b = 2     # offset of linear function
m = 1     # slope of the linear function
x = -5:5  # range to generate points for the linear function


testWeightedLS <- function(doPlot = F) {
  # Generate data points around the line with different variances for each x
  data = as.data.frame(t(sapply(x, function(i) c(i, m*i+b + rnorm(n=N, mean = 0, sd = sample(c(1,1,1,5),1))))))
  dataAligned <- melt(data,  variable.name = "key", id.vars = c(1))
  
  # Data used for training the models
  xTrain <- dataAligned[,1]
  yTrain <- dataAligned[,3]
  
  # Estimate the parameters for the unweighted least squares estimator
  thetaNoW = ginv(cbind(1,xTrain)) %*% yTrain
  
  # compute variance for each x
  estVars <- cbind(data[,1], apply(data[,c(2:ncol(data))], 1, var))
  w <- sapply(xTrain, FUN=function(i) estVars[which(estVars[,1] == i),2])
  
  # Weighting matrix W based on the variance for each x
  # n x n matrix! Should be done differently for larger data sets
  W <- diag(1/w)
  
  # Compute the parameters for the weighted least squares estimator
  X = cbind(1,xTrain)
  tXW = t(X) %*% W
  thetaW = ginv( tXW %*% X ) %*% tXW %*% yTrain
  
  if(doPlot) {
    df <- data.frame(x=xTrain, y=yTrain)
    plotDf <- melt(df, id.vars=c("x"))
    cc <- data.frame(sl = c(thetaNoW[2],thetaW[2], m), 
                     int = c(thetaNoW[1],thetaW[1], b), 
                     Estimator = c('unweighted','weighted','real'))
    p<-ggplot(data = plotDf, aes(x=x,y=value)) +
      geom_point() +
      theme_bw(base_size=25) 
    plot(p)
    
    p<-ggplot(data = plotDf, aes(x=x,y=value)) +
        geom_point() +
        theme_bw(base_size=25) +
        geom_abline(data = cc, aes(slope =sl, intercept = int,colour = Estimator))

    plot(p)
        
  }
  
  # Compute error of estimated parameters
  c(thetaNoW - c(b,m), thetaW - c(b,m))
}

runErrs <- t(replicate(10000, testWeightedLS()))
colnames(runErrs) <- c("Error unweighted LSE: b", "Error unweighted LSE: m", "Error weighted LSE: b", "Error weighted LSE: m")
apply((runErrs)^2,2, mean) # Compute the mean squared errors of the estimated parameters
apply((runErrs)^2,2, sum) # Compute the sum of squared errors of the estimated parameters
apply(abs(runErrs),2, sum) # Compute the sum of absolute errors of the estimated parameters

# Prepare data for density estimates
errs_b <- runErrs[,c(1,3)]
colnames(errs_b) <- c("unweighted", "weighted")
histData_b <- data.frame(melt(errs_b)[,-1], param = "b")

errs_m <- runErrs[,c(2,4)]
colnames(errs_m) <- c("unweighted", "weighted")
histData_m <- data.frame(melt(errs_m)[,-1], param = "m")

histData <- rbind(histData_b, histData_m)
colnames(histData) <- c("method", "error", "param")

# Compute 2.5% and 97.5% quantiles
d2 <- histData %>%
  group_by(method, param) %>%
  summarize(lower = quantile(error, probs = .025),
            upper = quantile(error, probs = .975))

# Plot density estimates
ggplot(histData, aes(x = error)) +
  facet_grid(method ~ param) +
  geom_density(aes(colour = method)) + 
  theme_bw(base_size=25) +
  geom_vline(data = d2, aes(xintercept = lower)) +
  geom_vline(data = d2, aes(xintercept = upper)) + 
  coord_cartesian(xlim = c(-1, 1)) +
  theme(legend.position="none")
{% endhighlight %}
