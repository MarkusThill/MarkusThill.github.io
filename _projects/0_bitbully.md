---
layout: page
title: BitBully
description: One of the fastest and perfect-playing Connect-4 solvers around
img: assets/img/project_bitbully/bitbully-logo-full.png
# redirect: https://unsplash.com
importance: 1
category: fun
related_publications: true
giscus_comments: true
---

**Links**  
🔗 [GitHub](https://github.com/MarkusThill/BitBully) · [PyPI](https://pypi.org/project/bitbully) · [Docs](https://markusthill.github.io/BitBully)

<div class="row">
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/project_bitbully/c4-1.png" title="Connect4 (1)" class="img-fluid rounded z-depth-1" %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/project_bitbully/c4-2.png" title="Connect4 (2)" class="img-fluid rounded z-depth-1" %}
    </div>
    <div class="col-sm mt-3 mt-md-0">
        {% include figure.liquid loading="eager" path="assets/img/project_bitbully/c4-3.png" title="Connect4 (3)" class="img-fluid rounded z-depth-1" %}
    </div>
</div>
<div class="caption">
    <b>From Opening to Victory:</b> The image shows three key stages of a Connect 4 match — an early board with initial placements, a mid-game filled with tension and strategy, and the final state where yellow wins by connecting four discs. Connect 4 is a two-player game where discs are dropped into columns, aiming to form a straight line of four. It blends tactical planning with defensive play, and despite its simplicity, it’s a classic example of solvable strategy games in AI.
</div>

**BitBully** is a high-performance, perfect-playing Connect-4 solver and analysis engine written in C++ with Python bindings. It’s designed for both developers and researchers who want to explore game-theoretic strategies or integrate a strong Connect-4 AI into their own projects.

---

## 🚀 Key Features

- **Blazing Fast Solving**: Uses MTD(f) and null-window search algorithms.
- **Bitboard Engine**: Board states are handled efficiently via low-level bitwise operations.
- **Advanced Heuristics**: Threat detection, move ordering, and transposition tables.
- **Opening Databases**: Covers all positions with up to 12 tokens, annotated with exact win/loss distances.
- **Cross-Platform**: Compatible with Linux, Windows, and macOS.
- **Python API**: Seamlessly integrates into Python projects via `bitbully_core` (powered by `pybind11`).
- **Open Source**: Available under the AGPL-3.0 license.

---

## 📦 Installation

Install the latest stable release from PyPI:

```bash
pip install bitbully
```

No compilation needed—pre-built wheels included!

---

## 🧠 Example Usage (Python)

```python
from bitbully import bitbully_core as bbc
import time

board = bbc.Board()
for _ in range(6):
    board.playMove(3)
print(board)

solver = bbc.BitBully()
start = time.time()
score = solver.mtdf(board, first_guess=0)
print(f"Solved in {round(time.time() - start, 2)}s → Score: {score}")
```

You can also solve boards defined as NumPy arrays, use opening books, and generate random game states.
For more examples check out the [docs](https://markusthill.github.io/BitBully) or the [GitHub repository](https://github.com/MarkusThill/BitBully)· 

---

## 📜 License

AGPL-3.0. [View License](https://github.com/MarkusThill/BitBully/tree/master?tab=AGPL-3.0-1-ov-file#readme)

---

## 🙏 Acknowledgments

Inspired by the solvers of [Pascal Pons](https://github.com/PascalPons/connect4) and [John Tromp](https://tromp.github.io/c4/Connect4.java).

---

## Related Work

### Literature
The application of machine learning to board games remains an active and challenging research area, particularly due to the complexity and strategic depth of games like Chess, Go, and Connect Four. Unlike humans who can intuitively recognize patterns, artificial agents require structured learning approaches, often supported by carefully engineered features or representations.

A milestone in this field was **Tesauro’s TD-Gammon**, which demonstrated that self-play combined with temporal difference learning (TDL) could lead to expert-level performance in backgammon. Inspired by this success, many studies attempted to apply TDL to other board games, but the outcomes were often mixed due to higher complexity and lack of domain knowledge {% cite Thill12 Thil12 %}.

Prior work on **Connect Four** showed that learning strong strategies through self-play alone is feasible, but only with a **very rich feature representation** and a large number of training games. One such approach used **N-tuple systems** in combination with TDL to approximate value functions. These systems produced high-quality agents capable of defeating even perfect-play opponents, all without incorporating handcrafted game-theoretic knowledge. The success was largely attributed to the expressiveness of the N-tuple representation and extensive training with millions of games {% cite Thill12 Thil12 %}.

Subsequent research introduced **eligibility traces**—including standard, resetting, and replacing variants—into these systems. Eligibility traces enhanced temporal credit assignment and significantly **accelerated learning (by a factor of two)** while improving asymptotic playing strength {% cite Thill2015a %}.

To further improve training efficiency, recent studies investigated **online-adaptable learning rate algorithms**, such as **Incremental Delta-Bar-Delta (IDBD)** and **Temporal Coherence Learning (TCL)**. A novel variant using **geometric step-size adaptation** outperformed conventional methods, reducing the number of required training games by **up to 75%** in some cases. The most effective algorithms proved to be those that combined geometric learning rates with nonlinear value functions and eligibility traces. These methods brought the total training requirement for learning Connect Four **down to just over 100,000 games**, a **13× improvement** over earlier baselines {% cite bagh16b %}.

Finally, preliminary experiments also applied this enhanced learning framework to other strategic games, such as **Dots-and-Boxes**, showing the framework’s potential for broader generalization, though some unique domain-specific challenges were identified {% cite Thil14 %}.

### [Connect-4 Game Playing Framework (C4GPF)](https://github.com/MarkusThill/Connect-Four)

The **C4GPF** is a Java-based framework for training, evaluating, and interacting with Connect Four agents. It features a GUI and supports various agent types, including:

- **Perfect-play Minimax agent** with database and transposition table support.
- **Reinforcement Learning agent** using n-tuple systems and TD-learning with eligibility traces.
- **Monte Carlo Tree Search (MCTS)** agent.
- **RL-Minimax hybrid**, combining tree search with learned state evaluations.

Key capabilities include:
- Animated or step-by-step agent matches.
- Benchmarking and head-to-head competitions.
- Visualization and editing of n-tuple lookup tables.
- Support for adaptive step-size algorithms (e.g., IDBD, TCL, AutoStep).

The framework is extensible and designed for research and teaching.

**🔗 Repository:** [Connect-4 Game Playing Framework (C4GPF)](https://github.com/MarkusThill/Connect-Four)

### [General Board Game Framework (GBG)](https://github.com/WolfgangKonen/GBG)

**GBG** is a flexible Java-based framework for **general board game (GBG)** learning and playing. Designed for research and education, it allows users to implement new board games or AI agents once and run them across all supported components.

Key features:
- Supports **1-player, 2-player, and n-player** board games.
- Comes with a variety of **built-in AI agents**, including reinforcement learning and tree-based strategies.
- Standardized **interfaces and abstract classes** make it easy to plug in new games or agents.
- Enables fair **competitions and benchmarking** between agents across multiple games.
- Suitable for both classroom use and research projects.

The framework includes documentation, a GUI, and a [technical report](http://www.gm.fh-koeln.de/ciopwebpub/Konen22a.d/TR-GBG.pdf) explaining its architecture.

**🔗 Repository:** [General Board Game Framework (GBG)](https://github.com/WolfgangKonen/GBG)


<br>