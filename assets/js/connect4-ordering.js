/**
 * Interactive move-ordering explorer for part 4 of the Connect-4 series.
 *
 * For the current position it shows the legal moves ranked exactly the way
 * `Board::sortMoves()` and `MoveList::pop()` would rank them, together with the
 * moves that `generateNonLosingMoves()` removes and the ones that
 * `doubleThreat()` recognises as an immediate forced win.
 *
 * All board arithmetic lives in `connect4-core.js`.
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
        <button type="button" data-act="forced">Forced reply</button>
        <button type="button" data-act="double">Double threat</button>
        <button type="button" data-act="lost">Already lost</button>
        <span class="c4bb-hint">click a column to drop a token</span>
      </div>
      <div class="c4bb-grid" role="group" aria-label="Connect-4 board"></div>
      <div class="c4bb-toggles">
        <label><input type="checkbox" data-opt="odd" checked>highlight odd rows (rows 3 and 5)</label>
        <label><input type="checkbox" data-opt="threats" checked>mark opponent threats</label>
      </div>
      <div class="c4bb-legend">
        <span><i class="c4bb-sw c4bb-yellow"></i>player to move</span>
        <span><i class="c4bb-sw c4bb-red"></i>opponent</span>
        <span><i class="c4bb-sw c4bb-legal"></i>candidate move</span>
        <span><i class="c4bb-sw c4bb-threat"></i>own winning cell</span>
      </div>
      <table class="c4bb-table">
        <thead><tr>
          <th>rank</th><th>column</th><th>new threats</th><th>centre class</th><th></th>
        </tr></thead>
        <tbody></tbody>
      </table>
      <dl class="c4bb-readout"></dl>`;

    const grid = root.querySelector(".c4bb-grid");
    const tbody = root.querySelector("tbody");
    const readout = root.querySelector(".c4bb-readout");
    const opts = { odd: true, threats: true };
    const cells = [];

    root.querySelectorAll("[data-opt]").forEach((el) =>
      el.addEventListener("change", () => {
        opts[el.dataset.opt] = el.checked;
        render();
      })
    );

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
    // Exactly one immediate threat of the opponent: the reply is forced and the
    // branching factor at this node drops from seven to one.
    root.querySelector('[data-act="forced"]').addEventListener("click", () => {
      reset();
      [4, 0, 5, 2, 3, 5, 2].forEach(play);
    });
    // A move with two of the player's own winning cells stacked above it.
    root.querySelector('[data-act="double"]').addEventListener("click", () => {
      reset();
      [5, 4, 5, 2, 2, 2, 2, 0, 4, 6].forEach(play);
    });
    // Two immediate threats of the opponent, only one of which can be blocked.
    root.querySelector('[data-act="lost"]').addEventListener("click", () => {
      reset();
      [3, 0, 4, 1, 5].forEach(play);
    });

    function render() {
      const legal = C4.legalMovesMask(state.all);
      const nonLosing = C4.generateNonLosingMoves(state.all, state.active);
      const dbl = C4.doubleThreat(state.all, state.active, nonLosing);
      const opponent = (state.active ^ state.all) & C4.MASK64;
      const oppThreats = C4.winningPositions(opponent, true) & ~state.all & C4.MASK64;
      const ownThreats = C4.winningPositions(state.active, true) & ~state.all & C4.MASK64;
      const won = C4.hasWin(state.all, state.active);
      const directThreats = oppThreats & legal;

      for (const cell of cells) {
        const b = C4.bitOf(+cell.dataset.col, +cell.dataset.row);
        cell.className = "c4bb-cell";
        if (opts.odd && C4.ODD_ROWS & b) cell.classList.add("c4bb-oddrow");
        if (state.active & b) cell.classList.add("c4bb-yellow");
        else if (opponent & b) cell.classList.add("c4bb-red");
        else if (ownThreats & b) cell.classList.add("c4bb-threat");
        else if (opts.threats && oppThreats & b) cell.classList.add("c4bb-oppthreat");
        else if (legal & b) cell.classList.add("c4bb-legal");
        cell.textContent = "";
      }

      // Rank the legal moves the way sortMoves() + MoveList would.
      const rows = [];
      let m = legal;
      while (m) {
        const mv = m & -m;
        rows.push({
          mv,
          col: C4.colOf(mv),
          score: C4.sortMoveScore(state.all, state.active, mv),
          prio: C4.priorityClass(mv),
          dropped: !(nonLosing & mv),
          winning: !!(dbl & mv),
          forced: !!(directThreats && nonLosing === mv),
        });
        m ^= mv;
      }
      rows.sort((a, b) => b.score - a.score || a.prio - b.prio);

      tbody.innerHTML =
        rows
          .map((r, i) => {
            const tags =
              (r.winning ? '<span class="c4bb-tag c4bb-tag-win">double threat &rarr; won</span>' : "") +
              (r.forced ? '<span class="c4bb-tag c4bb-tag-forced">forced reply</span>' : "") +
              (r.dropped ? '<span class="c4bb-tag c4bb-tag-lose">never generated &mdash; loses</span>' : "");
            const cls = (r.dropped ? "c4bb-dropped" : "") + (i === 0 && !r.dropped ? " c4bb-best" : "");
            return `<tr class="${cls.trim()}"><td class="c4bb-num">${r.dropped ? "&mdash;" : i + 1}</td>
              <td class="c4bb-num">${r.col}</td><td class="c4bb-num">${r.score}</td>
              <td class="c4bb-num">${r.prio + 1}</td><td>${tags}</td></tr>`;
          })
          .join("") || '<tr><td colspan="5">no legal moves</td></tr>';

      const row = (k, v, cls) => `<dt>${k}</dt><dd class="${cls || ""}">${v}</dd>`;
      const nLegal = C4.popcount(legal);
      const nKept = C4.popcount(nonLosing);
      readout.innerHTML =
        row("legalMovesMask()", `<code>${nLegal}</code> move${nLegal === 1 ? "" : "s"}`) +
        row(
          "generateNonLosingMoves()",
          nonLosing === 0n
            ? "<strong>empty</strong> &mdash; every reply loses, the position is lost"
            : `<code>${nKept}</code> of <code>${nLegal}</code> kept`,
          nonLosing === 0n ? "c4bb-win" : ""
        ) +
        row("doubleThreat()", dbl ? "<strong>forced win</strong> &mdash; no subtree has to be searched" : "<code>0</code>", dbl ? "c4bb-win" : "") +
        row(
          "odd / even threats",
          `<code>${C4.popcount(ownThreats & C4.ODD_ROWS)}</code> odd, ` +
            `<code>${C4.popcount(ownThreats & C4.EVEN_ROWS)}</code> even (player to move)`
        ) +
        (won ? row("hasWin()", "<strong>true</strong> &mdash; the game is over", "c4bb-win") : "");
    }

    render();
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-c4-ordering]").forEach(build);
  });
})();
