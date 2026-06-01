import json
import os
import shutil
import tomllib
import tomli_w
import zipfile
from datetime import datetime
from pathlib import Path

from .command_button import CommandButton
from ._default_buttons import get_default_buttons

CONFIG_VERSION = 3


class ConfigManager:
    # Class-level defaults used when no config_dir is passed (Linux legacy path).
    CONFIG_DIR = Path.home() / '.config' / 'commandeck'
    MACHINES_FILE = CONFIG_DIR / 'machines.toml'
    BUTTONS_FILE = CONFIG_DIR / 'buttons.toml'
    PROFILES_FILE = CONFIG_DIR / 'profiles.toml'

    def __init__(self, config_dir: Path | None = None):
        if config_dir is None:
            from commandeck_core.platform import get_platform
            config_dir = get_platform().config_dir()
        self.CONFIG_DIR = config_dir
        self.MACHINES_FILE = config_dir / 'machines.toml'
        self.BUTTONS_FILE = config_dir / 'buttons.toml'
        self.PROFILES_FILE = config_dir / 'profiles.toml'
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
            from commandeck_core.pro.models.machine import Machine
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
            from commandeck_core.pro.models.execution_profile import ExecutionProfile
        except ImportError:
            return []
        if not self.PROFILES_FILE.exists():
            return []
        with open(self.PROFILES_FILE, 'rb') as f:
            data = tomllib.load(f)
        profiles = [ExecutionProfile.from_dict(p) for p in data.get('profile', [])]
        self._migrate_inline_secrets(profiles, self.save_profiles)
        return profiles

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
        self._migrate_inline_secrets(buttons, self.save_buttons)
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

    def reset_buttons_to_defaults(self) -> Path | None:
        """Replace buttons.toml with the seeded defaults.

        Backs up the current file to buttons.toml.backup-YYYYMMDD-HHMMSS.
        Returns the backup path, or None if no buttons.toml existed yet.
        """
        backup_path = None
        if self.BUTTONS_FILE.exists():
            ts = datetime.now().strftime('%Y%m%d-%H%M%S')
            backup_path = self.BUTTONS_FILE.with_name(f'buttons.toml.backup-{ts}')
            shutil.copy2(self.BUTTONS_FILE, backup_path)
            self.BUTTONS_FILE.unlink()
        # load_buttons() reseeds the defaults when the file is missing.
        self.load_buttons()
        return backup_path

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

    def _migrate_inline_secrets(self, items: list, save_fn) -> None:
        """One-time migration: move any legacy inline sudo password (XOR in TOML)
        into the OS keychain (secret_store), then strip it from the TOML.

        Keyed by presence, not version: once stripped there is nothing left to do,
        so it is idempotent. After this, no secret remains in any config file —
        which is what makes backups secret-free by construction.
        """
        from commandeck_core.services.password_store import decode
        from commandeck_core.services.secret_store import set_secret
        dirty = False
        for it in items:
            enc = getattr(it, 'sudo_password_encoded', '')
            if not enc:
                continue
            pwd = decode(enc)
            if pwd:
                set_secret(it._secret_id(), pwd)
                it.has_sudo_password = True
            it.sudo_password_encoded = ''
            dirty = True
        if dirty:
            save_fn(items)

    def _reconcile_secret_flags(self, items: list, flag_attr: str, save_fn) -> list:
        """Clear a 'has_<secret>' flag where the secret is not actually present.

        Shared by buttons/profiles (`has_sudo_password`) and machines
        (`has_password`). Used after importing a backup: the flag travels in the
        TOML but the secret never does (it stays in the source device's keychain).
        Returns the names of affected items so the UI can ask the user to re-enter.

        Guarded by store readability so a transiently-locked keychain cannot wrongly
        clear a flag whose secret really does exist on this machine (e.g. a
        same-machine restore, where the keychain still holds it).
        """
        from commandeck_core.services import secret_store
        if not (secret_store.keyring_available() or (self.CONFIG_DIR / ".secrets").exists()):
            return []
        cleared = []
        for it in items:
            if getattr(it, flag_attr) and not secret_store.get_secret(it._secret_id()):
                setattr(it, flag_attr, False)
                cleared.append(it.name)
        if cleared:
            save_fn(items)
        return cleared

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
        # 'grid-columns' was removed when the grid switched to reflow-by-width
        # (no "Buttons per row" option). Kept out of backups so export doesn't
        # query a key the Qt Settings facade no longer defines (KeyError).
        'button-size':        's',
        'always-on-top':      'b',
        'hidden-categories':  'as',
        'icon-search-paths':  'as',
    }

    def export_backup(self, dest_path: Path, settings=None) -> None:
        """Write a .commandeck-backup zip archive (buttons + settings, no machines)."""
        with zipfile.ZipFile(dest_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            if self.BUTTONS_FILE.exists():
                # Serialize from loaded models (to_dict has NO secret field) rather
                # than copying the raw file — guarantees the backup is secret-free.
                buttons = self.load_buttons()
                zf.writestr('buttons.toml', tomli_w.dumps(
                    {'version': CONFIG_VERSION, 'button': [b.to_dict() for b in buttons]}))
            if settings:
                gs = {}
                for key, typ in self._GSETTINGS_KEYS.items():
                    try:  # a single unknown/failed key must not abort the whole backup
                        if typ == 'i':
                            gs[key] = settings.get_int(key)
                        elif typ == 'b':
                            gs[key] = settings.get_boolean(key)
                        elif typ == 's':
                            gs[key] = settings.get_string(key)
                        elif typ == 'as':
                            gs[key] = list(settings.get_strv(key))
                    except Exception:
                        continue
                zf.writestr('gsettings.json', json.dumps(gs, indent=2))

    def export_machines_backup(self, dest_path: Path) -> None:
        """Write a .cdmachines zip archive (machines.toml only)."""
        with zipfile.ZipFile(dest_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            if self.MACHINES_FILE.exists():
                zf.write(self.MACHINES_FILE, self.MACHINES_FILE.name)

    def import_machines_backup(self, src_path: Path) -> dict:
        """Restore machines from a .cdmachines zip archive.

        Neither the SSH private key nor the SSH password travels in a backup (only
        a flag / a key *path*). Returns what needs the user's attention on this
        device: {'missing_keys': [...names], 'need_password': [...names]}."""
        with zipfile.ZipFile(src_path, 'r') as zf:
            if 'machines.toml' in zf.namelist():
                self._safe_extract(zf, 'machines.toml', self.CONFIG_DIR)
                need_password = self._reconcile_secret_flags(
                    self.load_machines(), 'has_password', self.save_machines)
                return {'missing_keys': self._machines_missing_keys(),
                        'need_password': need_password}
        return {'missing_keys': [], 'need_password': []}

    def _machines_missing_keys(self) -> list:
        """Names of machines whose identity_file is set but does not resolve here.

        A machine with an empty identity_file uses ssh-agent / default ~/.ssh keys,
        so it is not flagged (nothing to re-select)."""
        missing = []
        for m in self.load_machines():
            if m.identity_file and not Path(m.identity_file).expanduser().exists():
                missing.append(m.name)
        return missing

    def export_profiles_backup(self, dest_path: Path) -> None:
        """Write a .rxprofiles zip archive (profiles.toml only)."""
        with zipfile.ZipFile(dest_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            if self.PROFILES_FILE.exists():
                # Serialize from loaded models (no secret field) → secret-free backup.
                profiles = self.load_profiles()
                zf.writestr('profiles.toml', tomli_w.dumps(
                    {'version': CONFIG_VERSION, 'profile': [p.to_dict() for p in profiles]}))

    def import_profiles_backup(self, src_path: Path) -> list:
        """Restore profiles from a .rxprofiles zip archive.

        Returns names of profiles whose sudo password must be re-entered on this
        device (the secret does not travel in the backup)."""
        with zipfile.ZipFile(src_path, 'r') as zf:
            if 'profiles.toml' in zf.namelist():
                self._safe_extract(zf, 'profiles.toml', self.CONFIG_DIR)
                return self._reconcile_secret_flags(
                    self.load_profiles(), 'has_sudo_password', self.save_profiles)
        return []

    def import_backup(self, src_path: Path, settings=None) -> list:
        """Restore config from a .commandeck-backup zip archive.

        After restoring buttons.toml, any default buttons not present in the
        backup are appended so that newly added defaults are never lost on import.

        Returns names of buttons whose sudo password must be re-entered on this
        device (the secret stays in the source device's keychain, never in the
        backup).
        """
        try:
            from commandeck_core.pro.license import _LICENSE_FILE
        except ImportError:
            _LICENSE_FILE = None
        cleared: list = []
        with zipfile.ZipFile(src_path, 'r') as zf:
            names = zf.namelist()
            if 'buttons.toml' in names:
                self._safe_extract(zf, 'buttons.toml', self.CONFIG_DIR)
                self._merge_missing_defaults()
                cleared = self._reconcile_secret_flags(
                    self.load_buttons(), 'has_sudo_password', self.save_buttons)
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
                    try:  # tolerate an unknown key from an older/other backup
                        if typ == 'i':
                            settings.set_int(key, gs[key])
                        elif typ == 'b':
                            settings.set_boolean(key, gs[key])
                        elif typ == 's':
                            settings.set_string(key, gs[key])
                        elif typ == 'as':
                            settings.set_strv(key, gs[key])
                    except Exception:
                        continue
        return cleared

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
        version = data.get('version', 0)
        if version < 3 and 'button' in data:
            # v→3: restore per-button bg colors on default seeds (stripped by
            # the erroneous v2 migration) and clear only text_color="#000000"
            # which caused invisible labels on dark themes like neon.
            seed_colors = {
                (btn.name, btn.command): btn.color
                for btn in get_default_buttons()
            }
            for btn_dict in data['button']:
                if btn_dict.get('is_default', False):
                    key = (btn_dict.get('name', ''), btn_dict.get('command', ''))
                    if key in seed_colors:
                        btn_dict['color'] = seed_colors[key]
                    btn_dict['text_color'] = ''
            data['version'] = 3
            self._atomic_write(path, data)
