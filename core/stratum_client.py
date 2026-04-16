
import socket
import json
import logging
import threading
import time
from typing import Dict, Any, Optional, Callable

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [STRATUM-CLIENT] - %(message)s')
logger = logging.getLogger(__name__)

class StratumClient:
    """
    StratumClient: Manages JSON-RPC connection to a mining pool.
    Supports mining.subscribe, mining.authorize, and mining.submit.
    """

    def __init__(self, host: str, port: int, worker_name: str, password: str = "x"):
        self.host = host
        self.port = port
        self.worker_name = worker_name
        self.password = password
        self.sock: Optional[socket.socket] = None
        self.extranonce1: Optional[str] = None
        self.extranonce2_size: int = 0
        self.authorized = False
        self.subscription_id: Optional[str] = None
        self.job_callback: Optional[Callable] = None
        self.running = False
        self._message_id = 1

    def connect(self) -> bool:
        """Establishes socket connection and initiates subscription."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.running = True
            logger.info(f"Connected to {self.host}:{self.port}")

            # Start message listener thread
            threading.Thread(target=self._listen, daemon=True).start()

            # Step 1: Subscribe
            self.send_request("mining.subscribe", [])
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def send_request(self, method: str, params: list):
        """Sends a JSON-RPC request to the pool."""
        request = {
            "id": self._message_id,
            "method": method,
            "params": params
        }
        self._message_id += 1
        msg = json.dumps(request) + "\n"
        self.sock.sendall(msg.encode())
        logger.debug(f"Sent: {msg.strip()}")

    def _listen(self):
        """Listens for incoming messages from the pool."""
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(4096).decode()
                if not data:
                    break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line:
                        self._handle_message(json.loads(line))
            except Exception as e:
                logger.error(f"Listener error: {e}")
                break
        self.running = False
        logger.warning("Stratum connection closed.")

    def _handle_message(self, msg: Dict[str, Any]):
        """Handles JSON-RPC responses and notifications."""
        method = msg.get("method")
        msg_id = msg.get("id")
        result = msg.get("result")
        params = msg.get("params")

        if msg_id == 1: # Response to mining.subscribe
            # result: [[["mining.set_difficulty", "sub_id"], ["mining.notify", "sub_id"]], "extranonce1", extranonce2_size]
            if result and len(result) >= 3:
                self.extranonce1 = result[1]
                self.extranonce2_size = result[2]
                logger.info(f"Subscribed. ExtraNonce1: {self.extranonce1}, Size: {self.extranonce2_size}")
                # Step 2: Authorize
                self.send_request("mining.authorize", [self.worker_name, self.password])

        elif msg_id == 2: # Response to mining.authorize
            if result is True:
                self.authorized = True
                logger.info(f"Authorized as {self.worker_name}")
            else:
                logger.error(f"Authorization failed for {self.worker_name}")

        elif method == "mining.notify":
            # params: [job_id, prevhash, coinb1, coinb2, [merkle_branch], version, nbits, ntime, clean_jobs]
            if self.job_callback:
                self.job_callback(params)

        elif method == "mining.set_difficulty":
            logger.info(f"Pool set difficulty to: {params[0]}")

    def submit_share(self, job_id: str, extranonce2: str, ntime: str, nonce: str):
        """Submits a found share (nonce) to the pool."""
        # params: [worker_name, job_id, extranonce2, ntime, nonce]
        self.send_request("mining.submit", [self.worker_name, job_id, extranonce2, ntime, nonce])
        logger.info(f"Submitted share for job {job_id}")

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()

if __name__ == "__main__":
    # Test connection to a public test pool (dry run)
    client = StratumClient("solo.antpool.com", 3333, "worker.1")
    # client.connect() # Uncomment to test real connection
    print("StratumClient initialized.")
