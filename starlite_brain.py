#!/usr/bin/env python3
"""Portable STARLITE identity and memory layer over the Ollama agent host."""

from __future__ import annotations

import argparse
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from starlite_agent import StarliteAgent


ROOT = Path(__file__).resolve().parent
DEFAULT_MEMORY_PATH = ROOT / "memory" / "starlite_brain.json"
DEVICE_PROFILES = {
    "workstation": {"label": "STARLITE workstation", "role": "primary host"},
    "samsung-galaxy-tab-a9-plus": {"label": "Samsung Galaxy Tab A9+", "role": "mobile companion"},
    "motorola-razr-2025": {"label": "Motorola Razr 2025", "role": "mobile companion"},
}
MEMORY_TYPES = ("episodic", "semantic", "emotional", "relational")


class StarliteBrain:
    """Custom STARLITE state that can use any reachable Ollama host."""

    def __init__(
        self,
        device_id: str | None = None,
        memory_path: str | Path | None = None,
        agent: StarliteAgent | None = None,
    ) -> None:
        self.device_id = device_id or os.getenv("STARLITE_DEVICE_ID", "workstation")
        self.profile = DEVICE_PROFILES.get(self.device_id, {"label": self.device_id, "role": "unregistered device"})
        self.memory_path = Path(memory_path or os.getenv("STARLITE_MEMORY_PATH", DEFAULT_MEMORY_PATH))
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.agent = agent or StarliteAgent()
        self.state = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.memory_path.exists():
            return self._empty_state()
        try:
            loaded = json.loads(self.memory_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"cannot load STARLITE memory at {self.memory_path}: {exc}") from exc
        if not isinstance(loaded, dict):
            raise RuntimeError("STARLITE memory must contain a JSON object")
        loaded.setdefault("identity", "STARLITE-INFINITY")
        loaded.setdefault("memories", [])
        loaded.setdefault("history", [])
        loaded.setdefault("memory_banks", {memory_type: [] for memory_type in MEMORY_TYPES})
        for memory_type in MEMORY_TYPES:
            if not isinstance(loaded["memory_banks"].get(memory_type), list):
                loaded["memory_banks"][memory_type] = []
        if not loaded["memory_banks"]["episodic"] and loaded["memories"]:
            loaded["memory_banks"]["episodic"] = list(loaded["memories"])
        return loaded

    @staticmethod
    def _empty_state() -> dict[str, Any]:
        return {
            "identity": "STARLITE-INFINITY",
            "memories": [],
            "memory_banks": {memory_type: [] for memory_type in MEMORY_TYPES},
            "history": [],
        }

    def _save(self) -> None:
        temporary_path = self.memory_path.with_suffix(".tmp")
        temporary_path.write_text(json.dumps(self.state, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        temporary_path.replace(self.memory_path)

    def remember(self, note: str, memory_type: str = "semantic") -> None:
        if memory_type not in MEMORY_TYPES:
            raise ValueError(f"memory_type must be one of: {', '.join(MEMORY_TYPES)}")
        memory = {"note": note, "memory_type": memory_type, "device_id": self.device_id, "timestamp": datetime.now(timezone.utc).isoformat()}
        with self.lock:
            self.state["memories"].append(memory)
            self.state["memory_banks"][memory_type].append(memory)
            self._save()

    def recall(self, memory_type: str | None = None, limit: int = 12) -> list[dict[str, Any]]:
        if memory_type is not None and memory_type not in MEMORY_TYPES:
            raise ValueError(f"memory_type must be one of: {', '.join(MEMORY_TYPES)}")
        if limit < 1:
            raise ValueError("limit must be positive")
        with self.lock:
            memories = self.state["memories"] if memory_type is None else self.state["memory_banks"][memory_type]
            return json.loads(json.dumps(memories[-limit:]))

    def export_state(self) -> dict[str, Any]:
        with self.lock:
            return json.loads(json.dumps(self.state))

    def import_state(self, state: dict[str, Any]) -> None:
        if not isinstance(state, dict) or not isinstance(state.get("memories", []), list) or not isinstance(state.get("history", []), list):
            raise ValueError("STARLITE state must contain memories and history lists")
        with self.lock:
            imported = self._empty_state()
            imported["memories"] = state["memories"]
            imported["history"] = state["history"]
            imported["memory_banks"] = state.get("memory_banks", {memory_type: [] for memory_type in MEMORY_TYPES})
            for memory_type in MEMORY_TYPES:
                imported["memory_banks"].setdefault(memory_type, [])
            self.state = imported
            self._save()

    def chat(self, user_text: str) -> str:
        with self.lock:
            context = {memory_type: self.state["memory_banks"][memory_type][-3:] for memory_type in MEMORY_TYPES}
            history = self.state["history"][-20:]
        prompt = (
            f"You are operating as STARLITE-INFINITY on {self.profile['label']} ({self.profile['role']}). "
            "Use the supplied memory as context, but do not claim capabilities it does not establish.\n"
            f"Shared STARLITE memory:\n{json.dumps(context, ensure_ascii=True)}\n\nUser request:\n{user_text}"
        )
        answer = self.agent.chat(prompt, history=history)
        with self.lock:
            self.state["history"].extend([
                {"role": "user", "content": user_text, "device_id": self.device_id},
                {"role": "assistant", "content": answer, "device_id": self.device_id},
            ])
            self._save()
        return answer


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the portable STARLITE custom brain")
    parser.add_argument("prompt", nargs="?", help="one prompt; omit for interactive mode")
    parser.add_argument("--device", default=None, choices=sorted(DEVICE_PROFILES))
    parser.add_argument("--memory", default=None, help="shared STARLITE JSON state path")
    args = parser.parse_args()
    brain = StarliteBrain(device_id=args.device, memory_path=args.memory)
    if args.prompt:
        print(brain.chat(args.prompt))
        return
    while True:
        try:
            prompt = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if prompt.lower() in {"exit", "quit"}:
            return
        try:
            print(f"starlite> {brain.chat(prompt)}")
        except RuntimeError as exc:
            print(f"starlite error> {exc}")


if __name__ == "__main__":
    main()