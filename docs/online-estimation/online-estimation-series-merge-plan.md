# Online estimation series: comparison and merge plan

Status: **completed locally**. The author approved the original derivation corrections and all newly discovered Python corrections, and explicitly authorized updating the existing destination notebook after a backup. Seven articles, four adapted R scripts, corrected Python examples, new figures, and per-post migration manifests are written. The existing notebook and its wrapper are updated in place; the original posts, thesis, and legacy Python export remain unchanged. See the [migration handoff](online-estimation-migration-handoff.md) and [backup manifest](online-estimation-backups.json).

The new series will combine the five original articles with Appendix B.2 of Markus Thill's *Machine Learning and Deep Learning Approaches for Multivariate Time Series Prediction and Anomaly Detection* (2022). The thesis supplies the derivations, notation, and motivation. The original posts supply the accessible unweighted example, R implementations, simulations, and reusable graphics. The supplied Python export and intended destination notebook now also supply implementation examples, with the corrections documented in the Python review.

## 1. Sources and precedence

The following sources were read and compared:

| ID | Source | Role |
| --- | --- | --- |
| T1 | [Thesis: `appendix/onlinemeancov.tex`](/home/mthill/PhD/Thesis.d/appendix/onlinemeancov.tex) | B.2.1–B.2.2: weighted estimates, batches, forgetting, inverse updates. Primary mathematical source. |
| T2 | [Thesis: `appendix/covweightedmean.tex`](/home/mthill/PhD/Thesis.d/appendix/covweightedmean.tex) | B.2.3: covariance of weighted sample means. |
| T3 | [Thesis: `appendix/onlineestimatormemory.tex`](/home/mthill/PhD/Thesis.d/appendix/onlineestimatormemory.tex) | B.2.4: finite-sample and limiting memory formulas. |
| T4 | [Thesis definitions](/home/mthill/PhD/Thesis.d/definitions.tex) and [thesis assembly](/home/mthill/PhD/Thesis.d/thesis.tex) | Actual rendered notation and appendix organization. Macro names such as `muhat` do not necessarily describe the printed symbol. |
| T5 | [Introduction](/home/mthill/PhD/Thesis.d/chIntroduction/chIntroduction.tex), [abstract](/home/mthill/PhD/Thesis.d/abstract.tex), and [summary](/home/mthill/PhD/Thesis.d/summary.tex) | Motivation: monitoring data streams, adapting to changing normal behavior, and the balance between stable estimates and fast adaptation. |
| T6 | [SORAD chapter](/home/mthill/PhD/Thesis.d/chEAIS2017/cheais2017.tex), especially §4.2.3 | Online estimation of prediction-error statistics. |
| T7 | [Online DWT-MLEAD chapter](/home/mthill/PhD/Thesis.d/chWavelets/ecda2018.tex), especially §5.3.2 | Incremental multivariate estimates and inverse covariance for Mahalanobis scoring. |
| B1 | [2017-11-20: online Gaussian estimation](../_posts/2017-11-20-online-estimation-of-gaussians.md) | Unweighted introduction, R estimator, convergence graphic. |
| B2 | [2018-01-13: weighted estimation](../_posts/2018-01-13-online-estimation-of-weighted-sample-mean-and-coviarance-matrix.md) | Single-observation weighted and forgetting derivations; bibliography. |
| B3 | [2018-01-18: covariance of weighted means](../_posts/2018-01-18-onthe-covariance-of-the-weighted-mean.md) | Closely overlaps T2. |
| B4 | [2018-02-03: estimator memory](../_posts/2018-02-03-memory-of-an-exponentially-weighted-estimator-of-the-arithmetic-mean-and-covariance-matrix.md) | Density simulations, drift simulation, three graphics. |
| B5 | [2018-10-14: inverse covariance](../_posts/2018-10-14-online-estimation-of-the-inverse-covariance-matrix.md) | Sherman–Morrison derivation and R implementation. |
| P1 | [Python notebook export](../assets/mahalanobis.py) | Original Python online/batch implementations and memory experiments; keep as provenance. |
| P2 | [Intended destination notebook](/home/mthill/MarkusThill.github.io/assets/jupyter/MarkusThill.github.io-jupyter/2025_09_27_online_estimate_cov_mu.ipynb) | Primary runnable companion after documented corrections; all 23 cells reviewed. |
| P3 | [Destination notebook wrapper](/home/mthill/MarkusThill.github.io/_posts/2025-09-26-online-batch-estimate-cov-mu.md) | Existing page that embeds P2; its availability check currently references the wrong notebook. |

PDF cross-checks:

- [Thesis v1.3](/home/mthill/PhD/thesis-thill-v1.3.pdf): B.2, printed pages 149–164.
- [Later print-production PDF, processed 21 February 2022](/home/mthill/PhD/docs/wetransfer_573560-l-sub01-bw-thill-pdf_2022-02-21_1255/573560-L-sub01-bw-Thill.pdf): B.2, printed pages 157–172. This is a production proof; its filename is not evidence of a separate revised mathematical edition.

The suspect Woodbury statement, squared-weight summary, and forgetting expansion are present in the thesis sources and checked PDFs. They are not merely artifacts of reading old blog posts. Use section/equation identifiers when citing the thesis, since pagination differs between PDFs.

The related least-squares posts and Appendix B.1 are outside this five-post series. Appendix B.3's Mahalanobis/chi-square proof can be mentioned as a further topic, but a new treatment of it is not needed for this merge.

## 2. Comparison and editorial decisions

| Topic | What the thesis contributes | What survives from the blog | Merge decision |
| --- | --- | --- | --- |
| Motivation | Concrete streaming anomaly-detection context; SORAD and DWT-MLEAD | Approachable explanation of processing one observation at a time | Write a standalone introduction based on the thesis. |
| Ordinary mean and covariance | Obtained by setting all weights to one and batch size to one | Worked Gaussian example, scalar specialization, R code, convergence plot | Keep this as the gentle entry point, using the thesis's scatter-matrix derivation specialized to the unweighted case. |
| Weighted mean and covariance | General batch derivation, both weight sums, normalization choices | Single-observation derivation | Present the common derivation once; show the online specialization explicitly. |
| Exponential forgetting | Fixed-size batches, forgetting once per batch, squared-weight recurrence, algorithm summary | Online intuition and drift simulation | Give forgetting its own article to keep the weighted article manageable. |
| Covariance of the estimated mean | Nearly the same derivation as the blog, with a clearer final IID statement | Explanatory distinction between data covariance and uncertainty in the mean | Follow the thesis's expansion and diagonal/off-diagonal split; state assumptions before using them. |
| Estimator memory | Corrected cancellation of the covariance matrix; finite-sample expression and limit | Useful failed-guess experiment at 100 observations and successful comparison at 199 | Keep the thesis algebra and the blog's two-stage experiment, with a precise definition of memory. |
| Inverse covariance | Woodbury batch derivation in addition to Sherman–Morrison | R implementation | Follow the thesis, explain matrix sizes, and reuse the implementation after the approved initialization fix. |

Avoid repeating B1's three alternative covariance derivations. Retain the thesis's sequence: define the weighted scatter matrix, expand it, subtract the old scatter, substitute the old/new mean relation, and factor the result. Intermediate steps that explain a transformation remain visible.

## 3. Implemented seven-post schedule

All dates are publication dates in 2026, beginning on **1 February** and separated by **14 days**. Front matter will use ISO dates to avoid ambiguity.

| Part | Date | Planned file under `_posts/` | Contents and sources |
| --- | --- | --- | --- |
| 1 | 2026-02-01 | `2026-02-01-online-estimation-introduction.md` | Why streaming estimates matter; changing normality; SORAD prediction errors and DWT-MLEAD feature vectors; role of means, covariances, and Mahalanobis scores; series map and notation. T5–T7 and T1 introduction. |
| 2 | 2026-02-15 | `2026-02-15-online-mean-and-covariance.md` | Ordinary sample mean, scatter matrix, one-observation derivation, scalar case, initialization, Gaussian ML versus unbiased covariance, R and NumPy examples with legacy and new convergence plots. T1 specialized to unit weights; B1 and P1–P2. |
| 3 | 2026-03-01 | `2026-03-01-weighted-mean-and-covariance.md` | Normalized/unnormalized weights, frequency versus deterministic reliability weights, unbiased normalization, full mini-batch derivation, online specialization, update order, NumPy weighted-batch example checked against direct estimates. T1 §B.2.1; B2 and P1–P2. |
| 4 | 2026-03-15 | `2026-03-15-exponentially-weighted-estimation.md` | Batch-age weights, geometric weight sums, recursive mean and scatter, online specialization, the no-forgetting limit, drift example, interpretation of decay per batch and per observation; shared-stream Python comparison. T1 §B.2.2; B2, B4, and P1–P2. |
| 5 | 2026-03-29 | `2026-03-29-covariance-of-weighted-means.md` | Covariance of the estimator rather than of the data; paired observations; expectation expansion; diagonal/off-diagonal terms; IID result; vector form, equal-weight check, and correct mean-weight normalization with a Python demonstration. T2; B3 and P1–P2. |
| 6 | 2026-04-12 | `2026-04-12-memory-of-exponential-estimators.md` | Why the sum of weights is not the variance-equivalent sample size; finite-sample memory; limiting formula; 100-versus-199 simulation; limits of the window analogy, finite-sample Python simulation, and distinction from covariance-estimator uncertainty. T3; B4 and P1–P2. |
| 7 | 2026-04-26 | `2026-04-26-online-inverse-covariance.md` | Mahalanobis motivation; scatter-to-covariance scaling; Woodbury batch derivation; Sherman–Morrison specialization; invertibility and initialization; corrected R and NumPy examples; rank, initialization, regularization, and efficient matrix products. T1 §B.2.2.1; B5 and P1–P2. |

The expansion from five to seven articles comes from adding an introduction and separating arbitrary weighting from exponential forgetting. This accommodates the thesis's extra batch material without making one article disproportionately long.

## 4. Notation and mathematical presentation

Use the notation actually printed by the thesis macros:

| Symbol | Meaning |
| --- | --- |
| $\mathbf{x}_i$ | Observed column vector |
| $\bar{\mathbf{x}}_n$ | Estimated mean after observing $n$ examples |
| $\bar{\mathbf{M}}^{(n)}$, later $\bar{\mathbf{M}}_n$ | Weighted scatter matrix; explain the index change before the inverse derivation, as in the thesis |
| $\bar{\boldsymbol{\Sigma}}_n$ | Estimated covariance; explicitly label its normalization |
| $\boldsymbol{\Sigma}$ | Population covariance |
| $w'_i$, $w_i$ | Unnormalized and normalized weights |
| $W_n$, $W_n^{(2)}$ | Sum of weights and sum of squared weights |
| $\mu$, $M=n/\mu$, $k=n-\mu+1$ | Batch size, number of batches, first index of the current batch |
| $\boldsymbol{\Delta}_i$ | Difference from the mean before the current batch; define historical versions explicitly when unrolling |
| $\lambda$ | Forgetting factor, with decay once per batch in the batch formulation |
| $\mathbf{D}_n$, $\boldsymbol{\mathcal{X}}_n$ | Batch matrices of residuals before and after the mean update |
| $n_{\mathrm{mem}}$ | Variance-equivalent sample size for the mean |

Keep $\mu$ for batch size; use the thesis's population-mean notation with a subscript where needed to distinguish it. The temporary batch-sum vector called $\boldsymbol{\Sigma}_j$ in T1 is visually confusable with covariance: write its defining sum explicitly in the new article instead of introducing another symbol. Explain that the legacy drift graphic's `Q` means $\lambda$.

Expand thesis-only LaTeX macros into standard math commands in Markdown. Use self-contained equations, clear display-math delimiters, and unique equation labels where references are useful. Do not require the thesis's `definitions.tex` to render the articles.

State the statistical assumptions where they enter. Incremental arithmetic identities do not require Gaussian data. The unbiased reliability-weight correction and the simplified covariance-of-means formula require the appropriate fixed-weight, common-distribution assumptions. Actual time-series observations need not be independent; the memory result must not be presented as universal for correlated streams.

## 5. Existing artifacts to retain

These paths are relative to this repository unless they start with `/home/mthill/PhD/`. The porting agent must preserve the historical directory spelling `coviarance` when copying existing images, or update every reference consistently.

| Artifact | Intended use | Provenance / handling |
| --- | --- | --- |
| [Gaussian convergence plot](../images/2017-11-20-online-estimation-of-gaussians/estimator.png) | Part 2 | B1. Existing graphic uses the unbiased covariance normalization. Caption will say so. |
| [Density comparison at 100 observations](../images/2018-01-13-online-estimation-of-weighted-sample-mean-and-coviarance-matrix/distriMeans.png) | Part 6 | B4, Gaussian simulation; illustrates the incorrect initial memory guess. |
| [Density comparison at 199 observations](../images/2018-01-13-online-estimation-of-weighted-sample-mean-and-coviarance-matrix/distriMeans2.png) | Part 6 | B4, Gaussian simulation; illustrates matched covariance of the means. |
| [Drift and forgetting plot](../images/2018-01-13-online-estimation-of-weighted-sample-mean-and-coviarance-matrix/forgetting.png) | Part 4 | B4. Different streams have different baseline means. Label `Q` as $\lambda$; document the plot/code jump-size discrepancy from the review. |
| [Existing feature image](../images/stats.jpg) | Shared front-matter feature image | Referenced by all five original posts; list it explicitly in each new post that uses it. |
| [Thesis density figure](/home/mthill/PhD/Thesis.d/appendix/Figures.d/density-weighted-mean.pdf) | Optional supplementary download in Part 6 | T3 / Figure B.1 uses uniform data, unlike the blog's Gaussian experiment. Preserve this distinction. If included, copy the PDF into the new series' asset directory and reference that copy. |
| [Weighted-estimation bibliography](../_bibliography/onlineEstimation.bib) | Part 3 reference provenance | `price1972extension`. |
| [Inverse-estimation bibliography](../_bibliography/onlinemlead.bib) | Part 7 reference provenance | `sherman1950adjustment`, `woodbury1950inverting`; review the incorrect DOI attached to the latter before reuse. |
| [Thesis bibliography](/home/mthill/PhD/Thesis.d/bib/thesis.bib) | Reference provenance for all articles | Copy only relevant entries into any new series bibliography. |

The R code for this series is embedded in B1, B4, and B5; no separate R source files are linked by those five posts. The following files now contain adapted versions of those blocks, with origins in comments:

- `assets/examples/online-estimation/online-mean-covariance.R` — B1's estimator and convergence example.
- `assets/examples/online-estimation/forgetting-drift.R` — B4's drift simulation.
- `assets/examples/online-estimation/estimator-memory.R` — B4's two density comparisons.
- `assets/examples/online-estimation/inverse-covariance.R` — B5's inverse example.
- `assets/examples/online-estimation/README.md` — dependencies, run instructions, seeds, differences from legacy examples, and which historical graphics are reused.

All four R scripts and the companion README now exist. They use explicit `MASS::mvrnorm` calls where needed, modest simulation defaults, and reproducible seeds. An R runtime was unavailable, so these scripts were reviewed but not executed. Historical images lack recorded seeds, so the adapted scripts must not claim pixel-identical reproduction. Reuse the existing images as historical examples and identify them accordingly.

## 6. Portability contract for each new post

Each new Markdown file will include:

1. Valid front matter with its scheduled date, title, description, categories, and tags.
2. Series navigation and explicit links to the other parts, with source filenames listed for migration.
3. Normal Markdown image links, descriptive alt text, and captions that define the plotted quantities.
4. Fenced R/Python code and links to extracted `.R` and `.py` files; link the runnable companion notebook from the relevant parts and record its exact `.ipynb` path for migration.
5. A compact HTML comment titled `Migration dependencies`, containing exact repository-relative paths for every image, downloadable example, optional PDF, bibliography source, and sibling post it depends on. Mark runtime/copy dependencies separately from historical provenance.
6. Thesis source paths and section/equation identifiers in a source note or provenance comment. These external local files are editorial sources, not assumed public site URLs or mandatory runtime assets.
7. Plain reference entries with verified links where available, so citations do not depend on a bibliography plugin in the destination repository.

The old posts use [`_includes/image.md`](../_includes/image.md), `{% highlight %}`, `{% post_url %}`, and Jekyll Scholar citation tags. Replace the image/highlight/citation dependencies with portable Markdown in the new articles. Current-site navigation can use `post_url`, provided the migration comment also records the corresponding Markdown filenames. Math rendering remains a capability the destination site must support; the formulas themselves will not require custom site macros.

## 7. Execution and verification

1. Apply the agreed mathematical decisions to the new writing only, recording departures from the thesis in provenance notes.
2. Draft the introduction and Part 2 to establish the voice and notation; then write Parts 3–7 following the outline above.
3. Extract the relevant R examples and reuse the validated NumPy companion. Make the approved corrections and connect historical and newly generated figures to accurate captions. Apply the notebook cell changes listed in the Python review as a separate, traceable migration step.
4. Validate YAML front matter, scheduled dates, fenced blocks, display-math delimiters, LaTeX environment pairs, equation references, series links, and local artifact paths.
5. Check the adapted numerical examples against direct weighted means, scatter matrices, and inverses, including startup behavior, $\lambda=1$, one-observation updates, and batches. Report honestly whether an R runtime was available; none was found during this comparison.
6. Review the final copy manifest against every image/code/PDF/reference actually used. Do not run Jekyll or Ruby.

Completed mathematical checks during comparison: exact rational arithmetic on 132 weighted/decaying batch states and 75 inverse updates, across batch sizes 1, 2, and 3 and decay factors 1, 1/2, and 99/100. These confirm the central final recurrences against direct calculations; the [review](online-estimation-derivation-review.md) gives counterexamples for the erroneous intermediate expressions. This is not a claim that the original R scripts have been executed.

All mathematical corrections, including the mean-weight normalization in P1/P2 documented in §3 of the Python review, are approved and implemented in the new articles and corrected notebook.


## 8. Python notebook integration and generated examples

**Keep the seven-post schedule.** The notebook is a runnable companion to Parts 2–7, not an eighth theory article. Keep the existing destination wrapper's 2025 date unless separately asked to change it. Each article should contain its essential derivation and a focused example, with a link to the notebook for the complete experiment. Retain useful R code and legacy graphics.

The notebook audit explains the old mini-batch problem: the first scatter is necessarily singular in its 300-dimensional, 10–19-observation setup. The pre-correction destination notebook's inverse instead tracks an implicit ridge term that is absent from its reported covariance; a seeded example gives a 21.9% inverse mismatch. Its main mean/scatter recurrences are correct. The pre-correction notebook had the squared-weight typo in displayed math; its executable recurrence was already correct. The corrected notebook fixes the display.

The [cell-by-cell review](online-estimation-python-review.md) lists every reviewed correction, including mean-weight normalization, inverse initialization, startup handling, per-batch forgetting, theoretical annotations, typing, plotting API usage, reference calculations for forgetting, benchmark fairness, and the wrapper's wrong notebook-existence check. Preserve that review with the migration handoff.

| Existing new artifact | Role in the series / migration |
| --- | --- |
| [NumPy estimator](../assets/examples/online-estimation/online_estimation.py) | Shared example code for Parts 2–7; optional inverse updates begin after a valid initial solve. Documents batch decay and explicit observation weights. |
| [Original-class audit](../assets/examples/online-estimation/audit_notebook.py) | Reproduces notebook issues and tests the shared implementation against direct weighted calculations. |
| [Audit results](../assets/examples/online-estimation/audit-results.json) | Source fingerprints, exact inspected file paths, environment, numerical findings, and validation results. |
| [Plot generator](../assets/examples/online-estimation/generate_examples.py) | Seeded, modest-size examples; regenerates all new figures. |
| [Figure results](../assets/examples/online-estimation/figure-results.json) | Numerical values and inverse-error traces used by the figures. |
| [Requirements](../assets/examples/online-estimation/requirements.txt) and [README/copy manifest](../assets/examples/online-estimation/README.md) | Tested NumPy/Matplotlib versions, commands, source provenance, example API, and exact artifact paths. |
| [Convergence PNG](../images/2026-online-estimation/python-convergence.png) / [SVG](../images/2026-online-estimation/python-convergence.svg) | Part 2: Python version of the original three-dimensional Gaussian experiment. |
| [Forgetting PNG](../images/2026-online-estimation/batch-forgetting.png) / [SVG](../images/2026-online-estimation/batch-forgetting.svg) | Part 4: the same stream processed online or in batches; shows the effect of decay convention. |
| [Mean-weight PNG](../images/2026-online-estimation/mean-weight-normalization.png) / [SVG](../images/2026-online-estimation/mean-weight-normalization.svg) | Parts 5–6: simulation and analytic comparison of correct versus notebook normalization. This illustrates the approved correction using the preserved original as the diagnostic reference. |
| [Inverse PNG](../images/2026-online-estimation/inverse-initialization.png) / [SVG](../images/2026-online-estimation/inverse-initialization.svg) | Part 7: implicit regularization and legacy rank deficiency. |

The examples used the existing environment at `/home/mthill/MarkusThill.github.io/tools/.venv/bin/python`. No new environment was installed. Tests cover the NumPy backend only. The companion passed 432 weighted prefix checks and 396 inverse comparisons; the maximum relative inverse error in that test set was approximately $2.5\times10^{-14}$. The original expensive GPU-dependent notebook was not executed end-to-end. The corrected notebook was: all nine Python cells passed, including 480 weighted-prefix checks and 450 inverse comparisons, with maximum relative inverse error about $2.0\times10^{-13}$. The local runner executes sequential plain Python cells and captures notebook stdout and figures; no Jupyter kernel package is installed.

When porting, copy the Python directory and each image referenced by a post. Each post's dependency comment must also identify the notebook path `assets/jupyter/MarkusThill.github.io-jupyter/2025_09_27_online_estimate_cov_mu.ipynb` and wrapper `_posts/2025-09-26-online-batch-estimate-cov-mu.md` when it links the companion. These already exist in the destination repository; the migration agent should update them there rather than create an unexplained second notebook. The historical embedded PNGs from original cells 19/21 are preserved byte-for-byte in the notebook backup. Reproducible figures replace them in the corrected notebook. The backup also supplies the original classes to the historical audit.

Completed: source comparison; approved mathematical and Python corrections; all seven articles; four R adaptations; existing-notebook backup and revision; wrapper correction; Python experiments and exported figures; article syntax, navigation, and dependency checks. Publication and migration remain the user's later task. No Jekyll or Ruby was run.

Additional delivered artifacts:

- `images/2026-online-estimation/notebook-memory-comparison.png` and `.svg`: the seeded 100-versus-199 comparison used by Part 6.
- `images/2026-online-estimation/notebook-convergence.png` and `.svg`, and `notebook-batch-forgetting.png` and `.svg`: exports of the notebook's other plots.
- `assets/examples/online-estimation/density-weighted-mean-thesis.pdf`: the thesis's uniform-data illustration, clearly distinguished from Gaussian blog simulations.
- `assets/examples/online-estimation/execute_notebook.py` and `notebook-validation.json`: reproducible execution and results.
- `docs/online-estimation-backups.json`: exact original paths, backup paths, and SHA-256 hashes.
- `docs/online-estimation-migration-handoff.md`: final copy instructions and validation limits.

The notebook consolidates the two duplicated estimator classes into `IncrementalMoments`, embedding the same implementation as `online_estimation.py`. Its API changes are documented in a notebook cell. It supports NumPy only; it does not promise JAX/GPU compatibility. Explicit regularization is explained and illustrated by the R script, while Python defaults to an unregularized warm-up.
