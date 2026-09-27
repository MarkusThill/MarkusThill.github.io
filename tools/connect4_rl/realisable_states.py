"""
Counting, enumerating and ranking the realisable states of an n-tuple on a Connect-4 board.

An n-tuple samples N cells of the board. Each cell is coded as 0 (empty), 1 (yellow), 2 (red) or
3 (empty and reachable, i.e. the next stone in its column lands there), and the tuple's table index
is sum_i code_i * 4**i over the tuple's cells in their listed order. Under gravity, most of the 4**N
indices can never occur. Within one column, the stones fill the rows from the bottom, the first free
row is reachable and every row above it is empty; different columns are independent. Hence the
realisable states of a tuple are all combinations of one realisable state per column.

This module
- counts them with the column recursion of the Bachelor thesis (`count_recursive`),
- enumerates them column by column (`column_states`, `realisable_indices`), and
- ranks them: `rank` maps a realisable table index to 0..r-1 and `unrank` maps it back, so that a
  trained table can be stored as r values without any indices.

Cells are given as bit indices of BitBully's layout, col * 9 + row (row 0 at the bottom).
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

N_ROWS = 6
COLUMN_BIT_OFFSET = 9
EMPTY, YELLOW, RED, REACHABLE = 0, 1, 2, 3


def cells(tuple_bits: list[int]) -> list[tuple[int, int]]:
    """(column, row) of every tuple cell, in tuple order."""
    return [divmod(b, COLUMN_BIT_OFFSET) for b in tuple_bits]


def count_recursive(tuple_bits: list[int]) -> int:
    """Number of realisable states: product over columns of the thesis recursion S(x, 0)."""
    rows_by_col: dict[int, set[int]] = {}
    for col, row in cells(tuple_bits):
        rows_by_col.setdefault(col, set()).add(row)
    total = 1
    for rows in rows_by_col.values():
        S = 1  # S(x, 6) = 1
        for y in range(N_ROWS - 1, -1, -1):
            p, p_above = int(y in rows), int(y + 1 in rows)
            z = 1 if y == 0 else 2  # non-filled states possible in row y
            S = S * (p + 1) + p * (z - 2 * p_above)
        total *= S
    return total


def count_column(rows: list[int]) -> int:
    """Realisable states of the sampled rows of one column, in closed form.

    With the sampled rows r_1 < ... < r_k, the lowest j of them can be filled (2**j colourings); the next
    one is then either reachable, or empty if at least one unsampled row lies below it (for j = 0: if it
    is not in the bottom row). With j = k all sampled cells are filled.
    """
    r = sorted(rows)
    total = 2 ** len(r)
    for j in range(len(r)):
        gap = r[j] if j == 0 else r[j] - r[j - 1] - 1  # unsampled rows directly below r_{j+1}
        total += 2**j * (1 + (gap > 0))
    return total


def count_closed_form(tuple_bits: list[int]) -> int:
    """Number of realisable states: product of the closed-form column counts."""
    rows_by_col: dict[int, list[int]] = {}
    for col, row in cells(tuple_bits):
        rows_by_col.setdefault(col, []).append(row)
    total = 1
    for rows in rows_by_col.values():
        total *= count_column(rows)
    return total


@dataclass(frozen=True)
class ColumnStates:
    column: int
    positions: tuple[int, ...]  # positions of this column's cells within the tuple
    partials: tuple[int, ...]  # sum code_i * 4**i over these cells, one per realisable state, sorted


def column_states(tuple_bits: list[int]) -> list[ColumnStates]:
    """The realisable states of every column the tuple touches, in increasing column order."""
    cs = cells(tuple_bits)
    result = []
    for col in sorted({c for c, _ in cs}):
        positions = tuple(i for i, (c, _) in enumerate(cs) if c == col)
        rows = [cs[i][1] for i in positions]
        partials = set()
        for height in range(N_ROWS + 1):  # number of stones in the column
            filled = [k for k, r in enumerate(rows) if r < height]
            for colours in itertools.product((YELLOW, RED), repeat=len(filled)):
                code = [EMPTY] * len(rows)
                for k, colour in zip(filled, colours):
                    code[k] = colour
                for k, r in enumerate(rows):
                    if r == height:
                        code[k] = REACHABLE
                partials.add(sum(v * 4**p for v, p in zip(code, positions)))
        result.append(ColumnStates(col, positions, tuple(sorted(partials))))
    return result


class Ranking:
    """Bijection between the realisable table indices of one tuple and 0..r-1.

    The rank is a mixed-radix number with one digit per column: the digit of a column is the position
    of its partial index in the sorted list of that column's realisable partials.
    """

    def __init__(self, tuple_bits: list[int]):
        self.columns = column_states(tuple_bits)
        self.sizes = [len(c.partials) for c in self.columns]
        self.count = 1
        for n in self.sizes:
            self.count *= n
        self.strides = []
        stride = 1
        for n in reversed(self.sizes):
            self.strides.insert(0, stride)
            stride *= n
        self._digit = [{p: d for d, p in enumerate(c.partials)} for c in self.columns]

    def partial(self, index: int, column: ColumnStates) -> int:
        """The part of a table index contributed by the cells of one column."""
        return sum(((index >> (2 * p)) & 3) << (2 * p) for p in column.positions)

    def rank(self, index: int) -> int:
        """Rank of a realisable table index (KeyError if the index is not realisable)."""
        return sum(self._digit[k][self.partial(index, c)] * self.strides[k] for k, c in enumerate(self.columns))

    def unrank(self, rank: int) -> int:
        index = 0
        for k, c in enumerate(self.columns):
            digit, rank = divmod(rank, self.strides[k])
            index += c.partials[digit]
        return index

    def indices(self) -> list[int]:
        """All realisable table indices, in rank order."""
        return [self.unrank(r) for r in range(self.count)]
