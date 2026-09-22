/**
 * Interactive bit board explorer for part 3 of the Connect-4 series.
 *
 * Lets the reader click a column and watch the two 64-bit words change. All
 * board arithmetic lives in `connect4-core.js`, which is verified against the
 * C++ engine by `tools/connect4/check_widget.mjs`.
 */
(function () {
  "use strict";

  function build(root) {
    const C4 = window.C4;
    const state = { all: 0n, active: 0n, movesLeft: 42, history: [] };

    root.innerHTML = `
      <div class="c4bb-controls">
        <button type="button" data-act="undo">Undo</button>
        <button type="button" data-act="reset">Reset</button>
        <button type="button" data-act="demo">Example position</button>
        <span class="c4bb-hint">click a column to drop a token</span>
      </div>
      <div class="c4bb-grid" role="group" aria-label="Connect-4 bit board"></div>
      <div class="c4bb-legend">
        <span><i class="c4bb-sw c4bb-yellow"></i>player to move</span>
        <span><i class="c4bb-sw c4bb-red"></i>opponent</span>
        <span><i class="c4bb-sw c4bb-legal"></i>legal move (carry lands here)</span>
        <span><i class="c4bb-sw c4bb-threat"></i>winning cell for the player to move</span>
        <span><i class="c4bb-sw c4bb-guard"></i>guard bit</span>
      </div>
      <dl class="c4bb-readout"></dl>`;

    const grid = root.querySelector(".c4bb-grid");
    const readout = root.querySelector(".c4bb-readout");
    const cells = [];

    for (let r = C4.N_ROWS + 2; r >= 0; r--) {
      for (let c = 0; c < C4.N_COLUMNS; c++) {
        const cell = document.createElement("button");
        cell.type = "button";
        cell.className = "c4bb-cell" + (r >= C4.N_ROWS ? " c4bb-guard" : "");
        cell.dataset.col = c;
        cell.dataset.row = r;
        cell.textContent = c * 9 + r;
        if (r < C4.N_ROWS) cell.addEventListener("click", () => play(c));
        else cell.disabled = true;
        grid.appendChild(cell);
        cells.push(cell);
      }
    }

    function play(col) {
      const legal = C4.legalMovesMask(state.all);
      let mv = 0n;
      for (let r = 0; r < C4.N_ROWS; r++) {
        const b = C4.bitOf(col, r);
        if (legal & b) {
          mv = b;
          break;
        }
      }
      if (!mv || C4.hasWin(state.all, state.active)) return;
      state.history.push({ all: state.all, active: state.active, movesLeft: state.movesLeft });
      Object.assign(state, C4.play(state, mv));
      render();
    }

    function reset() {
      state.all = 0n;
      state.active = 0n;
      state.movesLeft = 42;
      state.history = [];
    }

    root.querySelector('[data-act="undo"]').addEventListener("click", () => {
      const prev = state.history.pop();
      if (prev) {
        Object.assign(state, prev);
        render();
      }
    });
    root.querySelector('[data-act="reset"]').addEventListener("click", () => {
      reset();
      render();
    });
    root.querySelector('[data-act="demo"]').addEventListener("click", () => {
      reset();
      [3, 3, 4, 4, 5, 2, 3].forEach(play);
    });

    function render() {
      const legal = C4.legalMovesMask(state.all);
      const opponent = (state.active ^ state.all) & C4.MASK64;
      const won = C4.hasWin(state.all, state.active);
      const threats = C4.winningPositions(state.active, true) & ~state.all & C4.MASK64;

      for (const cell of cells) {
        const b = C4.bitOf(+cell.dataset.col, +cell.dataset.row);
        cell.classList.remove("c4bb-yellow", "c4bb-red", "c4bb-legal", "c4bb-threat");
        if (+cell.dataset.row >= C4.N_ROWS) continue;
        if (state.active & b) cell.classList.add("c4bb-yellow");
        else if (opponent & b) cell.classList.add("c4bb-red");
        else if (threats & b) cell.classList.add("c4bb-threat");
        else if (legal & b) cell.classList.add("c4bb-legal");
      }

      const row = (k, v, cls) => `<dt>${k}</dt><dd class="${cls || ""}">${v}</dd>`;
      readout.innerHTML =
        row("m_bAllTokens", `<code>${C4.fmtHex(state.all)}</code><br><code class="c4bb-bin">${C4.fmtBin(state.all)}</code>`) +
        row("m_bActivePTokens", `<code>${C4.fmtHex(state.active)}</code><br><code class="c4bb-bin">${C4.fmtBin(state.active)}</code>`) +
        row("opponent (active ^ all)", `<code>${C4.fmtHex(opponent)}</code>`) +
        row("legalMovesMask()", `<code>${C4.fmtHex(legal)}</code>`) +
        row("uid() = active + all", `<code>${C4.fmtHex(state.active + state.all)}</code>`) +
        row("movesLeft()", `<code>${state.movesLeft}</code>`) +
        row(
          "hasWin()",
          won ? "<strong>true</strong> &mdash; the player who just moved has four in a row" : "<code>false</code>",
          won ? "c4bb-win" : ""
        );
    }

    render();
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-c4-bitboard]").forEach(build);
  });
})();
