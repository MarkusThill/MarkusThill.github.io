# Online estimation series: completed work and migration handoff

The seven articles are written in the working repository. All original derivation corrections and the additional Python corrections were approved and incorporated. The existing notebook in the destination repository was backed up, corrected, extended, and executed. Nothing has been committed, pushed, published, or migrated automatically.

## Articles to copy

The dates start on 1 February 2026 and are separated by 14 days. Every post has front matter, series navigation, standard LaTeX, and an HTML `Migration dependencies` comment with exact paths.

| Date | Article |
| --- | --- |
| 2026-02-01 | [Introduction](../_posts/2026-02-01-online-estimation-introduction.md) |
| 2026-02-15 | [Online mean and covariance](../_posts/2026-02-15-online-mean-and-covariance.md) |
| 2026-03-01 | [Weighted mean and covariance](../_posts/2026-03-01-weighted-mean-and-covariance.md) |
| 2026-03-15 | [Exponential forgetting](../_posts/2026-03-15-exponentially-weighted-estimation.md) |
| 2026-03-29 | [Covariance of weighted means](../_posts/2026-03-29-covariance-of-weighted-means.md) |
| 2026-04-12 | [Memory of exponential estimators](../_posts/2026-04-12-memory-of-exponential-estimators.md) |
| 2026-04-26 | [Online inverse covariance](../_posts/2026-04-26-online-inverse-covariance.md) |

The seven-part structure remains appropriate: it adds a thesis-based introduction and separates arbitrary weights from forgetting, while the notebook serves as the runnable companion rather than an eighth theory article.

## Assets and rendering

Copy these paths from `/home/mthill/MarkusThill.github.io.working`:

- The seven `_posts/2026-*.md` files listed above.
- `assets/examples/online-estimation/` in full: NumPy implementation, R scripts, diagnostic and execution helpers, results, requirements, README, and the thesis figure PDF.
- `images/2026-online-estimation/` in full: seven PNG/SVG pairs. Five are used directly by the articles; two are supplementary notebook exports.
- `images/stats.jpg`.
- `images/2017-11-20-online-estimation-of-gaussians/estimator.png`.
- `images/2018-01-13-online-estimation-of-weighted-sample-mean-and-coviarance-matrix/forgetting.png`.
- `images/2018-01-13-online-estimation-of-weighted-sample-mean-and-coviarance-matrix/distriMeans.png`.
- `images/2018-01-13-online-estimation-of-weighted-sample-mean-and-coviarance-matrix/distriMeans2.png`.
- `docs/online-estimation-series-merge-plan.md`, `docs/online-estimation-derivation-review.md`, `docs/online-estimation-python-review.md`, `docs/online-estimation-backups.json`, `docs/online-estimation-validation.json`, and this handoff for provenance.
- `assets/mahalanobis.py` if preserving the reproducible historical audit. It is unchanged and is not the corrected implementation to recommend to readers.

Preserve the legacy spelling `coviarance` in image paths or update every reference. The old articles, thesis LaTeX, and bibliographies are editorial sources, not runtime requirements. Plain reference entries in the new posts avoid a Jekyll Scholar dependency.

Adapt old-theme front matter (`image.feature`, categories, comments) to the destination theme during migration. Preserve the dates. The articles use `post_url` for sibling navigation; update navigation if the destination stops supporting that tag. Math requires a renderer supporting standard LaTeX; no thesis-specific macros are needed. Images and code use Markdown, without old image includes or highlight tags.

**Notebook links intentionally resolve in the destination repository.** They point to `/assets/jupyter/MarkusThill.github.io-jupyter/2025_09_27_online_estimate_cov_mu.ipynb`, which exists there already. There is no duplicate live notebook under that path in the working repository. If publishing the posts on the old site first, remap this companion link to the destination or provide the corresponding asset.

## Notebook already updated in place

- [Corrected notebook](/home/mthill/MarkusThill.github.io/assets/jupyter/MarkusThill.github.io-jupyter/2025_09_27_online_estimate_cov_mu.ipynb).
- [Existing wrapper](/home/mthill/MarkusThill.github.io/_posts/2025-09-26-online-batch-estimate-cov-mu.md), retaining its 2025 publication date. Its `file_exists` check now names the notebook actually embedded, and its introduction describes the revised examples.
- [Original notebook backup](/home/mthill/MarkusThill.github.io/assets/jupyter/MarkusThill.github.io-jupyter/backups/2025_09_27_online_estimate_cov_mu.ipynb.before-2026-series.bak).
- [Original wrapper backup](/home/mthill/MarkusThill.github.io/docs/online-estimation-backups/2025-09-26-online-batch-estimate-cov-mu.md.before-2026-series.bak), stored outside `_posts` so it cannot be discovered as an extra article.

The [backup manifest](online-estimation-backups.json) records SHA-256 hashes of the byte-for-byte originals. The original notebook's hash is `70149cded8eeb5bf1379b5f5c8f23d9ffb8e5955eca73edf84c1452ce7d9815c`. Its embedded historical images remain in the backup. Diagnostic scripts now read that backup, so their original-code comparisons remain reproducible after the live notebook update.

The notebook directory is a **Git submodule**. To publish later, include changes in that submodule and then update its recorded revision in the parent repository. The wrapper and seven posts belong to the parent repository. No commits or pushes were made during this work.

The revised notebook keeps the original structure, prose, examples and figures, and retains both `OnlineCovarianceMeanEstimator` and `BatchCovarianceMeanEstimator` with their original public API. Only the recorded defects were changed: inverse initialization, the mean-weight normalization in the covariance check, the `Expected` annotation in the distribution plot, the squared-weight recurrence in the summary text, and the memory statement. Seeds were added, JAX and TensorFlow became optional, and the Sherman-Morrison and Woodbury updates were reordered to avoid an unnecessary dense matrix-matrix product. The two 2x3 distribution figures that were previously pasted in as static base64 images are now produced by the cells that precede them. It runs on NumPy and Matplotlib alone; standard Jupyter can also run the plain Python cells.

## Corrections applied

The detailed derivation and Python reviews retain the evidence and original cell references. The principal changes are:

- Preserve historical means when expanding forgetting increments; retain the valid thesis scatter recurrence.
- Correct the displayed sum-of-squared-weights recurrence and general Woodbury product.
- Use the thesis's valid batch derivation in place of the old blog's incorrect unweighted batch expression.
- Distinguish Gaussian ML covariance, unbiased sample covariance, and the inverse of a covariance estimate.
- Normalize mean weights by `W`, not the unbiased covariance denominator.
- Report finite memory as well as its limit; interpret it as matching covariance of the mean under fixed-weight IID assumptions.
- Start the Python inverse only when rank/conditioning permits. The original zero-scatter/nonzero-inverse mismatch is removed. The separate R example initializes an explicit ridge and its inverse consistently.
- Apply decay at a declared time scale; show exact online/batch agreement when within-batch weights match.
- Use valid NumPy typing, input/startup guards, efficient multiplication order, explicit weighted references, seeded experiments, correct theoretical standard deviations, valid plotting calls, and equal-data timing comparisons.

The memory plots are regenerated from seeded simulations. Historical blog figures remain clearly labeled and are not presented as outputs of the revised code. The copied thesis PDF uses uniform observations, while the blog and notebook density examples use Gaussian observations.

## Verification and limits

[Article validation](online-estimation-validation.json) records front-matter parsing, the seven 14-day dates, Markdown parsing, balanced code/display-math/LaTeX environments, series references, and the existence and manifest coverage of linked assets. All six article Python examples were executed successfully. Original article bytes still match Git HEAD; the supplied Python export retains its original hash. Both backup hashes were verified.

[Notebook validation](../assets/examples/online-estimation/notebook-validation.json) records execution of all nine code cells in a fresh namespace using the [plain-Python execution helper](../assets/examples/online-estimation/execute_notebook.py), with stdout and figures saved as standard notebook outputs. No Jupyter kernel was installed. Results include:

- 480 weighted-prefix checks and 450 inverse comparisons, across online/fixed/variable batches, decay factors 1, 0.5, and 0.99, and unequal incoming weights.
- Maximum relative covariance error approximately `1.15e-15`; maximum relative inverse error approximately `1.97e-13`; maximum covariance-times-precision residual approximately `1.50e-12` on those cases.
- Exact per-observation forgetting reproduced at batch boundaries to numerical tolerance.
- Correct startup behavior for insufficient rank, including 300 dimensions and 15 observations.
- Finite effective sample size `196.4020177474536` at decay 0.99 and 500 observations, and seeded Monte Carlo agreement with its predicted mean variances.
- Fair timing runs on identical pre-generated data, with final covariance and precision checks. Timings compare the complete example methods and are machine-specific.

The separate historical audit retains 432 weighted-prefix checks and 396 inverse comparisons for the shared module, and reproduces the original 21.9% implicit-ridge discrepancy.

R scripts were adapted and reviewed but **not executed**, because no R runtime was available. No Jekyll/Ruby build, publication, GPU test, or browser rendering test was performed. Python checks do not establish stability for arbitrarily ill-conditioned matrices or indefinitely long streams; the articles state the numerical limitations and refactoring options.
