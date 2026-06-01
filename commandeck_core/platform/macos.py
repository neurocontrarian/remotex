import hashlib
import os
import platform
import plistlib
import shlex
import subprocess
import tempfile
import uuid as uuid_module
import webbrowser
from pathlib import Path

from .base import PlatformAdapter

_BUNDLE_ID = "io.github.neurocontrarian.commandeck"
_LAUNCH_AGENT = Path.home() / "Library" / "LaunchAgents" / f"{_BUNDLE_ID}.plist"


class MacAdapter(PlatformAdapter):
    def config_dir(self) -> Path:
        base = Path.home() / "Library" / "Application Support"
        d = base / "Commandeck"
        d.mkdir(parents=True, exist_ok=True)
        self._migrate_legacy_config(d, base / "RemoteX")
        return d

    def machine_id(self) -> str:
        try:
            out = subprocess.check_output(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                timeout=5, text=True,
            )
            for line in out.splitlines():
                if "IOPlatformUUID" in line:
                    uuid = line.split('"')[3]
                    return hashlib.sha256(uuid.encode()).hexdigest()[:32]
        except Exception:
            pass
        parts = [platform.node(), str(uuid_module.getnode())]
        return hashlib.sha256("|".join(parts).encode()).hexdigest()[:32]

    def open_browser(self, url: str) -> None:
        webbrowser.open(url)

    def open_in_terminal(self, shell_command: str) -> bool:
        fd, path = tempfile.mkstemp(prefix="commandeck-", suffix=".sh", dir="/tmp")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(
                    "#!/bin/bash\n"
                    + shell_command
                    + f'\n\necho\nread -n 1 -s -r -p "Press any key to close..."\nrm -f {shlex.quote(path)}\n'
                )
            os.chmod(path, 0o755)
            subprocess.Popen(["open", "-a", "Terminal", path])
            return True
        except Exception:
            try:
                os.unlink(path)
            except OSError:
                pass
            return False

    def set_autostart(self, enabled: bool, exec_line: str | None = None) -> None:
        if not enabled:
            if _LAUNCH_AGENT.exists():
                subprocess.run(["launchctl", "unload", str(_LAUNCH_AGENT)], check=False)
                _LAUNCH_AGENT.unlink()
            return
        if exec_line is None:
            exec_line = "/Applications/Commandeck.app/Contents/MacOS/Commandeck"
        plist = {
            "Label": _BUNDLE_ID,
            "ProgramArguments": [exec_line],
            "RunAtLoad": True,
            "KeepAlive": False,
        }
        _LAUNCH_AGENT.parent.mkdir(parents=True, exist_ok=True)
        with _LAUNCH_AGENT.open("wb") as f:
            plistlib.dump(plist, f)
        subprocess.run(["launchctl", "load", str(_LAUNCH_AGENT)], check=False)

    def is_autostart_enabled(self) -> bool:
        return _LAUNCH_AGENT.exists()

    def is_sandboxed(self) -> bool:
        return False

    # always-on-top: Qt.WindowStaysOnTopHint on QMainWindow handles it via NSWindow.level
    def supports_always_on_top(self) -> tuple[bool, str]:
        return True, ""

    def apply_always_on_top(self, native_window: object) -> None:
        # Qt sets WindowStaysOnTopHint on the QMainWindow directly — no OS call needed.
        pass
