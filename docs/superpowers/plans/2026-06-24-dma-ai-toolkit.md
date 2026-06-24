# dma-ai-toolkit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `VoidChecksum/dma-ai-toolkit` as a separate source-grounded AI toolkit for authorized DMALibrary-based DMA development and reverse-engineering workflows.

**Architecture:** Keep the repo documentation-first like `pcx-ai-toolkit`: context packs and skills define the agent contract, small Python tools extract and validate DMALibrary API usage, and tiny C++ templates demonstrate non-target-specific structure. DMALibrary is an optional submodule under `third_party/DMALibrary`; generated indexes record provenance instead of vendoring source.

**Tech Stack:** Python 3.10+ stdlib, pytest, GitHub Actions, C++17 templates, optional git submodule to `Metick/DMALibrary`.

---

## File Structure

Create these files:

```text
README.md
LICENSE
.gitignore
pyproject.toml
.github/workflows/ci.yml
docs/AI_AGENT_OPERATING_MANUAL.md
docs/llms-dma.md
docs/dmalibrary/api-reference.md
docs/dmalibrary/memory.md
docs/reverse-engineering/evidence-log.md
docs/reverse-engineering/triage-workflow.md
knowledge/unsupported-symbols.json
knowledge/pitfalls.md
tools/extract-dmalibrary-api.py
tools/validate-cpp-answer.py
tools/check-doc-drift.py
tools/build-provenance.py
tests/test_extract_dmalibrary_api.py
tests/test_validate_cpp_answer.py
tests/test_check_doc_drift.py
templates/minimal-dma-client/README.md
templates/minimal-dma-client/main.cpp
templates/scatter-read-example/README.md
templates/scatter-read-example/main.cpp
.claude/skills/dma-coding-discipline/SKILL.md
.claude/skills/dma-re-discipline/SKILL.md
.claude/skills/dmalibrary-api-lookup/SKILL.md
```

Generated during implementation:

```text
knowledge/dmalibrary-api-index.json
knowledge/provenance.json
third_party/DMALibrary/    # optional git submodule
```

---

### Task 1: Repository Skeleton

**Files:**
- Create: `README.md`
- Create: `LICENSE`
- Create: `.gitignore`
- Create: `pyproject.toml`

- [ ] **Step 1: Create README**

Write `README.md`:

```markdown
# dma-ai-toolkit

Source-grounded AI toolkit for authorized DMA software development and reverse-engineering workflows using [Metick/DMALibrary](https://github.com/Metick/DMALibrary).

## What This Is

`dma-ai-toolkit` teaches agents how to use DMALibrary from verified source, not guessed APIs. It provides context packs, API indexes, validators, templates, and agent skills.

## What This Is Not

This is not a target-specific offset pack, anti-cheat bypass guide, or turnkey cheating application. Use it only on owned systems, labs, and authorized research targets.

## AI Start Here

1. Read `docs/AI_AGENT_OPERATING_MANUAL.md`.
2. Read `docs/llms-dma.md`.
3. Verify every DMALibrary symbol against `knowledge/dmalibrary-api-index.json`.
4. For reverse-engineering work, keep evidence in `docs/reverse-engineering/evidence-log.md` format.
5. Run `python tools/validate-cpp-answer.py <file>` before trusting generated answers or snippets.

## Optional DMALibrary Source

DMALibrary is an optional submodule:

```bash
git submodule add https://github.com/Metick/DMALibrary third_party/DMALibrary
git submodule update --init --recursive
```

The toolkit records source provenance in `knowledge/provenance.json`.

## Quick Checks

```bash
python -m pytest
python tools/validate-cpp-answer.py README.md
```

## License

MIT. DMALibrary is MIT licensed by its upstream project.
```

- [ ] **Step 2: Create license**

Write `LICENSE`:

```text
MIT License

Copyright (c) 2026 VoidChecksum

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 3: Create gitignore**

Write `.gitignore`:

```gitignore
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
dist/
build/
*.egg-info/
.DS_Store
.worktrees/
```

- [ ] **Step 4: Create pytest config**

Write `pyproject.toml`:

```toml
[project]
name = "dma-ai-toolkit"
version = "0.1.0"
description = "Source-grounded AI toolkit for authorized DMALibrary workflows"
requires-python = ">=3.10"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
```

- [ ] **Step 5: Run metadata check**

Run:

```bash
python -m pytest --version
```

Expected: command prints pytest version.

- [ ] **Step 6: Commit**

```bash
git add README.md LICENSE .gitignore pyproject.toml
git commit -m "chore: add repository skeleton"
```

---

### Task 2: DMALibrary API Extractor

**Files:**
- Create: `tools/extract-dmalibrary-api.py`
- Create: `tests/test_extract_dmalibrary_api.py`
- Generate: `knowledge/dmalibrary-api-index.json`

- [ ] **Step 1: Write failing extractor tests**

Write `tests/test_extract_dmalibrary_api.py`:

```python
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "extract-dmalibrary-api.py"

spec = importlib.util.spec_from_file_location("extract_dmalibrary_api", MODULE_PATH)
extractor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extractor)


def test_extracts_class_methods_from_header(tmp_path):
    header = tmp_path / "Memory.h"
    header.write_text(
        """
class Memory
{
public:
    bool Init(std::string process_name, bool memMap = true, bool debug = false);
    template <typename T>
    T Read(uint64_t address);
    bool Read(uintptr_t address, void* buffer, size_t size) const;
};
""".strip()
    )

    index = extractor.build_index(tmp_path)

    assert index["source"] == "Metick/DMALibrary"
    symbols = {item["name"]: item for item in index["symbols"]}
    assert symbols["Memory::Init"]["kind"] == "method"
    assert symbols["Memory::Read"]["class"] == "Memory"
    assert "uint64_t address" in symbols["Memory::Read"]["signature"]


def test_cli_writes_json(tmp_path):
    source = tmp_path / "src"
    source.mkdir()
    (source / "Memory.h").write_text("class Memory { public: bool FixCr3(); };\n")
    output = tmp_path / "index.json"

    extractor.main([str(source), "--output", str(output)])

    data = json.loads(output.read_text())
    assert data["symbols"][0]["name"] == "Memory::FixCr3"
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
python -m pytest tests/test_extract_dmalibrary_api.py -v
```

Expected: FAIL because `tools/extract-dmalibrary-api.py` does not exist.

- [ ] **Step 3: Implement extractor**

Write `tools/extract-dmalibrary-api.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

METHOD_RE = re.compile(
    r"^(?P<prefix>(?:static\s+)?(?:inline\s+)?(?:virtual\s+)?)"
    r"(?P<return>[A-Za-z_][\w:<>,\s*&]+?)\s+"
    r"(?P<name>[A-Za-z_]\w*)\s*\((?P<params>[^;{}]*)\)"
    r"(?P<suffix>\s*(?:const)?)\s*(?:;|\{)"
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

    for line_no, raw in enumerate(path.read_text(errors="ignore").splitlines(), start=1):
        line = clean(raw)
        if not line or line.startswith("//"):
            continue

        class_match = CLASS_RE.match(line)
        if class_match:
            current_class = class_match.group("name")
            access = "private"
            symbols.append(
                {
                    "name": current_class,
                    "kind": "class",
                    "class": None,
                    "signature": line,
                    "file": str(path.relative_to(root)),
                    "line": line_no,
                    "access": None,
                }
            )
            continue

        access_match = ACCESS_RE.match(line)
        if access_match:
            access = access_match.group(1)
            continue

        if line.startswith("template"):
            pending_template = line + " "
            continue

        method_match = METHOD_RE.match(line)
        if current_class and method_match:
            method_name = method_match.group("name")
            signature = pending_template + line.rstrip("{")
            pending_template = ""
            symbols.append(
                {
                    "name": f"{current_class}::{method_name}",
                    "kind": "method",
                    "class": current_class,
                    "signature": signature.rstrip(";"),
                    "file": str(path.relative_to(root)),
                    "line": line_no,
                    "access": access,
                }
            )

    return symbols


def build_index(source_root: str | Path) -> dict:
    root = Path(source_root)
    symbols: list[dict] = []
    for header in iter_headers(root):
        symbols.extend(extract_file(header, root))
    return {
        "source": "Metick/DMALibrary",
        "schema": 1,
        "symbols": sorted(symbols, key=lambda item: (item["file"], item["line"], item["name"])),
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
```

- [ ] **Step 4: Run extractor tests**

Run:

```bash
python -m pytest tests/test_extract_dmalibrary_api.py -v
```

Expected: PASS.

- [ ] **Step 5: Generate API index when submodule exists**

Run:

```bash
python tools/extract-dmalibrary-api.py third_party/DMALibrary --output knowledge/dmalibrary-api-index.json
```

Expected when submodule exists: `knowledge/dmalibrary-api-index.json` contains `Memory::Init`, `Memory::Read`, and `Memory::Write` symbols.

- [ ] **Step 6: Commit**

```bash
git add tools/extract-dmalibrary-api.py tests/test_extract_dmalibrary_api.py knowledge/dmalibrary-api-index.json
git commit -m "feat: add dmalibrary api extractor"
```

---

### Task 3: Answer Validator

**Files:**
- Create: `tools/validate-cpp-answer.py`
- Create: `tests/test_validate_cpp_answer.py`
- Create: `knowledge/unsupported-symbols.json`

- [ ] **Step 1: Create unsupported symbol list**

Write `knowledge/unsupported-symbols.json`:

```json
{
  "schema": 1,
  "symbols": [
    "DMA::Read",
    "DMA::Write",
    "mem.ReadString",
    "Memory::ReadString",
    "Memory::GetModuleBase",
    "draw_esp",
    "get_offsets"
  ]
}
```

- [ ] **Step 2: Write failing validator tests**

Write `tests/test_validate_cpp_answer.py`:

```python
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "validate-cpp-answer.py"

spec = importlib.util.spec_from_file_location("validate_cpp_answer", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def make_index(tmp_path):
    index = tmp_path / "index.json"
    index.write_text(json.dumps({"symbols": [{"name": "Memory::Read"}, {"name": "Memory::Init"}]}))
    unsupported = tmp_path / "unsupported.json"
    unsupported.write_text(json.dumps({"symbols": ["Memory::ReadString", "DMA::Read"]}))
    return index, unsupported


def test_rejects_unsupported_symbol(tmp_path):
    index, unsupported = make_index(tmp_path)
    answer = tmp_path / "answer.md"
    answer.write_text("```cpp\nauto name = mem.ReadString(addr);\n```\n")

    result = validator.validate(answer, index, unsupported)

    assert not result.ok
    assert "Memory::ReadString" in result.errors[0]


def test_accepts_documented_symbol(tmp_path):
    index, unsupported = make_index(tmp_path)
    answer = tmp_path / "answer.md"
    answer.write_text("```cpp\nauto value = mem.Read<int>(addr);\n```\n")

    result = validator.validate(answer, index, unsupported)

    assert result.ok
    assert result.errors == []
```

- [ ] **Step 3: Run tests to verify failure**

Run:

```bash
python -m pytest tests/test_validate_cpp_answer.py -v
```

Expected: FAIL because validator file does not exist.

- [ ] **Step 4: Implement validator**

Write `tools/validate-cpp-answer.py`:

```python
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
        bare = symbol.split("::")[-1]
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
```

- [ ] **Step 5: Run validator tests**

Run:

```bash
python -m pytest tests/test_validate_cpp_answer.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add knowledge/unsupported-symbols.json tools/validate-cpp-answer.py tests/test_validate_cpp_answer.py
git commit -m "feat: add dmalibrary answer validator"
```

---

### Task 4: Provenance and Drift Checks

**Files:**
- Create: `tools/build-provenance.py`
- Create: `tools/check-doc-drift.py`
- Create: `tests/test_check_doc_drift.py`
- Generate: `knowledge/provenance.json`

- [ ] **Step 1: Write drift tests**

Write `tests/test_check_doc_drift.py`:

```python
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check-doc-drift.py"

spec = importlib.util.spec_from_file_location("check_doc_drift", MODULE_PATH)
drift = importlib.util.module_from_spec(spec)
spec.loader.exec_module(drift)


def test_detects_matching_commit(tmp_path):
    provenance = tmp_path / "provenance.json"
    provenance.write_text(json.dumps({"dmalibrary_commit": "abc123"}))
    commit = tmp_path / "commit.txt"
    commit.write_text("abc123\n")

    assert drift.check(provenance, commit).ok


def test_detects_drift(tmp_path):
    provenance = tmp_path / "provenance.json"
    provenance.write_text(json.dumps({"dmalibrary_commit": "abc123"}))
    commit = tmp_path / "commit.txt"
    commit.write_text("def456\n")

    result = drift.check(provenance, commit)

    assert not result.ok
    assert "abc123" in result.message
    assert "def456" in result.message
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
python -m pytest tests/test_check_doc_drift.py -v
```

Expected: FAIL because `tools/check-doc-drift.py` does not exist.

- [ ] **Step 3: Implement provenance builder**

Write `tools/build-provenance.py`:

```python
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
```

- [ ] **Step 4: Implement drift checker**

Write `tools/check-doc-drift.py`:

```python
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
```

- [ ] **Step 5: Run drift tests**

Run:

```bash
python -m pytest tests/test_check_doc_drift.py -v
```

Expected: PASS.

- [ ] **Step 6: Add optional submodule and generate provenance**

Run:

```bash
git submodule add https://github.com/Metick/DMALibrary third_party/DMALibrary
python tools/build-provenance.py --submodule third_party/DMALibrary --output knowledge/provenance.json
python tools/check-doc-drift.py
```

Expected: drift checker prints `DMALibrary provenance current: <commit>` and exits 0.

- [ ] **Step 7: Commit**

```bash
git add .gitmodules third_party/DMALibrary tools/build-provenance.py tools/check-doc-drift.py tests/test_check_doc_drift.py knowledge/provenance.json
git commit -m "feat: track dmalibrary provenance"
```

---

### Task 5: Agent Documentation

**Files:**
- Create: `docs/AI_AGENT_OPERATING_MANUAL.md`
- Create: `docs/llms-dma.md`
- Create: `docs/dmalibrary/api-reference.md`
- Create: `docs/dmalibrary/memory.md`
- Create: `docs/reverse-engineering/evidence-log.md`
- Create: `docs/reverse-engineering/triage-workflow.md`
- Create: `knowledge/pitfalls.md`

- [ ] **Step 1: Write operating manual**

Write `docs/AI_AGENT_OPERATING_MANUAL.md`:

```markdown
# DMA Agent Operating Manual

## Required Sequence

Before writing DMA C++ or reverse-engineering guidance:

1. Read `docs/llms-dma.md`.
2. Check `knowledge/dmalibrary-api-index.json` for each DMALibrary class or method.
3. Check `knowledge/unsupported-symbols.json` before using helper names from memory.
4. For reverse engineering, record observations using `docs/reverse-engineering/evidence-log.md`.
5. Run `python tools/validate-cpp-answer.py <answer-or-snippet-file>`.

## Scope Boundary

Allowed scope: owned systems, labs, and authorized research.

Disallowed repo content: target-specific offsets, anti-cheat bypass instructions, credential theft, persistence, stealth malware behavior, or turnkey cheating workflows.

## Source Rule

If the API index does not prove a DMALibrary symbol exists, do not use it. Say the symbol is unverified and point to the nearest documented API.
```

- [ ] **Step 2: Write compact context pack**

Write `docs/llms-dma.md`:

```markdown
# DMALibrary LLM Context Pack

## Project Contract

Use DMALibrary only through source-proven symbols in `knowledge/dmalibrary-api-index.json`.

## Core Concepts

- `Memory` owns DMA initialization and process context.
- `Memory::Init(process_name, memMap, debug)` initializes DMA for a process name.
- `Memory::Read<T>(address)` reads typed memory from an address.
- `Memory::Read(address, buffer, size)` reads into a caller-owned buffer.
- `Memory::Write(address, buffer, size)` writes caller-provided bytes.
- Scatter handles must be closed after use.
- Optional dependencies such as `FTD3XX.dll`, `leechcore.dll`, `vmm.dll`, `leechcore.lib`, and `vmm.lib` are supplied by the user.

## Required Checks

- Do not invent helpers like `ReadString`, `GetModuleBase`, or `DMA::Read`.
- Prefer explicit buffer reads for strings and structs.
- Keep templates non-target-specific.
- Keep reverse-engineering conclusions tied to evidence.
```

- [ ] **Step 3: Write API docs**

Write `docs/dmalibrary/api-reference.md`:

```markdown
# DMALibrary API Reference

This page summarizes symbols extracted from upstream source. The machine-readable contract is `knowledge/dmalibrary-api-index.json`.

## Memory

Primary class for DMA initialization, process/module lookup, memory reads/writes, scatter I/O, registry helpers, keyboard helpers, and shellcode helpers.

Use the index before relying on a method signature.
```

Write `docs/dmalibrary/memory.md`:

```markdown
# Memory Class Notes

## Initialization

`Memory::Init(std::string process_name, bool memMap = true, bool debug = false)` initializes DMA access for a process name.

## Reads

Use `Memory::Read<T>(uint64_t address)` for simple typed reads and `Memory::Read(uintptr_t address, void* buffer, size_t size)` for explicit buffers.

## Writes

Use writes only in authorized labs. Prefer examples that demonstrate validation and lifecycle, not target-specific mutation.

## Scatter I/O

Create a scatter handle, add requests, execute the requests, then close the handle.
```

- [ ] **Step 4: Write RE docs**

Write `docs/reverse-engineering/evidence-log.md`:

```markdown
# Reverse-Engineering Evidence Log Format

Use one entry per claim.

```text
Observation: exact thing seen
Source: file, tool, address, symbol, or command output
Interpretation: narrow conclusion supported by observation
Confidence: low | medium | high
Next check: smallest check that could disprove this interpretation
```
```

Write `docs/reverse-engineering/triage-workflow.md`:

```markdown
# Reverse-Engineering Triage Workflow

1. Identify file type, architecture, imports, strings, and symbols.
2. Record every claim in evidence-log format.
3. Prefer source headers and symbols before decompilation.
4. Use dynamic analysis only in a controlled lab.
5. Do not publish target-specific offsets in this repo.
```

- [ ] **Step 5: Write pitfalls**

Write `knowledge/pitfalls.md`:

```markdown
# DMALibrary Agent Pitfalls

- `Memory::ReadString` is not part of the verified API.
- `DMA::Read` is not part of the verified API.
- Scatter handles must be closed.
- Required DMA DLLs and libs are user-supplied.
- Reverse-engineering claims need evidence, not model memory.
```

- [ ] **Step 6: Commit**

```bash
git add docs knowledge/pitfalls.md
git commit -m "docs: add dma agent operating docs"
```

---

### Task 6: Agent Skills

**Files:**
- Create: `.claude/skills/dma-coding-discipline/SKILL.md`
- Create: `.claude/skills/dma-re-discipline/SKILL.md`
- Create: `.claude/skills/dmalibrary-api-lookup/SKILL.md`

- [ ] **Step 1: Create coding discipline skill**

Write `.claude/skills/dma-coding-discipline/SKILL.md`:

```markdown
---
name: dma-coding-discipline
description: Use before writing C++ code that uses DMALibrary or DMA helper APIs.
---

# DMA Coding Discipline

Before writing code:

1. Read `docs/AI_AGENT_OPERATING_MANUAL.md`.
2. Read `docs/llms-dma.md`.
3. Verify every DMALibrary symbol in `knowledge/dmalibrary-api-index.json`.
4. Avoid target-specific offsets and bypass instructions.
5. Validate final answer with `python tools/validate-cpp-answer.py <file>`.

Prefer minimal C++17 examples. Use explicit buffers for uncertain structures. Close scatter handles.
```

- [ ] **Step 2: Create RE discipline skill**

Write `.claude/skills/dma-re-discipline/SKILL.md`:

```markdown
---
name: dma-re-discipline
description: Use before reverse-engineering binaries, dumps, headers, or memory layouts for DMA workflows.
---

# DMA Reverse-Engineering Discipline

Use evidence-first workflow:

1. Record file/tool/source for each observation.
2. Separate observation from interpretation.
3. Keep confidence explicit.
4. Do not publish target-specific offsets in this repo.
5. Use `docs/reverse-engineering/evidence-log.md` format.
```

- [ ] **Step 3: Create API lookup skill**

Write `.claude/skills/dmalibrary-api-lookup/SKILL.md`:

```markdown
---
name: dmalibrary-api-lookup
description: Use when referencing a DMALibrary class, method, helper, or example.
---

# DMALibrary API Lookup

The API contract is `knowledge/dmalibrary-api-index.json`.

Rules:

- If a symbol is missing, do not use it.
- Check `knowledge/unsupported-symbols.json` for known hallucinations.
- Cite the indexed file and line when explaining an API.
- Prefer verified method names over familiar names from other DMA libraries.
```

- [ ] **Step 4: Commit**

```bash
git add .claude/skills
git commit -m "feat: add dma agent skills"
```

---

### Task 7: Minimal Templates

**Files:**
- Create: `templates/minimal-dma-client/README.md`
- Create: `templates/minimal-dma-client/main.cpp`
- Create: `templates/scatter-read-example/README.md`
- Create: `templates/scatter-read-example/main.cpp`

- [ ] **Step 1: Create minimal client template**

Write `templates/minimal-dma-client/README.md`:

```markdown
# Minimal DMA Client Template

Non-target-specific DMALibrary structure for authorized labs.

Build requirements are supplied by the user:

- DMALibrary include path
- LeechCore and MemProcFS libraries
- Required runtime DLLs
```

Write `templates/minimal-dma-client/main.cpp`:

```cpp
#include <DMALibrary/Memory/Memory.h>
#include <cstdint>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: minimal-dma-client <process.exe>\n";
        return 2;
    }

    Memory mem;
    const std::string process_name = argv[1];
    if (!mem.Init(process_name, true, false)) {
        std::cerr << "failed to initialize DMA for " << process_name << "\n";
        return 1;
    }

    const auto base = mem.GetBaseDaddy(process_name);
    if (base == 0) {
        std::cerr << "failed to resolve base address\n";
        return 1;
    }

    std::uint32_t mz = 0;
    if (!mem.Read(base, &mz, sizeof(mz))) {
        std::cerr << "failed to read base header\n";
        return 1;
    }

    std::cout << "base=0x" << std::hex << base << " header=0x" << mz << "\n";
    return 0;
}
```

- [ ] **Step 2: Create scatter example template**

Write `templates/scatter-read-example/README.md`:

```markdown
# Scatter Read Example

Shows scatter handle lifecycle only: create, add read request, execute, close.
```

Write `templates/scatter-read-example/main.cpp`:

```cpp
#include <DMALibrary/Memory/Memory.h>
#include <cstdint>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: scatter-read-example <process.exe>\n";
        return 2;
    }

    Memory mem;
    const std::string process_name = argv[1];
    if (!mem.Init(process_name, true, false)) {
        std::cerr << "failed to initialize DMA\n";
        return 1;
    }

    const auto base = mem.GetBaseDaddy(process_name);
    if (base == 0) {
        std::cerr << "failed to resolve base address\n";
        return 1;
    }

    std::uint32_t header = 0;
    auto handle = mem.CreateScatterHandle();
    mem.AddScatterReadRequest(handle, base, &header, sizeof(header));
    mem.ExecuteReadScatter(handle);
    mem.CloseScatterHandle(handle);

    std::cout << "header=0x" << std::hex << header << "\n";
    return 0;
}
```

- [ ] **Step 3: Validate template answer text**

Run:

```bash
python tools/validate-cpp-answer.py templates/minimal-dma-client/main.cpp
python tools/validate-cpp-answer.py templates/scatter-read-example/main.cpp
```

Expected: both print `PASS` after API index generation includes the referenced symbols.

- [ ] **Step 4: Commit**

```bash
git add templates
git commit -m "feat: add minimal dma templates"
```

---

### Task 8: CI

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create GitHub Actions workflow**

Write `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: false
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install test dependency
        run: python -m pip install pytest
      - name: Run tests
        run: python -m pytest -v
      - name: Validate README
        run: python tools/validate-cpp-answer.py README.md
```

- [ ] **Step 2: Run CI commands locally**

Run:

```bash
python -m pytest -v
python tools/validate-cpp-answer.py README.md
```

Expected: tests pass and validator prints `PASS`.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add test workflow"
```

---

### Task 9: Final Verification and GitHub Repo Creation

**Files:**
- Modify: none unless verification finds a defect

- [ ] **Step 1: Run full local verification**

Run:

```bash
python -m pytest -v
python tools/validate-cpp-answer.py README.md
python tools/check-doc-drift.py
```

Expected: all commands exit 0.

- [ ] **Step 2: Create separate GitHub repo**

Run:

```bash
gh repo create VoidChecksum/dma-ai-toolkit --public --source=. --remote=origin --push
```

Expected: GitHub creates `https://github.com/VoidChecksum/dma-ai-toolkit` and pushes `main`.

- [ ] **Step 3: Check remote repository view**

Run:

```bash
gh repo view VoidChecksum/dma-ai-toolkit --web=false
```

Expected: output describes `VoidChecksum/dma-ai-toolkit`, not `VoidChecksum/pcx-ai-toolkit`.

- [ ] **Step 4: Commit cleanup if verification changed files**

If verification generated or corrected files, run:

```bash
git add README.md docs knowledge tools tests templates .github .claude pyproject.toml
git commit -m "chore: finalize dma toolkit"
```

Expected: either a new cleanup commit is created or Git reports no changes to commit.
