import pathlib, shutil, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))
import generate_site


def test_build_produces_pages_and_passes_checks(tmp_path):
    work = tmp_path / "site"
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns(".git", "tests"))
    generate_site.build(work)
    assert (work / "index.html").is_file()
    assert (work / "use-cases" / "index.html").is_file()
    assert (work / "use-cases" / "UC-A1.html").is_file()
    assert (work / "environments" / "goad.html").is_file()
    assert list((work / "figures").glob("*.png"))
    assert generate_site.check_output(work) == []
