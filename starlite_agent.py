#!/usr/bin/env python3
"""Small Ollama agent with explicit, host-controlled repository tools."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any, Callable

import requests


ROOT = Path(__file__).resolve().parent
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.getenv("STARLITE_MODEL", "starlite-infinity")


def _inside_root(path: str) -> Path:
    candidate = (ROOT / path).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError("path must stay inside the STARLITE-INFINITY repository") from exc
    return candidate


def read_file(path: str, max_bytes: int = 20000) -> dict[str, Any]:
    """Read a bounded UTF-8 text file from the repository."""
    target = _inside_root(path)
    if not target.is_file():
        raise ValueError(f"not a file: {path}")
    data = target.read_bytes()
    truncated = len(data) > max_bytes
    return {"path": str(target.relative_to(ROOT)), "content": data[:max_bytes].decode("utf-8", errors="replace"), "truncated": truncated}


def list_directory(path: str = ".") -> dict[str, Any]:
    """List one repository directory without following symlinks."""
    target = _inside_root(path)
    if not target.is_dir():
        raise ValueError(f"not a directory: {path}")
    entries = []
    for entry in sorted(target.iterdir(), key=lambda item: item.name.lower()):
        entries.append({"name": entry.name, "kind": "directory" if entry.is_dir() else "file"})
    return {"path": str(target.relative_to(ROOT)) or ".", "entries": entries[:200]}


SAFE_COMMANDS = {"pwd", "ls", "find", "rg", "git", "python", "python3"}
BLOCKED_TOKENS = {";", "&&", "||", ">", ">>", "<", "|", "sudo", "curl", "wget", "rm", "mv", "chmod", "chown", "pip", "npm", "ssh"}
BLOCKED_ARGUMENTS = {"-c", "--command", "-exec", "-execdir", "-delete", "commit", "reset", "checkout", "restore", "clean", "push", "pull", "fetch"}
READ_ONLY_GIT_COMMANDS = {"status", "diff", "log", "show"}


def run_shell(command: str, timeout_seconds: int = 20) -> dict[str, Any]:
    """Run a bounded, non-mutating inspection/test command in the repository."""
    parts = shlex.split(command)
    if not parts or parts[0] not in SAFE_COMMANDS:
        raise ValueError(f"command must start with one of: {', '.join(sorted(SAFE_COMMANDS))}")
    lowered_parts = [token.lower() for token in parts]
    if any(token in BLOCKED_TOKENS or token in BLOCKED_ARGUMENTS for token in lowered_parts):
        raise ValueError("command contains a blocked shell token or operation")
    if any(token.startswith("/") or token == ".." or token.startswith("../") for token in parts[1:]):
        raise ValueError("command paths must stay inside the repository")
    if parts[0] == "git" and (len(parts) < 2 or parts[1] not in READ_ONLY_GIT_COMMANDS):
        raise ValueError("git is limited to status, diff, log, and show")
    if parts[0] in {"python", "python3"} and parts[1:] not in [["-m", "py_compile", "starlite_agent.py"], ["-m", "unittest", "test_starlite_agent"]]:
        raise ValueError("python is limited to the agent syntax check and agent unit tests")
    if not 1 <= timeout_seconds <= 60:
        raise ValueError("timeout_seconds must be between 1 and 60")
    completed = subprocess.run(
        parts,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
        env={"PATH": os.getenv("PATH", ""), "PYTHONPATH": str(ROOT)},
    )
    return {"command": command, "returncode": completed.returncode, "stdout": completed.stdout[-12000:], "stderr": completed.stderr[-12000:]}


TOOL_SPECS = [
    {"type": "function", "function": {"name": "read_file", "description": "Read a UTF-8 text file inside the repository.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "max_bytes": {"type": "integer", "minimum": 1, "maximum": 20000}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "list_directory", "description": "List entries in a repository directory.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {"name": "run_shell", "description": "Run an explicitly requested read-only inspection or test command in the repository.", "parameters": {"type": "object", "properties": {"command": {"type": "string"}, "timeout_seconds": {"type": "integer", "minimum": 1, "maximum": 60}}, "required": ["command"]}}},
]

TOOL_FUNCTIONS: dict[str, Callable[..., dict[str, Any]]] = {"read_file": read_file, "list_directory": list_directory, "run_shell": run_shell}


class StarliteAgent:
    def __init__(self, model: str = DEFAULT_MODEL, base_url: str = OLLAMA_URL, max_tool_rounds: int = 6) -> None:
        if max_tool_rounds < 1:
            raise ValueError("max_tool_rounds must be positive")
        self.model = model
        self.chat_url = f"{base_url.rstrip('/')}/api/chat"
        self.max_tool_rounds = max_tool_rounds

    def chat(self, user_text: str, history: list[dict[str, Any]] | None = None) -> str:
        messages = list(history or []) + [{"role": "user", "content": user_text}]
        for _ in range(self.max_tool_rounds):
            try:
                response = requests.post(self.chat_url, json={"model": self.model, "messages": messages, "tools": TOOL_SPECS, "stream": False}, timeout=120)
                response.raise_for_status()
                message = response.json().get("message", {})
            except requests.RequestException as exc:
                raise RuntimeError(f"Ollama is unavailable at {self.chat_url}. Start Ollama and create model '{self.model}'.") from exc
            except (ValueError, AttributeError, TypeError) as exc:
                raise RuntimeError("Ollama returned an invalid /api/chat response") from exc
            if not isinstance(message, dict):
                raise RuntimeError("Ollama returned an invalid chat message")
            tool_calls = message.get("tool_calls") or []
            messages.append(message)
            if not tool_calls:
                return message.get("content", "").strip()
            for call in tool_calls:
                function = call.get("function", {})
                name = function.get("name")
                arguments = function.get("arguments") or {}
                try:
                    if isinstance(arguments, str):
                        arguments = json.loads(arguments)
                    if not isinstance(arguments, dict):
                        raise ValueError("tool arguments must be a JSON object")
                    result = TOOL_FUNCTIONS[name](**arguments)
                except (json.JSONDecodeError, KeyError, TypeError, ValueError, OSError, subprocess.TimeoutExpired) as exc:
                    result = {"error": str(exc)}
                messages.append({"role": "tool", "content": json.dumps(result)})
        raise RuntimeError("Ollama exceeded the maximum number of tool rounds")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with the local STARLITE Ollama agent")
    parser.add_argument("prompt", nargs="?", help="one prompt; omit for interactive mode")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()
    agent = StarliteAgent(model=args.model)
    if args.prompt:
        print(agent.chat(args.prompt))
        return
    history: list[dict[str, Any]] = []
    while True:
        try:
            prompt = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if prompt.lower() in {"exit", "quit"}:
            break
        answer = agent.chat(prompt, history)
        print(f"starlite> {answer}")
        history.extend([{"role": "user", "content": prompt}, {"role": "assistant", "content": answer}])


if __name__ == "__main__":
    main()