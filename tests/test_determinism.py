import filecmp, pathlib, shutil, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))
import generate_site


def test_two_builds_are_identical(tmp_path):
    # No-commit proxy for the spec's rebuild-clean guard: building the same data
    # twice must yield byte-identical HTML, so committed output cannot drift.
    a, b = tmp_path / "a", tmp_path / "b"
    for d in (a, b):
        shutil.copytree(ROOT, d, ignore=shutil.ignore_patterns(".git", "tests", "__pycache__"))
        generate_site.build(d)
    for p in a.rglob("*.html"):
        rel = p.relative_to(a)
        assert filecmp.cmp(p, b / rel, shallow=False), f"non-deterministic: {rel}"
