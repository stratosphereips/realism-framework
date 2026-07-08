import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))
from validate_data import validate_dimensions_meta

DJ = ROOT / "data" / "dimensions.json"


def test_real_dimensions_meta_valid():
    assert validate_dimensions_meta(DJ) == []


def test_groups_cover_all_11_dimensions_once():
    d = json.loads(DJ.read_text())
    covered = [x for g in d["groups"] for x in g["dims"]]
    assert len(covered) == 11
    assert set(covered) == {f"D{i}" for i in range(1, 12)}
