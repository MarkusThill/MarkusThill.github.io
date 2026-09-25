

require(MASS)
require(R6)
library(quantreg)

RLSModel <- R6Class(
  classname = "RLSModel",
  inherit = IModel,
  portable = TRUE,
  private = list(
    rlsPredictions = NaN,
    myThreshold = NaN,
    offset = 0,
    rls.step = NaN,
    MU = 0.9999, #only makes sense if also the means and the SDs of the distribution are scaled
    useForgettingDistri=NaN,
    TRANSIENT = 20,
    tCounter=0,
    deltaT=0.0
  ),
  public = list(
    #
    # Parameters of the linear model
    #
    train_err = 0,
    train_absErr = 0,
    mu_err = 0,
    sd_err = 0,
    M = 0,
    n = 1,
    sdFac = 1,
    Sum = 0,
    #
    # Constructor
    #
    initialize = function(data, myThreshold, forgetting, useForgettingDistri) {
      private$myThreshold <- myThreshold
      private$MU <- forgetting
      private$useForgettingDistri <- useForgettingDistri
#       X <- data$X$getMatrix()[1:20,]
#       y <- data$y[1:20,]
#       
#       N <- ncol(X)
#       I <- diag(ncol(X))
#       I[1,1] = 0 # We do not regularize the bias
#       thetaFit <- ginv(t(X) %*% X + (1e-6 * I)) %*%  t(X) %*% y
#       
#       t <- thetaFit #as.matrix(numeric(N)+ 1/N) 
      #browser()
      N <- ncol(data$X$getMatrix())
      powOf2 <- rev(2^-c(1:(N-1)))
      t <- matrix(c(0, powOf2))
      P <- 5000*diag(N)
      #
      # How to init the weights? Maybe as 1/N (averaging) 
      #
      private$rls.step <- list(t,P)
      
      #
      # 1/2 + 1/4 + 1/8 +....
      #
      #browser()
     # X <- data$X$getMatrix()
     # y <- data$y
     # theta <- t(lm.fit.recursive(X=X, y=y, int=F))
      
      #y_p <- rep(0,nrow(X))
     # y_p <- matrix(y_p, nrow = length(y_p))
     # for(i in 1:nrow(X)) {
     #   y_p[i,1] = X[i,] %*% as.matrix(theta[i,])
     # }
      
     # private$rlsPredictions = list(X = X, y_p = y_p)
      
      
#       #
#       # Test
#       #
#       rls<-function(x,y,t,P,mu=1){
#         P.new <-(P-(P%*%x%*%x%*%P)/as.numeric(mu+x%*%P%*%x))/mu
#         ga <- P.new%*%x
#         epsi <- y-x%*%t
#         t.new<-t+ga*as.numeric(epsi)
#         list(t.new,P.new)
#       }
#       
#       n <- 5
#       N = nrow(X)
#       t<-as.matrix(numeric(n+1))
#       P<-1*diag(n+1)
#       mu<-1.0
#       y_pp <- rep(0,nrow(X))
#       y_pp <- matrix(y_p, nrow = length(y_p))
#       for (i in 1:N){
#         y_pp[i,1] <- X[i,]%*%t
#         rls.step <- rls(X[i,],y[i,1],t,P,mu)
#         t<-rls.step[[1]]
#         P<-rls.step[[2]]
        
        #plot(X[1:i],y[1:i],
        #     xlim=c(-4,4),
        #     ylim=c(-2,2),
        #     main=paste("Forgetting factor mu<-",mu))
        
        #lines(X[1:i],cbind(array(1,c(i,1)), X[1:i])%*%t,
        #      col="red",
        #) 
     # }
      #browser()
      
    },
    #
    # Train on new data
    #
    train = function(trainData, CVData) {
    },
    predict = function(x, t) {
      #browser()
      #library(prodlim)
      #i <- row.match(x[1,], private$rlsPredictions[["X"]])
      #i <- which(apply(private$rlsPredictions[["X"]], 1, function(p) all(p %in% x)) )
      
      #i <- which(private$rlsPredictions[["X"]] %in% x)
      #
      # If more than one match, take the largest index at the moment...
      #
      #if(t == 1244) browser()
      #i <- t + private$offset
      #if(!all(x[1,]==private$rlsPredictions[["X"]][i,])) { 
        #browser()
       # off <- row.match(x[1,], private$rlsPredictions[["X"]]) - t
       # private$offset <- off#if(is.na(off)) private$offset + 10 else off
      #}
      #i <- t + private$offset
      #y <- private$rlsPredictions[["y_p"]][i,1]
      
      
      t<-private$rls.step[[1]]
      #y_pp <- rep(0,nrow(X))
      #y_pp <- matrix(y_p, nrow = length(y_p))
      #for (i in 1:N){
      y <- x%*%t
      ##
      # Actually, we are not allowed to update, if we have an anomaly...
      #
      #private$rls.step <- rls(c(x),y,t,P,private$MU)
        
        
        #plot(X[1:i],y[1:i],
        #     xlim=c(-4,4),
        #     ylim=c(-2,2),
        #     main=paste("Forgetting factor mu<-",mu))
        
        #lines(X[1:i],cbind(array(1,c(i,1)), X[1:i])%*%t,
        #      col="red",
        #) 
      #}
      return (y)
    },
    rls = function(x,y,t,P,mu=1){
      epsi <- y - x %*% t
      P.new <-(P-(P%*%x%*%x%*%P)/as.numeric(mu+x%*%P%*%x))/mu
      ga <- P.new %*% x
      private$deltaT <- private$deltaT + ga * as.numeric(epsi)
      t.new <- t + if(private$tCounter>private$TRANSIENT) private$deltaT else 0
      private$tCounter <- private$tCounter + 1
      if(private$tCounter>private$TRANSIENT) private$deltaT <- 0.0
      list(t.new, P.new)
    },
    update = function(delta,x,y) {
      
      t<-private$rls.step[[1]]
      P<-private$rls.step[[2]]
      
      private$rls.step <- self$rls(c(x),y,t,P,private$MU)
      
      #
      # Estimate distribution
      #
      # myLen <- min(length(self$train_err), 100)
      # ll <- length(self$train_err)
      # qq <- max((ll-myLen),0)
      # mean(self$train_err[qq:ll])
      #browser()
      self$train_err <- append(x = self$train_err, values = delta)
      testMu <-  mean(self$train_err)
      testSD <- sd(self$train_err)
      #self$mu_err <- mean(self$train_err)
      #self$sd_err <- sd(self$train_err)
      #browser()
      #deltaMu <- delta - self$mu_err
      #self$mu_err <- self$mu_err + deltaMu / length(self$train_err)
      #self$M <- self$M + deltaMu * (delta - self$mu_err)
      #self$sd_err <- self$M / length(self$train_err)
      #alpha <- 0.99
      #diff <- delta - self$mu_err
      #incr <- alpha * diff
      #self$mu_err <- self$mu_err + incr
      #variance <- self$sd_err^2
      #variance <- (1 - alpha) * (variance + diff * incr)
      #self$sd_err <- sqrt(variance)
      
      # forget = 0.99
      # self$n = self$n + 1
      # mydelta = delta - self$mu_err
      # self$mu_err = self$mu_err + mydelta/self$n
      # mydelta2 = delta - self$mu_err
      # self$M = self$M + abs(mydelta*mydelta2)
      # if(self$n >= 2) self$sd_err <- sqrt(self$M / (self$n-1))
      
      q <- if(private$useForgettingDistri) private$MU else 1.0
      self$n = self$n + 1
      self$sdFac <- q*self$sdFac+1
      mydelta = delta - self$mu_err
      self$Sum <- q*self$Sum + delta#q^2*self$Sum + q^2 
      myTestMu <- self$Sum / self$sdFac
      self$mu_err = self$mu_err + mydelta/(q * self$n - q + 1)
      mydelta2 = delta - self$mu_err
      self$M = q*self$M + mydelta*mydelta2
      #cat("Correct:", myTestMu, " Approx.: ",self$mu_err, "\n")
      #MYERRORS <<- c(MYERRORS, (myTestMu-self$mu_err)^2)
      if(self$n >= 2) self$sd_err <- sqrt(self$M / self$sdFac)

      #     q <- if(private$useForgettingDistri) private$MU else 1.0
      #     
      #     self$sdFac <- q*self$sdFac+1
      #     mydelta = delta - self$mu_err
      #     self$Sum = q*self$Sum + delta
      #     self$mu_err = (self$Sum)/(self$sdFac+1) # + mydelta/self$sdFac#(q * self$n + 1)
      # 
      #     mydelta2 = delta - self$mu_err
      #     self$M = q*self$M + mydelta*mydelta2
      # 
      #     if(self$n >= 2) self$sd_err <- sqrt(self$M / (self$sdFac-1))
      #     self$n = self$n + 1
      #     
      # }

      #self$mu_err <- mean(self$train_err)
      #self$sd_err <- sd(self$train_err)
      
      myMean <- self$mu_err
      mySD <- self$sd_err
      p <- private$myThreshold
      #browser()
      if(length(self$train_err) < private$TRANSIENT) {
        private$lowerThres <- -Inf
        private$upperThres <- +Inf
      } else {
        #if(!is.nan(myMean) & is.numeric(myMean) & mySD > 0.1) {
          private$lowerThres <- qnorm(p, mean = myMean, sd = mySD)
          private$upperThres <- qnorm(p, mean = myMean, sd = mySD, lower.tail = F)
       # }
      }
    }
  ), # End public
  #
  # Active bindings. Can be accessed like fields, although a function is called internally.
  #
  active = list(
    summary = function() {
      #
      # Make a density plot of the training error
      # TODO: Make density plot nicer...
      #
      df <- data.frame(self$train_err)
      base <- ggplot(df, aes(self$train_err)) + geom_density()
      base <- base + stat_function(fun = dnorm, colour = "red", args = list(mean = self$mu_err, sd = self$sd_err))
      ret <- list()
      ret[["trainErr"]] <- self$train_err
      self$train_absErr <- abs(self$train_err)
      ret[["trainAbsErr"]] <- self$train_absErr
      ret[["thetaFit"]] <- self$thetaFit
      ret[["bestLambda"]] <- self$bestlambda
      ret[["trainErrPlot"]] <- base
      return (ret)
    },
    getTrainErrs = function() {
      return (self$train_err)
    }
  )
  
  
)