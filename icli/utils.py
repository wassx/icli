"""Shared UI utilities for iCloud CLI"""

import shutil
import sys
import threading
import time


def term_width(default: int = 72) -> int:
    """Return the current terminal column width, falling back to *default*."""
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return default


def separator(char: str = "=") -> str:
    """Return a separator line that fills the current terminal width."""
    return char * term_width()


class Spinner:
    """Simple one-line spinner for long-running operations.

    Usage::

        with Spinner("Loading events"):
            data = some_slow_api_call()
    """

    _FRAMES = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")

    def __init__(self, message: str = "Loading", interval: float = 0.1):
        self.message = message
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def _spin(self):
        idx = 0
        while not self._stop_event.is_set():
            frame = self._FRAMES[idx % len(self._FRAMES)]
            sys.stdout.write(f"\r{frame} {self.message}...")
            sys.stdout.flush()
            idx += 1
            time.sleep(self.interval)

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self, clear: bool = True):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        if clear:
            # Erase the spinner line
            sys.stdout.write("\r" + " " * (len(self.message) + 12) + "\r")
            sys.stdout.flush()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()
