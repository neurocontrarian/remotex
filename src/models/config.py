import json
import os
import tomllib
import tomli_w
import zipfile
from pathlib import Path

from .command_button import CommandButton
from ._default_buttons import get_default_buttons

CONFIG_VERSION = 1


class ConfigManager:
    CONFIG_DIR = Path.home() / '.config' / 'remotex'
    MACHINES_FILE = CONFIG_DIR / 'machines.toml'
    BUTTONS_FILE = CONFIG_DIR / 'buttons.toml'
    PROFILES_FILE = CONFIG_DIR / 'profiles.toml'

    def __init__(self):
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        for f in (self.MACHINES_FILE, self.BUTTONS_FILE, self.PROFILES_FILE):
            if f.exists():
                try:
                    os.chmod(f, 0o600)
                except OSError:
                    pass

    # --- Machines ---

    def load_machines(self) -> list:
        try:
            from pro.models.machine import Machine
        except ImportError:
            return []
        if not self.MACHINES_FILE.exists():
            return []
        with open(self.MACHINES_FILE, 'rb') as f:
            data = tomllib.load(f)
        self._migrate_if_needed(data, self.MACHINES_FILE)
        return [Machine.from_dict(m) for m in data.get('machine', [])]

    def save_machines(self, machines: list) -> None:
        data = {
            'version': CONFIG_VERSION,
            'machine': [m.to_dict() for m in machines],
        }
        self._atomic_write(self.MACHINES_FILE, data)

    def add_machine(self, machine) -> None:
        machines = self.load_machines()
        machines.append(machine)
        self.save_machines(machines)

    def update_machine(self, machine) -> None:
        machines = self.load_machines()
        machines = [m if m.id != machine.id else machine for m in machines]
        self.save_machines(machines)

    def delete_machine(self, machine_id: str) -> None:
        machines = self.load_machines()
        self.save_machines([m for m in machines if m.id != machine_id])

    # --- Profiles ---

    def load_profiles(self) -> list:
        try:
            from pro.models.execution_profile import ExecutionProfile
        except ImportError:
            return []
        if not self.PROFILES_FILE.exists():
            return []
        with open(self.PROFILES_FILE, 'rb') as f:
            data = tomllib.load(f)
        return [ExecutionProfile.from_dict(p) for p in data.get('profile', [])]

    def save_profiles(self, profiles: list) -> None:
        data = {
            'version': CONFIG_VERSION,
            'profile': [p.to_dict() for p in profiles],
        }
        self._atomic_write(self.PROFILES_FILE, data)

    def add_profile(self, profile) -> None:
        profiles = self.load_profiles()
        profiles.append(profile)
        self.save_profiles(profiles)

    def update_profile(self, profile) -> None:
        profiles = self.load_profiles()
        profiles = [p if p.id != profile.id else profile for p in profiles]
        self.save_profiles(profiles)

    def delete_profile(self, profile_id: str) -> None:
        profiles = self.load_profiles()
        self.save_profiles([p for p in profiles if p.id != profile_id])

    def get_profile_by_id(self, profile_id: str):
        return next((p for p in self.load_profiles() if p.id == profile_id), None)

    # --- Buttons ---

    def load_buttons(self) -> list[CommandButton]:
        if not self.BUTTONS_FILE.exists():
            defaults = get_default_buttons()
            self.save_buttons(defaults)
            return defaults
        with open(self.BUTTONS_FILE, 'rb') as f:
            data = tomllib.load(f)
        self._migrate_if_needed(data, self.BUTTONS_FILE)
        buttons = [CommandButton.from_dict(b) for b in data.get('button', [])]
        if not buttons:
            defaults = get_default_buttons()
            self.save_buttons(defaults)
            return defaults
        if not any(b.is_default for b in buttons):
            self._migrate_mark_defaults(buttons)
        return sorted(buttons, key=lambda b: b.position)

    def save_buttons(self, buttons: list[CommandButton]) -> None:
        buttons = sorted(buttons, key=lambda b: b.position)
        for i, btn in enumerate(buttons):
            btn.position = i
        data = {
            'version': CONFIG_VERSION,
            'button': [b.to_dict() for b in buttons],
        }
        self._atomic_write(self.BUTTONS_FILE, data)

    def add_button(self, button: CommandButton) -> None:
        buttons = self.load_buttons()
        button.position = len(buttons)
        buttons.append(button)
        self.save_buttons(buttons)

    def update_button(self, button: CommandButton) -> None:
        buttons = self.load_buttons()
        buttons = [b if b.id != button.id else button for b in buttons]
        self.save_buttons(buttons)

    def delete_button(self, button_id: str) -> None:
        buttons = self.load_buttons()
        self.save_buttons([b for b in buttons if b.id != button_id])

    def count_custom_buttons(self) -> int:
        """Return the number of user-created (non-default) buttons."""
        return sum(1 for b in self.load_buttons() if not b.is_default)

    def count_machines(self) -> int:
        """Return the number of configured SSH machines."""
        return len(self.load_machines())

    # --- Internals ---

    def _atomic_write(self, path: Path, data: dict) -> None:
        """Write data atomically: write to .tmp, backup existing to .bak, then rename."""
        tmp = path.with_suffix('.toml.tmp')
        bak = path.with_suffix('.toml.bak')
        with open(tmp, 'wb') as f:
            tomli_w.dump(data, f)
        os.chmod(tmp, 0o600)
        if path.exists():
            path.replace(bak)
        tmp.replace(path)

    @staticmethod
    def _safe_extract(zf: zipfile.ZipFile, name: str, dest: Path) -> None:
        """Extract a single archive entry, rejecting path traversal attempts."""
        if name != Path(name).name or name in ('', '.', '..'):
            raise ValueError(f"Unsafe entry name in archive: {name!r}")
        zf.extract(name, dest)

    def _migrate_mark_defaults(self, buttons: list) -> None:
        """Mark buttons that match the default set — handles configs created before is_default existed."""
        default_keys = {(b.name, b.command) for b in get_default_buttons()}
        for btn in buttons:
            if (btn.name, btn.command) in default_keys:
                btn.is_default = True
        self.save_buttons(buttons)

    # --- Backup / Restore ---

    _GSETTINGS_KEYS = {
        'window-width':       'i',
        'window-height':      'i',
        'window-maximized':   'b',
        'command-timeout':    'i',
        'confirm-before-run': 'b',
        'grid-columns':       'i',
        'button-size':        's',
        'always-on-top':      'b',
        'hidden-categories':  'as',
        'icon-search-paths':  'as',
    }

    def export_backup(self, dest_path: Path, settings=None) -> None:
        """Write a .remotex-backup zip archive (buttons + settings, no machines)."""
        with zipfile.ZipFile(dest_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            if self.BUTTONS_FILE.exists():
                zf.write(self.BUTTONS_FILE, self.BUTTONS_FILE.name)
            if settings:
                gs = {}
                for key, typ in self._GSETTINGS_KEYS.items():
                    if typ == 'i':
                        gs[key] = settings.get_int(key)
                    elif typ == 'b':
                        gs[key] = settings.get_boolean(key)
                    elif typ == 's':
                        gs[key] = settings.get_string(key)
                    elif typ == 'as':
                        gs[key] = list(settings.get_strv(key))
                zf.writestr('gsettings.json', json.dumps(gs, indent=2))

    def export_machines_backup(self, dest_path: Path) -> None:
        """Write a .remotex-machines zip archive (machines.toml only)."""
        with zipfile.ZipFile(dest_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            if self.MACHINES_FILE.exists():
                zf.write(self.MACHINES_FILE, self.MACHINES_FILE.name)

    def import_machines_backup(self, src_path: Path) -> None:
        """Restore machines from a .remotex-machines zip archive."""
        with zipfile.ZipFile(src_path, 'r') as zf:
            if 'machines.toml' in zf.namelist():
                self._safe_extract(zf, 'machines.toml', self.CONFIG_DIR)

    def export_profiles_backup(self, dest_path: Path) -> None:
        """Write a .rxprofiles zip archive (profiles.toml only)."""
        with zipfile.ZipFile(dest_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            if self.PROFILES_FILE.exists():
                zf.write(self.PROFILES_FILE, self.PROFILES_FILE.name)

    def import_profiles_backup(self, src_path: Path) -> None:
        """Restore profiles from a .rxprofiles zip archive."""
        with zipfile.ZipFile(src_path, 'r') as zf:
            if 'profiles.toml' in zf.namelist():
                self._safe_extract(zf, 'profiles.toml', self.CONFIG_DIR)

    def import_backup(self, src_path: Path, settings=None) -> None:
        """Restore config from a .remotex-backup zip archive.

        After restoring buttons.toml, any default buttons not present in the
        backup are appended so that newly added defaults are never lost on import.
        """
        try:
            from pro.license import _LICENSE_FILE
        except ImportError:
            _LICENSE_FILE = None
        with zipfile.ZipFile(src_path, 'r') as zf:
            names = zf.namelist()
            if 'buttons.toml' in names:
                self._safe_extract(zf, 'buttons.toml', self.CONFIG_DIR)
                self._merge_missing_defaults()
            if 'machines.toml' in names:
                self._safe_extract(zf, 'machines.toml', self.CONFIG_DIR)
            if 'license.key' in names and _LICENSE_FILE is not None:
                _LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)
                self._safe_extract(zf, 'license.key', _LICENSE_FILE.parent)
            if 'gsettings.json' in names and settings:
                gs = json.loads(zf.read('gsettings.json'))
                for key, typ in self._GSETTINGS_KEYS.items():
                    if key not in gs:
                        continue
                    if typ == 'i':
                        settings.set_int(key, gs[key])
                    elif typ == 'b':
                        settings.set_boolean(key, gs[key])
                    elif typ == 's':
                        settings.set_string(key, gs[key])
                    elif typ == 'as':
                        settings.set_strv(key, gs[key])

    def _merge_missing_defaults(self) -> None:
        """Append any default buttons absent from the current buttons.toml.

        A default button is considered absent if no existing button shares the
        same command string.  This preserves intentional user deletions while
        ensuring newly added defaults (added after the backup was made) appear.
        """
        existing = self.load_buttons()
        existing_commands = {b.command for b in existing}
        missing = [
            btn for btn in get_default_buttons()
            if btn.command not in existing_commands
        ]
        if not missing:
            return
        # Append after the last existing position
        next_pos = max((b.position for b in existing), default=-1) + 1
        for i, btn in enumerate(missing):
            btn.position = next_pos + i
        self.save_buttons(existing + missing)

    def _migrate_if_needed(self, data: dict, path: Path) -> None:
        """Apply schema migrations for older config versions."""
        version = data.get('version', 1)
        if version < CONFIG_VERSION:
            pass  # future migrations go here
