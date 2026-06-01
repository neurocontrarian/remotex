"""Best-effort execution logger for diagnosing button click → output dialog flow.

Writes to <config_dir>/execution.log. Thread-safe, never raises.
Rotates at 64 KB to keep the file small.
"""
from __future__ import annotations

import threading
import time
from pathlib import Path

_LOCK = threading.Lock()
_PATH: Path | None = None


def set_log_path(path: Path) -> None:
    """Set the log file path. Called once at app startup."""
    global _PATH
    _PATH = path
    try:
        if _PATH.exists() and _PATH.stat().st_size > 64 * 1024:
            _PATH.unlink()
    except OSError:
        pass
    log(f"=== session start (pid={_pid()}, platform={_platform()}) ===")


def log(msg: str) -> None:
    """Append a timestamped message to the log file. Never raises."""
    if _PATH is None:
        return
    try:
        ts = time.strftime("%H:%M:%S")
        with _LOCK:
            with open(_PATH, 'a', encoding='utf-8') as f:
                f.write(f"{ts} {msg}\n")
                f.flush()
    except Exception:
        pass


def get_log_path() -> Path | None:
    return _PATH


def _pid() -> int:
    import os
    return os.getpid()


def _platform() -> str:
    import sys
    return sys.platform
