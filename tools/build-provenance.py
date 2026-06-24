#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def git_commit(path: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=path, text=True).strip()


def build(submodule: Path) -> dict:
    return {
        "schema": 1,
        "source": "Metick/DMALibrary",
        "source_url": "https://github.com/Metick/DMALibrary",
        "dmalibrary_commit": git_commit(submodule),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "license": "MIT",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record DMALibrary provenance")
    parser.add_argument("--submodule", default="third_party/DMALibrary")
    parser.add_argument("--output", default="knowledge/provenance.json")
    args = parser.parse_args(argv)

    data = build(Path(args.submodule))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
