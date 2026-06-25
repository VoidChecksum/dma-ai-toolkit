import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "dma.py"


def run_cli(*args):
    return subprocess.run([sys.executable, str(CLI), *args], cwd=ROOT, text=True, capture_output=True)


def test_cli_api_lookup_returns_json():
    result = run_cli("api", "Memory::Read")

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["name"] == "Memory::Read"


def test_cli_unknown_api_fails():
    result = run_cli("api", "Memory::ReadString")

    assert result.returncode == 1
    assert "unverified" in result.stderr


def test_cli_recommend_context_mentions_scatter_doc():
    result = run_cli("recommend-context", "scatter reliability")

    assert result.returncode == 0
    assert "docs/dmalibrary/scatter-cookbook.md" in result.stdout
