import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "validate-cpp-answer.py"

spec = importlib.util.spec_from_file_location("validate_cpp_answer", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)


def make_index(tmp_path):
    index = tmp_path / "index.json"
    index.write_text(json.dumps({"symbols": [{"name": "Memory::Read"}, {"name": "Memory::Init"}]}))
    unsupported = tmp_path / "unsupported.json"
    unsupported.write_text(json.dumps({"symbols": ["Memory::ReadString", "DMA::Read"]}))
    return index, unsupported


def test_rejects_unsupported_symbol(tmp_path):
    index, unsupported = make_index(tmp_path)
    answer = tmp_path / "answer.md"
    answer.write_text("```cpp\nauto name = mem.ReadString(addr);\n```\n")

    result = validator.validate(answer, index, unsupported)

    assert not result.ok
    assert "Memory::ReadString" in result.errors[0]


def test_accepts_documented_symbol(tmp_path):
    index, unsupported = make_index(tmp_path)
    answer = tmp_path / "answer.md"
    answer.write_text("```cpp\nauto value = mem.Read<int>(addr);\n```\n")

    result = validator.validate(answer, index, unsupported)

    assert result.ok
    assert result.errors == []


def test_does_not_treat_memory_read_as_dma_namespace(tmp_path):
    index, unsupported = make_index(tmp_path)
    answer = tmp_path / "answer.md"
    answer.write_text("```cpp\nauto value = mem.Read<int>(addr);\n```\n")

    result = validator.validate(answer, index, unsupported)

    assert result.ok
