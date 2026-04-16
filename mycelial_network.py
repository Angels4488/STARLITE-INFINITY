from typing import Any, Dict

class MycelialNetworkProtocol:
    def __init__(self, node_id: str):
        self.node_id = node_id

    def request_hive_mind(self, q: Any) -> Dict[str, Any]:
        return {"consensus": f"Hive echo from {self.node_id}: {q}"}
