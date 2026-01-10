#!/bin/bash
# ==============================================================================
# 🔨 STEP TWO: THE IRON-CLAD ENVIRONMENT BUILDER
# Installs Python 3.10, creates venv, and forces correct PyTorch (CPU).
# ==============================================================================

set -e

echo "💅 [Step 2] Initializing Environment Protocol..."

# 1. Install System Dependencies
echo "📦 [1/5] Installing System Libraries..."
sudo apt update
sudo apt install -y python3-pip python3-venv python3-dev python3-full build-essential \
    libopenblas-dev libffi-dev libssl-dev git

# 2. Nuke and Rebuild Venv
echo "💥 [2/5] Resetting Virtual Environment..."
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# 3. Upgrade Pip
echo "⬆️  [3/5] Upgrading Pip..."
pip install --upgrade pip

# 4. Install The Heavy Hitters (CPU Versions first to avoid conflicts)
echo "🧠 [4/5] Installing PyTorch (CPU Mode)..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 5. Install The Rest
echo "📚 [5/5] Installing AGI Dependencies..."
pip install \
    transformers \
    sentence-transformers \
    faiss-cpu \
    gradio \
    psutil \
    pyyaml \
    spacy \
    numpy

# Download SpaCy model
python -m spacy download en_core_web_sm

echo "==================================================="
echo "✅ STEP TWO COMPLETE."
echo "   Your environment is locked, loaded, and fabulous."
echo "   Run 'omni' (if using zsh) or 'python Master_Convo_Modules/OMNIGURU_PRIME.py' to launch."
echo "==================================================="
