"""Assemble data/environment_element_scores.json from the source repo.

Element-level coverage is assessed in the source repo and copied here. The only
transformation is the key: the source keys environments by display name, while
this site keys them by the lowercase slug used in data/environments.json,
verdicts.json, and the generated page filenames.

Environments absent from the output file have not been assessed at element level.
Cross-environment comparison stays at dimension level until every environment has
been assessed here, because a flat mean over a dimension's elements and a
dimension-level grade are not directly comparable.

Usage:
    python build/seed_environment_elements.py \\
        <path to environment_element_scores.json> data/environment_element_scores.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def main(src_path, out_path):
    src = json.load(open(src_path))["environments"]
    site_envs = json.load(open(os.path.join(ROOT, "data", "environments.json")))["environments"]
    elements = json.load(open(os.path.join(ROOT, "data", "dimension_elements.json")))["dimensions"]
    valid_keys = {f"{d['id']}.{el['n']}" for d in elements for el in d["elements"]}

    out_envs = {}
    for name, rec in src.items():
        slug = name.lower()
        if slug not in site_envs:
            raise SystemExit(
                f"{name!r} maps to slug {slug!r}, which is not in data/environments.json. "
                f"Add the environment there first, or add an explicit mapping here."
            )
        scores = rec["scores"]
        if set(scores) != valid_keys:
            missing = sorted(valid_keys - set(scores))[:3]
            extra = sorted(set(scores) - valid_keys)[:3]
            raise SystemExit(f"{slug}: scores do not match the element catalog "
                             f"(missing {missing}, unexpected {extra})")

        entry = {"source": rec.get("source", ""), "scores": scores}
        notes = rec.get("notes")
        if notes:
            entry["notes"] = {k: notes[k] for k in scores if k in notes}
        out_envs[slug] = entry

    out = {
        "meta": {
            "scale": ["F", "P", "A", "U"],
            "key_format": "D{dim}.{n}",
            "note": ("Element-level coverage per environment. Keys match data/environments.json. "
                     "Environments absent from this file have not been assessed at this level, "
                     "and cross-environment comparison remains at dimension level until all are."),
        },
        "environments": out_envs,
    }
    json.dump(out, open(out_path, "w"), indent=2, ensure_ascii=False)

    print(f"wrote {out_path}: {len(out_envs)} environment(s) assessed at element level")
    for slug, e in out_envs.items():
        counts = {}
        for v in e["scores"].values():
            counts[v] = counts.get(v, 0) + 1
        summary = ", ".join(f"{counts.get(c, 0)} {c}" for c in ("F", "P", "A", "U"))
        print(f"  {slug}: {len(e['scores'])} elements ({summary}); "
              f"notes on {len(e.get('notes', {}))}")
    unscored = sorted(set(site_envs) - set(out_envs))
    print(f"  not yet assessed at element level ({len(unscored)}): {', '.join(unscored)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
