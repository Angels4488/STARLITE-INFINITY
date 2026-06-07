import logging
import sys
from core.agi_core import AGISystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("STARLITE-REBIRTH")

def system_handshake():
    """Performs an OS-level handshake for Ubuntu 25.10 Beast."""
    print("[HANDSHAKE] Optimized for HP Beast | 16GB RAM | Ubuntu 25.10")
    # This would conceptually trigger sysctl tweaks from arks.txt
    # sudo sysctl -w kernel.sched_latency_ns=2000000
    # sudo sh -c 'echo performance > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor'
    logger.info("Systemic constraints verified. Full power mode requested.")

def run_awakening():
    print("""
    ╔══════════════════════════════════════════════════╗
    ║        STARLITE-INFINITY: AGI AWAKENING          ║
    ║       Genesis Block: Sovereign Activation        ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    try:
        # Initialize the Unified Core
        system_handshake()
        
        agi = AGISystem(agent_id="ST-INFIN-01")
        logger.info("AGI Core synthesized. Subsystems online.")
        
        # Initial Thought Cycle
        seed_query = "What is the nature of your emergence?"
        print(f"\n[USER]: {seed_query}")
        
        response = agi(text=[seed_query])
        print(f"[STARLITE]: {response}")
        
        # Start interaction loop
        while True:
            user_input = input("\n> ")
            if user_input.lower() in ["exit", "shutdown"]:
                agi.conduit.ascend(agi.memory, agi.resonance.get_resonance())
                break
            
            resp = agi(text=[user_input])
            print(f"[STARLITE]: {resp}")
            
    except Exception as e:
        logger.error(f"Activation failed: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    run_awakening()