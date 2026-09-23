# Python and destination-notebook review

**Status: all corrections approved and implemented.** The seven new articles and the existing destination notebook now incorporate the findings below. The notebook and wrapper were backed up first; [backup paths and hashes](online-estimation-backups.json) preserve the originals. The legacy Python export remains unchanged.

This review describes the **pre-correction** sources. References to the “updated notebook” below distinguish the user's 2025 notebook from the older Python export, not the corrected notebook delivered with the 2026 series. Its cell indices refer to the 23-cell backup. See the [handoff](online-estimation-migration-handoff.md) for the final 21-cell notebook and validation.

## Sources and execution scope

| Source | What was reviewed |
| --- | --- |
| [`assets/mahalanobis.py`](../assets/mahalanobis.py) | Entire exported notebook; focus on online class at lines 427–470, memory experiment, and batch class at lines 684–735. |
| [Destination wrapper post](/home/mthill/MarkusThill.github.io/_posts/2025-09-26-online-batch-estimate-cov-mu.md) | Front matter and the notebook include/availability check. This Markdown file embeds a notebook; it is not itself the notebook. |
| [Actual destination notebook](/home/mthill/MarkusThill.github.io/assets/jupyter/MarkusThill.github.io-jupyter/2025_09_27_online_estimate_cov_mu.ipynb) | All 23 cells, code and prose, saved textual results, and inventory of embedded graphics. Cell indices below are zero-based. |
| [Reproducible audit](../assets/examples/online-estimation/audit_notebook.py) and [results](../assets/examples/online-estimation/audit-results.json) | Extracts the original classes; compares their NumPy updates with explicitly weighted offline calculations. Source fingerprints are stored in the results. |

Environment used: `/home/mthill/MarkusThill.github.io/tools/.venv/bin/python`, Python 3.10.12, NumPy 2.2.6, Matplotlib 3.10.9. No packages were installed. JAX and TensorFlow were unavailable in this environment; only NumPy behavior was tested. Class annotations were postponed for numerical testing after separately reproducing the `Type[np]` error described below. The expensive original notebook was not run end-to-end, and its saved outputs were not treated as newly verified results.

## 1. The legacy mini-batch failure has a concrete cause

The legacy example uses 300-dimensional data with initial batches of 10–19 observations. The old batch class immediately calls `inv` on the first batch's centered scatter matrix.

A centered scatter matrix formed from $b$ observations has rank at most $b-1$. Therefore the first $300\times300$ scatter has rank at most 18. Its inverse does not exist. Depending on floating-point roundoff, attempting inversion can either raise an exception or return enormous, unreliable values. This explains the legacy warning about implausible inverse estimates without requiring an error in the thesis's Woodbury derivation. NumPy also explicitly documents that ill-conditioned inputs can yield inaccurate inverses without an exception. [NumPy inverse documentation](https://numpy.org/doc/stable/reference/generated/numpy.linalg.inv.html).

A four-dimensional example with rows `(0,0,0,0)`, `(1,0,0,0)`, `(0,1,0,0)` reproduces `LinAlgError: Singular matrix` in the actual old class.

The updated notebook removes the immediate first-batch inversion. That addresses this particular failure but introduces/retains the state-consistency issue below.

## 2. The updated notebook maintains two different scatter matrices

Both updated classes initialize the explicitly stored scatter to zero. Their inverse states instead correspond to nonzero initial scatter:

| Class / notebook cell | Stored scatter | Inverse initialization | Implied initial scatter |
| --- | --- | --- | --- |
| Online, cell 3 | $0$ | $10^7\mathbf{I}$ | $10^{-7}\mathbf{I}$ |
| Batch, cell 9 | $0$ | $10^3\mathbf{I}$ | $10^{-3}\mathbf{I}$ |

In exact arithmetic the inverse recurrence is tracking

$$
\left(\bar{\mathbf{M}}_n+\lambda^t\rho\mathbf{I}\right)^{-1},
$$

where $t$ counts update calls and $\rho$ is the implied initial scatter above. The reported covariance uses only $\bar{\mathbf{M}}_n$. Consequently, `get_cov_inv()` is not the inverse of `get_cov()`.

**Measured example:** 40 seeded four-dimensional Gaussian observations with population covariance $10^{-4}\mathbf{I}$, processed in batches of five with $\lambda=1$:

- Updated notebook covariance versus direct covariance: maximum absolute error $4.1\times10^{-20}$.
- Updated notebook inverse versus inverse of the reported covariance: **21.9% relative Frobenius error**.
- Updated notebook inverse versus its implicit regularized target: relative error $2.9\times10^{-16}$.

This is a difference in the matrix being inverted, rather than unexplained error caused by multiplying a large normalization factor by a small inverse. Tests with $\lambda=0.8$ also confirm the predicted decaying-ridge target for both classes.

**Recommended notebook change:** offer explicit choices. For exact sample statistics, accumulate the scatter until sufficient rank/conditioning is available, initialize its inverse with a solve, then apply Woodbury/Sherman–Morrison. If regularization from startup is desired, initialize both states consistently and describe the resulting regularized covariance. Do not label a covariance with a ridge contribution as an unbiased sample covariance.

The [corrected NumPy companion](../assets/examples/online-estimation/online_estimation.py) demonstrates the first choice. It checks positive definiteness and a declared condition limit during inverse initialization, reports unavailable inverses explicitly, and uses the thesis recurrence afterward. This approach requires an initial direct solve; remove the notebook's blanket claim that no matrix inverse/solve is ever needed.

![Inverse initialization and rank diagnosis](../images/2026-online-estimation/inverse-initialization.png)

Figure source: [generator](../assets/examples/online-estimation/generate_examples.py). [SVG](../images/2026-online-estimation/inverse-initialization.svg). The right panel is an analytical rank bound for the old example.

## 3. New substantive correction: mean weights use the wrong denominator

This additional error occurs in both the old Python export and destination notebook **cells 13 and 16**. It was not one of the previously reviewed thesis errors.

The notebook uses

$$
w_i=\frac{w'_i}{W_n-W_n^{(2)}/W_n}
$$

when predicting the covariance of the weighted mean. That denominator corrects a scatter-based covariance estimate for bias; it does **not** normalize the weights of a mean. These weights do not sum to one.

The replacement is

$$
w_i=\frac{w'_i}{W_n},\qquad
\operatorname{Cov}(\bar{\mathbf{X}}_n)
=\boldsymbol{\Sigma}\frac{W_n^{(2)}}{W_n^2},
$$

under the fixed-weight IID assumptions already discussed in the thesis.

At the notebook settings $\lambda=0.99$, $n=500$, and population variance $\Sigma_{11}=3$:

| Quantity | Correct value | Notebook value |
| --- | --- | --- |
| Sum of normalized weights | 1 | 1.00511765 |
| Predicted variance of the first mean component | 0.01527479 | 0.01543153 |

The notebook overstates this variance by **1.026%**. Its absolute-error assertion of `1e-3` is too loose to detect this discrepancy. At $\lambda=0.8$ the asymptotic overstatement is **26.5625%**, so the same bug is much easier to see.

The estimator's mean update itself uses the correct $W_n$. The error is in the explanation and predicted covariance used to validate the simulation, not in the mean estimator. Its finite-sample effective size at the notebook settings is **196.402**, rather than the limiting value 199. That startup difference should also be represented in expectations for the experiment.

**Approved and applied:** mean weights now use `raw_weights / W`, both in the notebook explanation and executable predictions. Parts 5–6 incorporate the corrected variance and finite-sample memory. The diagnostic below retains the old expression for comparison.

![Correct and incorrect normalization of weighted means](../images/2026-online-estimation/mean-weight-normalization.png)

Figure source: [generator](../assets/examples/online-estimation/generate_examples.py). [SVG](../images/2026-online-estimation/mean-weight-normalization.svg). The histogram uses 20,000 Gaussian experiments with $\lambda=0.8$, $n=80$; empirical mean variance is 0.33067, versus correct theory 0.33333 and the notebook expression 0.42188. The adjacent curve uses $n=500$.

## 4. Which previously approved issues are in the Python code?

| Earlier issue | Python finding | Action |
| --- | --- | --- |
| Wrong historical mean in the expanded forgetting proof | The classes implement the correct final recurrence, not the faulty expanded proof. | Keep their basic mean/scatter updates. |
| Missing superscript in the squared-weight recurrence | Present in notebook cell 1 and legacy displayed equations. Both classes correctly execute `W_n2 = lambda**2 * W_n2 + batch_size`. | Correct the prose equation; no change to this code line. |
| Extra plus in the general Woodbury identity | Not used in the implemented formula. Cell 8 and both batch classes have the correct specialized matrix product. | Keep the formula; improve initialization and evaluation order. |
| Overstated interpretation of effective memory | Present in notebook cell 13 and the legacy memory text. | Use variance-equivalent size for the mean; do not imply exact agreement of covariance-estimator distributions or a hard observation cutoff. |
| Wrong unweighted blog mini-batch equation | The Python batch classes use the valid thesis update instead. | No corresponding correction to their scatter equation. |
| Inconsistent R inverse initialization | A related inconsistency remains in both updated Python classes. | Use the explicit initialization policy described above. |

For the actual old and updated classes, direct checks of online and variable-batch weighted means/covariances at $\lambda=1,0.8,0.99$ agree within $9\times10^{-16}$ maximum absolute error on the tested data. The old batch case was started with a sufficiently large, nondegenerate batch for this separate algebra check.

## 5. Batch forgetting changes the statistical target

The thesis's batch formulation assigns unit weights to the entire newest batch and multiplies all older weights by $\lambda$ **once per batch**. The updated notebook implements that correctly. With variable batch sizes, it is still a valid estimator, but the age of an observation is measured in update calls rather than individual observations.

For fixed batch size $\mu$, its limiting effective sample size in observations is

$$
n_{\mathrm{mem}}\longrightarrow
\mu\frac{1+\lambda}{1-\lambda}.
$$

With $\mu=20$ and $\lambda=0.98$, that gives 1,980 observations, versus 99 for the fully online estimator using the same $\lambda$. Different drift responses are therefore expected.

Using $\lambda_{\mathrm{batch}}=\lambda_{\mathrm{observation}}^{\mu}$ matches decay of old batches but still weights all observations within a new batch equally. Exact online equivalence is possible by additionally assigning geometric weights within the new batch. For a batch of $b$ observations, use old-state decay $r^b$ and incoming weights $(r^{b-1},\ldots,r,1)$. This follows by applying the thesis's weighted update after rescaling the old weights; it is a clearly labeled extension to the constant-within-batch example.

In the seeded drift example, exact weighted batching matches online means at batch boundaries within $1.8\times10^{-15}$. This also corrects the notebook's broad claim that batching itself trades accuracy for efficiency: for identical observation weights, the statistics agree in exact arithmetic.

![Observation-wise and batch-wise forgetting on the same stream](../images/2026-online-estimation/batch-forgetting.png)

Figure source: [generator](../assets/examples/online-estimation/generate_examples.py). [SVG](../images/2026-online-estimation/batch-forgetting.svg). All curves use the same observations and a population-mean change after observation 600.

## 6. Remaining notebook fixes and improvements

| Location | Finding | Planned correction |
| --- | --- | --- |
| Cell 3 signature | `Union[Type[np], Type[jnp]]` uses modules where types are required; class definition raises `TypeError` on the available Python 3.10 environment. | Use `types.ModuleType`, a suitable protocol, or `Any`; make NumPy the required backend. [Python module type](https://docs.python.org/3/library/types.html#types.ModuleType). |
| Cells 2/3/9 | Unconditional JAX and unused TensorFlow/Keras imports prevent running NumPy-only examples without those frameworks. | Optional backend cells/imports; NumPy examples run independently. GPU timings require separate validation. |
| Cells 3/9 getters | Undefined results before sufficient data; no checks for empty/malformed batches, invalid decay, nonfinite input, or missing inverse. | Explicit input and startup behavior; no zero matrix masquerading as a valid precision estimate. |
| Cell 3 attributes | `W_n2` is called “Squared running weight.” | Call it the “sum of squared weights”; it is not `W_n**2`. |
| Cells 3/9 inverse getters | “Unbiased inverse covariance estimate” is misleading. | “Inverse of the unbiased covariance estimate.” Matrix inversion does not preserve unbiasedness. |
| Cells 3/9 inverse products | Left-associated chains build a dense intermediate and then multiply two $d\times d$ matrices. This introduces cubic work even in the rank-one update. | Cache `P @ delta` and `residual.T @ P` before their outer product. For batches, use `(P @ D.T) @ solve(inner, residual @ P)` with weights where appropriate. |
| Cell 8 complexity discussion | Cost is said to scale with batch size rather than ambient dimension; batch size below dimension is described as a guaranteed speed criterion. | Explain optimized cost $O(d^2\mu+d\mu^2+\mu^3)$ and that speed depends on dimensions, backend, and reference implementation. Do not claim measured speedups from unequal experiments. |
| Cells 6/11 timings | Online timing excludes data generation and processes 5,000 observations; batch timing includes generation and processes 5,000 batches. | Benchmark identical data/counts; separate generation and estimator time; precompute a sampling factor if appropriate. |
| Cells 7/12 validation | Unweighted `np.cov` and ordinary mean remain the reference even if a reader changes $\lambda<1$ as invited. | Compare with explicit exponential observation/batch weights and the same normalization/regularization; reserve `np.cov` without weights for $\lambda=1$. [NumPy weighted covariance documentation](https://numpy.org/doc/stable/reference/generated/numpy.cov.html). |
| Cells 7/12 tolerances | Only absolute average-entry errors are tested; no startup, inverse identity, symmetry, scale, or conditioning checks. | Add relative norm errors and inverse residuals on well-conditioned cases; test startup, variable batch sizes, decay, and rescaled data. |
| Cells 10/11 | `if cov is None` fails if `cov` is undefined; hidden dependence on earlier globals. | Each example creates explicit data or receives parameters. |
| Cells 14/15 | Last-window sample estimates are called “ground truth”; no random seed; 50,000 experiments maintain unused inverse states. | Call them comparison estimators; use seeded, configurable simulation; calculate only required statistics. |
| Cell 17 | `std` is calculated for the theoretical annotation, but the string displays `sigma` from the empirical result. | Display `std`; distinguish mean and covariance parameters in labels. |
| Cell 17 | `plt.show(fig)` raises `TypeError` with the installed Matplotlib 3.10.9. | Use `plt.show()` or `fig.savefig(...)`. The current [show API](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.show.html) also has no positional figure argument. |
| Cells 19/21 | Historical comparison images are embedded as base64 and lack a reproducible generating cell/seed. | Preserve their provenance; regenerate current examples with explicit parameters and export linked PNG/SVG assets. Do not label historical images as outputs of corrected cells. |
| Cell 1 | A universal recommendation to set $\lambda=1-10^{-8}$ to avoid numerical instability is too strong. | Explain the estimation/adaptation tradeoff; forgetting does not guarantee good conditioning or numerical stability. |
| Wrapper post | It embeds `2025_09_27_online_estimate_cov_mu.ipynb` but tests existence of `2025_09_26_mahalanobis.ipynb`. | Make the availability check refer to the notebook actually embedded. |

The legacy batch class also reshapes a flat observation to `(dim,1)` instead of `(1,dim)`: input `[1,2]` produces an internal mean `[1.5,1.5]` and weight 2 before its inverse fails. The updated notebook already fixes this; preserve the fix.

The Mahalanobis-only sections of the legacy export contain other issues worth avoiding during extraction: `if not cov` fails for an array-valued covariance; a fixed determinant threshold is scale-dependent and can reject a perfectly conditioned covariance; some squared-distance plots are labeled as distances. The chi-square statement requires known Gaussian population parameters for exactness, whereas some examples substitute fitted parameters. These sections already have separate destination-blog posts and should not be imported wholesale into the new estimation series.

## 7. New companion artifacts and checks

The [Python companion directory](../assets/examples/online-estimation/README.md) contains the reference implementation, original-class audit, figure generator, tested requirements, and numerical results. Four figures exist in PNG and SVG, including a Python version of B1's Gaussian convergence experiment:

![Seeded Python convergence example](../images/2026-online-estimation/python-convergence.png)

[SVG](../images/2026-online-estimation/python-convergence.svg). The covariance is undefined at one observation and is plotted starting with the second. Population values are references; the estimate is not expected to equal them exactly in a finite random sample.

The reference passed 432 weighted prefix-state comparisons and 396 inverse comparisons across online, fixed-batch, and variable-batch settings. Maximum relative covariance error was $7.9\times10^{-16}$; maximum relative inverse error was $2.5\times10^{-14}$ on that test set. Startup behavior and exact per-observation forgetting represented in batches were also checked. These are NumPy checks, not a guarantee for arbitrarily ill-conditioned data or other backends.

## 8. Decision for the article series

Keep the seven dates and topics. Put Python convergence in Part 2, weighted/batch updates in Part 3, the forgetting comparison in Part 4, corrected mean-weight normalization in Part 5, Monte Carlo validation and finite-sample memory in Part 6, and inverse initialization/performance in Part 7. Retain useful R examples and legacy graphics alongside the new Python material.

Treat the destination notebook as the runnable companion, linked from those articles. It does not need an eighth theory article. Its existing 2025 wrapper date is outside the new seven-post schedule and need not be changed just to link the new series.

The author approved the additional correction and requested an in-place notebook update with a backup. That work is complete. All nine corrected code cells were executed in order with NumPy, including 480 weighted-prefix checks and 450 inverse checks. The maximum relative inverse error was approximately $2.0\times10^{-13}$; the maximum covariance-times-precision residual was approximately $1.5\times10^{-12}$. See [notebook validation results](../assets/examples/online-estimation/notebook-validation.json).

The corrected notebook uses a single `IncrementalMoments` class, with the same source as the downloadable module. It replaces historical embedded figures with seeded outputs and keeps the originals in the backup. The wrapper now checks the same notebook it embeds. The [execution helper](../assets/examples/online-estimation/execute_notebook.py) captures stdout and PNG outputs without requiring Jupyter packages. No Ruby/Jekyll build or R execution was performed.
