import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))
from validate_data import validate_environments, load_json

ENV = ROOT / "data" / "environments.json"


def test_real_environments_valid():
    assert validate_environments(ENV) == []


def test_has_12_evaluated_environments():
    # 18 in the main-repo docs minus 5 unlinked (paper-only) minus CALDERA (adversary-emulation
    # tooling, not an environment an agent is evaluated in), all excluded here.
    assert len(load_json(ENV)["environments"]) == 12


def test_goad_present_with_scores():
    envs = load_json(ENV)["environments"]
    assert "goad" in envs and set(envs["goad"]["scores"]) == {f"D{i}" for i in range(1, 12)}
