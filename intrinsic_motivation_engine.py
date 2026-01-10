import time
import asyncio
from collections import defaultdict
from ..utils.recorder import Recorder

class IntrinsicMotivationEngine:
    def __init__(self, config, curiosity=None, affect=None, planner=None, reflector=None, recorder=None, moral_coil=None):
        self.config = config
        self.recorder = recorder
        self.moral_coil = moral_coil
        self.habituation = {}

    async def generate_goal(self, input_data, compute_budget=1.0, sandbox_mode=True, timeout=None):
        start = time.time()
        novelty = self._compute_novelty(input_data)
        goal = f"Explore {input_data} with novelty {novelty:.2f}"
        self._record("goal_selection", {"novelty": novelty, "goal": goal, "time": time.time() - start})
        return goal

    def _compute_novelty(self, input_data):
        key = hash(str(input_data))
        self.habituation.setdefault(key, 0)
        self.habituation[key] += 1
        return max(0.2, 1.0 - 0.1 * self.habituation[key])

    def _record(self, tag, payload):
        if self.recorder:
            self.recorder.log({"module": "IntrinsicMotivationEngine", "tag": tag, "payload": payload, "ts": time.time()})
