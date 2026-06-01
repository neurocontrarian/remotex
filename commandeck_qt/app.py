"""PySide6 application entry point."""
from __future__ import annotations

import os
import sys


# Force defence-in-depth env vars on Linux BEFORE Qt is imported. These alone
# do NOT prevent the GTK3 plugin from being loaded (six prior attempts proved
# it), but they reduce the surface area: Qt won't actively select gtk3 as the
# theme, and QFileDialog defaults to non-native. The real fix is the plugin
# sandbox installed below in _install_plugin_sandbox(), which prevents Qt
# from ever finding libqgtk3.so / libqxdgdesktopportal.so in the first place.
if sys.platform.startswith("linux"):
    os.environ["QT_QPA_PLATFORMTHEME"] = "none"
    os.environ.setdefault("QT_STYLE_OVERRIDE", "Fusion")
    # Silence the noisy "Got leave event for surface 0x0" warning that the Qt
    # Wayland text-input plugin spams on dialog close. Harmless, but pollutes
    # stderr/journal. setdefault so the user can still override via env.
    os.environ.setdefault(
        "QT_LOGGING_RULES", "qt.qpa.wayland.textinput.warning=false"
    )

from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


def _install_plugin_sandbox_linux() -> None:
    """Block Qt from ever loading the bundled GTK3 / xdg-desktop-portal
    platform-theme plugins on Linux.

    Why this is necessary
    ---------------------
    PySide6's wheels ship `libqgtk3.so` and `libqxdgdesktopportal.so` under
    `<pkg>/PySide6/Qt/plugins/platformthemes/`. On X11 sessions Qt eagerly
    instantiates the matching theme based on `XDG_CURRENT_DESKTOP` (Cinnamon,
    GNOME, KDE…). When QFileDialog is opened, Qt then asks that theme to
    resolve standard file icons, which calls into `libgtk-3.so.0` and reads
    GTK's internal GResource bundle (`/org/gtk/libgtk/icons/.../image-missing.png`).
    On Linux Mint inside a `--system-site-packages` venv, the host pixbuf SVG
    loader is misconfigured and the GResource read fails, triggering
    `Gtk:ERROR` + `abort()` — a C-level crash that Python `try/except` cannot
    catch.

    Six prior attempts only set environment variables (`QT_QPA_PLATFORMTHEME`,
    `QT_STYLE_OVERRIDE`, `DontUseNativeDialog`, custom `QFileIconProvider`).
    None of them prevent Qt from *loading* the plugin once the desktop is
    detected — they only influence which one is chosen. The crash happens
    inside the plugin itself, before any of those guards take effect.

    Note: `QT_PLUGIN_PATH` *prepends* to Qt's compiled-in plugin search; it
    does not replace it. Qt would still find the bundled `platformthemes/`.
    `QCoreApplication.setLibraryPaths()` *replaces* the search list entirely,
    which is what we need.

    Fix
    ---
    1. Mirror every plugin subdir from `PySide6/Qt/plugins/` into a per-process
       temp dir via symlinks (cheap, no copy).
    2. Create an empty `platformthemes/` inside it.
    3. Call `QCoreApplication.setLibraryPaths([sandbox])` BEFORE the first
       `QApplication(...)` — this is when Qt does plugin discovery.

    With no theme plugin findable, Qt falls back to its built-in generic
    theme. `QFileDialog` (non-native) renders fine using Qt's own icons;
    `libgtk-3.so.0` is never dlopen'd in the process.

    This affects Linux only. macOS / Windows are untouched.
    The temp dir is auto-cleaned on process exit via `atexit`.
    """
    import tempfile
    import atexit
    import shutil
    from pathlib import Path

    try:
        import PySide6
    except ImportError:
        return

    src_plugins = Path(PySide6.__file__).parent / "Qt" / "plugins"
    if not src_plugins.is_dir():
        return

    sandbox = Path(tempfile.mkdtemp(prefix="commandeck-qt-plugins-"))
    atexit.register(shutil.rmtree, sandbox, ignore_errors=True)

    sandbox_usable = True
    for child in src_plugins.iterdir():
        target = sandbox / child.name
        if child.name == "platformthemes":
            # Replace with an empty dir — Qt finds nothing to load here.
            try:
                target.mkdir()
            except OSError:
                sandbox_usable = False
                break
            continue
        try:
            target.symlink_to(child)
        except OSError:
            # Filesystem without symlink support (rare). Bail out and let Qt
            # use its default plugin path; the env-var defences above are the
            # only line of defence in that case.
            sandbox_usable = False
            break

    if not sandbox_usable:
        return

    # setLibraryPaths replaces (not prepends) Qt's plugin search list. Must be
    # called BEFORE the first QApplication() — Qt caches plugin metadata at
    # construction time.
    QCoreApplication.setLibraryPaths([str(sandbox)])


if sys.platform.startswith("linux"):
    _install_plugin_sandbox_linux()

from commandeck_core.platform import get_platform
from commandeck_core.utils import threading as core_threading
from commandeck_core.models.config import ConfigManager
from commandeck_core.i18n import set_language, set_ui_framework

# Declare Qt framework before any core import that could trigger GTK.
set_ui_framework("qt")

from commandeck_qt.settings import Settings
from commandeck_qt.window import CommandeckWindow
from commandeck_qt._version import __version__ as APP_VERSION

_QSS_PATH = __import__("pathlib").Path(__file__).parent / "resources" / "style" / "base.qss"


def _load_stylesheet(app: QApplication) -> None:
    if _QSS_PATH.exists():
        app.setStyleSheet(_QSS_PATH.read_text())


def _dark_palette() -> QPalette:
    """A Fusion-style dark palette. base.qss uses palette(...) roles, so the
    whole UI follows it."""
    R, G = QPalette.ColorRole, QPalette.ColorGroup
    win, base, txt = QColor(53, 53, 53), QColor(35, 35, 35), QColor(230, 230, 230)
    hl = QColor(42, 130, 218)
    p = QPalette()
    p.setColor(R.Window, win);            p.setColor(R.WindowText, txt)
    p.setColor(R.Base, base);             p.setColor(R.AlternateBase, win)
    p.setColor(R.ToolTipBase, QColor(25, 25, 25)); p.setColor(R.ToolTipText, txt)
    p.setColor(R.Text, txt)
    p.setColor(R.Button, win);            p.setColor(R.ButtonText, txt)
    p.setColor(R.BrightText, QColor(255, 80, 80))
    p.setColor(R.Link, hl)
    p.setColor(R.Highlight, hl);          p.setColor(R.HighlightedText, QColor(20, 20, 20))
    p.setColor(R.Mid, QColor(90, 90, 90))
    p.setColor(R.PlaceholderText, QColor(140, 140, 140))
    for role in (R.WindowText, R.Text, R.ButtonText):
        p.setColor(G.Disabled, role, QColor(127, 127, 127))
    return p


# The platform/default palette captured on first apply, so "system" can restore it.
_default_palette: QPalette | None = None


def apply_color_scheme(app: QApplication, scheme: str) -> None:
    """Apply 'system' | 'light' | 'dark' to the running app (palette + scheme hint)."""
    global _default_palette
    if _default_palette is None:
        _default_palette = QPalette(app.palette())
    sh = app.styleHints()
    hint = {"dark": "Dark", "light": "Light"}.get(scheme, "Unknown")
    if hasattr(sh, "setColorScheme"):
        try:
            sh.setColorScheme(getattr(Qt.ColorScheme, hint))
        except Exception:
            pass
    if scheme == "dark":
        app.setPalette(_dark_palette())
    elif scheme == "light":
        app.setPalette(app.style().standardPalette())
    else:  # system — restore whatever the platform gave us at startup
        app.setPalette(_default_palette)
    _load_stylesheet(app)  # re-resolve palette(...) refs in the QSS


def _resolve_language(settings: Settings) -> str:
    lang = settings.get_str("language")
    if lang in ("system", ""):
        import locale
        lc = locale.getlocale()[0] or ""
        return lc[:2] if lc else "en"
    return lang


def _schedule_smoke_quit(app: "QApplication") -> None:
    """Quit after a short delay in --smoke-test mode, printing OK to stdout."""
    from PySide6.QtCore import QTimer

    def _quit() -> None:
        print("smoke-test: OK", flush=True)
        app.quit()

    QTimer.singleShot(800, _quit)


def _migrate_legacy_qsettings() -> None:
    """One-time copy of pre-rename QSettings (app "RemoteX") into the new store
    ("Commandeck"), so an existing install keeps its preferences after the
    RemoteX → Commandeck rename. Safe to call every launch: it only copies when
    the new store is empty and the old one has keys."""
    from PySide6.QtCore import QSettings
    try:
        new = QSettings("neurocontrarian", "Commandeck")
        if new.allKeys():
            return  # already have settings (or already migrated)
        old = QSettings("neurocontrarian", "RemoteX")
        keys = old.allKeys()
        if not keys:
            return
        for k in keys:
            new.setValue(k, old.value(k))
        new.sync()
    except Exception:
        pass  # preferences have safe defaults; never block startup


def _first_run_legal_gate(settings, parent) -> bool:
    """One-time disclaimer the user must accept before first use. Records
    consent (clickwrap) so the limitation-of-liability terms actually bind the
    user. Returns False if the user declines — the caller should then exit."""
    if settings.get_bool("legal-disclaimer-accepted"):
        return True
    from PySide6.QtWidgets import QMessageBox
    from commandeck_core.i18n import _
    box = QMessageBox(parent)
    box.setWindowTitle(_("Welcome to Commandeck"))
    box.setIcon(QMessageBox.Icon.Information)
    box.setTextFormat(Qt.TextFormat.RichText)
    box.setText("<b>" + _(
        "Commandeck runs the commands you create — with no sandbox, locally or "
        "over SSH.") + "</b>")
    box.setInformativeText(
        _("You alone are responsible for the commands you create and run, "
          "including any data loss or damage they may cause. The software is "
          "provided \"as is\", without warranty of any kind.")
        + "<br><br>"
        + _("By continuing you accept the")
        + ' <a href="https://commandeck.app/legal/terms/">'
        + _("Terms of Service") + "</a>.")
    agree = box.addButton(_("I understand and agree"),
                          QMessageBox.ButtonRole.AcceptRole)
    box.addButton(_("Quit"), QMessageBox.ButtonRole.RejectRole)
    box.setDefaultButton(agree)
    box.exec()
    if box.clickedButton() is agree:
        settings.set_bool("legal-disclaimer-accepted", True)
        return True
    return False


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--smoke-test", action="store_true",
                        help="Headless startup check: show window then quit cleanly.")
    args, remaining = parser.parse_known_args()

    smoke = args.smoke_test
    if smoke:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        # Suppress Qt platform warnings on headless runners. Overrides (not
        # setdefault) the narrower wayland-textinput rule installed at import
        # time on Linux — smoke runs want the broader filter.
        os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"

    QCoreApplication.setOrganizationName("neurocontrarian")
    QCoreApplication.setOrganizationDomain("io.github.neurocontrarian.commandeck")
    QCoreApplication.setApplicationName("Commandeck")
    QCoreApplication.setApplicationVersion(APP_VERSION)
    _migrate_legacy_qsettings()

    app = QApplication([sys.argv[0]] + remaining)

    # Wire threading bridge: worker thread → Qt main thread via QueuedConnection signal.
    # QTimer.singleShot(0, fn) from a non-Qt thread has no event loop and never fires.
    from commandeck_qt.threading_qt import get_dispatcher
    core_threading.set_main_thread_dispatcher(get_dispatcher().dispatch)

    platform = get_platform()
    config = ConfigManager(platform.config_dir())

    # Best-effort execution log for diagnostics. Path shown in Help menu.
    from commandeck_core.utils.exec_log import set_log_path, log as _diag_log
    set_log_path(platform.config_dir() / "execution.log")

    # Without this hook, exceptions raised inside Qt slots (e.g. button clicks)
    # are silently swallowed when the app runs under PyInstaller console=False
    # — stderr is not connected to anything. Routing them through exec_log
    # ensures any silent failure shows up next to its triggering log lines.
    import traceback as _tb
    _prev_hook = sys.excepthook

    def _excepthook(exc_type, exc, tb):
        _diag_log(f"!! UNHANDLED {exc_type.__name__}: {exc}\n{''.join(_tb.format_tb(tb))}")
        _prev_hook(exc_type, exc, tb)

    sys.excepthook = _excepthook

    settings = Settings()
    set_language(_resolve_language(settings))

    # Load base stylesheet + apply the saved color scheme (system / light / dark)
    apply_color_scheme(app, settings.get_str("color-scheme"))

    win = CommandeckWindow(config, platform)
    win.show()

    if smoke:
        _schedule_smoke_quit(app)
    elif not _first_run_legal_gate(settings, win):
        return  # user declined the first-run disclaimer — exit without running

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
