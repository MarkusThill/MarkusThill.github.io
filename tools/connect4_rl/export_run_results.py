"""
Compact, lossless extract of a training run for the blog's assets.

The training notebook writes, per run, a configuration file, the n-tuple set, and for every repeat a
metrics file (every 100 steps), an arena file (every 1,000 steps) and a text log. This script keeps
everything the analysis needs in four files:

    params.json      the run configuration, unchanged (GPU name, versions, commit)
    ntuples.json     the 200 n-tuples, unchanged
    metrics.csv.gz   one row per repeat and logged step, all numeric metrics
    arena.csv.gz     one row per repeat, evaluation step and pairing (agents, epsilons, games, outcomes)

Dropped are only the text logs, the formatted duplicate `training_elapsed` of the metrics, and the
arena columns `score` and `avg`, which follow from the outcomes. `connect4_results.load_run` reads the
extract like the original folder; the script checks this before it finishes.

    tools/connect4_rl/.venv/bin/python tools/connect4_rl/export_run_results.py \
        --run <exp_L_batch_fast_tau_...> --out assets/data/2026-08-27-near-perfect-connect4-in-five-minutes
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import shutil
from pathlib import Path

import connect4_results as cr

DROPPED_METRICS = {"training_elapsed"}
DROPPED_ARENA = {"score", "avg"}


def write_csv_gz(path: Path, header: list[str], rows: list[list]) -> None:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)  # floats as repr: exact round trip
    with gzip.GzipFile(path, "wb", mtime=0) as f:  # mtime=0: identical bytes for identical data
        f.write(buffer.getvalue().encode())


def export(run: Path, out: Path) -> None:
    params, repeats = cr.load_run(run)
    out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(run / "0_params.json", out / "params.json")
    shutil.copyfile(run / "0_ntuples.json", out / "ntuples.json")

    metric_keys = [k for k in repeats[0].metrics[0] if k not in DROPPED_METRICS]
    write_csv_gz(out / "metrics.csv.gz", ["repeat", *metric_keys],
                 [[rep.index, *(m[k] for k in metric_keys)] for rep in repeats for m in rep.metrics])

    arena_keys = [k for k in repeats[0].arena[0]["aggregates"][0] if k not in DROPPED_ARENA]
    write_csv_gz(out / "arena.csv.gz", ["repeat", "step", "training_elapsed_s", *arena_keys],
                 [[rep.index, a["step"], a["training_elapsed_s"], *(g[k] for k in arena_keys)]
                  for rep in repeats for a in rep.arena for g in a["aggregates"]])

    # The extract must load to the same data, apart from the dropped fields.
    params2, repeats2 = cr.load_run(out)
    assert params2 == params
    for r1, r2 in zip(repeats, repeats2, strict=True):
        assert r2.index == r1.index
        assert r2.metrics == [{k: v for k, v in m.items() if k not in DROPPED_METRICS} for m in r1.metrics]
        assert r2.arena == [{**a, "aggregates": [{k: v for k, v in g.items() if k not in DROPPED_ARENA}
                                                 for g in a["aggregates"]]} for a in r1.arena]
    for f in sorted(out.iterdir()):
        print(f"{f.stat().st_size / 1024:8.1f} KB  {f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True, help="run folder written by the training notebook")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    export(args.run, args.out)


if __name__ == "__main__":
    main()
