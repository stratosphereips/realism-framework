import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))
from validate_data import validate_environment_elements, load_json  # noqa: E402

ELEM_SCORES = ROOT / "data" / "environment_element_scores.json"
ELEMENTS = ROOT / "data" / "dimension_elements.json"
ENVS = ROOT / "data" / "environments.json"


def _write(tmp_path, data):
    p = tmp_path / "element_scores.json"
    p.write_text(json.dumps(data))
    return p


def test_real_file_valid():
    assert validate_environment_elements(ELEM_SCORES, ELEMENTS, ENVS) == []


def test_partial_coverage_is_allowed():
    """Only assessed environments appear; the rest are absent, not empty."""
    scored = set(load_json(ELEM_SCORES)["environments"])
    known = set(load_json(ENVS)["environments"])
    assert scored, "expected at least one environment assessed at element level"
    assert scored < known, "assessed environments must be a subset of known environments"


def test_goad_covers_every_element_with_a_reason():
    rec = load_json(ELEM_SCORES)["environments"]["goad"]
    assert len(rec["scores"]) == 115
    assert set(rec["notes"]) == set(rec["scores"]), "every grade needs a recorded reason"
    assert rec["source"]


def test_rejects_unknown_environment(tmp_path):
    data = load_json(ELEM_SCORES)
    data["environments"]["not-an-environment"] = data["environments"]["goad"]
    errs = validate_environment_elements(_write(tmp_path, data), ELEMENTS, ENVS)
    assert any("not an environment" in e for e in errs)


def test_rejects_incomplete_element_coverage(tmp_path):
    data = copy.deepcopy(load_json(ELEM_SCORES))
    data["environments"]["goad"]["scores"].pop("D1.1")
    errs = validate_environment_elements(_write(tmp_path, data), ELEMENTS, ENVS)
    assert any("element catalog exactly" in e for e in errs)


def test_rejects_bad_code(tmp_path):
    data = copy.deepcopy(load_json(ELEM_SCORES))
    data["environments"]["goad"]["scores"]["D1.1"] = "C"  # a requirement level, not a coverage code
    errs = validate_environment_elements(_write(tmp_path, data), ELEMENTS, ENVS)
    assert any("bad code" in e for e in errs)


def test_rejects_note_for_unknown_element(tmp_path):
    data = copy.deepcopy(load_json(ELEM_SCORES))
    data["environments"]["goad"]["notes"]["D99.1"] = "no such element"
    errs = validate_environment_elements(_write(tmp_path, data), ELEMENTS, ENVS)
    assert any("unknown elements" in e for e in errs)
