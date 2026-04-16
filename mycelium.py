import collections
from pathlib import Path
from typing import Dict, Any

class MyceliumMemory:
    def __init__(self, storage_dir: str = "/mnt/blue_nvme/STARLITE/mycelium_memory"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.q_table = collections.defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])

    def add_memory(self, key: str, interaction: Dict[str, Any]):
        state = (hash(interaction.get("input", "")) % 4,)
        action = hash(interaction.get("input", "")) % 4
        self.q_table[state][action] += 0.1

    def recall(self, key: str) -> Dict[str, Any]:
        return {"q_table_size": len(self.q_table)}
