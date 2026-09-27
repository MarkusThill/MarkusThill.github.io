/**
 * The learned Connect-4 agent of the reinforcement-learning series, in the browser.
 *
 * A transcription of techdays26's n-tuple agent on top of `connect4-core.js` (same 9-bits-per-column
 * layout, BigInt bit boards):
 *
 *   BoardBatch.table_positions()           ->  cellCodes(), tableIndex()
 *   NTupleNetwork.forward()                ->  value()
 *   TDConnect4AgentTorch.score_all_moves() ->  scoreAllMoves()
 *   TDConnect4AgentTorch.best_move()       ->  bestMove()   (ties: column nearest to the centre)
 *
 * The weights file stores only the realisable table entries of every n-tuple, in the rank order of
 * `tools/connect4_rl/realisable_states.py`; `Ranking` below computes the same rank from a table index.
 *
 * Verified against the Python agent by `tools/connect4_rl/check_ntuple_widget.mjs`.
 */
(function (global) {
  "use strict";

  const C4 = global.C4;
  const N_ROWS = 6;
  const OFF = 9;
  const EMPTY = 0,
    YELLOW = 1,
    RED = 2,
    REACHABLE = 3;

  /**
   * Mixed-radix rank of the realisable states of one tuple: one digit per column, the position of the
   * column's partial index among that column's realisable partials (sorted ascending).
   */
  function buildRanking(bits) {
    const cells = bits.map((b) => [Math.floor(b / OFF), b % OFF]);
    const cols = [...new Set(cells.map(([c]) => c))].sort((a, b) => a - b);
    const columns = cols.map((col) => {
      const positions = cells.map(([c], i) => (c === col ? i : -1)).filter((i) => i >= 0);
      const rows = positions.map((i) => cells[i][1]);
      const partials = new Set();
      for (let height = 0; height <= N_ROWS; height++) {
        const filled = rows.map((r, k) => (r < height ? k : -1)).filter((k) => k >= 0);
        for (let colours = 0; colours < 1 << filled.length; colours++) {
          const code = rows.map((r) => (r === height ? REACHABLE : EMPTY));
          filled.forEach((k, j) => (code[k] = (colours >> j) & 1 ? RED : YELLOW));
          partials.add(code.reduce((acc, v, k) => acc + v * 4 ** positions[k], 0));
        }
      }
      const sorted = [...partials].sort((a, b) => a - b);
      return { positions, digit: new Map(sorted.map((p, d) => [p, d])), size: sorted.length };
    });
    const strides = new Array(columns.length);
    let stride = 1;
    for (let k = columns.length - 1; k >= 0; k--) {
      strides[k] = stride;
      stride *= columns[k].size;
    }
    return { columns, strides, count: stride };
  }

  function rank(ranking, index) {
    let r = 0;
    ranking.columns.forEach((col, k) => {
      let partial = 0;
      for (const p of col.positions) partial += (Math.floor(index / 4 ** p) % 4) * 4 ** p;
      const d = col.digit.get(partial);
      if (d === undefined) throw new Error("table index is not realisable");
      r += d * ranking.strides[k];
    });
    return r;
  }

  /** Cell codes of all 63 bit positions, as in BoardBatch.table_positions(). */
  function cellCodes(state) {
    const reachable = C4.legalMovesMask(state.all);
    const activeIsYellow = state.movesLeft % 2 === 0;
    const codes = new Uint8Array(7 * OFF);
    for (let c = 0; c < 7; c++)
      for (let r = 0; r < N_ROWS; r++) {
        const bit = C4.bitOf(c, r);
        const occupied = (state.all & bit) !== 0n;
        const isActive = (state.active & bit) !== 0n;
        let code = EMPTY;
        if (occupied) code = (activeIsYellow ? isActive : !isActive) ? YELLOW : RED;
        else if (reachable & bit) code = REACHABLE;
        codes[c * OFF + r] = code;
      }
    return codes;
  }

  function tableIndex(codes, bits) {
    let index = 0;
    bits.forEach((b, i) => (index += codes[b] * 4 ** i));
    return index;
  }

  /** Parse an (already decompressed) weights file. */
  function parseWeights(buffer) {
    const bytes = new Uint8Array(buffer);
    const magic = String.fromCharCode(...bytes.slice(0, 4));
    if (magic !== "C4NT") throw new Error("not an n-tuple weights file");
    const view = new DataView(buffer);
    const headerLength = view.getUint32(4, true);
    const header = JSON.parse(new TextDecoder().decode(bytes.slice(8, 8 + headerLength)));
    const tuples = header.tuples;
    const mirrored = tuples.map((t) => t.map((b) => (6 - Math.floor(b / OFF)) * OFF + (b % OFF)));
    const rankings = tuples.map(buildRanking);
    const total = 2 * header.counts.reduce((a, b) => a + b, 0);
    const values = new Float32Array(total);
    let offset = 8 + headerLength;
    if (header.dtype === "int8") {
      const raw = new Int8Array(buffer, offset, total);
      let k = 0;
      for (let t = 0; t < 2 * tuples.length; t++) {
        const n = header.counts[t % tuples.length];
        for (let i = 0; i < n; i++, k++) values[k] = raw[k] * header.scales[t];
      }
    } else if (header.dtype === "float16") {
      for (let k = 0; k < total; k++) values[k] = halfToFloat(view.getUint16(offset + 2 * k, true));
    } else {
      for (let k = 0; k < total; k++) values[k] = view.getFloat32(offset + 4 * k, true);
    }
    const starts = [];
    let start = 0;
    for (let t = 0; t < 2 * tuples.length; t++) {
      starts.push(start);
      start += header.counts[t % tuples.length];
    }
    return { header, tuples, mirrored, rankings, values, starts };
  }

  function halfToFloat(h) {
    const sign = h & 0x8000 ? -1 : 1;
    const exp = (h >> 10) & 0x1f;
    const frac = h & 0x3ff;
    if (exp === 0) return sign * 2 ** -14 * (frac / 1024);
    if (exp === 31) return frac ? NaN : sign * Infinity;
    return sign * 2 ** (exp - 15) * (1 + frac / 1024);
  }

  /** Network value of a position from Yellow's point of view, as in NTupleNetwork.forward(). */
  function value(net, state) {
    const codes = cellCodes(state);
    const player = state.movesLeft % 2 !== 0 ? 1 : 0; // table set of the player to move
    const M = net.tuples.length;
    let sum = 0;
    for (let m = 0; m < M; m++) {
      const base = net.starts[player * M + m];
      const r = net.rankings[m];
      sum += net.values[base + rank(r, tableIndex(codes, net.tuples[m]))];
      sum += net.values[base + rank(r, tableIndex(codes, net.mirrored[m]))];
    }
    return Math.tanh(sum);
  }

  function columnMask(col) {
    let m = 0n;
    for (let r = 0; r < N_ROWS; r++) m |= C4.bitOf(col, r);
    return m;
  }

  /** Integer score per legal column, as in TDConnect4AgentTorch.score_all_moves(). */
  function scoreAllMoves(net, state) {
    const playerToMove = state.movesLeft % 2 === 0 ? 1 : 2;
    const legal = C4.legalMovesMask(state.all);
    const scores = {};
    const values = {};
    for (let col = 0; col < 7; col++) {
      const mv = legal & columnMask(col);
      if (!mv) continue;
      const after = C4.play(state, mv);
      if (C4.hasWin(after.all, after.active)) scores[col] = 100;
      else if (C4.winningPositions(after.active, true) & C4.legalMovesMask(after.all)) scores[col] = -100;
      else {
        let s = value(net, after);
        values[col] = s;
        if (playerToMove === 2) s = -s;
        scores[col] = Math.trunc(s * 100);
      }
    }
    return { scores, values };
  }

  /** The agent's move: highest score, ties broken towards the centre column. */
  function bestMove(net, state) {
    const { scores } = scoreAllMoves(net, state);
    const cols = Object.keys(scores).map(Number);
    if (!cols.length) throw new Error("no legal moves");
    const best = Math.max(...cols.map((c) => scores[c]));
    return cols.filter((c) => scores[c] === best).sort((a, b) => Math.abs(a - 3) - Math.abs(b - 3) || a - b)[0];
  }

  /** Fetch and decompress a gzip-compressed weights file. */
  async function loadWeights(url) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`could not load ${url}: ${response.status}`);
    const stream = response.body.pipeThrough(new DecompressionStream("gzip"));
    return parseWeights(await new Response(stream).arrayBuffer());
  }

  global.C4NTuple = { buildRanking, rank, cellCodes, tableIndex, parseWeights, value, scoreAllMoves, bestMove, loadWeights };
})(typeof window !== "undefined" ? window : globalThis);
