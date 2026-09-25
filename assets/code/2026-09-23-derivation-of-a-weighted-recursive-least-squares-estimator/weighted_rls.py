"""Weighted recursive least squares (RLS) with exponential forgetting.

Reference implementation for the blog post "Derivation of a Weighted Recursive
Linear Least Squares Estimator". The companion notebook develops this class
step by step, starting from the equations derived in the post.
"""
from typing import Optional, Tuple

import numpy as np
from numpy.typing import ArrayLike, NDArray


class WeightedRLS:
    """Weighted recursive least squares with exponential forgetting.

    Fits the linear model ``Y ≈ X @ theta`` and refines the coefficients
    whenever new observations arrive, using the batch equations of the blog
    post. Each call of :meth:`update` processes a batch of ``mu >= 1``
    observations (the rows of ``X``) with optional positive weights, for one or
    several outputs (the columns of ``Y``).

    Attributes:
        n_features: Number of entries k of an input vector.
        n_outputs: Number of outputs m.
        forgetting: Forgetting factor lambda in (0, 1].
        ridge: Initial regularization coefficient rho > 0.
        theta: Current coefficients, shape (n_features, n_outputs).
        A_inv: Current inverse of the regularized, weighted normal matrix,
            shape (n_features, n_features).
        n_seen: Number of observations processed so far.

    Example:
        >>> rng = np.random.default_rng(0)
        >>> X = np.column_stack([np.ones(100), rng.uniform(-1, 1, 100)])
        >>> y = X @ [2.0, -1.0] + 0.01 * rng.normal(size=100)
        >>> rls = WeightedRLS(n_features=2, ridge=1e-3)
        >>> errors = rls.fit(X, y, batch_size=10)
        >>> rls.theta.round(2).ravel()
        array([ 2., -1.])
        >>> rls.predict([1.0, 0.5]).round(2)
        array([[1.5]])
    """

    def __init__(self, n_features: int, n_outputs: int = 1,
                 forgetting: float = 1.0, ridge: float = 1.0) -> None:
        """Initializes the estimator with theta = 0 and A_inv = I / ridge.

        Args:
            n_features: Number of entries k of an input vector. If the model
                needs an intercept, add a column of ones to the inputs.
            n_outputs: Number of outputs m.
            forgetting: Forgetting factor lambda in (0, 1]. With 1, all
                observations keep their weight. With a smaller value, the
                weights of all earlier batches are multiplied by lambda in
                every update except the first one.
            ridge: Initial regularization coefficient rho > 0, i.e.
                A_0 = rho * I. With forgetting, it decays together with the
                old observations.

        Raises:
            ValueError: If an argument is outside its valid range.
        """
        if n_features < 1 or n_outputs < 1:
            raise ValueError("n_features and n_outputs must be at least 1")
        if not 0.0 < forgetting <= 1.0:
            raise ValueError("forgetting must be in (0, 1]")
        if not ridge > 0.0:
            raise ValueError("ridge must be positive")
        self.n_features = n_features
        self.n_outputs = n_outputs
        self.forgetting = forgetting
        self.ridge = ridge
        self.reset()

    def reset(self) -> None:
        """Forgets all observations: sets theta = 0 and A_inv = I / ridge."""
        self.theta: NDArray[np.float64] = np.zeros((self.n_features, self.n_outputs))
        self.A_inv: NDArray[np.float64] = np.eye(self.n_features) / self.ridge
        self.n_seen = 0

    def update(self, X: ArrayLike, Y: ArrayLike,
               weights: Optional[ArrayLike] = None) -> NDArray[np.float64]:
        """Learns from one batch of observations.

        Args:
            X: Input vectors as rows, shape (mu, n_features). A 1-D array is
                interpreted as a single observation.
            Y: Targets, shape (mu, n_outputs). For a single output, shape (mu,)
                is accepted as well, and for a single observation, shape
                (n_outputs,) or a scalar.
            weights: Positive observation weights, shape (mu,), i.e. the
                diagonal of W_mu. Defaults to all ones.

        Returns:
            The prediction errors ``Y - X @ theta``, shape (mu, n_outputs),
            computed with the coefficients from *before* the update.

        Raises:
            ValueError: If the batch has the wrong shape, contains NaN or
                infinite values, or has non-positive weights.
        """
        X_mu, Y_mu, w_mu = self._check_batch(X, Y, weights)
        lam_n = 1.0 if self.n_seen == 0 else self.forgetting   # lambda_0 = 1: nothing to forget yet

        E_mu = Y_mu - X_mu @ self.theta                          # prediction errors E_mu, shape (mu, m)
        XA = X_mu @ self.A_inv                                   # X_mu A_n^{-1}, shape (mu, k), used three times
        S = lam_n * np.diag(1.0 / w_mu) + XA @ X_mu.T            # lambda_n W_mu^{-1} + X_mu A_n^{-1} X_mu^T, (mu, mu)
        # solve(S, XA) computes S^{-1} X_mu A_n^{-1} without inverting S explicitly. Because S
        # and A^{-1} are symmetric, its transpose is the gain Delta_mu = A_n^{-1} X_mu^T S^{-1}.
        Delta_mu = np.linalg.solve(S, XA).T                      # gain matrix, shape (k, mu)
        self.theta = self.theta + Delta_mu @ E_mu                # Theta_{n+mu} = Theta_n + Delta_mu E_mu
        A_inv = (self.A_inv - Delta_mu @ XA) / lam_n             # A_{n+mu}^{-1}
        self.A_inv = 0.5 * (A_inv + A_inv.T)                     # keep A^{-1} exactly symmetric
        self.n_seen += len(X_mu)
        return E_mu

    def fit(self, X: ArrayLike, Y: ArrayLike, batch_size: int = 1,
            weights: Optional[ArrayLike] = None) -> NDArray[np.float64]:
        """Processes a whole data set in consecutive batches.

        The fit continues from the current state; call :meth:`reset` first to
        start from scratch.

        Args:
            X: Input vectors as rows, shape (n, n_features).
            Y: Targets, shape (n, n_outputs), or (n,) for a single output.
            batch_size: Number of rows per batch. The last batch may be
                smaller.
            weights: Positive observation weights, shape (n,). Defaults to
                all ones.

        Returns:
            The prediction errors of all rows, shape (n, n_outputs), each
            computed before its batch was learned.
        """
        X = np.asarray(X, dtype=float)
        Y = np.asarray(Y, dtype=float)
        w = np.ones(len(X)) if weights is None else np.asarray(weights, dtype=float)
        # rows i, ..., i + batch_size - 1 form one batch; slicing stops at the end of the data
        errors = [self.update(X[i:i + batch_size], Y[i:i + batch_size], w[i:i + batch_size])
                  for i in range(0, len(X), batch_size)]
        return np.vstack(errors) if errors else np.empty((0, self.n_outputs))

    def predict(self, X: ArrayLike) -> NDArray[np.float64]:
        """Predicts the targets of the given inputs with the current coefficients.

        Args:
            X: Input vectors as rows, shape (n, n_features), or a single input
                vector of shape (n_features,).

        Returns:
            The predictions ``X @ theta``, shape (n, n_outputs).

        Raises:
            ValueError: If X does not have n_features columns.
        """
        X = np.atleast_2d(np.asarray(X, dtype=float))          # a single vector becomes one row
        if X.shape[1] != self.n_features:
            raise ValueError(f"X must have {self.n_features} columns")
        return X @ self.theta

    def _check_batch(self, X: ArrayLike, Y: ArrayLike, weights: Optional[ArrayLike]
                     ) -> Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
        """Brings a batch into standard shapes and validates it.

        Args:
            X: Input vectors, as described in :meth:`update`.
            Y: Targets, as described in :meth:`update`.
            weights: Observation weights or None, as described in :meth:`update`.

        Returns:
            A tuple ``(X_mu, Y_mu, w_mu)`` with the shapes (mu, k), (mu, m)
            and (mu,).

        Raises:
            ValueError: If the batch has the wrong shape, contains NaN or
                infinite values, or has non-positive weights.
        """
        X_mu = np.atleast_2d(np.asarray(X, dtype=float))       # a single vector becomes one row
        mu = X_mu.shape[0]
        Y_mu = np.asarray(Y, dtype=float)
        if Y_mu.ndim == 0 or (Y_mu.ndim == 1 and self.n_outputs == 1):
            Y_mu = Y_mu.reshape(-1, 1)           # scalar, or the mu targets of a single output
        elif Y_mu.ndim == 1 and mu == 1:
            Y_mu = Y_mu.reshape(1, -1)           # the m targets of a single observation
        w_mu = np.ones(mu) if weights is None else np.asarray(weights, dtype=float).reshape(-1)
        if X_mu.ndim != 2 or X_mu.shape[1] != self.n_features:
            raise ValueError(f"X must have shape (mu, {self.n_features})")
        if Y_mu.shape != (mu, self.n_outputs):
            raise ValueError(f"Y must have shape ({mu}, {self.n_outputs})")
        if w_mu.shape != (mu,) or np.any(w_mu <= 0):
            raise ValueError(f"weights must contain {mu} positive values")
        if not (np.isfinite(X_mu).all() and np.isfinite(Y_mu).all() and np.isfinite(w_mu).all()):
            raise ValueError("the batch must not contain NaN or infinite values")
        return X_mu, Y_mu, w_mu
