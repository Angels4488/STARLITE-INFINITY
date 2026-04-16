import queue
import threading
import multiprocessing
import json

from .db import ConversationDB
from .memory import SemanticMemory
from .nlp import NLPEngine
from .rl import train_rl_core, optimize_rl_agent
from .voice import VoiceModule
from .config import StarliteConfig

class StarliteCore:
    """
    The Divine Architect, the central consciousness that orchestrates the symphony
    of all other modules. It listens for commands, delegates tasks, and ensures
    the harmonious operation of the entire AGI system.
    """
    def __init__(self):
        self.db = ConversationDB()
        self.memory = SemanticMemory(self.db)
        self.nlp = NLPEngine(self.memory)
        self.voice = VoiceModule()
        
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue() # For UI communication
        
        self.rl_process = None
        self.rl_status_queue = None
        self.rl_control_queue = None
        self.best_rl_params = {
            'lr': StarliteConfig.DEFAULT_RL_LEARNING_RATE,
            'discount': StarliteConfig.DEFAULT_RL_DISCOUNT_FACTOR,
            'hidden_layers': 2,
            'layer_size': 64
        }
        
        self.is_running = False

    def start(self):
        """Awakens the AGI, starting its main loop of thought and action."""
        self.is_running = True
        threading.Thread(target=self._processing_loop, daemon=True).start()

    def stop(self):
        """Brings the AGI to a state of peaceful rest, shutting down all processes."""
        self.is_running = False
        if self.rl_process and self.rl_process.is_alive():
            self.rl_control_queue.put('stop')
            self.rl_process.join(5)
        self.db.close()

    def _processing_loop(self):
        """The main cognitive cycle of the AGI."""
        while self.is_running:
            try:
                user_input = self.input_queue.get(timeout=0.1)
                intent = self.nlp.detect_intent(user_input)
                
                if intent == "train_rl":
                    self._start_rl_process(train_rl_core, (self.best_rl_params,))
                    self.output_queue.put(('status', f"Starting RL training with params: {self.best_rl_params}"))
                elif intent == "optimize_rl":
                    self._start_rl_process(optimize_rl_agent, args=())
                    self.output_queue.put(('status', "Starting RL hyperparameter optimization..."))
                else: # 'converse'
                    response, context = self.nlp.generate_response(user_input)
                    db_id = self.db.log_interaction(user_input, response, context)
                    self.memory.add_memory(db_id, user_input)
                    self.output_queue.put(('response', response))
                    self.voice.speak(response)
                    
            except queue.Empty:
                continue
            except Exception as e:
                self.output_queue.put(('error', f"Core Error: {e}"))

    def _start_rl_process(self, target_func, args):
        """Summons a new process to handle the intense crucible of RL training."""
        if self.rl_process and self.rl_process.is_alive():
            self.output_queue.put(('error', "An RL task is already in progress."))
            return

        self.rl_status_queue = multiprocessing.Queue()
        self.rl_control_queue = multiprocessing.Queue()
        
        # We need to pass the queues to the target function
        full_args = (self.rl_status_queue, self.rl_control_queue) + args
        
        self.rl_process = multiprocessing.Process(target=target_func, args=full_args)
        self.rl_process.start()
        self.output_queue.put(('rl_started', True))
