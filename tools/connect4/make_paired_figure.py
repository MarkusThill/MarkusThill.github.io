#!/usr/bin/env python3
"""Paired-timings figure for part 8 of the Connect-4 series.

Draws the raw pairs measured by ``bench_paired.py`` (cached in
``data/paired_raw.json``) in two panels:

* left: a log-log scatter of the per-position solve times, MTD(f) against
  wide-window negamax. Every dot is one position solved by both drivers;
  dots below the diagonal are positions on which MTD(f) was faster. The
  five-orders-of-magnitude spread *along* the diagonal is the heavy tail the
  post talks about, and the reason the difficulty of the position has to be
  paired away.
* right: the distribution of the per-position ratio negamax/MTD(f) on a log
  axis. A consistent-but-modest advantage shows up as most of the mass
  sitting slightly right of 1 -- which is exactly the situation in which a
  rank-based test is informative and a comparison of means is not.

The annotations (median ratio, share of positions on which MTD(f) won) are
computed from the data, not typed in.

Run from the repo root::

    tools/.venv/bin/python tools/connect4/make_paired_figure.py
"""

from __future__ import annotations

import json
import pathlib
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RAW = pathlib.Path("tools/connect4/data/paired_raw.json")
OUT_DIR = pathlib.Path("assets/img/2026-04-09-connect-4-verification-and-benchmarking")

C_LIVE = "#4C78A8"
C_ACCENT = "#D62728"
C_TEXT = "#333333"
C_TEXT_LIGHT = "#666666"
C_GRID = "#DDDDDD"


def style_axis(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(C_GRID)
    ax.tick_params(colors=C_TEXT_LIGHT, labelsize=8.5)
    ax.grid(True, which="major", color=C_GRID, lw=0.6)
    ax.set_axisbelow(True)


def main() -> None:
    rows = json.loads(RAW.read_text())
    mtdf = np.array([t for r in rows for t in r["mtdf_s"]])
    nega = np.array([t for r in rows for t in r["negamax_s"]])
    ratio = nega / mtdf

    median_ratio = statistics.median(ratio)
    frac_faster = float(np.mean(nega > mtdf))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 4.3))

    # -- left: paired scatter ------------------------------------------------
    lo = min(mtdf.min(), nega.min()) * 0.7
    hi = max(mtdf.max(), nega.max()) * 1.4
    ax1.plot([lo, hi], [lo, hi], color=C_TEXT_LIGHT, lw=1.0, ls="--", zorder=2)
    ax1.scatter(nega, mtdf, s=11, color=C_LIVE, alpha=0.4, linewidths=0, zorder=3)
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xlim(lo, hi)
    ax1.set_ylim(lo, hi)
    ax1.set_aspect("equal")
    ax1.set_xlabel("wide-window negamax, solve time [s]", fontsize=9, color=C_TEXT)
    ax1.set_ylabel("MTD(f), solve time [s]", fontsize=9, color=C_TEXT)
    ax1.text(
        0.97,
        0.06,
        "below the diagonal:\nMTD(f) faster",
        transform=ax1.transAxes,
        ha="right",
        va="bottom",
        fontsize=8.5,
        color=C_TEXT_LIGHT,
    )
    ax1.set_title(f"one dot = one position, solved by both ({len(ratio)} pairs)", fontsize=9.5, color=C_TEXT)
    style_axis(ax1)

    # -- right: ratio distribution ------------------------------------------
    bins = np.logspace(np.log10(ratio.min()), np.log10(ratio.max()), 45)
    ax2.hist(ratio, bins=bins, color=C_LIVE, edgecolor="white", lw=0.4, zorder=3)
    ax2.set_xscale("log")
    ax2.axvline(1.0, color=C_TEXT_LIGHT, lw=1.0, ls="--", zorder=4)
    ax2.axvline(median_ratio, color=C_ACCENT, lw=1.4, zorder=4)
    ax2.text(
        median_ratio * 1.1,
        0.96,
        f"median ×{median_ratio:.2f}",
        transform=ax2.get_xaxis_transform(),
        ha="left",
        va="top",
        fontsize=8.5,
        color=C_ACCENT,
    )
    ax2.text(
        0.97,
        0.80,
        f"MTD(f) faster on\n{frac_faster:.0%} of positions",
        transform=ax2.transAxes,
        ha="right",
        va="top",
        fontsize=8.5,
        color=C_TEXT_LIGHT,
    )
    ax2.set_xlabel("per-position ratio  negamax / MTD(f)", fontsize=9, color=C_TEXT)
    ax2.set_ylabel("positions", fontsize=9, color=C_TEXT)
    ax2.set_title("the same pairs, as a ratio", fontsize=9.5, color=C_TEXT)
    style_axis(ax2)

    fig.tight_layout(w_pad=2.5)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "paired-timings.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", pad_inches=0.10, facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")
    print(f"median ratio {median_ratio:.3f}, MTD(f) faster on {frac_faster:.1%} of {len(ratio)} pairs")


if __name__ == "__main__":
    main()
