"""Add/Edit machine dialog."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QButtonGroup
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QDialogButtonBox, QComboBox,
    QPushButton, QLabel, QHBoxLayout,
    QGroupBox, QToolButton, QScrollArea,
    QWidget, QSizePolicy, QMessageBox, QFrame,
)

from commandeck_core.models.config import ConfigManager
from commandeck_core.pro.models.machine import Machine
from commandeck_core.utils.threading import run_in_thread
from commandeck_core.i18n import _
from commandeck_qt.button_tile import resolve_icon_pixmap, _BOOTSTRAP_DIR


_MACHINE_ICONS = [
    ("pc-display",            "Desktop"),
    ("pc-display-horizontal", "Desktop wide"),
    ("laptop",                "Laptop"),
    ("server",                "Server"),
    ("router",                "Router"),
    ("wifi",                  "Wi-Fi"),
    ("ethernet",              "Network"),
    ("terminal",              "Terminal"),
]


def _load_machine_icon(icon_id: str, size: int) -> QPixmap | None:
    svg = os.path.join(_BOOTSTRAP_DIR, f"{icon_id}.svg")
    if os.path.isfile(svg):
        return resolve_icon_pixmap(icon_id, size)
    return None


def show_machine_dialog(config: ConfigManager, machine: Machine | None = None,
                        on_saved: Callable | None = None, parent=None) -> None:
    dlg = MachineDialog(config, machine=machine, on_saved=on_saved, parent=parent)
    dlg.exec()


class MachineDialog(QDialog):
    def __init__(self, config: ConfigManager, machine: Machine | None = None,
                 on_saved: Callable | None = None, parent=None):
        super().__init__(parent)
        self._config = config
        self._machine = machine
        self._on_saved = on_saved
        self._is_edit = machine is not None
        self._icon_name = machine.icon_name if machine and machine.icon_name else "pc-display"
        self._icon_group = QButtonGroup(self)
        self._icon_group.setExclusive(True)

        self.setWindowTitle(_("Edit Machine") if self._is_edit else _("Add Machine"))
        self.setMinimumWidth(480)
        self._build_ui()
        self._populate_fields()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        inner = QWidget()
        vbox = QVBoxLayout(inner)
        vbox.setContentsMargins(16, 16, 16, 16)
        vbox.setSpacing(16)

        vbox.addWidget(self._build_connection_group())
        vbox.addWidget(self._build_icon_group_widget())
        vbox.addWidget(self._build_test_group())
        self._key_setup_box = self._build_ssh_key_group()
        vbox.addWidget(self._key_setup_box)

        scroll.setWidget(inner)
        outer.addWidget(scroll)

        bb = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        bb.setContentsMargins(16, 8, 16, 12)
        bb.accepted.connect(self._on_save)
        bb.rejected.connect(self.reject)
        outer.addWidget(bb)
        # Apply the initial auth-mode enable/visibility state.
        self._on_auth_changed(self._auth_combo.currentIndex())

    def _build_connection_group(self) -> QGroupBox:
        box = QGroupBox(_("Connection"))
        form = QFormLayout(box)
        form.setLabelAlignment(Qt.AlignRight)

        self._name_edit = QLineEdit()
        self._host_edit = QLineEdit()
        self._user_edit = QLineEdit()
        self._port_spin = QSpinBox()
        self._port_spin.setRange(1, 65535)
        self._port_spin.setValue(22)
        self._key_edit = QLineEdit(str(Path.home() / ".ssh" / "id_ed25519"))
        # Auth method selector — SSH key OR password (the keychain-stored password,
        # not the one-time copy-key password). Choosing one hides/ignores the other,
        # and password mode forces password-only auth (no key/agent fallback) so a
        # test actually validates the password.
        self._auth_combo = QComboBox()
        self._auth_combo.addItems([_("SSH Key"), _("Password")])
        self._auth_combo.currentIndexChanged.connect(self._on_auth_changed)
        # Stored SSH password. Kept in the OS keychain via secret_store — never in
        # machines.toml or a backup.
        self._auth_pwd_edit = QLineEdit()
        self._auth_pwd_edit.setEchoMode(QLineEdit.Password)
        self._auth_pwd_edit.setPlaceholderText(
            _("Connect with a password (stored in your keychain)"))
        self._group_edit = QLineEdit()
        self._group_edit.setToolTip(
            _("Optional group name (e.g. 'Production', 'Home').\n"
              "Machines in the same group can be targeted together.")
        )

        form.addRow(_("Name"), self._name_edit)
        form.addRow(_("Host / IP"), self._host_edit)
        form.addRow(_("SSH User"), self._user_edit)
        form.addRow(_("Port"), self._port_spin)
        form.addRow(_("Authentication"), self._auth_combo)
        form.addRow(_("SSH Key Path"), self._key_edit)
        form.addRow(_("SSH Password"), self._auth_pwd_edit)
        form.addRow(_("Group"), self._group_edit)
        return box

    def _on_auth_changed(self, idx: int) -> None:
        key_mode = idx == 0
        self._key_edit.setEnabled(key_mode)
        self._auth_pwd_edit.setEnabled(not key_mode)
        if hasattr(self, "_key_setup_box"):
            self._key_setup_box.setVisible(key_mode)

    def _build_icon_group_widget(self) -> QGroupBox:
        box = QGroupBox(_("Appearance"))
        vbox = QVBoxLayout(box)
        vbox.setContentsMargins(8, 8, 8, 8)

        lbl = QLabel(_("Icon"))
        vbox.addWidget(lbl)

        flow = QHBoxLayout()
        flow.setSpacing(4)
        self._icon_btns: list[tuple[str, QToolButton]] = []
        for icon_id, label in _MACHINE_ICONS:
            btn = QToolButton()
            btn.setToolTip(label)
            btn.setCheckable(True)
            btn.setAutoRaise(True)
            btn.setFixedSize(36, 36)
            px = _load_machine_icon(icon_id, 22)
            if px:
                from PySide6.QtGui import QIcon
                btn.setIcon(QIcon(px))
                btn.setIconSize(px.size())
            else:
                btn.setText(label[:3])
            self._icon_group.addButton(btn)
            flow.addWidget(btn)
            self._icon_btns.append((icon_id, btn))
            btn.clicked.connect(lambda checked, iid=icon_id: self._on_icon_selected(iid))

        flow.addStretch()
        vbox.addLayout(flow)
        return box

    def _on_icon_selected(self, icon_id: str):
        self._icon_name = icon_id
        for iid, btn in self._icon_btns:
            btn.blockSignals(True)
            btn.setChecked(iid == icon_id)
            btn.blockSignals(False)

    def _build_test_group(self) -> QGroupBox:
        box = QGroupBox(_("Test Connection"))
        hbox = QHBoxLayout(box)
        self._test_btn = QPushButton(_("Test"))
        self._test_btn.setFixedWidth(80)
        self._test_btn.clicked.connect(self._on_test)
        self._test_label = QLabel("")
        self._test_label.setWordWrap(True)
        hbox.addWidget(self._test_btn)
        hbox.addWidget(self._test_label, 1)
        return box

    def _build_ssh_key_group(self) -> QGroupBox:
        box = QGroupBox(_("SSH Key Setup"))
        vbox = QVBoxLayout(box)

        self._key_status_lbl = QLabel("")
        vbox.addWidget(self._key_status_lbl)

        self._gen_btn = QPushButton(_("Generate SSH key pair"))
        self._gen_btn.clicked.connect(self._on_generate_key)
        vbox.addWidget(self._gen_btn)

        vbox.addWidget(QLabel(_("Remote Password (used once, never stored):")))
        self._pwd_edit = QLineEdit()
        self._pwd_edit.setEchoMode(QLineEdit.Password)
        self._pwd_edit.setPlaceholderText(_("Remote user's password"))
        vbox.addWidget(self._pwd_edit)

        self._copy_btn = QPushButton(_("Copy Key to Machine"))
        self._copy_btn.clicked.connect(self._on_copy_key)
        vbox.addWidget(self._copy_btn)

        self._copy_label = QLabel("")
        self._copy_label.setWordWrap(True)
        vbox.addWidget(self._copy_label)

        self._refresh_key_status()
        return box

    def _populate_fields(self):
        if not self._machine:
            return
        self._name_edit.setText(self._machine.name)
        self._host_edit.setText(self._machine.host)
        self._user_edit.setText(self._machine.user)
        self._port_spin.setValue(self._machine.port)
        if self._machine.identity_file:
            self._key_edit.setText(self._machine.identity_file)
        if self._machine.group:
            self._group_edit.setText(self._machine.group)
        # Password mode = a stored password and no key; otherwise key mode.
        if self._machine.has_password and not self._machine.identity_file:
            self._auth_combo.setCurrentIndex(1)
            self._auth_pwd_edit.setPlaceholderText(
                _("•••• already saved — leave empty to keep it"))
        else:
            self._auth_combo.setCurrentIndex(0)
        # Set icon button
        for iid, btn in self._icon_btns:
            btn.blockSignals(True)
            btn.setChecked(iid == self._icon_name)
            btn.blockSignals(False)

    def _refresh_key_status(self):
        try:
            from commandeck_core.pro.services.ssh_key_service import SSHKeyService
            svc = SSHKeyService()
            keys = svc.find_existing_keys()
            if keys:
                names = ", ".join(k.name for k in keys)
                self._key_status_lbl.setText(f"✓  {names}")
                self._gen_btn.setVisible(False)
                self._key_edit.setText(str(svc.preferred_key()))
            else:
                self._key_status_lbl.setText(_("No SSH key found — generate one first"))
                self._gen_btn.setVisible(True)
        except Exception:
            self._key_status_lbl.setText(_("SSH key service unavailable"))

    def _build_machine_from_fields(self, for_test: bool = False) -> Machine | None:
        name = self._name_edit.text().strip()
        host = self._host_edit.text().strip()
        user = self._user_edit.text().strip()
        if not name or not host or not user:
            return None
        port = self._port_spin.value()
        group = self._group_edit.text().strip()
        key_mode = self._auth_combo.currentIndex() == 0
        key = self._key_edit.text().strip() if key_mode else ""
        # For a test, always use a throwaway Machine (has_password False) so a
        # previously-stored secret can't shadow the method being tested.
        if for_test or not (self._is_edit and self._machine):
            machine = Machine(name=name, host=host, user=user, port=port,
                              identity_file=key, icon_name=self._icon_name, group=group)
        else:
            m = self._machine
            m.name, m.host, m.user, m.port = name, host, user, port
            m.identity_file = key
            m.icon_name, m.group = self._icon_name, group
            machine = m
        # Transient password (used by Test, and for a fresh new machine) — the
        # keychain write happens only in _on_save. Empty in key mode → key-only.
        if key_mode:
            machine._pending_password = ""
        else:
            pending = self._auth_pwd_edit.text()
            # On Test in edit mode with an empty field, test the STORED password
            # (not nothing — otherwise SSH would fall back to a key and the test
            # would lie). Empty everywhere → "" (caller refuses to test).
            if for_test and not pending and self._is_edit and self._machine:
                pending = self._machine.get_password()
            machine._pending_password = pending
        return machine

    def _on_save(self):
        machine = self._build_machine_from_fields()
        if machine is None:
            QMessageBox.warning(self, _("Incomplete"), _("Name, Host and User are required."))
            return
        key_mode = self._auth_combo.currentIndex() == 0
        typed_pwd = self._auth_pwd_edit.text()
        if key_mode:
            machine.set_password("")          # key auth chosen → drop any stored password
        elif typed_pwd:
            machine.set_password(typed_pwd)    # password mode, new password → store it
        # password mode + empty field → keep the already-stored password
        if self._is_edit:
            self._config.update_machine(machine)
        else:
            self._config.add_machine(machine)
        from commandeck_qt.secret_warning import warn_if_no_keychain
        warn_if_no_keychain(self, bool(typed_pwd) and not key_mode)
        if self._on_saved:
            self._on_saved()
        self.accept()

    def _on_test(self):
        machine = self._build_machine_from_fields(for_test=True)
        if machine is None:
            self._test_label.setText(_("Fill in Name, Host and User first."))
            return
        if self._auth_combo.currentIndex() == 1 and not machine.get_password():
            self._test_label.setText(_("Enter a password to test."))
            return
        self._test_btn.setEnabled(False)
        self._test_label.setText(_("Testing…"))
        try:
            from commandeck_core.pro.services.executor_pro import CommandExecutorPro
        except ImportError:
            # Free build (no Pro/SSH stack) — the free CommandExecutor has no
            # test_connection, so report instead of crashing the Qt slot.
            self._test_btn.setEnabled(True)
            self._test_label.setText(_("SSH connection testing requires Commandeck Pro."))
            return
        executor = CommandExecutorPro(self._config)
        executor.test_connection(machine, self._on_test_result)

    def _on_test_result(self, success: bool, message: str):
        self._test_btn.setEnabled(True)
        icon = "✓" if success else "✗"
        self._test_label.setText(f"{icon}  {message}")

    def _on_generate_key(self):
        try:
            from commandeck_core.pro.services.ssh_key_service import SSHKeyService
            svc = SSHKeyService()
            self._gen_btn.setEnabled(False)
            ok, msg, _ = svc.generate_key()
            self._gen_btn.setEnabled(True)
            self._copy_label.setText(f"{'✓' if ok else '✗'}  {msg}")
            self._refresh_key_status()
        except Exception as e:
            self._gen_btn.setEnabled(True)
            self._copy_label.setText(str(e))

    def _on_copy_key(self):
        machine = self._build_machine_from_fields()
        if machine is None:
            self._copy_label.setText(_("Fill in Host and User first."))
            return
        password = self._pwd_edit.text()
        if not password:
            self._copy_label.setText(_("Enter the remote user's password."))
            return
        try:
            from commandeck_core.pro.services.ssh_key_service import SSHKeyService
            svc = SSHKeyService()
            key = svc.preferred_key()
            if key is None:
                self._copy_label.setText(_("No SSH key found. Generate one first."))
                return
            self._copy_btn.setEnabled(False)
            self._pending_copy = (machine, password, key)
            if svc.is_host_known(machine):
                self._do_copy()
            else:
                # First contact: verify the host fingerprint in-app (TOFU) so
                # the user never has to run `ssh` in a terminal beforehand.
                self._copy_label.setText(_("Verifying host identity…"))
                run_in_thread(svc.scan_host_key, self._on_host_key_scanned, machine)
        except Exception as e:
            self._copy_btn.setEnabled(True)
            self._copy_label.setText(str(e))

    def _on_host_key_scanned(self, result):
        from commandeck_core.pro.services.ssh_key_service import SSHKeyService
        if isinstance(result, Exception):
            self._copy_btn.setEnabled(True)
            self._copy_label.setText(f"✗  {result}")
            return
        ok, info, host_key = result
        if not ok:
            self._copy_btn.setEnabled(True)
            self._copy_label.setText(f"✗  {info}")
            return
        machine, _password, _key = self._pending_copy
        answer = QMessageBox.question(
            self,
            _("Verify host identity"),
            _("The authenticity of host '{host}' can't be established.\n\n"
              "Fingerprint:\n{fp}\n\n"
              "Only continue if you recognise this host. Add it to known "
              "hosts and copy the key?").format(host=machine.host, fp=info),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            self._copy_btn.setEnabled(True)
            self._copy_label.setText(_("Cancelled — host not verified."))
            return
        try:
            SSHKeyService().add_host_key(machine, host_key)
        except Exception as e:
            self._copy_btn.setEnabled(True)
            self._copy_label.setText(f"✗  {e}")
            return
        self._do_copy()

    def _do_copy(self):
        from commandeck_core.pro.services.ssh_key_service import SSHKeyService
        machine, password, key = self._pending_copy
        self._copy_label.setText(_("Copying key…"))
        run_in_thread(
            SSHKeyService().copy_key_to_machine,
            self._on_copy_result,
            machine, password, key,
        )

    def _on_copy_result(self, result):
        if isinstance(result, Exception):
            self._copy_btn.setEnabled(True)
            self._copy_label.setText(f"✗  {result}")
            return
        success, message = result
        self._copy_btn.setEnabled(True)
        self._pwd_edit.clear()
        icon = "✓" if success else "✗"
        self._copy_label.setText(f"{icon}  {message}")
        if success:
            self._refresh_key_status()
