import logging

logger = logging.getLogger(__name__)

class NeuralPlasticityEngine:
    """
    Self-Rewiring Engine: Prevents cognitive stagnation via Hebbian decay/reinforcement.
    Simulates the strengthening and weakening of synaptic pathways based on utility.
    """
    def __init__(self, decay_rate=0.01):
        self.synaptic_weights = {} # (path_id) -> strength
        self.decay_rate = decay_rate
        logger.info("Neural Plasticity Engine engaged.")

    def update_pathways(self, active_paths: list, outcome_score: float):
        """
        Strengthens paths involved in successful outcomes and applies global decay.
        """
        # Reinforcement
        for path in active_paths:
            self.synaptic_weights[path] = self.synaptic_weights.get(path, 0.5) + (outcome_score * 0.1)
        
        # Global Entropic Decay
        for path in list(self.synaptic_weights.keys()):
            self.synaptic_weights[path] *= (1 - self.decay_rate)
            if self.synaptic_weights[path] < 0.05:
                del self.synaptic_weights[path]

    def get_path_strength(self, path):
        return self.synaptic_weights.get(path, 0.0)
