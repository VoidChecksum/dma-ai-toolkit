from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "dma_core.py"

spec = importlib.util.spec_from_file_location("dma_core", MODULE_PATH)
dma_core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dma_core)


def test_api_lookup_returns_memory_read():
    result = dma_core.api_lookup(ROOT, "Memory::Read")

    assert result["name"] == "Memory::Read"
    assert result["source"] == "Metick/DMALibrary"
    assert result["kind"] in {"method", "function"}


def test_api_lookup_rejects_unknown_symbol():
    try:
        dma_core.api_lookup(ROOT, "Memory::ReadString")
    except KeyError as error:
        assert "Memory::ReadString" in str(error)
    else:
        raise AssertionError("expected KeyError")


def test_recommend_context_for_scatter_reliability_task():
    docs = dma_core.recommend_context("fix scatter read reliability and stale data", ROOT)

    assert "docs/llms-dma.md" in docs
    assert "docs/dmalibrary/scatter-cookbook.md" in docs
    assert "docs/dmalibrary/reliability.md" in docs
