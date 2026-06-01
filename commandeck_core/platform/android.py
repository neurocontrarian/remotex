"""Android PlatformAdapter (Phase 25, M1).

Stays PURE PYTHON, like the other adapters — the only OS-specific values
(the app-private files dir, the ANDROID_ID, a browser-open callback) are read
natively by the Toga app at startup and injected via `set_android_context()`.
This keeps commandeck_core free of any UI/JNI import, per the strict core rule.

Path/identifier contract: dev/SHARED_FORMATS.md §1 (config files live directly in
the app-private `files/` dir) and §6 (machine_id = sha256(ANDROID_ID)[:32]).
"""
import hashlib
import uuid as uuid_module
from pathlib import Path
from typing import Callable

from .base import PlatformAdapter

# Injected by the Toga app at startup (commandeck_mobile/app.py). None until then.
_files_dir: Path | None = None
_android_id: str = ""
_browser_open: Callable[[str], None] | None = None


def set_android_context(files_dir, android_id: str = "",
                        browser_open: Callable[[str], None] | None = None) -> None:
    """Inject the native Android values the adapter needs. Called once, early,
    by the Toga app before any ConfigManager / license use."""
    global _files_dir, _android_id, _browser_open
    _files_dir = Path(files_dir)
    _android_id = android_id or ""
    if browser_open is not None:
        _browser_open = browser_open


class AndroidAdapter(PlatformAdapter):
    def config_dir(self) -> Path:
        # SHARED_FORMATS §1: Android config lives in the app-private files/ dir.
        # Fallback keeps the adapter usable in desktop tests / `briefcase dev`
        # where no native context was injected.
        d = _files_dir if _files_dir is not None else (Path.home() / ".commandeck-android")
        d.mkdir(parents=True, exist_ok=True)
        return d

    def machine_id(self) -> str:
        # SHARED_FORMATS §6: sha256(ANDROID_ID)[:32]. Only used by password_store
        # (XOR) on mobile — NOT for licensing (mobile billing is store-side).
        if _android_id:
            return hashlib.sha256(_android_id.encode()).hexdigest()[:32]
        # No ANDROID_ID available — persist a random id so it stays stable.
        marker = self.config_dir() / ".machine_id"
        try:
            existing = marker.read_text().strip()
            if existing:
                return existing
        except OSError:
            pass
        generated = hashlib.sha256(uuid_module.uuid4().hex.encode()).hexdigest()[:32]
        try:
            marker.write_text(generated)
        except OSError:
            pass
        return generated

    def open_browser(self, url: str) -> None:
        # Delegated to a native ACTION_VIEW intent injected by the app. Used only
        # for support/legal links — NEVER for purchases (store-compliance).
        if url and _browser_open is not None:
            _browser_open(url)

    def open_in_terminal(self, shell_command: str) -> bool:
        return False  # no host shell / terminal on Android

    def set_autostart(self, enabled: bool, exec_line: str | None = None) -> None:
        return  # not applicable on Android

    def is_autostart_enabled(self) -> bool:
        return False

    def is_sandboxed(self) -> bool:
        return True

    def supports_always_on_top(self) -> tuple[bool, str]:
        return False, "Not applicable on mobile."
