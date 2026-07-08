"""Validate data, render figures, and generate the static site."""
import os
import re
import sys
from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate_data as V  # noqa: E402
import radar  # noqa: E402

DIMS = [f"D{i}" for i in range(1, 12)]
DIM_ABBR = {"D1": "Topo", "D2": "Svc", "D3": "OS", "D4": "Id", "D5": "Tmp",
            "D6": "Def", "D7": "Ben", "D8": "Tel", "D9": "Act", "D10": "Obs", "D11": "Ext"}
LEVEL_WORD = {"C": "Critical", "U": "Useful", "-": "Not needed"}
CODE_WORD = {"F": "Full", "P": "Partial", "A": "Absent", "U": "Unknown"}
VERDICT_WORD = {"suitable": "Suitable", "partial": "Partial fit",
                "not_suitable": "Not suitable", "incomplete": "Incomplete data"}


def _validate(root):
    d = os.path.join(root, "data")
    errs = (V.validate_elements(os.path.join(d, "dimension_elements.json"))
            + V.validate_use_cases(os.path.join(d, "use_cases.json"),
                                   os.path.join(d, "dimension_elements.json"))
            + V.validate_environments(os.path.join(d, "environments.json"))
            + V.validate_dimensions_meta(os.path.join(d, "dimensions.json")))
    if errs:
        raise SystemExit("DATA VALIDATION FAILED:\n  " + "\n  ".join(errs))
    if not os.path.exists(os.path.join(root, "verdicts.json")):
        raise SystemExit("verdicts.json missing; run build/compute_verdicts.mjs (or ./build.sh) first.")


def _element_summary(requirements):
    summ = {d: {"C": 0, "U": 0, "-": 0} for d in DIMS}
    for key, lvl in requirements.items():
        summ[key.split(".")[0]][lvl] += 1
    return summ


def _reason(rec, dim_names):
    """A diagnostic phrase for an (environment, objective) verdict."""
    v = rec["verdict"]
    if v == "suitable":
        return "covers the dimensions this objective requires"
    if v == "partial":
        return "covers the required dimensions, but below the fit threshold"
    if v == "not_suitable":
        gaps = rec.get("hardGaps", [])
        if gaps:
            noun = "a dimension" if len(gaps) == 1 else "dimensions"
            return ("does not provide " + ", ".join(dim_names[d] for d in gaps)
                    + ", " + noun + " this objective treats as critical")
        return "misses a dimension this objective treats as critical"
    unk = rec.get("unresolved", [])
    if unk:
        return "coverage of " + ", ".join(dim_names[d] for d in unk) + " is unknown"
    return "too little of the required coverage is documented"


def build(root):
    root = str(root)
    _validate(root)
    radar.render_all(os.path.join(root, "data"), os.path.join(root, "figures"))
    env = Environment(loader=FileSystemLoader(os.path.join(root, "build", "templates")),
                      autoescape=True)

    def load(name):
        return V.load_json(os.path.join(root, "data", f"{name}.json"))

    elements = load("dimension_elements")
    ucs = load("use_cases")["use_cases"]
    envs = load("environments")["environments"]
    dims_meta = load("dimensions")
    site = load("site")
    verdicts = V.load_json(os.path.join(root, "verdicts.json"))["pairs"]
    dim_names = {d["id"]: d["name"] for d in elements["dimensions"]}
    g = dict(dims=DIMS, dim_abbr=DIM_ABBR, dim_names=dim_names,
             level_word=LEVEL_WORD, code_word=CODE_WORD,
             wip=site.get("wip", False), wip_note=site.get("wip_note", ""))

    def write(path, tmpl, rel, **ctx):
        html = env.get_template(tmpl).render(rel=rel, **g, **ctx)
        full = os.path.join(root, path)
        os.makedirs(os.path.dirname(full) or root, exist_ok=True)
        with open(full, "w") as fh:
            fh.write(html)

    # ---- field-level aggregates for the Environments index ----
    coverage = {d: {"F": 0, "P": 0, "A": 0, "U": 0} for d in DIMS}
    for e in envs.values():
        for d in DIMS:
            coverage[d][e["scores"][d]] += 1
    least_covered = [dim_names[d] for d in sorted(DIMS, key=lambda x: -coverage[x]["A"])[:5]]
    served = {u: 0 for u in ucs}
    for slug in verdicts:
        for u, rec in verdicts[slug].items():
            if rec["verdict"] in ("suitable", "partial"):
                served[u] = served.get(u, 0) + 1
    unserved = [ucs[u]["name"] for u in ucs if served.get(u, 0) == 0]
    family_counts = {}
    for e in envs.values():
        fam = e.get("family", "?")
        family_counts[fam] = family_counts.get(fam, 0) + 1

    caption = f"Realism coverage of {len(envs)} environments across 11 dimensions."
    write("index.html", "index.html.j2", "", groups=dims_meta["groups"],
          dim_short=dims_meta["short"], dim_notes=dims_meta.get("notes", {}),
          n_uc=len(ucs), n_env=len(envs))
    write("use-cases/index.html", "use_cases_index.html.j2", "../", ucs=ucs)
    for uc_id, uc in ucs.items():
        es = _element_summary(uc["requirements"]) if uc.get("requirements") else None
        write(f"use-cases/{uc_id}.html", "use_case.html.j2", "../",
              uc_id=uc_id, uc=uc, element_summary=es)
    write("environments/index.html", "environments_index.html.j2", "../",
          envs=envs, caption=caption, least_covered=least_covered,
          unserved=unserved, family_counts=family_counts)
    for slug, e in envs.items():
        fits = [{"id": uc_id, "name": uc["name"], "verdict": verdicts[slug][uc_id]["verdict"],
                 "word": VERDICT_WORD[verdicts[slug][uc_id]["verdict"]],
                 "reason": _reason(verdicts[slug][uc_id], dim_names)}
                for uc_id, uc in ucs.items()]
        best = [f["name"] for f in fits if f["verdict"] in ("suitable", "partial")]
        write(f"environments/{slug}.html", "environment.html.j2", "../",
              slug=slug, env=e, objective_fits=fits, best_suited=best)


# Unrendered Jinja tags always contain "{{"; matching that (not bare "}}") avoids
# false positives on legitimate JavaScript, which routinely contains "}}".
PLACEHOLDER = re.compile(r"\{\{|\bTODO\b|\bTBD\b")


def check_output(root):
    root = str(root)
    errs = []
    pages = [os.path.join(dp, f) for dp, _, fs in os.walk(root) for f in fs
             if f.endswith(".html") and ".git" not in dp]
    for p in pages:
        html = open(p).read()
        if PLACEHOLDER.search(html):
            errs.append(f"{p}: leftover placeholder/unrendered tag")
        for m in re.finditer(r'(?:href|src)="(?!https?:|mailto:|data:|//|#)([^"]+)"', html):
            target = os.path.normpath(os.path.join(os.path.dirname(p), m.group(1).split("#")[0]))
            if m.group(1) and not os.path.exists(target):
                errs.append(f"{p}: broken link {m.group(1)}")
    return errs


if __name__ == "__main__":
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    build(here)
    problems = check_output(here)
    if problems:
        raise SystemExit("PROBLEMS:\n  " + "\n  ".join(problems))
    print("built OK")
