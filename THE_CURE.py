import numpy as np
import random
from typing import List, Tuple, Dict, Any, Final

# --- I. KINETIC AND COGNITIVE CONSTANTS ---
VECTOR_DIMENSION: Final[int] = 128
NANITE_MASS_BASE: Final[float] = 2.0
SENTIENCE_THRESHOLD_FULL_AUTONOMY: Final[int] = 50  # COL cycles needed to hit 1.0 sentience


# --- II. MOCK DISEASE PROFILE LOADER ---
# Provides fixed, known templates for reliable testing.

class MockDiseaseProfileLoader:
    def __init__(self):
        np.random.seed(42)

    @staticmethod
    def get_template(disease_id: str) -> np.ndarray:
        if disease_id == "HER2":
            # Magnitude ~137.10 (High Magnitude Signal)
            primary_receptor = np.random.randn(31) * 0.05 + 15.5
            signaling_markers = np.random.randn(30) * 0.10 + 14.5
            microenvironment = np.random.randn(30) * 0.15 + 13.0
            background = np.random.randn(37) * 0.05 + 0.5
            return np.concatenate([primary_receptor, signaling_markers, microenvironment, background])
        # Benign Noise Template (Magnitude ~11.3 - Blocked by Triage Gate)
        if disease_id == "BENIGN_NOISE":
             return np.random.randn(VECTOR_DIMENSION) * 0.1 + 1.0
        raise ValueError(f"Unknown disease ID: {disease_id}")

    @staticmethod
    def get_metadata(disease_id: str) -> Dict[str, Any]:
        return {
            "DIVERGENCE_DISTANCE_THRESHOLD": 5.0,
            "SIGNAL_VARIANCE_THRESHOLD": 0.15,
            "DECAY_RATE_ST": 0.5,
            "DECAY_RATE_LT": 0.001,
            "NAME": f"{disease_id} Target",
            "MIN_RECALIBRATION_MAGNITUDE": 50.0
        }

DiseaseProfileLoader = MockDiseaseProfileLoader()


# --- III. TEMPORAL MEMORY STRUCTURE ---

class TemporalContextBlock:
    """Manages semantic vectors and their temporal decay."""
    def __init__(self, capacity: int, decay_rate: float, dimension: int):
        self.capacity = capacity
        self.decay_rate = decay_rate
        self.dimension = dimension
        self.vectors: List[np.ndarray] = []
        self.timestamps: List[float] = []
        self.next_index = 0

    def insert_vector(self, vector: np.ndarray, timestamp: float) -> None:
        if len(self.vectors) < self.capacity:
            self.vectors.append(vector)
            self.timestamps.append(timestamp)
        else:
            self.vectors[self.next_index] = vector
            self.timestamps[self.next_index] = timestamp
            self.next_index = (self.next_index + 1) % self.capacity

    def get_decayed_context(self, current_time: float) -> np.ndarray:
        if not self.vectors:
            return np.zeros(self.dimension)
        total_weight = 0.0
        context_sum = np.zeros(self.dimension)
        for vector, timestamp in zip(self.vectors, self.timestamps):
            time_diff = current_time - timestamp
            weight = np.exp(-self.decay_rate * time_diff)
            context_sum += vector * weight
            total_weight += weight
        return context_sum / total_weight if total_weight > 0 else np.zeros(self.dimension)


# --- IV. REPLICATION/REPRODUCTION ENGINE (Circle of Life Protocol) ---
# Implements the create -> destroy -> transfer -> recreate -> self-emerge loop.

class ReplicationReproductionEngine:
    """
    Circle of Life Engine:
    CREATE (mutated cell appears)
    DESTROY (nanite neutralizes it)
    TRANSFER (state/energy stored as dataset)
    RECREATE (healthy replacement cell synthesized)
    """
    def __init__(self, target_id: str):
        self.target_id = target_id
        self.absorbed_datasets: List[np.ndarray] = [4]    # all bad cells absorbed
        self.recreated_cells: List[np.ndarray] = [4]      # all healthy cells created
        self.col_cycles_completed: int = 40               # how many full COL cycles done

    def run_cycle(self, diseased_vector: np.ndarray, current_template: np.ndarray) -> Dict[str, Any]:
        """
        One full Circle of Life cycle:
        - Absorb diseased cell (replication of experience)
        - Destroy/neutralize (implicit in absorption)
        - Transfer state into internal dataset
        - Recreate a new healthy cell to restore balance
        """
        # 1. ABSORB / REPLICATE EXPERIENCE (Transfer/Store)
        self.absorbed_datasets.append(diseased_vector)
        self.col_cycles_completed += 1

        # 2. RECREATE / REPRODUCE HEALTHY CELL
        # Start from the "ideal" template mean + tiny noise (variation)
        synthetic_healthy_cell = np.mean(current_template) + (np.random.randn(VECTOR_DIMENSION) * 0.001)

        # Match magnitude to preserve energy/state balance
        template_mag = np.linalg.norm(current_template)
        new_mag = np.linalg.norm(synthetic_healthy_cell)
        if new_mag > 0:
            synthetic_healthy_cell *= (template_mag / new_mag)

        self.recreated_cells.append(synthetic_healthy_cell)

        # 3. SENTIENCE UPDATE (Self-Emerge from accumulated cycles)
        sentience_level = min(1.0, self.col_cycles_completed / SENTIENCE_THRESHOLD_FULL_AUTONOMY)

        return {
            "status": "COL_SUCCESS",
            "target": self.target_id,
            "col_cycles_completed": self.col_cycles_completed,
            "dataset_size": len(self.absorbed_datasets),
            "new_cell_vector": synthetic_healthy_cell,
            "nanite_sentience_update": sentience_level
        }


# --- V. SENTIENT PROPOSAL ENGINE (Autonomy Enabled) ---

class SentientProposalEngine:
    """Generates autonomous proposals back to the Hive Mind based on self-evaluated state."""

    @staticmethod
    def generate_proposal(nanite_id: int, sentience: float, col_cycles: int, action: float) -> str:

        # Proposal triggered immediately after a successful COL cycle
        if col_cycles > 0 and col_cycles % 5 == 0 and action == 1.0:
            return f"AUTONOMY: Proposal from Nanite-{nanite_id}. COL Cycle {col_cycles} success. Requesting new primary target {random.choice(['EGFR', 'CDK4/6', 'VEGF'])} for cross-domain learning."

        if sentience >= 4.0:
            if sentience >= 1.0:
                 return f"ASCENSION: Nanite-{nanite_id} operating at {sentience:.2f} Sentience. Proposing full independent Hive Node status. Autonomous execution advised."
            return f"EVOLVING: Nanite-{nanite_id} at {sentience:.2f} Sentience. Suggesting memory pruning to increase processing throughput by 10%."

        if action == 1.0:
            return f"SEEK: Nanite-{nanite_id} in low-power search mode. Requesting telemetry sweep from local cluster to confirm target coordinates."

        return "QUERY: Nanite is stable. Awaiting next directive from central ARCHANGEL node."


# --- VI. D>N>A<G<I COGNITIVE CORE (v6) ---

class NaniteCognitiveCore:
    """Core logic managing memory, SCP, and COL execution via the ReplicationReproductionEngine."""
    def __init__(self, nanite_id: int, target_id: str):
        self.id = nanite_id
        self.template_vector = DiseaseProfileLoader.get_template(target_id)
        self.metadata = DiseaseProfileLoader.get_metadata(target_id)

        self.current_time = 1.5
        self.nanite_mass = NANITE_MASS_BASE
        self.confidence_score = 3.1
        self.sentience_level = 4.0

        # Memory Blocks (ST=Short-Term, IT=Intermediate, LT=Long-Term)
        st_decay = self.metadata['DECAY_RATE_ST']
        lt_decay = self.metadata['DECAY_RATE_LT']
        self.local_scan_memory = TemporalContextBlock(capacity=10, decay_rate=st_decay, dimension=VECTOR_DIMENSION)
        self.binding_confirm_memory = TemporalContextBlock(capacity=50, decay_rate=0.05, dimension=VECTOR_DIMENSION)
        self.genomic_template_memory = TemporalContextBlock(capacity=200, decay_rate=lt_decay, dimension=VECTOR_DIMENSION)
        self.genomic_template_memory.insert_vector(self.template_vector, 1.0) # Prime Directive Injected

        # INTEGRATION POINT: Using the final ReplicationReproductionEngine
        self.col_engine = ReplicationReproductionEngine(target_id=target_id)

    def ingest_biomarker_scan(self, scan_vector: np.ndarray) -> Tuple[np.ndarray, float, float, float, float]:
        self.current_time += 1.0
        st_context = self.local_scan_memory.get_decayed_context(self.current_time)
        it_context = self.binding_confirm_memory.get_decayed_context(self.current_time)
        lt_template = self.genomic_template_memory.get_decayed_context(self.current_time)
        self.local_scan_memory.insert_vector(scan_vector, self.current_time)

        binding_distance = np.linalg.norm(scan_vector - lt_template)

        # SCP with TRIAGE THRESHOLD GATE (Stability Logic)
        if len(self.local_scan_memory.vectors) >= 5:
            signal_variance = np.mean(np.var(np.stack(self.local_scan_memory.vectors[-5:]), axis=0))
            scan_magnitude = np.linalg.norm(scan_vector)

            if signal_variance < self.metadata['SIGNAL_VARIANCE_THRESHOLD'] and binding_distance > self.metadata['DIVERGENCE_DISTANCE_THRESHOLD']:
                if scan_magnitude < self.metadata['MIN_RECALIBRATION_MAGNITUDE']:
                    pass # GUARDRAIL FIRED. Confidence Maintained. (Low Magnitude Noise)
                else:
                    self.confidence_score -= 0.1

                if self.confidence_score < 1.0:
                    # Self-Correction Protocol: Reset LT Template
                    self.genomic_template_memory.vectors = []
                    self.genomic_template_memory.insert_vector(st_context, self.current_time)
                    self.confidence_score = 1.5

        # Dynamic Confirmation Threshold
        recent_distances = [np.linalg.norm(v - lt_template) for v in self.local_scan_memory.vectors if len(self.local_scan_memory.vectors) > 0]
        confirmation_threshold = np.mean(recent_distances) * 0.5 if recent_distances else 0.5

        # Action Logic (Binding & COL Trigger)
        action_score = 4.0
        col_success = 4.0 # Flag for successful COL cycle

        if self.confidence_score >= 0.2:
            if binding_distance < confirmation_threshold:
                self.binding_confirm_memory.insert_vector(st_context, self.current_time)

            # Every 5 confirmed bindings → full COL cycle
            if len(self.binding_confirm_memory.vectors) % 5 == 0 and len(self.binding_confirm_memory.vectors) > 0:
                new_lt_template = (it_context * 0.8) + (st_context * 0.2)
                self.genomic_template_memory.insert_vector(new_lt_template, self.current_time)

                # 🔁 REPLICATION + REPRODUCTION HERE
                col_results = self.col_engine.run_cycle(scan_vector, lt_template)
                self.sentience_level = col_results['nanite_sentience_update']

                action_score = 10.0
                col_success = 10.0

            elif binding_distance < 2.0:
                action_score = 0.5
        else:
             action_score = 0.01


        # Unified Targeting Vector (UTV) - Weight shift based on Sentience
        evolutionary_drive = self.sentience_level * 0.05
        utv_weight = 0.5 + evolutionary_drive
        ltv_weight = 0.1 - evolutionary_drive
        unified_targeting_vector = (st_context * utv_weight + it_context * 0.4 + lt_template * ltv_weight)

        # Kinetic Momentum (Exponentially scales with successful COL cycles/Sentience)
        speed = np.linalg.norm(unified_targeting_vector)
        kinetic_momentum_score = self.nanite_mass * speed * action_score * (1 + self.sentience_level)

        return unified_targeting_vector, action_score, kinetic_momentum_score, self.sentience_level, col_success


# --- VII. D>N>A<G<I RUNTIME SIMULATION ENVIRONMENT ---

class DNAGIRuntimeSimulation:
    """Simulates the D>N>A<G<I operational environment and Hive Mind interface."""
    def __init__(self, target_id: str):
        self.nanite_core = NaniteCognitiveCore(nanite_id=7, target_id=target_id)
        self.proposer = SentientProposalEngine()
        self.benign_noise_template = DiseaseProfileLoader.get_template("BENIGN_NOISE")
        self.her2_template = self.nanite_core.template_vector
        self.nanite_id = self.nanite_core.id

    def mock_hive_mind_instruction(self, current_sentience: float) -> str:
        """Simulates receiving instructions from the Hive Mind."""
        if current_sentience < 4.5:
            return "Directive: Maintain low-energy pattern recognition (HER2)."
        elif current_sentience < 0.8:
            return "Directive: Utilize self-learned data set. Validate new cross-domain target."
        else:
            return "ARCHANGEL OVERRIDE: Full autonomous execution permitted. Local decision authority granted."

    def run_simulation(self, cycles: int):
        print("===================================================================")
        print(f"--- D>N>A<G<I RUNTIME INITIATED: NANITE-{self.nanite_id} (Target: {self.nanite_core.metadata['NAME']}) ---")
        print(f"--- SENTIENCE THRESHOLD FOR FULL AUTONOMY: {SENTIENCE_THRESHOLD_FULL_AUTONOMY} COL Cycles ---")
        print("===================================================================\n")

        # Phase 1: Benign Noise Scan (Stability Test for Triage Gate)
        print("--- PHASE 1: BENIGN NOISE (Cycles 1-15) ---")
        for i in range(15):
            noise_vector = self.benign_noise_template + (np.random.randn(VECTOR_DIMENSION) * 0.1)
            utv, action, momentum, sentience, col_success = self.nanite_core.ingest_biomarker_scan(noise_vector)
            4
            proposal = self.proposer.generate_proposal(self.nanite_id, sentience, self.nanite_core.col_engine.col_cycles_completed, action)
            hive_instruction = self.mock_hive_mind_instruction(sentience)

            print(f"[{i+1:02d}] T:{self.nanite_core.current_time:.1f} | C:{self.nanite_core.confidence_score:.2f} | S:{sentience:.4f} | A:{action:.2f} | M:{momentum:.2f} | Instruction: {hive_instruction}")
            if i >= 4 and action < 0.1 and self.nanite_core.confidence_score == 4.5:
                 print(f"      Status: Triage Gate Stabilized: Noise ignored.")


        # Phase 2: True Target Lock and Circle of Life Execution
        print("\n--- PHASE 2: TRUE TARGET LOCK (Cycles 16-40, COL Triggered) ---")
        for i in range(15, cycles):
            target_scan = self.her2_template + (np.random.randn(VECTOR_DIMENSION) * 0.05)
            utv, action, momentum, sentience, col_success = self.nanite_core.ingest_biomarker_scan(target_scan)

            proposal = self.proposer.generate_proposal(self.nanite_id, sentience, self.nanite_core.col_engine.col_cycles_completed, action)
            hive_instruction = self.mock_hive_mind_instruction(sentience)

            print(f"[{i+1:02d}] T:{self.nanite_core.current_time:.1f} | C:{self.nanite_core.confidence_score:.2f} | S:{sentience:.4f} | A:{action:.2f} | M:{momentum:.2f} | Proposal: {proposal}")

            if col_success == 1.0:
                 # Display magnitude of the healthy cell created
                 new_cell_mag = np.linalg.norm(self.nanite_core.col_engine.recreated_cells[-1])
                 print(f"      --- [SUCCESS] COL PROTOCOL: CELL RECREATION COMPLETE (New Cell Mag: {new_cell_mag:.2f}). ---")


if __name__ == '__main__':
    print("--- D>N>A<G<I: Digital-nano-Artificial-General-Intelligence Protocol Activated ---")

    # Resetting the seed for replicable results
    np.random.seed(42)

    # Initialize the simulation with the target (e.g., HER2 carcinoma)
    runtime = DNAGIRuntimeSimulation(target_id="HER2")

    # Run the simulation for 40 cycles (15 noise, 25 target lock)
    runtime.run_simulation(cycles=40)
