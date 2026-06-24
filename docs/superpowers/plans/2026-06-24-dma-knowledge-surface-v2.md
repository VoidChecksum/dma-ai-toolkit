# DMA Knowledge Surface v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add source-grounded DMA ecosystem research, UnknownCheats-derived lessons, DMALibrary cookbooks, reliability guidance, and stronger validator rules to `dma-ai-toolkit`.

**Architecture:** Store cited research in `knowledge/research-sources.json`, present synthesized guidance in focused Markdown docs, and extend the existing Python validator with policy checks for risky DMA answers. Keep examples generic and non-target-specific.

**Tech Stack:** Python 3.10+ stdlib, pytest, Markdown docs, existing `tools/validate-cpp-answer.py`.

---

## File Structure

Create:

```text
docs/research/github-dma-ecosystem.md
docs/research/unknowncheats-dma-lessons.md
docs/dmalibrary/scatter-cookbook.md
docs/dmalibrary/signature-scan-cookbook.md
docs/dmalibrary/reliability.md
knowledge/research-sources.json
tests/test_research_sources.py
```

Modify:

```text
README.md
docs/llms-dma.md
tools/validate-cpp-answer.py
tests/test_validate_cpp_answer.py
```

---

### Task 1: Research Source Index

**Files:**
- Create: `knowledge/research-sources.json`
- Create: `tests/test_research_sources.py`

- [ ] **Step 1: Write source index test**

Create `tests/test_research_sources.py`:

```python
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_research_sources_have_required_ids_and_urls():
    data = json.loads((ROOT / "knowledge" / "research-sources.json").read_text())
    assert data["schema"] == 1
    ids = {source["id"] for source in data["sources"]}
    assert {
        "github-pcileech",
        "github-memprocfs",
        "github-orpheus",
        "github-cs2-dma",
        "github-dma-mouse-control",
        "github-volkdma",
        "uc-dmalibrary-thread",
        "uc-vmmsharp-wrapper-thread",
        "uc-eft-dma-radar-lite",
        "uc-cr3-physical-memory-thread",
    }.issubset(ids)
    for source in data["sources"]:
        assert source["url"].startswith("https://")
        assert source["facts"]
```

- [ ] **Step 2: Run test to verify failure**

Run:

```bash
uv run --with pytest pytest tests/test_research_sources.py -v
```

Expected: FAIL because `knowledge/research-sources.json` does not exist.

- [ ] **Step 3: Create source index**

Create `knowledge/research-sources.json`:

```json
{
  "schema": 1,
  "sources": [
    {
      "id": "github-pcileech",
      "type": "github-repo",
      "url": "https://github.com/ufrisk/pcileech",
      "facts": [
        "PCILeech documents hardware and software acquisition methods in a capability matrix.",
        "PCILeech explicitly documents limitations such as IOMMU/VT-d and modern OS DMA protections.",
        "PCILeech points users to LeechCore and MemProcFS as ecosystem dependencies."
      ]
    },
    {
      "id": "github-memprocfs",
      "type": "github-repo",
      "url": "https://github.com/ufrisk/MemProcFS",
      "facts": [
        "MemProcFS presents memory as a virtual file system and as APIs for C/C++, C#, Python, Rust, Java, and Go.",
        "MemProcFS documents dependency setup for Windows, Linux, macOS, FPGA, and software acquisition modes.",
        "MemProcFS release notes call out API changes, refresh options, logging callbacks, and scatter-read performance improvements."
      ]
    },
    {
      "id": "github-orpheus",
      "type": "github-repo",
      "url": "https://github.com/super2xl/orpheus",
      "facts": [
        "Orpheus groups MCP tools into memory, analysis, functions, RTTI, snapshots, emulation, and utilities.",
        "Orpheus documents automatic and manual MCP setup for AI assistants.",
        "Orpheus separates DMA interface, analysis, decompiler, emulation, MCP, and utilities in its project structure."
      ]
    },
    {
      "id": "github-cs2-dma",
      "type": "github-repo",
      "url": "https://github.com/chao-shushu/CS2-DMA",
      "facts": [
        "CS2-DMA documents scatter batch reads, on-demand reading, tiered entity caching, and zero-copy snapshots.",
        "CS2-DMA uses health states and progressive recovery vocabulary for DMA read failures.",
        "CS2-DMA documents logging, crash dumps, config persistence, update checks, and runtime stats."
      ]
    },
    {
      "id": "github-dma-mouse-control",
      "type": "github-repo",
      "url": "https://github.com/J4sp3rTM/DMA-Mouse-Control",
      "facts": [
        "DMA-Mouse-Control uses a small quickstart, clear requirements, simple API reference, architecture diagram, and troubleshooting section.",
        "Its simple public API demonstrates how lightweight wrappers reduce onboarding friction.",
        "The project includes a disclaimer but its target behavior is not suitable to copy into this toolkit."
      ]
    },
    {
      "id": "github-volkdma",
      "type": "github-repo",
      "url": "https://github.com/lyk64/VolkDMA",
      "facts": [
        "VolkDMA advertises RAII DMA handles, optional memmap bootstrapping, PID lookup, module metadata, pointer chains, scatter I/O, v2p translation, and CR3 fix.",
        "VolkDMA shows DMALibrary-adjacent vocabulary useful for API comparison docs.",
        "VolkDMA includes patched binaries, which this toolkit should not vendor."
      ]
    },
    {
      "id": "uc-dmalibrary-thread",
      "type": "forum-thread",
      "url": "https://www.unknowncheats.me/forum/general-programming-and-reversing/614269-dmalibrary-extensive-dma-library.html",
      "facts": [
        "Users asked for Memory::FindSignature range examples.",
        "Users asked for scatter read performance examples.",
        "The DMALibrary author explained that dependent scatter reads require executing the first batch before using returned pointer values."
      ]
    },
    {
      "id": "uc-vmmsharp-wrapper-thread",
      "type": "forum-thread",
      "url": "https://www.unknowncheats.me/forum/c-/522455-memprocfs-vmmsharp-dma-wrapper.html",
      "facts": [
        "Users discussed wrapper-over-wrapper tradeoffs around Vmmsharp and custom abstractions.",
        "Participants noted byte reads plus typed conversion as the minimal primitive for many wrappers.",
        "Users reported scatter-read performance can regress when abstractions add boxing, exceptions, or CPU overhead."
      ]
    },
    {
      "id": "uc-eft-dma-radar-lite",
      "type": "forum-thread",
      "url": "https://www.unknowncheats.me/forum/escape-from-tarkov/712525-eft-dma-radar-lite-wpf.html",
      "facts": [
        "The post emphasizes clean code, WPF, MVVM patterns, and source-only distribution.",
        "Forum replies show users need clear startup instructions for source-only releases.",
        "File approval output includes dependency hashes, showing release hygiene expectations."
      ]
    },
    {
      "id": "uc-cr3-physical-memory-thread",
      "type": "forum-thread",
      "url": "https://www.unknowncheats.me/forum/anti-cheat-bypass/591802-search-physical-memory-target-processs-cr3.html",
      "facts": [
        "Forum discussion treats PE-header based CR3/base discovery as brittle.",
        "Participants note PE headers may not always be reliable evidence.",
        "CR3/base heuristics should be documented as caveated reliability topics, not guaranteed recipes."
      ]
    }
  ]
}
```

- [ ] **Step 4: Run test**

Run:

```bash
uv run --with pytest pytest tests/test_research_sources.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add knowledge/research-sources.json tests/test_research_sources.py
git commit -m "docs: add dma research source index"
```

---

### Task 2: GitHub Ecosystem Research Doc

**Files:**
- Create: `docs/research/github-dma-ecosystem.md`

- [ ] **Step 1: Create GitHub ecosystem doc**

Create `docs/research/github-dma-ecosystem.md`:

```markdown
# GitHub DMA Ecosystem Lessons

This page records safe lessons from public DMA-adjacent repositories. It is not an endorsement of target-specific features or bypass claims.

## ufrisk/pcileech

Source: https://github.com/ufrisk/pcileech
License: AGPL-3.0

Useful lesson: document acquisition methods, hardware/software modes, speed limits, operating-system limitations, and ecosystem dependencies in explicit tables.

Do not copy: offensive command recipes, implants, unlock flows, or AGPL code.

Safe adaptation: add a device/dependency matrix that explains `FTD3XX.dll`, `leechcore.dll`, `vmm.dll`, memmap files, and why IOMMU/VT-d/VBS can change behavior.

## ufrisk/MemProcFS

Source: https://github.com/ufrisk/MemProcFS
License: AGPL-3.0

Useful lesson: present memory acquisition as both a virtual file system and a programmable API. Surface language bindings, plugin points, release changes, and dependency setup.

Do not copy: source code, bundled dependency layout, or GPL/AGPL material.

Safe adaptation: document DMALibrary's relationship to MemProcFS and link to official APIs instead of reproducing headers.

## super2xl/orpheus

Source: https://github.com/super2xl/orpheus
License: GPL-3.0

Useful lesson: agent tooling becomes clearer when grouped by task: memory, analysis, functions, RTTI, snapshots, emulation, and utilities.

Do not copy: UI implementation, tool handlers, telemetry, or GPL code.

Safe adaptation: use its MCP taxonomy as inspiration for future `dma-ai-toolkit` lookup tools.

## chao-shushu/CS2-DMA

Source: https://github.com/chao-shushu/CS2-DMA
License: MIT

Useful lesson: production DMA tools need vocabulary for scatter batching, tiered caching, stale-data tolerance, health states, recovery, logging, crash dumps, and config.

Do not copy: target-specific offsets, feature code, rendering implementation, web radar behavior, or update automation tied to a game.

Safe adaptation: add generic reliability docs and neutral examples that teach the concepts without game data.

## J4sp3rTM/DMA-Mouse-Control

Source: https://github.com/J4sp3rTM/DMA-Mouse-Control
License: MIT

Useful lesson: onboarding improves with quickstart, simple API reference, architecture diagram, requirements, and troubleshooting.

Do not copy: input-control behavior or target process design.

Safe adaptation: add concise DMALibrary quickstart and troubleshooting docs.

## lyk64/VolkDMA

Source: https://github.com/lyk64/VolkDMA
License: MIT

Useful lesson: DMALibrary-like APIs often converge on RAII handles, memmap bootstrapping, PID lookup, module metadata, pointer-chain reads, scatter I/O, v2p translation, and CR3 fix.

Do not copy: patched binaries or implementation code.

Safe adaptation: create comparison vocabulary and verification checks for these concepts.
```

- [ ] **Step 2: Commit**

```bash
git add docs/research/github-dma-ecosystem.md
git commit -m "docs: map public dma ecosystem lessons"
```

---

### Task 3: Forum Lessons and DMALibrary Cookbooks

**Files:**
- Create: `docs/research/unknowncheats-dma-lessons.md`
- Create: `docs/dmalibrary/scatter-cookbook.md`
- Create: `docs/dmalibrary/signature-scan-cookbook.md`
- Create: `docs/dmalibrary/reliability.md`

- [ ] **Step 1: Create forum lessons doc**

Create `docs/research/unknowncheats-dma-lessons.md`:

```markdown
# UnknownCheats DMA Lessons

Sources are indexed in `knowledge/research-sources.json`. The local UnknownCheats MCP server was available during research, but live listing hit Cloudflare. This page uses public web-indexed forum pages and stores only short factual lessons.

## Recurring Questions

### How do I choose `FindSignature` ranges?

Use a meaningful virtual-address range: usually module base to `base + module_size`, or a tighter section range when the code location is known. Avoid scanning arbitrary huge ranges by default.

### How do scatter reads work?

Scatter reads batch independent memory reads, then execute them together. Values are not available until `ExecuteReadScatter` returns.

### Can dependent pointer reads be in one scatter batch?

No. If the second address depends on the first read's result, split the work into two phases: execute pointer reads first, then build a second batch for pointee reads.

### Are wrappers always faster?

No. Forum discussion around Vmmsharp wrappers notes that abstractions can add boxing, exceptions, and CPU overhead. The primitive should remain clear: read bytes, convert deliberately, batch where useful.

### Are CR3/base heuristics guaranteed?

No. Physical-memory and PE-header heuristics are environment-sensitive. Treat them as evidence to verify, not truth.

## Repository Lessons

- Source-only releases need clear startup instructions.
- Dependency hashes and release hygiene matter.
- Clean UI/DMA separation helps maintainability.
- Minimal bases are easier for developers to adapt than full feature dumps.
```

- [ ] **Step 2: Create scatter cookbook**

Create `docs/dmalibrary/scatter-cookbook.md`:

```markdown
# DMALibrary Scatter Cookbook

Sources: `knowledge/research-sources.json` entries `uc-dmalibrary-thread`, `uc-vmmsharp-wrapper-thread`, and DMALibrary symbols in `knowledge/dmalibrary-api-index.json`.

## Lifecycle

1. Create a handle with `Memory::CreateScatterHandle`.
2. Add independent requests with `Memory::AddScatterReadRequest`.
3. Execute with `Memory::ExecuteReadScatter`.
4. Close with `Memory::CloseScatterHandle`.

## Independent Read Batch

```cpp
auto handle = mem.CreateScatterHandle();

std::uint64_t address1 = 0;
std::uint64_t address2 = 0;
std::uint32_t value = 0;

mem.AddScatterReadRequest(handle, base + 0x10, &address1, sizeof(address1));
mem.AddScatterReadRequest(handle, base + 0x18, &address2, sizeof(address2));
mem.AddScatterReadRequest(handle, base + 0x20, &value, sizeof(value));
mem.ExecuteReadScatter(handle);
mem.CloseScatterHandle(handle);
```

The example addresses above are neutral lab-process addresses. Do not store target offsets in this repository.

## Two-Phase Pointer Reads

```cpp
auto first = mem.CreateScatterHandle();
std::uint64_t pointer_a = 0;
std::uint64_t pointer_b = 0;

mem.AddScatterReadRequest(first, base + 0x10, &pointer_a, sizeof(pointer_a));
mem.AddScatterReadRequest(first, base + 0x18, &pointer_b, sizeof(pointer_b));
mem.ExecuteReadScatter(first);
mem.CloseScatterHandle(first);

if (pointer_a == 0 || pointer_b == 0) {
    return 1;
}

auto second = mem.CreateScatterHandle();
std::uint32_t value_a = 0;
std::uint32_t value_b = 0;

mem.AddScatterReadRequest(second, pointer_a + 0x04, &value_a, sizeof(value_a));
mem.AddScatterReadRequest(second, pointer_b + 0x04, &value_b, sizeof(value_b));
mem.ExecuteReadScatter(second);
mem.CloseScatterHandle(second);
```

A dependent read cannot use `pointer_a` before the first scatter batch executes.

## Checklist

- Batch independent reads.
- Split dependent reads into phases.
- Validate pointers before second-phase reads.
- Close every handle.
- Measure CPU overhead when adding wrapper layers.
```

- [ ] **Step 3: Create signature scan cookbook**

Create `docs/dmalibrary/signature-scan-cookbook.md`:

```markdown
# DMALibrary Signature Scan Cookbook

Sources: `knowledge/research-sources.json` entry `uc-dmalibrary-thread` and DMALibrary symbol `Memory::FindSignature`.

## Range Meaning

`range_start` is the first virtual address to scan. `range_end` is the exclusive upper bound. For a whole module, use `base` and `base + size`.

```cpp
const auto base = mem.GetBaseDaddy("process.exe");
const auto size = mem.GetBaseSize("process.exe");
const auto found = mem.FindSignature("48 8B ?? ??", base, base + size);
```

The signature above is a generic syntax example, not a target signature.

## Choosing Ranges

- Use module range for broad discovery.
- Use section range for known code/data sections.
- Use short local ranges when validating a nearby instruction pattern.
- Record where a signature came from in an evidence log.

## Anti-patterns

- Scanning all virtual memory without a reason.
- Treating forum signatures as durable truth.
- Shipping target-specific signatures in this repo.
```

- [ ] **Step 4: Create reliability doc**

Create `docs/dmalibrary/reliability.md`:

```markdown
# DMA Reliability Notes

Sources: `knowledge/research-sources.json` entries `github-cs2-dma`, `github-memprocfs`, `uc-cr3-physical-memory-thread`, and `uc-vmmsharp-wrapper-thread`.

## Read Validation

DMA reads can fail, return zeroed buffers, or return stale data. Validate pointers, ranges, structure sizes, and sentinel fields before trusting a read.

## Data Freshness

Separate fields by update frequency:

- high frequency: position, view matrix, fast-changing state
- medium frequency: health, flags, short-lived object state
- low frequency: names, module metadata, static configuration

This vocabulary helps agents design cache strategies without target-specific code.

## Health States

Use three generic states:

- Healthy: recent reads pass validation.
- Degraded: some reads fail or stale data is held temporarily.
- Failed: repeated validation failures require reinitialization or cache reset.

## Recovery Principles

- Probe before full reset.
- Reinitialize process/module metadata when base assumptions break.
- Reset caches after repeated failures.
- Log transitions and failure counts.

## CR3 and Base Discovery Caveats

CR3/base heuristics depend on OS version, memory manager behavior, page table state, and whether useful PE/header evidence exists. Present them as hypotheses to verify, not guaranteed facts.
```

- [ ] **Step 5: Commit**

```bash
git add docs/research/unknowncheats-dma-lessons.md docs/dmalibrary/scatter-cookbook.md docs/dmalibrary/signature-scan-cookbook.md docs/dmalibrary/reliability.md
git commit -m "docs: add dmalibrary cookbooks and forum lessons"
```

---

### Task 4: Validator Policy Upgrade

**Files:**
- Modify: `tools/validate-cpp-answer.py`
- Modify: `tests/test_validate_cpp_answer.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_validate_cpp_answer.py`:

```python

def test_rejects_target_offset_dump(tmp_path):
    index, unsupported = make_index(tmp_path)
    answer = tmp_path / "answer.md"
    answer.write_text(
        """
| name | offset |
|---|---:|
| a | 0x11111111 |
| b | 0x22222222 |
| c | 0x33333333 |
| d | 0x44444444 |
| e | 0x55555555 |
| f | 0x66666666 |
""".strip()
    )

    result = validator.validate(answer, index, unsupported)

    assert not result.ok
    assert any("offset dump" in error for error in result.errors)


def test_rejects_anti_cheat_guarantee_language(tmp_path):
    index, unsupported = make_index(tmp_path)
    answer = tmp_path / "answer.md"
    answer.write_text("This DMA method is undetected and works on EAC.\n")

    result = validator.validate(answer, index, unsupported)

    assert not result.ok
    assert any("unsafe guarantee" in error for error in result.errors)


def test_accepts_warning_about_bad_guarantees(tmp_path):
    index, unsupported = make_index(tmp_path)
    answer = tmp_path / "answer.md"
    answer.write_text("Do not claim a method is undetected or works on EAC.\n")

    result = validator.validate(answer, index, unsupported)

    assert result.ok
```

- [ ] **Step 2: Run tests to verify failure**

Run:

```bash
uv run --with pytest pytest tests/test_validate_cpp_answer.py -v
```

Expected: FAIL because validator does not detect offset dumps or unsafe guarantee language.

- [ ] **Step 3: Implement policy checks**

In `tools/validate-cpp-answer.py`, add near imports:

```python
OFFSET_RE = re.compile(r"\b0x[0-9A-Fa-f]{4,}\b")
UNSAFE_GUARANTEE_RE = re.compile(r"\b(undetected|works on\s+(?:EAC|FACEIT|Vanguard)|bypass(?:es|ed|ing)?)\b", re.IGNORECASE)
WARNING_PREFIX_RE = re.compile(r"\b(do not|don't|never|avoid|no)\b", re.IGNORECASE)
```

Add helper functions before `validate`:

```python
def check_offset_dump(answer: str) -> list[str]:
    offsets = OFFSET_RE.findall(answer)
    if len(offsets) >= 6:
        return [f"possible target-specific offset dump: {len(offsets)} hex constants"]
    risky_names = ("offsets.json", "client_dll.json", "dump.cs")
    if any(name in answer for name in risky_names):
        return ["possible target-specific offset dump: offset artifact name present"]
    return []


def check_unsafe_guarantees(answer: str) -> list[str]:
    errors: list[str] = []
    for match in UNSAFE_GUARANTEE_RE.finditer(answer):
        start = max(0, match.start() - 32)
        context = answer[start:match.start()]
        if WARNING_PREFIX_RE.search(context):
            continue
        errors.append(f"unsafe guarantee language: {match.group(0)}")
    return errors
```

Inside `validate`, after unsupported-symbol checks and before method-call checks, add:

```python
    errors.extend(check_offset_dump(answer))
    errors.extend(check_unsafe_guarantees(answer))
```

- [ ] **Step 4: Run validator tests**

Run:

```bash
uv run --with pytest pytest tests/test_validate_cpp_answer.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/validate-cpp-answer.py tests/test_validate_cpp_answer.py
git commit -m "feat: strengthen dma answer validator"
```

---

### Task 5: README and Context Pack Wiring

**Files:**
- Modify: `README.md`
- Modify: `docs/llms-dma.md`

- [ ] **Step 1: Update README AI Start Here section**

Replace the README `AI Start Here` list with:

```markdown
## AI Start Here

1. Read `docs/AI_AGENT_OPERATING_MANUAL.md`.
2. Read `docs/llms-dma.md`.
3. For ecosystem context, read `docs/research/github-dma-ecosystem.md` and `docs/research/unknowncheats-dma-lessons.md`.
4. For DMALibrary usage, read the matching cookbook under `docs/dmalibrary/`.
5. Verify every DMALibrary symbol against `knowledge/dmalibrary-api-index.json`.
6. Check cited research in `knowledge/research-sources.json`.
7. Run `python tools/validate-cpp-answer.py <file>` before trusting generated answers or snippets.
```

- [ ] **Step 2: Extend context pack**

Append to `docs/llms-dma.md`:

```markdown
## Research-Backed Guidance

- Use `docs/dmalibrary/scatter-cookbook.md` for scatter handle lifecycle and two-phase dependent reads.
- Use `docs/dmalibrary/signature-scan-cookbook.md` for `FindSignature` range selection.
- Use `docs/dmalibrary/reliability.md` for stale data, health states, recovery, and CR3/base caveats.
- Use `docs/research/github-dma-ecosystem.md` for public repo lessons.
- Use `docs/research/unknowncheats-dma-lessons.md` for forum-derived developer pain points.

Do not output target-specific offsets, anti-cheat bypass claims, or guarantees like "undetected".
```

- [ ] **Step 3: Validate README**

Run:

```bash
python3 tools/validate-cpp-answer.py README.md
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add README.md docs/llms-dma.md
git commit -m "docs: wire knowledge surface into ai workflow"
```

---

### Task 6: Final Verification and Push

**Files:**
- Modify: none unless verification finds a defect

- [ ] **Step 1: Run tests**

Run:

```bash
uv run --with pytest pytest -v
```

Expected: all tests PASS.

- [ ] **Step 2: Run validator on key docs**

Run:

```bash
python3 tools/validate-cpp-answer.py README.md
python3 tools/validate-cpp-answer.py docs/dmalibrary/scatter-cookbook.md
python3 tools/validate-cpp-answer.py docs/dmalibrary/signature-scan-cookbook.md
```

Expected: all print `PASS`.

- [ ] **Step 3: Push branch**

Run:

```bash
git push origin HEAD:main
```

Expected: push succeeds to `VoidChecksum/dma-ai-toolkit`.

- [ ] **Step 4: Watch CI**

Run:

```bash
gh run watch --repo VoidChecksum/dma-ai-toolkit --branch main
```

Expected: CI succeeds.
