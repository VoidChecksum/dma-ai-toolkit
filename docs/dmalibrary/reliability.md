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
