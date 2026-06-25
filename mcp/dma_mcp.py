#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import dma_core

TOOLS = [
    {"name": "overview", "description": "Return DMA toolkit contract and start files", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "recommend_context", "description": "Recommend docs for a DMA task", "inputSchema": {"type": "object", "properties": {"task": {"type": "string"}}, "required": ["task"]}},
    {"name": "api_lookup", "description": "Look up a source-backed DMALibrary symbol", "inputSchema": {"type": "object", "properties": {"symbol": {"type": "string"}}, "required": ["symbol"]}},
    {"name": "validate_answer", "description": "Validate a Markdown/C++ answer file", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "get_file", "description": "Read a repository file", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "list_docs", "description": "List indexed docs", "inputSchema": {"type": "object", "properties": {}}},
]


def content(value) -> dict:
    text = value if isinstance(value, str) else json.dumps(value, indent=2, sort_keys=True)
    return {"content": [{"type": "text", "text": text}]}


def handle_call(name: str, args: dict) -> dict:
    if name == "overview":
        return content(dma_core.overview(ROOT))
    if name == "recommend_context":
        return content(dma_core.recommend_context(args["task"], ROOT))
    if name == "api_lookup":
        return content(dma_core.api_lookup(ROOT, args["symbol"]))
    if name == "validate_answer":
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "validate-cpp-answer.py"), args["path"]],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        return content({"ok": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr})
    if name == "get_file":
        return content(dma_core.read_repo_file(ROOT, args["path"]))
    if name == "list_docs":
        return content(dma_core.list_docs(ROOT))
    raise ValueError(f"unknown tool: {name}")


def handle(message: dict) -> dict:
    method = message.get("method")
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "dma-ai-toolkit", "version": "0.1.0"},
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": message.get("id"), "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = message.get("params", {})
        try:
            result = handle_call(params.get("name", ""), params.get("arguments", {}))
            return {"jsonrpc": "2.0", "id": message.get("id"), "result": result}
        except Exception as error:
            return {"jsonrpc": "2.0", "id": message.get("id"), "error": {"code": -32000, "message": str(error)}}
    return {"jsonrpc": "2.0", "id": message.get("id"), "error": {"code": -32601, "message": "method not found"}}


def main() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        print(json.dumps(handle(json.loads(line))), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
