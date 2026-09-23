# Adapted from _posts/2017-11-20-online-estimation-of-gaussians.md.
# Seeded experiment, not a pixel-identical recreation of the historical PNG.
# Run from this directory: Rscript online-mean-covariance.R
set.seed(20260215)
mu <- c(1, 10, 20)
Sigma <- matrix(c(1, -1, .5, -1, 3, -1, .5, -1, 3), 3, 3)
X <- MASS::mvrnorm(n = 1000, mu = mu, Sigma = Sigma)
running_mean <- numeric(3)
scatter <- matrix(0, 3, 3)
means <- matrix(NA_real_, nrow(X), 3)
variances <- matrix(NA_real_, nrow(X), 3)
for (n in seq_len(nrow(X))) {
  delta <- X[n, ] - running_mean
  running_mean <- running_mean + delta / n
  scatter <- scatter + tcrossprod(delta, X[n, ] - running_mean)
  means[n, ] <- running_mean
  # Unbiased sample covariance is undefined for n = 1.
  if (n > 1) variances[n, ] <- diag(scatter / (n - 1))
}
stopifnot(isTRUE(all.equal(running_mean, colMeans(X), tolerance = 1e-10)))
stopifnot(isTRUE(all.equal(scatter / (nrow(X) - 1), cov(X), tolerance = 1e-10)))
pdf('r-online-mean-covariance.pdf', width = 10, height = 4)
par(mfrow = c(1, 2))
matplot(means, type = 'l', lty = 1, xlab = 'Observations', ylab = 'Estimated mean')
abline(h = mu, col = 1:3, lty = 2)
matplot(variances, type = 'l', lty = 1, xlab = 'Observations', ylab = 'Unbiased variance')
abline(h = diag(Sigma), col = 1:3, lty = 2)
dev.off()
print(running_mean)
print(scatter / (nrow(X) - 1))
