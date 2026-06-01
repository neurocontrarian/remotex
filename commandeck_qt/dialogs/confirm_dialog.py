"""Confirmation dialog before running a command."""
from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import QMessageBox

from commandeck_core.models.command_button import CommandButton
from commandeck_core.i18n import _


def show_confirm_dialog(parent, button: CommandButton, on_confirm: Callable) -> None:
    box = QMessageBox(parent)
    box.setWindowTitle(_("Run command?"))
    box.setText(f'{_("Run")} "{_(button.name)}"?')
    box.setInformativeText(button.command)
    box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    box.setDefaultButton(QMessageBox.Yes)
    if box.exec() == QMessageBox.Yes:
        on_confirm()
