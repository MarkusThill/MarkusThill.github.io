---
layout: page
title: BitBully Databases
description: Precomputed Connect-4 opening books with millions of evaluated positions
img: https://raw.githubusercontent.com/MarkusThill/bitbully-databases/master/bitbully-databases-logo.png
importance: 2
category: fun
related_publications: false
giscus_comments: true
---

**Links**  
🔗 [GitHub](https://github.com/MarkusThill/bitbully-databases) ·
[PyPI](https://pypi.org/project/bitbully-databases) ·
[Docs](https://markusthill.github.io/bitbully-databases)

<h1 align="center">
<img src="https://raw.githubusercontent.com/MarkusThill/bitbully-databases/master/bitbully-databases-logo.png"
     alt="bitbully-databases-logo"
     width="400">
</h1>

---

**BitBully Databases** is a companion project to
[BitBully](https://github.com/MarkusThill/BitBully) that provides **precomputed Connect-4 opening books**
containing **millions of fully evaluated positions**.

Each database stores Huffman-encoded board states together with exact **game-theoretic evaluations**
(win, loss, or draw), optionally extended by **signed distance-to-win / distance-to-loss values**.
The databases are distributed as compact binary assets and can be accessed directly from Python via the
`bitbully_databases` module.

In addition to the data itself, the package includes a **pure-Python reference implementation**
(without a NumPy dependency) that demonstrates how to read, search, and interpret these databases.
This makes BitBully Databases suitable both for **educational purposes** and for **research-oriented exploration**.
For performance-critical inference and solver integration, the native
**C++ / pybind11 BitBully API** can be used.

---

<br>

## 🚀 Key Features

- **Large-Scale Opening Books** with millions of evaluated positions
- **Exact Game-Theoretic Values** (win / loss / draw)
- **Optional Distance Information** indicating moves until win or loss
- **Huffman-Encoded Board Representation** for compact storage
- **Pure-Python Reference Implementation** (no NumPy dependency)
- **Binary-Search Lookup** over sorted position–value tables
- **Symmetry Handling** via horizontal board mirroring
- **Designed for Integration** with the BitBully solver

---

### 🕰️ Historical Note on the 8-Ply Database

The **8-ply opening database** included in *BitBully Databases* is based on the pioneering work of **John Tromp**, who was among the first to strongly solve large parts of Connect-4 by exhaustively enumerating and evaluating all positions up to 8 plies. Tromp's computation—performed on Sun and SGI workstations at [CWI](https://www.cwi.nl/) — required an impressive **≈ 40,000 hours of CPU time**, making it one of the most computationally demanding Connect-4 database efforts of its time.  

However, Tromp's original 8-ply database did not include positions with immediate winning threats for Red, implicitly treating such positions as already decided. In practice, these positions are *not terminal*, since Yellow may still be able to neutralize the threat and continue the game. To address this subtle but important detail, the 8-ply database distributed with BitBully was extended to include and correctly score these neutralizable threat positions, resulting in a more accurate and practically useful opening book.  

For historical context and further details, see John Tromp’s original Connect-4 page:

👉 [https://tromp.github.io/c4/c4.html](https://tromp.github.io/c4/c4.html)


<br>

## 🗂️ Available Databases

| Name | Ply Depth | Entries | Win Distances | Disk Size | In-Memory Size (Python) | Description |
|------|-----------|----------|---------------|-----------|-------------------------|-------------|
| **8-ply** | 8 | 34 515 | ✗ | 102 KB | ~271 KB | Smallest opening book. Stores only Red-win/draw outcomes (not contained=Yellow-win). |
| **12-ply** | 12 | 1 735 945 | ✗ | 6.7 MB | ~14.9 MB | Covers all positions up to 12 plies with Red-win/draw values (not contained=Yellow-win). |
| **12-ply-dist** *(default)* | 12 | 4 200 899 | ✓ | 21 MB | ~33.1 MB | Most detailed book. Includes signed distance-to-win/loss values. Recommended for analysis and research. |

All databases are **sorted by Huffman-encoded position keys** to enable efficient binary-search lookups.

---

<br>

## 🔍 BitBully vs. BitBully Databases

While **BitBully** is a high-performance **solver and analysis engine** that computes Connect-4 positions on the fly using advanced search algorithms (MTD(f), null-window search, transposition tables), **BitBully Databases** provide **precomputed opening books** with exact game-theoretic values for millions of early-game positions. In practice, BitBully Databases act as a *knowledge source*—enabling instant lookup of optimal evaluations—whereas BitBully is the *reasoning engine* that explores and solves positions beyond the database horizon. The two projects are designed to complement each other: databases accelerate early-game analysis and research workflows, while the solver handles deeper or unseen positions with perfect-play guarantees.


## 🎓 Educational and Research Focus

The pure-Python implementation emphasizes **clarity over raw performance** and illustrates:

- Huffman encoding of Connect-4 board states  
- Binary search over large, sorted opening books  
- Symmetry reduction through horizontal mirroring  
- Interpretation of win/loss and distance-to-win values  

For large-scale simulations or solver-level performance, the
[BitBully C++/pybind11 API](https://github.com/MarkusThill/BitBully)
should be preferred.

---

<br>

## 📚 Further Resources

- **Documentation & API Reference**  
  👉 [https://markusthill.github.io/bitbully-databases](https://markusthill.github.io/bitbully-databases)
- **Main Solver Project (BitBully)**  
  👉 [https://github.com/MarkusThill/BitBully](https://markusthill.github.io/bitbully-databases)

---

<br>

## 📜 License

MIT License.
See the [license file](https://github.com/MarkusThill/bitbully-databases) for details.

---

<br>

## 📦 Installation

Install the latest stable release from PyPI:

```bash
pip install bitbully-databases
```

Pre-packaged binary databases are included — no compilation required.

<br>

## 🧠 Example Usage (Python)
### Basic Database Usage

```python
import bitbully_databases as bbd

# Load the 12-ply book with distances (default)
db = bbd.BitBullyDatabases("12-ply-dist")

# Get the absolute file path of the packaged database
path = bbd.BitBullyDatabases.get_database_path("12-ply-dist")
print("Database path:", path)

# Inspect database metadata
print("Book size:", db.get_book_size())
print("Memory size (bytes):", db.get_book_memory_size())
print("Contains win distances:", db.has_win_distances())
```

### Querying a Board Position

```python
board = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 1, 0, 2, 0, 0, 0],
    [0, 2, 0, 1, 0, 2, 0],
    [0, 1, 0, 2, 0, 1, 0],
    [0, 2, 0, 1, 0, 2, 0],
]

value = db.get_book_value(board)
print("Book value:", value)

if value is not None and db.has_win_distances():
    print(f"→ Player 1 wins in {100 - abs(value)} moves.")
```

**8-Ply Database — Win/Loss Only**

```python
val = bbd.BitBullyDatabases("8-ply").get_book_value(board)
print(val)  # → 1 (Player 1 win)
```

**12-Ply Database — Win/Loss/Draw**

```python
val = bbd.BitBullyDatabases("12-ply").get_book_value(board)
print(val)  # → 0 (draw)
```

**12-Ply-Dist Database — Distance Values**

```python
val = bbd.BitBullyDatabases("12-ply-dist").get_book_value(board)
print(val)  # → 71 (Player 1 wins in 29 moves)
```
