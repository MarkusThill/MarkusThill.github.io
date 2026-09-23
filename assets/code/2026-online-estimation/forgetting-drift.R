# Adapted from the drift example in the 2018-02-03 estimator-memory post.
# Historical figure: images/2018-01-13-online-estimation-of-weighted-sample-mean-and-coviarance-matrix/forgetting.png
# Here the mean jumps by 2; the old embedded code used 5. Separate offset
# streams reproduce the illustration's intent, not its unrecorded random seed.
set.seed(20260315)
factors <- c(.9, .99, .999, 1)
N <- 10000L
traces <- matrix(0, N, length(factors))
for (j in seq_along(factors)) {
  baseline <- 3 * (j - 1)
  X <- rnorm(N, baseline, 1)
  X[5001:N] <- X[5001:N] + 2
  W <- 0
  running_mean <- 0
  for (n in seq_len(N)) {
    W <- factors[j] * W + 1
    running_mean <- running_mean + (X[n] - running_mean) / W
    traces[n, j] <- running_mean
  }
}
pdf('r-forgetting-drift.pdf', width = 9, height = 5)
matplot(traces, type = 'l', lty = 1, xlab = 'Observations', ylab = 'Estimated mean')
abline(v = 5000.5, lty = 2)
legend('topleft', legend = paste('lambda =', factors), col = seq_along(factors), lty = 1)
dev.off()
