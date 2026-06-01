"""Output dialog — displays stdout/stderr of a completed command."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QPlainTextEdit,
    QLabel, QDialogButtonBox, QFrame,
)

from commandeck_core.services.executor import ExecutionResult
from commandeck_core.i18n import _


def show_output_dialog(parent, button_name: str, result: ExecutionResult) -> None:
    dlg = QDialog(parent)
    dlg.setWindowTitle(_(button_name))
    dlg.resize(640, 440)
    dlg.setAttribute(Qt.WA_DeleteOnClose)

    vbox = QVBoxLayout(dlg)
    vbox.setContentsMargins(12, 12, 12, 8)
    vbox.setSpacing(8)

    output = result.stdout or ""
    if result.stderr:
        if output:
            output += "\n--- stderr ---\n"
        output += result.stderr
    if not output:
        output = _("(no output)")

    text_edit = QPlainTextEdit()
    text_edit.setReadOnly(True)
    # "Monospace" is an X11/fontconfig alias that does not exist on Windows or
    # macOS, where it silently falls back to a proportional font and breaks
    # column alignment of Format-Table / df output. Use the platform's real
    # fixed-pitch font (Consolas, Menlo, DejaVu Sans Mono, …).
    mono = QFontDatabase.systemFont(QFontDatabase.FixedFont)
    mono.setPointSize(10)
    mono.setStyleHint(QFont.Monospace)
    text_edit.setFont(mono)
    # Never word-wrap fixed-width tables — let the user scroll horizontally.
    text_edit.setLineWrapMode(QPlainTextEdit.NoWrap)
    text_edit.setPlainText(output)
    vbox.addWidget(text_edit)

    sep = QFrame()
    sep.setFrameShape(QFrame.HLine)
    sep.setFrameShadow(QFrame.Sunken)
    vbox.addWidget(sep)

    icon = "✓" if result.success else "✗"
    status_lbl = QLabel(
        f"{icon}  Exit {result.return_code}  —  {result.duration_ms} ms"
    )
    vbox.addWidget(status_lbl)

    bb = QDialogButtonBox(QDialogButtonBox.Close)
    bb.rejected.connect(dlg.accept)
    vbox.addWidget(bb)

    dlg.show()
