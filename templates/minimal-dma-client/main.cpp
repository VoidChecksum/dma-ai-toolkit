#include <DMALibrary/Memory/Memory.h>
#include <cstdint>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: minimal-dma-client <process.exe>\n";
        return 2;
    }

    Memory mem;
    const std::string process_name = argv[1];
    if (!mem.Init(process_name, true, false)) {
        std::cerr << "failed to initialize DMA for " << process_name << "\n";
        return 1;
    }

    const auto base = mem.GetBaseDaddy(process_name);
    if (base == 0) {
        std::cerr << "failed to resolve base address\n";
        return 1;
    }

    std::uint32_t mz = 0;
    if (!mem.Read(base, &mz, sizeof(mz))) {
        std::cerr << "failed to read base header\n";
        return 1;
    }

    std::cout << "base=0x" << std::hex << base << " header=0x" << mz << "\n";
    return 0;
}
