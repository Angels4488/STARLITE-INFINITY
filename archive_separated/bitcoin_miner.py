# bitcoin_miner.py
import hashlib
import time
import sqlite3
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any
# ----------------------------------------------------------------------
# Bitcoin block header handling (based on Bitcoin Developer Reference)[web:146]
# ----------------------------------------------------------------------
@dataclass
class BitcoinHeader:
    version: int
    prev_block: bytes # 32 bytes, internal little‑endian
    merkle_root: bytes # 32 bytes, internal little‑endian
    timestamp: int # Unix time
    nbits: int # compact target encoding
    nonce: int # 4‑byte nonce
    @classmethod
    def from_hex(cls, header_hex: str) -> "BitcoinHeader":
        raw = bytes.fromhex(header_hex)
        if len(raw) != 80:
            raise ValueError(f"Bitcoin header must be 80 bytes, got {len(raw)}")
        return cls(
            version=int.from_bytes(raw[0:4], "little"),
            prev_block=raw[4:36],
            merkle_root=raw[36:68],
            timestamp=int.from_bytes(raw[68:72], "little"),
            nbits=int.from_bytes(raw[72:76], "little"),
            nonce=int.from_bytes(raw[76:80], "little"),
        )
    def serialize(self) -> bytes:
        """Serialize the 80‑byte header exactly as Bitcoin does (little‑endian fields)."""
        return b"".join([
            self.version.to_bytes(4, "little"),
            self.prev_block,
            self.merkle_root,
            self.timestamp.to_bytes(4, "little"),
            self.nbits.to_bytes(4, "little"),
            self.nonce.to_bytes(4, "little"),
        ])
    def hash256(self) -> bytes:
        """Double SHA‑256 of the serialized header."""
        first = hashlib.sha256(self.serialize()).digest()
        return hashlib.sha256(first).digest()
    def block_hash_hex(self) -> str:
        """Hash as displayed by block explorers (big‑endian)."""
        return self.hash256()[::-1].hex()
def nbits_to_target(nbits: int) -> int:
    """Decode the compact nBits field into the integer target threshold.""" #[web:159][web:146]
    exponent = (nbits >> 24) & 0xff
    coefficient = nbits & 0x007fffff
    if nbits & 0x00800000:
        raise ValueError("sign bit set in nBits")
    if exponent <= 3:
        return coefficient >> (8 * (3 - exponent))
    return coefficient << (8 * (exponent - 3))
def header_meets_target(header: BitcoinHeader) -> bool:
    """True iff the header's hash satisfies the PoW target."""
    target = nbits_to_target(header.nbits)
    header_hash_int = int.from_bytes(header.hash256(), "big")
    return header_hash_int <= target
# ----------------------------------------------------------------------
# SQLite logging store
# ----------------------------------------------------------------------
class MiningStore:
    """Simple SQLite logger for mining attempts and results."""
    CREATE_SQL = """
    CREATE TABLE IF NOT EXISTS mining_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_label TEXT NOT NULL,
        mode TEXT NOT NULL, -- historical_validate | simulated_mine | live_mine
        started_at INTEGER NOT NULL,
        ended_at INTEGER,
        notes TEXT
    );
    CREATE TABLE IF NOT EXISTS mined_headers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id INTEGER NOT NULL,
        source TEXT NOT NULL, -- api | fixture | synthetic
        header_hex TEXT NOT NULL,
        version INTEGER NOT NULL,
        prev_block_hex TEXT NOT NULL,
        merkle_root_hex TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        nbits INTEGER NOT NULL,
        nonce INTEGER NOT NULL,
        target_hex TEXT NOT NULL,
        block_hash_hex TEXT NOT NULL,
        valid_pow INTEGER NOT NULL, -- 0/1
        attempts INTEGER,
        elapsed_ms INTEGER,
        created_at INTEGER NOT NULL,
        FOREIGN KEY(run_id) REFERENCES mining_runs(id)
    );
    CREATE INDEX IF NOT EXISTS idx_mined_headers_run_id ON mined_headers(run_id);
    CREATE INDEX IF NOT EXISTS idx_mined_headers_valid_pow ON mined_headers(valid_pow);
    CREATE INDEX IF NOT EXISTS idx_mined_headers_timestamp ON mined_headers(timestamp);
    """
    def __init__(self, db_path: str = "/media/agi/bitcoin_mining.db"):
        self.db_path = db_path
        self._init_db()
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(self.CREATE_SQL)
    def start_run(self, label: str, mode: str, notes: str = "") -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO mining_runs (run_label, mode, started_at, notes) VALUES (?, ?, ?, ?)",
                (label, mode, int(time.time()), notes),
            )
            return cur.lastrowid
    def finish_run(self, run_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE mining_runs SET ended_at = ? WHERE id = ?",
                (int(time.time()), run_id),
            )
    def log_header(
        self,
        run_id: int,
        source: str,
        header: BitcoinHeader,
        valid_pow: bool,
        attempts: int,
        elapsed_s: float,
    ):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO mined_headers (
                    run_id, source, header_hex, version, prev_block_hex,
                    merkle_root_hex, timestamp, nbits, nonce, target_hex,
                    block_hash_hex, valid_pow, attempts, elapsed_ms, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    source,
                    header.serialize().hex(),
                    header.version,
                    header.prev_block.hex(),
                    header.merkle_root.hex(),
                    header.timestamp,
                    header.nbits,
                    header.nonce,
                    header_meets_target(header).__str__(), # store target hex for debugging
                    header.block_hash_hex(),
                    int(valid_pow),
                    attempts,
                    int(elapsed_s * 1000),
                    int(time.time()),
                ),
            )
# ----------------------------------------------------------------------
# Bitcoin miner (nonce‑based, with optional extraNonce via timestamp)
# ----------------------------------------------------------------------
class BitcoinMiner:
    """
    Mines a Bitcoin‑style block header by varying the 4‑byte nonce.
    If the nonce space is exhausted, the miner can optionally bump the
    timestamp (extraNonce) and continue – mimicking what real miners do.
    """
    def __init__(
        self,
        target_bits: Optional[int] = 1,
        db_path: str = "/media/agi/bitcoin_mining.db",
        max_nonce: int = 2**32 - 1,
        timestamp_step: int = 1,
    ):
        """
        target_bits: if set, overrides the nBits-derived target with a synthetic
                    difficulty expressed as required leading zero bits.
        db_path: where to store SQLite logs.
        max_nonce: upper bound for nonce search before considering extra work.
        timestamp_step: seconds to add to header.timestamp when nonce space is exhausted.
        """
        self.store = MiningStore(db_path)
        self.target_bits = target_bits
        self.max_nonce = max_nonce
        self.timestamp_step = timestamp_step
        # If target_bits is None we will derive target from header.nbits on each call.
    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_target(self, header: BitcoinHeader) -> int:
        if self.target_bits is not None:
            # target = 2**(256 - target_bits)
            return 1 << (256 - self.target_bits)
        return nbits_to_target(header.nbits)
    def _mine_once(self, header: BitcoinHeader) -> Optional[Dict[str, Any]]:
        """Try to find a valid nonce for the given header (no timestamp change)."""
        target = self._get_target(header)
        start = time.perf_counter()
        attempts = 0
        for nonce in range(self.max_nonce + 1):
            header.nonce = nonce
            if int.from_bytes(header.hash256(), "big") <= target:
                elapsed = time.perf_counter() - start
                return {
                    "nonce": nonce,
                    "hash_hex": header.block_hash_hex(),
                    "attempts": attempts + 1,
                    "elapsed_s": elapsed,
                }
            attempts += 1
        return None # nonce space exhausted
    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def mine_block(
        self,
        header: BitcoinHeader,
        run_label: str = "btc_mine",
        mode: str = "simulated_mine",
        allow_timestamp_roll: bool = True,
        progress_cb: Optional[Callable[[int], None]] = None,
    ) -> Dict[str, Any]:
        """
        Attempt to mine a block. Returns a dict with success info or
        raises RuntimeError if unable to satisfy target after exhausting
        nonce space and (optionally) timestamp rolls.
        The method logs each attempt run to SQLite via MiningStore.
        """
        run_id = self.store.start_run(run_label, mode, notes=f"target_bits={self.target_bits}")
        start_wall = time.perf_counter()
        total_attempts = 0
        work_header = BitcoinHeader(
            version=header.version,
            prev_block=header.prev_block,
            merkle_root=header.merkle_root,
            timestamp=header.timestamp,
            nbits=header.nbits,
            nonce=header.nonce,
        )
        while True:
            result = self._mine_once(work_header)
            if result is not None:
                break
            if progress_cb:
                progress_cb(total_attempts)
            if result is not None:
                # Success!
                wall_elapsed = time.perf_counter() - start_wall
                self.store.finish_run(run_id)
                self.store.log_header(
                    run_id=run_id,
                    source="synthetic" if mode == "simulated_mine" else "live",
                    header=work_header,
                    valid_pow=True,
                    attempts=result["attempts"] + total_attempts,
                    elapsed_s=result["elapsed_s"],
                )
                return {
                    "success": True,
                    "header": work_header,
                    "nonce": result["nonce"],
                    "hash_hex": result["hash_hex"],
                    "attempts": result["attempts"] + total_attempts,
                    "elapsed_s": result["elapsed_s"],
                    "wall_elapsed_s": wall_elapsed,
                    "run_id": run_id,
                }
            # Nonce space exhausted – optionally roll timestamp and continue
            if not allow_timestamp_roll:
                break
            work_header.timestamp += self.timestamp_step
            total_attempts += self.max_nonce + 1 # we tried all nonces for this timestamp
            # Optional: you could add a max timestamp limit here to avoid infinite loops
        # If we get here, we failed to find a solution
        wall_elapsed = time.perf_counter() - start_wall
        self.store.finish_run(run_id)
        self.store.log_header(
            run_id=run_id,
            source="synthetic" if mode == "simulated_mine" else "live",
            header=work_header,
            valid_pow=False,
            attempts=total_attempts,
            elapsed_s=wall_elapsed,
        )
        raise RuntimeError(
            f"Exhausted nonce space ({self.max_nonce + 1} nonces) and timestamp rolling "
            f"without meeting target after {wall_elapsed:.2f}s."
        )
    # ------------------------------------------------------------------
    # Validation helper (useful for historical checks)
    # ------------------------------------------------------------------
    @staticmethod
    def validate_header(header: BitcoinHeader) -> bool:
        """Return True if the header's stored nonce satisfies the target."""
        return header_meets_target(header)
# ----------------------------------------------------------------------
# Example usage (run as script to see a quick demo)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Example 1: Validate the real Bitcoin block #500000
    # Block hash from explorer: 00000000000000000000abb5f60029926dc111a1657644fee8f7d206e040ab89
    # We need the full 80‑byte header – fetch it from a public API or a known fixture.
    # For demo we use a known header hex for block 500000 (source: blockchain.com):
    header_hex_500 = (
        "02000000" # version
        "6a625f06636b8bb6ac7b960a8d03705d1ace08b1a19da3fdcc99ddbd" # prev_block
        "9480b5e91ef6b1bd178fee2e668f9ba3ef201a6ac6f5ef749cb6434ef63309b6d" # merkle_root
        "5a3b6ed5" # timestamp (little‑endian) = 2017‑12‑18 18:35:25
        "f1c14f1a" # nbits = 0x1a4fc1f1
        "d5c59505" # nonce = 0x0595c5d5 = 1560058197
    )
    header_500 = BitcoinHeader.from_hex('header_hex_500')
    print("Block #500000 validation:", BitcoinMiner.validate_header(header_500)) # should be True
    print("Hash:", header_500.block_hash_hex())
    print("Target (from nbits):", hex(nbits_to_target(header_500.nbits)))
    # Example 2: Mine a block with artificially low difficulty (e.g., 20 leading zero bits)
    # Start from the same header but lower the target to make mining fast.
    synth_header = BitcoinHeader(
        version=header_500.version,
        prev_block=header_500.prev_block,
        merkle_root=header_500.merkle_root,
        timestamp=header_500.timestamp,
        nbits=header_500.nbits, # will be ignored if target_bits set
        nonce=header_500.nonce,
    )
    miner = BitcoinMiner(target_bits=20) # ~1M hashes expected
    print("\nMining with target_bits=20 (synthetic easy)...")
    result = miner.mine_block(
        synth_header,
        run_label="demo_easy",
        mode="simulated_mine",
        allow_timestamp_roll=True,
        progress_cb=lambda cnt: None if cnt % 200_000 else print(f" tried {cnt:,} nonces"),
    )
    print("Success:", result["success"])
    print("Nonce found:", result["nonce"])
    print("Hash:", result["hash_hex"])
    print("Attempts:", result["attempts"])
    print("Elapsed (s):", result["elapsed_s"])
