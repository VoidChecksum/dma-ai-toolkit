# dma-ai-toolkit Design

Date: 2026-06-24
Owner: VoidChecksum
Target repo: `VoidChecksum/dma-ai-toolkit`

## Goal

Create a separate AI-facing toolkit for authorized DMA software development and reverse-engineering workflows, modeled after `pcx-ai-toolkit` but scoped around `Metick/DMALibrary`.

## Non-goals

- Do not merge this into `pcx-ai-toolkit`.
- Do not vendor a permanent copy of DMALibrary source.
- Do not ship target-specific offsets, bypass recipes, or a full working cheat application.
- Do not invent APIs that are not proven by source or generated indexes.

## Source Inputs

- `VoidChecksum/pcx-ai-toolkit`: structure reference for docs, skills, validators, context packs, MCP-style tooling, templates, and CI.
- `Metick/DMALibrary`: optional source submodule/input for API extraction, examples, and provenance.

Both repos are MIT licensed at time of review.

## Architecture

```text
dma-ai-toolkit/
  README.md
  LICENSE
  docs/
    AI_AGENT_OPERATING_MANUAL.md
    llms-dma.md
    dmalibrary/
      api-reference.md
      memory.md
      scatter.md
      process.md
      keyboard.md
      registry.md
      shellcode.md
    reverse-engineering/
      evidence-log.md
      triage-workflow.md
      symbol-validation.md
  knowledge/
    dmalibrary-api-index.json
    unsupported-symbols.json
    provenance.json
    pitfalls.md
  tools/
    extract-dmalibrary-api.py
    validate-cpp-answer.py
    check-doc-drift.py
  templates/
    minimal-dma-client/
    scatter-read-example/
  .claude/
    skills/
      dma-coding-discipline/
      dma-re-discipline/
      dmalibrary-api-lookup/
  third_party/
    DMALibrary/        # optional git submodule, not copied source
```

## Core Workflow

Agents must follow this sequence before producing DMA C++ or RE guidance:

1. Load `docs/AI_AGENT_OPERATING_MANUAL.md`.
2. Load `docs/llms-dma.md`.
3. Verify each DMALibrary symbol against `knowledge/dmalibrary-api-index.json`.
4. For RE work, write evidence to an evidence log before conclusions.
5. Validate generated answers/snippets with `tools/validate-cpp-answer.py`.
6. If the index cannot prove a symbol exists, say so instead of guessing.

## Components

### Documentation

Docs are the primary agent contract. `llms-dma.md` is the compact context pack. Detailed pages under `docs/dmalibrary/` mirror the library's functional areas: initialization, process/module lookup, read/write, scatter I/O, keyboard, registry, shellcode, and utility helpers.

### Knowledge Index

`knowledge/dmalibrary-api-index.json` stores extracted classes, methods, signatures, file paths, and source-line anchors. `unsupported-symbols.json` blocks common hallucinations. `provenance.json` records source repo, commit, generated time, and extractor version.

### Tools

Tools stay minimal:

- `extract-dmalibrary-api.py`: parse headers/source into the API index.
- `validate-cpp-answer.py`: fail generated Markdown or C++ snippets when they use unsupported symbols or omit required context.
- `check-doc-drift.py`: compare current submodule commit/index against committed provenance.

No custom build system unless templates need one.

### Templates

Templates are intentionally small and non-target-specific:

- `minimal-dma-client`: initialization, process selection, safe read wrapper.
- `scatter-read-example`: scatter handle lifecycle and cleanup.

Templates should compile only when the user supplies required DMALibrary dependencies locally.

### Skills

Skills mirror the PCX model but stay narrower:

- `dma-coding-discipline`: source-grounded C++ generation rules.
- `dma-re-discipline`: evidence-first RE workflow.
- `dmalibrary-api-lookup`: mandatory symbol verification before API usage.

## Safety and Scope

The repo is for authorized labs, owned systems, and legitimate research. It must not provide target-specific offsets, anti-cheat bypass instructions, or turnkey cheating workflows. Reverse-engineering guidance must preserve evidence and authorization boundaries.

## Testing

Smallest useful checks:

- API extractor produces stable JSON from DMALibrary headers.
- validator rejects one known hallucinated symbol.
- validator accepts one documented DMALibrary call.
- doc drift check fails when provenance commit differs from submodule commit.

## Release Shape

Initial repo should ship only:

1. README and license.
2. Agent operating manual.
3. generated/hand-curated DMALibrary docs.
4. API index and unsupported-symbol list.
5. extractor + validator + drift checker.
6. two minimal templates.
7. three agent skills.
8. CI running the small checks above.

Anything beyond that waits until this smaller loop works.
