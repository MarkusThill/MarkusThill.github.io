"""Redraw the two Hesse-normal-form figures of the boundary-points post.

Replaces the original hand-drawn hessenormal.png and hessedistance.png with
clean vector-quality renderings in the style of supportvec.png. Both figures
share one line and one unit normal, so they can be read as a pair.

Usage: python make_hesse_figures.py [--output-dir PATH]
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, FancyArrowPatch

# Shared geometry: the line n0.x = D, drawn identically in both figures.
N0 = np.array([1.0, 2.0]) / np.sqrt(5.0)  # unit normal, about 63 degrees
T0 = np.array([N0[1], -N0[0]])  # along the line, towards the lower right
D = 3.9  # signed offset, positive in both figures
XLIM = (-0.6, 7.55)
YLIM = (-0.5, 5.85)

INK = "black"
AXIS_LW = 2.6
LINE_LW = 2.2
VEC_LW = 3.0
LABEL_SIZE = 34


def line_points(x_from, x_to):
    """Two points on n0.x = D, for plotting the line itself."""
    xs = np.array([x_from, x_to])
    return xs, (D - N0[0] * xs) / N0[1]


def arrow(ax, tail, head, lw=VEC_LW, shrink=0.0):
    ax.add_patch(
        FancyArrowPatch(
            tail,
            head,
            arrowstyle="-|>",
            mutation_scale=34,
            linewidth=lw,
            color=INK,
            shrinkA=shrink,
            shrinkB=shrink,
            joinstyle="miter",
            capstyle="butt",
        )
    )


def right_angle(ax, corner, u, v, size=0.32):
    """Square marker showing that directions u and v meet at a right angle."""
    u = np.asarray(u, float) / np.linalg.norm(u)
    v = np.asarray(v, float) / np.linalg.norm(v)
    pts = np.array([corner + u * size, corner + (u + v) * size, corner + v * size])
    ax.plot(pts[:, 0], pts[:, 1], color=INK, lw=1.8, solid_joinstyle="miter")


def new_axes():
    fig, ax = plt.subplots(figsize=(7.0, 5.8), dpi=250)
    ax.set(xlim=XLIM, ylim=YLIM)
    ax.set_aspect("equal")
    ax.axis("off")
    # Coordinate axes, drawn as arrows out of the origin.
    arrow(ax, (0, 0), (XLIM[1] - 0.35, 0), lw=AXIS_LW)
    arrow(ax, (0, 0), (0, YLIM[1] - 0.25), lw=AXIS_LW)
    ax.text(XLIM[1] - 0.18, -0.06, "$x_1$", size=LABEL_SIZE, ha="left", va="center")
    ax.text(0.16, YLIM[1] - 0.2, "$x_2$", size=LABEL_SIZE, ha="left", va="top")
    xs, ys = line_points(-0.5, 7.15)
    ax.plot(xs, ys, color=INK, lw=LINE_LW, solid_capstyle="round")
    return fig, ax


def save(fig, path):
    fig.savefig(path, bbox_inches="tight", pad_inches=0.06, facecolor="white",
                metadata={"Software": "Matplotlib"})
    plt.close(fig)
    print(f"wrote {path}")


def figure_hessenormal(folder):
    """Unit normal, signed offset d, and the perpendicular foot of the origin."""
    fig, ax = new_axes()
    foot = D * N0                      # perpendicular projection of the origin
    on_line = np.array([5.2, (D - N0[0] * 5.2) / N0[1]])  # some other point on the line
    normal_base = foot + 0.95 * T0     # keep n0 clear of the arrowhead at the foot

    arrow(ax, (0, 0), on_line)         # x, an arbitrary point of the line
    arrow(ax, (0, 0), foot)            # d * n0
    arrow(ax, normal_base, normal_base + N0)  # n0 itself, with true unit length
    # No right-angle marker here: its inner vertex would fall on the arrow's own
    # centreline, and any size clearing the arrowhead collides with the d*n0 label.
    # n0 is drawn perpendicular to the line, and alpha marks the angle at the origin.

    # Angle between the two position vectors, so that n0.x = |x| cos(alpha) = d.
    a1 = np.degrees(np.arctan2(*on_line[::-1]))
    a2 = np.degrees(np.arctan2(*foot[::-1]))
    ax.add_patch(Arc((0, 0), 2.3, 2.3, theta1=a1, theta2=a2, lw=1.8, color=INK))
    mid = np.radians((a1 + a2) / 2)
    ax.text(1.52 * np.cos(mid), 1.52 * np.sin(mid), r"$\alpha$",
            size=LABEL_SIZE - 4, ha="center", va="center")

    ax.text(normal_base[0] + 0.66, normal_base[1] + 0.72, r"$\vec{n}_0$",
            size=LABEL_SIZE, ha="left", va="center")
    ax.text(1.62, 2.62, r"$d\,\vec{n}_0$", size=LABEL_SIZE, ha="left", va="center")
    ax.text(3.15, 0.58, r"$\vec{x}$", size=LABEL_SIZE, ha="center", va="center")
    save(fig, folder / "hessenormal.png")


def figure_hessedistance(folder):
    """A point off the line and its signed distance along the unit normal."""
    fig, ax = new_axes()
    foot = np.array([3.6, (D - N0[0] * 3.6) / N0[1]])  # projection of r onto the line
    d_r = 1.45                         # positive: r lies on the side n0 points to
    r = foot + d_r * N0
    normal_base = np.array([1.15, (D - N0[0] * 1.15) / N0[1]])

    arrow(ax, (0, 0), r)               # r
    arrow(ax, normal_base, normal_base + N0)  # n0, again with unit length
    ax.plot([foot[0], r[0]], [foot[1], r[1]], color=INK, lw=LINE_LW)
    right_angle(ax, foot, N0, T0, size=0.28)

    ax.text(normal_base[0] + 0.52, normal_base[1] + 0.68, r"$\vec{n}_0$",
            size=LABEL_SIZE, ha="left", va="center")
    ax.text(1.12, 1.66, r"$\vec{r}$", size=LABEL_SIZE, ha="center", va="center")
    mid = (foot + r) / 2
    ax.text(mid[0] + 0.34, mid[1] - 0.08, r"$d_r$", size=LABEL_SIZE,
            ha="left", va="center")
    save(fig, folder / "hessedistance.png")


def main():
    default = Path(__file__).resolve().parents[2] / "assets/img/2026-09-23-linear-classifier-boundary-points"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=default)
    folder = parser.parse_args().output_dir
    folder.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"mathtext.fontset": "stix", "font.family": "STIXGeneral"})
    figure_hessenormal(folder)
    figure_hessedistance(folder)


if __name__ == "__main__":
    main()
