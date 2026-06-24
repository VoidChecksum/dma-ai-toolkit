# dma-ai-toolkit

Source-grounded AI toolkit for authorized DMA software development and reverse-engineering workflows using [Metick/DMALibrary](https://github.com/Metick/DMALibrary).

## What This Is

`dma-ai-toolkit` teaches agents how to use DMALibrary from verified source, not guessed APIs. It provides context packs, API indexes, validators, templates, and agent skills.

## What This Is Not

This is not a target-specific offset pack, anti-cheat bypass guide, or turnkey cheating application. Use it only on owned systems, labs, and authorized research targets.

## AI Start Here

1. Read `docs/AI_AGENT_OPERATING_MANUAL.md`.
2. Read `docs/llms-dma.md`.
3. For ecosystem context, read `docs/research/github-dma-ecosystem.md` and `docs/research/unknowncheats-dma-lessons.md`.
4. For DMALibrary usage, read the matching cookbook under `docs/dmalibrary/`.
5. Verify every DMALibrary symbol against `knowledge/dmalibrary-api-index.json`.
6. Check cited research in `knowledge/research-sources.json`.
7. Run `python tools/validate-cpp-answer.py <file>` before trusting generated answers or snippets.

## Optional DMALibrary Source

DMALibrary is an optional submodule:

```bash
git submodule add https://github.com/Metick/DMALibrary third_party/DMALibrary
git submodule update --init --recursive
```

The toolkit records source provenance in `knowledge/provenance.json`.

## Quick Checks

```bash
python -m pytest
python tools/validate-cpp-answer.py README.md
```

## License

MIT. DMALibrary is MIT licensed by its upstream project.
