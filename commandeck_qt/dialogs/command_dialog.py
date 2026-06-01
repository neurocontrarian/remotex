"""Add/Edit command button dialog."""
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QCheckBox, QDialogButtonBox, QPushButton,
    QLabel, QGroupBox, QComboBox, QScrollArea,
    QWidget, QMessageBox, QListWidget, QListWidgetItem,
    QFrame, QToolButton,
)

from commandeck_core.models.config import ConfigManager
from commandeck_core.models.command_button import CommandButton
from commandeck_core.i18n import _
from commandeck_qt.button_tile import resolve_icon_pixmap, _BOOTSTRAP_DIR, _ICONS_DIR

_FALLBACK_ICON = "utilities-terminal"

# GNOME palette (40 colors)
_GNOME_PALETTE = [
    "#99c1f1", "#62a0ea", "#3584e4", "#1c71d8", "#1a5fb4",
    "#8ff0a4", "#57e389", "#33d17a", "#2ec27e", "#26a269",
    "#f9f06b", "#f8e45c", "#f6d32d", "#f5c211", "#e5a50a",
    "#ffbe6f", "#ffa348", "#ff7800", "#e66100", "#c64600",
    "#f66151", "#ed333b", "#e01b24", "#c01c28", "#a51d2d",
    "#dc8add", "#c061cb", "#9141ac", "#813d9c", "#613583",
    "#cdab8f", "#b5835a", "#986a44", "#865e3c", "#63452c",
    "#ffffff", "#deddda", "#9a9996", "#5e5c64", "#000000",
]

_icon_cache: list[str] | None = None


def _build_icon_cache() -> list[str]:
    global _icon_cache
    if _icon_cache is not None:
        return _icon_cache
    seen: set[str] = set()
    bundled: list[str] = []
    for d in (_BOOTSTRAP_DIR, _ICONS_DIR):
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith(".svg"):
                    name = f[:-4]
                    if name not in seen:
                        seen.add(name)
                        bundled.append(name)
    _icon_cache = bundled
    return _icon_cache


def show_command_dialog(config: ConfigManager,
                        command_button: CommandButton | None = None,
                        on_saved: Callable | None = None,
                        parent=None) -> bool:
    # parent=None (not `parent`): a modal dialog with a transient parent gets glued to
    # it on GNOME/Wayland ("attached modal dialogs"). Parentless → floats as its own
    # window, still modal via exec(). Same reasoning for the nested dialogs below.
    dlg = CommandDialog(config, command_button=command_button,
                        on_saved=on_saved, parent=None)
    return dlg.exec() == QDialog.Accepted


class CommandDialog(QDialog):
    def __init__(self, config: ConfigManager,
                 command_button: CommandButton | None = None,
                 on_saved: Callable | None = None,
                 parent=None):
        super().__init__(parent)
        self._config = config
        self._button = command_button
        self._on_saved = on_saved
        self._is_edit = command_button is not None
        self._machine_switches: list[tuple[str, QCheckBox]] = []

        self.setWindowTitle(_("Edit Button") if self._is_edit else _("Add Button"))
        self.setMinimumWidth(480)
        self.setMinimumHeight(520)
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

        vbox.addWidget(self._build_details_group())
        vbox.addWidget(self._build_machines_group())
        vbox.addWidget(self._build_appearance_group())
        vbox.addWidget(self._build_organisation_group())
        vbox.addWidget(self._build_behaviour_group())

        scroll.setWidget(inner)
        outer.addWidget(scroll)

        bb = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        bb.setContentsMargins(16, 8, 16, 12)
        bb.accepted.connect(self._on_save)
        bb.rejected.connect(self.reject)
        outer.addWidget(bb)

    def _build_details_group(self) -> QGroupBox:
        box = QGroupBox(_("Button"))
        form = QFormLayout(box)
        form.setLabelAlignment(Qt.AlignRight)
        self._name_edit = QLineEdit()
        self._command_edit = QLineEdit()
        form.addRow(_("Label"), self._name_edit)
        form.addRow(_("Command"), self._command_edit)
        return box

    def _build_machines_group(self) -> QGroupBox:
        box = QGroupBox(_("Target machines"))
        vbox = QVBoxLayout(box)
        desc = QLabel(
            _("Select where this command can run.\n"
              "If multiple targets are selected, you will be asked which one to use at run time.")
        )
        desc.setWordWrap(True)
        vbox.addWidget(desc)

        self._local_check = QCheckBox(_("Local (this machine)"))
        self._local_check.setChecked(True)
        vbox.addWidget(self._local_check)

        machines = self._config.load_machines()
        if machines:
            self._all_check = QCheckBox(_("All machines"))
            self._all_check.toggled.connect(self._on_all_toggled)
            self._local_check.toggled.connect(self._on_individual_toggled)
            vbox.addWidget(self._all_check)

            for m in machines:
                cb = QCheckBox(f"{m.name}  –  {m.user}@{m.host}:{m.port}")
                cb.toggled.connect(self._on_individual_toggled)
                vbox.addWidget(cb)
                self._machine_switches.append((m.id, cb))
        else:
            self._all_check = None
            hint = QLabel(_("No remote machines configured. Add machines via menu → Manage Machines."))
            hint.setWordWrap(True)
            vbox.addWidget(hint)
        return box

    def _on_all_toggled(self, checked: bool):
        self._local_check.blockSignals(True)
        self._local_check.setChecked(checked)
        self._local_check.blockSignals(False)
        for _, cb in self._machine_switches:
            cb.blockSignals(True)
            cb.setChecked(checked)
            cb.blockSignals(False)

    def _on_individual_toggled(self):
        if self._all_check is None:
            return
        all_checks = [self._local_check] + [cb for _, cb in self._machine_switches]
        all_on = all(cb.isChecked() for cb in all_checks)
        self._all_check.blockSignals(True)
        self._all_check.setChecked(all_on)
        self._all_check.blockSignals(False)

    def _build_appearance_group(self) -> QGroupBox:
        box = QGroupBox(_("Appearance"))
        form = QFormLayout(box)
        form.setLabelAlignment(Qt.AlignRight)

        # Icon row
        icon_row = QHBoxLayout()
        self._icon_preview = QLabel()
        self._icon_preview.setFixedSize(24, 24)
        self._icon_edit = QLineEdit()
        self._icon_edit.setPlaceholderText(_FALLBACK_ICON)
        self._icon_edit.textChanged.connect(self._on_icon_changed)
        browse_btn = QPushButton(_("Browse"))
        browse_btn.setFixedWidth(72)
        browse_btn.clicked.connect(self._on_browse_icon)
        icon_row.addWidget(self._icon_preview)
        icon_row.addWidget(self._icon_edit, 1)
        icon_row.addWidget(browse_btn)
        form.addRow(_("Icon"), icon_row)

        # Background color
        bg_row, self._bg_color_edit = self._build_color_row()
        form.addRow(_("Background color"), bg_row)

        # Text color
        txt_row, self._text_color_edit = self._build_color_row()
        form.addRow(_("Text color"), txt_row)

        self._hide_label_check = QCheckBox(_("Hide label (icon only)"))
        form.addRow("", self._hide_label_check)
        self._hide_icon_check = QCheckBox(_("Hide icon (text only)"))
        form.addRow("", self._hide_icon_check)
        return box

    def _build_color_row(self):
        row = QHBoxLayout()
        row.setSpacing(4)
        self_swatch = QLabel()
        self_swatch.setFixedSize(24, 24)
        self_swatch.setStyleSheet("background: rgba(128,128,128,0.2); border-radius: 4px;")
        entry = QLineEdit()
        entry.setPlaceholderText("#rrggbb")
        entry.setFixedWidth(90)
        clear_btn = QToolButton()
        clear_btn.setText("✕")
        clear_btn.setToolTip(_("Clear color"))
        pick_btn = QPushButton(_("…"))
        pick_btn.setFixedWidth(32)
        pick_btn.setToolTip(_("Open color palette"))

        def update_swatch(color_str: str):
            if color_str and color_str.startswith("#") and len(color_str) == 7:
                c = QColor(color_str)
                if c.isValid():
                    self_swatch.setStyleSheet(
                        f"background: {color_str}; border-radius: 4px;"
                    )
                    return
            self_swatch.setStyleSheet("background: rgba(128,128,128,0.2); border-radius: 4px;")

        entry.textChanged.connect(update_swatch)
        clear_btn.clicked.connect(lambda: entry.setText(""))
        pick_btn.clicked.connect(lambda: self._show_color_picker(entry))

        row.addWidget(self_swatch)
        row.addWidget(entry)
        row.addWidget(clear_btn)
        row.addWidget(pick_btn)
        return row, entry

    def _show_color_picker(self, hex_entry: QLineEdit):
        from PySide6.QtWidgets import QColorDialog
        initial = QColor(hex_entry.text()) if hex_entry.text() else QColor(Qt.white)
        color = QColorDialog.getColor(initial, self, _("Pick a color"))
        if color.isValid():
            hex_entry.setText(color.name().upper())

    def _build_organisation_group(self) -> QGroupBox:
        box = QGroupBox(_("Organisation"))
        form = QFormLayout(box)
        form.setLabelAlignment(Qt.AlignRight)
        self._category_edit = QLineEdit()
        form.addRow(_("Category"), self._category_edit)
        return box

    def _build_behaviour_group(self) -> QGroupBox:
        box = QGroupBox(_("Behaviour"))
        form = QFormLayout(box)
        form.setLabelAlignment(Qt.AlignRight)

        self._tooltip_edit = QLineEdit()
        self._tooltip_edit.setToolTip(
            _("Text shown when hovering. Leave empty to show the command.")
        )
        form.addRow(_("Tooltip"), self._tooltip_edit)

        self._confirm_check = QCheckBox(_("Confirm before running"))
        form.addRow("", self._confirm_check)

        self._exec_mode_combo = QComboBox()
        self._exec_mode_values = ["silent", "output", "terminal"]
        for label in [_("Silent (toast only)"), _("Show output"), _("Open in terminal")]:
            self._exec_mode_combo.addItem(label)
        form.addRow(_("Execution mode"), self._exec_mode_combo)

        # Execution profile (Pro) — reusable run-as + working-dir
        try:
            from commandeck_core.pro.license import is_pro_active
            _pro = is_pro_active()
        except ImportError:
            _pro = False
        self._profile_combo = QComboBox()
        self._profile_id_values = [""]
        self._profile_combo.addItem(_("None (use button settings)"))
        if _pro:
            for p in sorted(self._config.load_profiles(), key=lambda p: p.name):
                self._profile_combo.addItem(p.name)
                self._profile_id_values.append(p.id)
            self._profile_combo.currentIndexChanged.connect(self._on_profile_changed)
        else:
            self._profile_combo.setEnabled(False)
            self._profile_combo.setToolTip(
                _("Pro feature — upgrade to use execution profiles"))
        form.addRow(_("Execution profile"), self._profile_combo)

        # Run as (privileges)
        self._priv_combo = QComboBox()
        self._priv_values = ["", "root", "__other__"]
        for label in [_("Current user"), _("Root (sudo)"), _("Other user…")]:
            self._priv_combo.addItem(label)
        self._priv_combo.currentIndexChanged.connect(self._on_priv_changed)
        form.addRow(_("Run as"), self._priv_combo)

        self._run_as_user_edit = QLineEdit()
        self._run_as_user_edit.setPlaceholderText("www-data, postgres, …")
        self._run_as_user_edit.setVisible(False)
        form.addRow(_("Username"), self._run_as_user_edit)

        self._sudo_pwd_edit = QLineEdit()
        self._sudo_pwd_edit.setEchoMode(QLineEdit.Password)
        self._sudo_pwd_edit.setPlaceholderText(_("Sudo password (stored locally)"))
        self._sudo_pwd_edit.setVisible(False)
        form.addRow(_("Sudo password"), self._sudo_pwd_edit)

        try:
            from commandeck_core.pro.license import is_pro_active
            pro = is_pro_active()
        except ImportError:
            pro = False

        self._mcp_check = QCheckBox(_("Allow AI to run this button"))
        if not pro:
            self._mcp_check.setEnabled(False)
            self._mcp_check.setToolTip(_("Pro feature — upgrade to enable MCP execution"))
        form.addRow("", self._mcp_check)

        return box

    def _on_priv_changed(self, idx: int):
        val = self._priv_values[idx]
        self._run_as_user_edit.setVisible(val == "__other__")
        has_sudo = val in ("root", "__other__")
        self._sudo_pwd_edit.setVisible(has_sudo)

    def _on_profile_changed(self, idx: int):
        # When a profile is selected, the button's own run-as settings are ignored.
        has_profile = self._profile_id_values[idx] != ""
        for w in (self._priv_combo, self._run_as_user_edit, self._sudo_pwd_edit):
            w.setEnabled(not has_profile)

    def _on_icon_changed(self, text: str):
        icon_name = text.strip() or _FALLBACK_ICON
        px = resolve_icon_pixmap(icon_name, 24)
        if px:
            self._icon_preview.setPixmap(px.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self._icon_preview.clear()

    def _on_browse_icon(self):
        icons = _build_icon_cache()
        if not icons:
            QMessageBox.information(self, _("Icon picker"),
                                    _("No bundled icons found. Type the icon name manually."))
            return
        dlg = _IconPickerDialog(icons, None)   # parentless → floats (not glued on GNOME)
        if dlg.exec() == QDialog.Accepted and dlg.selected_icon:
            self._icon_edit.setText(dlg.selected_icon)

    def _populate_fields(self):
        if not self._button:
            self._confirm_check.setChecked(True)
            self._exec_mode_combo.setCurrentIndex(1)  # default: "output"
            return
        btn = self._button
        self._name_edit.setText(btn.name)
        self._command_edit.setText(btn.command)

        machine_ids_set = set(btn.machine_ids)
        self._local_check.setChecked("" in machine_ids_set or not machine_ids_set)
        for mid, cb in self._machine_switches:
            cb.setChecked(mid in machine_ids_set)
        self._on_individual_toggled()

        icon = btn.icon_name or _FALLBACK_ICON
        self._icon_edit.setText(icon)
        self._on_icon_changed(icon)

        self._bg_color_edit.setText(btn.color or "")
        self._text_color_edit.setText(btn.text_color or "")
        self._hide_label_check.setChecked(btn.hide_label)
        self._hide_icon_check.setChecked(btn.hide_icon)
        self._category_edit.setText(btn.category or "")
        self._tooltip_edit.setText(btn.tooltip or "")
        self._confirm_check.setChecked(btn.confirm_before_run)
        self._mcp_check.setChecked(btn.mcp_executable)

        mode = btn.execution_mode or ("output" if btn.show_output else "silent")
        idx = self._exec_mode_values.index(mode) if mode in self._exec_mode_values else 0
        self._exec_mode_combo.setCurrentIndex(idx)

        run_as = btn.run_as_user or ""
        if run_as == "root":
            self._priv_combo.setCurrentIndex(1)
        elif run_as:
            self._priv_combo.setCurrentIndex(2)
            self._run_as_user_edit.setText(run_as)
        self._on_priv_changed(self._priv_combo.currentIndex())
        if btn.has_sudo_password:
            # The field stays empty (secrets are never shown), so signal that one
            # is already stored — empty on save keeps it.
            self._sudo_pwd_edit.setPlaceholderText(
                _("•••• already saved — leave empty to keep it"))

        if btn.profile_id and btn.profile_id in self._profile_id_values:
            self._profile_combo.setCurrentIndex(
                self._profile_id_values.index(btn.profile_id))
            self._on_profile_changed(self._profile_combo.currentIndex())

    def _resolve_run_as_user(self) -> str:
        val = self._priv_values[self._priv_combo.currentIndex()]
        if val == "root":
            return "root"
        if val == "__other__":
            return self._run_as_user_edit.text().strip()
        return ""

    def _selected_profile_id(self) -> str:
        return self._profile_id_values[self._profile_combo.currentIndex()]

    def _build_button_from_fields(self) -> CommandButton | None:
        name = self._name_edit.text().strip()
        command = self._command_edit.text().strip()
        if not name or not command:
            return None

        machine_ids: list[str] = []
        if self._local_check.isChecked():
            machine_ids.append("")
        for mid, cb in self._machine_switches:
            if cb.isChecked():
                machine_ids.append(mid)
        # [] means local-only (no remote override needed)
        if machine_ids == [""]:
            machine_ids = []

        icon_name = self._icon_edit.text().strip() or _FALLBACK_ICON
        color = self._bg_color_edit.text().strip()
        text_color = self._text_color_edit.text().strip()
        exec_mode = self._exec_mode_values[self._exec_mode_combo.currentIndex()]

        if self._is_edit and self._button:
            b = self._button
            b.name = name
            b.command = command
            b.machine_ids = machine_ids
            b.icon_name = icon_name
            b.color = color
            b.text_color = text_color
            b.hide_label = self._hide_label_check.isChecked()
            b.hide_icon = self._hide_icon_check.isChecked()
            b.category = self._category_edit.text().strip()
            b.tooltip = self._tooltip_edit.text().strip()
            b.confirm_before_run = self._confirm_check.isChecked()
            b.mcp_executable = self._mcp_check.isChecked()
            b.execution_mode = exec_mode
            b.show_output = (exec_mode == "output")
            b.profile_id = self._selected_profile_id()
            if b.profile_id:
                # The profile governs run-as user + sudo password; clear the button's own
                # so the executor doesn't shadow the profile with stale button values.
                b.run_as_user = ""
                b.set_sudo_password("")
            else:
                b.run_as_user = self._resolve_run_as_user()
                pwd = self._sudo_pwd_edit.text()
                if pwd:
                    b.set_sudo_password(pwd)
            return b
        else:
            buttons = self._config.load_buttons()
            profile_id = self._selected_profile_id()
            btn = CommandButton(
                id=str(uuid.uuid4()),
                name=name,
                command=command,
                machine_ids=machine_ids,
                icon_name=icon_name,
                color=color,
                text_color=text_color,
                hide_label=self._hide_label_check.isChecked(),
                hide_icon=self._hide_icon_check.isChecked(),
                category=self._category_edit.text().strip(),
                tooltip=self._tooltip_edit.text().strip(),
                confirm_before_run=self._confirm_check.isChecked(),
                mcp_executable=self._mcp_check.isChecked(),
                execution_mode=exec_mode,
                show_output=(exec_mode == "output"),
                run_as_user="" if profile_id else self._resolve_run_as_user(),
                profile_id=profile_id,
                position=max((b.position for b in buttons), default=0) + 1,
            )
            if not profile_id:
                pwd = self._sudo_pwd_edit.text()
                if pwd:
                    btn.set_sudo_password(pwd)
            return btn

    def _on_save(self):
        button = self._build_button_from_fields()
        if button is None:
            QMessageBox.warning(self, _("Incomplete"),
                                _("Label and Command are required."))
            return
        if self._is_edit:
            self._config.update_button(button)
        else:
            self._config.add_button(button)
        from commandeck_qt.secret_warning import warn_if_no_keychain
        warn_if_no_keychain(
            self, bool(self._sudo_pwd_edit.text()) and not self._selected_profile_id())
        if self._on_saved:
            self._on_saved()
        self.accept()


class _IconPickerDialog(QDialog):
    def __init__(self, icons: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Pick an icon"))
        self.setMinimumSize(360, 440)
        self.selected_icon: str = ""
        self._all_icons = icons
        self._build_ui()

    def _build_ui(self):
        vbox = QVBoxLayout(self)
        self._search = QLineEdit()
        self._search.setPlaceholderText(f"Search {len(self._all_icons)} icons…")
        self._search.textChanged.connect(self._on_search)
        vbox.addWidget(self._search)

        self._list = QListWidget()
        self._list.setViewMode(QListWidget.IconMode)
        self._list.setIconSize(QSize(32, 32))
        self._list.setResizeMode(QListWidget.Adjust)
        self._list.setSpacing(4)
        self._list.setUniformItemSizes(True)
        self._list.itemDoubleClicked.connect(self._on_pick)
        vbox.addWidget(self._list, 1)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self._on_accept)
        bb.rejected.connect(self.reject)
        vbox.addWidget(bb)

        self._populate(self._all_icons)

    def _populate(self, icons: list[str]):
        self._list.clear()
        for name in icons:
            item = QListWidgetItem(name)
            item.setToolTip(name)
            px = resolve_icon_pixmap(name, 32)
            if px:
                item.setIcon(QIcon(px))
            self._list.addItem(item)

    def _on_search(self, text: str):
        q = text.lower()
        filtered = [n for n in self._all_icons if q in n.lower()] if q else self._all_icons
        self._populate(filtered)

    def _on_pick(self, item: QListWidgetItem):
        self.selected_icon = item.text()
        self.accept()

    def _on_accept(self):
        item = self._list.currentItem()
        if item:
            self.selected_icon = item.text()
        self.accept()
