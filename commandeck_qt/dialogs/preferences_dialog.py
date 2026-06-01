"""Preferences dialog — Qt equivalent of GTK PreferencesDialog."""
from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QTabWidget, QWidget, QLabel, QCheckBox,
    QSpinBox, QComboBox, QLineEdit, QPushButton,
    QGroupBox, QScrollArea, QDialogButtonBox,
    QMessageBox, QListWidget, QListWidgetItem,
    QFileDialog, QFileIconProvider, QFrame, QSizePolicy,
)

from commandeck_core.models.config import ConfigManager
from commandeck_core.i18n import _, set_language, SUPPORTED_LANGUAGES
from commandeck_qt.settings import Settings


class _NullIconProvider(QFileIconProvider):
    """Icon provider that returns empty icons — prevents Qt from loading GTK3
    file-type icons which crash on Linux Mint venvs with broken pixbuf loaders."""
    def icon(self, *args):
        return QIcon()


def _make_file_dialog(parent, caption: str, directory: str = "",
                      name_filter: str = "") -> QFileDialog:
    dlg = QFileDialog(parent, caption, directory, name_filter)
    dlg.setOption(QFileDialog.DontUseNativeDialog, True)
    dlg.setIconProvider(_NullIconProvider())
    return dlg


def _safe_get_save_filename(parent, caption: str, default_name: str,
                             name_filter: str) -> str:
    dlg = _make_file_dialog(parent, caption, default_name, name_filter)
    dlg.setAcceptMode(QFileDialog.AcceptSave)
    if dlg.exec() != QDialog.Accepted:
        return ""
    files = dlg.selectedFiles()
    return files[0] if files else ""


def _safe_get_open_filename(parent, caption: str, name_filter: str) -> str:
    dlg = _make_file_dialog(parent, caption, "", name_filter)
    dlg.setAcceptMode(QFileDialog.AcceptOpen)
    dlg.setFileMode(QFileDialog.ExistingFile)
    if dlg.exec() != QDialog.Accepted:
        return ""
    files = dlg.selectedFiles()
    return files[0] if files else ""


def _safe_get_existing_directory(parent, caption: str) -> str:
    dlg = _make_file_dialog(parent, caption)
    dlg.setFileMode(QFileDialog.Directory)
    dlg.setOption(QFileDialog.ShowDirsOnly, True)
    if dlg.exec() != QDialog.Accepted:
        return ""
    files = dlg.selectedFiles()
    return files[0] if files else ""


def show_preferences_dialog(config: ConfigManager, settings: Settings,
                             parent=None) -> None:
    # Non-modal, independent window: shown with show() (not exec()) so it is not
    # tied to the main window. GNOME/Wayland renders MODAL transient dialogs glued
    # to the parent's titlebar — a modeless dialog appears as its own window.
    # Reuse a single instance and keep a reference so it is not garbage-collected.
    existing = getattr(parent, "_preferences_dialog", None)
    if existing is not None:
        existing.raise_()
        existing.activateWindow()
        return
    dlg = PreferencesDialog(config, settings, parent=parent)
    dlg.setModal(False)
    dlg.setAttribute(Qt.WA_DeleteOnClose, True)
    if parent is not None:
        parent._preferences_dialog = dlg
        dlg.destroyed.connect(lambda *_: setattr(parent, "_preferences_dialog", None))
        # Refresh the main window when the dialog closes — theme, button size,
        # hidden categories etc. only affect already-built tiles after a
        # re-apply + re-populate. The dialog is non-modal (show(), not exec()),
        # so the caller cannot run this after the user closes it.
        if hasattr(parent, "_apply_theme") and hasattr(parent, "populate_grid"):
            def _refresh_parent():
                parent._apply_theme()
                parent.populate_grid()
            dlg.finished.connect(lambda *_: _refresh_parent())
    dlg.show()
    dlg.raise_()
    dlg.activateWindow()


class PreferencesDialog(QDialog):
    def __init__(self, config: ConfigManager, settings: Settings, parent=None):
        super().__init__(parent)
        self._config = config
        self._settings = settings
        self.setWindowTitle(_("Preferences"))
        self.setMinimumSize(520, 580)
        self._build_ui()

    def _build_ui(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_general_tab(), _("General"))
        self._tabs.addTab(self._build_appearance_tab(), _("Appearance"))
        self._tabs.addTab(self._build_categories_tab(), _("Categories"))
        self._tabs.addTab(self._build_desktop_tab(), _("Desktop"))
        self._tabs.addTab(self._build_license_tab(), _("License"))
        self._tabs.addTab(self._build_backup_tab(), _("Backup"))
        vbox.addWidget(self._tabs, 1)

        bb = QDialogButtonBox(QDialogButtonBox.Close)
        bb.setContentsMargins(12, 8, 12, 12)
        bb.rejected.connect(self.accept)
        vbox.addWidget(bb)

    # ── General tab ───────────────────────────────────────────────────────────

    def _build_general_tab(self) -> QWidget:
        tab = _ScrollTab()
        vbox = tab.inner_layout()

        # Command execution group
        exec_box = QGroupBox(_("Command Execution"))
        exec_form = QFormLayout(exec_box)
        exec_form.setLabelAlignment(Qt.AlignRight)

        self._timeout_spin = QSpinBox()
        self._timeout_spin.setRange(5, 300)
        self._timeout_spin.setSingleStep(5)
        self._timeout_spin.setValue(self._settings.get_int("command-timeout"))
        self._timeout_spin.setToolTip(_("Maximum duration before a command is killed (seconds)"))
        self._timeout_spin.valueChanged.connect(
            lambda v: self._settings.set_int("command-timeout", v)
        )
        exec_form.addRow(_("Command timeout (s)"), self._timeout_spin)

        self._confirm_check = QCheckBox(_("Pre-tick 'Confirm before running' for new buttons"))
        self._confirm_check.setChecked(self._settings.get_bool("confirm-before-run"))
        self._confirm_check.toggled.connect(
            lambda v: self._settings.set_bool("confirm-before-run", v)
        )
        exec_form.addRow("", self._confirm_check)
        vbox.addWidget(exec_box)

        # Note: there is no "buttons per row" setting — the grid reflows to fit the
        # window width automatically (see commandeck_qt/flow_layout.py).

        # Language group
        lang_box = QGroupBox(_("Interface"))
        lang_form = QFormLayout(lang_box)
        lang_form.setLabelAlignment(Qt.AlignRight)

        self._lang_combo = QComboBox()
        self._lang_codes = list(SUPPORTED_LANGUAGES.keys())
        for label in SUPPORTED_LANGUAGES.values():
            self._lang_combo.addItem(label)
        cur_lang = self._settings.get_str("language")
        idx = self._lang_codes.index(cur_lang) if cur_lang in self._lang_codes else 0
        self._lang_combo.setCurrentIndex(idx)
        self._lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        self._lang_combo.setToolTip(_("Restart Commandeck to apply the language change"))
        lang_form.addRow(_("Language"), self._lang_combo)
        vbox.addWidget(lang_box)

        vbox.addStretch()
        return tab

    def _on_lang_changed(self, idx: int):
        lang = self._lang_codes[idx]
        cur = self._settings.get_str("language")
        if lang == cur:
            return
        self._settings.set_str("language", lang)
        set_language(lang)
        if self.parent() and hasattr(self.parent(), "show_toast"):
            self.parent().show_toast(_("Language changed — restart Commandeck to apply"))

    # ── Appearance tab ────────────────────────────────────────────────────────

    def _on_scheme_changed(self, index: int) -> None:
        scheme = self._scheme_values[index]
        self._settings.set_str("color-scheme", scheme)
        try:  # apply live to the running app
            from PySide6.QtWidgets import QApplication
            from commandeck_qt.app import apply_color_scheme
            apply_color_scheme(QApplication.instance(), scheme)
        except Exception:
            pass

    def _build_appearance_tab(self) -> QWidget:
        tab = _ScrollTab()
        vbox = tab.inner_layout()

        app_box = QGroupBox(_("Appearance"))
        app_form = QFormLayout(app_box)
        app_form.setLabelAlignment(Qt.AlignRight)

        # Color scheme (applies to the whole UI; free)
        self._scheme_combo = QComboBox()
        self._scheme_values = ["system", "light", "dark"]
        for label in [_("System"), _("Light"), _("Dark")]:
            self._scheme_combo.addItem(label)
        cur_scheme = self._settings.get_str("color-scheme")
        self._scheme_combo.setCurrentIndex(
            self._scheme_values.index(cur_scheme) if cur_scheme in self._scheme_values else 0
        )
        self._scheme_combo.currentIndexChanged.connect(self._on_scheme_changed)
        app_form.addRow(_("Color scheme"), self._scheme_combo)

        self._size_combo = QComboBox()
        self._size_values = ["small", "medium", "large"]
        for label in [_("Small (80×80)"), _("Medium (120×120)"), _("Large (160×160)")]:
            self._size_combo.addItem(label)
        cur_size = self._settings.get_str("button-size")
        self._size_combo.setCurrentIndex(
            self._size_values.index(cur_size) if cur_size in self._size_values else 1
        )
        self._size_combo.currentIndexChanged.connect(
            lambda i: self._settings.set_str("button-size", self._size_values[i])
        )
        app_form.addRow(_("Button size"), self._size_combo)

        try:
            from commandeck_core.pro.license import is_pro_active
            pro = is_pro_active()
        except ImportError:
            pro = False

        self._theme_combo = QComboBox()
        self._theme_values = ["bold", "cards", "phone", "neon", "tron", "retro"]
        for label in [_("Bold (default)"), _("Cards"), _("Phone keys"), _("Neon"), _("Tron"), _("Retro")]:
            self._theme_combo.addItem(label)
        if pro:
            cur_theme = self._settings.get_str("button-theme")
            self._theme_combo.setCurrentIndex(
                self._theme_values.index(cur_theme) if cur_theme in self._theme_values else 0
            )
            self._theme_combo.currentIndexChanged.connect(
                lambda i: self._settings.set_str("button-theme", self._theme_values[i])
            )
        else:
            self._theme_combo.setEnabled(False)
            self._theme_combo.setToolTip(_("Pro feature — upgrade to unlock custom themes"))
        app_form.addRow(_("Button theme (Pro)"), self._theme_combo)
        vbox.addWidget(app_box)

        # Custom icon directories
        icon_box = QGroupBox(_("Custom Icon Directories"))
        icon_box.setToolTip(
            _("Directories searched for icons before the bundled Bootstrap Icons set.\n"
              "Place .png or .svg files named after the icon here.")
        )
        icon_vbox = QVBoxLayout(icon_box)
        self._icon_list = QListWidget()
        self._icon_list.setMaximumHeight(120)
        icon_vbox.addWidget(self._icon_list)
        self._refresh_icon_paths()

        icon_btns = QHBoxLayout()
        add_dir_btn = QPushButton(_("Add directory…"))
        add_dir_btn.clicked.connect(self._on_add_icon_dir)
        rm_dir_btn = QPushButton(_("Remove"))
        rm_dir_btn.clicked.connect(self._on_remove_icon_dir)
        icon_btns.addStretch()
        icon_btns.addWidget(add_dir_btn)
        icon_btns.addWidget(rm_dir_btn)
        icon_vbox.addLayout(icon_btns)
        vbox.addWidget(icon_box)

        vbox.addStretch()
        return tab

    def _refresh_icon_paths(self):
        self._icon_list.clear()
        for p in self._settings.get_strv("icon-search-paths"):
            self._icon_list.addItem(p)

    def _on_add_icon_dir(self):
        folder = _safe_get_existing_directory(self, _("Select icon directory"))
        if folder:
            current = self._settings.get_strv("icon-search-paths")
            if folder not in current:
                current.append(folder)
                self._settings.set_strv("icon-search-paths", current)
            self._refresh_icon_paths()

    def _on_remove_icon_dir(self):
        item = self._icon_list.currentItem()
        if not item:
            return
        current = self._settings.get_strv("icon-search-paths")
        p = item.text()
        if p in current:
            current.remove(p)
            self._settings.set_strv("icon-search-paths", current)
        self._refresh_icon_paths()

    # ── Categories tab ────────────────────────────────────────────────────────

    def _build_categories_tab(self) -> QWidget:
        tab = _ScrollTab()
        vbox = tab.inner_layout()

        buttons = self._config.load_buttons()
        categories = sorted({b.category for b in buttons if b.category})
        hidden = set(self._settings.get_strv("hidden-categories"))

        if not categories:
            lbl = QLabel(_("No categories defined yet.\nAdd a category to a button to see it here."))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setWordWrap(True)
            vbox.addWidget(lbl)
            vbox.addStretch()
            return tab

        box = QGroupBox(_("Categories"))
        box.setToolTip(_("Hidden categories and their buttons will not appear in the grid"))
        form = QFormLayout(box)

        for cat in categories:
            cb = QCheckBox(cat)
            cb.setChecked(cat not in hidden)

            def make_handler(cat_name):
                def on_toggle(checked):
                    cur = set(self._settings.get_strv("hidden-categories"))
                    if checked:
                        cur.discard(cat_name)
                    else:
                        cur.add(cat_name)
                    self._settings.set_strv("hidden-categories", sorted(cur))
                return on_toggle

            cb.toggled.connect(make_handler(cat))
            form.addRow("", cb)

        vbox.addWidget(box)
        vbox.addStretch()
        return tab

    # ── Desktop tab ───────────────────────────────────────────────────────────

    def _build_desktop_tab(self) -> QWidget:
        tab = _ScrollTab()
        vbox = tab.inner_layout()

        from commandeck_core.platform import get_platform
        platform = get_platform()
        aot_ok, aot_reason = platform.supports_always_on_top()

        desktop_box = QGroupBox(_("Desktop Integration"))
        desktop_form = QFormLayout(desktop_box)
        desktop_form.setLabelAlignment(Qt.AlignRight)

        self._aot_check = QCheckBox(_("Keep Commandeck above all other windows"))
        self._aot_check.setChecked(self._settings.get_bool("always-on-top") and aot_ok)
        if not aot_ok:
            self._aot_check.setEnabled(False)
            self._aot_check.setToolTip(aot_reason)
        else:
            self._aot_check.toggled.connect(self._on_always_on_top)
        desktop_form.addRow(_("Always on top"), self._aot_check)

        self._autostart_check = QCheckBox(_("Start Commandeck automatically when you log in"))
        self._autostart_check.setChecked(platform.is_autostart_enabled())
        self._autostart_check.toggled.connect(
            lambda v: platform.set_autostart(v)
        )
        desktop_form.addRow(_("Launch at login"), self._autostart_check)
        vbox.addWidget(desktop_box)

        # MCP section (Pro only)
        try:
            from commandeck_core.pro.license import is_pro_active
            pro = is_pro_active()
        except ImportError:
            pro = False

        if pro:
            mcp_box = QGroupBox(_("MCP Access (AI Integration)"))
            mcp_form = QFormLayout(mcp_box)
            mcp_form.setLabelAlignment(Qt.AlignRight)
            from commandeck_core.platform import get_platform
            config_dir = get_platform().config_dir()
            mcp_flag = config_dir / ".mcp_enabled"
            mcp_enabled = mcp_flag.exists()

            # The headless MCP server (commandeck_core, no Qt) cannot read QSettings, so
            # the "allow AI execution" choice is mirrored to a shared flag file it can
            # read. Reconcile the legacy QSettings value into the flag on open.
            mcp_exec_flag = config_dir / ".mcp_execution_enabled"
            mcp_exec_enabled = (
                mcp_exec_flag.exists()
                or self._settings.get_bool("mcp-execution-enabled")
            )
            if mcp_exec_enabled and not mcp_exec_flag.exists():
                mcp_exec_flag.parent.mkdir(parents=True, exist_ok=True)
                mcp_exec_flag.touch()

            self._mcp_check = QCheckBox(
                _("Let AI assistants read and edit your buttons via MCP")
            )
            self._mcp_check.setChecked(mcp_enabled)

            self._mcp_exec_check = QCheckBox(
                _("Permit AI clients to trigger buttons that have 'Allow AI' enabled")
            )
            self._mcp_exec_check.setChecked(mcp_exec_enabled)
            self._mcp_exec_check.setEnabled(mcp_enabled)

            def on_mcp_exec_toggle(v):
                self._settings.set_bool("mcp-execution-enabled", v)
                if v:
                    mcp_exec_flag.parent.mkdir(parents=True, exist_ok=True)
                    mcp_exec_flag.touch()
                else:
                    mcp_exec_flag.unlink(missing_ok=True)

            self._mcp_exec_check.toggled.connect(on_mcp_exec_toggle)

            def on_mcp_toggle(checked):
                if checked:
                    mcp_flag.parent.mkdir(parents=True, exist_ok=True)
                    mcp_flag.touch()
                else:
                    mcp_flag.unlink(missing_ok=True)
                self._mcp_exec_check.setEnabled(checked)

            self._mcp_check.toggled.connect(on_mcp_toggle)

            mcp_form.addRow(_("Allow MCP access"), self._mcp_check)
            mcp_form.addRow(_("Allow AI execution"), self._mcp_exec_check)
            vbox.addWidget(mcp_box)

        vbox.addStretch()
        return tab

    def _on_always_on_top(self, checked: bool):
        self._settings.set_bool("always-on-top", checked)
        if self.parent():
            flags = self.parent().windowFlags()
            if checked:
                self.parent().setWindowFlags(flags | Qt.WindowStaysOnTopHint)
            else:
                self.parent().setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
            self.parent().show()

    # ── License tab ───────────────────────────────────────────────────────────

    def _build_license_tab(self) -> QWidget:
        tab = _ScrollTab()
        self._license_vbox = tab.inner_layout()
        self._rebuild_license_section()
        return tab

    def _rebuild_license_section(self):
        while self._license_vbox.count():
            item = self._license_vbox.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            from commandeck_core.pro.license import (
                is_pro_active, get_license_info, get_trial_info,
                clear_license_key, validate_license_online,
                FREE_BUTTON_LIMIT, FREE_MACHINE_LIMIT,
                PRO_BUY_URL, SUPPORT_EMAIL, PRO_AVAILABLE,
            )
        except ImportError:
            # Free build
            self._license_vbox.addWidget(QLabel(_("Pro features are not available in this build.")))
            self._license_vbox.addStretch()
            return

        info = get_license_info()
        box = QGroupBox(_("License"))
        form = QFormLayout(box)

        if info.get("active"):
            is_yearly = info.get("type") == "yearly"
            days = info.get("days_until_expiry")
            key = info.get("key", "")
            masked = key[:4] + "·" * max(0, len(key) - 8) + key[-4:] if len(key) > 8 else key

            if is_yearly:
                title = _("Commandeck Pro — Yearly")
                if days is not None and days <= 30:
                    sub = _("Expires in {days} days — renew to keep Pro access").format(days=max(0, days))
                else:
                    sub = _("Yearly license — expires on {date}").format(date=info.get("expires", "—"))
            else:
                title = _("Commandeck Pro — Lifetime")
                sub = _("Lifetime license — enjoy all Pro features!")

            form.addRow(_("Status"), QLabel(f"✓  {title}"))
            form.addRow(_("Info"), QLabel(sub))
            form.addRow(_("Key"), QLabel(masked))

            al = info.get("activation_limit")
            au = info.get("activation_usage")
            if al is not None and au is not None:
                form.addRow(_("Activations"),
                            QLabel(_("{used} / {limit} devices").format(used=au, limit=al)))

            deact_btn = QPushButton(_("Deactivate license"))
            deact_btn.clicked.connect(lambda: self._on_deactivate(clear_license_key))
            form.addRow("", deact_btn)

            if is_yearly:
                renew_btn = QPushButton(_("Renew license — $29/year"))
                renew_btn.clicked.connect(lambda: self._open_url(PRO_BUY_URL))
                form.addRow("", renew_btn)

        elif info.get("is_expired"):
            key = info.get("key", "")
            masked = key[:4] + "·" * max(0, len(key) - 8) + key[-4:] if len(key) > 8 else key
            form.addRow(_("Status"), QLabel(_("License expired on {date}").format(
                date=info.get("expires", "—"))))
            form.addRow(_("Key"), QLabel(masked))
            renew_btn = QPushButton(_("Renew license — $29/year"))
            renew_btn.clicked.connect(lambda: self._open_url(PRO_BUY_URL))
            form.addRow("", renew_btn)
            rm_btn = QPushButton(_("Remove expired key"))
            rm_btn.clicked.connect(lambda: self._on_deactivate(clear_license_key))
            form.addRow("", rm_btn)

        elif not PRO_AVAILABLE:
            form.addRow(
                _("Status"),
                QLabel(_("Free tier — limited to {n} custom buttons.").format(
                    n=FREE_BUTTON_LIMIT))
            )
            buy_btn = QPushButton(_("Get Commandeck Pro — $29/year"))
            buy_btn.clicked.connect(lambda: self._open_url(PRO_BUY_URL))
            form.addRow("", buy_btn)

        else:
            trial = get_trial_info()
            if trial.get("active"):
                days = trial.get("days_remaining", 0)
                expires = trial.get("expires_at", "")
                form.addRow(
                    _("Status"),
                    QLabel(_("Trial — {days} day(s) remaining (until {date})").format(
                        days=days, date=expires))
                )
            else:
                form.addRow(
                    _("Status"),
                    QLabel(_("Free tier — limited to {n} custom buttons.").format(
                        n=FREE_BUTTON_LIMIT))
                )

            self._key_edit = QLineEdit()
            self._key_edit.setPlaceholderText(_("License key"))
            form.addRow(_("License key"), self._key_edit)

            self._email_edit = QLineEdit()
            self._email_edit.setPlaceholderText(_("Purchase email"))
            form.addRow(_("Purchase email"), self._email_edit)

            act_btn = QPushButton(_("Activate Pro"))
            act_btn.clicked.connect(lambda: self._on_activate(
                validate_license_online, SUPPORT_EMAIL
            ))
            form.addRow("", act_btn)

            buy_btn = QPushButton(_("Get Commandeck Pro — $29/year"))
            buy_btn.clicked.connect(lambda: self._open_url(PRO_BUY_URL))
            form.addRow("", buy_btn)

        self._license_vbox.addWidget(box)
        self._license_vbox.addStretch()

    def _on_deactivate(self, clear_fn):
        answer = QMessageBox.question(
            self, _("Deactivate license"),
            _("Remove the license key from this device?"),
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            try:
                clear_fn()
            except Exception:
                pass
            self._rebuild_license_section()
            if self.parent() and hasattr(self.parent(), "show_toast"):
                self.parent().show_toast(_("License deactivated"))

    def _on_activate(self, validate_fn, support_email: str):
        key = self._key_edit.text().strip() if hasattr(self, "_key_edit") else ""
        email = self._email_edit.text().strip() if hasattr(self, "_email_edit") else ""
        if not key:
            QMessageBox.warning(self, _("Missing key"), _("Enter your license key."))
            return

        from commandeck_core.utils.threading import run_in_thread

        def _run():
            try:
                return validate_fn(key, email)
            except Exception:
                return (False, "network_error", None)

        def _done(result):
            if isinstance(result, Exception):
                QMessageBox.critical(self, _("Error"), str(result))
                return
            valid, license_type, expires = result
            if valid:
                self._rebuild_license_section()
                if self.parent() and hasattr(self.parent(), "show_toast"):
                    self.parent().show_toast(_("Pro activated — enjoy Commandeck Pro!"))
            else:
                if license_type == "network_error":
                    QMessageBox.critical(self, _("Activation failed"),
                                         _("Internet connection required for activation."))
                elif license_type == "email_mismatch":
                    QMessageBox.warning(self, _("Activation failed"),
                                        _("Email does not match this license key."))
                elif license_type == "limit_reached":
                    QMessageBox.warning(
                        self, _("Activation failed"),
                        _("You have reached the maximum number of activations.\n"
                          "Deactivate on another device first, or contact {email}.").format(
                            email=support_email)
                    )
                else:
                    QMessageBox.warning(self, _("Activation failed"),
                                        _("Invalid or expired license key."))

        run_in_thread(_run, _done)

    def _open_url(self, url: str):
        from commandeck_core.platform import get_platform
        get_platform().open_browser(url)

    # ── Backup tab ────────────────────────────────────────────────────────────

    def _build_backup_tab(self) -> QWidget:
        tab = _ScrollTab()
        vbox = tab.inner_layout()

        try:
            from commandeck_core.pro.license import is_pro_active
            pro = is_pro_active()
        except ImportError:
            pro = False

        if not pro:
            lbl = QLabel(_("Backup and restore features require Commandeck Pro."))
            lbl.setWordWrap(True)
            lbl.setAlignment(Qt.AlignCenter)
            vbox.addWidget(lbl)
            vbox.addStretch()
            return tab

        # Buttons & settings backup
        btn_box = QGroupBox(_("Buttons & Settings Backup"))
        btn_box.setToolTip(
            _("Export your buttons and settings to a .cdbackup file.\n"
              "Machines are exported separately below.")
        )
        btn_vbox = QVBoxLayout(btn_box)
        exp_btn = QPushButton(_("Export buttons & settings…"))
        exp_btn.clicked.connect(self._on_export_buttons)
        imp_btn = QPushButton(_("Import buttons & settings…"))
        imp_btn.clicked.connect(self._on_import_buttons)
        btn_vbox.addWidget(exp_btn)
        btn_vbox.addWidget(imp_btn)
        vbox.addWidget(btn_box)

        # Machines backup
        mach_box = QGroupBox(_("Machines Backup"))
        mach_box.setToolTip(
            _("Export machine definitions (hosts, users, ports).\n"
              "SSH private keys are never included.")
        )
        mach_vbox = QVBoxLayout(mach_box)
        exp_m_btn = QPushButton(_("Export machines…"))
        exp_m_btn.clicked.connect(self._on_export_machines)
        imp_m_btn = QPushButton(_("Import machines…"))
        imp_m_btn.clicked.connect(self._on_import_machines)
        mach_vbox.addWidget(exp_m_btn)
        mach_vbox.addWidget(imp_m_btn)
        vbox.addWidget(mach_box)

        # Reset to defaults
        reset_box = QGroupBox(_("Reset Buttons"))
        reset_vbox = QVBoxLayout(reset_box)
        reset_lbl = QLabel(
            _("Restore the default buttons. Your current buttons.toml is backed up first.")
        )
        reset_lbl.setWordWrap(True)
        reset_vbox.addWidget(reset_lbl)
        reset_btn = QPushButton(_("Reset to default buttons"))
        reset_btn.clicked.connect(self._on_reset_buttons)
        reset_vbox.addWidget(reset_btn)
        vbox.addWidget(reset_box)

        vbox.addStretch()
        return tab

    def _on_export_buttons(self):
        path = _safe_get_save_filename(
            self, _("Export buttons & settings"),
            "commandeck.cdbackup", "Commandeck backup (*.cdbackup)",
        )
        if path:
            try:
                self._config.export_backup(Path(path), self._settings)
                self._toast(_("Config exported successfully"))
            except Exception as e:
                QMessageBox.critical(self, _("Export failed"), str(e))

    def _on_import_buttons(self):
        path = _safe_get_open_filename(
            self, _("Import buttons & settings"),
            "Commandeck backup (*.cdbackup *.rxbackup)",
        )
        if path:
            try:
                need_pwd = self._config.import_backup(Path(path), self._settings)
                self._toast(_("Config imported — restart Commandeck to apply all changes"))
                if need_pwd:
                    QMessageBox.information(
                        self, _("Re-enter sudo passwords"),
                        _("Sudo passwords are not included in backups (for security). "
                          "Re-enter the password on this device for these buttons:")
                        + "\n\n• " + "\n• ".join(need_pwd))
            except Exception as e:
                QMessageBox.critical(self, _("Import failed"), str(e))

    def _on_export_machines(self):
        path = _safe_get_save_filename(
            self, _("Export machines"),
            "commandeck.cdmachines", "Commandeck machines (*.cdmachines)",
        )
        if path:
            try:
                self._config.export_machines_backup(Path(path))
                self._toast(_("Machines exported successfully"))
            except Exception as e:
                QMessageBox.critical(self, _("Export failed"), str(e))

    def _on_import_machines(self):
        path = _safe_get_open_filename(
            self, _("Import machines"),
            "Commandeck machines (*.cdmachines *.rxmachines)",
        )
        if path:
            try:
                result = self._config.import_machines_backup(Path(path))
                self._toast(_("Machines imported — restart Commandeck to apply"))
                blocks = []
                if result.get("missing_keys"):
                    blocks.append(
                        _("SSH key file not found on this device — open each machine "
                          "and re-select its key:")
                        + "\n• " + "\n• ".join(result["missing_keys"]))
                if result.get("need_password"):
                    blocks.append(
                        _("SSH passwords are not included in backups (for security) — "
                          "re-enter the password for:")
                        + "\n• " + "\n• ".join(result["need_password"]))
                if blocks:
                    QMessageBox.information(
                        self, _("Action needed after import"), "\n\n".join(blocks))
            except Exception as e:
                QMessageBox.critical(self, _("Import failed"), str(e))

    def _on_reset_buttons(self):
        answer = QMessageBox.question(
            self,
            _("Reset to default buttons?"),
            _("All your custom buttons will be replaced by the default buttons. "
              "Your current buttons.toml will be backed up first."),
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            try:
                backup = self._config.reset_buttons_to_defaults()
                if self.parent() and hasattr(self.parent(), "populate_grid"):
                    self.parent().populate_grid()
                msg = (_("Buttons reset — backup saved to {path}").format(path=backup.name)
                       if backup else _("Buttons reset to defaults"))
                self._toast(msg)
            except Exception as e:
                QMessageBox.critical(self, _("Reset failed"), str(e))

    def _toast(self, msg: str):
        if self.parent() and hasattr(self.parent(), "show_toast"):
            self.parent().show_toast(msg)


class _ScrollTab(QScrollArea):
    """A scroll area that acts as a tab page."""
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self._inner = QWidget()
        self._vbox = QVBoxLayout(self._inner)
        self._vbox.setContentsMargins(16, 16, 16, 16)
        self._vbox.setSpacing(16)
        self.setWidget(self._inner)

    def inner_layout(self) -> QVBoxLayout:
        return self._vbox
