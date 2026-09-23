"""Reproduce the synthetic light-relay example, CSVs, results, plot, and ZIP.

Usage: python generate_example.py [--output-dir PATH] [--seed 20171006]
The default output directory is this script's directory, regardless of cwd.
Requires only NumPy and Matplotlib plus the Python standard library.
"""

import argparse
import json
from pathlib import Path
import platform
import shutil
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

from boundary_classifier import classify_logs


DEFAULT_SEED = 20171006
BOUNDARY_COUNT = 18
QUERY_COUNT = 240
NOISE_STD = 0.018
TRUE_W = np.array([0.65, 0.90])
TRUE_B = -0.75
OFF_COLOR = "#2471a3"
ON_COLOR = "#c86417"
FIT_COLOR = "#124b41"
BUNDLE_FILES = [
    "README.md", "requirements.txt", "boundary_classifier.py", "generate_example.py",
    "boundary_points.csv", "orientation_points.csv", "unlabeled_points.csv",
    "evaluation_truth.csv", "predictions.csv", "results.json",
    "calibration-and-predictions.png", "calibration-and-predictions.svg",
]


def save_csv(path, values, header, fmt="%.12f"):
    np.savetxt(path, values, delimiter=",", header=header, comments="", fmt=fmt)


def generate_inputs(folder, seed):
    """Simulate boundary measurements, four controls, and unlabeled old logs."""
    rng = np.random.default_rng(seed)
    x1 = np.linspace(0.10, 0.90, BOUNDARY_COUNT)
    exact_boundary = np.column_stack((x1, -(TRUE_W[0] * x1 + TRUE_B) / TRUE_W[1]))
    # Both recorded lamp settings have independent measurement noise.
    boundary = exact_boundary + rng.normal(0.0, NOISE_STD, exact_boundary.shape)
    controls = np.array([[0.15, 0.10], [0.20, 0.40], [0.80, 0.50], [0.90, 0.90]])
    control_labels = np.where(controls @ TRUE_W + TRUE_B > 0, 1, -1)
    # Three readable examples first, followed by uniformly sampled old settings.
    queries = np.vstack(([[0.15, 0.20], [0.80, 0.80], [0.50, 0.47]],
                         rng.uniform(0.0, 1.0, (QUERY_COUNT - 3, 2))))
    ids = np.arange(QUERY_COUNT)
    save_csv(folder / "boundary_points.csv", boundary, "x1,x2")
    save_csv(folder / "orientation_points.csv", np.column_stack((controls, control_labels)),
             "x1,x2,label", ["%.12f", "%.12f", "%d"])
    save_csv(folder / "unlabeled_points.csv", np.column_stack((ids, queries)),
             "log_id,x1,x2", ["%d", "%.12f", "%.12f"])


def evaluate(folder, w, b, ids, distances, predictions):
    """Use simulation truth only after fitting and predictions are complete."""
    logged = np.loadtxt(folder / "unlabeled_points.csv", delimiter=",", skiprows=1)
    boundary = np.loadtxt(folder / "boundary_points.csv", delimiter=",", skiprows=1)
    queries = logged[:, 1:3]
    true_norm = np.linalg.norm(TRUE_W)
    true_distances = (queries @ TRUE_W + TRUE_B) / true_norm
    true_labels = np.where(true_distances > 0.0, 1, -1)
    correct = predictions == true_labels
    save_csv(folder / "evaluation_truth.csv", np.column_stack((ids, true_labels, true_distances)),
             "log_id,true_label,true_signed_distance", ["%d", "%d", "%.12f"])
    save_csv(folder / "predictions.csv", np.column_stack((ids, distances, predictions)),
             "log_id,signed_distance,predicted_label", ["%d", "%.12f", "%d"])
    diagnostics = {
        "fitted_unit_normal": w.tolist(),
        "fitted_intercept": b,
        "true_unit_normal": (TRUE_W / true_norm).tolist(),
        "true_unit_intercept": float(TRUE_B / true_norm),
        "orientation_error_degrees": float(np.degrees(np.arccos(np.clip(w @ (TRUE_W / true_norm), -1, 1)))),
        "boundary_rms_distance": float(np.sqrt(np.mean((boundary @ w + b) ** 2))),
        "test_correct": int(correct.sum()),
        "test_count": len(ids),
        "test_accuracy": float(correct.mean()),
        "misclassified_log_ids": ids[~correct].tolist(),
        "first_three_predictions": [
            {"log_id": int(i), "x1": float(x[0]), "x2": float(x[1]),
             "signed_distance": float(d), "predicted_label": int(y), "true_label": int(t)}
            for i, x, d, y, t in zip(ids[:3], queries[:3], distances[:3], predictions[:3], true_labels[:3])
        ],
    }
    return queries, true_labels, diagnostics


def make_plot(folder, w, b, queries, predictions, true_labels, diagnostics):
    """Plot actual supplied measurements and the independently evaluated predictions."""
    boundary = np.loadtxt(folder / "boundary_points.csv", delimiter=",", skiprows=1)
    controls = np.loadtxt(folder / "orientation_points.csv", delimiter=",", skiprows=1)
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "axes.titlesize": 13, "axes.labelsize": 12,
        "axes.spines.top": False, "axes.spines.right": False,
        "svg.hashsalt": "boundary-points-example",
    })
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 6.3))
    fig.subplots_adjust(left=0.07, right=0.985, bottom=0.23, top=0.83, wspace=0.25)
    fig.suptitle("Reconstructing a light relay's switching boundary", fontsize=17, y=0.97)
    fig.text(0.5, 0.905,
             f"Synthetic data  |  {BOUNDARY_COUNT} boundary estimates  |  4 labeled controls  |  {QUERY_COUNT} logged settings",
             ha="center", color="#52606d", fontsize=11)
    grid = np.linspace(0.0, 1.0, 160)
    gx, gy = np.meshgrid(grid, grid)
    fitted_scores = gx * w[0] + gy * w[1] + b
    for ax in axes:
        ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="Lamp 1 setting, $x_1$", ylabel="Lamp 2 setting, $x_2$")
        ax.set_aspect("equal")
        ax.set_xticks(np.linspace(0, 1, 6))
        ax.set_yticks(np.linspace(0, 1, 6))
        ax.grid(color="#d8dfe5", alpha=0.45, linewidth=0.6)
        ax.contour(gx, gy, fitted_scores, levels=[0], colors=[FIT_COLOR], linewidths=2.1, zorder=4)
        ax.contour(gx, gy, gx * TRUE_W[0] + gy * TRUE_W[1] + TRUE_B,
                   levels=[0], colors=["#68727d"], linestyles="--", linewidths=1.5, zorder=3)

    axes[0].set_title("A. Calibration inputs and fitted line", loc="left", pad=12)
    axes[0].scatter(boundary[:, 0], boundary[:, 1], marker="*", s=115,
                    c="#68727d", edgecolors="white", linewidths=0.5, zorder=5)
    for label, color, marker in [(-1, OFF_COLOR, "o"), (1, ON_COLOR, "s")]:
        subset = controls[controls[:, 2] == label, :2]
        axes[0].scatter(subset[:, 0], subset[:, 1], c=color, marker=marker, s=75,
                        edgecolors="white", linewidths=0.7, zorder=6)
    axes[0].legend(handles=[
        Line2D([], [], marker="*", color="none", markerfacecolor="#68727d", markeredgecolor="none",
               markersize=11, label="Measured boundary point"),
        Line2D([], [], marker="o", color="none", markerfacecolor=OFF_COLOR, markeredgecolor="none",
               markersize=7, label="Known OFF (−1)"),
        Line2D([], [], marker="s", color="none", markerfacecolor=ON_COLOR, markeredgecolor="none",
               markersize=7, label="Known ON (+1)"),
    ], loc="upper center", bbox_to_anchor=(0.5, -0.18), frameon=False, fontsize=10)

    axes[1].set_title("B. Classifying logged settings", loc="left", pad=12)
    axes[1].contourf(gx, gy, fitted_scores, levels=[-2, 0, 2],
                     colors=["#eef5fb", "#fff3e9"], alpha=0.75, zorder=0)
    for label, color, marker in [(-1, OFF_COLOR, "o"), (1, ON_COLOR, "s")]:
        subset = queries[predictions == label]
        axes[1].scatter(subset[:, 0], subset[:, 1], c=color, marker=marker,
                        s=17, alpha=0.8, edgecolors="none", zorder=2)
    errors = queries[predictions != true_labels]
    if len(errors):
        axes[1].scatter(errors[:, 0], errors[:, 1], s=95, facecolors="none",
                        edgecolors="#1d2733", linewidths=1.2, zorder=6)
    # Log 1 is an example ON point; the segment is its perpendicular distance.
    query = queries[1]
    distance = float(query @ w + b)
    projection = query - distance * w
    axes[1].plot(*np.vstack((projection, query)).T, color="#263441", linewidth=1.2, zorder=5)
    axes[1].scatter(*query, s=68, c=ON_COLOR, marker="s", edgecolors="#263441", zorder=7)
    axes[1].scatter(*projection, s=24, c=FIT_COLOR, zorder=7)
    axes[1].annotate(f"log 1: distance {distance:+.3f}", xy=query, xytext=(0.41, 0.95),
                     arrowprops={"arrowstyle": "-", "color": "#52606d"},
                     fontsize=10, bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.9}, zorder=8)
    axes[1].text(0.03, 0.04, f"{diagnostics['test_correct']}/{QUERY_COUNT} predictions match the simulator",
                 transform=axes[1].transAxes, fontsize=9,
                 bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.9}, zorder=8)
    axes[1].legend(handles=[
        Line2D([], [], color=FIT_COLOR, linewidth=2, label="Fitted boundary"),
        Line2D([], [], color="#68727d", linestyle="--", linewidth=1.5, label="True boundary (evaluation only)"),
        Line2D([], [], marker="o", color="none", markerfacecolor="none", markeredgecolor="#1d2733",
               markersize=8, label=f"Incorrect prediction ({len(errors)})"),
    ], loc="upper center", bbox_to_anchor=(0.5, -0.18), frameon=False, fontsize=10)
    for extension in ("png", "svg"):
        metadata = {"Software": "Matplotlib"} if extension == "png" else {"Date": None}
        fig.savefig(folder / f"calibration-and-predictions.{extension}", dpi=180,
                    bbox_inches="tight", facecolor="white", metadata=metadata)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()
    folder = args.output_dir.resolve()
    folder.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).resolve().parent
    for filename in ("README.md", "requirements.txt", "boundary_classifier.py", "generate_example.py"):
        if folder != source:
            shutil.copyfile(source / filename, folder / filename)

    generate_inputs(folder, args.seed)
    # The fitter sees only the three input CSVs, not the simulator parameters.
    w, b, ids, distances, predictions = classify_logs(folder)
    queries, true_labels, diagnostics = evaluate(folder, w, b, ids, distances, predictions)
    results = {
        "scenario": "Synthetic light-triggered relay; not measured experimental data",
        "seed": args.seed,
        "feature_scaling": "Each lamp setting is normalized to the interval [0, 1]",
        "boundary_count": BOUNDARY_COUNT, "orientation_label_count": 4,
        "boundary_measurement_noise_std_per_coordinate": NOISE_STD,
        "true_unnormalized_weights": TRUE_W.tolist(), "true_unnormalized_intercept": TRUE_B,
        "decision_rule": "ON (+1) for a positive score; OFF (-1) otherwise",
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "matplotlib": matplotlib.__version__},
        **diagnostics,
    }
    (folder / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    make_plot(folder, w, b, queries, predictions, true_labels, diagnostics)
    # Fixed archive metadata makes repeated runs reproducible on the same setup.
    with zipfile.ZipFile(folder / "boundary-example.zip", "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for filename in BUNDLE_FILES:
            info = zipfile.ZipInfo("boundary-points/" + filename, date_time=(2026, 9, 23, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, (folder / filename).read_bytes())
    print(f"Saved example files in {folder}")
    print(f"Fitted unit normal: {w}; intercept: {b:.6f}")
    print(f"Evaluation: {diagnostics['test_correct']}/{QUERY_COUNT} correct ({diagnostics['test_accuracy']:.2%})")
    print(f"Boundary RMS distance: {diagnostics['boundary_rms_distance']:.6f}")


if __name__ == "__main__":
    main()
