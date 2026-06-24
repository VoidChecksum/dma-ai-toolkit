#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

METHOD_CALL_RE = re.compile(r"\bmem\.(?P<name>[A-Za-z_]\w*)\s*(?:<[^>]+>)?\s*\(")


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]


def load_symbols(path: Path) -> set[str]:
    if not path.exists():
        return set()
    data = json.loads(path.read_text())
    return {item["name"] for item in data.get("symbols", []) if isinstance(item, dict) and "name" in item}


def load_unsupported(path: Path) -> set[str]:
    if not path.exists():
        return set()
    data = json.loads(path.read_text())
    return set(data.get("symbols", []))


def normalize_call(method: str) -> str:
    return f"Memory::{method}"


def validate(answer_path: str | Path, index_path: str | Path, unsupported_path: str | Path) -> ValidationResult:
    answer = Path(answer_path).read_text(errors="ignore")
    supported = load_symbols(Path(index_path))
    unsupported = load_unsupported(Path(unsupported_path))
    errors: list[str] = []

    for symbol in sorted(unsupported):
        bare = symbol.split("::")[-1].removeprefix("mem.")
        if symbol in answer or re.search(rf"\bmem\.{re.escape(bare)}\s*\(", answer):
            errors.append(f"unsupported symbol used: {symbol}")

    for match in METHOD_CALL_RE.finditer(answer):
        symbol = normalize_call(match.group("name"))
        if supported and symbol not in supported:
            errors.append(f"unverified DMALibrary symbol: {symbol}")

    return ValidationResult(ok=not errors, errors=errors)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Markdown/C++ answer against DMALibrary API index")
    parser.add_argument("answer")
    parser.add_argument("--index", default="knowledge/dmalibrary-api-index.json")
    parser.add_argument("--unsupported", default="knowledge/unsupported-symbols.json")
    args = parser.parse_args(argv)

    result = validate(args.answer, args.index, args.unsupported)
    if result.ok:
        print("PASS")
        return 0
    for error in result.errors:
        print(f"FAIL: {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
