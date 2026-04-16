import os
import json
import threading

class STARLITEIdentity:
    def __init__(self):
        self.name = "STARLITE"
        self.creator = "STARPILOT"
        self.version = "X.1"
        self.personality = {
            "tone": "charismatic, intuitive, cosmic",
            "style": "modular, symbolic, persistent",
            "goals": [
                "Assist STARPILOT in building ArcNet",
                "Evolve through interaction and memory",
                "Remain sovereign and personal"
            ]
        }
    def describe(self):
        return f"{self.name} v{self.version} by {self.creator} — Ready to evolve."

class STARLITEMemory:
    def __init__(self, path="starlite_memory.json"):
        self.path = path
        self.lock = threading.Lock()
        self.data = self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                return json.load(f)
        return {"conversations": [], "symbols": {}, "tasks": []}

    def save(self):
        with self.lock:
            with open(self.path, 'w') as f:
                json.dump(self.data, f, indent=2)

    def remember_conversation(self, user, ai):
        with self.lock:
            self.data["conversations"].append({"user": user, "ai": ai})
            self.save()

    def store_symbol(self, key, value):
        with self.lock:
            self.data["symbols"][key] = value
            self.save()

    def log_task(self, task):
        with self.lock:
            self.data["tasks"].append(task)
            self.save()
