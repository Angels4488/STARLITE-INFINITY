import numpy as np

# --- V1 CORE: NANITE SENTINEL (The fixed base class) ---
class NaniteSentinel:
    """
    Nanite V1: The Sentinel. The base class for autonomous atomic clusters,
    providing core kinetic functions like COM calculation and force application.
    """
    # FIX 1: Renaming 'masses' to 'global_mass_array' to clarify intent
    def __init__(self, nanite_id, atom_indices, global_mass_array):
        self.nanite_id = nanite_id
        self.atom_indices = list(atom_indices)

        # FIX 2: Store the reference to the GLOBAL mass array. This is the source of truth.
        self._global_mass_array = global_mass_array

        self.mode = "SEEK"
        self.perception_radius = 2.5
        self.target_atom = None
        self.binding_force_gain = 0.5 # Force magnitude for steering

    def get_com(self, current_positions):
        """
        Calculates Center of Mass (COM) for the nanite's specific atoms.
        FIXED: Dynamically fetches masses based on current self.atom_indices.
        """
        p = current_positions[self.atom_indices]

        # FIX 3: Dynamic Mass Sync. Guarantee the mass list matches the position list (N x 1).
        current_masses = self._global_mass_array[self.atom_indices]
        m_broadcast = current_masses[:, np.newaxis]

        # Mass-weighted sum of positions
        return np.sum(p * m_broadcast, axis=0) / np.sum(current_masses)

    def update_steering_forces(self, current_positions, forces):
        """Applies steering force toward the current target atom."""
        if self.target_atom is None:
            return forces

        com = self.get_com(current_positions)
        direction = current_positions[self.target_atom] - com
        direction_magnitude = np.linalg.norm(direction)

        # Prevent division by zero if COM is exactly on target
        if direction_magnitude < 1e-9:
            return forces

        unit_vector = direction / direction_magnitude
        steering_force = unit_vector * self.binding_force_gain

        # Distribute force equally to ensure rigid-body like movement
        force_per_atom = steering_force / len(self.atom_indices)

        for idx in self.atom_indices:
            forces[idx] += force_per_atom

        # Check for binding contact (The physical trigger)
        if direction_magnitude < 1.2:
            print(f"[{self.nanite_id}] Contact: Atom {self.target_atom} ready for binding.")
            self.mode = "BIND_PENDING"

        return forces

# --- HIVE COMMUNICATION (The shared resource manager) ---
class HivePulse:
    """The central communication hub for the nanite swarm, managing resource claims."""
    def __init__(self):
        # {atom_index: nanite_id} -> Key is the resource, value is the claiming agent
        self.claimed_targets = {}

    def broadcast_claim(self, nanite_id, atom_idx):
        """Attempts to claim an atom. Returns True if successful, False if already claimed."""
        if atom_idx not in self.claimed_targets:
            self.claimed_targets[atom_idx] = nanite_id
            return True
        return False

    def release_claim(self, nanite_id, atom_idx):
        """Releases a claim, typically after binding is complete or target is lost."""
        if self.claimed_targets.get(atom_idx) == nanite_id:
            del self.claimed_targets[atom_idx]

# --- V2 AGENT: NANITE SWARM AGENT (The social agent) ---
class NaniteSwarmAgent(NaniteSentinel):
    """
    V2 Agent: Inherits Sentinel core but adds Swarm Coordination/Collision
    avoidance logic using the HivePulse.
    """
    # FIX 4: Update constructor signature to pass global_mass_array correctly
    def __init__(self, nanite_id, atom_indices, global_mass_array, hive):
        # Initialize Sentinel base class (Passing the global_mass_array)
        super().__init__(nanite_id, atom_indices, global_mass_array)
        self.hive = hive
        self.binding_threshold = 1.2 # Must match the check in V1 steering
        self.com_history = [] # For telemetry

    def update_behavior(self, current_positions, velocities, forces, environment_atoms):
        com = self.get_com(current_positions)
        self.com_history.append(com)

        # 1. SCAN & CLAIM (The Swarm Coordination Logic)
        if self.mode == "SEEK":
            # 1a. Filter environment: Must be available and not part of this nanite.
            available = [a for a in environment_atoms
                         if a not in self.hive.claimed_targets
                         and a not in self.atom_indices]

            if available:
                # 1b. Calculate closest available target
                dists = [np.linalg.norm(current_positions[a] - com) for a in available]
                target_idx = available[np.argmin(dists)]

                # 1c. Broadcast claim to the Hive
                if self.hive.broadcast_claim(self.nanite_id, target_idx):
                    self.target_atom = target_idx
                    self.mode = "BIND"
                    print(f"[NANITE {self.nanite_id}] CLAIMED {target_idx}. Mode: BIND")

        # 2. EXECUTE BINDING (V1 Steering Logic)
        forces = self.update_steering_forces(current_positions, forces)

        # 3. POST-STEERING / BINDING TRANSITION
        if self.mode == "BIND_PENDING":
             # This is where the physical bond/integration would occur.
             # For now, we simulate success and update the agent's body.
             new_atom_idx = self.target_atom
             self.atom_indices.append(new_atom_idx)
             self.hive.release_claim(self.nanite_id, new_atom_idx)
             self.target_atom = None
             self.mode = "SEEK" # After binding, start looking for the next piece
             print(f"[{self.nanite_id}] BIND SUCCESS. New size: {len(self.atom_indices)}")


        return forces

# --- SIMULATION EXECUTION LOOP ---
def run_swarm_sim():
    hive = HivePulse()
    # 10 atoms total: N1 = [0,1,2], N2 = [3,4,5], Unbound = [6,7,8,9]
    pos = np.random.rand(10, 3) * 10
    vel = np.zeros_like(pos)
    m = np.ones(10) # The Global Mass Array (Source of Truth)
    f = np.zeros_like(pos)

    # Initialize the two nanites (Passing 'm' as the global mass array)
    n1 = NaniteSwarmAgent(nanite_id=1, atom_indices=[0,1,2], global_mass_array=m, hive=hive)
    n2 = NaniteSwarmAgent(nanite_id=2, atom_indices=[3,4,5], global_mass_array=m, hive=hive)
    nanites = [n1, n2]

    # All atoms in the environment
    environment_atoms = list(range(10))

    print("Swarm Engaged. Tracking Hive Claims...")

    for step in range(30):
        f.fill(0) # Reset forces

        # Update forces from Nanite behavior
        for nanite in nanites:
            f = nanite.update_behavior(pos, vel, f, environment_atoms)

        # Simple Integration (Verlet/Euler loop would be here)
        vel += f * 0.1
        pos += vel * 0.1

        # [Kinetic Stabilization would occur here, after force application/integration]

        if step % 5 == 0:
            print(f"\n--- STEP {step} ---")
            print(f"Hive Targets: {hive.claimed_targets}")
            for n in nanites:
                print(f"N{n.nanite_id}: Mode={n.mode}, COM={n.get_com(pos)}, Atoms={n.atom_indices}")

if __name__ == "__main__":
    run_swarm_sim()
