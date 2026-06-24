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


def test_rejects_target_offset_dump(tmp_path):
    index, unsupported = make_index(tmp_path)
    answer = tmp_path / "answer.md"
    answer.write_text(
        """
| name | offset |
|---|---:|
| a | 0x11111111 |
| b | 0x22222222 |
| c | 0x33333333 |
| d | 0x44444444 |
| e | 0x55555555 |
| f | 0x66666666 |
""".strip()
    )

    result = validator.validate(answer, index, unsupported)

    assert not result.ok
    assert any("offset dump" in error for error in result.errors)


def test_rejects_anti_cheat_guarantee_language(tmp_path):
    index, unsupported = make_index(tmp_path)
    answer = tmp_path / "answer.md"
    answer.write_text("This DMA method is undetected and works on EAC.\n")

    result = validator.validate(answer, index, unsupported)

    assert not result.ok
    assert any("unsafe guarantee" in error for error in result.errors)


def test_accepts_warning_about_bad_guarantees(tmp_path):
    index, unsupported = make_index(tmp_path)
    answer = tmp_path / "answer.md"
    answer.write_text("Do not claim a method is undetected or works on EAC.\n")

    result = validator.validate(answer, index, unsupported)

    assert result.ok
