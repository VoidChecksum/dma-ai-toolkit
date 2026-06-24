import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_research_sources_have_required_ids_and_urls():
    data = json.loads((ROOT / "knowledge" / "research-sources.json").read_text())
    assert data["schema"] == 1
    ids = {source["id"] for source in data["sources"]}
    assert {
        "github-pcileech",
        "github-memprocfs",
        "github-orpheus",
        "github-cs2-dma",
        "github-dma-mouse-control",
        "github-volkdma",
        "uc-dmalibrary-thread",
        "uc-vmmsharp-wrapper-thread",
        "uc-eft-dma-radar-lite",
        "uc-cr3-physical-memory-thread",
    }.issubset(ids)
    for source in data["sources"]:
        assert source["url"].startswith("https://")
        assert source["facts"]
