"""Unified secret store — the single place secrets (sudo passwords, …) are kept.

Design rule (decided 2026-05-29): **config TOML files never contain a secret, and
no secret is ever included in a backup.** Models persist only a boolean flag
(has_sudo_password); the secret itself lives here, keyed by a namespaced id.

Two backends, tried in order:
  1. The OS keychain via `keyring` — macOS Keychain, Windows Credential Manager,
     Linux Secret Service (gnome-keyring / KWallet). Encrypted at rest, never on
     Commandeck's disk, never in a backup.
  2. Fallback (no working keychain — e.g. minimal/headless Linux): a dedicated
     local file `<config_dir>/.secrets`, XOR-obfuscated (machine-id key, like the
     old sudo encoding) and chmod 600. **This file is NEVER added to any export/
     backup** (see ConfigManager export_* — they only zip the named TOML files).
     Callers should WARN the user when the fallback is used (keyring_available()
     is False), since obfuscation is not real encryption.

The fallback keeps the feature working everywhere with zero secrets in backups,
honoring the rule by construction regardless of keychain availability.
"""
import json
import os

_SERVICE = "io.github.neurocontrarian.commandeck"
_PROBE_ID = "__commandeck_probe__"

_keyring_ok: bool | None = None
_backend_obj = None  # the keyring backend instance, or False if unavailable


def _backend():
    """Return the platform keyring backend INSTANCE, or False.

    We instantiate the backend explicitly instead of relying on
    keyring.get_keyring() / entry-point discovery, which is unreliable inside a
    PyInstaller-frozen app (the backend metadata is often missing, so keyring
    silently falls back to the null backend on every platform). Importing the
    backend module directly also lets PyInstaller bundle it by static analysis.
    """
    global _backend_obj
    if _backend_obj is not None:
        return _backend_obj
    import sys
    try:
        if sys.platform == "darwin":
            from keyring.backends import macOS
            _backend_obj = macOS.Keyring()
        elif sys.platform.startswith("win"):
            from keyring.backends import Windows
            _backend_obj = Windows.Keyring()
        else:
            from keyring.backends import SecretService
            _backend_obj = SecretService.Keyring()
    except Exception:
        _backend_obj = False  # no keyring lib / backend importable (e.g. Android)
    return _backend_obj


# ── keychain availability (probed once, cached) ───────────────────────────────

def keyring_available() -> bool:
    """True if a real OS keychain round-trips. Cached after first probe.

    Importing the backend is not enough: on Linux the Secret Service backend may
    be present but D-Bus unreachable at runtime, so we do an actual round-trip.
    """
    global _keyring_ok
    if _keyring_ok is None:
        _keyring_ok = _probe_keyring()
    return _keyring_ok


def _probe_keyring() -> bool:
    kr = _backend()
    if not kr:
        return False
    try:
        kr.set_password(_SERVICE, _PROBE_ID, "1")
        ok = kr.get_password(_SERVICE, _PROBE_ID) == "1"
        try:
            kr.delete_password(_SERVICE, _PROBE_ID)
        except Exception:
            pass
        return ok
    except Exception:
        return False


# ── public API ────────────────────────────────────────────────────────────────

def set_secret(secret_id: str, password: str) -> str:
    """Store a secret. Returns the backend used: 'keyring' or 'fallback'."""
    if keyring_available():
        try:
            _backend().set_password(_SERVICE, secret_id, password)
            _fallback_delete(secret_id)  # clear any stale fallback copy
            return "keyring"
        except Exception:
            pass
    _fallback_set(secret_id, password)
    return "fallback"


def get_secret(secret_id: str) -> str:
    """Return the stored secret, or '' if none."""
    if keyring_available():
        try:
            value = _backend().get_password(_SERVICE, secret_id)
            if value is not None:
                return value
        except Exception:
            pass
    return _fallback_get(secret_id)


def delete_secret(secret_id: str) -> None:
    if keyring_available():
        try:
            _backend().delete_password(_SERVICE, secret_id)
        except Exception:
            pass
    _fallback_delete(secret_id)


# ── local fallback file (.secrets — never exported) ───────────────────────────

def _fallback_path():
    from commandeck_core.platform import get_platform
    return get_platform().config_dir() / ".secrets"


def _fallback_load() -> dict:
    p = _fallback_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def _fallback_save(data: dict) -> None:
    p = _fallback_path()
    p.write_text(json.dumps(data))
    try:
        os.chmod(p, 0o600)
    except OSError:
        pass


def _fallback_set(secret_id: str, password: str) -> None:
    from commandeck_core.services.password_store import encode
    data = _fallback_load()
    data[secret_id] = encode(password)
    _fallback_save(data)


def _fallback_get(secret_id: str) -> str:
    from commandeck_core.services.password_store import decode
    enc = _fallback_load().get(secret_id, "")
    return decode(enc) if enc else ""


def _fallback_delete(secret_id: str) -> None:
    data = _fallback_load()
    if secret_id in data:
        del data[secret_id]
        _fallback_save(data)
