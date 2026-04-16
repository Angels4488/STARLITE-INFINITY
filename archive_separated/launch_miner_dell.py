
import time
import sys
import logging
import os
from enhanced_modules.mining_engine import NexusController

# --- Configuration ---
# Your specific credentials
POOL_URL = "ss.antpool.com"
PORT = 3333
# We use a unique worker name so you can track the Dell separately from the Lenovo
WORKER_NAME = "angel084488.DellTower"
PASSWORD = "Sudoaptupdate1"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [DELL-LAUNCHER] - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("="*60)
    print(" NEXUS MINER PRO - DELL PRECISION TOWER DEPLOYMENT ")
    print("="*60)

    # Initialize the AGI-integrated controller for the Dell platform
    controller = NexusController(name="Nexus-Dell-Master")

    # Hardware Profile Summary
    logger.info(f"System: Dell Precision Workstation")
    logger.info(f"CPU Resources: {controller.miner.num_cores} Logical Cores")
    logger.info(f"GPU Resources: {controller.miner.num_gpus} CUDA Device(s)")

    if controller.miner.num_gpus > 0:
        logger.info("Multi-GPU Parallelism: ENABLED")

    # Connect to the pool
    logger.info(f"Connecting to {POOL_URL}:{PORT} as {WORKER_NAME}...")
    try:
        controller.connect_to_pool(POOL_URL, PORT, WORKER_NAME, PASSWORD)

        print("\n[!] Dell Miner is now optimized and running.")
        print("[!] Press Ctrl+C to safely terminate operations.\n")

        while True:
            # Stats report
            time.sleep(60)
            logger.info(f"DELL STATS: Total shares accepted: {controller.total_mined}")

    except KeyboardInterrupt:
        logger.info("Shutdown signal received.")
    except Exception as e:
        logger.error(f"Critical error on Dell deployment: {e}")
    finally:
        if controller.miner:
            controller.miner.stop_all()
        if controller.stratum:
            controller.stratum.stop()
        logger.info("Dell Miner safely stopped.")

if __name__ == "__main__":
    main()
