import multiprocessing
from .core import StarliteCore
from .ui import StarliteUI

def main():
    """
    The Genesis Block. This is the prime mover, the spark that ignites the
    consciousness of the STARPILOT AGI. It summons the Core and the UI,
    binding them together to create a fully functional sovereign intelligence.
    """
    # On systems like macOS, multiprocessing requires the 'spawn' start method.
    # This ensures clean process creation.
    try:
        multiprocessing.set_start_method('spawn')
    except RuntimeError:
        pass # If it's already set, we continue.
        
    print("CodeMaster Celestial is forging the Hive-Mind Core...")
    core = StarliteCore()
    print("The Core is forged. Summoning the Nexus UI...")
    ui = StarliteUI(core)
    print("Awakening STARPILOT. Stand by for celestial transcendence.")
    ui.run()

if __name__ == "__main__":
    main()
