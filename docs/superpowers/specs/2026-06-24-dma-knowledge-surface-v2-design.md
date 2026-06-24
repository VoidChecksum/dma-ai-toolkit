# DMA Knowledge Surface v2 Design

Date: 2026-06-24
Target repo: `VoidChecksum/dma-ai-toolkit`

## Goal

Upgrade `dma-ai-toolkit` from a minimal DMALibrary index into a stronger source-grounded knowledge surface for agents building authorized DMA software and doing evidence-first reverse engineering.

## Research Inputs

### GitHub

- `ufrisk/pcileech` — device/acquisition matrix, install notes, limitations, and ecosystem links.
- `ufrisk/MemProcFS` — multi-language API docs, virtual file system framing, plugin architecture, release/changelog lessons, and dependency guidance.
- `super2xl/orpheus` — agent-facing DMA analysis framework with MCP tool taxonomy: memory, analysis, functions, RTTI, snapshots, emulation, utilities.
- `chao-shushu/CS2-DMA` — production lessons: scatter batching, tiered caching, DMA health states, stale-data tolerance, logging, config, crash diagnostics, and update checks.
- `J4sp3rTM/DMA-Mouse-Control` — small wrapper ergonomics: quickstart, simple API reference, troubleshooting sections.
- `lyk64/VolkDMA` — DMALibrary-like surface: RAII handles, memmap bootstrapping, module metadata, pointer chains, scatter I/O, v2p translation, CR3 fix.

### UnknownCheats / Forum Sources

The local UnknownCheats MCP server exists and exposes `search_forum`, `read_thread`, and other read tools, but direct forum listing hit Cloudflare 403 in this session. Web-indexed UnknownCheats pages still provided useful public evidence:

- DMALibrary release thread: users ask for `FindSignature` range examples and scatter read examples; author answers that `FindSignature` should use a meaningful module/section range and that scatter reads must execute before dependent pointer values exist.
- MemProcFS/Vmmsharp wrapper thread: users discuss wrapper-over-wrapper tradeoffs, boxing/unboxing overhead, struct/byte conversion, and scatter performance.
- DMA radar/source posts: cleaner bases use MVVM/separation of UI and DMA reads, minimal feature scope, dependency hash/release hygiene, and source-only distribution.
- Physical memory/CR3 posts: PE-header and CR3/base discovery heuristics are brittle and must be documented as reliability caveats, not guaranteed recipes.

## Non-goals

- No target-specific offsets, signatures, or game implementation details.
- No anti-cheat bypass instructions.
- No turnkey cheat or production app implementation.
- No forum scraping cache containing private content or credentials.
- No vendored forum data beyond short source citations and URLs.

## Proposed Additions

```text
docs/
  research/
    github-dma-ecosystem.md
    unknowncheats-dma-lessons.md
  dmalibrary/
    scatter-cookbook.md
    signature-scan-cookbook.md
    reliability.md
knowledge/
  research-sources.json
tools/
  validate-cpp-answer.py        # extend existing validator
tests/
  test_validate_cpp_answer.py   # extend existing tests
```

## Documentation Design

### `docs/research/github-dma-ecosystem.md`

A concise evidence-backed map of public DMA-adjacent repositories. Each entry records:

- repo URL
- license
- main lesson for `dma-ai-toolkit`
- what not to copy
- safe adaptation for this repo

Expected synthesis:

- PCILeech/MemProcFS teach dependency/device matrices and explicit limitations.
- Orpheus teaches MCP/tool taxonomy and AI analysis workflow organization.
- CS2-DMA teaches reliability/performance vocabulary, but target-specific feature code is out of scope.
- Lightweight wrappers teach quickstart/API ergonomics.

### `docs/research/unknowncheats-dma-lessons.md`

A forum-derived FAQ without private data. Focus on recurring developer confusion:

- how scatter reads work
- why dependent reads require two phases
- how to choose signature scan ranges
- wrapper abstraction versus performance
- CR3/base heuristics as brittle evidence, not certainty
- source-only releases need clear start instructions

### `docs/dmalibrary/scatter-cookbook.md`

Generic DMALibrary scatter guidance:

- handle lifecycle: create, add, execute, close
- independent read batch example
- two-phase pointer-chain example: first batch reads pointers, second batch reads pointees
- why dependent scatter reads cannot use values before execution
- performance checklist: group stable fields, avoid per-field round trips, close handles

All examples use neutral names like `process.exe`, `base`, `address1`; no game offsets.

### `docs/dmalibrary/signature-scan-cookbook.md`

Generic signature scan guidance:

- `range_start` is the beginning VA to scan
- `range_end` should be `base + size` or a tighter section range
- prefer module/section size over arbitrary huge scans
- keep signature provenance in evidence log
- never store target signatures in this repo

### `docs/dmalibrary/reliability.md`

Reliability model for agents:

- failed reads and zeroed buffers need validation
- stale data tolerance is often better than flicker/false negatives
- separate high-frequency fields from low-frequency fields
- health states: Healthy, Degraded, Failed
- recovery principles: probe, reinitialize, reset cache
- CR3/base discovery is environment-sensitive and should be presented as caveated

## Knowledge Source Index

`knowledge/research-sources.json` stores citation records:

```json
{
  "schema": 1,
  "sources": [
    {
      "id": "uc-dmalibrary-thread",
      "type": "forum-thread",
      "url": "https://www.unknowncheats.me/forum/general-programming-and-reversing/614269-dmalibrary-extensive-dma-library.html",
      "facts": [
        "Users asked for FindSignature range examples.",
        "Users asked for scatter read performance examples.",
        "Author explained dependent scatter reads need execution before pointee reads."
      ]
    }
  ]
}
```

No private forum content or cookies are stored.

## Validator Upgrade

Extend `tools/validate-cpp-answer.py` with Markdown answer checks:

1. Reject obvious target-specific offset dumps:
   - repeated `0x...` constants in lists/tables beyond a small threshold
   - filenames like `offsets.json`, `client_dll.json`, `dump.cs` when presented as content to ship
2. Reject unsafe promise language:
   - `undetected`, `bypass`, `works on FACEIT`, `works on EAC`, unless the text is explicitly warning against claims
3. Require citations for cookbook claims when validating Markdown docs under `docs/research/` or `docs/dmalibrary/*cookbook.md`:
   - at least one URL from `knowledge/research-sources.json`
   - at least one local source path or DMALibrary symbol reference when discussing API usage

## Tests

Add tests for:

- validator rejects target offset tables
- validator rejects unsupported anti-cheat guarantee language
- validator accepts neutral scatter cookbook snippets with citations
- research source JSON has stable schema and required IDs

## Safety Boundary

The upgraded repo should make agents better at asking/verifying the right DMA engineering questions, not better at shipping a cheat. Every example remains generic and source-grounded.

## Success Criteria

- Research docs cover GitHub and UnknownCheats lessons with URLs.
- Scatter and signature scan cookbooks answer the exact forum pain points found during research.
- Reliability doc gives agents a vocabulary for stale reads, health states, and recovery without target-specific code.
- Validator catches at least two new risky answer classes: offset dumps and anti-cheat guarantee language.
- CI passes after added tests.
