import math, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))
import radar


def test_requirement_values():
    assert radar.level_value("C") == 100
    assert radar.level_value("U") == 50
    assert radar.level_value("-") == 0


def test_coverage_values_and_unknown_is_not_zero():
    assert radar.code_value("F") == 100
    assert radar.code_value("P") == 50
    assert radar.code_value("A") == 0
    # U must be distinct from A (Absent), not silently 0
    u = radar.code_value("U")
    assert isinstance(u, float) and math.isnan(u)
