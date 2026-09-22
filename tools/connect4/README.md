# Figure & measurement harness — Connect-4 series (parts 3–9)

The newly reproduced measurements and generated figures in the classical Connect-4 series
come from scripts in this directory. Measurements retained from the 2012 development notes are
labelled as historical in the posts.

## Setup

```bash
python3 -m venv tools/.venv
tools/.venv/bin/pip install bitbully bitbully-databases matplotlib pandas scipy
```

## Conventions

- One `make_<figure>.py` per figure; run from the repo root.
- Figures are written to `assets/img/<post-slug>/`.
- Raw measurements are cached to `data/<name>.json` next to the scripts, so plots can be
  restyled without re-running a multi-minute solve. Delete the JSON to force a re-measure.
- Anything that takes more than a few seconds prints progress and honours `--quick` for a
  cheap smoke run.

## Scripts

| Script | Feeds | Produces |
| --- | --- | --- |
| `make_alphabeta_figure.py` | part 2 | alpha-beta pruning tree diagram, derived by running the illustrated fail-hard search |
| `bitboard_layout.py` | part 3 | bit-layout diagram, CFour vs. BitBully |
| `make_thumbnail.py` | part 3 | post thumbnail: a position next to the two 64-bit words |
| `bench_tt_size.py` | part 5 | nodes/time per solve, mirror-symmetry deduplication |
| `book_stats.py` | part 6 | book sizes, win/loss/draw distribution, encoding costs |
| `bench_drivers.py` | part 7 | mtdf vs. negamax vs. null_window across plies |
| `bench_paired.py` | part 8 | paired timings + Wilcoxon signed-rank (raw pairs cached for the figure) |
| `make_paired_figure.py` | part 8 | paired scatter + ratio histogram from the raw pairs |
| `verify.py` | part 8 | four correctness checks, incl. vs. Tromp's 8-ply book |
| `make_winning_patterns.py` | part 9 | the three decided-position patterns, each asserted against the engine |
| `widget_reference.py` + `check_widget.mjs` | parts 3–7 | cross-checks the interactive widgets (`assets/js/connect4-*.js`) against BitBully: board operations, ordering, Huffman encoding, `hash()`, and the scores returned by the JS solver of the part-7 widget |

## What is deliberately *not* measured here

Every benchmark in this directory times **BitBully's own C++ code** through its Python
bindings, or counts positions the engine itself enumerates. There are no reimplementations.

An earlier version of this harness contained two hand-written comparisons — a pure-Python
array-scan vs. bitboard win check, and a pure-Python alpha-beta with the move ordering swapped
out. Both were removed: a ratio measured between two Python implementations says nothing about
a C++ engine, and a search written for the blog post is not the search being described. Where
a technique cannot be ablated against the real engine, the posts cite the original 2012
development measurements and label them as such.

This directory is excluded from the Jekyll build via `exclude:` in `_config.yml`.
