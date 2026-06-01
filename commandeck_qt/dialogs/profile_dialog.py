"""Add/Edit execution profile dialog (Pro)."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QComboBox, QDialogButtonBox, QPushButton,
    QHBoxLayout, QLabel, QWidget, QMessageBox,
)

from commandeck_core.models.config import ConfigManager
from commandeck_core.pro.models.execution_profile import ExecutionProfile
from commandeck_core.i18n import _


def show_profile_dialog(config: ConfigManager, profile: ExecutionProfile | None = None,
                        on_saved: Callable | None = None, parent=None) -> None:
    dlg = ProfileDialog(config, profile=profile, on_saved=on_saved, parent=parent)
    dlg.exec()


class ProfileDialog(QDialog):
    def __init__(self, config: ConfigManager, profile: ExecutionProfile | None = None,
                 on_saved: Callable | None = None, parent=None):
        super().__init__(parent)
        self._config = config
        self._profile = profile
        self._is_edit = profile is not None
        self._on_saved = on_saved
        self.setWindowTitle(_("Edit Profile") if self._is_edit else _("New Profile"))
        self.setMinimumWidth(440)
        self._build_ui()
        if self._is_edit:
            self._populate_fields()
        self._on_priv_changed(self._priv_combo.currentIndex())

    def _build_ui(self):
        vbox = QVBoxLayout(self)

        group = QGroupBox(_("Execution Profile"))
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignRight)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText(_("e.g. As www-data in /var/www"))
        form.addRow(_("Profile name"), self._name_edit)

        self._priv_combo = QComboBox()
        self._priv_values = ["", "root", "__other__"]
        for label in [_("Current user (no sudo)"), _("Root (sudo)"), _("Other user…")]:
            self._priv_combo.addItem(label)
        self._priv_combo.currentIndexChanged.connect(self._on_priv_changed)
        form.addRow(_("Run as"), self._priv_combo)

        self._run_as_user_edit = QLineEdit()
        self._run_as_user_edit.setPlaceholderText("www-data, postgres, …")
        self._run_as_user_edit.setVisible(False)
        form.addRow(_("Username"), self._run_as_user_edit)

        self._working_dir_edit = QLineEdit()
        self._working_dir_edit.setToolTip(
            _("cd into this directory before running the command.\n"
              "Leave empty to use the default working directory.")
        )
        form.addRow(_("Working directory"), self._working_dir_edit)

        self._description_edit = QLineEdit()
        form.addRow(_("Description"), self._description_edit)

        vbox.addWidget(group)

        # Sudo password (only when running as root / other user)
        self._sudo_group = QGroupBox(_("Sudo Password"))
        sudo_form = QFormLayout(self._sudo_group)
        sudo_form.setLabelAlignment(Qt.AlignRight)

        self._pwd_edit = QLineEdit()
        self._pwd_edit.setEchoMode(QLineEdit.Password)
        self._pwd_edit.setToolTip(
            _("Stored locally, encoded with a machine-specific key.\n"
              "Leave empty to keep the existing password.")
        )
        sudo_form.addRow(_("Sudo password"), self._pwd_edit)

        self._stored_widget = QWidget()
        stored_row = QHBoxLayout(self._stored_widget)
        stored_row.setContentsMargins(0, 0, 0, 0)
        stored_lbl = QLabel(_("A password is stored. Type a new one to replace it."))
        clear_btn = QPushButton(_("Clear"))
        clear_btn.clicked.connect(self._on_clear_password)
        stored_row.addWidget(stored_lbl, 1)
        stored_row.addWidget(clear_btn)
        sudo_form.addRow("", self._stored_widget)
        self._stored_widget.setVisible(False)

        vbox.addWidget(self._sudo_group)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        vbox.addWidget(buttons)

    def _populate_fields(self):
        p = self._profile
        self._name_edit.setText(p.name)
        if p.run_as_user == "root":
            self._priv_combo.setCurrentIndex(1)
        elif p.run_as_user:
            self._priv_combo.setCurrentIndex(2)
            self._run_as_user_edit.setText(p.run_as_user)
        self._working_dir_edit.setText(p.working_dir or "")
        self._description_edit.setText(p.description or "")
        if p.has_sudo_password:
            self._stored_widget.setVisible(True)

    def _on_priv_changed(self, idx: int):
        val = self._priv_values[idx]
        self._run_as_user_edit.setVisible(val == "__other__")
        is_sudo = val in ("root", "__other__")
        self._sudo_group.setVisible(is_sudo)
        if not is_sudo:
            self._stored_widget.setVisible(False)

    def _on_clear_password(self):
        if self._profile:
            self._profile.set_sudo_password("")
            self._config.update_profile(self._profile)
        self._stored_widget.setVisible(False)
        self._pwd_edit.clear()

    def _resolve_run_as_user(self) -> str:
        val = self._priv_values[self._priv_combo.currentIndex()]
        if val == "root":
            return "root"
        if val == "__other__":
            return self._run_as_user_edit.text().strip()
        return ""

    def _on_save(self):
        name = self._name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, _("Incomplete"), _("A profile name is required."))
            return

        run_as = self._resolve_run_as_user()
        if self._is_edit and self._profile:
            profile = self._profile
            profile.name = name
            profile.run_as_user = run_as
            profile.working_dir = self._working_dir_edit.text().strip()
            profile.description = self._description_edit.text().strip()
        else:
            profile = ExecutionProfile(
                name=name,
                run_as_user=run_as,
                working_dir=self._working_dir_edit.text().strip(),
                description=self._description_edit.text().strip(),
            )

        if not profile.run_as_user:
            profile.set_sudo_password("")
        password = self._pwd_edit.text()
        if password:
            profile.set_sudo_password(password)

        if self._is_edit:
            self._config.update_profile(profile)
        else:
            self._config.add_profile(profile)
        from commandeck_qt.secret_warning import warn_if_no_keychain
        warn_if_no_keychain(self, bool(password))
        if self._on_saved:
            self._on_saved()
        self.accept()
