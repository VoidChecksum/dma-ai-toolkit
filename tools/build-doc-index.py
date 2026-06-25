#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def title_for(path: Path) -> str:
    for line in path.read_text(errors="ignore").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.name


def build_index() -> str:
    rows = []
    for path in sorted((ROOT / "docs").rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        rows.append(f"| `{rel}` | {title_for(path)} |")
    return "# DMA Toolkit Documentation Index\n\n| Path | Title |\n|---|---|\n" + "\n".join(rows) + "\n"


def count_lines(paths: list[Path]) -> int:
    return sum(len(path.read_text(errors="ignore").splitlines()) for path in paths)


def build_counts() -> dict:
    docs = sorted((ROOT / "docs").rglob("*.md"))
    skills = sorted((ROOT / ".claude" / "skills").glob("*/SKILL.md")) if (ROOT / ".claude" / "skills").exists() else []
    templates = sorted((ROOT / "templates").glob("*/README.md")) if (ROOT / "templates").exists() else []
    api = json.loads((ROOT / "knowledge" / "dmalibrary-api-index.json").read_text())
    sources = json.loads((ROOT / "knowledge" / "research-sources.json").read_text())
    return {
        "docs": len(docs),
        "doc_lines": count_lines(docs),
        "skills": len(skills),
        "templates": len(templates),
        "api_symbols": len(api.get("symbols", [])),
        "research_sources": len(sources.get("sources", [])),
        "mcp_tools": 6,
        "native_tools": 5,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build docs index and counts")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    index_path = ROOT / "docs" / "INDEX.md"
    counts_path = ROOT / "docs" / "COUNTS.json"
    index = build_index()
    if not args.check:
        index_path.write_text(index)
    counts = json.dumps(build_counts(), indent=2, sort_keys=True) + "\n"
    if args.check:
        if not index_path.exists() or index_path.read_text() != index:
            raise SystemExit("docs/INDEX.md is stale; run tools/build-doc-index.py")
        if not counts_path.exists() or counts_path.read_text() != counts:
            raise SystemExit("docs/COUNTS.json is stale; run tools/build-doc-index.py")
        return 0
    counts_path.write_text(counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
