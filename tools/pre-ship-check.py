#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    [sys.executable, "-m", "pytest", "-v"],
    [sys.executable, "tools/check-doc-drift.py"],
    [sys.executable, "tools/build-doc-index.py", "--check"],
    [sys.executable, "tools/validate-cpp-answer.py", "README.md"],
    [sys.executable, "tools/dma.py", "api", "Memory::Read"],
]


def main() -> int:
    for command in COMMANDS:
        print("$ " + " ".join(command))
        result = subprocess.run(command, cwd=ROOT)
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
