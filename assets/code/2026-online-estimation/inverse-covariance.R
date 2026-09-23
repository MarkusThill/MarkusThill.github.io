# Adapted from _posts/2018-10-14-online-estimation-of-the-inverse-covariance-matrix.md.
# This explicitly regularized example contrasts with Python's zero-scatter
# warm-up policy. The initial ridge decays once per observation.
set.seed(20260426)
d <- 3L
N <- 500L
lambda <- .99
rho <- .01
Sigma <- matrix(c(1, -1, .5, -1, 3, -1, .5, -1, 3), d, d)
X <- MASS::mvrnorm(N, mu = c(1, 10, 20), Sigma = Sigma)
W <- 0
Q <- 0  # Sum of squared weights, not the square of W.
running_mean <- numeric(d)
M <- rho * diag(d)
P <- diag(d) / rho  # 100 I, the inverse of 0.01 I.
errors <- numeric(N)
for (n in seq_len(N)) {
  W <- lambda * W + 1
  Q <- lambda^2 * Q + 1
  delta <- X[n, ] - running_mean
  running_mean <- running_mean + delta / W
  residual <- X[n, ] - running_mean
  M <- lambda * M + tcrossprod(delta, residual)
  left <- P %*% delta
  right <- t(residual) %*% P
  P <- (P - (left %*% right) / as.numeric(lambda + right %*% delta)) / lambda
  P <- (P + t(P)) / 2
  errors[n] <- norm(P - solve(M), 'F') / norm(solve(M), 'F')
}
raw <- lambda ^ (N - seq_len(N))
reference_mean <- colSums(X * raw) / sum(raw)
residuals <- sweep(X, 2, reference_mean)
data_scatter <- crossprod(residuals, residuals * raw)
reference_M <- data_scatter + lambda^N * rho * diag(d)
stopifnot(isTRUE(all.equal(M, reference_M, tolerance = 1e-9)))
stopifnot(max(errors) < 1e-7)
# Report the covariance and precision of the SAME regularized scatter.
# These are not an unbiased sample covariance / unbiased population precision.
regularized_covariance <- M / W
regularized_precision <- W * P
stopifnot(max(abs(regularized_covariance %*% regularized_precision - diag(d))) < 1e-7)
print(list(maximum_relative_inverse_error = max(errors),
           remaining_scatter_ridge = lambda^N * rho,
           regularized_covariance = regularized_covariance))
pdf('r-inverse-covariance.pdf', width = 7, height = 4)
plot(seq_len(N), pmax(errors, .Machine$double.eps), type = 'l', log = 'y',
     xlab = 'Observations', ylab = 'Relative inverse error')
dev.off()
