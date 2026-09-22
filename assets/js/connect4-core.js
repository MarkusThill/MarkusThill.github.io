/**
 * Shared Connect-4 bit board operations for the interactive widgets of the
 * "Building Intelligent Agents for Connect-4" series.
 *
 * Every function here is a transcription of the corresponding member of
 * BitBully's `src/Board.h`, using the same 9-bits-per-column layout:
 *
 *   legalMovesMask()         ->  (all + BB_BOTTOM_ROW) & BB_ALL_LEGAL_TOKENS
 *   playMoveFastBB()         ->  active ^= all;  all ^= mv;  movesLeft--
 *   uid()                    ->  active + all
 *   hash()                   ->  Mix13 avalanche finalizer over uid()
 *   winningPositions(x, v)   ->  shift-and-mask over k in {1, 8, 9, 10}
 *   hasWin()                 ->  four shift pairs on the player who just moved
 *   generateNonLosingMoves() ->  drop moves under an opponent threat
 *   doubleThreat(moves)      ->  two own threats stacked above the move
 *   nextMove(moves)          ->  centre-first priority classes
 *   toHuffman()              ->  the opening-book encoding
 *
 * BigInt is required rather than merely convenient: the layout places bits at
 * indices up to 62, and an ordinary JavaScript number is a double-precision
 * float which loses integer precision above 2^53.
 *
 * Verified against the C++ engine by `tools/connect4/check_widget.mjs`.
 */
(function (global) {
  "use strict";

  const N_COLUMNS = 7;
  const N_ROWS = 6;
  const OFF = 9n; // COLUMN_BIT_OFFSET
  const MASK64 = (1n << 64n) - 1n;

  let BB_BOTTOM_ROW = 0n;
  for (let c = 0; c < N_COLUMNS; c++) BB_BOTTOM_ROW |= 1n << (BigInt(c) * OFF);

  let BB_ALL_LEGAL = 0n;
  for (let c = 0; c < N_COLUMNS; c++) for (let r = 0; r < N_ROWS; r++) BB_ALL_LEGAL |= 1n << (BigInt(c) * OFF + BigInt(r));

  // Rows are counted from 0 at the bottom; "odd rows" in the sense of part 4
  // (rows 3 and 5 when counting from 1) are rows 2 and 4 here.
  let ODD_ROWS = 0n;
  let EVEN_ROWS = 0n;
  for (let c = 0; c < N_COLUMNS; c++)
    for (let r = 0; r < N_ROWS; r++) {
      const b = 1n << (BigInt(c) * OFF + BigInt(r));
      if (r === 2 || r === 4) ODD_ROWS |= b;
      else EVEN_ROWS |= b;
    }

  const mask = (bits) => bits.reduce((a, b) => a | (1n << BigInt(b)), 0n);
  const PRIORITY = [
    mask([29, 30]),
    mask([31, 21, 20, 28, 38, 39]),
    mask([40, 32, 22, 19, 27, 37]),
    mask([47, 48, 11, 12]),
    mask([49, 41, 23, 13, 10, 18, 36, 46]),
    mask([45, 50, 14, 9]),
  ];

  const bitOf = (col, row) => 1n << (BigInt(col) * OFF + BigInt(row));
  const colOf = (mv) => Number(BigInt(mv.toString(2).length - 1) / OFF);
  const popcount = (v) => {
    let n = 0;
    while (v) {
      v &= v - 1n;
      n++;
    }
    return n;
  };

  function legalMovesMask(all) {
    return (all + BB_BOTTOM_ROW) & BB_ALL_LEGAL;
  }

  function winningPositions(x, verticals) {
    let wins = verticals ? (x << 1n) & (x << 2n) & (x << 3n) : 0n;
    for (const b of [OFF - 1n, OFF, OFF + 1n]) {
      let tmp = (x << b) & (x << (2n * b));
      wins |= tmp & (x << (3n * b));
      wins |= tmp & (x >> b);
      tmp = (x >> b) & (x >> (2n * b));
      wins |= tmp & (x << b);
      wins |= tmp & (x >> (3n * b));
    }
    return wins & BB_ALL_LEGAL;
  }

  function hasWin(all, active) {
    const y = (active ^ all) & MASK64; // the player who just moved
    for (const k of [1n, OFF, OFF - 1n, OFF + 1n]) {
      const x = y & (y >> k);
      if (x & (x >> (2n * k))) return true;
    }
    return false;
  }

  function generateNonLosingMoves(all, active) {
    let moves = legalMovesMask(all);
    const threats = winningPositions((active ^ all) & MASK64, true);
    const directThreats = threats & moves;
    if (directThreats) {
      // more than one immediate threat cannot be neutralised
      moves = directThreats & (directThreats - 1n) ? 0n : directThreats;
    }
    return moves & ~(threats >> 1n) & MASK64; // never move under an opponent threat
  }

  function doubleThreat(all, active, moves) {
    const ownThreats = winningPositions(active, false);
    const otherThreats = winningPositions((active ^ all) & MASK64, true);
    return moves & (ownThreats >> 1n) & (ownThreats >> 2n) & ~(otherThreats >> 1n) & MASK64;
  }

  /** Priority class (0 = best) of a single-bit move mask, mirroring nextMove(). */
  function priorityClass(mv) {
    for (let i = 0; i < PRIORITY.length; i++) if (mv & PRIORITY[i]) return i;
    return PRIORITY.length;
  }

  /** Score of one move as computed by Board::sortMoves(). */
  function sortMoveScore(all, active, mv) {
    const ownThreats = winningPositions(active, false);
    const threats = winningPositions(active ^ mv, true) & ~(all ^ mv) & MASK64;
    let n = popcount(threats);
    if (ownThreats & (mv << 1n)) n--; // avoid moving under one's own threat
    return n;
  }

  /** Play a move mask, returning the new state (the original is not modified). */
  function play(state, mv) {
    return {
      all: state.all ^ mv,
      active: state.active ^ state.all,
      movesLeft: state.movesLeft - 1,
    };
  }

  /** Board::toHuffman(), with the intermediate steps kept for visualisation. */
  function toHuffman(all, active) {
    const steps = [];
    let huff = 0n;
    let bits = "";
    for (let c = 0; c < N_COLUMNS; c++) {
      for (let r = 0; r < N_ROWS; r++) {
        const b = bitOf(c, r);
        if (!(all & b)) break;
        const code = active & b ? "10" : "11";
        huff = (huff << 2n) | (active & b ? 2n : 3n);
        bits += code;
        steps.push({ col: c, row: r, code, kind: active & b ? "active" : "other" });
      }
      huff <<= 1n; // a single 0 bit terminates the column
      bits += "0";
      steps.push({ col: c, row: null, code: "0", kind: "sep" });
    }
    return { value: huff << 1n, bits: bits + "0", steps };
  }

  /** David Stafford's Mix13 finalizer -- the static Board::hash(x). */
  function hash64(x) {
    x &= MASK64;
    x = ((x ^ (x >> 30n)) * 0xbf58476d1ce4e5b9n) & MASK64;
    x = ((x ^ (x >> 27n)) * 0x94d049bb133111ebn) & MASK64;
    x = x ^ (x >> 31n);
    return x & MASK64;
  }

  /** Board::hash() -- hash(hash(active) ^ (hash(all) << 1)). */
  function boardHash(all, active) {
    return hash64(hash64(active) ^ ((hash64(all) << 1n) & MASK64));
  }

  const fmtHex = (v) => "0x" + v.toString(16).padStart(16, "0");

  /** Split the 63 used bits into the seven 9-bit column groups, high column first. */
  function fmtBin(v) {
    const out = [];
    for (let c = 0; c < N_COLUMNS; c++) {
      let grp = "";
      for (let r = 8; r >= 0; r--) grp += (v >> (BigInt(c) * OFF + BigInt(r))) & 1n ? "1" : "0";
      out.push(grp);
    }
    return out.reverse().join(" ");
  }

  global.C4 = {
    N_COLUMNS,
    N_ROWS,
    OFF,
    MASK64,
    BB_BOTTOM_ROW,
    BB_ALL_LEGAL,
    ODD_ROWS,
    EVEN_ROWS,
    PRIORITY,
    bitOf,
    colOf,
    popcount,
    legalMovesMask,
    winningPositions,
    hasWin,
    generateNonLosingMoves,
    doubleThreat,
    priorityClass,
    sortMoveScore,
    play,
    toHuffman,
    hash64,
    boardHash,
    fmtHex,
    fmtBin,
  };
})(typeof window !== "undefined" ? window : globalThis);
