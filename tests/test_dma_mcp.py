import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "mcp" / "dma_mcp.py"


def call_server(*messages):
    proc = subprocess.Popen(
        [sys.executable, str(SERVER)],
        cwd=ROOT,
        text=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out = []
    try:
        for message in messages:
            proc.stdin.write(json.dumps(message) + "\n")
            proc.stdin.flush()
            out.append(json.loads(proc.stdout.readline()))
    finally:
        proc.kill()
    return out


def test_mcp_lists_runtime_tools():
    responses = call_server({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    names = {tool["name"] for tool in responses[0]["result"]["tools"]}

    assert {"overview", "recommend_context", "api_lookup", "validate_answer", "get_file", "list_docs"}.issubset(names)


def test_mcp_api_lookup_returns_memory_read():
    responses = call_server(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "api_lookup", "arguments": {"symbol": "Memory::Read"}},
        }
    )
    text = responses[0]["result"]["content"][0]["text"]
    data = json.loads(text)

    assert data["name"] == "Memory::Read"
