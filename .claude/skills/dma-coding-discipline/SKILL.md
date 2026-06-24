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
