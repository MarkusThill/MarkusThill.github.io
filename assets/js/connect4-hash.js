/**
 * Interactive transposition and hashing explorer for part 5 of the Connect-4
 * series.
 *
 * The reader plays moves and watches three numbers change: uid(), the board
 * hash produced from the two bitboards with Mix13, and the table index derived
 * from the hash. A small 64-slot transposition table is kept across board
 * resets, so reaching the same position through a different move order
 * produces a visible table hit, and two different positions landing in the
 * same slot produce a visible collision. Flipped bits are highlighted after
 * every move to make the avalanche effect of the hash tangible.
 *
 * All board arithmetic lives in `connect4-core.js`, which is verified against
 * the C++ engine by `tools/connect4/check_widget.mjs`.
 */
(function () {
  "use strict";

  const K = 6; // 2^6 = 64 slots -- small enough to draw, big enough to be honest

  function build(root) {
    const C4 = window.C4;
    const state = { all: 0n, active: 0n, movesLeft: 42, history: [], path: [] };
    // The little transposition table: index -> [{uid, path}]. It survives
    // "Reset board" on purpose; only "Clear table" empties it.
    let table = new Map();
    let stored = new Map(); // uid -> path of first storage
    let prev = null; // previous {uid, hash} for the flipped-bit display

    root.innerHTML = `
      <div class="c4bb-controls">
        <button type="button" data-act="undo">Undo</button>
        <button type="button" data-act="reset">Reset board</button>
        <button type="button" data-act="clear">Clear table</button>
        <button type="button" data-act="seqA">Play 3, 4, 2, 5</button>
        <button type="button" data-act="seqB">Play 2, 5, 3, 4</button>
        <span class="c4bb-hint">click a column &mdash; the table keeps its entries across board resets</span>
      </div>
      <div class="c4bb-grid" role="group" aria-label="Connect-4 board"></div>
      <dl class="c4bb-readout"></dl>
      <div class="c4bb-slots" aria-label="transposition table slots"></div>
      <div class="c4bb-legend">
        <span><i class="c4bb-sw c4bb-slot-used"></i>occupied slot</span>
        <span><i class="c4bb-sw c4bb-slot-here"></i>slot of the current position</span>
        <span><i class="c4bb-sw c4bb-slot-coll"></i>collision: two different positions in one slot</span>
      </div>
      <p class="c4bb-hashmsg"></p>`;

    const grid = root.querySelector(".c4bb-grid");
    const readout = root.querySelector(".c4bb-readout");
    const slotsEl = root.querySelector(".c4bb-slots");
    const msgEl = root.querySelector(".c4bb-hashmsg");
    const cells = [];

    for (let r = C4.N_ROWS - 1; r >= 0; r--) {
      for (let c = 0; c < C4.N_COLUMNS; c++) {
        const cell = document.createElement("button");
        cell.type = "button";
        cell.className = "c4bb-cell";
        cell.dataset.col = c;
        cell.dataset.row = r;
        cell.addEventListener("click", () => play(c));
        grid.appendChild(cell);
        cells.push(cell);
      }
    }

    for (let i = 0; i < 1 << K; i++) {
      const s = document.createElement("i");
      s.className = "c4bb-slot";
      s.dataset.idx = i;
      slotsEl.appendChild(s);
    }
    const slotCells = Array.from(slotsEl.children);

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
      state.history.push({ all: state.all, active: state.active, movesLeft: state.movesLeft, path: state.path });
      prev = snapshot();
      const next = C4.play(state, mv);
      state.all = next.all;
      state.active = next.active;
      state.movesLeft = next.movesLeft;
      state.path = state.path.concat(col);
      store();
      render();
    }

    function snapshot() {
      const uid = state.all + state.active;
      return { uid, hash: C4.boardHash(state.all, state.active) };
    }

    function store() {
      const { uid, hash } = snapshot();
      if (state.path.length === 0) return; // the empty board is not worth a slot
      const idx = Number(hash & BigInt((1 << K) - 1));
      if (!stored.has(uid)) {
        stored.set(uid, state.path.join(", "));
        if (!table.has(idx)) table.set(idx, []);
        table.get(idx).push(uid);
      }
    }

    function resetBoard() {
      prev = null;
      state.all = 0n;
      state.active = 0n;
      state.movesLeft = 42;
      state.history = [];
      state.path = [];
    }

    root.querySelector('[data-act="undo"]').addEventListener("click", () => {
      const p = state.history.pop();
      if (p) {
        prev = null;
        Object.assign(state, { all: p.all, active: p.active, movesLeft: p.movesLeft, path: p.path });
        render();
      }
    });
    root.querySelector('[data-act="reset"]').addEventListener("click", () => {
      resetBoard();
      render();
    });
    root.querySelector('[data-act="clear"]').addEventListener("click", () => {
      table = new Map();
      stored = new Map();
      resetBoard();
      render();
    });
    root.querySelector('[data-act="seqA"]').addEventListener("click", () => {
      resetBoard();
      [3, 4, 2, 5].forEach(play);
    });
    root.querySelector('[data-act="seqB"]').addEventListener("click", () => {
      resetBoard();
      [2, 5, 3, 4].forEach(play);
    });

    /** 64-bit binary string with the bits that differ from `ref` wrapped. */
    function markedBits(v, ref) {
      let out = "";
      for (let i = 63n; i >= 0n; i--) {
        const bit = (v >> i) & 1n;
        const flip = ref !== null && bit !== ((ref >> i) & 1n);
        out += flip ? `<span class="c4bb-flip">${bit}</span>` : bit.toString();
        if (i % 8n === 0n && i > 0n) out += " ";
      }
      return out;
    }

    const flips = (v, ref) => (ref === null ? null : C4.popcount((v ^ ref) & C4.MASK64));

    function render() {
      const legal = C4.legalMovesMask(state.all);
      const opponent = (state.active ^ state.all) & C4.MASK64;
      for (const cell of cells) {
        const b = C4.bitOf(+cell.dataset.col, +cell.dataset.row);
        cell.className = "c4bb-cell";
        if (state.active & b) cell.classList.add("c4bb-yellow");
        else if (opponent & b) cell.classList.add("c4bb-red");
        else if (legal & b) cell.classList.add("c4bb-legal");
      }

      const { uid, hash } = snapshot();
      const idx = Number(hash & BigInt((1 << K) - 1));
      const uidFlips = flips(uid, prev ? prev.uid : null);
      const hashFlips = flips(hash, prev ? prev.hash : null);

      const row = (k, v, cls) => `<dt>${k}</dt><dd class="${cls || ""}">${v}</dd>`;
      readout.innerHTML =
        row("moves so far", state.path.length ? `<code>${state.path.join(", ")}</code>` : "<code>&mdash;</code>") +
        row("uid() = active + all", `<code>${C4.fmtHex(uid)}</code><br><code class="c4bb-bin">${markedBits(uid, prev ? prev.uid : null)}</code>`) +
        row("hash()", `<code>${C4.fmtHex(hash)}</code><br><code class="c4bb-bin">${markedBits(hash, prev ? prev.hash : null)}</code>`) +
        (uidFlips !== null
          ? row("bits flipped by the last move", `<code>${uidFlips}</code> of 64 in uid, <code>${hashFlips}</code> of 64 in the hash`)
          : "") +
        row(`index = hash &amp; (2<sup>${K}</sup> &minus; 1)`, `<code>${idx}</code>`);

      // Slot strip.
      for (const s of slotCells) {
        s.className = "c4bb-slot";
        const entry = table.get(+s.dataset.idx);
        if (entry && entry.length > 1) s.classList.add("c4bb-slot-coll");
        else if (entry) s.classList.add("c4bb-slot-used");
      }
      if (state.path.length) slotCells[idx].classList.add("c4bb-slot-here");

      // Transposition / collision message.
      let msg = "";
      if (state.path.length && stored.has(uid) && stored.get(uid) !== state.path.join(", ")) {
        msg = `<strong>Table hit:</strong> this position was already stored after the moves <code>${stored.get(uid)}</code> &mdash; a transposition.`;
      } else if (state.path.length && table.get(idx) && table.get(idx).length > 1) {
        msg = `<strong>Collision:</strong> slot ${idx} already holds a different position. The stored <code>uid</code> is what tells the two apart.`;
      }
      msgEl.innerHTML = msg;
    }

    render();
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-c4-hash]").forEach(build);
  });
})();
