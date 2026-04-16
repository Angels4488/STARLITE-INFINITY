
import numpy as np
import random
import time
import logging
from typing import Dict, Any, List, Tuple, Final, Optional

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - Swarm - %(message)s')
logger = logging.getLogger(__name__)

# Constants
ARBITRATION_RANGE: Final[float] = 0.5  # Micrometers
TARGET_COORDINATE: Final[np.ndarray] = np.array([10.0, 10.0, 10.0])
NANITE_MASS_BASE: Final[float] = 1.0

class Nanite:
    """Enhanced Nanite Unit with momentum-based decision making."""
    def __init__(self, nanite_id: int):
        self.id = nanite_id
        self.position = TARGET_COORDINATE + np.random.uniform(-2.0, 2.0, 3)
        self.is_in_contention = False
        self.momentum_score = 0.0
        self.action = "SEEK"
        self.is_entangled = False

    def update_state(self):
        """Update physics and cognitive state based on proximity to target."""
        distance = np.linalg.norm(self.position - TARGET_COORDINATE)

        # Physics-based momentum calculation
        velocity = max(0.1, 10.0 / (distance + 0.1))
        confidence = min(1.0, 0.5 + (1.0 / (distance + 1.0)))
        mass = NANITE_MASS_BASE + np.random.uniform(-0.05, 0.05)

        self.momentum_score = mass * velocity * confidence

        # Contention Logic
        if distance <= ARBITRATION_RANGE:
            self.is_in_contention = True
            self.action = "CONTENDING"
        else:
            self.is_in_contention = False
            self.action = "SEEK"

        # Movement simulation (simple attractor)
        if distance > 0.02:
            self.position += (TARGET_COORDINATE - self.position) * 0.05 * (velocity / 10.0)

class KineticArbiterProtocol:
    """Arbiter: Resolves swarm contention using the 'Highest Momentum Wins' principle."""
    def __init__(self):
        self.contention_pool: List[Nanite] = []
        self.winner: Optional[Nanite] = None

    def register(self, nanite: Nanite):
        if nanite.is_in_contention:
            self.contention_pool.append(nanite)

    def arbitrate(self) -> Optional[Nanite]:
        if not self.contention_pool:
            return None

        # The core enhancement: Selection based on kinetic potential
        self.winner = max(self.contention_pool, key=lambda n: n.momentum_score)
        self.winner.action = "PAYLOAD_RELEASE"

        for n in self.contention_pool:
            if n is not self.winner:
                n.action = "HOLD_POSITION"

        return self.winner

class QuantumEntanglementTaskProtocol:
    """Non-local consensus for High Value Targets (HVTs)."""
    HVT_THRESHOLD: float = 15.0 # Momentum requirement for HVT

    def __init__(self, hive_id: str):
        self.hive_id = hive_id
        self.assignments: Dict[int, int] = {} # {hvt_id: nanite_id}
        self.cohort: List[int] = []

    def entangle(self, nanite_id: int):
        if nanite_id not in self.cohort:
            self.cohort.append(nanite_id)
            logger.info(f"QETP: Nanite {nanite_id} entangled in Hive {self.hive_id}.")

    def assign_hvt(self, nanite_id: int, hvt_id: int) -> bool:
        """Instantaneous consensus logic: Lowest ID in cohort gets priority."""
        if hvt_id not in self.assignments:
            if nanite_id == min(self.cohort):
                self.assignments[hvt_id] = nanite_id
                logger.info(f"QETP: HVT {hvt_id} assigned to Nanite {nanite_id} via entanglement.")
                return True
        return False

class HiveMindOrchestrator:
    """Top-level manager for swarm operations."""
    def __init__(self, num_nanites: int = 20):
        self.swarm = [Nanite(i) for i in range(num_nanites)]
        self.arbiter = KineticArbiterProtocol()
        self.qetp = QuantumEntanglementTaskProtocol("Hive-01")

        # Entangle half the swarm
        for n in self.swarm[:num_nanites//2]:
            self.qetp.entangle(n.id)
            n.is_entangled = True

    def run_cycle(self, step: int):
        self.arbiter.contention_pool = []
        for n in self.swarm:
            n.update_state()
            self.arbiter.register(n)

        winner = self.arbiter.arbitrate()
        if winner:
            logger.info(f"Cycle {step}: Winner Nanite {winner.id} released payload (Momentum: {winner.momentum_score:.2f})")
            return True
        return False

if __name__ == "__main__":
    orchestrator = HiveMindOrchestrator(15)
    print("\n--- SWARM INTELLIGENCE SIMULATION ---")
    for i in range(1, 51):
        if orchestrator.run_cycle(i):
            print(f"Simulation converged at step {i}.")
            break
        if i % 10 == 0:
            print(f"Step {i}: Swarm converging on target...")
