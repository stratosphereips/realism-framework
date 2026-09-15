// Compute every (environment, use-case) verdict once, at build time, using the SAME
// scoring module the browser app uses, and write verdicts.json for the generator.
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { ucVerdict, ucFit, requiredCompleteness, ucGaps } from "../assets/scorecard_scoring.js";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const uc = JSON.parse(readFileSync(join(ROOT, "data/use_cases.json"))).use_cases;
const env = JSON.parse(readFileSync(join(ROOT, "data/environments.json"))).environments;
const THRESHOLD = 0.75;

// Verdicts are computed at the dimension level: 11 requirement levels against 11
// coverage grades. The scoring functions are key-agnostic and would compute an
// element-level verdict if given 115-key inputs, but environment coverage exists at
// that granularity for only some environments, and the two levels are not directly
// comparable. Recording the granularity keeps that explicit for anyone reading the file.
const out = { threshold: THRESHOLD, granularity: "dimension", pairs: {} };
for (const [es, e] of Object.entries(env)) {
  out.pairs[es] = {};
  for (const [us, u] of Object.entries(uc)) {
    const g = ucGaps(u.profile, e.scores);
    out.pairs[es][us] = {
      verdict: ucVerdict(u.profile, e.scores, THRESHOLD),
      fit: ucFit(u.profile, e.scores),
      completeness: requiredCompleteness(u.profile, e.scores),
      hardGaps: g.hardGaps,       // critical dimensions scored Absent
      unresolved: g.unresolved,   // critical dimensions scored Unknown
    };
  }
}
writeFileSync(join(ROOT, "verdicts.json"), JSON.stringify(out, null, 2) + "\n");
console.log(`wrote verdicts.json: ${Object.keys(out.pairs).length} environments x ${Object.keys(uc).length} use cases`);
