
import hashlib
import time
import multiprocessing
import os
import logging
import threading
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
from typing import List, Dict, Any, Optional, Tuple
from enhanced_modules.nonce_engine import worker_task, gpu_worker_task
from enhanced_modules.stratum_client import StratumClient
from enhanced_modules.agent_framework import BaseAgent

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [MINING-ENGINE] - %(message)s')
logger = logging.getLogger(__name__)

class NexusMiner:
    """
    NexusMiner: Orchestrates CPU and GPU engines.
    Optimized for Dell Precision and Lenovo ThinkStation workstations.
    """
    
    def __init__(self, num_cores: Optional[int] = None, use_gpu: bool = True):
        self.num_cores = num_cores or os.cpu_count()
        self.use_gpu = use_gpu and HAS_TORCH and torch.cuda.is_available()
        self.num_gpus = torch.cuda.device_count() if self.use_gpu else 0
        self.result_queue = multiprocessing.Queue()
        self.processes: List[multiprocessing.Process] = []
        self.current_job: Optional[Dict] = None
        logger.info(f"NexusMiner initialized. Cores: {self.num_cores}, GPUs: {self.num_gpus}")

    def construct_block_header(self, version: int, prev_block_hash: str, merkle_root: str, timestamp: int, bits: int) -> bytes:
        """Constructs the 76-byte header prefix (excluding the 4-byte nonce)."""
        header = (
            version.to_bytes(4, 'little') +
            bytes.fromhex(prev_block_hash)[::-1] +
            bytes.fromhex(merkle_root)[::-1] +
            timestamp.to_bytes(4, 'little') +
            bits.to_bytes(4, 'little')
        )
        return header

    def decode_target(self, bits: int) -> int:
        """Converts the 'bits' field to a 256-bit target."""
        exponent = bits >> 24
        coefficient = bits & 0xFFFFFF
        target = coefficient * (2 ** (8 * (exponent - 3)))
        return target

    def start_mining(self, header_prefix: bytes, target: int):
        """Dispatches work to all CPU and GPU units."""
        self.stop_all() # Ensure clean state
        
        # 1. Dispatch to all available GPUs (common in high-end Dell T7000 series)
        if self.use_gpu:
            for gpu_id in range(self.num_gpus):
                logger.info(f"Dispatching task to GPU-{gpu_id}...")
                p_gpu = multiprocessing.Process(
                    target=gpu_worker_task,
                    args=(gpu_id, header_prefix, 0, 0xFFFFFFFF, target, self.result_queue)
                )
                self.processes.append(p_gpu)
                p_gpu.start()

        # 2. Dispatch to all CPU cores (highly effective on Xeon-based Dell Towers)
        nonce_range_per_core = 0xFFFFFFFF // self.num_cores
        logger.info(f"Dispatching tasks to {self.num_cores} CPU cores...")
        for i in range(self.num_cores):
            start_nonce = i * nonce_range_per_core
            end_nonce = (i + 1) * nonce_range_per_core if i != self.num_cores - 1 else 0xFFFFFFFF
            
            p = multiprocessing.Process(
                target=worker_task, 
                args=(i, header_prefix, start_nonce, end_nonce, target, self.result_queue)
            )
            self.processes.append(p)
            p.start()

    def monitor(self) -> Optional[Tuple[int, str]]:
        """Monitors the result queue for a successful nonce."""
        try:
            while True:
                if not self.result_queue.empty():
                    res = self.result_queue.get()
                    self.stop_all()
                    return res
                
                if not any(p.is_alive() for p in self.processes):
                    if not self.result_queue.empty():
                        res = self.result_queue.get()
                        self.stop_all()
                        return res
                    break
                
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop_all()
        return None

    def stop_all(self):
        """Terminates all mining processes."""
        if self.processes:
            logger.info("Stopping all mining processes...")
            for p in self.processes:
                if p.is_alive():
                    p.terminate()
            for p in self.processes:
                p.join()
            self.processes = []

class NexusController(BaseAgent):
    """
    NexusController: An AGI-integrated mining agent.
    Manages Stratum pool connections and hardware resources.
    """
    def __init__(self, name: str = "NexusMiner-PRO"):
        super().__init__(name, personality="Diligent & Resource-Efficient")
        self.miner = NexusMiner()
        self.stratum: Optional[StratumClient] = None
        self.total_mined = 0

    def connect_to_pool(self, host: str, port: int, worker: str, password: str = "x"):
        """Connects to a Stratum pool and sets up job callback."""
        self.stratum = StratumClient(host, port, worker, password)
        self.stratum.job_callback = self._on_new_job
        self.stratum.connect()

    def _on_new_job(self, params: List):
        """Triggered when the pool sends a new mining job."""
        # params: [job_id, prevhash, coinb1, coinb2, [merkle_branch], version, nbits, ntime, clean_jobs]
        job_id = params[0]
        prev_hash = params[1]
        coinb1 = params[2]
        coinb2 = params[3]
        merkle_branch = params[4]
        version = int(params[5], 16)
        nbits = int(params[6], 16)
        ntime = params[7]
        
        logger.info(f"New job received from pool: {job_id}")
        
        # 1. Generate extranonce2 (e.g., 00000001)
        extranonce2 = "00000001"
        extranonce1 = self.stratum.extranonce1 if self.stratum else "00000000"
        
        # 2. Build Coinbase Transaction
        coinbase_hex = coinb1 + extranonce1 + extranonce2 + coinb2
        coinbase_hash = hashlib.sha256(hashlib.sha256(bytes.fromhex(coinbase_hex)).digest()).digest()
        
        # 3. Calculate Merkle Root
        merkle_root = coinbase_hash
        for branch in merkle_branch:
            merkle_root = hashlib.sha256(hashlib.sha256(merkle_root + bytes.fromhex(branch)).digest()).digest()
        
        merkle_root_hex = merkle_root.hex()
        target = self.miner.decode_target(nbits)
        
        # 4. Construct Header Prefix
        header_prefix = self.miner.construct_block_header(version, prev_hash, merkle_root_hex, int(ntime, 16), nbits)
        
        # 5. Start Mining
        self.miner.start_mining(header_prefix, target)
        
        # Monitor for result in a separate thread
        threading.Thread(target=self._monitor_result, args=(job_id, extranonce2, ntime), daemon=True).start()

    def _monitor_result(self, job_id: str, extranonce2: str, ntime: str):
        result = self.miner.monitor()
        if result and self.stratum:
            nonce_val, hash_hex = result
            # Convert nonce to 4-byte little-endian hex string
            nonce_hex = nonce_val.to_bytes(4, 'little').hex()
            self.stratum.submit_share(job_id, extranonce2, ntime, nonce_hex)
            self.total_mined += 1
            logger.info(f"Share submitted for job {job_id} (Nonce: {nonce_hex})")

    def reason(self, input_signal: str) -> str:
        return f"{self.name} analyzing {input_signal}..."

    def act(self, goal: str) -> bool:
        logger.info(f"{self.name} executing: {goal}")
        return True

if __name__ == "__main__":
    controller = NexusController()
    print(f"\n--- {controller.name} STRATUM & GPU READY ---")
    print(f"Hardware Profile: {controller.miner.num_cores} Cores, GPU Acceleration: {'Active' if controller.miner.use_gpu else 'Inactive (Torch/CUDA missing)'}")
    # To run for real: controller.connect_to_pool("solo.antpool.com", 3333, "myworker")
