---
name: dmalibrary-api-lookup
description: Use when referencing a DMALibrary class, method, helper, or example.
---

# DMALibrary API Lookup

The API contract is `knowledge/dmalibrary-api-index.json`.

Rules:

- If a symbol is missing, do not use it.
- Check `knowledge/unsupported-symbols.json` for known hallucinations.
- Cite the indexed file and line when explaining an API.
- Prefer verified method names over familiar names from other DMA libraries.
