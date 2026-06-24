import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "extract-dmalibrary-api.py"

spec = importlib.util.spec_from_file_location("extract_dmalibrary_api", MODULE_PATH)
extractor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extractor)


def test_extracts_class_methods_from_header(tmp_path):
    header = tmp_path / "Memory.h"
    header.write_text(
        """
class Memory
{
public:
    bool Init(std::string process_name, bool memMap = true, bool debug = false);
    template <typename T>
    T Read(uint64_t address);
    bool Read(uintptr_t address, void* buffer, size_t size) const;
};
""".strip()
    )

    index = extractor.build_index(tmp_path)

    assert index["source"] == "Metick/DMALibrary"
    symbols = {item["name"]: item for item in index["symbols"]}
    assert symbols["Memory::Init"]["kind"] == "method"
    assert symbols["Memory::Read"]["class"] == "Memory"
    assert "uint64_t address" in symbols["Memory::Read"]["signature"]


def test_cli_writes_json(tmp_path):
    source = tmp_path / "src"
    source.mkdir()
    (source / "Memory.h").write_text("class Memory { public: bool FixCr3(); };\n")
    output = tmp_path / "index.json"

    extractor.main([str(source), "--output", str(output)])

    data = json.loads(output.read_text())
    assert data["symbols"][0]["name"] == "Memory::FixCr3"
