import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check-doc-drift.py"

spec = importlib.util.spec_from_file_location("check_doc_drift", MODULE_PATH)
drift = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = drift
spec.loader.exec_module(drift)


def test_detects_matching_commit(tmp_path):
    provenance = tmp_path / "provenance.json"
    provenance.write_text(json.dumps({"dmalibrary_commit": "abc123"}))
    commit = tmp_path / "commit.txt"
    commit.write_text("abc123\n")

    assert drift.check(provenance, commit).ok


def test_detects_drift(tmp_path):
    provenance = tmp_path / "provenance.json"
    provenance.write_text(json.dumps({"dmalibrary_commit": "abc123"}))
    commit = tmp_path / "commit.txt"
    commit.write_text("def456\n")

    result = drift.check(provenance, commit)

    assert not result.ok
    assert "abc123" in result.message
    assert "def456" in result.message
