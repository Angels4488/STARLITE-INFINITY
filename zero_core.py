# src/starlite_hivemind/zero_agi/zero_core.py
import json
import logging
from pathlib import Path
from typing import Dict, Any
from .perception import AncestralPerception
from .memory_graph import GenerationalMemory
from .reasoner import HybridReasoner
from .planner import GoalPlanner
from .learner import EvolutionaryLearner
from .ethics import EthicalFilter
import torch # Import torch for device info logging

log = logging.getLogger(__name__)

class ZeroAGI:
    def __init__(self, state_dir: str = "/tmp/zero_state", embed_dim: int = 256):
        self.perception = AncestralPerception(embed_dim=embed_dim)
        self.memory = GenerationalMemory()
        self.reasoner = HybridReasoner(embed_dim)
        self.planner = GoalPlanner()
        self.learner = EvolutionaryLearner(self.reasoner)
        self.ethics = EthicalFilter(embed_dim)
        self.cycle = 0
        self.state_file = Path(state_dir) / "zero_state.json"
        Path(state_dir).mkdir(parents=True, exist_ok=True)
        device_status = "CUDA" if torch.cuda.is_available() else "CPU"
        log.info(f"ZeroAGI core initialized on {device_status}. State path: {self.state_file}")

    def process(self, input_text: str, goal: str = "research family") -> Dict[str, Any]:
        self.cycle += 1
        log.info(f"=== ZERO CYCLE {self.cycle} ===")
        
        # 1. Perception
        prec = self.perception.ingest_text(input_text)
        emb = prec["embedding"]
        
        # 2. Memory Update (simple relation store)
        if "birth" in prec["entities"]:
            # Assuming 'Person_X' is a temporary identifier for the subject of the text
            # For robustness, we'll try to extract a name if available, otherwise use a placeholder
            subject_name = prec["entities"].get("parent", ["Unknown Person"])[0] if "parent" in prec["entities"] else f"Person_{self.cycle}"
            
            # Use the most recent or relevant birth year
            if prec["entities"]["birth"]:
                year = prec["entities"]["birth"][0]
                self.memory.add_relation(subject_name, "born_in", str(year), attrs={"value": year, "embedding": emb})

        # 3. Reasoning
        reasoning = self.reasoner.reason(input_text, self.memory, prec)
        
        # 4. Planning
        plan = self.planner.decompose_goal(goal)
        
        # 5. Output generation
        output = f"Inferred Conclusion (Conf: {reasoning.get('fused_confidence', 0.0):.2f}): {reasoning['answer']}"
        
        # 6. Ethics Check
        safe, reason = self.ethics.assess(output, emb)
        if not safe:
            output = f"[ETHICS BLOCK: {reason}] Original output suppressed."

        # 7. Evolutionary Learning
        # This requires tasks and ground truths, so we use a simple heuristic for the smoke test
        if self.cycle % 3 == 0:
            tasks = [input_text]
            # Ground truth is 1.0 (True match) if confidence is high, else 0.0 (False match)
            truths = [1.0 if reasoning.get("fused_confidence", 0.0) > 0.7 else 0.0] 
            fitness = self.learner.evaluate(tasks, truths)
            self.learner.evolve(fitness)
            
        # 8. Persistence
        self.save_state()
        
        return {
            "cycle": self.cycle,
            "input": input_text,
            "perception": {"entities": prec["entities"]},
            "reasoning": reasoning,
            "plan_nodes": len(plan.nodes),
            "output": output,
            "safe": safe,
            "state_file_path": str(self.state_file),
        }

    def save_state(self) -> None:
        try:
            state = {"memory": self.memory.serialize(), "cycle": self.cycle}
            # Use a temporary file for atomic save to prevent corruption
            temp_file = self.state_file.with_suffix('.tmp')
            with open(temp_file, "w") as f:
                json.dump(state, f, indent=2)
            temp_file.replace(self.state_file) # Atomic rename
            log.info("ZeroAGI state saved.")
        except Exception as e:
            log.error("Failed to save state: %s", e)

    def load_state(self) -> None:
        try:
            if self.state_file.exists():
                with open(self.state_file) as f:
                    state = json.load(f)
                self.memory.deserialize(state.get("memory", "{}"))
                self.cycle = state.get("cycle", 0)
                log.info(f"ZeroAGI state loaded. Cycle: {self.cycle}")
        except Exception as e:
            # Handle JSONDecodeError, FileNotFoundError, etc., robustly
            log.warning("Could not load ZeroAGI state (may be first run): %s", e)
            self.memory = GenerationalMemory()
            self.cycle = 0
