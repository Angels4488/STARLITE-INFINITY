#!/usr/bin/env python3
"""
Nanite Binding Upgrade - Core Swarm Intelligence System
Part of STARLITE-INFINITY AGI Architecture
"""

import numpy as np
import random
import time
from collections import deque
from typing import List, Dict, Union


# --- CONFIGURATION CONSTANTS ---
NUM_ATOMS = 15
NUM_NANITES = 3
TIMESTEP = 0.01
BIND_DISTANCE = 0.5
BIND_ENERGY_COST = 5.0
FORCING_COEFF = 0.05
MAX_STEERING_FORCE = 1.0
INITIAL_ENERGY = 100.0


# --- CORE UTILITY FUNCTIONS ---

def get_inertia_tensor(positions, masses, com):
    """Computes the full 3x3 inertia tensor relative to the Center of Mass (COM)."""
    r = positions - com
    I = np.zeros((3, 3))
    I[0, 0] = np.sum(masses * (r[:, 1]**2 + r[:, 2]**2))
    I[1, 1] = np.sum(masses * (r[:, 0]**2 + r[:, 2]**2))
    I[2, 2] = np.sum(masses * (r[:, 0]**2 + r[:, 1]**2))
    I[0, 1] = I[1, 0] = -np.sum(masses * r[:, 0] * r[:, 1])
    I[0, 2] = I[2, 0] = -np.sum(masses * r[:, 0] * r[:, 2])
    I[1, 2] = I[2, 1] = -np.sum(masses * r[:, 1] * r[:, 2])
    return I


# --- NANITE/SWARM CLASSES ---

class HivePulse:
    """Manages global state, claims, and atomic ownership for the swarm."""
    def __init__(self, nanites, initial_atom_masses):
        self.nanites = nanites
        self.claimed_targets = {}
        self.initial_atom_masses = initial_atom_masses

    def get_all_owned_atoms(self):
        owned = set()
        for n in self.nanites:
            owned.update(n.atom_indices)
        return owned

    def get_free_atoms(self, environment_atoms):
        owned_atoms = self.get_all_owned_atoms()
        free = [
            a for a in environment_atoms
            if a not in owned_atoms
            and a not in self.claimed_targets
        ]
        return free

    def claim_target(self, nanite_id, atom_index):
        if atom_index not in self.claimed_targets:
            self.claimed_targets[atom_index] = nanite_id
            return True
        return False

    def release_claim(self, atom_index):
        if atom_index in self.claimed_targets:
            del self.claimed_targets[atom_index]


class Nanite:
    def __init__(self, nanite_id, atom_indices, initial_masses, hive):
        self.id = nanite_id
        self.atom_indices = np.array(atom_indices)
        self.masses = initial_masses[self.atom_indices]
        self.hive = hive
        self.mode = "SEEK"
        self.target_atom_index = None
        self.energy = INITIAL_ENERGY
        self.status = "OK"

    def get_com(self, positions):
        p = positions[self.atom_indices]
        m = self.masses[:, np.newaxis]
        if np.sum(self.masses) == 0:
            return np.mean(p, axis=0)
        return np.sum(p * m, axis=0) / np.sum(self.masses)

    def acquire_atom(self, atom_index, atom_mass):
        if self.energy < BIND_ENERGY_COST:
            self.mode = "SEEK"
            self.status = "LOW_ENERGY"
            return False
        self.atom_indices = np.append(self.atom_indices, atom_index)
        self.masses = np.append(self.masses, atom_mass)
        self.energy -= BIND_ENERGY_COST
        self.mode = "STABILIZE"
        self.target_atom_index = None
        self.status = "GROWING"
        return True

    def update_behavior(self, pos, vel, f, environment_atoms):
        if self.energy < INITIAL_ENERGY:
            self.energy += 0.01
        if self.energy <= 0.0:
            self.mode = "IDLE"
            self.status = "CRITICAL_SHUTDOWN"
            return f

        if self.mode == "SEEK":
            available_targets = self.hive.get_free_atoms(environment_atoms)
            if available_targets:
                target_atom = random.choice(available_targets)
                if self.hive.claim_target(self.id, target_atom):
                    self.target_atom_index = target_atom
                    self.mode = "BIND"
                    self.status = "TARGET_ACQUIRED"
            else:
                self.mode = "IDLE"
                self.status = "NO_TARGETS"

        elif self.mode == "BIND":
            if self.target_atom_index is None:
                self.mode = "SEEK"
                return f
            target_pos = pos[self.target_atom_index]
            nanite_com = self.get_com(pos)
            dist = np.linalg.norm(target_pos - nanite_com)
            if dist < BIND_DISTANCE:
                self.mode = "ACQUIRE"
                self.status = "BINDING_PENDING"
                return f
            direction = target_pos - nanite_com
            unit_dir = direction / (dist + 1e-9)
            steering_force = unit_dir * FORCING_COEFF * self.masses[:, np.newaxis]
            steering_force = np.clip(steering_force, -MAX_STEERING_FORCE, MAX_STEERING_FORCE)
            f[self.atom_indices] += steering_force
            self.energy -= 0.005
            self.status = f"DIST={dist:.3f}"

        elif self.mode == "ACQUIRE":
            self.status = "ACQUIRING_ATOM"
            return f

        elif self.mode == "STABILIZE":
            self.status = "KINETIC_STABILIZATION"
            self.mode = "SEEK"
            return f

        elif self.mode == "IDLE":
            self.status = f"WAITING ({self.energy:.2f})"
            return f

        return f


class AtomicConstraintManager:
    def __init__(self, masses, tolerance=1e-8):
        self.masses = masses
        self.total_mass = np.sum(masses)
        self.tolerance = tolerance

    def perform_full_kinetic_stabilization(self, pos, vel):
        if self.total_mass <= 0:
            return vel
        com = np.sum(pos * self.masses[:, np.newaxis], axis=0) / self.total_mass
        com_vel = np.sum(vel * self.masses[:, np.newaxis], axis=0) / self.total_mass
        vel = vel - com_vel
        r = pos - com
        L = np.sum(np.cross(r, vel * self.masses[:, np.newaxis]), axis=0)
        I = get_inertia_tensor(pos, self.masses, com)
        det_I = np.linalg.det(I)
        if abs(det_I) > self.tolerance:
            I_inv = np.linalg.inv(I)
            omega = I_inv @ L
            v_rot = np.cross(omega, r)
            vel = vel - v_rot
        com_vel_final = np.sum(vel * self.masses[:, np.newaxis], axis=0) / self.total_mass
        vel = vel - com_vel_final
        return vel


def setup_nanites(hive, masses):
    nanite_1_indices = [0, 1, 2]
    nanite_1 = Nanite(1, nanite_1_indices, masses, hive)
    hive.nanites.append(nanite_1)
    nanite_2_indices = [3, 4, 5]
    nanite_2 = Nanite(2, nanite_2_indices, masses, hive)
    hive.nanites.append(nanite_2)
    nanite_3_indices = [6, 7, 8]
    nanite_3 = Nanite(3, nanite_3_indices, masses, hive)
    hive.nanites.append(nanite_3)
    return hive.nanites


def initialize_simulation():
    masses = np.ones(NUM_ATOMS) * 1.0
    masses[9:] = 0.5
    pos = np.random.rand(NUM_ATOMS, 3) * 10
    vel = np.zeros((NUM_ATOMS, 3))
    pos[0] = [5.0, 5.0, 5.0]
    pos[1] = [5.1, 5.0, 5.0]
    pos[2] = [5.0, 5.1, 5.0]
    pos[3] = [1.0, 1.0, 1.0]
    pos[4] = [1.1, 1.0, 1.0]
    pos[5] = [1.05, 1.1, 1.0]
    pos[6] = [8.0, 8.0, 8.0]
    pos[7] = [8.1, 8.0, 8.0]
    pos[8] = [8.2, 8.0, 8.0]
    pos[9] = [5.5, 5.5, 5.5]
    pos[10] = [1.5, 1.5, 1.5]
    pos[11] = [7.5, 7.5, 7.5]
    pos[12] = [4.0, 4.0, 4.0]
    pos[13] = [2.0, 2.0, 2.0]
    pos[14] = [6.0, 6.0, 6.0]
    environment_atoms = np.arange(NUM_ATOMS)
    constraint_manager = AtomicConstraintManager(masses)
    hive = HivePulse([], masses)
    nanites = setup_nanites(hive, masses)
    return pos, vel, masses, constraint_manager, nanites, hive, environment_atoms


def run_swarm_sim(steps=50):
    pos, vel, masses, constraint_manager, nanites, hive, environment_atoms = initialize_simulation()
    print("Swarm Engaged. Tracking Hive Claims...")
    for step in range(steps):
        f = np.zeros_like(pos)
        acquisition_events = []
        for nanite in nanites:
            f = nanite.update_behavior(pos, vel, f, environment_atoms)
            if nanite.mode == "ACQUIRE":
                acquisition_events.append((nanite.id, nanite.target_atom_index))

        for nanite_id, target_idx in acquisition_events:
            nanite = next(n for n in nanites if n.id == nanite_id)
            if hive.claimed_targets.get(target_idx) == nanite_id:
                atom_mass = masses[target_idx]
                success = nanite.acquire_atom(target_idx, atom_mass)
                if success:
                    hive.release_claim(target_idx)
                    print(f"[TRANSACTION] N{nanite_id} SUCCESS BIND on Atom {target_idx}. New size: {len(nanite.atom_indices)}. Cost: {BIND_ENERGY_COST:.2f}")
                else:
                    hive.release_claim(target_idx)
                    nanite.target_atom_index = None
                    nanite.mode = "SEEK"

        vel = vel + (f * TIMESTEP) / masses[:, np.newaxis]
        pos = pos + vel * TIMESTEP
        vel = constraint_manager.perform_full_kinetic_stabilization(pos, vel)

        if step % 5 == 0 or acquisition_events:
            print(f"\n--- STEP {step} ---")
            print(f"Hive Targets: {hive.claimed_targets}")
            for nanite in nanites:
                print(f"N{nanite.id}: Mode={nanite.mode}, Atoms={nanite.atom_indices.tolist()}, Energy={nanite.energy:.2f}, Status={nanite.status}, COM={nanite.get_com(pos)}")

            if all(n.mode == "IDLE" for n in nanites if n.status == "NO_TARGETS") and len(hive.claimed_targets) == 0:
                print("\n[SWARM STATUS] All free targets consumed. Simulation ending.")
                break


if __name__ == "__main__":
    np.random.seed(42)
    random.seed(42)
    run_swarm_sim(steps=50)

