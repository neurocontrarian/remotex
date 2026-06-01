from .base import PlatformAdapter

_instance: PlatformAdapter | None = None


def get_platform() -> PlatformAdapter:
    global _instance
    if _instance is not None:
        return _instance
    import sys
    # Android reports sys.platform == "linux", so detect it FIRST via the
    # interpreter-level marker only present on Android, before the linux fallback.
    if hasattr(sys, "getandroidapilevel"):
        from .android import AndroidAdapter
        _instance = AndroidAdapter()
    elif sys.platform == "darwin":
        from .macos import MacAdapter
        _instance = MacAdapter()
    elif sys.platform.startswith("win"):
        from .windows import WindowsAdapter
        _instance = WindowsAdapter()
    else:
        from .linux import LinuxAdapter
        _instance = LinuxAdapter()
    return _instance
