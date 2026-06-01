"""Machine picker dialog — shown at click time when a button targets multiple machines."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QCheckBox, QDialogButtonBox, QPushButton,
    QScrollArea, QWidget,
)

from commandeck_core.i18n import _


def show_machine_picker(
    parent,
    options: list[tuple[str, str, str]],
    on_chosen: Callable[[list[str]], None],
) -> None:
    """Modal picker for multi-machine buttons.

    options: list of (machine_id, title, subtitle).
             machine_id="" represents local execution.
    on_chosen: called with the list of selected machine_ids.
    """
    dlg = _MachinePickerDialog(parent, options, on_chosen)
    dlg.exec()


class _MachinePickerDialog(QDialog):
    def __init__(self, parent, options: list[tuple[str, str, str]],
                 on_chosen: Callable[[list[str]], None]):
        super().__init__(parent)
        self._options = options
        self._on_chosen = on_chosen
        self._checks: list[tuple[str, QCheckBox]] = []

        self.setWindowTitle(_("Choose machines"))
        self.setMinimumWidth(360)
        self.setMinimumHeight(300)
        self._build_ui()

    def _build_ui(self):
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(16, 16, 16, 12)

        header = QLabel(
            _("Select the machines to run this command on.\n"
              "One output window will open per machine.")
        )
        header.setWordWrap(True)
        vbox.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        inner = QWidget()
        inner_vbox = QVBoxLayout(inner)
        inner_vbox.setContentsMargins(0, 0, 0, 0)

        for machine_id, title, subtitle in self._options:
            cb = QCheckBox()
            cb.setText(f"{title}\n{subtitle}" if subtitle else title)
            cb.toggled.connect(self._update_run_button)
            inner_vbox.addWidget(cb)
            self._checks.append((machine_id, cb))

        scroll.setWidget(inner)
        vbox.addWidget(scroll, 1)

        # Select all / deselect all
        self._toggle_all_btn = QPushButton(_("Select all"))
        self._toggle_all_btn.setFlat(True)
        self._toggle_all_btn.clicked.connect(self._on_toggle_all)
        vbox.addWidget(self._toggle_all_btn, alignment=Qt.AlignLeft)

        bb = QDialogButtonBox()
        self._run_btn = bb.addButton(_("Run"), QDialogButtonBox.AcceptRole)
        self._run_btn.setEnabled(False)
        bb.addButton(QDialogButtonBox.Cancel)
        bb.accepted.connect(self._on_accept)
        bb.rejected.connect(self.reject)
        vbox.addWidget(bb)

    def _update_run_button(self):
        count = sum(1 for _, cb in self._checks if cb.isChecked())
        total = len(self._checks)
        self._run_btn.setEnabled(count > 0)
        self._run_btn.setText(
            _("Run on {count}").format(count=count) if count > 1 else _("Run")
        )
        self._toggle_all_btn.setText(
            _("Deselect all") if count == total else _("Select all")
        )

    def _on_toggle_all(self):
        count = sum(1 for _, cb in self._checks if cb.isChecked())
        select = count < len(self._checks)
        for _, cb in self._checks:
            cb.blockSignals(True)
            cb.setChecked(select)
            cb.blockSignals(False)
        self._update_run_button()

    def _on_accept(self):
        chosen = [mid for mid, cb in self._checks if cb.isChecked()]
        if chosen:
            self.accept()
            self._on_chosen(chosen)
