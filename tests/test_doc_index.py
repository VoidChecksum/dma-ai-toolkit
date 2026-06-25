import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "build-doc-index.py"


def test_build_doc_index_creates_counts_and_index():
    result = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, text=True, capture_output=True)

    assert result.returncode == 0, result.stderr
    counts = json.loads((ROOT / "docs" / "COUNTS.json").read_text())
    index = (ROOT / "docs" / "INDEX.md").read_text()
    assert counts["docs"] >= 8
    assert counts["api_symbols"] >= 10
    assert counts["mcp_tools"] == 6
    assert "docs/llms-dma.md" in index


def test_build_doc_index_check_mode_passes_after_generation():
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    result = subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=ROOT, text=True, capture_output=True)

    assert result.returncode == 0, result.stderr
