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
