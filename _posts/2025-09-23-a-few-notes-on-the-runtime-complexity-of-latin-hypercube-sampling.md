---
layout: post
title: "Notes on the Runtime Complexity of Latin Hypercube Sampling"
modified:
categories: [programming, math]
description: "Exploring the runtime complexity of the Latin Hypercube Sampling (LHS) algorithm, this post investigates how computation time scales with the number of design points. By measuring runtimes, applying log-log transformations, and using weighted linear regression, we estimate the polynomial order of growth and provide practical insights into the expected performance of LHS for larger datasets."
tags: [math]

thumbnail: assets/img/2025-09-23-a-few-notes-on-the-runtime-complexity-of-latin-hypercube-sampling/thumbail.png
giscus_comments: true
toc:
  beginning: true
share: true
date: 2025-09-24T20:00:51+01:00
pretty_table: false
related_posts: true
tabs: true
images:
  compare: false
  slider: false
---


\\(   
  \def\myT{\mathsf{T}}
  \def\myPhi{\mathbf{\Phi}}
\\)

Recently, I needed to tune several parameters of a simple algorithm (five in total). To efficiently explore the parameter space, I chose to use a **Latin Hypercube Sampling (LHS)** design. Because each design point could be evaluated very quickly, selecting **1,000 design points** seemed reasonable.  

In **R**, the `lhs` package provides a convenient function, `optimumLHS`, to generate such designs. However, when attempting to generate \(n = 1000\) points, the function failed to return even after several minutes. This behavior highlights an important issue: **the runtime complexity of the LHS algorithm**.  

To better understand this, I measured the runtime of LHS for different numbers of design points. The following R code illustrates how these measurements were obtained:


{% highlight R %}
library(lhs)
library(ggplot2)
library(MASS)
library(dplyr)
library(pbapply)

runLHS <- function(whichN, repeats){
  lhsTimes <- data.frame()
  for(i in whichN){
    for(j in 1:repeats) {
      tStart <- proc.time()
      invisible(optimumLHS(n = i, k = 5, verbose = FALSE))
      tt <- (proc.time() - tStart)
      lhsTimes<-rbind(lhsTimes,data.frame(user=tt[1], system=tt[2], elapsed=tt[3], n=i))
    }
  }
  return (lhsTimes)
}


res <- pblapply(X=rev(1:30)*10, FUN=runLHS, 10, cl=1)
res <- do.call(rbind, res)
# saveRDS(object=res, file="lhs.rds") # In case you want to save the results
# res <- readRDS(file="lhs.rds") # In case you want to load the results
stop("Stop here for the moment")

plotData <- res[which(res$elapsed>.01),] # smaller values are not really interesting
p <- ggplot(plotData,aes(x=n,y=user)) + geom_point()
p <- p + theme_bw()
p <- p + ylab("computation time / s") +
  theme(axis.text=element_text(size=12),
        axis.title=element_text(size=14, face="bold"))
plot(p)
{% endhighlight %}
<hr> <!---* -->

The corresponding plot is shown below:

{% include figure.liquid loading="eager" path="assets/img/2025-09-23-a-few-notes-on-the-runtime-complexity-of-latin-hypercube-sampling/initialplot.png" class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="70%"
caption="Computation time of the LHS algorithm for different numbers of design points $$n$$. For each $$n$$ we ran LHS 10 times and measured the times. Each design point is a 5-dimensional vector." %}

At first glance, the runtime appears to grow at least polynomially, and it could even suggest exponential growth. To investigate this further, we add a logarithmic scale to the y-axis:

{% include figure.liquid loading="eager" path="assets/img/2025-09-23-a-few-notes-on-the-runtime-complexity-of-latin-hypercube-sampling/log_y_scalePlot.png" class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="70%"
caption="Same as before, but with a log10 scale on the y-axis. From this view, the runtime growth does not appear exponential." %}

If the runtime were exponential, the log-scaled y-axis would produce a straight line. Since this is not the case, a polynomial growth seems more likely. To confirm, we also apply a log10 scale to the x-axis:

{% include figure.liquid loading="eager" path="assets/img/2025-09-23-a-few-notes-on-the-runtime-complexity-of-latin-hypercube-sampling/logxyPlot.png" class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="70%"
caption="Same as Fig. 1, but with log10 scales on both axes. The resulting straight line suggests that the runtime complexity of LHS is polynomial." %}


Since we now observe a straight line on the log-log plot, it is reasonable to conclude that the runtime of the LHS algorithm grows polynomially. Next, it is interesting to determine the order of this polynomial. To do so, we estimate the slope and intercept of the line using linear regression. 

Because we have 10 measurements for each value of $$n$$, we can employ a weighted linear regression approach to account for variations in the observed runtimes.


$$
\begin{align}
  \vec{\theta} = \big(\myPhi^\myT \mathbf{W} \myPhi + \lambda \mathbf{I} \big)^{-1} \myPhi^\myT \mathbf{W} \vec{y}_*
\end{align}
$$

with

$$\mathbf{W} = \mbox{diag}(\vec{w})$$

and

$$
\begin{align}
w_i = \frac{1}{\sigma_{x_i}^2}.
\end{align}
$$

The R code for estimating the Intercept $$b$$ and the slope $$m$$ of the line is as follows:

{% highlight R %}
# Apply log10 to the data
log_n = log10(plotData$n)
log_y = log10(plotData$user)
log_data <- data.frame(log_n, log_y)

#
# Since we repeated each run several times: Measure the variance for each point n
#
grouped <- group_by(cbind(data.frame(log_n=log_n), data.frame(log_y=log_y)), log_n)
stats <- summarise(grouped, mean=mean(log_y), var=var(log_y))

# Now assign the corresponding variance to each data-point again
mergedData <- merge(log_data, stats)

# Prepare the vectors and matrices for the weighted linear least squares estimator
W = diag(1.0 / mergedData$var)
X = cbind(1,mergedData$log_n)
y = mergedData$log_y

# Estimate the Intercept and Slope using weighted linear least squares
theta = ginv(t(X) %*% W %*% X) %*% t(X) %*% W %*% y
cat("slope m=", theta[2], ". Intercept b=", theta[1], sep="")

# Plot the estimated line
p <- ggplot(plotData,aes(x=n,y=user)) +
  geom_point() +
  scale_y_log10() +
  scale_x_log10() +
  geom_abline(slope=theta[2], intercept = theta[1]) +
  theme_bw() +
  ylab("computation time / s") +
  theme(axis.text=element_text(size=12),
        axis.title=element_text(size=14,face="bold"))
plot(p)
{% endhighlight %}
<hr> <!---* -->

The estimator computes the following values for the slope and the intercept:

{% highlight R %}
Slope m=3.993954. Intercept b=-7.875513
{% endhighlight %}
<!---* -->

The fitted line aligns closely with the data, as illustrated in the plot below:

{% include figure.liquid loading="eager" path="assets/img/2025-09-23-a-few-notes-on-the-runtime-complexity-of-latin-hypercube-sampling/logXYfitPlot.png" class="img-fluid rounded z-depth-1 imgcenter" zoomable=true width="70%"
caption="Computation time of the LHS algorithm for different numbers of design points $$n$$, shown on a log10 scale for both axes. A fitted line through all points helps estimate the runtime complexity of LHS." %}

Using the estimated slope and intercept, we can now express the expected runtime of the LHS algorithm as a function of the number of design points $$n$$:


$$
\begin{align}
\log_{10} y &= m \log_{10} n + b \\
f(n) = y &= 10 ^{m \log_{10} n + b} \\
  &= \big(10^{\log_{10} n} \big)^m \cdot 10^b \\
  &= 10^b \cdot n^m \\
  &= 10^{-7.8755} \cdot n^{3.9939} \\
  &\approx 10^{-7.8} \cdot n^{4}
\end{align}
$$

The estimated runtime from the fitted line is slightly pessimistic, so in practice the actual computation time (at least on my machine) is likely a bit lower. Extrapolating this estimate to $$n=1000$$, we would expect a runtime of approximately 16,000 seconds, or about 4.5 hours. 

In summary, we can conclude that the LHS algorithm exhibits a runtime complexity of order $$\mathcal{O}(n^4)$$.
