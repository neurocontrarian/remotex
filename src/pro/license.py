"""Pro license management — LemonSqueezy API with local JSON cache."""

import hashlib
import json
import os
import platform
import uuid as uuid_module
from datetime import date
from pathlib import Path

_CONFIG_DIR   = Path.home() / '.config' / 'remotex'
_LICENSE_FILE = _CONFIG_DIR / 'license.key'

FREE_BUTTON_LIMIT = 3
FREE_MACHINE_LIMIT = 0

PRO_INFO_URL    = "https://github.com/flelard/remotex#remotex-pro"
PRO_BUY_URL     = "https://neurocontrarian.lemonsqueezy.com/checkout/buy/f2b9451a-588d-49c2-b1ed-1afe21ffd9e2"
SUPPORT_EMAIL   = "support@neurocontrarian.com"

_GRACE_DAYS       = 3    # Extra days after yearly expiry before access is cut
_WARN_DAYS        = 30   # Days before yearly expiry to show a warning toast
_REVALIDATE_HOURS = 24   # Re-check with LemonSqueezy every N hours

_LS_API = "https://api.lemonsqueezy.com/v1/licenses"


# ── Machine fingerprint ───────────────────────────────────────────────────────

def get_machine_id() -> str:
    """Return a stable, anonymous identifier for this machine.

    Uses /etc/machine-id (set at OS install, survives reboots and hostname
    changes) with a fallback to hostname + MAC address.
    """
    try:
        mid = Path('/etc/machine-id').read_text().strip()
        if mid:
            return hashlib.sha256(mid.encode()).hexdigest()[:32]
    except OSError:
        pass
    parts = [platform.node(), str(uuid_module.getnode()), platform.machine()]
    return hashlib.sha256('|'.join(parts).encode()).hexdigest()[:32]


# ── HTTP helper (no extra deps — stdlib only) ─────────────────────────────────

def _post(endpoint: str, payload: dict, timeout: int = 10) -> dict:
    """POST form-encoded data to a LemonSqueezy endpoint. Returns parsed JSON."""
    import urllib.request
    import urllib.parse
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(
        f"{_LS_API}/{endpoint}",
        data=data,
        method='POST',
        headers={'Accept': 'application/json'},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


# ── Local file I/O ────────────────────────────────────────────────────────────

def _read_raw() -> dict | None:
    """Return the parsed license dict, migrating old plain-text format if needed."""
    if not _LICENSE_FILE.exists():
        return None
    raw = _LICENSE_FILE.read_text().strip()
    if not raw:
        return None
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and 'key' in data:
            return data
    except json.JSONDecodeError:
        # Legacy plain-text key → migrate to lifetime (pre-LemonSqueezy era)
        migrated = {
            'key': raw,
            'type': 'lifetime',
            'expires': None,
            'activated_at': None,
            'instance_id': None,
            'machine_id': None,
            'last_validated_at': None,
        }
        _write_raw(migrated)
        return migrated
    return None


def _write_raw(data: dict) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _LICENSE_FILE.write_text(json.dumps(data, indent=2))
    os.chmod(_LICENSE_FILE, 0o600)


# ── Expiry helpers ────────────────────────────────────────────────────────────

def _compute_days_until(expires_str: str | None) -> int | None:
    if not expires_str:
        return None
    try:
        return (date.fromisoformat(expires_str) - date.today()).days
    except (ValueError, TypeError):
        return None


def _is_expired(data: dict) -> bool:
    if data.get('type') != 'yearly':
        return False
    days = _compute_days_until(data.get('expires'))
    if days is None:
        return False
    return days < -_GRACE_DAYS


# ── LemonSqueezy response parsing ─────────────────────────────────────────────

def _parse_ls_response(result: dict) -> tuple[str, str | None]:
    """Return (license_type, expires_iso_or_None) from a LemonSqueezy response."""
    lk = result.get('license_key') or {}
    expires_at = lk.get('expires_at')  # ISO datetime string or null
    if expires_at:
        # yearly: extract the date part
        expires = expires_at[:10] if isinstance(expires_at, str) else None
        return 'yearly', expires
    return 'lifetime', None


# ── Public API ────────────────────────────────────────────────────────────────

def is_pro_active() -> bool:
    """Return True when a valid, non-expired license is stored locally."""
    data = _read_raw()
    if not data or not data.get('key'):
        return False
    return not _is_expired(data)


def get_license_key() -> str:
    data = _read_raw()
    return data.get('key', '') if data else ''


def get_license_info() -> dict:
    """Return a dict with full license details for UI display.

    Keys: active, key, type, expires, activated_at, is_expired,
          days_until_expiry, expiry_warning.
    """
    data = _read_raw()
    if not data:
        return {
            'active': False, 'key': '', 'type': '', 'expires': None,
            'activated_at': None, 'is_expired': False,
            'days_until_expiry': None, 'expiry_warning': False,
            'activation_limit': None, 'activation_usage': None,
        }
    expired = _is_expired(data)
    days = _compute_days_until(data.get('expires')) if data.get('type') == 'yearly' else None
    return {
        'active': not expired and bool(data.get('key')),
        'key': data.get('key', ''),
        'type': data.get('type', 'lifetime'),
        'expires': data.get('expires'),
        'activated_at': data.get('activated_at'),
        'is_expired': expired,
        'days_until_expiry': days,
        'expiry_warning': days is not None and 0 <= days <= _WARN_DAYS,
        'activation_limit': data.get('activation_limit'),
        'activation_usage': data.get('activation_usage'),
    }


def validate_license_online(key: str, email: str = '') -> tuple[bool, str, str | None]:
    """Activate a license key against LemonSqueezy and save locally if valid.

    Returns (valid, license_type_or_error_code, expires_iso_or_None).
    Error codes: 'network_error', 'email_mismatch', 'limit_reached'
    """
    key = key.strip()
    if len(key) < 8:
        return False, '', None

    import urllib.error
    machine_id = get_machine_id()
    try:
        result = _post('activate', {
            'license_key': key,
            'instance_name': machine_id,
        })
    except urllib.error.HTTPError as e:
        if e.code == 422:
            return False, 'limit_reached', None
        return False, '', None
    except Exception:
        return False, 'network_error', None

    if not result.get('activated'):
        return False, '', None

    # App-side email validation: compare user input vs purchase email
    if email:
        customer_email = (result.get('meta') or {}).get('customer_email', '')
        if customer_email and email.strip().lower() != customer_email.lower():
            instance_id = (result.get('instance') or {}).get('id')
            if instance_id:
                try:
                    _post('deactivate', {'license_key': key, 'instance_id': instance_id})
                except Exception:
                    pass
            return False, 'email_mismatch', None

    license_type, expires = _parse_ls_response(result)
    instance_id = (result.get('instance') or {}).get('id')
    lk = result.get('license_key') or {}

    _write_raw({
        'key': key,
        'type': license_type,
        'expires': expires,
        'activated_at': date.today().isoformat(),
        'instance_id': instance_id,
        'machine_id': machine_id,
        'last_validated_at': date.today().isoformat(),
        'activation_limit': lk.get('activation_limit'),
        'activation_usage': lk.get('activation_usage'),
    })
    return True, license_type, expires


def revalidate_license() -> bool:
    """Re-check the stored license with LemonSqueezy. Call on startup (background thread).

    - Skipped if validated less than _REVALIDATE_HOURS ago.
    - On network error: tolerates failure, keeps license valid.
    - If LemonSqueezy returns invalid: removes the license file.
    Returns True if the license remains valid after the check.
    """
    data = _read_raw()
    if not data or not data.get('key'):
        return False

    # Skip if recently validated
    last = data.get('last_validated_at')
    if last:
        try:
            delta = (date.today() - date.fromisoformat(last)).days * 24
            if delta < _REVALIDATE_HOURS:
                return not _is_expired(data)
        except (ValueError, TypeError):
            pass

    instance_id = data.get('instance_id')
    if not instance_id:
        # Legacy activation without instance_id — keep valid, skip remote check
        return not _is_expired(data)

    try:
        result = _post('validate', {
            'license_key': data['key'],
            'instance_id': instance_id,
        })
    except Exception:
        # Network error — tolerate, do not revoke
        return not _is_expired(data)

    if result.get('valid'):
        data['last_validated_at'] = date.today().isoformat()
        license_type, expires = _parse_ls_response(result)
        data['type'] = license_type
        data['expires'] = expires
        lk = result.get('license_key') or {}
        if lk.get('activation_limit') is not None:
            data['activation_limit'] = lk['activation_limit']
            data['activation_usage'] = lk.get('activation_usage')
        _write_raw(data)
        return True

    # LemonSqueezy says the license is no longer valid (revoked, refunded…)
    _LICENSE_FILE.unlink(missing_ok=True)
    return False


def clear_license_key() -> None:
    """Deactivate the license on LemonSqueezy and remove it locally."""
    data = _read_raw()
    if data and data.get('key') and data.get('instance_id'):
        try:
            _post('deactivate', {
                'license_key': data['key'],
                'instance_id': data['instance_id'],
            })
        except Exception:
            pass  # Best-effort: remove locally even if the API call fails
    if _LICENSE_FILE.exists():
        _LICENSE_FILE.unlink()
