#include <DMALibrary/Memory/Memory.h>
#include <cstdint>
#include <iostream>
#include <string>

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: scatter-read-example <process.exe>\n";
        return 2;
    }

    Memory mem;
    const std::string process_name = argv[1];
    if (!mem.Init(process_name, true, false)) {
        std::cerr << "failed to initialize DMA\n";
        return 1;
    }

    const auto base = mem.GetBaseDaddy(process_name);
    if (base == 0) {
        std::cerr << "failed to resolve base address\n";
        return 1;
    }

    std::uint32_t header = 0;
    auto handle = mem.CreateScatterHandle();
    mem.AddScatterReadRequest(handle, base, &header, sizeof(header));
    mem.ExecuteReadScatter(handle);
    mem.CloseScatterHandle(handle);

    std::cout << "header=0x" << std::hex << header << "\n";
    return 0;
}
