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

## Research-Backed Guidance

- Use `docs/dmalibrary/scatter-cookbook.md` for scatter handle lifecycle and two-phase dependent reads.
- Use `docs/dmalibrary/signature-scan-cookbook.md` for `FindSignature` range selection.
- Use `docs/dmalibrary/reliability.md` for stale data, health states, recovery, and CR3/base caveats.
- Use `docs/research/github-dma-ecosystem.md` for public repo lessons.
- Use `docs/research/unknowncheats-dma-lessons.md` for forum-derived developer pain points.

Do not output target-specific offsets, anti-cheat bypass claims, or guarantees like "undetected".

## Agent Runtime Commands

- `python tools/dma.py overview` — project contract.
- `python tools/dma.py recommend-context "<task>"` — focused doc list.
- `python tools/dma.py api Memory::Read` — source-backed API proof.
- `python tools/dma.py validate-answer <file>` — answer validation.
- MCP server: `python mcp/dma_mcp.py`.
