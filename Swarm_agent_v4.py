import numpy as np

# --- EXPERIMENTAL AGI MODULE: ENERGY FLUX BALANCER ---
class EnergyFluxBalancer:
    """
    AGI Module for dynamic energy budgeting, consumption tracking, and 
    throttling of nanite actions (steering/binding).
    """
    # Static parameters for energy physics (can be evolved later)
    FORCE_COST_PER_UNIT = 0.05  # Energy consumed per unit of applied force 
    BINDING_COST = 5.0          # Fixed cost for forming one stable bond
    MAX_BUDGET = 100.0          # Starting budget for a new nanite
    CRITICAL_THRESHOLD = 10.0   # NEW: Threshold to trigger mandatory RECHARGE mode

    def __init__(self, nanite_id, initial_budget=None):
        self.nanite_id = nanite_id
        self.energy_budget = initial_budget if initial_budget is not None else self.MAX_BUDGET
        self.total_consumption = 0.0

    def consume_force_energy(self, total_force_magnitude):
        """Calculates and consumes energy based on the total force exerted."""
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
        
    def check_status(self):
        """
        FIX: Returns the nanite's current energy status (OK, LOW, CRITICAL). 
        This was the missing function causing the AttributeError.
        """
        if self.energy_budget >= self.MAX_BUDGET * 0.5:
            return "OK"
        elif self.energy_budget < self.CRITICAL_THRESHOLD:
            return "CRITICAL"
        else:
            return "LOW"

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
        self.energy_balancer = energy_balancer 
        
        self.mode = "SEEK"
        self.perception_radius = 5.0
        self.target_atom = None
        self.binding_force_gain = 4.0 # UPGRADE: Increased force gain to 4.0
        self.last_force_magnitude = 0.0 

    def get_com(self, current_positions):
        """
        Calculates Center of Mass (COM) for the nanite's specific atoms.
        """
        p = current_positions[self.atom_indices]
        current_masses = self._global_mass_array[self.atom_indices]
        m_broadcast = current_masses[:, np.newaxis] 
        return np.sum(p * m_broadcast, axis=0) / np.sum(current_masses)

    def apply_steering_forces(self, current_positions, forces):
        """
        Applies steering force toward the current target atom, checking energy budget first.
        Returns the modified forces array and True if force was applied.
        """
        if self.target_atom is None:
            self.last_force_magnitude = 0.0
            return forces, False

        com = self.get_com(current_positions)
        direction = current_positions[self.target_atom] - com
        direction_magnitude = np.linalg.norm(direction)
        
        if direction_magnitude < 1e-9:
            self.last_force_magnitude = 0.0
            return forces, False
            
        unit_vector = direction / direction_magnitude
        
        desired_steering_force = unit_vector * self.binding_force_gain
        total_desired_force = np.linalg.norm(desired_steering_force)
        
        # ENERGY CHECK (The Actuator Governor)
        if not self.energy_balancer.consume_force_energy(total_desired_force):
            # Energy critical: Throttling force and signaling failure to apply force
            print(f"[{self.nanite_id}] WARNING: Energy CRITICAL. Throttling force.")
            self.last_force_magnitude = 0.0
            return forces, False
            
        # If energy is sufficient, apply the full desired force
        steering_force = desired_steering_force
        self.last_force_magnitude = total_desired_force
        
        force_per_atom = steering_force / len(self.atom_indices)
        
        for idx in self.atom_indices:
            forces[idx] += force_per_atom
            
        # Check for binding contact (The physical trigger)
        if direction_magnitude < 1.2:
            print(f"[{self.nanite_id}] Contact: Atom {self.target_atom} ready for binding.")
            self.mode = "BIND_PENDING"

        return forces, True

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

# --- V4 AGENT: NANITE SWARM AGENT (The state-governed assembler) ---
class NaniteSwarmAgent(NaniteSentinel):
    """
    V4 Agent: Integrates state machine logic for SEEK, BIND, and RECHARGE modes.
    Ensures energy constraint governs all actions.
    """
    def __init__(self, nanite_id, atom_indices, global_mass_array, hive): 
        energy_balancer = EnergyFluxBalancer(nanite_id=nanite_id)
        super().__init__(nanite_id, atom_indices, global_mass_array, energy_balancer) 
        
        self.hive = hive
        self.binding_threshold = 1.2
        self.com_history = [] 

    def update_behavior(self, current_positions, velocities, forces, environment_atoms):
        com = self.get_com(current_positions)
        self.com_history.append(com)
        
        energy_status = self.energy_balancer.check_status()
        
        # --- STATE MACHINE GOVERNOR (FIXES THE ERROR HERE) ---
        if energy_status == "CRITICAL":
            # If critical, force switch to RECHARGE and do not apply forces.
            if self.mode != "RECHARGE":
                print(f"[{self.nanite_id}] !!! ENERGY FAILSAFE !!! Switching to RECHARGE mode.")
            self.mode = "RECHARGE"
            
        elif self.mode == "RECHARGE" and energy_status == "OK":
            # If charged back up (above 50% max budget), resume seeking.
            print(f"[{self.nanite_id}] CHARGE COMPLETE. Resuming SEEK mode.")
            self.mode = "SEEK"
            
        # --- MODE EXECUTION ---
        if self.mode == "SEEK":
            # 1. SCAN & CLAIM
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
        
        elif self.mode == "BIND":
            # 2. EXECUTE STEERING AND CHECK FOR BIND_PENDING
            # Renamed from update_steering_forces to apply_steering_forces
            forces, force_applied = self.apply_steering_forces(current_positions, forces) 
            
            # If force was NOT applied (due to energy throttle), switch back to SEEK
            if not force_applied and energy_status != "CRITICAL":
                # This only happens if we fail the force check but aren't yet CRITICAL
                print(f"[{self.nanite_id}] Steering Failed: Temporarily low energy, switching to SEEK.")
                self.mode = "SEEK"
            
        elif self.mode == "BIND_PENDING":
             # 3. POST-STEERING / BINDING TRANSITION
             
             # BINDING ENERGY CHECK (The Final Governor)
             if self.energy_balancer.consume_binding_energy():
                 # Success: Perform atomic integration
                 new_atom_idx = self.target_atom
                 self.atom_indices.append(new_atom_idx)
                 self.hive.release_claim(self.nanite_id, new_atom_idx)
                 self.target_atom = None
                 self.mode = "SEEK" 
                 print(f"[{self.nanite_id}] *** BIND SUCCESS *** New size: {len(self.atom_indices)}. Energy: {self.energy_balancer.energy_budget:.2f}")
             else:
                 # Failure: Not enough energy to seal the bond (too expensive).
                 print(f"[{self.nanite_id}] BIND FAILED: Insufficient Energy ({self.energy_balancer.energy_budget:.2f}). Must RECHARGE.")
                 self.hive.release_claim(self.nanite_id, self.target_atom)
                 self.target_atom = None
                 self.mode = "RECHARGE" # Go straight to recharge if binding failed

        # RECHARGE mode is implicitly handled by the governor state, applying zero force.
        
        return forces

# --- SIMULATION EXECUTION LOOP ---
def run_swarm_sim():
    hive = HivePulse()
    # 10 atoms total: N1 = [0,1,2], N2 = [3,4,5], Unbound = [6,7,8,9]
    # We will use atoms 6, 7, 8, 9 as free targets.
    pos = np.random.rand(10, 3) * 10
    vel = np.zeros_like(pos)
    m = np.ones(10) 
    f = np.zeros_like(pos)
    
    # Initialize the two nanites 
    n1 = NaniteSwarmAgent(nanite_id=1, atom_indices=[0,1,2], global_mass_array=m, hive=hive)
    n2 = NaniteSwarmAgent(nanite_id=3, atom_indices=[3,4,5], global_mass_array=m, hive=hive) # Renamed to N3
    nanites = [n1, n2]
    
    environment_atoms = list(range(10)) 
    
    print("Swarm Engaged. Tracking Hive Claims...")
    
    for step in range(50): # Extended to 50 steps to see the full cycle
        f.fill(0) # Reset forces
        
        # SWARM BEHAVIOR AND FORCE APPLICATION
        for nanite in nanites:
            f = nanite.update_behavior(pos, vel, f, environment_atoms)
        
        # ENERGY RECHARGE PHASE (Asymmetric ambient energy simulation)
        for nanite in nanites:
             # N3 is in a hot spot (faster recharge)
             recharge_rate = 0.5 if nanite.nanite_id == 1 else 1.5 
             nanite.energy_balancer.recharge(recharge_rate) 

        # KINETIC INTEGRATION (Verlet/Euler loop)
        vel += f * 0.1
        pos += vel * 0.1
        
        if step % 5 == 0:
            print(f"\n--- STEP {step} ---")
            print(f"Hive Targets: {hive.claimed_targets}")
            for n in nanites:
                print(f"N{n.nanite_id}: Mode={n.mode}, Atoms={n.atom_indices}, Energy={n.energy_balancer.energy_budget:.2f}, Status={n.energy_balancer.check_status()}")

if __name__ == "__main__":
    run_swarm_sim()
