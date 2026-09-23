# Online Estimation: Python and R Companions

These files accompany the seven 2026 articles and the [companion notebook](../../jupyter/MarkusThill.github.io-jupyter/2025_09_27_online_estimate_cov_mu.ipynb). The notebook is self-contained and keeps its own two estimator classes, `OnlineCovarianceMeanEstimator` and `BatchCovarianceMeanEstimator`, which mirror the two subsections of the thesis appendix. `online_estimation.py` here is the article helper: one `IncrementalMoments` class covering both cases, used by the code snippets in the posts. The two implement the same recurrences and agree numerically; they differ only in how the API is arranged. The [merge plan](../../../docs/online-estimation/online-estimation-series-merge-plan.md), [Python audit](../../../docs/online-estimation/online-estimation-python-review.md), and [migration handoff](../../../docs/online-estimation/online-estimation-migration-handoff.md) document the decisions.

## Code and results

| File | Purpose |
| --- | --- |
| [online_estimation.py](online_estimation.py) | Weighted mean/scatter and optional Woodbury inverse updates after sufficient rank is available. |
| [audit_notebook.py](audit_notebook.py) | Reproduce the original implementation problems using the **backup**, and check the corrected module against explicit weighted references. |
| [audit-results.json](audit-results.json) | Historical audit, source hashes, and 432 prefix/396 inverse comparisons. |
| [generate_examples.py](generate_examples.py) | Generate four article figures with recorded seeds; historical inverse diagnosis reads the backup. |
| [figure-results.json](figure-results.json) | Numerical values used in those figures. |
| [execute_notebook.py](execute_notebook.py) | Execute the revised notebook's plain Python cells in order, capture stdout and Matplotlib images, and save outputs. It uses a fresh Python namespace, not a Jupyter kernel. |
| [notebook-validation.json](notebook-validation.json) | Revised notebook execution: 480 weighted-prefix checks, 450 inverse comparisons, simulations, and fair-workload timings. |
| [requirements.txt](requirements.txt) | Tested NumPy and Matplotlib versions. No GPU packages required. |
| [online-mean-covariance.R](online-mean-covariance.R) | Seeded version of the original Gaussian convergence example. |
| [forgetting-drift.R](forgetting-drift.R) | The original offset-stream illustration, with a documented jump of 2 and a seed. |
| [estimator-memory.R](estimator-memory.R) | Gaussian mean-distribution comparisons with 100 and 199 observations. |
| [inverse-covariance.R](inverse-covariance.R) | Consistent explicit initial ridge, with checks against the same regularized scatter. |
| [density-weighted-mean-thesis.pdf](density-weighted-mean-thesis.pdf) | Thesis Figure B.1, using uniform observations; distinct from the Gaussian blog simulations. |
| [legacy/mahalanobis.py](legacy/mahalanobis.py) | Unedited legacy Python export from the old blog repository, used only by the historical audit. |

## Running Python

Use Python 3.10+ with NumPy and Matplotlib. From this directory:

```bash
python audit_notebook.py
python generate_examples.py
python execute_notebook.py
```

The first two commands default to the preserved **historical backup** under `assets/jupyter/MarkusThill.github.io-jupyter/backups/`. Do not point them at the corrected notebook: they intentionally inspect the old classes. `execute_notebook.py` defaults to the **corrected live notebook**, executes all code cells, updates its stored outputs, and exports figures. After porting, supply explicit paths:

```bash
python audit_notebook.py --notebook /path/to/original-notebook-backup.bak --legacy-source /path/to/mahalanobis.py
python generate_examples.py --notebook /path/to/original-notebook-backup.bak --legacy-source /path/to/mahalanobis.py
python execute_notebook.py --notebook /path/to/2025_09_27_online_estimate_cov_mu.ipynb --output-dir /path/to/assets/img/2026-online-estimation
```

The environment used was `/home/mthill/MarkusThill.github.io/tools/.venv/bin/python` (Python 3.10.12, NumPy 2.2.6, Matplotlib 3.10.9). Its packages were reused without installation. Set `OPENBLAS_NUM_THREADS=1` for reproducible small-matrix overhead and `MPLCONFIGDIR=/tmp/online-estimation-mpl` for a writable cache. Timings depend on hardware and load; the notebook gives all methods the same observations and checks results.

The historical audit extracts only the original estimator classes. It postpones annotations to isolate arithmetic from the separately recorded `Type[np]` error. Original GPU imports and expensive top-level experiments are not executed. The corrected notebook needs neither JAX nor TensorFlow and has been executed end-to-end using the plain-Python runner.

## Estimator API

```python
import numpy as np
from online_estimation import IncrementalMoments

X = np.array([[0., 0.], [2., 1.], [4., -1.], [6., 3.]])
state = IncrementalMoments(2, track_inverse=True)
state.update(X[:2])
assert state.scatter_inverse is None
state.update(X[2:])
np.testing.assert_allclose(state.mean, X.mean(axis=0))
np.testing.assert_allclose(state.covariance(), np.cov(X, rowvar=False))
np.testing.assert_allclose(state.covariance() @ state.precision(), np.eye(2), atol=1e-12)
```

`decay` applies once per update call. For exact per-observation decay `r` represented by a batch:

```python
r = .98
batch = X[:3]
state = IncrementalMoments(2)
state.update(batch, decay=r**len(batch),
             weights=r**np.arange(len(batch)-1, -1, -1))
```

`covariance()` uses the fixed reliability-weight correction; its unbiasedness requires independent observations with a common mean and covariance and fixed weights. `covariance(unbiased=False)` uses the population normalization. `precision()` returns the inverse of the selected covariance, without claiming an unbiased estimate of population precision.

Python starts from zero scatter and initializes its inverse only after a Cholesky check and a declared condition limit of `1e10`. Subsequent updates use Woodbury. Insufficient rank or conditioning means the inverse remains unavailable. Long runs need application-specific residual and conditioning checks and, when necessary, refactoring; symmetrization alone is not a stability guarantee.

## Running R

R scripts require base R and `MASS` for `MASS::mvrnorm`. Run `Rscript filename.R` from this directory. They write `r-online-mean-covariance.pdf`, `r-forgetting-drift.pdf`, `r-estimator-memory.pdf`, and `r-inverse-covariance.pdf` respectively. These optional regenerated PDFs are not used as article dependencies. R was unavailable here, so the R scripts were reviewed but not executed. The inverse script makes its regularization explicit, whereas the Python estimator uses unregularized warm-up.

## Figure copy manifest

Copy the images referenced in each post; retain SVGs for vector reuse. All following files are under `assets/img/2026-online-estimation/`, with both `.png` and `.svg` extensions:

| Basename | Generator / role |
| --- | --- |
| `python-convergence` | `generate_examples.py`; Part 2, original 3D Gaussian setup. |
| `batch-forgetting` | `generate_examples.py`; Part 4, same stream with a mean change after 600 observations. |
| `mean-weight-normalization` | `generate_examples.py`; Part 5, corrected theory versus original notebook expression. |
| `inverse-initialization` | `generate_examples.py`; Part 7, original implicit ridge and legacy analytical rank bound. |
| `notebook-memory-comparison` | Revised notebook / `execute_notebook.py`; Part 6, 20,000 Gaussian replicates, 100 versus 199, finite memory 196.402. |
| `notebook-convergence` | Revised notebook export; supplementary mean/variance figure. |
| `notebook-batch-forgetting` | Revised notebook export; supplementary shared-stream figure. |

Legacy images also retained in the articles:

- `assets/img/2026-online-estimation/stats.jpg` (series thumbnail, formerly `images/stats.jpg`)
- `assets/img/2026-online-estimation/historical/estimator.png` (formerly `images/2017-11-20-online-estimation-of-gaussians/`)
- `assets/img/2026-online-estimation/historical/forgetting.png`
- `assets/img/2026-online-estimation/historical/distriMeans.png`
- `assets/img/2026-online-estimation/historical/distriMeans2.png`

The last three came from `images/2018-01-13-online-estimation-of-weighted-sample-mean-and-coviarance-matrix/` in the old repository; the legacy spelling `coviarance` does not survive the move, and no link in this repository depends on it. Their original seeds were not recorded, so the new scripts reproduce the experiments rather than the exact historical traces.

## Provenance and backup

The [backup manifest](../../../docs/online-estimation/online-estimation-backups.json) records byte-for-byte original notebook and wrapper copies and their SHA-256 hashes. The notebook backup preserves its historical embedded images and supplies the original diagnostic classes. The legacy Python export is preserved unedited as `legacy/mahalanobis.py` for that audit.

The notebook lives at `assets/jupyter/MarkusThill.github.io-jupyter/2025_09_27_online_estimate_cov_mu.ipynb` and is rendered by the wrapper post `_posts/2025-09-26-online-batch-estimate-cov-mu.md`. That directory is a Git submodule, so publishing a notebook change means committing inside the submodule and then updating its recorded revision here.
