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
