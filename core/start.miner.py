from __future__ import annotations

import logging
import signal
import sys
import threading
import time
from types import FrameType
from typing import Optional

logger = logging.getLogger("precision_beast")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

_shutdown_requested = threading.Event()


class PrecisionBeastController:
    def __init__(self) -> None:
        self._stop_event = threading.Event()
        self._stopped = threading.Event()
        self._lock = threading.Lock()
        self._stop_called = False
        self._threads: list[threading.Thread] = []

    def start(self) -> None:
        logger.info("[BEAST] starting controller")

        stratum_thread = threading.Thread(
            target=self._stratum_loop,
            name="stratum-loop",
            daemon=False,
        )
        beast_thread = threading.Thread(
            target=self._beast_loop,
            name="beast-loop",
            daemon=False,
        )

        self._threads.extend([stratum_thread, beast_thread])

        for t in self._threads:
            t.start()

    def stop(self, join_timeout: float = 10.0) -> None:
        with self._lock:
            if self._stop_called:
                return
            self._stop_called = True

        logger.info("[BEAST] stop requested")
        self._stop_event.set()

        self._close_network_resources()

        deadline = time.monotonic() + join_timeout
        for t in list(self._threads):
            remaining = max(0.0, deadline - time.monotonic())
            if t.is_alive():
                logger.info("[BEAST] joining thread=%s timeout=%.2f", t.name, remaining)
                t.join(timeout=remaining)

        alive = [t.name for t in self._threads if t.is_alive()]
        if alive:
            logger.warning("[BEAST] threads still alive after timeout: %s", alive)
        else:
            logger.info("[BEAST] all worker threads stopped cleanly")

        self._stopped.set()

    def wait_stopped(self, timeout: Optional[float] = None) -> bool:
        return self._stopped.wait(timeout=timeout)

    def should_stop(self) -> bool:
        return self._stop_event.is_set()

    def _close_network_resources(self) -> None:
        logger.info("[BEAST] closing sockets / pool connections")
        # Example:
        # if self.stratum_client is not None:
        #     self.stratum_client.close()

    def _stratum_loop(self) -> None:
        logger.info("[BEAST] stratum loop started")
        try:
            while not self.should_stop():
                # Keep blocking ops bounded so shutdown can be observed.
                # Example:
                # self.stratum_client.recv_with_timeout(timeout=1.0)
                time.sleep(0.25)
        except Exception:
            logger.exception("[BEAST] stratum loop crashed")
            self._stop_event.set()
            _shutdown_requested.set()
        finally:
            logger.info("[BEAST] stratum loop exited")

    def _beast_loop(self) -> None:
        logger.info("[BEAST] beast loop started")
        try:
            while not self.should_stop():
                # Mining / orchestration tick
                time.sleep(0.25)
        except Exception:
            logger.exception("[BEAST] beast loop crashed")
            self._stop_event.set()
            _shutdown_requested.set()
        finally:
            logger.info("[BEAST] beast loop exited")


def install_signal_handlers(controller: PrecisionBeastController) -> None:
    def handler(signum: int, frame: Optional[FrameType]) -> None:
        if _shutdown_requested.is_set():
            logger.warning("[BEAST] second signal %s received, forcing exit", signum)
            raise SystemExit(128 + signum)

        logger.warning("[BEAST] signal %s received, requesting shutdown", signum)
        _shutdown_requested.set()
        controller.stop()

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


def main() -> int:
    controller = PrecisionBeastController()
    install_signal_handlers(controller)
    controller.start()

    try:
        while not _shutdown_requested.is_set():
            time.sleep(0.5)
    finally:
        controller.stop()
        controller.wait_stopped(timeout=2.0)

    logger.info("[BEAST] shutdown complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
