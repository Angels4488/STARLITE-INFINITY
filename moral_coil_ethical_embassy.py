from typing import Any, Dict

class EthicalEmbassy:
    def __init__(self, core_values_hash: str):
        self.core_hash = core_values_hash

    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "ETHICS_OK", "safe": True}
