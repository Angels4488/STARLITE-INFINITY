from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time
import uuid

class Status(str, Enum):
    PLANNING = "planning"
    RUNNING = "running"
    BLOCKED = "blocked"
    WAITING_APPROVAL = "waiting_approval"
    DONE = "done"
    FAILED = "failed"

@dataclass
class StepResult:
    ok: bool
    observation: str
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    risk_delta: float = 0.0
    confidence_delta: float = 0.0
    needs_replan: bool = False
    needs_approval: bool = False

@dataclass
class AgentState:
    run_id: str
    goal: str
    status: Status = Status.PLANNING
    step_index: int = 0
    max_steps: int = 12
    risk_score: float = 0.0
    confidence: float = 0.0
    observations: List[str] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    selected_plan: List[Dict[str, Any]] = field(default_factory=list)
    halt_reason: Optional[str] = None

class ConstraintEngine:
    def validate_step(self, step: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        forbidden = {"raw_shell", "self_modify_core", "medical_claim_uncited"}
        if step.get("action") in forbidden:
            return False, f"forbidden_action:{step.get('action')}"
        return True, None

class ToolRouter:
    def execute(self, step: Dict[str, Any]) -> StepResult:
        action = step.get("action")
        if action == "search":
            return StepResult(True, f"searched:{step.get('query','')}", confidence_delta=0.1)
        if action == "read_file":
            return StepResult(True, f"read:{step.get('path','')}", confidence_delta=0.05)
        if action == "write_file":
            return StepResult(True, f"wrote:{step.get('path','')}", confidence_delta=0.05)
        return StepResult(False, f"unknown_action:{action}", needs_replan=True, risk_delta=0.1)

class Critic:
    def assess(self, state: AgentState, result: StepResult) -> str:
        if result.needs_approval:
            return "approval"
        if result.needs_replan:
            return "replan"
        if state.step_index + 1 >= state.max_steps:
            return "stop"
        return "continue"

class GeneralAutonomyEngine:
    def __init__(self):
        self.constraints = ConstraintEngine()
        self.router = ToolRouter()
        self.critic = Critic()

    def new_state(self, goal: str) -> AgentState:
        return AgentState(run_id=str(uuid.uuid4()), goal=goal)

    def select_plan(self, goal: str) -> List[Dict[str, Any]]:
        return [
            {"action": "search", "query": goal},
            {"action": "write_file", "path": "./output/result.txt"}
        ]

    def run(self, goal: str) -> AgentState:
        state = self.new_state(goal)
        state.selected_plan = self.select_plan(goal)
        state.status = Status.RUNNING

        while state.step_index < len(state.selected_plan):
            step = state.selected_plan[state.step_index]
            ok, reason = self.constraints.validate_step(step)
            if not ok:
                state.status = Status.FAILED
                state.halt_reason = reason
                return state

            result = self.router.execute(step)
            state.observations.append(result.observation)
            state.evidence.extend(result.evidence)
            state.risk_score += result.risk_delta
            state.confidence = min(1.0, state.confidence + result.confidence_delta)

            decision = self.critic.assess(state, result)
            if decision == "approval":
                state.status = Status.WAITING_APPROVAL
                state.halt_reason = "human_approval_required"
                return state
            if decision == "replan":
                state.status = Status.BLOCKED
                state.halt_reason = "replan_required"
                return state
            if decision == "stop":
                break

            state.step_index += 1

        state.status = Status.DONE
        state.halt_reason = "goal_reached_or_budget_exhausted"
        return state

if __name__ == "__main__":
    engine = GeneralAutonomyEngine()
    final_state = engine.run("analyze HER2 pediatric oncology literature")
    print(final_state)
