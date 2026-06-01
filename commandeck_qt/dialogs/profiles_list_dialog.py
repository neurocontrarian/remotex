"""Manage execution profiles dialog (Pro)."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton,
    QLabel, QMessageBox, QStackedWidget,
    QWidget, QToolBar,
)

from commandeck_core.models.config import ConfigManager
from commandeck_core.i18n import _


def show_profiles_list_dialog(config: ConfigManager, parent=None) -> None:
    # parent=None: modal dialogs with a transient parent get glued to it on
    # GNOME/Wayland. Parentless → floats as its own window, still modal.
    dlg = ProfilesListDialog(config, parent=None)
    dlg.exec()


class ProfilesListDialog(QDialog):
    _STACK_EMPTY = 0
    _STACK_LIST = 1

    def __init__(self, config: ConfigManager, parent=None):
        super().__init__(parent)
        self._config = config
        self._profiles: list = []
        self.setWindowTitle(_("Execution Profiles"))
        self.setMinimumSize(480, 420)
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        tb = QToolBar()
        tb.setMovable(False)
        add_action = tb.addAction(_("Add Profile"))
        add_action.triggered.connect(self._on_add)
        vbox.addWidget(tb)

        self._stack = QStackedWidget()

        empty = QWidget()
        ev = QVBoxLayout(empty)
        ev.setAlignment(Qt.AlignCenter)
        empty_lbl = QLabel(_("No execution profiles yet.\nClick 'Add Profile' to create one."))
        empty_lbl.setAlignment(Qt.AlignCenter)
        ev.addWidget(empty_lbl)
        self._stack.addWidget(empty)   # _STACK_EMPTY

        list_widget = QWidget()
        lv = QVBoxLayout(list_widget)
        lv.setContentsMargins(12, 12, 12, 12)
        self._list = QListWidget()
        self._list.setSelectionMode(QListWidget.SingleSelection)
        self._list.itemDoubleClicked.connect(lambda _i: self._on_edit())
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

        self._stack.addWidget(list_widget)  # _STACK_LIST
        vbox.addWidget(self._stack, 1)

    def _refresh(self):
        self._list.clear()
        self._profiles = sorted(self._config.load_profiles(), key=lambda p: p.name)
        if not self._profiles:
            self._stack.setCurrentIndex(self._STACK_EMPTY)
            return
        self._stack.setCurrentIndex(self._STACK_LIST)
        for p in self._profiles:
            parts = []
            if p.run_as_user:
                parts.append(p.run_as_user)
            if p.working_dir:
                parts.append(p.working_dir)
            if p.description and not parts:
                parts.append(p.description)
            label = p.name + (f"   –   {'  •  '.join(parts)}" if parts else "")
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, p.id)
            self._list.addItem(item)

    def _selected_profile(self):
        item = self._list.currentItem()
        if not item:
            return None
        pid = item.data(Qt.UserRole)
        return next((p for p in self._profiles if p.id == pid), None) if pid else None

    def _on_add(self):
        from commandeck_qt.dialogs.profile_dialog import show_profile_dialog
        show_profile_dialog(self._config, on_saved=self._refresh, parent=None)

    def _on_edit(self):
        profile = self._selected_profile()
        if not profile:
            return
        from commandeck_qt.dialogs.profile_dialog import show_profile_dialog
        show_profile_dialog(self._config, profile=profile,
                            on_saved=self._refresh, parent=None)

    def _on_delete(self):
        profile = self._selected_profile()
        if not profile:
            return
        answer = QMessageBox.question(
            self,
            _('Delete "{name}"?').format(name=profile.name),
            _("Buttons using this profile will fall back to their own settings."),
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self._config.delete_profile(profile.id)
            self._refresh()
