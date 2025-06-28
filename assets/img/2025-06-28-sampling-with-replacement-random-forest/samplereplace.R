# How often do we want to repeat the simulation?
nSimulations <- 100000

runSimulation <- function(n) {
  # Function that draws a sample of size n from a set of n values
  # and returns the fraction of unique values within the sample
  sampleWithRep <- function(n) {
    # sample the set n times with replacement
    p <- sample(1:n, n, replace = T, prob = rep(1/n,n))
    
    # compute the fraction of unique values in this sample
    #length(unique(p)) / n
    #if(length(unique(p)) == n) print(p)
    #browser()
    return (length(unique(p)) == 1)
  }
  
  # Run simulation many times and print the mean value for the 
  # fraction of unique values within all simulated samples
  mean(sapply(rep(n,nSimulations), sampleWithRep))
}

# Sufficiently large set
n <- 5

cat("On average, each sample contained", (runSimulation(n)), 
    "% of the values of the original set.")

# get sequence 1, 2, ..., 9, 10, 20, ..., 90, 100, 200, ..., 900, 1000, ..., 90 000
#Ns <- c(t(1:9) %o% 10^(0:4))

# Run simulation for different n's
#result <- cbind(Ns, sapply(Ns, runSimulation))

#runSimulation(n)
