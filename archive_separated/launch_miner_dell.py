import os
import time
import signal
import hashlib
import logging
import multiprocessing as mp
from multiprocessing import shared_memory
from dataclasses import dataclass

TOTAL_NONCES = 2**32
HEADER_SIZE = 76
DEFAULT_BATCH = 16384


@dataclass(frozen=True)
class NonceRange:
    start: int
    end: int  # exclusive


def split_nonce_ranges(worker_count: int) -> list[NonceRange]:
    if worker_count <= 0:
        raise ValueError("worker_count must be > 0")

    chunk = TOTAL_NONCES // worker_count
    ranges = []

    for i in range(worker_count):
        start = i * chunk
        end = TOTAL_NONCES if i == worker_count - 1 else (i + 1) * chunk
        ranges.append(NonceRange(start, end))

    return ranges


def sha256d(header80: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(header80).digest()).digest()


def worker_loop(
    worker_id: int,
    start_nonce: int,
    end_nonce: int,
    shm_name: str,
    generation,
    shutdown_flag,
    found_queue,
    target_prefix_zeros: int = 2,
    batch_size: int = DEFAULT_BATCH,
):
    shm = shared_memory.SharedMemory(name=shm_name)
    header_view = shm.buf

    try:
        local_generation = -1

        while True:
            if shutdown_flag.value:
                return

            current_generation = generation.value
            if current_generation == local_generation:
                time.sleep(0.001)
                continue

            local_generation = current_generation
            header_prefix = bytes(header_view[:HEADER_SIZE])

            nonce = start_nonce
            while nonce < end_nonce:
                if shutdown_flag.value:
                    return

                if generation.value != local_generation:
                    break

                upper = min(nonce + batch_size, end_nonce)

                while nonce < upper:
                    header80 = header_prefix + nonce.to_bytes(4, "little", signed=False)
                    digest = sha256d(header80)

                    if digest[:target_prefix_zeros] == b"\x00" * target_prefix_zeros:
                        found_queue.put(
                            {
                                "generation": local_generation,
                                "worker_id": worker_id,
                                "nonce": nonce,
                                "hash_hex": digest.hex(),
                            }
                        )
                    nonce += 1

    finally:
        shm.close()


class NonceEngine:
    def __init__(self, worker_count: int | None = None, logger: logging.Logger | None = None):
        self.worker_count = worker_count or os.cpu_count() or 4
        self.logger = logger or logging.getLogger("NONCE-ENGINE")
        self.ctx = mp.get_context("spawn")

        self.generation = self.ctx.Value("Q", 0)
        self.shutdown_flag = self.ctx.Value("b", 0)
        self.found_queue = self.ctx.Queue()

        self.shm = shared_memory.SharedMemory(create=True, size=HEADER_SIZE)
        self.ranges = split_nonce_ranges(self.worker_count)
        self.workers: list[mp.Process] = []

    def start(self):
        if self.workers:
            return

        self.logger.info("Dispatching persistent tasks to %d CPU cores...", self.worker_count)

        for worker_id, nonce_range in enumerate(self.ranges):
            p = self.ctx.Process(
                target=worker_loop,
                args=(
                    worker_id,
                    nonce_range.start,
                    nonce_range.end,
                    self.shm.name,
                    self.generation,
                    self.shutdown_flag,
                    self.found_queue,
                ),
                daemon=True,
            )
            p.start()
            self.workers.append(p)
            self.logger.info(
                "Core-%d started mining range %d to %d (exclusive end %d)",
                worker_id,
                nonce_range.start,
                nonce_range.end - 1,
                nonce_range.end,
            )

    def submit_job(self, header_prefix_76: bytes, job_id=None):
        if len(header_prefix_76) != HEADER_SIZE:
            raise ValueError(f"header_prefix_76 must be {HEADER_SIZE} bytes, got {len(header_prefix_76)}")

        self.shm.buf[:HEADER_SIZE] = header_prefix_76

        with self.generation.get_lock():
            self.generation.value += 1
            gen = self.generation.value

        if job_id is None:
            self.logger.info("New job received from pool: generation=%d", gen)
        else:
            self.logger.info("New job received from pool: %s", job_id)

        return gen

    def poll_found(self):
        results = []
        while not self.found_queue.empty():
            results.append(self.found_queue.get())
        return results

    def stop(self):
        self.logger.info("Stopping nonce engine...")
        self.shutdown_flag.value = 1

        for p in self.workers:
            p.join(timeout=1.5)
            if p.is_alive():
                p.terminate()
                p.join(timeout=1.0)

        self.workers.clear()

        try:
            self.shm.close()
        finally:
            self.shm.unlink()


def install_signal_handlers(engine: NonceEngine):
    def _handle_signal(signum, _frame):
        engine.logger.warning("Signal %s received, shutting down...", signum)
        engine.stop()
        raise SystemExit(0)

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(name)s] - %(message)s",
    )

    engine = NonceEngine(worker_count=4)
    install_signal_handlers(engine)
    engine.start()

    try:
        for fake_job_id in (1593572, 1593573):
            engine.submit_job(os.urandom(76), job_id=fake_job_id)
            time.sleep(1.0)

            for share in engine.poll_found():
                logging.getLogger("NONCE-ENGINE").info(
                    "Share candidate: job_gen=%s core=%s nonce=%s hash=%s",
                    share["generation"],
                    share["worker_id"],
                    share["nonce"],
                    share["hash_hex"],
                )
    finally:
        engine.stop()
