#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import dma_core

ROOT = Path(__file__).resolve().parents[1]


def print_json(value) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Source-backed DMA agent runtime")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("overview")
    api = sub.add_parser("api")
    api.add_argument("symbol")
    ctx = sub.add_parser("recommend-context")
    ctx.add_argument("task")
    validate = sub.add_parser("validate-answer")
    validate.add_argument("path")
    sub.add_parser("list-docs")
    args = parser.parse_args(argv)

    try:
        if args.command == "overview":
            print_json(dma_core.overview(ROOT))
        elif args.command == "api":
            print_json(dma_core.api_lookup(ROOT, args.symbol))
        elif args.command == "recommend-context":
            for path in dma_core.recommend_context(args.task, ROOT):
                print(path)
        elif args.command == "validate-answer":
            return subprocess.run(
                [sys.executable, str(ROOT / "tools" / "validate-cpp-answer.py"), args.path],
                cwd=ROOT,
            ).returncode
        elif args.command == "list-docs":
            print_json(dma_core.list_docs(ROOT))
        return 0
    except Exception as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
