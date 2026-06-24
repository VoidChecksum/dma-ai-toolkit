# Memory Class Notes

## Initialization

`Memory::Init(std::string process_name, bool memMap = true, bool debug = false)` initializes DMA access for a process name.

## Reads

Use `Memory::Read<T>(uint64_t address)` for simple typed reads and `Memory::Read(uintptr_t address, void* buffer, size_t size)` for explicit buffers.

## Writes

Use writes only in authorized labs. Prefer examples that demonstrate validation and lifecycle, not target-specific mutation.

## Scatter I/O

Create a scatter handle, add requests, execute the requests, then close the handle.
