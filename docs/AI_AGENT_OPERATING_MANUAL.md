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
