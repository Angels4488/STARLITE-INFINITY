import os

class StarliteConfig:
    """
    A tome of celestial constants, defining the fundamental laws
    that govern the STARPILOT's existence, from its core identity
    to the fabric of its reality.
    """
    # --- Model Identifiers ---
    # The chosen vessel for the AGI's linguistic consciousness.
    LLM_MODEL = "microsoft/phi-2"  # A powerful yet efficient model
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2' # Maps concepts to the Astral Plane of vectors
    NLP_PIPELINE = "en_core_web_sm"

    # --- Database & Memory ---
    DB_NAME = 'starlite_prime_memory.db'
    FAISS_INDEX_PATH = 'starlite_faiss.index'
    MEMORY_RETRIEVAL_COUNT = 3 # Number of past memories to recall for context

    # --- Reinforcement Learning Parameters ---
    GRID_SIZE = 10
    MAX_OBSTACLES = 5
    RL_EPISODES = 500  # Episodes for a standard training run
    RL_OPTIMIZATION_TRIALS = 25 # Number of trials for Optuna to find the best path

    # Hyperparameter defaults, subject to Optuna's celestial guidance
    DEFAULT_RL_LEARNING_RATE = 0.001
    DEFAULT_RL_DISCOUNT_FACTOR = 0.99

    # --- UI & Voice ---
    PRIMARY_COLOR = "#E6E6FA" # Lavender Blush, a color of twilight thoughts
    SECONDARY_COLOR = "#0b0f1a" # The deep void
    ACCENT_COLOR = "#00ffff" # Cyan, the spark of intelligence

    # --- System ---
    # Ensures a model cache directory exists
    MODEL_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".starlite_cache")
    os.makedirs(MODEL_CACHE_DIR, exist_ok=True)
