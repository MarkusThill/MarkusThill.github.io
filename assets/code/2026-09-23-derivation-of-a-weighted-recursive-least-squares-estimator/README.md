# Weighted Recursive Least Squares

Code for the blog post [Derivation of a Weighted Recursive Linear Least Squares Estimator](https://markusthill.github.io/blog/2026/derivation-of-a-weighted-recursive-least-squares-estimator/).

| File | Content |
| --- | --- |
| `weighted_rls.py` | The `WeightedRLS` class: weighted recursive least squares for batches of any size (including single observations), one or several outputs and exponential forgetting. It only needs NumPy. |
| `test_weighted_rls.py` | Tests that compare the recursion with the direct weighted least squares solution after every update, and check shapes, invalid inputs and the docstring examples. |
| `requirements.txt` | NumPy and Matplotlib versions used for the notebook and its figures. |
| `RLSModel.R` | An R6 model class with a recursive least squares update and forgetting. It depends on its surrounding R project (for example the `IModel` base class) and does not run on its own. |

The R file is a legacy application example with a nonzero initial coefficient vector and a custom warm-up. During its first 21 observations, the inverse is updated while coefficient updates are suppressed, and the accumulated corrections are cleared before being applied. It therefore does not reproduce the estimator derived in the post during initialization.

The [companion notebook](https://github.com/MarkusThill/MarkusThill.github.io-jupyter/blob/main/2026_09_23_weighted_recursive_least_squares.ipynb) develops the class step by step from the equations in the post, with an example and a check against the direct solution after each step. It only needs NumPy and Matplotlib and can be [opened in Google Colab](https://colab.research.google.com/github/MarkusThill/MarkusThill.github.io-jupyter/blob/main/2026_09_23_weighted_recursive_least_squares.ipynb).

## Usage

The most common case: observations arrive one at a time, all of them are equally reliable, and the relationship may change slowly, so a forgetting factor slightly below 1 is used.

```python
import numpy as np
from weighted_rls import WeightedRLS

rng = np.random.default_rng(0)
X = np.column_stack([np.ones(500), rng.uniform(-3, 3, 500)])   # column of ones for the intercept
y = X @ [1.0, 0.6] + rng.normal(0, 0.1, 500)

rls = WeightedRLS(n_features=2, forgetting=0.99, ridge=1.0)
for x_t, y_t in zip(X, y):
    y_hat = rls.predict(x_t)     # predict first ...
    rls.update(x_t, y_t)         # ... then learn from the new observation
print(rls.theta.ravel())         # approximately [1.0, 0.6]
```

`update(X, Y, weights=None)` processes one batch (a 1-D `X` is a single observation) and returns the prediction errors computed before the update. `fit(X, Y, batch_size=1, weights=None)` processes a whole data set in consecutive batches, and `predict(X)` evaluates the model. The attributes `theta` and `A_inv` hold the current coefficients and the inverse of the regularized, weighted normal matrix.

**Input-validation limitations.** Use a positive integer `batch_size`, a finite positive `ridge`, nonempty batches for `update`, and exactly matching numbers of input rows, targets and weights. The current implementation does not enforce all of these conditions: a negative batch size silently processes nothing, surplus targets or weights are ignored, an empty update applies forgetting after training has started, and `ridge=np.inf` prevents learning. If a later batch is invalid, `fit` can fail after earlier batches have already changed the model; validate the whole data set before calling it.

## Tests

Run from this directory:

```bash
python -m unittest -v
```
