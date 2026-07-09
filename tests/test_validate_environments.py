import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))
from validate_data import validate_environments, load_json

ENV = ROOT / "data" / "environments.json"


def test_real_environments_valid():
    assert validate_environments(ENV) == []


def test_has_13_evaluated_environments():
    # 18 in the main-repo docs minus 5 unlinked (paper-only) that are not evaluated here.
    assert len(load_json(ENV)["environments"]) == 13


def test_goad_present_with_scores():
    envs = load_json(ENV)["environments"]
    assert "goad" in envs and set(envs["goad"]["scores"]) == {f"D{i}" for i in range(1, 12)}
