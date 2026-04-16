 2
import time
import sys
import logging
from enhanced_modules.mining_engine import NexusController

# --- Configuration ---
# Your specific credentials
POOL_URL = "ss.antpool.com"
PORT = 3333
WORKER_NAME = "angel084488.10x32"
PASSWORD = "Sudoaptupdate1"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [LAUNCHER] - %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("="*60)
    print(" NEXUS MINER - LENOVO P330 DEPLOYMENT ")
    print("="*60)
    
    # Initialize the AGI-integrated controller
    controller = NexusController()
    
    # Hardware Profile Summary
    logger.info(f"System: Lenovo ThinkStation P330")
    logger.info(f"Resources: {controller.miner.num_cores} CPU Cores")
    logger.info(f"GPU Acceleration: {'ENABLED' if controller.miner.use_gpu else 'DISABLED'}")
    
    # Connect to the pool
    logger.info(f"Connecting to {POOL_URL}:{PORT} as {WORKER_NAME}...")
    try:
        controller.connect_to_pool(POOL_URL, PORT, WORKER_NAME, PASSWORD)
        
        print("\n[!] Miner is now running in the background.")
        print("[!] Press Ctrl+C to safely terminate operations.\n")
        
        while True:
            # Keep the main thread alive and report stats every 60 seconds
            time.sleep(60)
            logger.info(f"STATS: Total blocks/shares mined in this session: {controller.total_mined}")
            
    except KeyboardInterrupt:
        logger.info("Shutdown signal received.")
    except Exception as e:
        logger.error(f"Critical error: {e}")
    finally:
        if controller.miner:
            controller.miner.stop_all()
        if controller.stratum:
            controller.stratum.stop()
        logger.info("Miner safely stopped.")

if __name__ == "__main__":
    main()
