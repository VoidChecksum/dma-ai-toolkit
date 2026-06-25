# DMA Core Agent Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a PCX-style core agent runtime to `dma-ai-toolkit`: CLI, read-only MCP server, doc index/counts generator, pre-ship check, and README routing.

**Architecture:** Keep Python stdlib only. Put shared read/query logic in `tools/dma_core.py`, expose it through `tools/dma.py` and `mcp/dma_mcp.py`, and verify through pytest plus pre-ship checks.

**Tech Stack:** Python 3.10+ stdlib, pytest, JSON-RPC over stdio, Markdown docs, GitHub Actions.

---

## File Structure

Create:

```text
tools/dma_core.py                 Shared source-backed lookup and doc recommendation logic
tools/dma.py                      Human/agent CLI facade
mcp/dma_mcp.py                    Read-only MCP stdio server
tools/build-doc-index.py          Deterministic docs index and counts generator
tools/pre-ship-check.py           Local/CI pre-ship verification gate
tests/test_dma_cli.py             CLI behavior tests
tests/test_dma_core.py            Shared logic tests
tests/test_doc_index.py           Doc index/count generator tests
tests/test_dma_mcp.py             MCP JSON-RPC smoke tests
mcp/README.md                     MCP setup and tool list
```

Modify:

```text
README.md                         Add PCX-style quick decision, badges, MCP, anti-hallucination pipeline
.github/workflows/ci.yml          Run pre-ship check instead of raw pytest only
docs/llms-dma.md                  Mention CLI/MCP commands
```

Generated:

```text
docs/INDEX.md
docs/COUNTS.json
```

## Task 1: Shared Runtime Core

**Files:**
- Create: `tools/dma_core.py`
- Test: `tests/test_dma_core.py`

- [ ] **Step 1: Write failing core tests**

Create `tests/test_dma_core.py`:

```python
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "dma_core.py"

spec = importlib.util.spec_from_file_location("dma_core", MODULE_PATH)
dma_core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dma_core)


def test_api_lookup_returns_memory_read():
    result = dma_core.api_lookup(ROOT, "Memory::Read")

    assert result["name"] == "Memory::Read"
    assert result["source"] == "Metick/DMALibrary"
    assert result["kind"] in {"method", "function"}


def test_api_lookup_rejects_unknown_symbol():
    try:
        dma_core.api_lookup(ROOT, "Memory::ReadString")
    except KeyError as error:
        assert "Memory::ReadString" in str(error)
    else:
        raise AssertionError("expected KeyError")


def test_recommend_context_for_scatter_reliability_task():
    docs = dma_core.recommend_context("fix scatter read reliability and stale data", ROOT)

    assert "docs/llms-dma.md" in docs
    assert "docs/dmalibrary/scatter-cookbook.md" in docs
    assert "docs/dmalibrary/reliability.md" in docs
```

- [ ] **Step 2: Run failing tests**

Run:

```bash
uv run --with pytest pytest tests/test_dma_core.py -v
```

Expected: FAIL because `tools/dma_core.py` does not exist.

- [ ] **Step 3: Implement shared core**

Create `tools/dma_core.py`:

```python
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
    existing = []
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
```

- [ ] **Step 4: Run tests**

Run:

```bash
uv run --with pytest pytest tests/test_dma_core.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/dma_core.py tests/test_dma_core.py
git commit -m "feat: add dma runtime core"
```

## Task 2: CLI Facade

**Files:**
- Create: `tools/dma.py`
- Test: `tests/test_dma_cli.py`

- [ ] **Step 1: Write failing CLI tests**

Create `tests/test_dma_cli.py`:

```python
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "dma.py"


def run_cli(*args):
    return subprocess.run([sys.executable, str(CLI), *args], cwd=ROOT, text=True, capture_output=True)


def test_cli_api_lookup_returns_json():
    result = run_cli("api", "Memory::Read")

    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["name"] == "Memory::Read"


def test_cli_unknown_api_fails():
    result = run_cli("api", "Memory::ReadString")

    assert result.returncode == 1
    assert "unverified" in result.stderr


def test_cli_recommend_context_mentions_scatter_doc():
    result = run_cli("recommend-context", "scatter reliability")

    assert result.returncode == 0
    assert "docs/dmalibrary/scatter-cookbook.md" in result.stdout
```

- [ ] **Step 2: Run failing tests**

Run:

```bash
uv run --with pytest pytest tests/test_dma_cli.py -v
```

Expected: FAIL because `tools/dma.py` does not exist.

- [ ] **Step 3: Implement CLI**

Create `tools/dma.py`:

```python
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
            return subprocess.run([sys.executable, str(ROOT / "tools" / "validate-cpp-answer.py"), args.path], cwd=ROOT).returncode
        elif args.command == "list-docs":
            print_json(dma_core.list_docs(ROOT))
        return 0
    except Exception as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run CLI tests**

Run:

```bash
uv run --with pytest pytest tests/test_dma_cli.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/dma.py tests/test_dma_cli.py
git commit -m "feat: add dma agent cli"
```

## Task 3: Read-only MCP Server

**Files:**
- Create: `mcp/dma_mcp.py`
- Create: `mcp/README.md`
- Test: `tests/test_dma_mcp.py`

- [ ] **Step 1: Write failing MCP tests**

Create `tests/test_dma_mcp.py`:

```python
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp" / "dma_mcp.py"


def call_server(*messages):
    proc = subprocess.Popen([sys.executable, str(SERVER)], cwd=ROOT, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = []
    try:
        for message in messages:
            proc.stdin.write(json.dumps(message) + "\n")
            proc.stdin.flush()
            out.append(json.loads(proc.stdout.readline()))
    finally:
        proc.kill()
    return out


def test_mcp_lists_runtime_tools():
    responses = call_server({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    names = {tool["name"] for tool in responses[0]["result"]["tools"]}

    assert {"overview", "recommend_context", "api_lookup", "validate_answer", "get_file", "list_docs"}.issubset(names)


def test_mcp_api_lookup_returns_memory_read():
    responses = call_server({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "api_lookup", "arguments": {"symbol": "Memory::Read"}}})
    text = responses[0]["result"]["content"][0]["text"]
    data = json.loads(text)

    assert data["name"] == "Memory::Read"
```

- [ ] **Step 2: Run failing MCP tests**

Run:

```bash
uv run --with pytest pytest tests/test_dma_mcp.py -v
```

Expected: FAIL because `mcp/dma_mcp.py` does not exist.

- [ ] **Step 3: Implement MCP server**

Create `mcp/dma_mcp.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import dma_core

TOOLS = [
    {"name": "overview", "description": "Return DMA toolkit contract and start files", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "recommend_context", "description": "Recommend docs for a DMA task", "inputSchema": {"type": "object", "properties": {"task": {"type": "string"}}, "required": ["task"]}},
    {"name": "api_lookup", "description": "Look up a source-backed DMALibrary symbol", "inputSchema": {"type": "object", "properties": {"symbol": {"type": "string"}}, "required": ["symbol"]}},
    {"name": "validate_answer", "description": "Validate a Markdown/C++ answer file", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "get_file", "description": "Read a repository file", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "list_docs", "description": "List indexed docs", "inputSchema": {"type": "object", "properties": {}}},
]


def content(value) -> dict:
    text = value if isinstance(value, str) else json.dumps(value, indent=2, sort_keys=True)
    return {"content": [{"type": "text", "text": text}]}


def handle_call(name: str, args: dict) -> dict:
    if name == "overview":
        return content(dma_core.overview(ROOT))
    if name == "recommend_context":
        return content(dma_core.recommend_context(args["task"], ROOT))
    if name == "api_lookup":
        return content(dma_core.api_lookup(ROOT, args["symbol"]))
    if name == "validate_answer":
        result = subprocess.run([sys.executable, str(ROOT / "tools" / "validate-cpp-answer.py"), args["path"]], cwd=ROOT, text=True, capture_output=True)
        return content({"ok": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr})
    if name == "get_file":
        return content(dma_core.read_repo_file(ROOT, args["path"]))
    if name == "list_docs":
        return content(dma_core.list_docs(ROOT))
    raise ValueError(f"unknown tool: {name}")


def handle(message: dict) -> dict:
    method = message.get("method")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": message.get("id"), "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "dma-ai-toolkit", "version": "0.1.0"}}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": message.get("id"), "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = message.get("params", {})
        try:
            result = handle_call(params.get("name", ""), params.get("arguments", {}))
            return {"jsonrpc": "2.0", "id": message.get("id"), "result": result}
        except Exception as error:
            return {"jsonrpc": "2.0", "id": message.get("id"), "error": {"code": -32000, "message": str(error)}}
    return {"jsonrpc": "2.0", "id": message.get("id"), "error": {"code": -32601, "message": "method not found"}}


def main() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        print(json.dumps(handle(json.loads(line))), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Create `mcp/README.md`:

```markdown
# dma-ai-toolkit MCP

Read-only MCP server for source-backed DMALibrary agent workflows.

## Run

```bash
python mcp/dma_mcp.py
```

## Tools

- `overview`
- `recommend_context`
- `api_lookup`
- `validate_answer`
- `get_file`
- `list_docs`

The server does not write files, scan networks, or fetch remote targets.
```

- [ ] **Step 4: Run MCP tests**

Run:

```bash
uv run --with pytest pytest tests/test_dma_mcp.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add mcp/dma_mcp.py mcp/README.md tests/test_dma_mcp.py
git commit -m "feat: add dma mcp server"
```

## Task 4: Doc Index and Counts

**Files:**
- Create: `tools/build-doc-index.py`
- Test: `tests/test_doc_index.py`
- Generate: `docs/INDEX.md`, `docs/COUNTS.json`

- [ ] **Step 1: Write failing doc index tests**

Create `tests/test_doc_index.py`:

```python
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "build-doc-index.py"


def test_build_doc_index_creates_counts_and_index(tmp_path):
    result = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, text=True, capture_output=True)

    assert result.returncode == 0, result.stderr
    counts = json.loads((ROOT / "docs" / "COUNTS.json").read_text())
    index = (ROOT / "docs" / "INDEX.md").read_text()
    assert counts["docs"] >= 8
    assert counts["api_symbols"] >= 10
    assert counts["mcp_tools"] == 6
    assert "docs/llms-dma.md" in index


def test_build_doc_index_check_mode_passes_after_generation():
    subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True)
    result = subprocess.run([sys.executable, str(SCRIPT), "--check"], cwd=ROOT, text=True, capture_output=True)

    assert result.returncode == 0, result.stderr
```

- [ ] **Step 2: Run failing tests**

Run:

```bash
uv run --with pytest pytest tests/test_doc_index.py -v
```

Expected: FAIL because `tools/build-doc-index.py` does not exist.

- [ ] **Step 3: Implement generator**

Create `tools/build-doc-index.py`:

```python
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
    index = build_index()
    counts = json.dumps(build_counts(), indent=2, sort_keys=True) + "\n"
    index_path = ROOT / "docs" / "INDEX.md"
    counts_path = ROOT / "docs" / "COUNTS.json"
    if args.check:
        if not index_path.exists() or index_path.read_text() != index:
            raise SystemExit("docs/INDEX.md is stale; run tools/build-doc-index.py")
        if not counts_path.exists() or counts_path.read_text() != counts:
            raise SystemExit("docs/COUNTS.json is stale; run tools/build-doc-index.py")
        return 0
    index_path.write_text(index)
    counts_path.write_text(counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run generator tests**

Run:

```bash
uv run --with pytest pytest tests/test_doc_index.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/build-doc-index.py tests/test_doc_index.py docs/INDEX.md docs/COUNTS.json
git commit -m "feat: add dma doc index generator"
```

## Task 5: Pre-ship Check and CI

**Files:**
- Create: `tools/pre-ship-check.py`
- Modify: `.github/workflows/ci.yml`

- [ ] **Step 1: Write pre-ship script**

Create `tools/pre-ship-check.py`:

```python
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
```

- [ ] **Step 2: Modify CI**

Replace `.github/workflows/ci.yml` test command with:

```yaml
      - name: Run pre-ship checks
        run: python tools/pre-ship-check.py
```

- [ ] **Step 3: Run pre-ship check**

Run:

```bash
uv run --with pytest python tools/pre-ship-check.py
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add tools/pre-ship-check.py .github/workflows/ci.yml
git commit -m "ci: add dma pre-ship gate"
```

## Task 6: README and Context Pack Upgrade

**Files:**
- Modify: `README.md`
- Modify: `docs/llms-dma.md`

- [ ] **Step 1: Update README**

Add PCX-style sections:

```markdown
# dma-ai-toolkit

Source-grounded AI toolkit for authorized DMA software development and reverse-engineering workflows using [Metick/DMALibrary](https://github.com/Metick/DMALibrary).

[![CI](https://github.com/VoidChecksum/dma-ai-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/VoidChecksum/dma-ai-toolkit/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Scope](https://img.shields.io/badge/Scope-Authorized%20DMA-f97316.svg)](#safety-and-scope)
[![Docs](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/VoidChecksum/dma-ai-toolkit/main/docs/COUNTS.json&query=$.docs&label=Docs&suffix=%20pages&color=22c55e)](#knowledge-surface)
[![MCP Tools](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/VoidChecksum/dma-ai-toolkit/main/docs/COUNTS.json&query=$.mcp_tools&label=MCP%20Tools&color=0ea5e9)](#mcp-integration)

## First Decision

```text
Need API proof?          Run python tools/dma.py api Memory::Read
Need task context?       Run python tools/dma.py recommend-context "scatter reliability"
Need MCP tools?          Run python mcp/dma_mcp.py
Need answer validation?  Run python tools/dma.py validate-answer README.md
Need release check?      Run python tools/pre-ship-check.py
```

## Anti-Hallucination Pipeline

1. Load `docs/AI_AGENT_OPERATING_MANUAL.md` and `docs/llms-dma.md`.
2. Ask `python tools/dma.py recommend-context "<task>"` for focused docs.
3. Verify every DMALibrary symbol with `python tools/dma.py api <symbol>`.
4. Validate generated Markdown/C++ with `python tools/dma.py validate-answer <file>`.
5. Treat `knowledge/research-sources.json` as evidence, not as an API contract.

## MCP Integration

Run the read-only server:

```bash
python mcp/dma_mcp.py
```

Tools: `overview`, `recommend_context`, `api_lookup`, `validate_answer`, `get_file`, `list_docs`.
```

Keep existing sections for What This Is, What This Is Not, Optional DMALibrary Source, Quick Checks, License.

- [ ] **Step 2: Update context pack**

Append to `docs/llms-dma.md`:

```markdown
## Agent Runtime Commands

- `python tools/dma.py overview` — project contract.
- `python tools/dma.py recommend-context "<task>"` — focused doc list.
- `python tools/dma.py api Memory::Read` — source-backed API proof.
- `python tools/dma.py validate-answer <file>` — answer validation.
- MCP server: `python mcp/dma_mcp.py`.
```

- [ ] **Step 3: Validate README**

Run:

```bash
python tools/validate-cpp-answer.py README.md
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add README.md docs/llms-dma.md
git commit -m "docs: document dma agent runtime"
```

## Task 7: Final Verification and Push

**Files:** all changed files.

- [ ] **Step 1: Run final checks**

Run:

```bash
uv run --with pytest python tools/pre-ship-check.py
```

Expected: PASS.

- [ ] **Step 2: Check status**

Run:

```bash
git status --short
```

Expected: no unstaged/untracked files.

- [ ] **Step 3: Push**

Run:

```bash
git push origin HEAD:main
```

Expected: push succeeds.

- [ ] **Step 4: Watch CI**

Run:

```bash
gh run watch --repo VoidChecksum/dma-ai-toolkit --branch main
```

Expected: CI succeeds.
