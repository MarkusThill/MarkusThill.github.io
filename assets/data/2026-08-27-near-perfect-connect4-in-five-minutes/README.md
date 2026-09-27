# Training results: near-perfect Connect-4 after five minutes of training

Results of the ten training runs of the post
[Near-Perfect Connect-4 after Five Minutes of Training: Reinforcement Learning from Scratch by Self-Play](https://markusthill.github.io/blog/2026/near-perfect-connect4-in-five-minutes/),
trained with `lab2/1_train_ntuple_net.ipynb` of [techdays26](https://github.com/MarkusThill/techdays26). The
complete raw output of the runs, including the text logs and the final weights of every run, is in a
[Google Drive folder](https://drive.google.com/drive/folders/1DlRfofqm-_Lw6pM9Wh518m_ZjbeiGfuY?usp=sharing).
These files contain the same numbers without the logs and weights. The script `export_run_results.py` in
`tools/connect4_rl/` of this blog's repository created them, and `connect4_results.load_run()` reads them.

| File             | Content                                                                                   |
| ---------------- | ----------------------------------------------------------------------------------------- |
| `params.json`    | Configuration of the runs, GPU, software versions and techdays26 commit, as logged        |
| `ntuples.json`   | The 200 n-tuples (cells as bit indices `column * 9 + row`, row 0 at the bottom)            |
| `metrics.csv.gz` | Training metrics, one row per run and every 100 training steps                            |
| `arena.csv.gz`   | Evaluation results, one row per run, evaluation step (every 1,000 steps) and pairing       |
| `selection.json` | Selection tournament of the ten final agents (200 games per condition, seed 20260927), the ranking criterion of every agent, and the fresh-games evaluation of the selected agent (seed 90210) |

## `metrics.csv.gz`

| Column                                     | Meaning                                                                                       |
| ------------------------------------------ | --------------------------------------------------------------------------------------------- |
| `repeat`                                   | Run, 0 to 9                                                                                   |
| `step`                                     | Training step (one move on every board, followed by one gradient step)                        |
| `training_elapsed_s`                       | Seconds since the start of the run, **including** all earlier evaluation pauses                |
| `wall_time_s`                              | Seconds since the end of the previous evaluation (or the start of the run)                     |
| `lr`                                       | Learning rate                                                                                 |
| `loss`                                     | Mean squared TD error of the step                                                             |
| `W_norm`, `delta_W_norm`                   | L2 norm of the non-zero weights before the step, and of their change by the step              |
| `rel_weight_update`                        | `delta_W_norm / W_norm`                                                                       |
| `V_old_min`, `_max`, `_mean`, `_std`, `_abs_mean` | Statistics of the network values of the afterstates updated in the step               |
| `grad_nnz`, `grad_mean`, `grad_std`        | Number of weights with a non-zero gradient, and mean and standard deviation of those gradients |
| `update_frac`                              | Fraction of the boards whose transition was used for the update                               |
| `done_frac`                                | Fraction of the boards whose game ended in the step                                           |
| `randomize_frac`                           | Fraction of the boards on which a random (exploratory) move was made                          |
| `n_wins`                                   | Number of boards with a four in a row after the step                                          |
| `moves_left_mean`, `moves_left_std`        | Mean and standard deviation of the number of empty cells over the boards                       |

## `arena.csv.gz`

| Column                             | Meaning                                                                                                  |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `repeat`, `step`                   | Run and training step of the evaluation                                                                  |
| `training_elapsed_s`               | Seconds since the start of the run, at the end of the evaluation                                         |
| `agent_yellow`, `agent_red`        | Players; Yellow moves first. `ntuple` is the trained agent, `random` plays random moves, `bitbully-*` are the search opponents |
| `epsilon_yellow`, `epsilon_red`    | Probability with which the player replaces its move by a random move that does not allow an immediate win of the other side |
| `games`                            | Number of games of the pairing                                                                           |
| `yellow_wins`, `red_wins`, `draws` | Outcomes                                                                                                 |

The duration of an evaluation is the difference between `training_elapsed_s` in `arena.csv.gz` and in
`metrics.csv.gz` at the same run and step. The post explains how the training time without evaluations
follows from it.

## `selection.json`

`candidates` lists, for each final agent (`checkpoint`), its results per condition (`rows`: side of the agent,
opponent, opponent epsilon, wins, draws, losses and games from the agent's point of view), the ranking criterion
(mean of `(wins - losses) / games` over the 22 conditions against BitBully) and the duration of its tournament in
seconds. `selected` holds the best agent and its results on fresh games. The script
`tools/connect4_rl/select_strongest.py` in this blog's repository produced the file; only the Google Drive paths
of the checkpoints are shortened to the run folder.

## Variants: `variant-slow-target/` and `variant-decaying-epsilon/`

Ten runs each of the two variants in the post's section "How Much Do the Settings Matter?", in the same format as the files above
(`params.json`, `ntuples.json`, `metrics.csv.gz`, `arena.csv.gz`):

| Folder                      | Differs from the recipe of the post                                                   |
| --------------------------- | -------------------------------------------------------------------------------------- |
| `variant-slow-target/`      | `tau = 0.05`                                                                           |
| `variant-decaying-epsilon/` | epsilon decreasing linearly from 0.2 to 0.02 over the 25,000 steps (the logged `epsilon` is the start value), `lam = 0.75`, `n_truncate = 8` |

`tools/connect4_rl/make_connect4_comparison_figures.py` computes the comparison figure and numbers from these folders
and the files of the recipe above.

The raw output of the variants, including text logs and final weights, is in the Google Drive folders
[variant-slow-target](https://drive.google.com/drive/folders/1WDT20CJJlLN1gia7THRk3o9piUQPhIyq?usp=sharing) and [variant-decaying-epsilon](https://drive.google.com/drive/folders/1P9dSZbrMgoGBSHaQC4_Gs9uOTOU-SJm5?usp=sharing).

## `earlier-sweeps.json`

Summary of the earlier sweeps (37 experiments, ten runs each, April to July 2026, plus the three runs of the post),
exported by the comparison notebook of techdays26: per setting the logged parameters, the differences from the
settings of that time (`diffs_from_baseline`), the final score of every matchup (`final_avg`, from Yellow's point
of view, and `final_std` over the ten runs), and the ranking score of the sweeps (first-player score over all
opponents, averaged over all evaluations). Only the Google Drive paths of the run folders are shortened to the
folder names. The post's appendix "Earlier Sweeps" summarises it.
