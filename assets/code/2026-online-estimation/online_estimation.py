"""NumPy examples for the thesis/blog merge, derived from Appendix B.2.

The API follows the ideas in assets/mahalanobis.py and notebook cells 3/9.
The corrected destination notebook embeds this same self-contained implementation.
Decay is applied once per update call. Observations are rows of a batch.
"""

import numpy as np


class IncrementalMoments:
    """Weighted mean/scatter with optional Woodbury inverse updates.

    Start with exact zero scatter. The inverse is unavailable until the scatter
    is positive definite and sufficiently well conditioned. At that point a
    direct solve initializes it; subsequent updates use the thesis's identity.
    No hidden ridge term is added. This is an educational NumPy implementation;
    long-running applications should monitor conditioning and roundoff.
    """

    def __init__(self, dim, decay=1.0, track_inverse=False):
        if not isinstance(dim, int) or dim < 1:
            raise ValueError("dim must be a positive integer")
        if not np.isfinite(decay) or not 0 < decay <= 1:
            raise ValueError("decay must be in (0, 1]")
        self.dim = dim
        self.decay = float(decay)
        self.track_inverse = track_inverse
        self.weight = 0.0
        self.weight_squared_sum = 0.0
        self.mean = np.zeros(dim)
        self.scatter = np.zeros((dim, dim))
        self.scatter_inverse = None
        self.positive_observations = 0

    def update(self, batch, weights=None, decay=None):
        """Apply a batch, optionally overriding its decay and incoming weights.

        For exact equivalence to per-observation forgetting at rate r, pass
        decay=r**len(batch) and weights=r**arange(len(batch)-1, -1, -1).
        Default unit weights instead implement the thesis's equal-weight batch.
        """
        batch = np.asarray(batch, dtype=float)
        if batch.ndim == 1:
            batch = batch.reshape(1, -1)
        if batch.ndim != 2 or batch.shape[1] != self.dim or len(batch) == 0:
            raise ValueError("batch must be nonempty with shape (n, dim)")
        if not np.isfinite(batch).all():
            raise ValueError("observations must be finite")
        b = len(batch)
        weights = np.ones(b) if weights is None else np.asarray(weights, dtype=float)
        if (weights.shape != (b,) or not np.isfinite(weights).all()
                or np.any(weights < 0) or not weights.sum() > 0):
            raise ValueError("weights must be finite, nonnegative, and have positive sum")
        decay = self.decay if decay is None else float(decay)
        if not np.isfinite(decay) or not 0 < decay <= 1:
            raise ValueError("decay must be in (0, 1]")

        self.weight = decay * self.weight + weights.sum()
        self.weight_squared_sum = decay**2 * self.weight_squared_sum + weights @ weights
        delta = batch - self.mean
        self.mean = self.mean + (weights @ delta) / self.weight
        residual = batch - self.mean
        weighted_residual = weights[:, None] * residual
        self.scatter = decay * self.scatter + delta.T @ weighted_residual
        self.scatter = (self.scatter + self.scatter.T) / 2
        self.positive_observations += np.count_nonzero(weights)

        if self.track_inverse:
            if self.scatter_inverse is None:
                self.refactor_inverse()
            else:
                # Parenthesize to avoid an unnecessary dim-by-dim multiplication.
                p = self.scatter_inverse
                left = p @ delta.T
                right = weighted_residual @ p
                middle = decay * np.eye(b) + weighted_residual @ left
                p = (p - left @ np.linalg.solve(middle, right)) / decay
                self.scatter_inverse = (p + p.T) / 2
        return self

    def refactor_inverse(self):
        """Initialize/recompute an inverse when the data support one.

        The condition limit is a declared numerical policy for these examples,
        not a claim that every invertible matrix below it is equally accurate.
        """
        self.scatter_inverse = None
        if self.positive_observations <= self.dim:
            return
        try:
            np.linalg.cholesky(self.scatter)
            if np.linalg.cond(self.scatter) <= 1e10:
                p = np.linalg.solve(self.scatter, np.eye(self.dim))
                self.scatter_inverse = (p + p.T) / 2
        except np.linalg.LinAlgError:
            pass

    def denominator(self, unbiased=True):
        if self.weight <= 0:
            raise ValueError("no observations yet")
        d = (self.weight - self.weight_squared_sum / self.weight
             if unbiased else self.weight)
        if d <= 0:
            raise ValueError("an unbiased covariance requires more than one positive weight")
        return d

    def covariance(self, unbiased=True):
        """Reliability-weight correction assumes fixed weights and IID data."""
        return self.scatter / self.denominator(unbiased)

    def precision(self, unbiased=True):
        """Inverse of the chosen covariance estimate; not an unbiased precision."""
        if self.scatter_inverse is None:
            raise ValueError("scatter inverse unavailable: insufficient rank or conditioning")
        return self.denominator(unbiased) * self.scatter_inverse

    def effective_sample_size(self):
        if self.weight_squared_sum <= 0:
            raise ValueError("no observations yet")
        return self.weight**2 / self.weight_squared_sum


def direct_moments(data, weights):
    """Independent two-pass reference over all observations, for validation."""
    data = np.asarray(data, dtype=float)
    weights = np.asarray(weights, dtype=float)
    mean = np.average(data, axis=0, weights=weights)
    residual = data - mean
    scatter = residual.T @ (weights[:, None] * residual)
    return mean, scatter
