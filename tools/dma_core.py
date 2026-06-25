from __future__ import annotations

import json
from pathlib import Path

CORE_DOCS = [
    "docs/AI_AGENT_OPERATING_MANUAL.md",
    "docs/llms-dma.md",
]

KEYWORD_DOCS = [
    (("scatter", "batch"), "docs/dmalibrary/scatter-cookbook.md"),
    (("signature", "sig", "findsignature", "pattern"), "docs/dmalibrary/signature-scan-cookbook.md"),
    (("reliability", "stale", "health", "cr3", "base"), "docs/dmalibrary/reliability.md"),
    (("forum", "unknowncheats", "uc"), "docs/research/unknowncheats-dma-lessons.md"),
    (("ecosystem", "github", "pcileech", "memprocfs"), "docs/research/github-dma-ecosystem.md"),
]


def load_json(root: Path, relative: str) -> dict:
    return json.loads((root / relative).read_text())


def api_lookup(root: Path, symbol: str) -> dict:
    data = load_json(root, "knowledge/dmalibrary-api-index.json")
    for item in data.get("symbols", []):
        if item.get("name") == symbol:
            out = dict(item)
            out.setdefault("source", data.get("source", "Metick/DMALibrary"))
            return out
    raise KeyError(f"unverified DMALibrary symbol: {symbol}")


def recommend_context(task: str, root: Path) -> list[str]:
    text = task.lower()
    docs = list(CORE_DOCS)
    for keywords, path in KEYWORD_DOCS:
        if any(keyword in text for keyword in keywords):
            docs.append(path)
    existing: list[str] = []
    for doc in docs:
        if doc not in existing and (root / doc).exists():
            existing.append(doc)
    return existing


def overview(root: Path) -> dict:
    return {
        "name": "dma-ai-toolkit",
        "scope": "authorized DMA software development and reverse-engineering workflows",
        "not": "target-specific offsets, bypass recipes, or turnkey cheating applications",
        "start_here": CORE_DOCS,
        "api_index": "knowledge/dmalibrary-api-index.json",
        "validator": "tools/validate-cpp-answer.py",
    }


def list_docs(root: Path) -> list[dict]:
    docs = []
    for path in sorted((root / "docs").rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        title = rel
        for line in path.read_text(errors="ignore").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        docs.append({"path": rel, "title": title})
    return docs


def read_repo_file(root: Path, relative: str) -> str:
    path = (root / relative).resolve()
    root_resolved = root.resolve()
    if root_resolved not in path.parents and path != root_resolved:
        raise ValueError("path escapes repository")
    return path.read_text(errors="ignore")
