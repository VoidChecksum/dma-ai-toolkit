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

## What This Is

`dma-ai-toolkit` teaches agents how to use DMALibrary from verified source, not guessed APIs. It provides context packs, API indexes, validators, templates, MCP tools, and agent skills.

## What This Is Not

This is not a target-specific offset pack, anti-cheat bypass guide, or turnkey cheating application. Use it only on owned systems, labs, and authorized research targets.

## AI Start Here

1. Read `docs/AI_AGENT_OPERATING_MANUAL.md`.
2. Read `docs/llms-dma.md`.
3. Run `python tools/dma.py recommend-context "<task>"` for focused docs.
4. Verify every DMALibrary symbol with `python tools/dma.py api <symbol>`.
5. Check cited research in `knowledge/research-sources.json`.
6. Run `python tools/dma.py validate-answer <file>` before trusting generated answers or snippets.

## Anti-Hallucination Pipeline

1. Load the operating manual and compact context pack.
2. Use CLI or MCP `recommend_context` before writing DMA code.
3. Verify APIs against `knowledge/dmalibrary-api-index.json`.
4. Reject known hallucinations from `knowledge/unsupported-symbols.json`.
5. Validate generated Markdown/C++ answers.
6. Treat research sources as evidence, not API contracts.

## Knowledge Surface

- `docs/llms-dma.md` — compact agent context pack.
- `docs/dmalibrary/scatter-cookbook.md` — scatter lifecycle and dependent read phases.
- `docs/dmalibrary/signature-scan-cookbook.md` — generic `FindSignature` range guidance.
- `docs/dmalibrary/reliability.md` — stale reads, health states, recovery, CR3/base caveats.
- `docs/research/github-dma-ecosystem.md` — public repository lessons.
- `docs/research/unknowncheats-dma-lessons.md` — forum-derived pain points.
- `docs/INDEX.md` and `docs/COUNTS.json` — generated documentation map and badge data.

## MCP Integration

Run the read-only server:

```bash
python mcp/dma_mcp.py
```

Tools: `overview`, `recommend_context`, `api_lookup`, `validate_answer`, `get_file`, `list_docs`.

The MCP server does not write files, scan networks, or fetch remote targets.

## Optional DMALibrary Source

DMALibrary is an optional submodule:

```bash
git submodule add https://github.com/Metick/DMALibrary third_party/DMALibrary
git submodule update --init --recursive
```

The toolkit records source provenance in `knowledge/provenance.json`.

## Quick Checks

```bash
python tools/pre-ship-check.py
python tools/dma.py api Memory::Read
python tools/dma.py validate-answer README.md
```

## Safety and Scope

Allowed: owned systems, labs, authorized research, generic DMALibrary usage, source-backed reverse-engineering notes.

Disallowed: target-specific offset dumps, anti-cheat circumvention recipes, guarantee claims, turnkey cheating workflows.

## License

MIT. DMALibrary is MIT licensed by its upstream project.
