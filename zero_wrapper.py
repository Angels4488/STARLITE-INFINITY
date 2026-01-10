# src/starlite_hivemind/zero_agi/zero_wrapper.py
import logging
from typing import Dict, Any
from .zero_core import ZeroAGI
import torch # Import torch to check GPU status for logging

log = logging.getLogger(__name__)

class ZeroAgentWrapper:
    def __init__(self):
        self.name = "Zero"
        self.log = logging.getLogger(self.name)
        self.core = ZeroAGI()
        self.core.load_state()
        gpu_status = "GPU-Enabled" if torch.cuda.is_available() else "CPU-Only"
        self.log.info(f"ZeroAgentWrapper initialized. Status: {gpu_status}")

    def get_cognitive_bias(self) -> Dict[str, float]:
        # fixed bias for integration; could be derived from Zero internal state later
        return {
            "logic_drive": 1.5,
            "creativity_drive": 1.8,
            "survival_drive": 1.0,
            "virtue_drive": 1.0,
            "growth_drive": 1.0,
            "empathy_drive": 1.0,
        }

    def get_dominant_drive(self) -> str:
        # Based on the highest fixed bias value
        biases = self.get_cognitive_bias()
        return max(biases, key=biases.get)

    def think_and_act(self, text_prompt: str) -> Dict[str, Any]:
        self.log.info(f"ZeroAgent received prompt: '{text_prompt}'")
        try:
            result = self.core.process(text_prompt)
            response = result.get("output", "[ZERO] No output")
            return {
                "final_response": response,
                "source_agent": self.name,
                "dominant_drive": self.get_dominant_drive(),
                "cycle": result.get("cycle"),
                "confidence": result.get("reasoning", {}).get("fused_confidence", 0.0),
                "safe": result.get("safe", True),
            }
        except Exception as e:
            self.log.error(f"Error during ZeroAGI processing: {e}", exc_info=True)
            return {
                "final_response": f"[ZERO ERROR] Core processing failed: {type(e).__name__}",
                "source_agent": self.name,
                "dominant_drive": "survival_drive",
                "cycle": self.core.cycle,
                "confidence": 0.0,
                "safe": False,
            }
