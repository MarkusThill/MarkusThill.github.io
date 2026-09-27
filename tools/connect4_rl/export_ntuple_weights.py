"""
Export the weights of a trained n-tuple network in a compact format for the in-browser agent.

Only the realisable table entries are stored, in the order of `realisable_states.Ranking`, so the file
needs no indices: for each player p (0 = yellow to move, 1 = red to move) and tuple m, the values
W[p, m, unrank(0)], W[p, m, unrank(1)], ... follow each other.

File layout (gzip-compressed as a whole):
    b"C4NT"                     magic
    uint32 little endian        length L of the JSON header
    L bytes                     JSON header: format, dtype, tuples, counts, scales (int8 only), source
    values                      int8 | float16 | float32, little endian, player-major, then tuple-major

Run with a Python environment that has PyTorch and techdays26 installed:
    python tools/connect4_rl/export_ntuple_weights.py <checkpoint.pt> <out.bin.gz> --dtype int8
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import struct
from pathlib import Path

import numpy as np
import torch

from realisable_states import Ranking

DTYPES = {"int8": np.int8, "float16": np.float16, "float32": np.float32}


def realisable_values(W: np.ndarray, tuples: list[list[int]]) -> tuple[list[np.ndarray], list[int]]:
    """Per (player, tuple) the weights of all realisable entries in rank order."""
    rankings = [Ranking(t) for t in tuples]
    order = [np.array(r.indices(), dtype=np.int64) for r in rankings]
    nonzero_outside = sum(int(np.count_nonzero(np.delete(W[p, m], order[m]))) for p in range(2) for m in range(len(tuples)))
    if nonzero_outside:
        raise ValueError(f"{nonzero_outside} non-zero weights outside the realisable set")
    values = [W[p, m, order[m]] for p in range(2) for m in range(len(tuples))]
    return values, [r.count for r in rankings]


def export(checkpoint: Path, out: Path, dtype: str) -> dict:
    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    W = payload["state_dict"]["W"].numpy().astype(np.float32)
    tuples = [list(map(int, t)) for t in payload["n_tuple_list"]]
    values, counts = realisable_values(W, tuples)
    header = {"format": "c4-ntuple-realisable", "version": 1, "dtype": dtype, "tuple_length": len(tuples[0]),
              "tuples": tuples, "counts": counts,
              "source_sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest()}
    if dtype == "int8":
        scales = [float(np.abs(v).max()) / 127 if v.size and np.abs(v).max() > 0 else 1.0 for v in values]
        header["scales"] = scales
        body = b"".join(np.clip(np.round(v / s), -127, 127).astype(np.int8).tobytes() for v, s in zip(values, scales))
    else:
        body = b"".join(v.astype(DTYPES[dtype]).astype(f"<{np.dtype(DTYPES[dtype]).str[1:]}").tobytes() for v in values)
    head = json.dumps(header, separators=(",", ":")).encode()
    raw = b"C4NT" + struct.pack("<I", len(head)) + head + body
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(gzip.compress(raw, 9))
    return {"values": int(sum(counts) * 2), "raw_bytes": len(raw), "gzip_bytes": out.stat().st_size}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--dtype", choices=sorted(DTYPES), default="int8")
    args = parser.parse_args()
    print(export(args.checkpoint, args.out, args.dtype))


if __name__ == "__main__":
    main()
