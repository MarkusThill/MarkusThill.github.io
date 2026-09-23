# Adapted from _posts/2018-02-03-memory-of-an-exponentially-weighted-estimator-of-the-arithmetic-mean-and-covariance-matrix.md.
# This is the Gaussian blog experiment; the thesis PDF uses uniform data.
set.seed(20260412)
lambda <- .99
N_weighted <- 2000L
repetitions <- 5000L
real_mean <- c(1, 3)
real_cov <- matrix(c(3, 1, 1, 2), 2, 2)
raw <- lambda ^ (N_weighted - seq_len(N_weighted))
w <- raw / sum(raw)  # Mean weights; do not use the covariance denominator.
effective_n <- 1 / sum(w^2)
weighted <- t(replicate(repetitions, {
  X <- MASS::mvrnorm(N_weighted, mu = real_mean, Sigma = real_cov)
  colSums(X * w)
}))
pdf('r-estimator-memory.pdf', width = 10, height = 4)
par(mfrow = c(1, 2))
for (size in c(100L, 199L)) {
  ordinary <- t(replicate(repetitions, {
    X <- MASS::mvrnorm(size, mu = real_mean, Sigma = real_cov)
    colMeans(X)
  }))
  dw <- density(weighted[, 1])
  du <- density(ordinary[, 1])
  plot(dw, col = '#177E89', lwd = 2, xlim = range(dw$x, du$x),
       ylim = range(0, dw$y, du$y), main = paste('Compare with n =', size),
       xlab = 'Estimated first mean component')
  lines(du, col = '#D45D45', lwd = 2)
  legend('topright', c('Exponential weights', 'Equal weights'),
         col = c('#177E89', '#D45D45'), lty = 1)
  print(list(size = size, covariance_of_ordinary_means = cov(ordinary),
             covariance_of_weighted_means = cov(weighted)))
}
dev.off()
print(list(finite_effective_size = effective_n,
           predicted_covariance_of_weighted_mean = real_cov / effective_n))
