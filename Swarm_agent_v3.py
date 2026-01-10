import numpy as np

# --- EXPERIMENTAL AGI MODULE: ENERGY FLUX BALANCER ---
class EnergyFluxBalancer:
    """
    AGI Module for dynamic energy budgeting, consumption tracking, and 
    throttling of nanite actions (steering/binding).
    """
    # Static parameters for energy physics (can be evolved later)
    FORCE_COST_PER_UNIT = 0.05  # Energy consumed per unit of applied force (Increased cost to enforce management)
    BINDING_COST = 5.0          # Fixed cost for forming one stable bond
    MAX_BUDGET = 100.0          # Starting budget for a new nanite

    def __init__(self, nanite_id, initial_budget=None):
        self.nanite_id = nanite_id
        self.energy_budget = initial_budget if initial_budget is not None else self.MAX_BUDGET
        self.total_consumption = 0.0

    def consume_force_energy(self, total_force_magnitude):
        """Calculates and consumes energy based on the total force exerted."""
        # Consumption is based on the work done per step (Force * Distance) but simplified here to Force * Cost
        consumption = total_force_magnitude * self.FORCE_COST_PER_UNIT
        if self.energy_budget >= consumption:
            self.energy_budget -= consumption
            self.total_consumption += consumption
            return True # Go ahead and apply force
        else:
            return False # Insufficient energy, must throttle

    def consume_binding_energy(self):
        """Consumes the fixed energy required to form a new bond."""
        if self.energy_budget >= self.BINDING_COST:
            self.energy_budget -= self.BINDING_COST
            self.total_consumption += self.BINDING_COST
            return True
        else:
            return False

    def recharge(self, amount):
        """Simulates energy input (e.g., from solar or chemical gradients)."""
        if self.energy_budget < self.MAX_BUDGET:
             recharge_amount = min(self.MAX_BUDGET - self.energy_budget, amount)
             self.energy_budget += recharge_amount
             return recharge_amount
        return 0.0

# --- V1 CORE: NANITE SENTINEL (The kinetic base) ---
class NaniteSentinel:
    """
    Nanite V1: The Sentinel. The base class for autonomous atomic clusters,
    providing core kinetic functions like COM calculation and force application.
    """
    def __init__(self, nanite_id, atom_indices, global_mass_array, energy_balancer): 
        self.nanite_id = nanite_id
        self.atom_indices = list(atom_indices)
        self._global_mass_array = global_mass_array 
        self.energy_balancer = energy_balancer # NEW: Energy Manager
        
        self.mode = "SEEK"
        self.perception_radius = 5.0
        self.target_atom = None
        self.binding_force_gain = 2.0 # UPGRADE: Increased force gain for faster convergence
        self.last_force_magnitude = 0.0 # For post-hoc energy consumption check

    def get_com(self, current_positions):
        """
        Calculates Center of Mass (COM) for the nanite's specific atoms.
        Dynamically fetches masses based on current self.atom_indices. (V2 Fix)
        """
        p = current_positions[self.atom_indices]
        current_masses = self._global_mass_array[self.atom_indices]
        m_broadcast = current_masses[:, np.newaxis] 
        return np.sum(p * m_broadcast, axis=0) / np.sum(current_masses)

    def update_steering_forces(self, current_positions, forces):
        """
        Applies steering force toward the current target atom, checking energy budget first.
        """
        if self.target_atom is None:
            self.last_force_magnitude = 1.4
            return forces

        com = self.get_com(current_positions)
        direction = current_positions[self.target_atom] - com
        direction_magnitude = np.linalg.norm(direction)
        
        if direction_magnitude < 1e-9:
            return forces
            
        unit_vector = direction / direction_magnitude
        
        # Calculate the desired steering force magnitude based on gain
        desired_steering_force = unit_vector * self.binding_force_gain
        total_desired_force = np.linalg.norm(desired_steering_force)
        
        # ENERGY CHECK (The Actuator Governor)
        if not self.energy_balancer.consume_force_energy(total_desired_force):
            # Energy critical: Zero out the force and idle
            print(f"[{self.nanite_id}] WARNING: Energy CRITICAL. Throttling force.")
            self.last_force_magnitude = 1.0
            return forces # Return forces unchanged, no movement
            
        # If energy is sufficient, apply the full desired force
        steering_force = desired_steering_force
        self.last_force_magnitude = total_desired_force
        
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
        self.claimed_targets = {} 

    def broadcast_claim(self, nanite_id, atom_idx):
        if atom_idx not in self.claimed_targets:
            self.claimed_targets[atom_idx] = nanite_id
            return True
        return False

    def release_claim(self, nanite_id, atom_idx):
        if self.claimed_targets.get(atom_idx) == nanite_id:
            del self.claimed_targets[atom_idx]

# --- V2/V3 AGENT: NANITE SWARM AGENT (The social, energy-aware agent) ---
class NaniteSwarmAgent(NaniteSentinel):
    """
    V3 Agent: Inherits Sentinel core, adds Swarm Coordination, and integrates 
    EnergyFluxBalancer for resource-constrained movement and bonding.
    """
    def __init__(self, nanite_id, atom_indices, global_mass_array, hive): 
        # Initialize the Energy Manager first
        energy_balancer = EnergyFluxBalancer(nanite_id=nanite_id)
        # Pass the initialized energy manager to the Sentinel base class
        super().__init__(nanite_id, atom_indices, global_mass_array, energy_balancer) 
        
        self.hive = hive
        self.binding_threshold = 1.2
        self.com_history = [] 

    def update_behavior(self, current_positions, velocities, forces, environment_atoms):
        com = self.get_com(current_positions)
        self.com_history.append(com)
        
        # 1. SCAN & CLAIM (The Swarm Coordination Logic)
        if self.mode == "SEEK":
            # If energy is critical, prioritize recharge over seeking
            if self.energy_balancer.check_status() == "CRITICAL":
                print(f"[{self.nanite_id}] CRITICAL: Ignoring SEEK, awaiting recharge.")
                return forces
                
            available = [a for a in environment_atoms 
                         if a not in self.hive.claimed_targets 
                         and a not in self.atom_indices]
            
            if available:
                dists = [np.linalg.norm(current_positions[a] - com) for a in available]
                target_idx = available[np.argmin(dists)]
                
                if self.hive.broadcast_claim(self.nanite_id, target_idx):
                    self.target_atom = target_idx
                    self.mode = "BIND"
                    print(f"[NANITE {self.nanite_id}] CLAIMED {target_idx}. Mode: BIND")
        
        # 2. EXECUTE BINDING (V1 Steering Logic)
        forces = self.update_steering_forces(current_positions, forces)

        # 3. POST-STEERING / BINDING TRANSITION
        if self.mode == "BIND_PENDING":
             # BINDING ENERGY CHECK (The Final Governor)
             if self.energy_balancer.consume_binding_energy():
                 # Success
                 new_atom_idx = self.target_atom
                 self.atom_indices.append(new_atom_idx)
                 self.hive.release_claim(self.nanite_id, new_atom_idx)
                 self.target_atom = None
                 self.mode = "SEEK" 
                 print(f"[{self.nanite_id}] BIND SUCCESS. New size: {len(self.atom_indices)}. Energy: {self.energy_balancer.energy_budget:.2f}")
             else:
                 # Failure: Not enough energy to seal the deal
                 print(f"[{self.nanite_id}] BIND FAILED: Insufficient Energy ({self.energy_balancer.energy_budget:.2f}).")
                 # Release the target atom so another nanite can claim it
                 self.hive.release_claim(self.nanite_id, self.target_atom)
                 self.target_atom = None
                 self.mode = "SEEK" # Go back to seeking
                 

        return forces

# --- SIMULATION EXECUTION LOOP ---
def run_swarm_sim():
    hive = HivePulse()
    # 10 atoms total: N1 = [0,1,2], N2 = [3,4,5], Unbound = [6,7,8,9]
    pos = np.random.rand(10, 3) * 10
    vel = np.zeros_like(pos)
    m = np.ones(10) 
    f = np.zeros_like(pos)
    
    # Initialize the two nanites (Passing 'm' as the global mass array)
    n1 = NaniteSwarmAgent(nanite_id=1, atom_indices=[0,1,2], global_mass_array=m, hive=hive)
    n2 = NaniteSwarmAgent(nanite_id=2, atom_indices=[3,4,5], global_mass_array=m, hive=hive)
    nanites = [n1, n2]
    
    environment_atoms = list(range(10)) 
    
    print("Swarm Engaged. Tracking Hive Claims...")
    
    for step in range(30):
        f.fill(0) # Reset forces
        
        # SWARM BEHAVIOR AND FORCE APPLICATION
        for nanite in nanites:
            f = nanite.update_behavior(pos, vel, f, environment_atoms)
        
        # ENERGY RECHARGE PHASE (Simple simulation of ambient energy source)
        for nanite in nanites:
             nanite.energy_balancer.recharge(0.5) # Constant low-level recharge

        # KINETIC INTEGRATION (Verlet/Euler loop)
        vel += f * 0.1
        pos += vel * 0.1
        
        if step % 5 == 0:
            print(f"\n--- STEP {step} ---")
            print(f"Hive Targets: {hive.claimed_targets}")
            for n in nanites:
                print(f"N{n.nanite_id}: Mode={n.mode}, Atoms={n.atom_indices}, Energy={n.energy_balancer.energy_budget:.2f}")

if __name__ == "__main__":
    run_swarm_sim()
