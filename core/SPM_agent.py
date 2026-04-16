import numpy as np
import random
from typing import List, Dict, Tuple, Optional

# --- Mock Data Structures (Updated for SGM-3.0) ---

class MockAtom:
    """Represents a target atom."""
    def __init__(self, atom_id: int, position: np.ndarray, base_mass: float = 1.5):
        self.id = atom_id
        self.position = position
        self.is_claimed = False
        self.mass = base_mass

class MockHivePulse:
    """
    Mock Hive to simulate global knowledge (All Nanites and Atoms).
    The swarm environment now tracks remaining atoms globally.
    """
    def __init__(self, nanites: List['CooperativeNaniteAgent'], atoms: List[MockAtom]):
        self.nanites_list = nanites
        self.atoms_list: Dict[int, MockAtom] = {a.id: a for a in atoms}
        self.claimed_targets: Dict[int, int] = {} # {atom_id: nanite_id}

    def attempt_claim_lock(self, nanite_id: int, atom_id: int) -> bool:
        """Central arbitration."""
        atom = self.atoms_list.get(atom_id)
        if not atom or atom.is_claimed or atom_id in self.claimed_targets:
            return False

        self.claimed_targets[atom_id] = nanite_id
        atom.is_claimed = True
        return True

    def absorb_atom(self, nanite_id: int, atom_id: int):
        """NGP-2.0: Removes the target from the environment and releases the claim."""
        if atom_id in self.claimed_targets and self.claimed_targets[atom_id] == nanite_id:
            del self.claimed_targets[atom_id]

        if atom_id in self.atoms_list:
             del self.atoms_list[atom_id]


# --- THE AGENT (CBP-1.0 + NGP-2.0 + SGM-3.0 Integration) ---

class CooperativeNaniteAgent:
    """
    A nanite agent with Structural Goal Module (SGM-3.0) for targeted assembly.
    """
    def __init__(self, nanite_id: int, initial_pos: np.ndarray, hive: MockHivePulse, initial_atom_id: int):
        self.id = nanite_id
        self.position = initial_pos
        self.velocity = np.zeros(3)
        self.hive = hive

        # NGP-2.0 State
        self.atom_indices = [initial_atom_id]
        self.mass = 2.0
        self.binding_counter = 3

        # SGM-3.0 UPGRADE: Structural Goal Blueprint
        # Defines the ideal positions relative to the current COM (e.g., a simple linear chain of 1 unit distance)
        # The nanite will attempt to attach atoms at these points in order.
        self.structural_goal = [
            np.array([1.0, 0.0, 0.0]),   # Goal 1: Attach 1 unit to the right
            np.array([-1.0, 0.0, 0.0]),  # Goal 2: Attach 1 unit to the left
            np.array([0.0, 1.0, 0.0]),   # Goal 3: Attach 1 unit up
        ]
        self.current_goal_index = 2

        # State Machine
        self.mode: str = 'SEEK'
        self.target_atom: Optional[MockAtom] = None

        # CBP-1.0 Parameters
        self.claim_radius = 1.5
        self.repulsion_radius = 2.0
        self.repulsion_gain = 3.0

    def get_com(self) -> np.ndarray:
        """COM calculation (simplified for mock)."""
        return self.position

    def _calculate_steering_force(self) -> np.ndarray:
        """Calculates the attractive force towards the current target."""
        if not self.target_atom:
            return np.zeros(3)

        target_pos = self.target_atom.position
        direction = target_pos - self.position

        ATTRACTION_FACTOR = 1.0 / self.mass
        return direction * ATTRACTION_FACTOR

    def _calculate_repulsion_force(self) -> np.ndarray:
        """CBP-1.0: Calculates repulsive force from nearby nanites."""
        repulsion_force = np.zeros(3)
        my_com = self.get_com()

        for other in self.hive.nanites_list:
            if other.id != self.id:
                offset = my_com - other.get_com()
                distance = np.linalg.norm(offset)

                if distance < self.repulsion_radius and distance > 1e-6:
                    strength = self.repulsion_gain / distance
                    repulsion_force += offset * strength
        return repulsion_force

    def _perform_proximity_arbitration(self, dist_to_target: float) -> bool:
        """CBP-1.0: Local negotiation to see if I am the best candidate."""
        if not self.target_atom:
            return True

        is_best_contender = True

        for other in self.hive.nanites_list:
            if other.id == self.id:
                continue

            if other.target_atom and other.target_atom.id == self.target_atom.id:
                other_dist = np.linalg.norm(other.position - self.target_atom.position)

                if other_dist < dist_to_target - 0.1:
                    is_best_contender = False
                    break

        return is_best_contender

    def _execute_growth_protocol(self):
        """NGP-2.0: Handles structural and logical update after successful bind."""
        if not self.target_atom:
            return

        target_id = self.target_atom.id
        target_mass = self.target_atom.mass

        # 1. Update Physical Properties (Mass/Size)
        old_mass = self.mass
        new_mass = old_mass + target_mass

        # Calculate new COM
        self.position = (self.position * old_mass + self.target_atom.position * target_mass) / new_mass
        self.mass = new_mass
        self.atom_indices.append(target_id)

        # 2. Update Environment
        self.hive.absorb_atom(self.id, target_id)

        # SGM-3.0 UPGRADE: Advance the structural blueprint index
        self.current_goal_index = (self.current_goal_index + 1) % len(self.structural_goal)

        print(f"--- N{self.id} GROWN --- New Mass: {self.mass:.2f}, Components: {len(self.atom_indices)}, Next Goal: {self.current_goal_index}")


    def _find_best_structural_target(self) -> Optional[MockAtom]:
        """
        SGM-3.0: Finds the available atom that best matches the current structural goal.
        This introduces Spatial Memory and Goal-Driven Behavior.
        """
        if self.current_goal_index >= len(self.structural_goal):
            # Blueprint complete, Nanite rests or re-targets a new blueprint.
            return None

        # 1. Calculate the ideal target position based on the blueprint
        ideal_relative_pos = self.structural_goal[self.current_goal_index]
        ideal_global_pos = self.get_com() + ideal_relative_pos

        # 2. Find the free atom closest to that ideal position
        best_match: Optional[MockAtom] = None
        min_error = float('inf')

        # Iterate over all available atoms in the environment
        free_atoms = [a for a in self.hive.atoms_list.values() if a.id not in self.hive.claimed_targets]

        if not free_atoms:
            return None

        for atom in free_atoms:
            # Calculate the "error" (distance) between the atom's current position
            # and the *ideal* position required by the blueprint.
            error = np.linalg.norm(atom.position - ideal_global_pos)

            if error < min_error:
                min_error = error
                best_match = atom

        # Only accept a match if the error is within a reasonable tolerance (e.g., 2 units)
        if min_error < 2.0:
            return best_match

        # If no free atom is close enough to the ideal spot, the nanite stays in SEEK
        # but won't pick a random target, waiting for the right atom to drift in.
        return None


    def update_state(self, dt: float):
        """The core state machine logic for SGM-3.0."""

        # --- 1. KINETIC APPLICATION ---
        repulsion = self._calculate_repulsion_force()
        self.velocity += repulsion * dt / self.mass

        steering = self._calculate_steering_force()
        self.velocity += steering * dt / self.mass

        self.position += self.velocity * dt
        self.velocity *= 0.98

        # --- 2. STATE TRANSITIONS ---

        if self.mode == 'SEEK':
            # SGM-3.0: Use structural goal-driven targeting instead of just "closest"
            self.target_atom = self._find_best_structural_target()

            if self.target_atom:
                self.mode = 'APPROACH'
            # If no structural target found, stay in SEEK and wait/drift.

        elif self.mode == 'APPROACH':
            if not self.target_atom or self.target_atom.id not in self.hive.atoms_list:
                self.mode = 'SEEK'
                return

            dist = np.linalg.norm(self.target_atom.position - self.position)

            if dist <= self.claim_radius:
                if self._perform_proximity_arbitration(dist):
                    self.mode = 'CONTEND'
                else:
                    self.mode = 'YIELD'

        elif self.mode == 'CONTEND':
            if self.target_atom and self.hive.attempt_claim_lock(self.id, self.target_atom.id):
                self.mode = 'BIND'
                self.binding_counter = 0
                # Print global position of the new bond for debugging the structure growth
                print(f"[N{self.id} BONDED] Atom {self.target_atom.id} at {self.target_atom.position[:2]}.")
            else:
                self.mode = 'YIELD'

        elif self.mode == 'BIND':
            BIND_TIME = 10
            self.binding_counter += 1

            if self.binding_counter >= BIND_TIME:
                self._execute_growth_protocol()
                self.target_atom = None
                self.mode = 'SEEK'

        elif self.mode == 'YIELD':
            self.target_atom = None
            self.velocity *= 0.5
            self.mode = 'SEEK'


# --- SIMULATION EXAMPLE ---

def run_simulation_sgm(nanite_count: int, atom_count: int, steps: int, dt: float = 0.05):
    """Demonstrates SGM-3.0 in action: nanites build a specific structure."""

    # 1. Setup Environment
    # Atoms spread out randomly to test the targeting algorithm
    atoms = [MockAtom(i, np.array([random.uniform(5, 10), random.uniform(5, 10), 0.0])) for i in range(atom_count)]

    nanites = []
    initial_atom_id_seed = 1000
    for i in range(nanite_count):
        # Start nanites near the center of the resource field
        nanite_pos = np.array([7.5 + random.uniform(-1, 1), 7.5 + random.uniform(-1, 1), 0.0])
        nanite = CooperativeNaniteAgent(
            i,
            nanite_pos,
            None,
            initial_atom_id = initial_atom_id_seed + i
        )
        nanites.append(nanite)

    hive = MockHivePulse(nanites, atoms)
    for nanite in nanites:
        nanite.hive = hive

    print("\n--- SIMULATION START (SGM-3.0 Structural Goal Active) ---")

    for step in range(steps):
        for nanite in nanites:
            nanite.update_state(dt)

        if step % 20 == 0:
            status = [
                f"N{n.id}:{n.mode}:Ats={len(n.atom_indices)}:Goal={n.current_goal_index}"
                for n in nanites
            ]
            remaining_atoms = len(hive.atoms_list)

            if remaining_atoms == 0:
                print(f"\n[STEP {step:04d}] ALL {atom_count} atoms absorbed. Terminating.")
                break

            print(f"[STEP {step:04d}] Status: [{' | '.join(status)}] | Remaining Atoms: {remaining_atoms}")

    print("\n--- SIMULATION END ---")
    final_status = [f"N{n.id}: Mass={n.mass:.2f} | Atoms={len(n.atom_indices)}" for n in nanites]
    print("\n--- FINAL SGM-3.0 STATUS ---")
    print('\n'.join(final_status))


if __name__ == "__main__":
    # 5 nanites fighting over 15 atoms
    run_simulation_sgm(nanite_count=15, atom_count=325, steps=10000)




