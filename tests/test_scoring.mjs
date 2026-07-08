import test from "node:test";
import assert from "node:assert/strict";
import * as S from "../assets/scorecard_scoring.js";

// reqs covering 3 elements in one dimension for focused tests
const reqs = { "D1.1": "C", "D1.2": "C", "D1.3": "U", "D1.4": "-" };

test("ucFit excludes Not-needed, Unknown, and unscored", () => {
  // D1.1=F(C,w2,v1)=2, D1.2=P(C,w2,v.5)=1, D1.3=F(U,w1,v1)=1 ; den=2+2+1=5
  const fit = S.ucFit(reqs, { "D1.1": "F", "D1.2": "P", "D1.3": "F", "D1.4": "F" });
  assert.equal(fit, 4 / 5);
});

test("ucFit is null when no required element is scored", () => {
  assert.equal(S.ucFit(reqs, { "D1.4": "F", "D1.1": "U" }), null);
});

test("requiredCompleteness counts scored required over total required", () => {
  // required = D1.1,D1.2,D1.3 (3). scored F/P/A = D1.1,D1.2 (2)
  assert.equal(S.requiredCompleteness(reqs, { "D1.1": "F", "D1.2": "A", "D1.3": "U" }), 2 / 3);
});

test("ucGaps splits Absent (hard) from Unknown/unscored (unresolved), criticals only", () => {
  const g = S.ucGaps(reqs, { "D1.1": "A", "D1.2": "U", "D1.3": "A" });
  assert.deepEqual(g.hardGaps, ["D1.1"]);       // D1.3 is Useful, not listed
  assert.deepEqual(g.unresolved, ["D1.2"]);
});

test("verdict: not_suitable when any Critical is Absent (precedence)", () => {
  const v = S.ucVerdict(reqs, { "D1.1": "A", "D1.2": "U", "D1.3": "F" }, 0.75, 0.8);
  assert.equal(v, "not_suitable");
});

test("verdict: incomplete on undefined fit", () => {
  assert.equal(S.ucVerdict(reqs, {}, 0.75, 0.8), "incomplete");
});

test("verdict: incomplete on unresolved Critical", () => {
  // D1.1=F, D1.2=U (unresolved critical) -> incomplete
  const v = S.ucVerdict(reqs, { "D1.1": "F", "D1.2": "U", "D1.3": "F" }, 0.75, 0.8);
  assert.equal(v, "incomplete");
});

test("verdict: incomplete on low required-completeness", () => {
  // only D1.1 scored of 3 required -> completeness 1/3 < 0.8
  const v = S.ucVerdict(reqs, { "D1.1": "F" }, 0.75, 0.8);
  assert.equal(v, "incomplete");
});

test("verdict: suitable at fit == threshold (inclusive)", () => {
  // all required F -> fit 1.0; completeness 1.0; >= 1.0 threshold
  const v = S.ucVerdict(reqs, { "D1.1": "F", "D1.2": "F", "D1.3": "F" }, 1.0, 0.8);
  assert.equal(v, "suitable");
});

test("verdict: partial when complete + no gaps but fit below threshold", () => {
  // D1.1=P,D1.2=P,D1.3=P -> fit .5 ; completeness 1 ; threshold .75
  const v = S.ucVerdict(reqs, { "D1.1": "P", "D1.2": "P", "D1.3": "P" }, 0.75, 0.8);
  assert.equal(v, "partial");
});

test("Useful-unscored inflation does not yield suitable", () => {
  // criticals all F, the single Useful required unscored -> completeness 2/3 < .8
  const v = S.ucVerdict(reqs, { "D1.1": "F", "D1.2": "F" }, 0.75, 0.8);
  assert.equal(v, "incomplete");
});

test("dimRequiredCoverage returns not_required when dimension has no required elements", () => {
  const r2 = { "D9.1": "-", "D9.2": "-" };
  assert.equal(S.dimRequiredCoverage(r2, { "D9.1": "F" }, "D9"), "not_required");
});

test("dimRequiredCoverage does not confuse D1 with D10", () => {
  const r2 = { "D1.1": "C", "D10.1": "C" };
  assert.equal(S.dimRequiredCoverage(r2, { "D1.1": "F", "D10.1": "A" }, "D1"), 1);
});

test("csvCell quotes commas, quotes, and newlines", () => {
  assert.equal(S.csvCell("plain"), "plain");
  assert.equal(S.csvCell("a,b"), '"a,b"');
  assert.equal(S.csvCell('he said "hi"'), '"he said ""hi"""');
  assert.equal(S.csvCell("line1\nline2"), '"line1\nline2"');
  assert.equal(S.csvCell(null), "");
});

test("parseCSV round-trips quoted commas, quotes, and embedded newlines", () => {
  const rows = [["a", "b,c", 'd"e', "f\ng"], ["1", "2", "3", "4"]];
  const text = rows.map(r => r.map(S.csvCell).join(",")).join("\n");
  assert.deepEqual(S.parseCSV(text), rows);
});

test("ucVerdict defaults minCompleteness to 0.8 when the arg is omitted", () => {
  // criticals all F, single Useful required unscored -> completeness 2/3 < 0.8 -> incomplete
  assert.equal(S.ucVerdict(reqs, { "D1.1": "F", "D1.2": "F" }, 0.75), "incomplete");
});
