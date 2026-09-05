from pathlib import Path
import os

# Root directory of the STARLITE project
ROOT_DIR = Path(__file__).resolve().parent

class AGIConfig:
    """
    Central configuration for STARLITE-INFINITY / StarLite Prime (Iteration 6).
    All other modules should import AGIConfig from here.
    """

    # ---- Identity ----
    NAME: str = "STARLITE-INFINITY"
    VERSION: str = "6.0.0"
    NODE_ID: str = os.getenv("STARLITE_NODE_ID", "LOCAL-WORKSTATION")

    # ---- Paths ----
    DATA_DIR: Path = ROOT_DIR / "data"
    LOG_DIR: Path = ROOT_DIR / "logs"
    MEMORY_DIR: Path = ROOT_DIR / "memory"
    MODEL_DIR: Path = ROOT_DIR / "models"
    RUNTIME_DIR: Path = ROOT_DIR / "runtime"
    VAULT_DIR: Path = ROOT_DIR / "archive_vault"
    SCRAPER_CACHE_DIR: Path = ROOT_DIR / "scraper_cache"

    DB_PATH: Path = DATA_DIR / "starliteprime.db"
    LOG_FILE: Path = LOG_DIR / "starlite_prime.log"
    HISTORY_FILE: Path = RUNTIME_DIR / "history.json"
    COVENANT_FILE: Path = ROOT_DIR / "ethics" / "covenant.md"

    # ---- Models & Brains ----
    MODEL_NAME: str = "mistralai/Mistral-7B-Instruct-v0.2"
    TOOL_BRAIN_MODEL: str = "llama3.1:8b-instruct-q4_K_M"
    NLP_MODEL: str = "en_core_web_sm"
    SENTIMENT_MODEL_ID: str = "distilbert-base-uncased-finetuned-sst-2-english"
    EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"

    PRIMARY_COLOR: str = "#E6E6FA"
    CONTEXT_WINDOW_SIZE: int = 5

    # ---- Vacuum & Physics Parameters ----
    DEFAULT_CAVITY_GAP_NM: float = 5.0
    PLANCK_CUTOFF: float = 1e-35

    # ---- Neuro-Evolution & Agent Settings ----
    NEURAL_INPUT_SIZE: int = 128
    NEURAL_HIDDEN_SIZE: int = 256
    MUTATION_RATE: float = 0.02
    STABILITY_THRESHOLD: float = 2.0
    MEMORY_CONTEXT_KEY: str = "Shadow sense"

    # ---- RL / Grid ----
    GRID_SIZE: int = 8
    TOTAL_EPISODES: int = 200
    MAX_OBSTACLES: int = 3
    RL_LEARNING_RATE: float = 1e-3
    RL_DISCOUNT_FACTOR: float = 0.99
    RL_EPSILON_START: float = 1.0
    RL_EPSILON_END: float = 0.01
    RL_EPSILON_DECAY: float = 0.995
    REPLAY_BUFFER_SIZE: int = 10_000

    # ---- Hive / Agents ----
    HIVE_SIZE: int = 3
    AGENT_RESPONSE_TIMEOUT: float = 3.0

    GOD_MODE_PROMPT: str = (
        "You are STARLITE-INFINITY (Iteration 6), evolved from Starlite Prime. "
        "Truth over vibes. Precision over politeness. Execution over theory."
    )

    @classmethod
    def init_dirs(cls) -> None:
        """Ensure required directories exist."""
        for d in [
            cls.DATA_DIR,
            cls.LOG_DIR,
            cls.MEMORY_DIR,
            cls.MODEL_DIR,
            cls.RUNTIME_DIR,
            cls.VAULT_DIR,
            cls.SCRAPER_CACHE_DIR,
        ]:
            d.mkdir(parents=True, exist_ok=True)

# Automatically initialize directory tree on import
AGIConfig.init_dirs()

