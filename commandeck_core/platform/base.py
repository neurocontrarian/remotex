import shutil
from abc import ABC, abstractmethod
from pathlib import Path


class PlatformAdapter(ABC):
    @abstractmethod
    def config_dir(self) -> Path: ...

    @staticmethod
    def _migrate_legacy_config(new_dir: Path, legacy_dir: Path) -> None:
        """One-time copy of an older RemoteX config dir into the new Commandeck dir.

        Only runs when the new dir has no config yet AND the legacy dir exists, so
        it never clobbers a real config and is safe to call on every config_dir()
        access. Covers the rename RemoteX → Commandeck (config_dir changed name)."""
        try:
            if legacy_dir == new_dir or not legacy_dir.is_dir():
                return
            if (new_dir / "buttons.toml").exists() or (new_dir / "machines.toml").exists():
                return  # already have config here
            for item in legacy_dir.iterdir():
                dest = new_dir / item.name
                if dest.exists():
                    continue
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
        except OSError:
            pass  # best-effort; a fresh config is created anyway

    @abstractmethod
    def machine_id(self) -> str:
        """Return a stable 32-hex anonymous device fingerprint."""
        ...

    @abstractmethod
    def open_browser(self, url: str) -> None: ...

    @abstractmethod
    def open_in_terminal(self, shell_command: str) -> bool:
        """Launch shell_command in a new terminal window. Returns True on success."""
        ...

    @abstractmethod
    def set_autostart(self, enabled: bool, exec_line: str | None = None) -> None: ...

    @abstractmethod
    def is_autostart_enabled(self) -> bool: ...

    @abstractmethod
    def is_sandboxed(self) -> bool: ...

    def supports_always_on_top(self) -> tuple[bool, str]:
        """Return (supported, reason_if_not). Default: supported."""
        return True, ""

    def apply_always_on_top(self, native_window: object) -> None:
        """Set always-on-top on the native window object. No-op by default."""

    def migrate_autostart_if_stale(self) -> None:
        """Rewrite autostart entry if its exec line drifted. No-op on most platforms."""
