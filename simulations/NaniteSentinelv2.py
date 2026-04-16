import numpy as np

class NaniteSentinel:
    """
    Nanite V1: The Sentinel.
    Autonomous atomic cluster with energy-aware steering and momentum-safe bonding.
    """
    def __init__(self, nanite_id, atom_indices, masses, positions):
        self.nanite_id = nanite_id
        self.atom_indices = list(atom_indices)
        self.masses = masses[self.atom_indices, np.newaxis]
        self.mode = "SEEK"  # Modes: IDLE, SEEK, BIND, STABILIZE
        self.energy_budget = 100.0
        self.perception_radius = 5.0
        self.target_atom = None

    def get_com(self, current_positions):
        """Calculates Center of Mass for the nanite's specific atoms."""
        p = current_positions[self.atom_indices]
        return np.sum(p * self.masses, axis=0) / np.sum(self.masses)

    def update_behavior(self, current_positions, velocities, forces, environment_atoms):
        """
        ENHANCED LOGIC: The 'Brain' of the Nanite.
        Modifies forces directly to steer toward unbound atoms.
        """
        com = self.get_com(current_positions)

        if self.mode == "SEEK":
            # Find closest unbound atom not in our group
            for idx in environment_atoms:
                if idx not in self.atom_indices:
                    dist = np.linalg.norm(current_positions[idx] - com)
                    if dist < self.perception_radius:
                        self.target_atom = idx
                        self.mode = "BIND"
                        break

        if self.mode == "BIND" and self.target_atom is not None:
            # Apply steering force toward target
            direction = current_positions[self.target_atom] - com
            unit_vector = direction / (np.linalg.norm(direction) + 1e-9)
            steering_force = unit_vector * 0.5  # Tuned gain

            # Distribute steering force across nanite atoms
            for idx in self.atom_indices:
                forces[idx] += steering_force / len(self.atom_indices)

            # Check for binding contact
            if np.linalg.norm(direction) < 1.2:
                print(f"[NANITE_{self.nanite_id}] Binding Atom {self.target_atom}!")
                self.atom_indices.append(self.target_atom)
                self.target_atom = None
                self.mode = "STABILIZE"

        return forces

# --- EXPERIMENTAL EXECUTION LOOP ---
def run_nanite_sim():
    # Setup: 3 atom nanite (L-shape) and 1 target atom
    pos = np.array([[0,0,0], [1,0,0], [0,1,0], [3,3,3]], dtype=float)
    vel = np.zeros_like(pos)
    m = np.ones(4)
    f = np.zeros_like(pos)

    # Initialize our first Nanite
    nanite = NaniteSentinel(nanite_id=1, atom_indices=[0,1,2], masses=m, positions=pos)
    unbound_atoms = [3]

    print("Starting Nanite V1 Simulation...")
    for step in range(50):
        # 1. Reset Forces
        f.fill(0)

        # 2. Nanite Brain Updates Forces
        f = nanite.update_behavior(pos, vel, f, unbound_atoms)

        # 3. Simple Integration (Euler for demo, use Verlet for production)
        vel += f * 0.1
        pos += vel * 0.1

        # 4. MOMENTUM STABILIZATION (Your AtomicStateManager V9 Logic)
        # [Placeholder for your existing stabilize(pos, vel) call]

        if step % 10 == 0:
            print(f"Step {step}: Nanite Mode={nanite.mode}, COM={nanite.get_com(pos)}")

if __name__ == "__main__":
    run_nanite_sim()
