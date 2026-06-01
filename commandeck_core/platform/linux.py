import functools
import hashlib
import os
import platform
import shlex
import shutil
import subprocess
import uuid as uuid_module
from pathlib import Path

from .base import PlatformAdapter
from commandeck_core.utils.sandbox import (
    host_argv, host_shell_argv, host_which, is_flatpak,
)

_TERM_COLS = 80
_TERM_ROWS = 24
_TERM_GEO = f"{_TERM_COLS}x{_TERM_ROWS}"

_TERMINAL_CANDIDATES = [
    ["xterm", "-fa", "Monospace", "-fs", "13", "-geometry", _TERM_GEO, "-e"],
    ["gnome-terminal", f"--geometry={_TERM_GEO}", "--"],
    ["konsole", "-e"],
    ["xfce4-terminal", f"--geometry={_TERM_GEO}", "-e"],
    ["mate-terminal", f"--geometry={_TERM_GEO}", "-e"],
    ["tilix", "-e"],
    ["terminator", f"--geometry={_TERM_GEO}", "-e"],
    ["alacritty", "-e"],
    ["kitty"],
]


@functools.cache
def _detect_terminal() -> list[str] | None:
    for cmd in _TERMINAL_CANDIDATES:
        if host_which(cmd[0]):
            return cmd
    return None


class LinuxAdapter(PlatformAdapter):
    def config_dir(self) -> Path:
        d = Path.home() / ".config" / "commandeck"
        d.mkdir(parents=True, exist_ok=True)
        self._migrate_legacy_config(d, Path.home() / ".config" / "remotex")
        return d

    def machine_id(self) -> str:
        try:
            mid = Path("/etc/machine-id").read_text().strip()
            if mid:
                return hashlib.sha256(mid.encode()).hexdigest()[:32]
        except OSError:
            pass
        parts = [platform.node(), str(uuid_module.getnode()), platform.machine()]
        return hashlib.sha256("|".join(parts).encode()).hexdigest()[:32]

    def open_browser(self, url: str) -> None:
        if not url:
            return
        candidates = []
        env_browser = os.environ.get("BROWSER", "").strip()
        if env_browser:
            candidates.append(env_browser)
        candidates += [
            "x-www-browser", "firefox", "chromium", "chromium-browser",
            "google-chrome", "brave-browser", "epiphany",
        ]
        for cmd in candidates:
            if not cmd or shutil.which(cmd) is None:
                continue
            try:
                subprocess.Popen(
                    [cmd, url],
                    start_new_session=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return
            except OSError:
                continue
        # No usable browser command found — silent no-op (the candidate list above
        # is comprehensive). The old GTK Gio last-resort was retired with GTK.

    def open_in_terminal(self, shell_command: str) -> bool:
        terminal = _detect_terminal()
        if terminal is None:
            return False
        try:
            bash_cmd = f'{shell_command}; echo; read -p "Press Enter to close..."'
            subprocess.Popen(
                host_argv(terminal + ["bash", "-c", bash_cmd]),
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except Exception:
            return False

    @staticmethod
    def _autostart_file() -> Path:
        return Path.home() / ".config" / "autostart" / "commandeck.desktop"

    def set_autostart(self, enabled: bool, exec_line: str | None = None) -> None:
        path = self._autostart_file()
        if not enabled:
            path.unlink(missing_ok=True)
            return
        if exec_line is None:
            exec_line = self._autostart_exec_line()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Commandeck\n"
            f"Exec={exec_line}\n"
            "Hidden=false\n"
            "NoDisplay=false\n"
            "X-GNOME-Autostart-enabled=true\n"
        )

    def is_autostart_enabled(self) -> bool:
        return self._autostart_file().exists()

    def is_sandboxed(self) -> bool:
        return is_flatpak()

    def supports_always_on_top(self) -> tuple[bool, str]:
        # The Qt window applies always-on-top itself via WindowStaysOnTopHint
        # (→ _NET_WM_STATE_ABOVE), which X11 window managers honor — no wmctrl needed
        # (that was a GTK-era requirement). Wayland compositors (GNOME/Mutter and most
        # others) forbid apps from forcing stay-on-top, so disable it there with a reason.
        if os.environ.get("XDG_SESSION_TYPE", "").lower() == "wayland" \
                or os.environ.get("WAYLAND_DISPLAY"):
            return False, ("Your desktop session (Wayland) does not let applications "
                           "force always-on-top. Use the window's title-bar menu "
                           "(right-click) → 'Always on Top', or use an X11 session.")
        return True, ""

    def apply_always_on_top(self, native_window: object) -> None:
        # No-op: the Qt window applies always-on-top itself via setWindowFlags
        # (Qt.WindowStaysOnTopHint). Retained for the PlatformAdapter interface;
        # the old GTK GdkX11/wmctrl path was retired with GTK.
        return

    def migrate_autostart_if_stale(self) -> None:
        path = self._autostart_file()
        if not path.exists():
            return
        try:
            current = path.read_text()
        except Exception:
            return
        expected_exec = f"Exec={self._autostart_exec_line()}"
        if expected_exec in current:
            return
        try:
            self.set_autostart(True)
        except Exception:
            pass

    def _autostart_exec_line(self) -> str:
        import sys
        if is_flatpak():
            return "flatpak run io.github.neurocontrarian.commandeck"
        exe = sys.argv[0] if sys.argv else ""
        if exe == "-c" or not Path(exe).exists():
            run_dev = Path(__file__).resolve().parent.parent.parent / "run_dev.sh"
            return shlex.quote(str(run_dev))
        if exe.endswith(".py"):
            return f"{shlex.quote(sys.executable)} {shlex.quote(exe)}"
        return shlex.quote(exe)
