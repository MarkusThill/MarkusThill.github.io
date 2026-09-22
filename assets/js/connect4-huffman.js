/**
 * Interactive Huffman encoder for part 6 of the Connect-4 series.
 *
 * Walks `Board::toHuffman()` one symbol at a time: columns left to right, cells
 * bottom to top, emitting `10` or `11` per token and a single `0` to terminate
 * each column. The board highlights the cell currently being encoded and the
 * bit stream grows underneath.
 *
 * All board arithmetic lives in `connect4-core.js`.
 */
(function () {
  "use strict";

  function build(root) {
    const C4 = window.C4;
    const state = { all: 0n, active: 0n, movesLeft: 42, step: 0, timer: null };

    root.innerHTML = `
      <div class="c4bb-controls">
        <button type="button" data-act="step">Step</button>
        <button type="button" data-act="play">Play</button>
        <button type="button" data-act="rand8">Random 8-token position</button>
        <button type="button" data-act="rand12">Random 12-token position</button>
        <button type="button" data-act="reset">Clear</button>
        <span class="c4bb-hint">or click a column to place tokens yourself</span>
      </div>
      <div class="c4bb-grid" role="group" aria-label="Connect-4 board"></div>
      <div class="c4bb-legend">
        <span><i class="c4bb-sw c4bb-yellow"></i>player to move &rarr; <code>10</code></span>
        <span><i class="c4bb-sw c4bb-red"></i>opponent &rarr; <code>11</code></span>
        <span><i class="c4bb-sw c4bb-guard"></i>end of column &rarr; <code>0</code></span>
      </div>
      <div class="c4bb-bitstream"></div>
      <dl class="c4bb-readout"></dl>`;

    const grid = root.querySelector(".c4bb-grid");
    const stream = root.querySelector(".c4bb-bitstream");
    const readout = root.querySelector(".c4bb-readout");
    const cells = [];

    for (let r = C4.N_ROWS - 1; r >= 0; r--) {
      for (let c = 0; c < C4.N_COLUMNS; c++) {
        const cell = document.createElement("button");
        cell.type = "button";
        cell.className = "c4bb-cell";
        cell.dataset.col = c;
        cell.dataset.row = r;
        cell.addEventListener("click", () => {
          play(c);
        });
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
      if (!mv) return;
      Object.assign(state, C4.play(state, mv));
      state.step = 0;
      render();
    }

    function reset() {
      stop();
      state.all = 0n;
      state.active = 0n;
      state.movesLeft = 42;
      state.step = 0;
    }

    function randomPosition(nPly) {
      reset();
      let guard = 0;
      while (42 - state.movesLeft < nPly && guard++ < 500) {
        const legal = C4.legalMovesMask(state.all);
        const cols = [];
        for (let c = 0; c < C4.N_COLUMNS; c++) for (let r = 0; r < C4.N_ROWS; r++) if (legal & C4.bitOf(c, r)) cols.push(c);
        if (!cols.length) break;
        const col = cols[Math.floor(Math.random() * cols.length)];
        const before = state.all;
        play(col);
        // avoid finished games: undo a move that ends the game
        if (C4.hasWin(state.all, state.active)) {
          reset();
          continue;
        }
        if (state.all === before) break;
      }
      state.step = 0;
      render();
    }

    function stop() {
      if (state.timer) {
        clearInterval(state.timer);
        state.timer = null;
        root.querySelector('[data-act="play"]').textContent = "Play";
      }
    }

    root.querySelector('[data-act="step"]').addEventListener("click", () => {
      stop();
      const total = C4.toHuffman(state.all, state.active).steps.length;
      state.step = state.step >= total ? 0 : state.step + 1;
      render();
    });
    root.querySelector('[data-act="play"]').addEventListener("click", (ev) => {
      if (state.timer) return stop();
      const total = C4.toHuffman(state.all, state.active).steps.length;
      if (state.step >= total) state.step = 0;
      ev.target.textContent = "Pause";
      state.timer = setInterval(() => {
        if (state.step >= total) return stop();
        state.step++;
        render();
      }, 380);
    });
    root.querySelector('[data-act="reset"]').addEventListener("click", () => {
      reset();
      render();
    });
    root.querySelector('[data-act="rand8"]').addEventListener("click", () => randomPosition(8));
    root.querySelector('[data-act="rand12"]').addEventListener("click", () => randomPosition(12));

    function render() {
      const opponent = (state.active ^ state.all) & C4.MASK64;
      const huff = C4.toHuffman(state.all, state.active);
      const shown = huff.steps.slice(0, state.step);
      const current = huff.steps[state.step - 1];
      const nTokens = 42 - state.movesLeft;

      for (const cell of cells) {
        const c = +cell.dataset.col;
        const r = +cell.dataset.row;
        const b = C4.bitOf(c, r);
        cell.className = "c4bb-cell";
        if (state.active & b) cell.classList.add("c4bb-yellow");
        else if (opponent & b) cell.classList.add("c4bb-red");
        if (current && current.col === c && current.row === r) cell.classList.add("c4bb-current");
        cell.textContent = "";
      }

      stream.innerHTML =
        shown.map((s, i) => `<span class="c4bb-bit c4bb-bit-${s.kind}${i === shown.length - 1 ? " c4bb-bit-now" : ""}">${s.code}</span>`).join("") ||
        '<span class="c4bb-hint">press <em>Step</em> or <em>Play</em> to encode the position</span>';

      const emitted = shown.reduce((n, s) => n + s.code.length, 0);
      const totalBits = huff.bits.length;
      const row = (k, v, cls) => `<dt>${k}</dt><dd class="${cls || ""}">${v}</dd>`;
      const complete = state.step >= huff.steps.length && huff.steps.length > 0;

      readout.innerHTML =
        row("tokens on the board", `<code>${nTokens}</code>`) +
        row("bits emitted", `<code>${emitted}</code> of <code>${totalBits}</code>`) +
        row(
          "size of the entry",
          `<code>${Math.ceil(totalBits / 8)}</code> byte${Math.ceil(totalBits / 8) === 1 ? "" : "s"}` +
            ` &nbsp;(a naive 2 &times; 42-bit dump would need <code>11</code>)`
        ) +
        (complete ? row("toHuffman()", `<code>${C4.fmtHex(huff.value)}</code>`) : row("toHuffman()", "<code>&hellip;</code>")) +
        (nTokens === 8 || nTokens === 12
          ? row(
              "opening book",
              `this position has ${nTokens} tokens, so it is exactly the kind of entry stored in the ${nTokens}-ply database`,
              "c4bb-win"
            )
          : row("opening book", "the books only contain positions with 8 or 12 tokens; the encoding itself works for any position"));
    }

    render();
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-c4-huffman]").forEach(build);
  });
})();
