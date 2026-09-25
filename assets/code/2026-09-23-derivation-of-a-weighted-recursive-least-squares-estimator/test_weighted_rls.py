"""Tests for the WeightedRLS class.

Run from this directory with ``python -m unittest -v``. Every check compares the
recursion with a directly computed weighted least squares solution.
"""
import doctest
import unittest

import numpy as np

import weighted_rls
from weighted_rls import WeightedRLS


def direct_solution(X, Y, w, rho, lam, batch_size):
    """Solve the problem that the recursion solves after processing X in batches.

    An observation whose batch is a batches old has the weight w * lam**a, and
    the initial regularization has decayed to rho * lam**(M - 1) after M batches.
    """
    batch_index = np.arange(len(X)) // batch_size
    n_batches = batch_index[-1] + 1
    weights = w * lam ** (n_batches - 1 - batch_index)
    A = X.T @ (weights[:, None] * X) + rho * lam ** (n_batches - 1) * np.eye(X.shape[1])
    return np.linalg.solve(A, X.T @ (weights[:, None] * Y))


class TestWeightedRLS(unittest.TestCase):

    def test_matches_direct_solution_after_every_update(self):
        rng = np.random.default_rng(1)
        X = np.column_stack([np.ones(57), rng.normal(size=(57, 3))])
        Y = X @ rng.normal(size=(4, 3)) + 0.1 * rng.normal(size=(57, 3))
        for batch_size in (1, 4, 10):
            for m in (1, 3):
                for lam in (1.0, 0.9):
                    for w in (np.ones(57), rng.uniform(0.2, 5.0, 57)):
                        rls = WeightedRLS(4, m, forgetting=lam, ridge=0.3)
                        for start in range(0, 57, batch_size):
                            stop = min(start + batch_size, 57)
                            errors = rls.update(X[start:stop], Y[start:stop, :m], w[start:stop])
                            self.assertEqual(errors.shape, (stop - start, m))
                            expected = direct_solution(X[:stop], Y[:stop, :m], w[:stop], 0.3, lam, batch_size)
                            np.testing.assert_allclose(rls.theta, expected, rtol=0, atol=1e-10)
                        np.testing.assert_array_equal(rls.A_inv, rls.A_inv.T)
                        self.assertEqual(rls.n_seen, 57)

    def test_errors_are_computed_before_the_update(self):
        rls = WeightedRLS(2, forgetting=0.95)
        rls.update([[1.0, 2.0], [1.0, -1.0]], [3.0, 0.5])
        X_new, y_new = np.array([[1.0, 0.5], [1.0, 3.0]]), np.array([1.0, 4.0])
        expected = y_new[:, None] - X_new @ rls.theta
        np.testing.assert_allclose(rls.update(X_new, y_new), expected)

    def test_fit_equals_repeated_updates(self):
        rng = np.random.default_rng(2)
        X = rng.normal(size=(23, 3))
        Y = rng.normal(size=(23, 2))
        w = rng.uniform(0.5, 2.0, 23)
        fitted = WeightedRLS(3, 2, forgetting=0.97)
        errors = fitted.fit(X, Y, batch_size=5, weights=w)
        manual = WeightedRLS(3, 2, forgetting=0.97)
        expected = np.vstack([manual.update(X[i:i + 5], Y[i:i + 5], w[i:i + 5]) for i in range(0, 23, 5)])
        np.testing.assert_array_equal(errors, expected)
        np.testing.assert_array_equal(fitted.theta, manual.theta)
        self.assertEqual(WeightedRLS(3).fit(np.empty((0, 3)), np.empty(0)).shape, (0, 1))

    def test_accepted_shapes_for_single_observations_and_outputs(self):
        rls = WeightedRLS(2)
        self.assertEqual(rls.update([1.0, 2.0], 3.0).shape, (1, 1))            # 1-D x, scalar y
        self.assertEqual(rls.update([[1.0, 2.0], [0.0, 1.0]], [1.0, 2.0]).shape, (2, 1))
        multi = WeightedRLS(2, n_outputs=3)
        self.assertEqual(multi.update([1.0, 2.0], [1.0, 2.0, 3.0]).shape, (1, 3))
        self.assertEqual(multi.predict([[1.0, 0.0], [0.0, 1.0]]).shape, (2, 3))
        self.assertEqual(rls.predict([1.0, 0.0]).shape, (1, 1))

    def test_invalid_input_raises_and_keeps_the_state(self):
        rls = WeightedRLS(2, n_outputs=2)
        rls.update([[1.0, 2.0]], [[1.0, 2.0]])
        theta, A_inv = rls.theta.copy(), rls.A_inv.copy()
        invalid_batches = [
            ([[1.0, 2.0, 3.0]], [[1.0, 2.0]], None),     # wrong number of features
            ([[1.0, 2.0]], [[1.0, 2.0, 3.0]], None),     # wrong number of outputs
            ([[1.0, 2.0], [3.0, 4.0]], [1.0, 2.0], None),  # ambiguous 1-D targets for two outputs
            ([[1.0, 2.0]], [[1.0, 2.0]], [0.0]),          # non-positive weight
            ([[1.0, 2.0]], [[1.0, 2.0]], [1.0, 1.0]),     # wrong number of weights
            ([[np.nan, 2.0]], [[1.0, 2.0]], None),        # NaN input
        ]
        for X, Y, w in invalid_batches:
            with self.assertRaises(ValueError):
                rls.update(X, Y, w)
            np.testing.assert_array_equal(rls.theta, theta)
            np.testing.assert_array_equal(rls.A_inv, A_inv)
        for kwargs in ({"forgetting": 0.0}, {"forgetting": 1.5}, {"ridge": 0.0}, {"n_outputs": 0}):
            with self.assertRaises(ValueError):
                WeightedRLS(2, **kwargs)

    def test_long_run_with_forgetting_stays_symmetric_and_accurate(self):
        rng = np.random.default_rng(3)
        X = np.column_stack([np.ones(20_000), rng.uniform(-3, 3, 20_000)])
        y = X @ [1.0, 0.6] + rng.normal(0, 0.5, 20_000)
        rls = WeightedRLS(2, forgetting=0.95, ridge=0.01)
        for x_i, y_i in zip(X, y):
            rls.update(x_i, y_i)
        np.testing.assert_array_equal(rls.A_inv, rls.A_inv.T)
        expected = direct_solution(X[-2000:], y[-2000:, None], np.ones(2000), 0.0, 0.95, 1)
        np.testing.assert_allclose(rls.theta, expected, rtol=0, atol=1e-9)

    def test_reset(self):
        rls = WeightedRLS(2, ridge=4.0)
        rls.update([1.0, 2.0], 3.0)
        rls.reset()
        np.testing.assert_array_equal(rls.theta, np.zeros((2, 1)))
        np.testing.assert_array_equal(rls.A_inv, np.eye(2) / 4.0)
        self.assertEqual(rls.n_seen, 0)

    def test_docstring_examples(self):
        result = doctest.testmod(weighted_rls, extraglobs={"np": np}, verbose=False)
        self.assertEqual(result.failed, 0)
        self.assertGreater(result.attempted, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
