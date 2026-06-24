#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DriftResult:
    ok: bool
    message: str


def current_commit_from_git(submodule: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=submodule, text=True).strip()


def check(provenance_path: str | Path, current_commit_path: str | Path) -> DriftResult:
    recorded = json.loads(Path(provenance_path).read_text())["dmalibrary_commit"]
    current = Path(current_commit_path).read_text().strip()
    if recorded == current:
        return DriftResult(True, f"DMALibrary provenance current: {current}")
    return DriftResult(False, f"DMALibrary drift: provenance={recorded} current={current}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check DMALibrary provenance drift")
    parser.add_argument("--provenance", default="knowledge/provenance.json")
    parser.add_argument("--submodule", default="third_party/DMALibrary")
    args = parser.parse_args(argv)

    temp = Path(".dmalibrary-current-commit")
    temp.write_text(current_commit_from_git(Path(args.submodule)) + "\n")
    try:
        result = check(args.provenance, temp)
    finally:
        temp.unlink(missing_ok=True)
    print(result.message)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
