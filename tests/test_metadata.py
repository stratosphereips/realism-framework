import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_required_files_exist():
    for f in ["LICENSE", "LICENSE-data", "CITATION.cff", ".zenodo.json", "README.md"]:
        assert (ROOT / f).is_file(), f"missing {f}"


def test_zenodo_json_parses_and_is_ccby():
    z = json.loads((ROOT / ".zenodo.json").read_text())
    assert z["license"] == "CC-BY-4.0"
    assert z["creators"]


def test_citation_is_cff_1_2():
    text = (ROOT / "CITATION.cff").read_text()
    assert "cff-version: 1.2.0" in text
