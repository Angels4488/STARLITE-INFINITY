#!/usr/bin/env python3
"""
Starlite-Infinity Node Core: Storage & Cache Optimization Engine
Tailored for NVMe/HDD Split Architecture with 56 GB RAM Profiles.
"""

import os
import sys
from pathlib import Path

class NodeOptimizer:
    def __init__(self):
        self.bitcoin_dir = Path(os.path.expanduser("~/.bitcoin"))
        self.config_path = self.bitcoin_dir / "bitcoin.conf"
        
    def check_system_limits(self) -> int:
        """Determines optimal cache setting based on system memory boundaries."""
        if not os.path.exists('/proc/meminfo'):
            # Fallback default if not on native Linux platform
            return 36864
            
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if 'MemTotal' in line:
                        total_kb = int(line.split()[1])
                        total_mb = total_kb // 1024
                        # If system has at least 48GB RAM, lock in the 36GB cache profile
                        if total_mb > 49152:
                            return 36864
                        return int(total_mb * 0.75)
        except Exception:
            pass
        return 16384

    def deploy_config(self, target_cache: int):
        """Generates and deploys the bare-metal performance bitcoin.conf."""
        self.bitcoin_dir.mkdir(parents=True, exist_ok=True)
        
        config_payload = f"""# --- Starlite-Infinity High-Performance Execution Matrix ---
# Optimized for 56 GB RAM and Dual-Drive Storage Routing

# Memory & Cache Allocation
dbcache={target_cache}
maxmempool=300

# Thread Parallelism (0 = Auto-detect all execution cores)
par=0

# Network Throughput Constraints
maxconnections=100
listen=0

# Database Constraints (Suppressed for high-speed Initial Block Download)
txindex=0
"""
        with open(self.config_path, "w") as f:
            f.write(config_payload.strip() + "\n")
        
        print(f"[+] Performance matrix deployed successfully to: {self.config_path}")
        print(f"[+] Assigned dbcache allocation: {target_cache} MiB")

if __name__ == "__main__":
    print("[*] Initiating hardware validation and configuration injection...")
    optimizer = NodeOptimizer()
    optimal_cache = optimizer.check_system_limits()
    optimizer.deploy_config(optimal_cache)
