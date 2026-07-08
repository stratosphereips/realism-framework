#!/usr/bin/env bash
# Validate data, regenerate figures and pages, and run the test suite.
set -euo pipefail
cd "$(dirname "$0")"

node build/compute_verdicts.mjs
conda run -n ml python build/generate_site.py
node --test tests/*.mjs
conda run -n ml python -m pytest tests/ -q

echo "build OK"
