/**
 * Cross-check the interactive widgets against the real engine.
 *
 * Loads the shipped `assets/js/connect4-core.js` (not a copy of it) and replays
 * a list of move sequences, comparing every operation the widgets rely on
 * against BitBully: the two bit boards, the legal-move mask, uid(), hasWin(),
 * generateNonLosingMoves(), doubleThreat(), the centre-first move ordering and
 * the Huffman encoding of the opening books.
 *
 * Usage, from the repo root:
 *
 *   tools/.venv/bin/python tools/connect4/widget_reference.py > /tmp/ref.json
 *   node tools/connect4/check_widget.mjs /tmp/ref.json
 */
import fs from "node:fs";
import vm from "node:vm";

const refPath = process.argv[2];
if (!refPath) {
  console.error("usage: node tools/connect4/check_widget.mjs <reference.json>");
  process.exit(2);
}

// Load the real widget core into a sandbox and take the C4 namespace it exports.
const sandbox = {};
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync("assets/js/connect4-core.js", "utf8"), sandbox);
vm.runInContext(fs.readFileSync("assets/js/connect4-search.js", "utf8"), sandbox);
const C4 = sandbox.C4;
const C4Search = sandbox.C4Search;
if (!C4) throw new Error("connect4-core.js did not define C4");
if (!C4Search) throw new Error("connect4-search.js did not define C4Search");

const ref = JSON.parse(fs.readFileSync(refPath, "utf8"));
const failures = [];

/** Order the legal moves the way Board::sortMoves + MoveList::pop would. */
function orderedColumns(all, active) {
  const moves = [];
  let m = C4.legalMovesMask(all);
  while (m) {
    const mv = m & -m;
    moves.push({ mv, score: C4.sortMoveScore(all, active, mv), prio: C4.priorityClass(mv) });
    m ^= mv;
  }
  // MoveList is a stable insertion sort popped from the top: highest score
  // first, ties broken by insertion order, which nextMove() makes centre-first.
  moves.sort((a, b) => b.score - a.score || a.prio - b.prio);
  return moves.map((x) => C4.colOf(x.mv));
}

for (const t of ref) {
  let st = { all: 0n, active: 0n, movesLeft: 42 };
  for (const col of t.moves) {
    const legal = C4.legalMovesMask(st.all);
    let mv = 0n;
    for (let r = 0; r < C4.N_ROWS; r++) {
      const b = C4.bitOf(col, r);
      if (legal & b) {
        mv = b;
        break;
      }
    }
    if (!mv) throw new Error("illegal move in reference sequence");
    st = C4.play(st, mv);
  }

  const checks = {
    all: st.all === BigInt(t.all),
    active: st.active === BigInt(t.active),
    legal: C4.legalMovesMask(st.all) === BigInt(t.legal),
    uid: st.active + st.all === BigInt(t.uid),
    hash: C4.boardHash(st.all, st.active) === BigInt(t.hash),
    hasWin: C4.hasWin(st.all, st.active) === t.hasWin,
    movesLeft: st.movesLeft === t.movesLeft,
    nonLosing: C4.generateNonLosingMoves(st.all, st.active) === BigInt(t.nonLosing),
    doubleThreat: C4.doubleThreat(st.all, st.active, C4.legalMovesMask(st.all)) === BigInt(t.doubleThreat),
    ordering: JSON.stringify(orderedColumns(st.all, st.active)) === JSON.stringify(t.ordered),
  };
  if ("huffman" in t) {
    checks.huffman = Number(BigInt.asIntN(32, C4.toHuffman(st.all, st.active).value)) === t.huffman;
  }
  if ("score" in t) {
    // The JS solver of the part-7 widget: all three drivers must reproduce
    // the engine's score, and the unpacked distance must agree as well.
    const mtdf = C4Search.driveMtdf(st, 0);
    const nega = C4Search.driveNegamax(st);
    const nullw = C4Search.driveNullWindow(st);
    checks.solverMtdf = mtdf.score === t.score;
    checks.solverNegamax = nega.score === t.score;
    checks.solverNullWindow = nullw.score === t.score;
    checks.solverEndsIn = C4Search.scoreToMovesLeft(mtdf.score, st) === t.endsIn;
  }

  for (const [name, ok] of Object.entries(checks)) {
    if (!ok) failures.push({ name, moves: t.moves });
  }
}

const byCheck = {};
for (const f of failures) byCheck[f.name] = (byCheck[f.name] || 0) + 1;

console.log(`checked ${ref.length} positions against BitBully`);
if (failures.length === 0) {
  console.log("  all operations agree");
} else {
  for (const [name, n] of Object.entries(byCheck)) console.log(`  ${name}: ${n} mismatches`);
  console.log("  first failing move sequence:", JSON.stringify(failures[0].moves));
}
process.exit(failures.length ? 1 : 0);
