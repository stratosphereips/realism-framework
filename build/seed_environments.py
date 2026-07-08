"""One-off: read environment_scores.csv and emit an environments.json skeleton
(scores filled from the CSV; summary/justification/sources left for curation)."""
import csv
import json
import sys

NAME_TO_D = {"topological": "D1", "service": "D2", "os": "D3", "identity": "D4",
             "temporal": "D5", "defensive": "D6", "benign": "D7", "telemetry": "D8",
             "action": "D9", "observation": "D10", "external": "D11"}

# Documented in the main repo but NOT evaluated in the artifact site: no verifiable
# public artifact/link could be found (paper-only sources).
EXCLUDE = {"farland", "cybershield", "cye", "cygil", "scorpion"}


def slug(name):
    return "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")


def main(csv_path, out_path):
    envs = {}
    with open(csv_path, newline="") as fh:
        for r in csv.DictReader(fh):
            s = slug(r["environment"])
            if s in EXCLUDE:
                continue
            scores = {NAME_TO_D[n]: r[n] for n in NAME_TO_D}
            envs[s] = {
                "name": r["environment"], "category": r["category"],
                "scores": scores, "summary": "", "justification": {}, "sources": []}
    json.dump({"environments": envs}, open(out_path, "w"), indent=2)
    print(f"wrote {out_path}: {len(envs)} environments (excluded {len(EXCLUDE)})")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
