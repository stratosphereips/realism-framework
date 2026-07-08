import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))
from validate_data import validate_elements, load_json

ELEMENTS = ROOT / "data" / "dimension_elements.json"
DIMS = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11"]


def test_real_catalog_is_valid():
    assert validate_elements(ELEMENTS) == []


def test_has_11_dims_and_115_elements():
    data = load_json(ELEMENTS)
    ids = [d["id"] for d in data["dimensions"]]
    assert ids == DIMS
    total = sum(len(d["elements"]) for d in data["dimensions"])
    assert total == 115


def test_detects_missing_dimension(tmp_path):
    data = load_json(ELEMENTS)
    data["dimensions"] = data["dimensions"][:-1]
    p = tmp_path / "broken.json"
    p.write_text(json.dumps(data))
    assert validate_elements(p) != []
