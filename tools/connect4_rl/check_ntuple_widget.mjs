/**
 * Cross-check the in-browser n-tuple agent against the Python agent.
 *
 * Loads the shipped `assets/js/connect4-core.js` and `assets/js/connect4-ntuple.js` (not copies of them)
 * together with an exported weights file, replays the positions of a reference file written by
 * `ntuple_reference.py`, and compares the network values, the integer scores per column and the chosen
 * move with those of `TDConnect4AgentTorch`.
 *
 * Usage, from the repo root:
 *
 *   node tools/connect4_rl/check_ntuple_widget.mjs <weights.bin.gz> <reference.json>
 */
import fs from "node:fs";
import vm from "node:vm";
import zlib from "node:zlib";

const [weightsPath, refPath] = process.argv.slice(2);
if (!weightsPath || !refPath) {
  console.error("usage: node tools/connect4_rl/check_ntuple_widget.mjs <weights.bin.gz> <reference.json>");
  process.exit(2);
}

const sandbox = { TextDecoder };
vm.createContext(sandbox);
for (const f of ["assets/js/connect4-core.js", "assets/js/connect4-ntuple.js"]) {
  vm.runInContext(fs.readFileSync(f, "utf8"), sandbox, { filename: f });
}
const { C4NTuple } = sandbox;

const raw = zlib.gunzipSync(fs.readFileSync(weightsPath));
const net = C4NTuple.parseWeights(raw.buffer.slice(raw.byteOffset, raw.byteOffset + raw.byteLength));
const ref = JSON.parse(fs.readFileSync(refPath, "utf8"));

let scoreMismatches = 0;
let moveMismatches = 0;
let columns = 0;
let maxValueError = 0;
for (const p of ref.positions) {
  const state = { all: BigInt(p.all), active: BigInt(p.active), movesLeft: p.movesLeft };
  const { scores, values } = C4NTuple.scoreAllMoves(net, state);
  for (const [col, s] of Object.entries(p.scores)) {
    columns++;
    if (scores[col] !== s) scoreMismatches++;
  }
  for (const [col, v] of Object.entries(values)) {
    maxValueError = Math.max(maxValueError, Math.abs(v - p.values[col]));
  }
  if (C4NTuple.bestMove(net, state) !== p.best) moveMismatches++;
}

const n = ref.positions.length;
console.log(`weights ${weightsPath} (${net.header.dtype})`);
console.log(`positions ${n}, scored columns ${columns}`);
console.log(`max |value difference| ${maxValueError.toExponential(2)}`);
console.log(`score mismatches ${scoreMismatches} (${((100 * scoreMismatches) / columns).toFixed(3)}%)`);
console.log(`move mismatches  ${moveMismatches} (${((100 * moveMismatches) / n).toFixed(3)}%)`);
process.exit(moveMismatches === 0 || net.header.dtype !== "float32" ? 0 : 1);
