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
