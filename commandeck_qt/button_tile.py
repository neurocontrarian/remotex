"""Qt button tile widget — equivalent of GTK ButtonTile."""
from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import Qt, Signal, QPoint, QTimer, QMimeData
from PySide6.QtGui import QColor, QIcon, QPixmap, QPainter, QCursor, QDrag
from PySide6.QtWidgets import (
    QFrame, QGraphicsDropShadowEffect, QStyle, QStyleOption,
    QVBoxLayout, QLabel, QSizePolicy, QApplication,
)


class _ColoredLabel(QLabel):
    """QLabel that paints its text in an explicit color via QPainter.

    Bypasses QSS, QPalette and platform-style overrides — notably macOS
    Cocoa, which silently ignores stylesheet color rules and palette
    overrides on QLabel descendants of a styled QFrame, leaving labels
    rendered in the system default color (black on neon's dark bg).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._paint_color: QColor | None = None

    def setPaintColor(self, color: QColor | None) -> None:
        if self._paint_color != color:
            self._paint_color = color
            self.update()

    def paintEvent(self, event):
        if self._paint_color is None:
            super().paintEvent(event)
            return
        painter = QPainter(self)
        painter.setPen(self._paint_color)
        painter.setFont(self.font())
        flags = int(self.alignment())
        if self.wordWrap():
            flags |= Qt.TextWordWrap
        painter.drawText(self.rect(), flags, self.text())

from commandeck_core.models.command_button import CommandButton
from commandeck_core.i18n import _

# Use str so Path.__truediv__ is never called at runtime — PySide6 6.11's
# shibokensupport intercepts stdlib imports triggered by Path ops and causes
# a RecursionError. Pre-compute str paths at import time instead.
_BOOTSTRAP_DIR = str(Path(__file__).parent.parent / 'data' / 'resources' / 'bootstrap')
_ICONS_DIR = str(Path(__file__).parent.parent / 'data' / 'resources' / 'icons')
_FALLBACK_ICON = "utilities-terminal"

# font_delta: point-size offset from the system default label font. Large keeps
# the default (names fit on one line); smaller tiles shrink so a wrapped name
# still fits the fixed tile height instead of being clipped mid-line.
# margin/spacing: small tiles trim the layout chrome to free vertical room so a
# long 3-line name fits.
_TILE_SIZES = {
    "small":  {"px": 20, "dim": 80,  "pad": 8,  "font_delta": -3, "margin": 3, "spacing": 1},
    "medium": {"px": 32, "dim": 120, "pad": 12, "font_delta": -1, "margin": 8, "spacing": 4},
    "large":  {"px": 48, "dim": 160, "pad": 16, "font_delta": 0,  "margin": 8, "spacing": 4},
}

# (x_offset, y_offset, blur_radius, QColor rgba)
_THEME_SHADOWS: dict[str, tuple] = {
    "bold":  (0, 3, 10, QColor(0, 0, 0, 71)),
    "cards": (0, 4, 12, QColor(0, 0, 0, 51)),
    "phone": (0, 4, 6,  QColor(0, 0, 0, 64)),
    "neon":  (0, 0, 10, QColor(0, 200, 255, 64)),
    "tron":  (0, 0, 14, QColor(30, 144, 255, 110)),
    "retro": (4, 4, 0,  QColor(0, 0, 0, 220)),
}

# Themes where icons (designed for light bg) need colorization to stay visible.
_THEME_ICON_TINT: dict[str, QColor] = {
    "neon": QColor(0, 200, 255),   # cyan
    "tron": QColor(30, 144, 255),  # dodgerblue
}

# Direct label text color per theme.  Empty = use system default.
# QSS descendant selectors (QFrame#T QLabel#L) set on a widget-level
# stylesheet don't propagate to child QLabel widgets in Qt6 — we set
# it directly on the label instead.
# phone needs an explicit dark color: its bg is always a light-gray
# gradient, so in dark mode the system default (light text) becomes
# unreadable.
_THEME_LABEL_COLORS: dict[str, str] = {
    "phone": "#1a1a1a",
    "neon":  "#00c8ff",
    "tron":  "#1e90ff",
    "retro": "#ffffff",
}


def _tint_pixmap(px: QPixmap, color: QColor) -> QPixmap:
    """Return a copy of px with all opaque pixels filled with color (icon recoloring)."""
    result = QPixmap(px.size())
    result.fill(Qt.transparent)
    painter = QPainter(result)
    painter.drawPixmap(0, 0, px)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(result.rect(), color)
    painter.end()
    return result


def _svg_to_pixmap(svg_path: str, size: int) -> QPixmap | None:
    try:
        from PySide6.QtSvg import QSvgRenderer
    except ImportError:
        return None
    renderer = QSvgRenderer(svg_path)
    if not renderer.isValid():
        return None
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    painter = QPainter(px)
    renderer.render(painter)
    painter.end()
    return px


def resolve_icon_pixmap(icon_name: str, size: int) -> QPixmap | None:
    """Try bundled Bootstrap/icons dirs first, then return None (caller uses theme)."""
    if not icon_name:
        return None
    for directory in (_BOOTSTRAP_DIR, _ICONS_DIR):
        # Use os.path.join (not Path /= operator) — PySide6 6.11 shibokensupport
        # intercepts stdlib imports during Path.__truediv__ causing RecursionError.
        svg_path = os.path.join(directory, f'{icon_name}.svg')
        if os.path.isfile(svg_path):
            px = _svg_to_pixmap(svg_path, size)
            if px:
                return px
    return None


class ButtonTile(QFrame):
    clicked = Signal()
    rightClicked = Signal(QPoint)
    # Emitted when this tile is dropped onto another: (dragged_id, target_id).
    reordered = Signal(str, str)

    # MIME type carrying the dragged button id (drag-to-reorder).
    _MIME = "application/x-commandeck-button-id"

    def __init__(self, command_button: CommandButton, size: str = "medium", parent=None):
        super().__init__(parent)
        self.command_button = command_button
        self._size = size
        self._press_pos: QPoint | None = None
        self._flash_timer: QTimer | None = None
        self._theme_qss = ""
        self._theme_name = ""
        self._bg_qss = ""
        self._text_color_qss = ""
        self._selected_qss = ""
        self._original_icon_px: QPixmap | None = None

        self.setObjectName("ButtonTile")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setProperty("tile-size", size)
        self.setProperty("running", False)
        self.setProperty("success", False)
        self.setProperty("error", False)
        self.setProperty("selected", "false")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFrameShape(QFrame.NoFrame)
        self.setAcceptDrops(True)  # drag-to-reorder (see mouse/drag events below)

        self._icon_label = QLabel()
        self._icon_label.setAlignment(Qt.AlignCenter)
        self._icon_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._text_label = _ColoredLabel()
        self._text_label.setObjectName("TileLabel")
        self._text_label.setAlignment(Qt.AlignCenter)
        self._text_label.setWordWrap(True)
        # Remember the system default point size so per-size deltas are relative.
        self._base_font_pt = self._text_label.font().pointSizeF()

        # Top/bottom stretches center the icon+label group while still letting
        # the word-wrapped label claim its full heightForWidth (2 lines) — a
        # layout-level AlignCenter would size it to a single line and clip the
        # second line mid-glyph on small/medium tiles.
        self._layout = QVBoxLayout(self)
        self._layout.addStretch(1)
        self._layout.addWidget(self._icon_label, 0, Qt.AlignHCenter)
        self._layout.addWidget(self._text_label)
        self._layout.addStretch(1)

        self._apply_style()

    def _apply_style(self):
        cfg = _TILE_SIZES.get(self._size, _TILE_SIZES["medium"])
        self.setFixedSize(cfg["dim"], cfg["dim"])

        m = cfg.get("margin", 8)
        self._layout.setContentsMargins(m, m, m, m)
        self._layout.setSpacing(cfg.get("spacing", 4))

        btn = self.command_button
        if self._base_font_pt > 0:
            font = self._text_label.font()
            font.setPointSizeF(self._base_font_pt + cfg.get("font_delta", 0))
            self._text_label.setFont(font)
        self._text_label.setText(_(btn.name))
        self._text_label.setVisible(not btn.hide_label)
        self._icon_label.setVisible(not btn.hide_icon)

        self._load_icon(cfg["px"])
        self._apply_colors()
        self._update_tooltip()

    def _load_icon(self, size: int):
        icon_name = self.command_button.icon_name
        px = resolve_icon_pixmap(icon_name, size)
        if px is None:
            icon = QIcon.fromTheme(icon_name)
            if icon.isNull():
                icon = QIcon.fromTheme(_FALLBACK_ICON)
            if not icon.isNull():
                px = icon.pixmap(size, size)
        if px and not px.isNull():
            self._original_icon_px = px
            self._icon_label.setPixmap(px)
            self._icon_label.setFixedSize(size, size)

    def _apply_colors(self):
        btn = self.command_button
        self._bg_qss = (
            f"QFrame#ButtonTile {{ background-color: {btn.color}; }}"
            if btn.color else ""
        )
        self._text_color_qss = (
            f"QFrame#ButtonTile QLabel#TileLabel {{ color: {btn.text_color}; }}"
            if btn.text_color else ""
        )
        self._rebuild_stylesheet()
        self._apply_theme_visuals()

    # Themes that define a full visual background (gradient or immersive color).
    # Per-button bg color is NOT allowed to override these — it would break the
    # gradient (phone) or the immersive look (retro/tron). Cards keeps its
    # neutral card bg as designed.  Only bold and neon let per-button colors show.
    _FULL_THEME_BG = frozenset(("cards", "phone", "retro", "tron"))

    def _rebuild_stylesheet(self):
        if self._theme_name in self._FULL_THEME_BG:
            parts = [self._bg_qss, self._theme_qss, self._text_color_qss]
        else:
            parts = [self._theme_qss, self._bg_qss, self._text_color_qss]
        # Selected state always wins — appended last so it overrides everything.
        if self._selected_qss:
            parts.append(self._selected_qss)
        self.setStyleSheet("\n".join(p for p in parts if p))

    def apply_theme(self, theme_qss: str, theme_name: str = "") -> None:
        """Called by CommandeckWindow when the theme changes."""
        self._theme_qss = theme_qss
        self._theme_name = theme_name
        self._rebuild_stylesheet()
        self._apply_shadow(theme_name)
        self._apply_theme_visuals()

    def _apply_theme_visuals(self) -> None:
        """Apply icon tinting and label paint color via the custom QPainter path.

        QSS-based color rules (widget level OR app level), QPalette, and HTML
        span inline styles are all silently overridden by macOS Cocoa for
        QLabel descendants of a styled QFrame. _ColoredLabel paints its text
        directly with QPainter, bypassing every layer that Cocoa interferes
        with. On Linux the same path is used — produces identical pixels.
        """
        # Icon tinting for dark themes (SVG icons are designed for light bg)
        tint = _THEME_ICON_TINT.get(self._theme_name)
        if self._original_icon_px and not self._original_icon_px.isNull():
            px = _tint_pixmap(self._original_icon_px, tint) if tint else self._original_icon_px
            self._icon_label.setPixmap(px)

        btn = self.command_button
        if btn.text_color:
            color = btn.text_color
        elif btn.color and self._theme_name not in self._FULL_THEME_BG:
            # Button has a per-button bg that will actually show (theme doesn't
            # override it here). Use system default text so the label stays
            # readable on the per-button color (e.g. dark text on pastel neon bg).
            color = ""
        else:
            color = _THEME_LABEL_COLORS.get(self._theme_name, "")
        self._text_label.setText(_(btn.name))
        self._text_label.setPaintColor(QColor(color) if color else None)

    def _apply_shadow(self, theme_name: str) -> None:
        params = _THEME_SHADOWS.get(theme_name)
        if params:
            xo, yo, blur, color = params
            fx = QGraphicsDropShadowEffect(self)
            fx.setXOffset(xo)
            fx.setYOffset(yo)
            fx.setBlurRadius(blur)
            fx.setColor(color)
            self.setGraphicsEffect(fx)
        else:
            self.setGraphicsEffect(None)

    def paintEvent(self, event):
        # QFrame.paintEvent calls CE_ShapedFrame which draws the frame outline
        # but does NOT paint QSS background-color when QFrame.NoFrame is set.
        # PE_Widget triggers the full QSS box model (background + border +
        # border-radius), matching what QWidget subclasses get by default.
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def _update_tooltip(self):
        btn = self.command_button
        lines = [_(btn.tooltip) if btn.tooltip else btn.command]
        remote_ids = [mid for mid in btn.machine_ids if mid]
        if remote_ids:
            if len(btn.machine_ids) > 1:
                lines.append(_("Multi-machine — asks which one at run time"))
            else:
                lines.append(_("Remote execution"))
        if btn.confirm_before_run:
            lines.append(_("Asks for confirmation before running"))
        self.setToolTip("\n".join(lines))

    def refresh(self, size: str | None = None):
        if size is not None:
            self._size = size
        self._apply_style()

    # ── State helpers ──────────────────────────────────────────────────────────

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", "true" if selected else "false")
        if selected:
            self._selected_qss = (
                "QFrame#ButtonTile { "
                "background-color: palette(highlight); "
                "border: 3px solid palette(highlight); }"
            )
        else:
            self._selected_qss = ""
        self._rebuild_stylesheet()
        self.update()

    def set_running(self, running: bool) -> None:
        self.setEnabled(not running)
        self.setProperty("running", running)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def flash_result(self, success: bool) -> None:
        prop = "success" if success else "error"
        self.setProperty(prop, True)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        if self._flash_timer:
            self._flash_timer.stop()
        self._flash_timer = QTimer(self)
        self._flash_timer.setSingleShot(True)
        self._flash_timer.timeout.connect(lambda: self._clear_flash(prop))
        self._flash_timer.start(1500)

    def _clear_flash(self, prop: str) -> None:
        self.setProperty(prop, False)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    # ── Events ─────────────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        # Left-click is emitted on *release* (not press) so a press-drag can
        # start a reorder instead of firing a click. Right-click opens the menu.
        if event.button() == Qt.LeftButton:
            self._press_pos = event.position().toPoint()
        elif event.button() == Qt.RightButton:
            self.rightClicked.emit(event.globalPosition().toPoint())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (self._press_pos is not None and (event.buttons() & Qt.LeftButton)
                and (event.position().toPoint() - self._press_pos).manhattanLength()
                >= QApplication.startDragDistance()):
            self._start_drag()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Emit click only for a left release that did NOT turn into a drag
        # (_start_drag clears _press_pos).
        if event.button() == Qt.LeftButton and self._press_pos is not None:
            self._press_pos = None
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def _start_drag(self):
        self._press_pos = None  # cancel the pending click
        drag = QDrag(self)
        mime = QMimeData()
        mime.setData(self._MIME, self.command_button.id.encode("utf-8"))
        drag.setMimeData(mime)
        pm = self.grab()
        drag.setPixmap(pm)
        drag.setHotSpot(QPoint(pm.width() // 2, pm.height() // 2))
        drag.exec(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(self._MIME):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(self._MIME):
            event.acceptProposedAction()

    def dropEvent(self, event):
        if not event.mimeData().hasFormat(self._MIME):
            return
        dragged_id = bytes(event.mimeData().data(self._MIME)).decode("utf-8")
        if dragged_id and dragged_id != self.command_button.id:
            self.reordered.emit(dragged_id, self.command_button.id)
            event.acceptProposedAction()
