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
