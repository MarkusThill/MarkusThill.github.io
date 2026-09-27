# Figure & data harness — Connect-4 reinforcement-learning series

The experiments, figures and videos of the reinforcement-learning series come from scripts in
this directory, in the same way as `tools/connect4/` serves the tree-search series. Code quoted
in a post is taken verbatim from a module here, so every snippet can be run as shown.

## Setup

The Frozen Lake environment lives in [techdays26](https://github.com/MarkusThill/techdays26),
which requires Python ≥ 3.11 (the `tools/.venv` of the search series uses 3.10). At the pinned
commit, `src/techdays26/frozen_lake/` has no `__init__.py`, so a regular `pip install` from GitHub
leaves the environment out; the harness therefore installs a pinned clone in editable mode.

```bash
python3.12 -m venv tools/connect4_rl/.venv
tools/connect4_rl/.venv/bin/pip install numpy==2.4.2 matplotlib==3.10.8 gymnasium==1.2.3 \
    pygame==2.6.1 imageio==2.37.0 imageio-ffmpeg==0.6.0
git clone https://github.com/MarkusThill/techdays26.git tools/connect4_rl/.techdays26
git -C tools/connect4_rl/.techdays26 checkout c18a0b5f3f2a3fdc48fec5c8872c698ac647dc49
tools/connect4_rl/.venv/bin/pip install --no-deps -e tools/connect4_rl/.techdays26
```

`.venv/` and `.techdays26/` are not committed.

## Conventions

- Run scripts from the repository root. `SDL_VIDEODRIVER=dummy` lets pygame render without a
  display.
- Figures are written to `assets/img/<post-slug>/`, videos to `assets/video/<post-slug>-*.mp4`.
- Experiment results are cached as JSON/NPZ in `data/`, so plots can be restyled without
  re-running the experiments. Delete a file to recompute it.
- `--quick` runs a cheap smoke version and writes nothing to `assets/`; with `--img-dir DIR` its
  figures go to `DIR` for a look.
- All randomness is seeded; the seeds are documented next to each experiment in the script.
- The learners only use sampled transitions. The transition table `env.P` is used exclusively for
  reference values (exact policy evaluation, value iteration, outcome probabilities).

## Scripts

| Script | Feeds | Produces |
| --- | --- | --- |
| `frozen_lake_rl.py` | part 3 | module: environment factory, the two fixed policies, first-visit Monte Carlo, TD(0), Q-learning, greedy evaluation, and the model-based reference computations |
| `make_frozen_lake_figures.py` | part 3 | all figures and both videos of the Frozen Lake post; caches `data/prediction_*.json`, `data/q_learning.json` and `data/q_learning_tables.npz`. Board figures come from `FrozenLakeEnv`'s own renderer (sprites plus `set_v`/`set_q` overlays, as in the Lab 1 notebook), re-rendered at 2× resolution by `render_board()` |
| `connect4_results.py` | part 9 | module: loads a training run (the notebook's folder with `0_params.json` and per-repeat `0_metrics.json` / `0_arena_metrics.json`, or its extract in `assets/data/`), orients arena results to the learned agent, timing without evaluation pauses (`evaluation_pauses`, `training_time`, `check_timing`), bootstrap CI, estimated game count — the code quoted in the post |
| `make_connect4_results_figures.py` | part 9 | learning curve over training minutes, final win/draw/loss per opponent and side, win rate vs. opponent ε, training/evaluation time split; `--run <folder or extract> --out <dir> [--numbers <json>]`; the published figures come from `assets/data/2026-08-27-near-perfect-connect4-in-five-minutes/` (identical to the raw run folder). Test renders of the older L run go to a scratch directory, never to `assets/` |
| `make_connect4_comparison_figures.py` | part 9 | comparison of the recipe with the variants (τ = 0.05; decaying ε with λ = 0.75, n = 8): learning curves with CI bands and late-phase win rates (last five evaluations pooled), early head start with a bootstrap CI of the difference; `--run label=folder` (repeatable), `--out`, `--numbers` (→ `data/post09/comparison_numbers.json`) |
| `export_run_results.py` | part 9 | lossless extract of a training run for `assets/data/` (`params.json`, `ntuples.json`, `metrics.csv.gz`, `arena.csv.gz`, 450 KB instead of 5.4 MB; drops only the text logs and derivable columns) and a check that it loads to the same data |
| `realisable_states.py` | part 9, side post S1 | counting (thesis recursion), enumeration and mixed-radix ranking of the realisable states of an n-tuple; `Ranking.rank`/`unrank` are verified to be inverse for all 200 tuples |
| `export_ntuple_weights.py` | part 9 | writes the realisable weights of a checkpoint in rank order (`C4NT` format, gzip), int8/float16/float32; refuses checkpoints with non-zero weights outside the realisable set |
| `ntuple_reference.py` | part 9 | reference positions with scores, values and moves of `TDConnect4AgentTorch` (self-play games with random moves) |
| `check_ntuple_widget.mjs` | part 9 | loads the shipped `assets/js/connect4-core.js` + `connect4-ntuple.js` and an exported weights file and compares values, scores and moves with the reference (released agent, run 1, float32: 0 of 7,447 scores and moves differ) |
| `select_strongest.py` | part 9 | selection tournament of the ten final checkpoints (self-contained, for Colab) and fresh-games evaluation of the winner; its output (run 1 selected) is `assets/data/2026-08-27-near-perfect-connect4-in-five-minutes/selection.json` |
| `make_frozen_lake_figures_matplotlib.py` | part 3 (not used) | flat matplotlib versions of the five board figures, kept as alternatives in `figures_matplotlib/`; needs the cached data above |

```bash
SDL_VIDEODRIVER=dummy tools/connect4_rl/.venv/bin/python tools/connect4_rl/make_frozen_lake_figures.py
```

The widget check:

```bash
# Python environment with PyTorch and techdays26; the shipped agent is repeat 1 of the L run (selection tournament)
python tools/connect4_rl/export_ntuple_weights.py <checkpoint.pt> assets/data/connect4-ntuple-agent.bin.gz --dtype float32
python tools/connect4_rl/ntuple_reference.py <checkpoint.pt> /tmp/ref.json
node tools/connect4_rl/check_ntuple_widget.mjs assets/data/connect4-ntuple-agent.bin.gz /tmp/ref.json
```

Checkpoints (≈105 MB each) live in `checkpoints/`, which is not committed.

A full run from an empty `data/` takes roughly 45 minutes on an Intel Core i7-3520M (most of it
in the 2 × 5 prediction runs of 20,000 episodes and in the evaluation episodes of the five
Q-learning runs); with the caches in place, only the figures and videos are regenerated.

This directory is excluded from the Jekyll build via `exclude: tools/` in `_config.yml`.
