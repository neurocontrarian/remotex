"""QSettings facade — same keys and defaults as the GSettings gschema."""
from PySide6.QtCore import QSettings

_DEFAULTS: dict = {
    'window-width':          900,
    'window-height':         600,
    'window-maximized':      False,
    'command-timeout':       30,
    'confirm-before-run':    True,
    'button-size':           'medium',
    'always-on-top':         False,
    'hidden-categories':     [],
    'language':              'system',
    'button-theme':          'bold',
    'color-scheme':          'system',
    'mcp-execution-enabled': False,
    'icon-search-paths':     [],
    'legal-disclaimer-accepted': False,
}


class Settings:
    def __init__(self):
        self._qs = QSettings()

    def get_int(self, key: str) -> int:
        return int(self._qs.value(key, _DEFAULTS[key]))

    def get_bool(self, key: str) -> bool:
        v = self._qs.value(key, _DEFAULTS[key])
        if isinstance(v, str):
            return v.lower() == 'true'
        return bool(v)

    def get_str(self, key: str) -> str:
        return str(self._qs.value(key, _DEFAULTS[key]))

    def get_strv(self, key: str) -> list[str]:
        v = self._qs.value(key, _DEFAULTS[key])
        if isinstance(v, list):
            return v
        if isinstance(v, str) and v:
            return [v]
        return []

    def set_int(self, key: str, val: int) -> None:
        self._qs.setValue(key, val)

    def set_bool(self, key: str, val: bool) -> None:
        self._qs.setValue(key, val)

    def set_str(self, key: str, val: str) -> None:
        self._qs.setValue(key, val)

    def set_strv(self, key: str, val: list[str]) -> None:
        self._qs.setValue(key, val)

    def get_timeout(self) -> int:
        return self.get_int('command-timeout')

    # GSettings-compatible aliases — used by ConfigManager.export_backup/import_backup
    def get_boolean(self, key: str) -> bool:
        return self.get_bool(key)

    def get_string(self, key: str) -> str:
        return self.get_str(key)

    def set_boolean(self, key: str, val: bool) -> None:
        self.set_bool(key, val)

    def set_string(self, key: str, val: str) -> None:
        self.set_str(key, val)
