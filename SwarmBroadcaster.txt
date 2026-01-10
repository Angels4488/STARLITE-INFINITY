import numpy as np

class HivePulse:
    """The central communication hub for the nanite swarm."""
    def __init__(self):
        self.claimed_targets = {} # {atom_index: nanite_id}

    def broadcast_claim(self, nanite_id, atom_idx):
        if atom_idx not in self.claimed_targets:
            self.claimed_targets[atom_idx] = nanite_id
            return True
        return False

    def release_claim(self, nanite_id):
        self.claimed_targets = {k: v for k, v in self.claimed_targets.items() if v != nanite_id}

class NaniteSwarmAgent(NaniteSentinel):
    """V2 Agent: Now with 100% more social skills."""
    def __init__(self, nanite_id, atom_indices, masses, hive):
        super().__init__(nanite_id, atom_indices, masses, None)
        self.hive = hive
        self.collision_buffer = 1.5

    def update_behavior(self, current_positions, velocities, forces, environment_atoms):
        com = self.get_com(current_positions)
        
        # 1. SCAN & CLAIM (The Hive Logic)
        if self.mode == "SEEK":
            # Filter environment for atoms not already claimed by the Hive
            available = [a for a in environment_atoms if a not in self.hive.claimed_targets and a not in self.atom_indices]
            
            if available:
                # Find closest available
                dists = [np.linalg.norm(current_positions[a] - com) for a in available]
                target_idx = available[np.argmin(dists)]
                
                if self.hive.broadcast_claim(self.nanite_id, target_idx):
                    self.target_atom = target_idx
                    self.mode = "BIND"

        # 2. COLLISION AVOIDANCE (Don't smack into brothers)
        # [Experimental: Subtle force push from other Nanite COMs]
        
        # 3. EXECUTE BINDING (Inherited physics)
        return super().update_behavior(current_positions, velocities, forces, environment_atoms)

# --- SWARM EXECUTION ---
def run_swarm_sim():
    hive = HivePulse()
    pos = np.random.rand(10, 3) * 10
    m = np.ones(10)
    f = np.zeros_like(pos)
    
    # Create two nanites competing for 4 unbound atoms
    n1 = NaniteSwarmAgent(1, [0,1,2], m, hive)
    n2 = NaniteSwarmAgent(2, [3,4,5], m, hive)
    unbound = [6, 7, 8, 9]

    print("Swarm Engaged. Tracking Hive Claims...")
    for _ in range(5):
        n1.update_behavior(pos, None, f, unbound)
        n2.update_behavior(pos, None, f, unbound)
        print(f"Hive Status: {hive.claimed_targets}")

if __name__ == "__main__":
    run_swarm_sim()
