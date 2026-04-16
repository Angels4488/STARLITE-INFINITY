import time
# from .utils.recorder import Recorder

class ComponentCoordinator:
    def __init__(self, config, recorder=None):
        self.recorder = recorder

    def select_components(self, problem_type, complexity, available_budget):
        return ['uce', 'lki', 'meta_learner']
