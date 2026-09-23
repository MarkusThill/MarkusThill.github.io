# Mathematical review before merging the online-estimation series

Status: the author approved corrections A–F and the smaller repairs in G. They have not been applied to the thesis or original posts. The additional notebook-specific normalization correction in the [Python review](online-estimation-python-review.md) has also been approved. All corrections are applied to the seven new posts and the revised destination notebook; historical sources remain unchanged. The requested series structure and artifact inventory are in the [merge plan](online-estimation-series-merge-plan.md).

The central weighted/batch mean and scatter recurrences, the specialized inverse updates, and the finite-sample memory formula check out. Several intermediate equations, one algorithm-summary equation, and one implementation need correction. Some are likely typographical in origin, but they affect mathematical meaning or numerical results, so they are being raised before drafting.

## A. Thesis forgetting derivation uses the wrong time index

Source: [`appendix/onlinemeancov.tex`, lines 178–187](/home/mthill/PhD/Thesis.d/appendix/onlinemeancov.tex:178), the expansion leading to Eq. (B.62). The same current-mean indexing appears in the checked PDFs.

The historical sum uses $\mathbf{x}_i-\bar{\mathbf{x}}_n$ for every previous batch. When unrolling the recurrence, each historical contribution must use the mean at the end of its own batch, $\bar{\mathbf{x}}_{n_j}$, with $n_j=j\mu$. Its residual $\boldsymbol{\Delta}_i$ must likewise refer to that batch's previous mean, $\bar{\mathbf{x}}_{n_j-\mu}$.

The final recurrence itself is correct:

$$
\bar{\mathbf{M}}^{(n)}
=\lambda\bar{\mathbf{M}}^{(n-\mu)}
+\sum_{i=k}^n\boldsymbol{\Delta}_i
(\mathbf{x}_i-\bar{\mathbf{x}}_n)^{\mathsf T}.
$$

**Exact counterexample.** Let $x_1=0$, $x_2=2$, $x_3=4$, $\mu=1$, $\lambda=1/2$, and start from zero weight and scatter. The means are $0$, $4/3$, and $20/7$. The direct weighted scatter and final recursive update both give $26/7$. The printed historical sum, interpreting each $\Delta_i$ as its historical update residual but using the current mean everywhere, gives $46/21$.

**Proposed treatment:** retain the thesis's update and derivation strategy. First justify it by multiplying all existing weights and the old scatter by $\lambda$, then applying the already derived weighted batch update with new weights equal to one. If displaying the unrolled expression, use historical batch means:

$$
\bar{\mathbf{M}}^{(n)}
=\sum_{j=1}^{M}\lambda^{M-j}
\sum_{i=k_j}^{n_j}
(\mathbf{x}_i-\bar{\mathbf{x}}_{n_j-\mu})
(\mathbf{x}_i-\bar{\mathbf{x}}_{n_j})^{\mathsf T},
$$

for zero initial scatter. This repairs the intermediate reasoning without changing the thesis's final algorithm.

## B. Thesis online summary propagates the wrong weight sum

Source: [`appendix/onlinemeancov.tex`, line 283](/home/mthill/PhD/Thesis.d/appendix/onlinemeancov.tex:283), Eq. (B.78) in both checked PDFs.

The printed equation is

$$
W_n^{(2)}=\lambda^2 W_{n-1}+1.
$$

The previous term must also be the **sum of squared weights**:

$$
W_n^{(2)}=\lambda^2 W_{n-1}^{(2)}+1.
$$

The thesis already gives the correct general batch version at lines 151 and 254. With $\lambda=1/2$ and three observations, the correct squared-weight sum is $21/16$, while the printed online summary gives $11/8$. This changes the denominator of the unbiased weighted covariance estimate.

**Proposed treatment:** use the correct specialization of the thesis's batch formula and record the missing superscript as an erratum in the new post's provenance note.

## C. General Woodbury identity contains an extra plus sign

Source: [`appendix/onlinemeancov.tex`, line 196](/home/mthill/PhD/Thesis.d/appendix/onlinemeancov.tex:196), Eq. (B.63) in both checked PDFs.

Inside the inverse, the thesis prints

$$
\mathbf{C}^{-1}+\mathbf{V}\mathbf{A}^{-1}+\mathbf{U}.
$$

It must be

$$
\mathbf{C}^{-1}+\mathbf{V}\mathbf{A}^{-1}\mathbf{U}.
$$

The printed sum is not even dimensionally defined for the intended rectangular batch matrices. The later specialized batch-inverse formula in the thesis uses the correct product and passes direct-inverse checks.

**Proposed treatment:** correct the displayed general identity; preserve the specialized derivation and final update. State the needed invertibility conditions and matrix dimensions.

## D. The memory derivation needs a narrower statistical claim

Sources: [`appendix/onlineestimatormemory.tex`, lines 51–73](/home/mthill/PhD/Thesis.d/appendix/onlineestimatormemory.tex:51), and the corresponding [original memory article](../_posts/2018-02-03-memory-of-an-exponentially-weighted-estimator-of-the-arithmetic-mean-and-covariance-matrix.md).

The thesis invokes the central limit theorem and writes an exact normal distribution for an ordinary sample mean. Normality is exact for IID Gaussian observations. For general IID observations with finite variance, a finite-sample mean need not be normally distributed; the usual CLT describes an asymptotic approximation after standardization. A fixed exponential forgetting factor also does not force an arbitrary input distribution's weighted mean to become Gaussian merely by extending the stream.

The useful result here needs no normality claim. Under the thesis's IID assumptions and deterministic weights,

$$
\operatorname{Cov}(\bar{\mathbf{X}}_n)
=\boldsymbol{\Sigma}\sum_{i=1}^n w_i^2,
\qquad
n_{\mathrm{mem}}(n)=\frac{1}{\sum_{i=1}^n w_i^2}
=\frac{W_n^2}{W_n^{(2)}}.
$$

Thus the thesis's finite-sample expression and limit remain:

$$
n_{\mathrm{mem}}(n)
=\left(\frac{1-\lambda^n}{1-\lambda}\right)^2
\frac{1-\lambda^2}{1-\lambda^{2n}},
\qquad
\lim_{n\to\infty}n_{\mathrm{mem}}(n)
=\frac{1+\lambda}{1-\lambda},
\quad 0<\lambda<1.
$$

**Proposed treatment:** define memory as the sample size of an ordinary mean with the same covariance. Keep the thesis's geometric-sum derivation. Explain that this is neither a hard cutoff of old observations nor a proof that the covariance-matrix estimator has the same sampling distribution or estimation error as a windowed estimator. The derivation matches uncertainty in the **mean**, even though the mean and scatter share a forgetting factor. For $\lambda=1$, handle the equal-weight case directly: $n_{\mathrm{mem}}=n$.

This is a substantive clarification of the thesis's interpretation, not a change to the final memory formula. The thesis's uniform-data figure and the blog's Gaussian-data figures should retain their distinct captions.

## E. The old unweighted mini-batch equation is numerically wrong

Source: [original unweighted article, mini-batch equation](../_posts/2017-11-20-online-estimation-of-gaussians.md), immediately before the unbiased covariance normalization.

The expression involving $(n+\mu-1)$ does not generally update the scatter correctly. With old observations $(0,2)$ and a new batch $(4,6)$, so $n=4$ and $\mu=2$, it gives a final scatter of **12**. Direct computation gives **20**. The thesis's weighted batch formula with unit weights gives **20** as well.

**Proposed treatment:** replace this blog-only detour with the thesis's valid batch derivation, specialized to unit weights when needed. Do not propagate the old mini-batch formula.

## F. The inverse example initializes inconsistent states

Source: [original inverse article, R example](../_posts/2018-10-14-online-estimation-of-the-inverse-covariance-matrix.md).

It initializes both `M` and `Mminus` to `0.01 * diag(d)`. They cannot be a matrix/inverse pair: their product is $10^{-4}\mathbf{I}$ rather than $\mathbf{I}$. Forgetting can hide this discrepancy after a long run, but early estimates do not describe the same matrix.

**Proposed treatment:** retain the regularized demonstration with `M <- 0.01 * diag(d)` and initialize `Mminus <- solve(M)`, which is `100 * diag(d)`. Explain that the initial positive-definite scatter is regularization, and its contribution decays with the recurrence. This is distinct from starting with the exact zero scatter of an empty sample. For an unregularized implementation, wait until sufficient nondegenerate data make the scatter invertible before starting inverse updates. Compare the maintained inverse with the inverse of the same scatter throughout the demonstration, not just after 100,000 observations.

## G. Smaller editorial, notation, and example repairs

These do not require a replacement mathematical method, but should be documented while merging:

| Issue | Source | Proposed handling |
| --- | --- | --- |
| Calling the $1/(n-1)$ covariance estimate maximum likelihood | B1 opening and title | Distinguish the Gaussian ML estimate (divide by $n$) from the unbiased estimate (divide by $n-1$), consistent with the thesis's normalization discussion. Preserve and correctly label the unbiased example. |
| $X_iY_j$ in the diagonal sum with only $i$ bound | T2 lines 49, 57–65; B3 | Use $X_iY_i$ in the diagonal terms. Keep the thesis's diagonal/off-diagonal proof. |
| An isolated wrong sign in a weighted derivation line | B2, expansion after substituting the mean expressions | Use the thesis's corresponding correct expansion. |
| A stray covariance matrix in the formula for scalar $n_{\mathrm{mem}}$ | B4 | Follow T3, which already correctly cancels the common covariance factor. |
| Exact formulas with $1-\lambda$ denominators used alongside $\lambda=1$ | T1/T3 and B2/B4 | Restrict the geometric closed forms to $\lambda<1$ and provide $\lambda=1$ separately. Use $0<\lambda\leq1$ for the inverse treatment. |
| Standard error versus variance of the mean | T2 and B3 introductions | State that $\sigma^2/n$ is the variance; its square root is the standard error. |
| Definition of “unbiased” is too broad without assumptions | T1/B2 normalization discussion | Distinguish frequency weights from fixed reliability weights; state independent common-population assumptions. Do not claim unbiasedness for arbitrary data-dependent weights or drifting populations. |
| Cross-products compressed before explaining the sum | T1 lines 74–79 and B1/B2 | Keep both transpose terms until using $\sum w'_i\mathbf{x}_i=W_n\bar{\mathbf{x}}_n$. Their **sums** agree; individual outer products generally do not. This is a presentation clarification, not an error in the summed identity. |
| R calls `mvrnorm` while only loading `mvtnorm` | B1 and the first B4 simulation | Use `MASS::mvrnorm`, as specified by the [official R documentation](https://stat.ethz.ch/R-manual/R-devel/library/MASS/html/mvrnorm.html). |
| B1 estimator has undefined `cov` for a single observation | B1 first R function | Define startup behavior explicitly; an unbiased covariance is unavailable before two observations. |
| Legacy drift graphic and script do not show the same jump | B4 `getMeanSeries` and `forgetting.png` | The code adds 5 to the first half; the graphic's baselines indicate a jump of about 2. Keep the historical graphic and identify it as such. Adapt the demonstrator to a documented jump of 2, with a new seed, without claiming to reproduce the original random trace. |
| Thesis and blog density examples differ | T3 Figure B.1 versus B4 `distriMeans2.png` | Thesis caption says uniform data and $10^4$ samples; blog code samples a multivariate Gaussian and uses 100,000 simulation replicates. Do not present one graphic as the output of the other experiment. |
| Incorrect DOI in Woodbury bibliography entry | [`_bibliography/onlinemlead.bib`](../_bibliography/onlinemlead.bib), `woodbury1950inverting` | `10.1137/1031049` identifies Hager's *Updating the Inverse of a Matrix*, not Woodbury's 1950 report. Omit that DOI from the Woodbury reference or cite Hager separately. Verified against the [publisher's record](https://epubs.siam.org/doi/10.1137/1031049). |
| Inverse post filename and front-matter date disagree | B5 | New posts receive consistent filenames and scheduled ISO dates. |

## H. Verification performed and approval received

The equations were checked using direct algebra and exact rational arithmetic, independently of the legacy R scripts:

- 132 weighted/decaying batch states matched direct weighted means and scatter matrices, using three-dimensional observations, batch sizes 1, 2, and 3, and decay factors 1, 1/2, and 99/100. Arbitrary positive fixed weights were also included.
- 75 Woodbury inverse updates, including the single-observation specialization, matched direct matrix inversion once the preceding scatter was invertible.
- The three-point and four-point counterexamples above distinguish the erroneous printed expressions from the correct recurrences without floating-point ambiguity.
- The finite-sample memory expression matched direct squared-weight calculations for $\lambda=1/2$ at sample sizes 1, 2, 10, and 1000. The limiting expression gives 199 for $\lambda=0.99$.

These checks establish agreement for the tested cases and support the algebraic review. They are not a substitute for the stated assumptions, and the original R examples have not been executed: an R runtime was not found. No Jekyll or Ruby build was run.

**Approval received:** carry corrections A–F and the smaller repairs in G into the new series, preserving the valid thesis derivations, notation, and final recurrences. These corrections do not require another approval. The subsequent Python normalization correction is also approved and implemented. See the [handoff](online-estimation-migration-handoff.md) for completed artifacts and verification.
