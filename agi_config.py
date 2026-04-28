from pathlib import Path
import os

# Root directory of the STARLITE project
ROOT_DIR = Path(__file__).resolve().parent

class AGIConfig:
    """
    Central configuration for STARLITE-INFINITY / Starlite Prime.
    All other modules should import AGIConfig from here.
    """

    # ---- Identity ----
    NAME: str = "STARLITE-INFINITY"
    NODE_ID: str = os.getenv("STARLITE_NODE_ID", "LOCAL")

    # ---- Paths ----
    DATA_DIR: Path = ROOT_DIR / "data"
    LOG_DIR: Path = ROOT_DIR / "logs"
    MEMORY_DIR: Path = ROOT_DIR / "memory"
    MODEL_DIR: Path = ROOT_DIR / "models"
    RUNTIME_DIR: Path = ROOT_DIR / "runtime"

    DB_PATH: Path = DATA_DIR / "starliteprime.db"
    LOG_FILE: Path = LOG_DIR / "starlite_prime.log"
    HISTORY_FILE: Path = RUNTIME_DIR / "history.json"
    COVENANT_FILE: Path = ROOT_DIR / "ethics" / "covenant.md"

    # ---- Models (from original StarliteConfig) [file:207] ----
    MODEL_NAME: str = "mistralai/Mistral-7B-Instruct-v0.2"
    NLP_MODEL: str = "en_core_web_sm"
    SENTIMENT_MODEL_ID: str = "distilbert-base-uncased-finetuned-sst-2-english"
    EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"

    PRIMARY_COLOR: str = "#E6E6FA"
    CONTEXT_WINDOW_SIZE: int = 5

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
        "You are STARLITE-INFINITY, evolved from Starlite Prime. "
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
        ]:
            d.mkdir(parents=True, exist_ok=True)

AGIConfig.init_dirs()
