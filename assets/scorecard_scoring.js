// Pure scoring functions for the realism scorecard's per-use-case lens.
// Browser-global when inlined; CommonJS export (guarded) for node:test.
// reqs: { "D1.1":"C"|"U"|"-", ... }   scores: { "D1.1":"F"|"P"|"A"|"U", ... } (missing = unscored)

var GRADE_VALUE = { F: 1, P: 0.5, A: 0 };   // U / unscored excluded
var REQ_WEIGHT = { C: 2, U: 1 };            // '-' excluded

function isGraded(s) { return s === "F" || s === "P" || s === "A"; }
function isRequired(v) { return v === "C" || v === "U"; }

function ucFit(reqs, scores) {
  var num = 0, den = 0;
  for (var k in reqs) {
    if (!isRequired(reqs[k])) continue;
    var s = scores[k];
    if (!isGraded(s)) continue;
    var w = REQ_WEIGHT[reqs[k]];
    num += w * GRADE_VALUE[s];
    den += w;
  }
  return den === 0 ? null : num / den;
}

function requiredCompleteness(reqs, scores) {
  var total = 0, scored = 0;
  for (var k in reqs) {
    if (!isRequired(reqs[k])) continue;
    total += 1;
    if (isGraded(scores[k])) scored += 1;
  }
  return total === 0 ? null : scored / total;
}

function ucGaps(reqs, scores) {
  var hardGaps = [], unresolved = [];
  for (var k in reqs) {
    if (reqs[k] !== "C") continue;
    var s = scores[k];
    if (s === "A") hardGaps.push(k);
    else if (s === undefined || s === null || s === "U") unresolved.push(k);
  }
  return { hardGaps: hardGaps, unresolved: unresolved };
}

function ucVerdict(reqs, scores, threshold, minCompleteness) {
  if (minCompleteness === undefined) minCompleteness = 0.8;
  var gaps = ucGaps(reqs, scores);
  if (gaps.hardGaps.length > 0) return "not_suitable";
  var fit = ucFit(reqs, scores);
  var completeness = requiredCompleteness(reqs, scores);
  if (fit === null || gaps.unresolved.length > 0 ||
      completeness === null || completeness < minCompleteness) return "incomplete";
  return fit >= threshold ? "suitable" : "partial";
}

function dimRequiredCoverage(reqs, scores, dimId) {
  var prefix = dimId + ".";
  var num = 0, den = 0, hasRequired = false;
  for (var k in reqs) {
    if (k.slice(0, prefix.length) !== prefix) continue;
    if (!isRequired(reqs[k])) continue;
    hasRequired = true;
    var s = scores[k];
    if (!isGraded(s)) continue;
    var w = REQ_WEIGHT[reqs[k]];
    num += w * GRADE_VALUE[s];
    den += w;
  }
  if (!hasRequired) return "not_required";
  return den === 0 ? null : num / den;
}

function csvCell(v) {
  v = (v === null || v === undefined) ? "" : String(v);
  return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
}

function parseCSV(text) {
  var rows = [], row = [], cur = "", q = false;
  for (var i = 0; i < text.length; i++) {
    var c = text[i];
    if (q) {
      if (c === '"') { if (text[i + 1] === '"') { cur += '"'; i++; } else q = false; }
      else cur += c;
    } else if (c === '"') q = true;
    else if (c === ",") { row.push(cur); cur = ""; }
    else if (c === "\n" || c === "\r") {
      if (c === "\r" && text[i + 1] === "\n") i++;
      row.push(cur); rows.push(row); row = []; cur = "";
    } else cur += c;
  }
  if (cur.length || row.length) { row.push(cur); rows.push(row); }
  return rows;
}

export { ucFit, requiredCompleteness, ucGaps, ucVerdict, dimRequiredCoverage, csvCell, parseCSV };
