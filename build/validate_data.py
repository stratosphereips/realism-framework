"""JSON-schema-style validation for the three public data files.
Each validate_* returns a list of human-readable error strings ([] == valid)."""
import json

DIMS = [f"D{i}" for i in range(1, 12)]


def load_json(path):
    with open(path) as fh:
        return json.load(fh)


def element_ids(elements_data):
    ids = set()
    for d in elements_data["dimensions"]:
        for e in d["elements"]:
            ids.add(f'{d["id"]}.{e["n"]}')
    return ids


def validate_elements(path):
    errs = []
    data = load_json(path)
    ids = [d["id"] for d in data.get("dimensions", [])]
    if ids != DIMS:
        errs.append(f"dimensions must be {DIMS}, got {ids}")
    total = sum(len(d.get("elements", [])) for d in data.get("dimensions", []))
    if total != 115:
        errs.append(f"expected 115 sub-dimensions, got {total}")
    for d in data.get("dimensions", []):
        for e in d.get("elements", []):
            for key in ("n", "label", "desc"):
                if key not in e:
                    errs.append(f'{d["id"]} sub-dimension missing {key}')
    return errs


LEVELS = {"C", "U", "-"}


def validate_use_cases(uc_path, elements_path):
    errs = []
    data = load_json(uc_path)
    ids = element_ids(load_json(elements_path))
    for uc_id, uc in data.get("use_cases", {}).items():
        prof = uc.get("profile", {})
        if set(prof) != set(DIMS):
            errs.append(f"{uc_id}: profile keys must be {DIMS}")
        for k, v in prof.items():
            if v not in LEVELS:
                errs.append(f"{uc_id}: bad level {v!r} at {k}")
        reqs = uc.get("requirements", {})
        for k, v in reqs.items():
            if k not in ids:
                errs.append(f"{uc_id}: requirement {k} is not a real sub-dimension id")
            if v not in LEVELS:
                errs.append(f"{uc_id}: bad requirement level {v!r} at {k}")
        if reqs and set(reqs) != ids:
            errs.append(f"{uc_id}: sub-dimension requirements must cover all {len(ids)} "
                        f"sub-dimensions ({len(ids - set(reqs))} missing)")
    return errs


CODES = {"F", "P", "A", "U"}


def validate_environments(path):
    errs = []
    data = load_json(path)
    for env_id, env in data.get("environments", {}).items():
        if env_id != env_id.lower() or " " in env_id:
            errs.append(f"{env_id}: id must be a lowercase slug")
        sc = env.get("scores", {})
        if set(sc) != set(DIMS):
            errs.append(f"{env_id}: scores must have keys {DIMS}")
        for k, v in sc.items():
            if v not in CODES:
                errs.append(f"{env_id}: bad code {v!r} at {k}")
        if not env.get("summary"):
            errs.append(f"{env_id}: missing summary")
        if env.get("family") not in {"Real-software emulator", "Abstract simulator", "Cyber range / other"}:
            errs.append(f"{env_id}: family must be a known value, got {env.get('family')!r}")
        for s in env.get("sources", []):
            if not str(s.get("url", "")).startswith(("http://", "https://")):
                errs.append(f"{env_id}: source url must be http(s)")
    return errs


def validate_dimensions_meta(path):
    errs = []
    data = load_json(path)
    covered = []
    for g in data.get("groups", []):
        if not g.get("name") or not g.get("question"):
            errs.append("group missing name or question")
        covered += g.get("dims", [])
    if sorted(covered) != sorted(DIMS):
        errs.append(f"groups must cover each of {DIMS} exactly once; got {sorted(covered)}")
    if set(data.get("short", {})) != set(DIMS):
        errs.append(f"short must have keys {DIMS}")
    return errs
