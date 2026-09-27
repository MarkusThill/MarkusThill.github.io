/**
 * Play Connect-4 against the learned n-tuple agent of the reinforcement-learning series.
 *
 * The agent itself lives in `connect4-ntuple.js` (verified move for move against the Python agent);
 * this file only draws the board and runs the game. The weights are loaded on request, since the
 * file has several megabytes.
 *
 * Usage in a post:
 *   <div class="c4bb" data-c4-play data-weights="…/agent.bin.gz" data-size="7.9 MB"></div>
 *   <script src="…/connect4-core.js"></script>
 *   <script src="…/connect4-ntuple.js"></script>
 *   <script src="…/connect4-play.js"></script>
 */
(function () {
  "use strict";

  if (typeof document === "undefined") return;
  const C4 = window.C4;
  const NT = window.C4NTuple;

  /** Weights as fetched: decompress unless the server already did (magic bytes decide). */
  async function fetchWeights(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`could not load the weights (${response.status})`);
    const bytes = new Uint8Array(await response.arrayBuffer());
    if (bytes[0] === 0x1f && bytes[1] === 0x8b) {
      const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
      return NT.parseWeights(await new Response(stream).arrayBuffer());
    }
    return NT.parseWeights(bytes.buffer);
  }

  function columnMask(col) {
    let m = 0n;
    for (let r = 0; r < C4.N_ROWS; r++) m |= C4.bitOf(col, r);
    return m;
  }

  function build(root) {
    const url = root.dataset.weights;
    const size = root.dataset.size || "";
    let net = null;
    let state = null;
    let human = 1; // 1 = yellow (moves first), 2 = red
    let lastMove = null;
    let over = false;

    root.innerHTML = `
      <div class="c4bb-controls">
        <button type="button" data-act="load">Load the agent${size ? ` (${size})` : ""}</button>
        <label class="c4bb-hint" hidden>you play
          <select data-opt="side">
            <option value="1" selected>yellow (first move)</option>
            <option value="2">red (second move)</option>
          </select>
        </label>
        <button type="button" data-act="new" hidden>New game</button>
        <span class="c4bb-hint" data-role="status" aria-live="polite"></span>
      </div>
      <div class="c4bb-grid c4play-grid" role="group" aria-label="Connect-4 board"></div>
      <div class="c4bb-grid c4play-scores" aria-label="The agent's scores of its moves"></div>
      <div class="c4bb-legend">
        <span><i class="c4bb-sw c4play-yellow"></i>yellow</span>
        <span><i class="c4bb-sw c4play-red"></i>red</span>
        <span>Numbers below the board: the agent's scores of its moves in its last turn
          (network value × 100 from its own point of view; ±100 for an immediate win or loss).</span>
      </div>`;

    const grid = root.querySelector(".c4play-grid");
    const scoresEl = root.querySelector(".c4play-scores");
    const statusEl = root.querySelector('[data-role="status"]');
    const sideSel = root.querySelector('[data-opt="side"]');
    const newBtn = root.querySelector('[data-act="new"]');
    const loadBtn = root.querySelector('[data-act="load"]');

    const cells = [];
    for (let row = C4.N_ROWS - 1; row >= 0; row--)
      for (let col = 0; col < C4.N_COLUMNS; col++) {
        const cell = document.createElement("button");
        cell.type = "button";
        cell.className = "c4bb-cell";
        cell.dataset.col = col;
        cell.setAttribute("aria-label", `column ${col + 1}`);
        cell.addEventListener("click", () => humanMove(col));
        grid.appendChild(cell);
        cells.push({ cell, col, row });
      }
    const scoreCells = [];
    for (let col = 0; col < C4.N_COLUMNS; col++) {
      const s = document.createElement("span");
      s.className = "c4play-score";
      scoresEl.appendChild(s);
      scoreCells.push(s);
    }

    const toMove = () => (state.movesLeft % 2 === 0 ? 1 : 2);
    const status = (text) => (statusEl.textContent = text);

    function render() {
      const yellowToMove = state.movesLeft % 2 === 0;
      for (const { cell, col, row } of cells) {
        const bit = C4.bitOf(col, row);
        let cls = "c4bb-cell";
        if (state.all & bit) {
          const isActive = (state.active & bit) !== 0n;
          cls += (yellowToMove ? isActive : !isActive) ? " c4play-yellow" : " c4play-red";
          if (bit === lastMove) cls += " c4play-last";
        }
        cell.className = cls;
        cell.disabled = !net || over || toMove() !== human || !(C4.legalMovesMask(state.all) & columnMask(col));
      }
    }

    function finished() {
      if (C4.hasWin(state.all, state.active)) {
        over = true;
        status(toMove() === human ? "The agent wins." : "You win!");
      } else if (state.movesLeft === 0) {
        over = true;
        status("Draw.");
      }
      return over;
    }

    function play(col) {
      const mv = C4.legalMovesMask(state.all) & columnMask(col);
      state = C4.play(state, mv);
      lastMove = mv;
    }

    function agentMove() {
      status("The agent is thinking …");
      render();
      setTimeout(() => {
        const { scores } = NT.scoreAllMoves(net, state);
        const col = NT.bestMove(net, state);
        scoreCells.forEach((s, c) => {
          const v = scores[c];
          s.textContent = v === undefined ? "" : v > 0 ? `+${v}` : `${v}`;
          s.classList.toggle("c4play-chosen", c === col);
        });
        play(col);
        if (!finished()) status("Your move.");
        render();
      }, 30);
    }

    function humanMove(col) {
      if (!net || over || toMove() !== human) return;
      if (!(C4.legalMovesMask(state.all) & columnMask(col))) return;
      play(col);
      render();
      if (!finished()) agentMove();
      else render();
    }

    function newGame() {
      state = { all: 0n, active: 0n, movesLeft: 42 };
      human = Number(sideSel.value);
      lastMove = null;
      over = false;
      scoreCells.forEach((s) => (s.textContent = ""));
      render();
      if (toMove() === human) status("Your move.");
      else agentMove();
    }

    loadBtn.addEventListener("click", async () => {
      loadBtn.disabled = true;
      status("Loading the agent …");
      try {
        net = await fetchWeights(url);
      } catch (err) {
        status(`${err.message}`);
        loadBtn.disabled = false;
        return;
      }
      loadBtn.hidden = true;
      sideSel.closest("label").hidden = false;
      newBtn.hidden = false;
      newGame();
    });
    newBtn.addEventListener("click", newGame);
    sideSel.addEventListener("change", newGame);

    state = { all: 0n, active: 0n, movesLeft: 42 };
    render();
    status("The agent is not loaded yet.");
  }

  function init() {
    document.querySelectorAll("[data-c4-play]").forEach(build);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
