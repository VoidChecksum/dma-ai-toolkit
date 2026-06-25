# DMA Core Agent Runtime Design

Date: 2026-06-25
Target repo: `VoidChecksum/dma-ai-toolkit`

## Goal

Upgrade `dma-ai-toolkit` from a documentation-first DMALibrary knowledge pack into a PCX-style agent runtime for authorized DMA software work.

## Non-goals

- Do not ship target-specific offsets, signatures, bypass recipes, or turnkey cheat flows.
- Do not add remote scanning or offensive network tooling.
- Do not build a full C++ DMA app framework in this slice.
- Do not mirror every `pcx-ai-toolkit` polish file; add only runtime pieces that agents use directly.

## Architecture

Use Python 3.10+ stdlib and existing pytest tests. Keep the repository boring: small scripts, JSON files, Markdown docs, and no persistent daemon beyond a stdio MCP process.

The runtime has four layers:

1. `tools/dma.py` — thin CLI facade for humans and agents.
2. `mcp/dma_mcp.py` — read-only JSON-RPC MCP server exposing the same source-backed facts.
3. `tools/build-doc-index.py` — deterministic docs/counts generator for `docs/INDEX.md` and `docs/COUNTS.json`.
4. `tools/pre-ship-check.py` — one local gate that runs tests, drift checks, doc index checks, and validator smoke tests.

Existing source files remain canonical:

- `knowledge/dmalibrary-api-index.json` proves DMALibrary symbols.
- `knowledge/unsupported-symbols.json` blocks known hallucinations.
- `knowledge/research-sources.json` stores cited public source evidence.
- `docs/llms-dma.md` remains the compact context pack.

## CLI Contract

Create `tools/dma.py` with these subcommands:

```text
python tools/dma.py overview
python tools/dma.py api Memory::Read
python tools/dma.py recommend-context "scatter read player list"
python tools/dma.py validate-answer README.md
python tools/dma.py list-docs
```

Behavior:

- `overview` prints a short project contract and core file list.
- `api <symbol>` looks up exact symbol names in `knowledge/dmalibrary-api-index.json` and prints JSON.
- `recommend-context <task>` returns ordered doc paths based on keyword matching.
- `validate-answer <path>` delegates to existing validator logic.
- `list-docs` prints indexed docs and titles.

## MCP Contract

Create `mcp/dma_mcp.py` as a stdio JSON-RPC MCP server with read-only tools:

- `overview()`
- `recommend_context(task: string)`
- `api_lookup(symbol: string)`
- `validate_answer(path: string)`
- `get_file(path: string)`
- `list_docs()`

The MCP server must not write files, run shell commands, or touch network resources. Errors return JSON-RPC error objects with concise messages.

## Documentation Index

Create `tools/build-doc-index.py`.

Generated files:

- `docs/INDEX.md` — table of docs grouped by directory with title and relative path.
- `docs/COUNTS.json` — counts for docs, doc lines, skills, templates, API symbols, research sources, MCP tools, and native tools.

The generator must be deterministic and safe to run repeatedly.

## Validation and Pre-ship

Create `tools/pre-ship-check.py`.

It runs:

1. `python -m pytest -v`
2. `python tools/check-doc-drift.py`
3. `python tools/build-doc-index.py --check`
4. `python tools/validate-cpp-answer.py README.md`
5. `python tools/dma.py api Memory::Read`

Exit nonzero on first failure.

## README Upgrade

Upgrade README toward PCX style:

- Add badge block for CI, license, scope, docs count, MCP tools, AI skills.
- Add First Decision block.
- Add Anti-Hallucination Pipeline section.
- Add MCP Integration section.
- Keep safety boundary prominent.

## Tests

Add tests before implementation:

- CLI API lookup returns `Memory::Read`.
- CLI rejects unknown symbols.
- context recommendation includes scatter and reliability docs for scatter/reliability task text.
- doc index generator creates required counts and index entries.
- MCP `tools/list` includes the six read-only tools.
- MCP `api_lookup` returns `Memory::Read`.
- pre-ship check can be invoked in CI after implementation.

## Success Criteria

- Local `python tools/pre-ship-check.py` passes.
- `docs/COUNTS.json` exists and README badges can consume it.
- MCP smoke test passes without network or secrets.
- GitHub Actions runs the pre-ship check and passes on `main`.
- Agents can answer "which DMA docs should I load?" and "is this DMALibrary symbol real?" without guessing.
