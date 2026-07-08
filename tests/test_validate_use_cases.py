import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))
from validate_data import validate_use_cases, load_json, element_ids

UC = ROOT / "data" / "use_cases.json"
EL = ROOT / "data" / "dimension_elements.json"
EXPECTED = {"UC-A1", "UC-A2", "UC-A3", "UC-A5", "UC-A6",
            "UC-D1", "UC-D2", "UC-D3", "UC-S1", "UC-S2"}  # 10 IT-enterprise use cases
# (UC-A7/A8/D6 are out of scope for the IT-enterprise comparison; UC-A4/A9/D4/D5/S3
#  have no dimension profile in the methodology mapping.)


def test_real_use_cases_valid():
    assert validate_use_cases(UC, EL) == []


def test_has_the_10_enterprise_use_cases():
    assert set(load_json(UC)["use_cases"]) == EXPECTED


def test_uc_a1_requirements_cover_all_115_elements():
    reqs = load_json(UC)["use_cases"]["UC-A1"]["requirements"]
    assert set(reqs) == element_ids(load_json(EL))


def test_detects_bad_level(tmp_path):
    data = load_json(UC)
    data["use_cases"]["UC-A1"]["profile"]["D1"] = "X"
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(data))
    assert validate_use_cases(p, EL) != []
