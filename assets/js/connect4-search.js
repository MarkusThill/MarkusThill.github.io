/**
 * Interactive search-driver race for part 7 of the Connect-4 series.
 *
 * Contains a real (if simplified) solver: a negamax with the free score
 * bounds, a Map-based transposition table with EXACT/LOWER/UPPER flags and
 * the threat-based move ordering -- everything the post describes, minus the
 * ETC/mirror/parity refinements of part 5. On top of it sit the same three
 * drivers as in BitBully: mtdf(), the wide-window negamax and the
 * binary-search nullWindow(). The widget solves a random position with all
 * three, shows the node counts and the probe sequences, and asserts that the
 * three scores agree.
 *
 * The solver namespace `C4Search` is exported separately from the DOM code so
 * that `tools/connect4/check_widget.mjs` can run the identical functions
 * headlessly and compare the scores against the C++ engine.
 */
(function (global) {
  "use strict";

  const C4 = global.C4;

  const EXACT = 1,
    LOWER = 2,
    UPPER = 3;

  function Solver() {
    this.tt = new Map(); // uid -> {flag, value}
    this.nodes = 0;
  }

  /** Can the player to move complete four in a row right now? */
  function canWin(st) {
    return (C4.winningPositions(st.active, true) & C4.legalMovesMask(st.all)) !== 0n;
  }

  /** Legal moves ordered the way sortMoves() + MoveList::pop would order them. */
  function orderedMoves(st, moves) {
    const out = [];
    let m = moves;
    while (m) {
      const mv = m & -m;
      out.push({ mv, score: C4.sortMoveScore(st.all, st.active, mv), prio: C4.priorityClass(mv) });
      m ^= mv;
    }
    out.sort((a, b) => b.score - a.score || a.prio - b.prio);
    return out;
  }

  Solver.prototype.negamax = function (st, alpha, beta) {
    this.nodes++;
    const mL = st.movesLeft;
    if (canWin(st)) return Math.floor((mL + 1) / 2);
    if (mL === 0) return 0;
    const moves = C4.generateNonLosingMoves(st.all, st.active);
    if (!moves) return -Math.floor(mL / 2);

    // The free bounds the position itself provides (part 7).
    const lo = -Math.floor(mL / 2);
    const hi = Math.floor((mL - 1) / 2);
    if (alpha < lo) {
      alpha = lo;
      if (alpha >= beta) return alpha;
    }
    if (beta > hi) {
      beta = hi;
      if (alpha >= beta) return beta;
    }

    const key = st.all + st.active;
    const e = this.tt.get(key);
    if (e) {
      if (e.flag === EXACT) return e.value;
      if (e.flag === LOWER && e.value > alpha) alpha = e.value;
      else if (e.flag === UPPER && e.value < beta) beta = e.value;
      if (alpha >= beta) return e.value;
    }

    const alphaOrig = alpha;
    for (const { mv } of orderedMoves(st, moves)) {
      const v = -this.negamax(C4.play(st, mv), -beta, -alpha);
      if (v > alpha) alpha = v;
      if (alpha >= beta) {
        this.tt.set(key, { flag: LOWER, value: alpha });
        return alpha;
      }
    }
    this.tt.set(key, { flag: alpha === alphaOrig ? UPPER : EXACT, value: alpha });
    return alpha;
  };

  /** Wide-window driver: one exact search. */
  function driveNegamax(st) {
    const s = new Solver();
    const g = s.negamax(st, -22, 22);
    return { score: g, nodes: s.nodes, probes: [] };
  }

  /** MTD(f): repeated null-window probes moving an upper and a lower bound. */
  function driveMtdf(st, firstGuess) {
    const s = new Solver();
    let g = firstGuess || 0;
    let upper = Infinity;
    let lower = -Infinity;
    const probes = [];
    while (lower < upper) {
      const beta = Math.max(g, lower + 1);
      const before = s.nodes;
      g = s.negamax(st, beta - 1, beta);
      if (g < beta) upper = g;
      else lower = g;
      probes.push({ window: beta, result: g, lower, upper, nodes: s.nodes - before });
    }
    return { score: g, nodes: s.nodes, probes };
  }

  /** Binary-search driver over the free bounds, probes biased towards zero. */
  function driveNullWindow(st) {
    const s = new Solver();
    let min = -Math.floor(st.movesLeft / 2);
    let max = Math.floor((st.movesLeft + 1) / 2);
    const probes = [];
    while (min < max) {
      let mid = min + Math.floor((max - min) / 2);
      if (mid <= 0 && Math.floor(min / 2) < mid) mid = Math.floor(min / 2);
      else if (mid >= 0 && Math.floor(max / 2) > mid) mid = Math.floor(max / 2);
      const before = s.nodes;
      const r = s.negamax(st, mid, mid + 1);
      if (r <= mid) max = r;
      else min = r;
      probes.push({ window: mid, result: r, lower: min, upper: max, nodes: s.nodes - before });
    }
    return { score: min, nodes: s.nodes, probes };
  }

  /** BitBully::scoreToMovesLeft() -- plies until the game ends, from the score. */
  function scoreToMovesLeft(score, st) {
    if (score === 0) return st.movesLeft;
    const p = (st.movesLeft + 1) % 2;
    const sgn = score < 0 ? 1 : 0;
    const abs = score < 0 ? -score : score;
    return st.movesLeft - (2 * (abs - 1) + (sgn ^ p));
  }

  /** A random legal position with n stones, no win on the board and no
   *  immediate win available (Board::random_board(n, forbid_direct_win)). */
  function randomBoard(nStones, rand) {
    const rnd = rand || Math.random;
    for (let attempt = 0; attempt < 1000; attempt++) {
      let st = { all: 0n, active: 0n, movesLeft: 42 };
      const path = [];
      let ok = true;
      while (path.length < nStones) {
        // Candidate moves that do not complete four in a row.
        const wins = C4.winningPositions(st.active, true);
        let m = C4.legalMovesMask(st.all) & ~wins;
        const cols = [];
        while (m) {
          const mv = m & -m;
          cols.push(mv);
          m ^= mv;
        }
        if (!cols.length) {
          ok = false;
          break;
        }
        const mv = cols[Math.floor(rnd() * cols.length)];
        st = C4.play(st, mv);
        path.push(C4.colOf(mv));
      }
      if (ok && !canWin(st)) return { st, path };
    }
    return null;
  }

  global.C4Search = { Solver, canWin, driveNegamax, driveMtdf, driveNullWindow, scoreToMovesLeft, randomBoard };

  /* ---- the widget itself ---------------------------------------------- */

  if (typeof document === "undefined") return;

  function build(root) {
    let position = null; // {st, path}

    root.innerHTML = `
      <div class="c4bb-controls">
        <label class="c4bb-hint">stones:
          <select data-opt="stones">
            <option>16</option><option selected>18</option><option>20</option><option>22</option>
          </select>
        </label>
        <button type="button" data-act="new">New random position</button>
        <button type="button" data-act="solve">Solve with all three drivers</button>
        <span class="c4bb-hint" data-role="status"></span>
      </div>
      <div class="c4bb-grid" role="group" aria-label="Connect-4 board"></div>
      <div class="c4bb-legend">
        <span><i class="c4bb-sw c4bb-yellow"></i>player to move</span>
        <span><i class="c4bb-sw c4bb-red"></i>opponent</span>
      </div>
      <div data-role="verdict"></div>
      <table class="c4bb-table" data-role="drivers" hidden>
        <thead><tr><th>driver</th><th>score</th><th>nodes</th><th>probes</th></tr></thead>
        <tbody></tbody>
      </table>
      <div data-role="probes"></div>`;

    const grid = root.querySelector(".c4bb-grid");
    const statusEl = root.querySelector('[data-role="status"]');
    const verdictEl = root.querySelector('[data-role="verdict"]');
    const driversTable = root.querySelector('[data-role="drivers"]');
    const probesEl = root.querySelector('[data-role="probes"]');
    const cells = [];

    for (let r = C4.N_ROWS - 1; r >= 0; r--) {
      for (let c = 0; c < C4.N_COLUMNS; c++) {
        const cell = document.createElement("span");
        cell.className = "c4bb-cell";
        cell.dataset.col = c;
        cell.dataset.row = r;
        grid.appendChild(cell);
        cells.push(cell);
      }
    }

    function renderBoard() {
      const st = position.st;
      const opponent = (st.active ^ st.all) & C4.MASK64;
      for (const cell of cells) {
        const b = C4.bitOf(+cell.dataset.col, +cell.dataset.row);
        cell.className = "c4bb-cell";
        if (st.active & b) cell.classList.add("c4bb-yellow");
        else if (opponent & b) cell.classList.add("c4bb-red");
      }
    }

    function newPosition() {
      const n = +root.querySelector('[data-opt="stones"]').value;
      position = randomBoard(n);
      renderBoard();
      verdictEl.innerHTML = "";
      driversTable.hidden = true;
      probesEl.innerHTML = "";
      statusEl.textContent = "";
    }

    /** One probe log as a small bounds chart: a bar per probe, the surviving
     *  window drawn on a fixed score axis. */
    function probeChart(title, probes, range) {
      if (!probes.length) return "";
      const span = range.hi - range.lo || 1;
      const pos = (v) => ((v - range.lo) / span) * 100;
      const rows = probes
        .map((p, i) => {
          const lo = Math.max(p.lower, range.lo);
          const hi = Math.min(p.upper, range.hi);
          return `<div class="c4bb-probe">
            <span class="c4bb-probe-label">probe ${i + 1}: test &beta; = ${p.window} &rarr; ${p.result}</span>
            <span class="c4bb-probe-track">
              <span class="c4bb-probe-window" style="left:${pos(lo)}%;width:${Math.max(pos(hi) - pos(lo), 1)}%"></span>
              <span class="c4bb-probe-mark" style="left:${pos(p.window)}%"></span>
            </span>
            <span class="c4bb-probe-nodes">${p.nodes.toLocaleString()} nodes</span>
          </div>`;
        })
        .join("");
      return `<p class="c4bb-probe-title">${title} &mdash; the surviving window after each null-window probe:</p>${rows}`;
    }

    function solve() {
      if (!position) return;
      statusEl.textContent = "solving…";
      // Let the status paint before the (synchronous) search starts.
      setTimeout(() => {
        const st = position.st;
        const t0 = performance.now();
        const mtdf = C4Search.driveMtdf(st, 0);
        const nega = C4Search.driveNegamax(st);
        const nullw = C4Search.driveNullWindow(st);
        const ms = performance.now() - t0;

        const agree = mtdf.score === nega.score && nega.score === nullw.score;
        const score = mtdf.score;
        const end = C4Search.scoreToMovesLeft(score, st);
        const outcome = score > 0 ? "the player to move wins" : score < 0 ? "the player to move loses" : "the game is a draw";

        verdictEl.innerHTML = agree
          ? `<p class="c4bb-verdict">All three drivers return <strong>${score >= 0 ? "+" + score : score}</strong>:
             ${outcome}${score !== 0 ? `, and under perfect play the game ends after <strong>${end}</strong> more plies` : ""}.
             Total wall-clock in this browser: ${ms.toFixed(0)} ms.</p>`
          : `<p class="c4bb-verdict c4bb-win">The drivers disagree &mdash; that would be a bug.</p>`;

        const tb = driversTable.querySelector("tbody");
        tb.innerHTML = [
          ["mtdf(b, 0)", mtdf],
          ["negamax(b, &minus;22, 22)", nega],
          ["nullWindow(b)", nullw],
        ]
          .map(
            ([name, r]) =>
              `<tr><td><code>${name}</code></td><td class="c4bb-num">${r.score}</td>
               <td class="c4bb-num">${r.nodes.toLocaleString()}</td>
               <td class="c4bb-num">${r.probes.length || "&mdash;"}</td></tr>`
          )
          .join("");
        driversTable.hidden = false;

        const range = { lo: -Math.floor(st.movesLeft / 2), hi: Math.floor((st.movesLeft + 1) / 2) };
        probesEl.innerHTML = probeChart("MTD(f)", mtdf.probes, range) + probeChart("nullWindow()", nullw.probes, range);
        statusEl.textContent = "";
      }, 20);
    }

    root.querySelector('[data-act="new"]').addEventListener("click", newPosition);
    root.querySelector('[data-act="solve"]').addEventListener("click", solve);
    newPosition();
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-c4-search]").forEach(build);
  });
})(typeof window !== "undefined" ? window : globalThis);
