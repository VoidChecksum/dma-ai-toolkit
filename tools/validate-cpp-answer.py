#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

METHOD_CALL_RE = re.compile(r"\bmem\.(?P<name>[A-Za-z_]\w*)\s*(?:<[^>]+>)?\s*\(")
OFFSET_RE = re.compile(r"\b0x[0-9A-Fa-f]{4,}\b")
UNSAFE_GUARANTEE_RE = re.compile(r"\b(undetected|works on\s+(?:EAC|FACEIT|Vanguard)|bypass(?:es|ed|ing)?)\b", re.IGNORECASE)
WARNING_PREFIX_RE = re.compile(r"\b(do not|don't|never|avoid|no|not)\b", re.IGNORECASE)



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


def check_offset_dump(answer: str) -> list[str]:
    offsets = OFFSET_RE.findall(answer)
    if len(offsets) >= 6:
        return [f"possible target-specific offset dump: {len(offsets)} hex constants"]
    risky_names = ("offsets.json", "client_dll.json", "dump.cs")
    if any(name in answer for name in risky_names):
        return ["possible target-specific offset dump: offset artifact name present"]
    return []


def check_unsafe_guarantees(answer: str) -> list[str]:
    errors: list[str] = []
    for match in UNSAFE_GUARANTEE_RE.finditer(answer):
        sentence_start = max(answer.rfind(".", 0, match.start()), answer.rfind("\n", 0, match.start())) + 1
        context = answer[sentence_start:match.start()]
        if WARNING_PREFIX_RE.search(context):
            continue
        errors.append(f"unsafe guarantee language: {match.group(0)}")
    return errors


def validate(answer_path: str | Path, index_path: str | Path, unsupported_path: str | Path) -> ValidationResult:
    answer = Path(answer_path).read_text(errors="ignore")
    supported = load_symbols(Path(index_path))
    unsupported = load_unsupported(Path(unsupported_path))
    errors: list[str] = []

    for symbol in sorted(unsupported):
        if symbol.startswith("mem."):
            pattern = rf"\b{re.escape(symbol)}\s*\("
        elif symbol.startswith("Memory::"):
            pattern = rf"\bmem\.{re.escape(symbol.split('::', 1)[1])}\s*\("
        else:
            pattern = rf"\b{re.escape(symbol)}\b"
        if symbol in answer or re.search(pattern, answer):
            errors.append(f"unsupported symbol used: {symbol}")

    errors.extend(check_offset_dump(answer))
    errors.extend(check_unsafe_guarantees(answer))

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
