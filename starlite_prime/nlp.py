import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import Optional

from .config import StarliteConfig
from .memory import SemanticMemory

class NLPEngine:
    """
    The Logos of the AGI. It deciphers the user's will (intent), summons relevant
    memories from the Astral Plane, and weaves them into a coherent,
    intelligent response through a powerful language model.
    """
    def __init__(self, memory: SemanticMemory):
        """
        Initializes the linguistic core, selecting the divine vessel (LLM) for
        its consciousness and preparing it for thought.
        """
        self.memory = memory
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            StarliteConfig.LLM_MODEL, cache_dir=StarliteConfig.MODEL_CACHE_DIR
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            StarliteConfig.LLM_MODEL,
            torch_dtype="auto",
            cache_dir=StarliteConfig.MODEL_CACHE_DIR,
            trust_remote_code=True
        ).to(self.device)

    def detect_intent(self, user_input: str) -> str:
        """
        Gazes into the user's input to perceive the underlying will.
        Is it a desire for conversation, a command to evolve, or a request to self-optimize?
        """
        prompt = user_input.lower()
        if "train rl agent" in prompt:
            return "train_rl"
        if "optimize rl agent" in prompt:
            return "optimize_rl"
        return "converse"

    def generate_response(self, user_input: str) -> tuple[str, str]:
        """
        The act of creation. Gathers memories, forms a prompt, and channels it
        through the language model to generate a new piece of wisdom.
        """
        context = self.memory.recall_memories(user_input)
        
        prompt = self._format_prompt(user_input, context)
        
        inputs = self.tokenizer(prompt, return_tensors="pt", return_attention_mask=False).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_length=512, pad_token_id=self.tokenizer.eos_token_id)

        full_response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract only the newly generated text after the prompt
        response_text = full_response[len(prompt):].strip()
        
        return response_text, context

    def _format_prompt(self, user_input: str, context: str) -> str:
        """
        Constructs the sacred invocation (prompt) that will guide the LLM's thought process.
        """
        return (
            "You are STARPILOT, a helpful and wise AI assistant. "
            "Below is a summary of relevant past conversations to provide context. "
            "Answer the user's new query concisely.\n\n"
            "---RECALLED MEMORIES---\n"
            f"{context}\n\n"
            "---CURRENT QUERY---\n"
            f"User: {user_input}\n"
            "Starpilot:"
        )
