# de Bruijn circle tools

Scripts behind the post *Binary Circles, Hamiltonian Cycles and de Bruijn Sequences*
(`_posts/2026-09-22-pe-165p100-binary-circles-and-de-bruijn-sequences.md`).

| File               | Purpose                                                                                   |
| ------------------ | ----------------------------------------------------------------------------------------- |
| `explore.py`       | Enumerates all circles for N <= 5, checks the count formula against the matrix-tree theorem, collects the per-position counts, verifies the reversal/complement symmetries, the Lyndon and prefer-one constructions, and the 64-bit bit-scan constant. Writes `data/explore.json`. |
| `dbseq.c`          | Same search in C with the visited set in a single `uint64_t`; reaches N = 6.               |
| `bitscan.c`        | Uses the smallest de Bruijn word of order 6 as the multiplication constant for locating a set bit; checks all 64 positions. |
| `bitpos_debruijn.c` | The same routine in the naming used by the bit-twiddling post (`initBitPosTable`, `bitPosDeBruijn`), with the `x & -x` call pattern. |
| `make_figures.py`  | Writes the three SVG figures to `assets/img/2026-09-22-binary-circles-de-bruijn/`.         |

```bash
python3 tools/debruijn/explore.py
gcc -O2 -o tools/debruijn/dbseq tools/debruijn/dbseq.c && ./tools/debruijn/dbseq 6
gcc -O2 -o /tmp/bitscan tools/debruijn/bitscan.c && /tmp/bitscan
gcc -O2 -o /tmp/bitpos tools/debruijn/bitpos_debruijn.c && /tmp/bitpos
python3 tools/debruijn/make_figures.py
```

Measurements quoted in the post were taken on an Intel Core i7-3520M (2.9 GHz),
CPython 3.10.12 and gcc with `-O2`.
