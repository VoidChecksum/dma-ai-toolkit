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
