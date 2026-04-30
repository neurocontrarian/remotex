"""Feature gate — single import surface for Pro feature checks.

Every caller in the codebase must import license/Pro-related symbols from THIS
module, never directly from `src.pro.*`. This decouples free builds (where
`src/pro/` is excluded from the artifact) from Pro builds (where it is shipped).

Behavior:
- Pro build: re-exports the real implementations from `src.pro.license`.
- Free build: `src.pro` is absent → fall back to stubs that report no Pro access.

Adding a new Pro symbol:
1. Add it to `src/pro/license.py` (or another `src.pro.*` module) and to
   `src/pro/__init__.py`'s public API.
2. Add the import + a free-mode stub here, keeping the same signature.
3. Add it to `__all__` below.
"""

try:
    from pro.license import (
        is_pro_active,
        get_license_key,
        get_license_info,
        get_trial_info,
        clear_license_key,
        validate_license_online,
        revalidate_license,
        get_machine_id,
        FREE_BUTTON_LIMIT,
        FREE_MACHINE_LIMIT,
        TRIAL_DAYS,
        PRO_INFO_URL,
        PRO_BUY_URL,
        SUPPORT_EMAIL,
    )
    PRO_AVAILABLE = True

except ImportError:
    # Free build — `src/pro/` is excluded from the artifact. Provide stubs that
    # match the Pro module's public signatures so callers compile and behave
    # as if no license exists.
    import hashlib
    import platform
    import uuid as uuid_module
    from pathlib import Path

    PRO_AVAILABLE = False

    FREE_BUTTON_LIMIT  = 3
    FREE_MACHINE_LIMIT = 0
    TRIAL_DAYS         = 14

    PRO_INFO_URL  = "https://github.com/neurocontrarian/remotex#remotex-pro"
    PRO_BUY_URL   = "https://neurocontrarian.lemonsqueezy.com/checkout/buy/9c16845a-8ab6-4a36-b8da-9874d9d64f33"
    SUPPORT_EMAIL = "neurocontrarian@gmail.com"

    def is_pro_active() -> bool:
        return False

    def get_license_key() -> str:
        return ""

    def get_license_info() -> dict:
        return {
            'active': False, 'key': '', 'type': '', 'expires': None,
            'activated_at': None, 'is_expired': False,
            'days_until_expiry': None, 'expiry_warning': False,
            'activation_limit': None, 'activation_usage': None,
        }

    def get_trial_info() -> dict:
        return {'active': False, 'days_remaining': None, 'started_at': None, 'expires_at': None}

    def clear_license_key() -> None:
        return None

    def validate_license_online(key: str, email: str = '') -> tuple[bool, str, None]:
        # Should never be called from a free build (UI gates this), but fail
        # gracefully if it is.
        return False, 'pro_required', None

    def revalidate_license() -> bool:
        return False

    def get_machine_id() -> str:
        try:
            mid = Path('/etc/machine-id').read_text().strip()
            if mid:
                return hashlib.sha256(mid.encode()).hexdigest()[:32]
        except OSError:
            pass
        parts = [platform.node(), str(uuid_module.getnode()), platform.machine()]
        return hashlib.sha256('|'.join(parts).encode()).hexdigest()[:32]


def make_executor(config):
    """Return a CommandExecutorPro if available, else the free CommandExecutor."""
    try:
        from pro.services.executor_pro import CommandExecutorPro
        return CommandExecutorPro(config)
    except ImportError:
        from services.executor import CommandExecutor
        return CommandExecutor(config)


__all__ = [
    'PRO_AVAILABLE',
    'is_pro_active', 'get_license_key', 'get_license_info', 'get_trial_info',
    'clear_license_key', 'validate_license_online', 'revalidate_license',
    'get_machine_id',
    'FREE_BUTTON_LIMIT', 'FREE_MACHINE_LIMIT', 'TRIAL_DAYS',
    'PRO_INFO_URL', 'PRO_BUY_URL', 'SUPPORT_EMAIL',
    'make_executor',
]
