"""Generate portable PNG/SVG figures for the proposed Python companion.

The inverse audit uses the original destination notebook's NumPy class.
Other panels use the thesis-based IncrementalMoments reference or direct
weighted simulations. See README.md for provenance and precise interpretations.
"""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from audit_notebook import DEFAULT_NOTEBOOK, HERE, ROOT, relative_error, source_classes
from online_estimation import IncrementalMoments


TEAL, CORAL, GOLD, NAVY = "#147d92", "#d75b48", "#a66d17", "#25324b"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.titlesize": 13, "axes.labelsize": 11, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#aab4c0", "axes.labelcolor": NAVY,
    "text.color": NAVY, "xtick.color": NAVY, "ytick.color": NAVY,
    "grid.color": "#dce3e9", "grid.alpha": .65,
    "legend.frameon": False, "legend.fontsize": 9,
    "figure.facecolor": "white", "savefig.facecolor": "white",
    "svg.hashsalt": "online-estimation-2026",
})


def save(fig, output, name):
    for suffix in ("png", "svg"):
        metadata = {"Date": None} if suffix == "svg" else None
        fig.savefig(output / f"{name}.{suffix}", dpi=160, bbox_inches="tight", metadata=metadata)
    plt.close(fig)


def inverse_figure(output, notebook, legacy):
    _, classes, _ = source_classes(notebook, legacy)
    notebook_state = classes["BatchCovarianceMeanEstimator"](np, 4, 1.)
    reference = IncrementalMoments(4, track_inverse=True)
    rng = np.random.default_rng(20260201)
    data = .01 * rng.normal(size=(300, 4))
    counts, errors, hidden_errors, corrected_errors = [], [], [], []
    for i in range(0, len(data), 5):
        batch = data[i:i+5]
        notebook_state.update(batch)
        reference.update(batch)
        n = i + len(batch)
        cov = np.cov(data[:n], rowvar=False)
        precision = np.linalg.solve(cov, np.eye(4))
        centered = data[:n] - data[:n].mean(0)
        hidden = np.linalg.solve(centered.T @ centered + 1e-3*np.eye(4), np.eye(4)) * (n-1)
        counts.append(n)
        errors.append(relative_error(notebook_state.get_cov_inv(), precision))
        hidden_errors.append(relative_error(notebook_state.get_cov_inv(), hidden))
        corrected_errors.append(relative_error(reference.precision(), precision))
    fig, ax = plt.subplots(1, 2, figsize=(12.2, 4.8), layout="constrained")
    fig.suptitle("Why the inverse estimates disagree", fontsize=17, fontweight="bold")
    floor = 1e-16
    ax[0].semilogy(counts, np.maximum(errors, floor), color=CORAL, lw=2.3,
                   label="Notebook vs. unregularized inverse")
    ax[0].semilogy(counts, np.maximum(hidden_errors, floor), color=GOLD, lw=1.5,
                   label="Notebook vs. inverse with implicit ridge")
    ax[0].semilogy(counts, np.maximum(corrected_errors, floor), color=TEAL, lw=1.5,
                   label="Consistent initialization vs. direct inverse")
    ax[0].set(title="Original notebook: inconsistent initial states",
              xlabel="Observations processed", ylabel="Relative Frobenius error")
    ax[0].grid(axis="y")
    ax[0].legend(loc="center right")
    ax[0].text(.97, .96, "4 dimensions · batches of 5\nsmall-scale, well-conditioned population",
               transform=ax[0].transAxes, ha="right", va="top", fontsize=9)
    n = np.arange(1, 341)
    ax[1].plot(n, np.minimum(n-1, 300), color=TEAL, lw=2.3,
               label="Maximum possible centered-scatter rank")
    ax[1].axhline(300, color=NAVY, ls="--", lw=1.3, label="Rank needed for an inverse")
    ax[1].axvspan(10, 19, color=CORAL, alpha=.2, label="First batch in the legacy example")
    ax[1].annotate("At most rank 18\nfor a 300 × 300 matrix",
                   xy=(19, 18), xytext=(85, 80), color=CORAL,
                   arrowprops={"arrowstyle": "->", "color": CORAL})
    ax[1].set(title="Legacy code: inversion before sufficient rank",
              xlabel="Observations processed", ylabel="Rank", xlim=(0, 340), ylim=(0, 330))
    ax[1].legend(loc="upper left", bbox_to_anchor=(0, .84))
    ax[1].grid(axis="y")
    save(fig, output, "inverse-initialization")
    return {"observations": counts, "notebook_precision_relative_errors": errors,
            "notebook_implicit_ridge_relative_errors": hidden_errors,
            "reference_precision_relative_errors": corrected_errors}


def memory_figure(output):
    rng = np.random.default_rng(20260412)
    decay, length, repetitions = .8, 80, 20000
    weights = decay**np.arange(length-1, -1, -1)
    weights /= weights.sum()
    q = weights @ weights
    actual = []
    for _ in range(repetitions // 500):
        data = rng.normal(1, np.sqrt(3), size=(500, length))
        actual.append(data @ weights)
    means = np.concatenate(actual)
    variance = 3*q
    wrong_variance = variance/(1-q)**2
    empirical_variance = means.var(ddof=1)
    # Monte Carlo variability of a Gaussian variance estimate: relative SD sqrt(2/(R-1)).
    assert abs(empirical_variance/variance-1) < 4*np.sqrt(2/(repetitions-1))
    fig, ax = plt.subplots(1, 2, figsize=(12.2, 4.8), layout="constrained")
    fig.suptitle("Normalize the weights of a mean by their sum", fontsize=17, fontweight="bold")
    ax[0].hist(means, bins=60, density=True, color=TEAL, alpha=.25,
               label="20,000 simulated weighted means")
    x = np.linspace(-1.5, 3.5, 500)
    for var, color, label in [(variance, TEAL, "Correct theoretical variance"),
                              (wrong_variance, CORAL, "Notebook normalization")]:
        y = np.exp(-(x-1)**2/(2*var))/np.sqrt(2*np.pi*var)
        ax[0].plot(x, y, color=color, lw=2.2, label=label)
    ax[0].set(title=r"A visible example: $\lambda=0.8$, $n=80$",
              xlabel="Weighted sample mean", ylabel="Density")
    ax[0].legend(loc="upper left", fontsize=8)
    ax[0].grid(axis="y")
    lam = np.linspace(.5, .995, 250)
    w = lam[:, None]**np.arange(500)[None, :]
    normalized = w/w.sum(axis=1, keepdims=True)
    q = np.sum(normalized**2, axis=1)
    percent_error = 100*((1-q)**-2-1)
    ax[1].plot(lam, percent_error, color=CORAL, lw=2.3)
    for rate, offset in [(.8, (-75, 38)), (.99, (-145, 35))]:
        w = rate**np.arange(500)
        q = np.sum((w/w.sum())**2)
        error = 100*((1-q)**-2-1)
        ax[1].scatter([rate], [error], color=CORAL, zorder=3)
        ax[1].annotate(f"λ = {rate}: +{error:.2f}%", (rate, error), xytext=offset,
                       textcoords="offset points", arrowprops={"arrowstyle": "->", "color": CORAL})
    ax[1].set(title="Error in predicted variance, after 500 observations",
              xlabel=r"Forgetting factor $\lambda$", ylabel="Variance overstatement (%)", ylim=(0, 135))
    ax[1].grid(axis="y")
    save(fig, output, "mean-weight-normalization")
    return {"lambda": decay, "observations": length, "replicates": repetitions,
            "empirical_mean_variance": float(empirical_variance),
            "correct_mean_variance": float(variance),
            "notebook_mean_variance": float(wrong_variance)}


def forgetting_figure(output):
    rng = np.random.default_rng(20260315)
    length, change, batch_size, rate = 1200, 600, 20, .98
    true_mean = np.where(np.arange(length) < change, 0., 4.)
    data = true_mean + rng.normal(0, 1, size=length)
    online = IncrementalMoments(1, rate)
    same_rate = IncrementalMoments(1, rate)
    adjusted = IncrementalMoments(1, rate**batch_size)
    exact = IncrementalMoments(1)
    online_means = []
    for x in data:
        online.update([x])
        online_means.append(online.mean[0])
    batch_means, adjusted_means, exact_means, endpoints = [], [], [], []
    for i in range(0, length, batch_size):
        batch = data[i:i+batch_size, None]
        same_rate.update(batch)
        adjusted.update(batch)
        exact.update(batch, weights=rate**np.arange(len(batch)-1, -1, -1), decay=rate**len(batch))
        batch_means.append(same_rate.mean[0])
        adjusted_means.append(adjusted.mean[0])
        exact_means.append(exact.mean[0])
        endpoints.append(i+len(batch))
    discrepancy = np.max(np.abs(np.array(exact_means)-np.array(online_means)[np.array(endpoints)-1]))
    assert discrepancy < 1e-12
    fig, ax = plt.subplots(1, 2, figsize=(12.2, 4.8), layout="constrained")
    fig.suptitle("Forgetting once per batch changes the meaning of λ", fontsize=17, fontweight="bold")
    ax[0].plot(np.arange(1, length+1), true_mean, color=NAVY, ls="--", label="Population mean")
    ax[0].plot(np.arange(1, length+1), online_means, color=TEAL, lw=1.6, label="Online: λ = 0.98 per observation")
    ax[0].plot(endpoints, batch_means, color=CORAL, lw=2, label="Batch: λ = 0.98 per batch of 20")
    ax[0].plot(endpoints, adjusted_means, color=GOLD, lw=1.8, ls="-.", label="Batch: λ = 0.98²⁰; equal new weights")
    ax[0].scatter(endpoints[::3], exact_means[::3], s=18, facecolors="none", edgecolors=TEAL,
                   label="Batch: exact per-observation weights", zorder=4)
    ax[0].set(title="The same stream, different adaptation speeds", xlabel="Observation", ylabel="Estimated mean")
    ax[0].legend(loc="upper left", fontsize=8)
    ax[0].grid(axis="y")
    ages = np.arange(length)
    weights_online = rate**ages
    weights_batch = rate**(ages//batch_size)
    weights_adjusted = rate**(batch_size*(ages//batch_size))
    for w, color, label in [(weights_online, TEAL, "Online"), (weights_batch, CORAL, "Same λ per batch"),
                             (weights_adjusted, GOLD, "Adjusted λ, equal batch weights")]:
        ax[1].plot(ages[:250], (w/w.sum())[:250], color=color, lw=1.8, label=label)
    ax[1].set(title="Normalized weights at the final batch boundary", xlabel="Age in observations", ylabel="Weight")
    ax[1].legend(loc="upper right")
    ax[1].grid(axis="y")
    save(fig, output, "batch-forgetting")
    return {"lambda_per_observation": rate, "batch_size": batch_size,
            "exact_batched_vs_online_mean_max_difference": float(discrepancy),
            "online_limiting_effective_sample_size": (1+rate)/(1-rate),
            "same_rate_batch_limiting_effective_sample_size": batch_size*(1+rate)/(1-rate),
            "equal_batch_adjusted_limiting_effective_sample_size": batch_size*(1+rate**batch_size)/(1-rate**batch_size)}


def convergence_figure(output):
    rng = np.random.default_rng(20260215)
    mean = np.array([1., 10., 20.])
    cov = np.array([[1, -1, .5], [-1, 3, -1], [.5, -1, 3]])
    data = rng.multivariate_normal(mean, cov, size=1000)
    state = IncrementalMoments(3)
    means, covariances = [], []
    for row in data:
        state.update(row)
        means.append(state.mean.copy())
        covariances.append(state.covariance() if state.weight > 1 else np.full((3, 3), np.nan))
    means, covariances = np.array(means), np.array(covariances)
    fig, ax = plt.subplots(1, 2, figsize=(12.2, 4.8), layout="constrained")
    fig.suptitle("Online estimates from one observation at a time", fontsize=17, fontweight="bold")
    for j, color in enumerate([TEAL, CORAL, GOLD]):
        ax[0].plot(np.arange(1, 1001), means[:, j]-mean[j], color=color, lw=1.3,
                   label=f"Mean component {j+1}")
    ax[0].axhline(0, color=NAVY, ls="--", lw=1)
    ax[0].set(title="Errors relative to the population means", xlabel="Observations", ylabel="Estimated mean − population mean")
    for (j, k), color in zip([(0, 0), (0, 1), (1, 1)], [TEAL, CORAL, GOLD]):
        ax[1].plot(np.arange(1, 1001), covariances[:, j, k], color=color, lw=1.3, label=f"Covariance ({j+1}, {k+1})")
        ax[1].axhline(cov[j, k], color=color, ls="--", lw=.8, alpha=.7)
    ax[1].set(title="Unbiased covariance; dashed lines show population values", xlabel="Observations", ylabel="Estimated covariance")
    for a in ax:
        a.set_xlim(1, 1000)
        a.grid(axis="y")
        a.legend(loc="upper right")
    save(fig, output, "python-convergence")
    np.testing.assert_allclose(state.covariance(), np.cov(data, rowvar=False), atol=1e-12)
    return {"samples": len(data), "mean": state.mean.tolist(), "covariance": state.covariance().tolist()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notebook", type=Path, default=DEFAULT_NOTEBOOK)
    parser.add_argument("--legacy-source", type=Path, default=HERE / "legacy/mahalanobis.py")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "assets/img/2026-online-estimation")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = {"inverse": inverse_figure(args.output_dir, args.notebook, args.legacy_source),
               "memory": memory_figure(args.output_dir),
               "forgetting": forgetting_figure(args.output_dir),
               "convergence": convergence_figure(args.output_dir)}
    (HERE / "figure-results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"Generated four figures as PNG and SVG in {args.output_dir}")
    print(json.dumps({k: v for k, v in results.items() if k != "inverse"}, indent=2))


if __name__ == "__main__":
    main()
