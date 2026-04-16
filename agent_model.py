import torch
import torch.nn as nn
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class StarliteModel(nn.Module):
    def __init__(self):
        super().__init__()
        # Using local path for compatibility
        self.models_path = Path("./models")
        self.models_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"StarliteModel loader ready on path → {self.models_path}")

    def load_or_create(self, name="base_manifold"):
        model_path = self.models_path / f"{name}.pt"
        if model_path.exists():
            model = torch.load(model_path, weights_only=False, map_location='cpu')
            print(f"Loaded existing model: {name}")
        else:
            # Construct the manifold
            model = nn.Sequential(
                nn.Linear(4096, 2048),
                nn.ReLU(),
                nn.Linear(2048, 1024),
                nn.ReLU(),
                nn.Linear(1024, 512)
            )
            torch.save(model, model_path)
            print(f"Created and saved new model: {name}")
        return model

if __name__ == "__main__":
    loader = StarliteModel()
    model = loader.load_or_create()
    print("Agent model ready.")
