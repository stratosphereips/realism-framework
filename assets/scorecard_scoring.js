// Pure scoring functions for the realism scorecard's per-use-case lens.
// Browser-global when inlined; CommonJS export (guarded) for node:test.
// reqs: { "D1.1":"C"|"U"|"-", ... }   scores: { "D1.1":"F"|"P"|"A"|"U", ... } (missing = unscored)
//
// Alternative requirement groups (optional `groups` argument): a use case may permit
// several valid ways to meet an objective. Each group is critical as a whole and is
// satisfied when any one option is complete. Members of a group stay Useful at the
// atomic level in `reqs`; the group carries the critical relationship. Shape:
//   { id, name, priority:"C", rule:"any_of", options: [ { name, all_of:["D2.2", ...] }, ... ] }

var GRADE_VALUE = { F: 1, P: 0.5, A: 0 };   // U / unscored excluded
var REQ_WEIGHT = { C: 2, U: 1 };            // '-' excluded

function isGraded(s) { return s === "F" || s === "P" || s === "A"; }
function isRequired(v) { return v === "C" || v === "U"; }

// --- alternative requirement groups -------------------------------------------

function memberState(s) {
  if (s === "F" || s === "P") return "present";
  if (s === "A") return "absent";
  return "unknown";                          // "U", undefined, or unscored
}

// An option is complete when all its elements are present, blocked when any is
// absent, and otherwise unknown (no absent element but at least one unresolved).
function optionState(option, scores) {
  var anyAbsent = false, anyUnknown = false;
  var keys = option.all_of || [];
  for (var i = 0; i < keys.length; i++) {
    var st = memberState(scores[keys[i]]);
    if (st === "absent") anyAbsent = true;
    else if (st === "unknown") anyUnknown = true;
  }
  if (anyAbsent) return "blocked";
  if (anyUnknown) return "unknown";
  return "complete";
}

// satisfied: some option complete; unresolved: none complete but some could be
// (unknown); unmet: every option is blocked by an absent element.
function groupState(group, scores) {
  var complete = false, unknown = false;
  var opts = group.options || [];
  for (var i = 0; i < opts.length; i++) {
    var st = optionState(opts[i], scores);
    if (st === "complete") complete = true;
    else if (st === "unknown") unknown = true;
  }
  if (complete) return "satisfied";
  if (unknown) return "unresolved";
  return "unmet";
}

// Best option coverage (0..1): the mean grade value over an option's graded
// elements, maximised across options. Size-independent, so a larger option is
// neither rewarded nor penalised. Null when no option has any graded element.
function groupBestCoverage(group, scores) {
  var best = null;
  var opts = group.options || [];
  for (var i = 0; i < opts.length; i++) {
    var keys = opts[i].all_of || [];
    var num = 0, den = 0;
    for (var j = 0; j < keys.length; j++) {
      var s = scores[keys[j]];
      if (!isGraded(s)) continue;
      num += GRADE_VALUE[s];
      den += 1;
    }
    if (den > 0) {
      var cov = num / den;
      if (best === null || cov > best) best = cov;
    }
  }
  return best;
}

function groupedKeys(groups) {
  var set = {};
  (groups || []).forEach(function (g) {
    (g.options || []).forEach(function (o) {
      (o.all_of || []).forEach(function (k) { set[k] = true; });
    });
  });
  return set;
}

// --- scoring ------------------------------------------------------------------

function ucFit(reqs, scores, groups) {
  groups = groups || [];
  var grouped = groupedKeys(groups);
  var num = 0, den = 0;
  for (var k in reqs) {
    if (!isRequired(reqs[k])) continue;
    if (grouped[k]) continue;                // counted via the group term instead
    var s = scores[k];
    if (!isGraded(s)) continue;
    var w = REQ_WEIGHT[reqs[k]];
    num += w * GRADE_VALUE[s];
    den += w;
  }
  for (var i = 0; i < groups.length; i++) {
    var g = groups[i];
    var cov = groupBestCoverage(g, scores);
    if (cov === null) continue;
    var gw = REQ_WEIGHT[g.priority] || 2;
    num += gw * cov;
    den += gw;
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

function ucGaps(reqs, scores, groups) {
  groups = groups || [];
  var hardGaps = [], unresolved = [];
  for (var k in reqs) {
    if (reqs[k] !== "C") continue;
    var s = scores[k];
    if (s === "A") hardGaps.push(k);
    else if (s === undefined || s === null || s === "U") unresolved.push(k);
  }
  var groupGaps = [], groupUnresolved = [];
  for (var i = 0; i < groups.length; i++) {
    var st = groupState(groups[i], scores);
    var label = groups[i].name || groups[i].id;
    if (st === "unmet") groupGaps.push(label);
    else if (st === "unresolved") groupUnresolved.push(label);
  }
  return { hardGaps: hardGaps, unresolved: unresolved,
           groupGaps: groupGaps, groupUnresolved: groupUnresolved };
}

function ucVerdict(reqs, scores, threshold, minCompleteness, groups) {
  if (minCompleteness === undefined) minCompleteness = 0.8;
  var gaps = ucGaps(reqs, scores, groups);
  if (gaps.hardGaps.length > 0 || gaps.groupGaps.length > 0) return "not_suitable";
  var fit = ucFit(reqs, scores, groups);
  var completeness = requiredCompleteness(reqs, scores);
  if (fit === null || gaps.unresolved.length > 0 || gaps.groupUnresolved.length > 0 ||
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

export { ucFit, requiredCompleteness, ucGaps, ucVerdict, dimRequiredCoverage,
         groupState, optionState, groupBestCoverage, csvCell, parseCSV };
