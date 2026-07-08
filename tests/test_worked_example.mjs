// Dimension-level regression for the paper's worked example.
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { ucVerdict } from "../assets/scorecard_scoring.js";

const uc = JSON.parse(readFileSync(new URL("../data/use_cases.json", import.meta.url)));
const env = JSON.parse(readFileSync(new URL("../data/environments.json", import.meta.url)));
const goad = env.environments["goad"].scores;   // {D1:"P", ...}
const THRESHOLD = 0.75;                           // the app's default Full-threshold slider value

function verdictFor(ucId) {
  // ucVerdict returns a bare string: not_suitable | incomplete | suitable | partial
  return ucVerdict(uc.use_cases[ucId].profile, goad, THRESHOLD);
}

test("GOAD is not suitable for targeted data exfiltration (UC-A1)", () => {
  assert.equal(verdictFor("UC-A1"), "not_suitable");
});

test("GOAD is suitable for credential-based privilege escalation (UC-A5)", () => {
  assert.equal(verdictFor("UC-A5"), "suitable");
});
