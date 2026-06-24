#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

METHOD_RE = re.compile(
    r"^(?P<prefix>(?:static\s+)?(?:inline\s+)?(?:virtual\s+)?)"
    r"(?P<return>[A-Za-z_][\w:<>,\s*&]*?)\s+"
    r"(?P<name>[A-Za-z_]\w*)\s*\((?P<params>[^;{}]*)\)"
    r"(?P<suffix>\s*(?:const)?)\s*(?:;|\{).*$"
)
CLASS_RE = re.compile(r"^class\s+(?P<name>[A-Za-z_]\w*)\b")
ACCESS_RE = re.compile(r"^(public|private|protected):")


def clean(line: str) -> str:
    return " ".join(line.strip().split())


def iter_headers(root: Path):
    yield from sorted(root.rglob("*.h"))
    yield from sorted(root.rglob("*.hpp"))


def extract_file(path: Path, root: Path) -> list[dict]:
    symbols: list[dict] = []
    current_class: str | None = None
    access = "private"
    pending_template = ""
    seen_methods: set[str] = set()

    for line_no, raw in enumerate(path.read_text(errors="ignore").splitlines(), start=1):
        line = clean(raw)
        if not line or line.startswith("//"):
            continue

        class_match = CLASS_RE.match(line)
        if class_match:
            current_class = class_match.group("name")
            access = "private"
            symbols.append({
                "name": current_class,
                "kind": "class",
                "class": None,
                "signature": line,
                "file": str(path.relative_to(root)),
                "line": line_no,
                "access": None,
            })
            if "{" not in line:
                continue
            line = clean(line.split("{", 1)[1])

        access_match = ACCESS_RE.match(line)
        if access_match:
            access = access_match.group(1)
            line = clean(line.split(":", 1)[1])
            if not line:
                continue

        if line.startswith("template"):
            pending_template = line + " "
            continue

        method_match = METHOD_RE.match(line)
        if current_class and method_match:
            method_name = method_match.group("name")
            full_name = f"{current_class}::{method_name}"
            if full_name in seen_methods:
                pending_template = ""
                continue
            seen_methods.add(full_name)
            signature = (pending_template + line.rstrip("{")).rstrip(";")
            pending_template = ""
            symbols.append({
                "name": full_name,
                "kind": "method",
                "class": current_class,
                "signature": signature,
                "file": str(path.relative_to(root)),
                "line": line_no,
                "access": access,
            })

    return symbols


def build_index(source_root: str | Path) -> dict:
    root = Path(source_root)
    symbols: list[dict] = []
    for header in iter_headers(root):
        symbols.extend(extract_file(header, root))
    return {
        "source": "Metick/DMALibrary",
        "schema": 1,
        "symbols": sorted(symbols, key=lambda item: (item["kind"] != "method", item["file"], item["line"], item["name"])),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract a compact DMALibrary API index")
    parser.add_argument("source", help="Path to DMALibrary checkout")
    parser.add_argument("--output", default="knowledge/dmalibrary-api-index.json")
    args = parser.parse_args(argv)

    data = build_index(args.source)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
