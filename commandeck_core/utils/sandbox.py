"""Flatpak sandbox detection and host-side command helpers.

Inside a Flatpak sandbox, `subprocess.run("ls", shell=True)` runs `ls` from the
sandbox runtime — not the user's host. Most Commandeck commands (system update,
git status, etc.) are useless in that context.

`flatpak-spawn --host` runs commands on the host shell from within the sandbox.
This module detects whether we're sandboxed and wraps commands accordingly.
"""

import functools
import shutil
import subprocess
import sys
from pathlib import Path

# Sandbox state is immutable for the process — read once at import time.
_IS_FLATPAK = Path("/.flatpak-info").exists()


def is_flatpak() -> bool:
    return _IS_FLATPAK


@functools.lru_cache(maxsize=1)
def is_wine() -> bool:
    """Detect Wine reliably via ntdll.wine_get_version export.

    Wine's ntdll always exports `wine_get_version` (and `wine_get_host_version`).
    Real Windows never exports these symbols. This is 100% reliable across
    Wine 5/6/7/8/9, Winboat, Proton, and any wineprefix configuration —
    independent of registry keys or environment variables which are often
    missing or stale (especially under Winboat-launched processes).
    """
    if not sys.platform.startswith("win"):
        return False
    # Lazy import to avoid a hard dep + circular ref at import time.
    try:
        from commandeck_core.utils.exec_log import log as _l
    except Exception:
        _l = lambda _m: None  # noqa: E731
    try:
        import ctypes
        ntdll = ctypes.WinDLL("ntdll")
        _l("is_wine: ntdll loaded")
        ver_fn = getattr(ntdll, "wine_get_version")
        _l(f"is_wine: wine_get_version symbol found ({ver_fn!r}) -> True")
        return True
    except OSError as e:
        _l(f"is_wine: WinDLL('ntdll') OSError: {e} -> False")
        return False
    except AttributeError as e:
        _l(f"is_wine: wine_get_version AttributeError: {e} -> False (likely real Windows)")
        return False


def host_shell_argv(shell_command: str) -> list[str]:
    """argv list that runs a shell command on the user's host shell.

    Inside Flatpak: flatpak-spawn --host bash -c '<cmd>' — escapes the sandbox.
    Windows:        powershell -NoProfile -Command '<cmd>' (modern default shell).
    Linux/macOS:    bash -c '<cmd>'.
    """
    if _IS_FLATPAK:
        return ["flatpak-spawn", "--host", "bash", "-c", shell_command]
    if sys.platform.startswith("win"):
        return ["powershell", "-NoProfile", "-Command", shell_command]
    return ["bash", "-c", shell_command]


def host_argv(argv: list[str]) -> list[str]:
    """Wrap a literal argv list so it runs on the host inside Flatpak."""
    if _IS_FLATPAK:
        return ["flatpak-spawn", "--host", *argv]
    return list(argv)


@functools.lru_cache(maxsize=None)
def host_which(binary: str) -> bool:
    """True if `binary` is available on the host (sandbox-aware, cached)."""
    if not _IS_FLATPAK:
        return shutil.which(binary) is not None
    try:
        result = subprocess.run(
            ["flatpak-spawn", "--host", "which", binary],
            capture_output=True, timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False
