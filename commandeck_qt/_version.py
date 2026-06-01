"""Single source of the app version shown in the UI (e.g. the About dialog).

The value below is the dev/source fallback. Release builds overwrite this file
from the git tag (COMMANDECK_VERSION) before freezing — see
packaging/linux/build_appimage.sh and the macOS/Windows build workflows — so the
shipped version is always in sync with the tag and never goes stale.
"""

__version__ = "2.0.12"
