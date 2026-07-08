import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
HTML = (ROOT / "scorecard.html").read_text()


def test_fetches_all_three_data_files():
    for f in ["data/dimension_elements.json", "data/use_cases.json", "data/environments.json"]:
        assert f in HTML


def test_imports_scoring_module_not_inlined():
    assert "assets/scorecard_scoring.js" in HTML   # scoring is imported, not inlined
    assert "const DATA = {" not in HTML            # inlined data removed
    assert "function ucVerdict" not in HTML        # scoring functions no longer inlined


def test_has_file_protocol_bootstrap():
    assert 'location.protocol === "file:"' in HTML
