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
| `make_frozen_lake_figures_matplotlib.py` | part 3 (not used) | flat matplotlib versions of the five board figures, kept as alternatives in `figures_matplotlib/`; needs the cached data above |

```bash
SDL_VIDEODRIVER=dummy tools/connect4_rl/.venv/bin/python tools/connect4_rl/make_frozen_lake_figures.py
```

A full run from an empty `data/` takes roughly 45 minutes on an Intel Core i7-3520M (most of it
in the 2 × 5 prediction runs of 20,000 episodes and in the evaluation episodes of the five
Q-learning runs); with the caches in place, only the figures and videos are regenerated.

This directory is excluded from the Jekyll build via `exclude: tools/` in `_config.yml`.
