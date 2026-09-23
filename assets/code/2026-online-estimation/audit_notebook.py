"""Reproduce the notebook review without running its expensive experiments.

Only class definitions are extracted from the user's local sources. Imports,
notebook magics, plotting cells, and top-level experiments are not executed.
Annotations are postponed to isolate numerical behavior from Type[np] failures.
The jnp annotation name points to NumPy; only the NumPy backend is tested.
"""

import argparse
import ast
import __future__
import hashlib
import json
from pathlib import Path
import platform
import typing

import numpy as np

from online_estimation import IncrementalMoments, direct_moments


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFAULT_NOTEBOOK = (ROOT / "assets/jupyter/MarkusThill.github.io-jupyter/backups/"
                    "2025_09_27_online_estimate_cov_mu.ipynb.before-2026-series.bak")


def load_classes(source, postpone_annotations=True):
    namespace = {"np": np, "jnp": np, "Union": typing.Union,
                 "Type": typing.Type, "Any": typing.Any, "ArrayLike": np.ndarray}
    for node in ast.parse(source).body:
        if isinstance(node, ast.ClassDef) and node.name.endswith("CovarianceMeanEstimator"):
            code = compile(ast.Module(body=[node], type_ignores=[]),
                           "<original estimator class>", "exec",
                           flags=__future__.annotations.compiler_flag if postpone_annotations else 0,
                           dont_inherit=True)
            exec(code, namespace)
    return namespace


def source_classes(notebook, legacy):
    nb = json.loads(notebook.read_text())
    source = "\n".join("".join(c["source"]) for c in nb["cells"]
                       if c["cell_type"] == "code" and
                       "class " in "".join(c["source"]))
    return source, load_classes(source), load_classes(legacy.read_text())


def relative_error(actual, expected):
    return float(np.linalg.norm(actual - expected) / np.linalg.norm(expected))


def check_reference():
    """Compare every prefix with explicit historical observation weights."""
    rng = np.random.default_rng(20260215)
    data = rng.normal(size=(48, 4)) @ np.diag([0.5, 1, 2, 3]) + [3, -2, 5, 1]
    checks = inverse_checks = 0
    max_covariance_error = max_inverse_error = 0.0
    for sizes in ([1]*48, [3]*16, [2, 7, 1, 5, 9, 4, 6, 14]):
        for decay in (1.0, 0.5, 0.99):
            for weighted in (False, True):
                state = IncrementalMoments(4, decay, track_inverse=True)
                all_weights = np.empty(0)
                offset = 0
                for b in sizes:
                    incoming = rng.uniform(0.2, 2, size=b) if weighted else np.ones(b)
                    state.update(data[offset:offset+b], incoming)
                    all_weights = np.r_[decay * all_weights, incoming]
                    offset += b
                    mean, scatter = direct_moments(data[:offset], all_weights)
                    np.testing.assert_allclose(state.mean, mean, rtol=1e-11, atol=1e-11)
                    np.testing.assert_allclose(state.scatter, scatter, rtol=1e-10, atol=1e-11)
                    np.testing.assert_allclose(state.weight_squared_sum, all_weights @ all_weights)
                    if offset > 1:
                        d = all_weights.sum() - (all_weights @ all_weights) / all_weights.sum()
                        max_covariance_error = max(max_covariance_error,
                            relative_error(state.covariance(), scatter / d))
                    if state.scatter_inverse is not None:
                        ref = np.linalg.solve(scatter, np.eye(4))
                        err = relative_error(state.scatter_inverse, ref)
                        max_inverse_error = max(max_inverse_error, err)
                        assert err < 1e-7, err
                        inverse_checks += 1
                    checks += 1
    # Per-observation decay reproduced exactly at batch boundaries.
    online = IncrementalMoments(4, .97)
    batched = IncrementalMoments(4)
    for chunk in np.split(data, 8):
        for row in chunk:
            online.update(row)
        batched.update(chunk, weights=.97**np.arange(len(chunk)-1, -1, -1),
                       decay=.97**len(chunk))
        np.testing.assert_allclose(batched.mean, online.mean, rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(batched.scatter, online.scatter, rtol=1e-12, atol=1e-12)
    # Undefined startup outputs and malformed observations must be explicit.
    state = IncrementalMoments(2, track_inverse=True)
    for method in (state.covariance, state.precision):
        try:
            method()
            raise AssertionError("undefined startup result was accepted")
        except ValueError:
            pass
    state.update([1, 2])
    assert state.scatter_inverse is None
    try:
        state.covariance()
        raise AssertionError("one observation has no unbiased covariance")
    except ValueError:
        pass
    return {"prefix_states": checks, "inverse_comparisons": inverse_checks,
            "maximum_relative_covariance_error": max_covariance_error,
            "maximum_relative_inverse_error": max_inverse_error}


def audit(notebook, legacy):
    source, updated, old = source_classes(notebook, legacy)
    result = {"python": platform.python_version(), "numpy": np.__version__,
              "notebook": str(notebook.resolve()), "legacy": str(legacy.resolve()),
              "notebook_sha256": hashlib.sha256(notebook.read_bytes()).hexdigest(),
              "legacy_sha256": hashlib.sha256(legacy.read_bytes()).hexdigest(),
              "execution_scope": "Extracted original NumPy classes; annotations postponed; no GPU claims."}
    try:
        load_classes(source, postpone_annotations=False)
        result["annotation_definition"] = "accepted"
    except Exception as exc:
        result["annotation_definition"] = f"{type(exc).__name__}: {exc}"

    first = np.array([[0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0]], float)
    try:
        state = old["BatchCovarianceMeanEstimator"](np, 4, 1.0)
        state.update(first)
        result["legacy_first_batch"] = "returned despite deficient rank"
    except np.linalg.LinAlgError as exc:
        result["legacy_first_batch"] = str(exc)
    result["legacy_example_rank_bound"] = {"dimension": 300, "first_batch_size_range": [10, 19],
                                          "first_scatter_rank_at_most": 18}
    # Actual supplied classes: covariance agrees; hidden ridge explains precision mismatch.
    rng = np.random.default_rng(20260201)
    data = .01 * rng.normal(size=(40, 4))
    state = updated["BatchCovarianceMeanEstimator"](np, 4, 1.0)
    for chunk in np.split(data, 8):
        state.update(chunk)
    cov = np.cov(data, rowvar=False)
    inv = np.linalg.solve(cov, np.eye(4))
    centered = data - data.mean(0)
    hidden = np.linalg.solve(centered.T @ centered + 1e-3*np.eye(4), np.eye(4)) * 39
    result["updated_small_scale_batch"] = {
        "covariance_max_absolute_error": float(np.max(np.abs(state.get_cov()-cov))),
        "precision_relative_error_against_advertised_covariance": relative_error(state.get_cov_inv(), inv),
        "precision_relative_error_against_implicit_ridge": relative_error(state.get_cov_inv(), hidden),
        "inverse_identity_residual_frobenius": float(np.linalg.norm(cov @ state.get_cov_inv()-np.eye(4)))}

    decaying_ridge_errors = {}
    for name, b, rho in [("OnlineCovarianceMeanEstimator", 1, 1e-7),
                         ("BatchCovarianceMeanEstimator", 5, 1e-3)]:
        state = updated[name](np, 4, .8)
        weights = np.empty(0)
        steps = 0
        for i in range(0, len(data), b):
            chunk = data[i:i+b]
            state.update(chunk[0] if b == 1 else chunk)
            weights = np.r_[.8*weights, np.ones(len(chunk))]
            steps += 1
        _, scatter = direct_moments(data, weights)
        den = weights.sum() - (weights @ weights)/weights.sum()
        hidden = np.linalg.solve(scatter + .8**steps*rho*np.eye(4), np.eye(4))*den
        decaying_ridge_errors[name] = relative_error(state.get_cov_inv(), hidden)
        assert decaying_ridge_errors[name] < 1e-10
    result["decaying_implicit_ridge_relative_errors"] = decaying_ridge_errors

    # Weighted prefixes for both supplied class versions, independent of inverse validity.
    max_errors = {}
    data = rng.normal(size=(30, 3))
    for name, cls, sizes in [
        ("updated_online", updated["OnlineCovarianceMeanEstimator"], [1]*30),
        ("updated_batch", updated["BatchCovarianceMeanEstimator"], [5, 2, 7, 1, 6, 9]),
        ("legacy_online", old["OnlineCovarianceMeanEstimator"], [1]*30),
        ("legacy_batch", old["BatchCovarianceMeanEstimator"], [5, 2, 7, 1, 6, 9])]:
        maximum = 0.0
        for decay in (1., .8, .99):
            state = cls(np, 3, decay)
            all_weights = np.empty(0)
            offset = 0
            for b in sizes:
                batch = data[offset:offset+b]
                state.update(batch[0] if name.endswith("online") else batch)
                all_weights = np.r_[decay*all_weights, np.ones(b)]
                offset += b
                mean, scatter = direct_moments(data[:offset], all_weights)
                maximum = max(maximum, float(np.max(np.abs(state.get_mean()-mean))))
                np.testing.assert_allclose(state.W_n2, all_weights @ all_weights)
                if offset > 1:
                    den = all_weights.sum()-(all_weights@all_weights)/all_weights.sum()
                    maximum = max(maximum, float(np.max(np.abs(state.get_cov()-scatter/den))))
        assert maximum < 1e-11
        max_errors[name] = maximum
    result["original_class_mean_and_covariance_max_absolute_errors"] = max_errors

    decay = .99
    weights = decay**np.arange(500)
    W, Q = weights.sum(), weights @ weights
    good, bad = weights/W, weights/(W-Q/W)
    result["memory_normalization"] = {
        "lambda": decay, "observations": 500, "normalized_weight_sum": float(good.sum()),
        "notebook_weight_sum": float(bad.sum()), "finite_effective_sample_size": float(W*W/Q),
        "correct_mean_variance_first_component": float(3*(good@good)),
        "notebook_mean_variance_first_component": float(3*(bad@bad)),
        "relative_variance_overstatement": float((bad@bad)/(good@good)-1)}
    result["reference_checks"] = check_reference()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notebook", type=Path, default=DEFAULT_NOTEBOOK)
    parser.add_argument("--legacy-source", type=Path, default=HERE / "legacy/mahalanobis.py")
    parser.add_argument("--output", type=Path, default=HERE / "audit-results.json")
    args = parser.parse_args()
    results = audit(args.notebook, args.legacy_source)
    args.output.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
