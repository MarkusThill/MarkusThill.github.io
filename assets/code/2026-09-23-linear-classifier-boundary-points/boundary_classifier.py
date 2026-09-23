"""Fit an affine classifier to boundary points, then orient it using labels.

Run this file next to the supplied CSV files to fit and classify the example.
All features must already use the same chosen scaling. A positive score means
class +1; this example assigns an exactly zero score to class -1.
"""

from pathlib import Path

import numpy as np


def fit_hyperplane(points):
    """Return a unit normal w and intercept b minimizing orthogonal residuals.

    points has shape (m, n), with m >= n >= 2. With n affinely independent
    points this interpolates them; with more points it fits by least squares.
    Reject a rank-deficient set or a numerically non-unique smallest direction.
    """
    points = np.asarray(points, dtype=float)
    if points.ndim != 2 or points.shape[1] < 2:
        raise ValueError("Expected a matrix of points in at least two dimensions.")
    if points.shape[0] < points.shape[1] or not np.isfinite(points).all():
        raise ValueError("Need at least n finite points in n dimensions.")

    center = points.mean(axis=0)
    # m >= n: even a reduced SVD contains all n right singular vectors.
    _, singular_values, vh = np.linalg.svd(points - center, full_matrices=False)
    tolerance = max(points.shape) * np.finfo(float).eps * singular_values[0]
    if np.count_nonzero(singular_values > tolerance) < points.shape[1] - 1:
        raise ValueError("Boundary points do not determine a unique hyperplane.")
    if singular_values[-2] - singular_values[-1] <= tolerance:
        raise ValueError("The smallest singular direction is not unique.")

    w = vh[-1].copy()  # SVD already gives a unit vector.
    b = -float(w @ center)
    return w, b


def orient_hyperplane(w, b, labeled_points, labels):
    """Choose the sign of (w, b) giving fewer errors on labeled observations.

    labels must be -1 or +1. A label exactly on the plane cannot determine
    its orientation. Raise ValueError if both orientations make equal errors.
    """
    w = np.asarray(w, dtype=float)
    points = np.asarray(labeled_points, dtype=float)
    labels = np.asarray(labels)
    if w.ndim != 1 or not np.isfinite(w).all() or np.linalg.norm(w) == 0:
        raise ValueError("Expected a finite, nonzero normal vector.")
    if not np.isfinite(b) or points.ndim != 2 or points.shape[1] != w.size:
        raise ValueError("Labeled points and plane must have matching dimensions.")
    if labels.shape != (points.shape[0],) or not np.isin(labels, [-1, 1]).all():
        raise ValueError("Provide one label (-1 or +1) per labeled point.")
    if not np.isfinite(points).all():
        raise ValueError("Labeled points must be finite.")

    signs = np.sign(points @ w + b)
    errors = np.count_nonzero(signs != labels)
    flipped_errors = np.count_nonzero(-signs != labels)
    if errors == flipped_errors:
        raise ValueError("The labeled observations do not resolve the orientation.")
    return (-w, -float(b)) if flipped_errors < errors else (w, float(b))


def classify_logs(folder):
    """Fit from CSV inputs only; never read the evaluation truth file."""
    folder = Path(folder)
    boundary = np.loadtxt(folder / "boundary_points.csv", delimiter=",", skiprows=1)
    labeled = np.loadtxt(folder / "orientation_points.csv", delimiter=",", skiprows=1)
    logged = np.loadtxt(folder / "unlabeled_points.csv", delimiter=",", skiprows=1)
    w, b = fit_hyperplane(boundary)
    w, b = orient_hyperplane(w, b, labeled[:, :2], labeled[:, 2])
    distances = logged[:, 1:3] @ w + b
    predictions = np.where(distances > 0.0, 1, -1)
    return w, b, logged[:, 0].astype(int), distances, predictions


def main():
    folder = Path(__file__).resolve().parent
    w, b, ids, distances, predictions = classify_logs(folder)
    print("Unit normal:", np.array2string(w, precision=6))
    print(f"Intercept: {b:.6f}")
    print("log_id  signed_distance  predicted_class")
    for log_id, distance, prediction in zip(ids[:3], distances[:3], predictions[:3]):
        print(f"{log_id:6d}  {distance:+.6f}        {prediction:+d}")
    print("Distances use the normalized lamp-setting coordinates.")


if __name__ == "__main__":
    main()
