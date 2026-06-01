from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

from .base import PlatformAdapter

_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_RUN_VALUE = "Commandeck"


class WindowsAdapter(PlatformAdapter):
    def config_dir(self) -> Path:
        appdata = os.environ.get("APPDATA")
        base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        d = base / "Commandeck"
        d.mkdir(parents=True, exist_ok=True)
        self._migrate_legacy_config(d, base / "RemoteX")
        return d

    def machine_id(self) -> str:
        import winreg
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Cryptography",
                0,
                winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
            ) as k:
                guid, _ = winreg.QueryValueEx(k, "MachineGuid")
            return hashlib.sha256(guid.encode("utf-8")).hexdigest()[:32]
        except OSError:
            import platform, uuid
            fallback = f"{platform.node()}-{uuid.getnode()}"
            return hashlib.sha256(fallback.encode("utf-8")).hexdigest()[:32]

    def open_browser(self, url: str) -> None:
        webbrowser.open(url)

    def open_in_terminal(self, shell_command: str) -> bool:
        # Run the command in PowerShell (Commandeck's local shell, so button
        # commands written in PowerShell syntax work) and keep the window open
        # afterwards (-NoExit) so the user can read the output.
        ps_args = ["powershell.exe", "-NoProfile", "-NoExit", "-Command", shell_command]
        wt = shutil.which("wt.exe")
        try:
            if wt:
                # Windows Terminal opens its own window; no console flag needed.
                subprocess.Popen([wt] + ps_args)
            else:
                # GUI app has no console — force a fresh console window.
                subprocess.Popen(
                    ps_args,
                    creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
                )
            return True
        except OSError:
            return False

    def set_autostart(self, enabled: bool, exec_line: str | None = None) -> None:
        import winreg
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE
        ) as k:
            if enabled:
                cmd = exec_line or f'"{sys.executable}"'
                winreg.SetValueEx(k, _RUN_VALUE, 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(k, _RUN_VALUE)
                except FileNotFoundError:
                    pass

    def is_autostart_enabled(self) -> bool:
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as k:
                winreg.QueryValueEx(k, _RUN_VALUE)
            return True
        except FileNotFoundError:
            return False

    def is_sandboxed(self) -> bool:
        return False
