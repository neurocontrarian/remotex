"""Manage machines list dialog."""
from __future__ import annotations

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton,
    QLabel, QMessageBox, QStackedWidget,
    QWidget, QToolBar,
)

from commandeck_core.models.config import ConfigManager
from commandeck_core.i18n import _
from commandeck_qt.button_tile import resolve_icon_pixmap, _BOOTSTRAP_DIR


def _machine_icon(icon_id: str) -> QIcon | None:
    if not icon_id:
        icon_id = "pc-display"
    px = resolve_icon_pixmap(icon_id, 24)
    return QIcon(px) if px else None


def show_machines_list_dialog(config: ConfigManager, parent=None) -> None:
    # parent=None: a modal dialog with a transient parent is glued to it on
    # GNOME/Wayland. Parentless → floats as its own window, still modal.
    dlg = MachinesListDialog(config, parent=None)
    dlg.exec()


class MachinesListDialog(QDialog):
    def __init__(self, config: ConfigManager, parent=None):
        super().__init__(parent)
        self._config = config
        self.setWindowTitle(_("Manage Machines"))
        self.setMinimumSize(480, 420)
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        # Toolbar
        tb = QToolBar()
        tb.setMovable(False)
        add_action = tb.addAction(_("Add Machine"))
        add_action.triggered.connect(self._on_add)
        vbox.addWidget(tb)

        self._stack = QStackedWidget()

        # Empty state
        empty = QWidget()
        ev = QVBoxLayout(empty)
        ev.setAlignment(Qt.AlignCenter)
        empty_lbl = QLabel(_("No machines configured yet.\nClick 'Add Machine' to add one."))
        empty_lbl.setAlignment(Qt.AlignCenter)
        ev.addWidget(empty_lbl)
        self._stack.addWidget(empty)   # index 0

        # List
        list_widget = QWidget()
        lv = QVBoxLayout(list_widget)
        lv.setContentsMargins(12, 12, 12, 12)
        self._list = QListWidget()
        self._list.setSelectionMode(QListWidget.SingleSelection)
        lv.addWidget(self._list)

        btn_row = QHBoxLayout()
        self._edit_btn = QPushButton(_("Edit"))
        self._edit_btn.clicked.connect(self._on_edit)
        self._delete_btn = QPushButton(_("Delete"))
        self._delete_btn.clicked.connect(self._on_delete)
        btn_row.addStretch()
        btn_row.addWidget(self._edit_btn)
        btn_row.addWidget(self._delete_btn)
        lv.addLayout(btn_row)

        self._stack.addWidget(list_widget)  # index 1
        vbox.addWidget(self._stack, 1)

    def _refresh(self):
        self._list.clear()
        machines = self._config.load_machines()
        if not machines:
            self._stack.setCurrentIndex(0)
            return
        self._stack.setCurrentIndex(1)
        machines_sorted = sorted(machines, key=lambda m: (not m.group, m.group or "", m.name))
        current_group = object()
        for m in machines_sorted:
            if m.group != current_group:
                current_group = m.group
                if current_group:
                    sep = QListWidgetItem(f"── {current_group} ──")
                    sep.setFlags(Qt.NoItemFlags)
                    self._list.addItem(sep)
            item = QListWidgetItem(f"{m.name}  –  {m.user}@{m.host}:{m.port}")
            icon = _machine_icon(m.icon_name)
            if icon:
                item.setIcon(icon)
            item.setData(Qt.UserRole, m.id)
            self._list.addItem(item)

    def _selected_machine(self):
        item = self._list.currentItem()
        if not item:
            return None
        mid = item.data(Qt.UserRole)
        if not mid:
            return None
        machines = self._config.load_machines()
        return next((m for m in machines if m.id == mid), None)

    def _on_add(self):
        from commandeck_qt.dialogs.machine_dialog import show_machine_dialog
        show_machine_dialog(self._config, on_saved=self._refresh, parent=None)

    def _on_edit(self):
        machine = self._selected_machine()
        if not machine:
            return
        from commandeck_qt.dialogs.machine_dialog import show_machine_dialog
        show_machine_dialog(self._config, machine=machine,
                            on_saved=self._refresh, parent=None)

    def _on_delete(self):
        machine = self._selected_machine()
        if not machine:
            return
        answer = QMessageBox.question(
            self,
            _('Delete "{name}"?').format(name=machine.name),
            _("This will remove the machine from Commandeck. "
              "Buttons linked to it will no longer work."),
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self._config.delete_machine(machine.id)
            self._refresh()
