"""Main application window — PySide6 equivalent of GTK CommandeckWindow."""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, QSize, QPoint, QRect, QCoreApplication
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QToolBar, QLineEdit, QWidget, QHBoxLayout,
    QScrollArea, QStackedWidget, QLabel, QPushButton,
    QVBoxLayout, QStatusBar, QMenu, QMessageBox,
    QButtonGroup, QToolButton, QFrame, QRubberBand, QApplication,
)

from commandeck_core.models.config import ConfigManager
from commandeck_core.models.command_button import CommandButton
from commandeck_core.services.executor import ExecutionResult
from commandeck_core.i18n import _
from commandeck_core.utils.exec_log import log as _exec_log, get_log_path as _exec_log_path

from commandeck_qt.button_tile import ButtonTile
from commandeck_qt.flow_layout import FlowLayout
from commandeck_qt.settings import Settings

import os as _os
_QSS_BASE_PATH = _os.path.join(_os.path.dirname(__file__), "resources", "style", "base.qss")

_THEME_QSS: dict[str, str] = {
    # bold: accent bg + bold text, matching GTK .theme-bold.
    # Per-button colors (appended after in tile stylesheet) override this bg.
    "bold": """
QFrame#ButtonTile {
    background-color: palette(highlight);
    border: none;
    border-radius: 10px;
}
QFrame#ButtonTile:hover {
    background-color: palette(dark);
}
QFrame#ButtonTile QLabel#TileLabel {
    color: palette(highlighted-text);
    font-weight: bold;
}
""",
    # cards: white/card bg, accent-tinted border — matching GTK .theme-cards.
    "cards": """
QFrame#ButtonTile {
    background-color: palette(base);
    border: 2px solid rgba(53,132,228,71);
    border-radius: 12px;
}
QFrame#ButtonTile:hover {
    border-color: rgba(53,132,228,165);
}
""",
    # phone: light gray gradient + bottom-heavy border for 3D key press look.
    # GTK used box-shadow: 0 4px 0 rgba(0,0,0,0.25) — simulated via border-bottom.
    "phone": """
QFrame#ButtonTile {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #f5f5f5,stop:1 #d8d8d8);
    border: 1px solid rgba(0,0,0,38);
    border-bottom: 4px solid rgba(0,0,0,64);
    border-radius: 8px;
}
QFrame#ButtonTile:hover {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #ffffff,stop:1 #e8e8e8);
}
""",
    # neon: pure black bg, cyan border, cyan text — matching GTK .theme-neon.
    # Hover only changes border-color (0.2→0.6 opacity), not border width.
    "neon": """
QFrame#ButtonTile {
    background-color: #0d0d0d;
    border: 1px solid rgba(0,200,255,51);
    border-radius: 8px;
}
QFrame#ButtonTile:hover {
    border-color: rgba(0,200,255,153);
}
QFrame#ButtonTile QLabel#TileLabel {
    color: #00c8ff;
    font-weight: bold;
}
""",
    # tron: pure black bg, electric-blue border (dodgerblue), sharp 2px radius —
    # angular Tron aesthetic, visually distinct from neon's cyan/8px-radius look.
    "tron": """
QFrame#ButtonTile {
    background-color: #000000;
    border: 1px solid rgba(30,144,255,128);
    border-radius: 2px;
}
QFrame#ButtonTile:hover {
    border-color: rgba(30,144,255,220);
    background-color: #060a10;
}
QFrame#ButtonTile QLabel#TileLabel {
    color: #1e90ff;
    font-weight: bold;
}
""",
    # retro: diagonal orange gradient, thick dark border, offset shadow via
    # border-right/bottom — matching GTK .theme-retro (box-shadow: 4px 4px 0 #000).
    "retro": """
QFrame#ButtonTile {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #e8622a,stop:1 #f0981a);
    border: 3px solid #993300;
    border-radius: 4px;
}
QFrame#ButtonTile:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #ff7a3d,stop:1 #ffb030);
}
QFrame#ButtonTile QLabel#TileLabel {
    color: #ffffff;
    font-weight: bold;
}
""",
}

def _load_base_stylesheet() -> str:
    return open(_QSS_BASE_PATH).read() if _os.path.isfile(_QSS_BASE_PATH) else ""


class _GridWidget(QWidget):
    """Grid container that supports rubber-band drag selection."""

    def __init__(self, window: "CommandeckWindow"):
        super().__init__()
        self._window = window
        self._rubber_band: QRubberBand | None = None
        self._drag_start: QPoint | None = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.childAt(event.position().toPoint()) is None:
            self._drag_start = event.position().toPoint()
            if self._rubber_band is None:
                self._rubber_band = QRubberBand(QRubberBand.Rectangle, self)
            self._rubber_band.setGeometry(QRect(self._drag_start, QSize()))
            self._rubber_band.show()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_start is not None and self._rubber_band:
            self._rubber_band.setGeometry(
                QRect(self._drag_start, event.position().toPoint()).normalized()
            )
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_start is not None and self._rubber_band:
            rect = QRect(self._drag_start, event.position().toPoint()).normalized()
            self._rubber_band.hide()
            self._drag_start = None
            if rect.width() > 5 and rect.height() > 5:
                self._window._on_rubber_band_select(rect)
        super().mouseReleaseEvent(event)


class CommandeckWindow(QMainWindow):
    def __init__(self, config: ConfigManager, platform, parent=None):
        super().__init__(parent)
        self._config = config
        self._platform = platform
        self._settings = Settings()
        self._tiles: dict[str, ButtonTile] = {}
        self._search_text = ""
        self._active_category: str | None = None  # None = All
        self._cat_buttons: list[QToolButton] = []
        self._cat_group = QButtonGroup(self)
        self._cat_group.setExclusive(True)
        self._selected_ids: set[str] = set()
        # None = no free-tier restriction (Pro/trial). Otherwise the set of
        # non-default custom button ids that stay visible under the free limit.
        self._free_visible_ids: set[str] | None = None
        self._current_theme_name = "bold"
        self._current_theme_qss = ""

        self.setWindowTitle("Commandeck")
        # Re-apply persisted "always on top" before the first show. The menu only
        # reflected the saved setting's checkbox; the flag itself was never applied
        # at startup, so the window wasn't actually on top until toggled.
        if self._settings.get_bool("always-on-top") \
                and self._platform.supports_always_on_top()[0]:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self._restore_size()
        self._build_ui()
        # _apply_theme() stores _current_theme_qss; populate_grid() passes it to
        # each tile at construction. Order matters — theme must be set first.
        self._apply_theme()
        self.populate_grid()

        # Defer license/trial checks
        QTimer.singleShot(200, self._check_license_state)

    # ── Window state ───────────────────────────────────────────────────────────

    def _restore_size(self):
        w = self._settings.get_int("window-width")
        h = self._settings.get_int("window-height")
        self.resize(w, h)
        if self._settings.get_bool("window-maximized"):
            self.showMaximized()

    def closeEvent(self, event):
        self._settings.set_bool("window-maximized", self.isMaximized())
        if not self.isMaximized():
            self._settings.set_int("window-width", self.width())
            self._settings.set_int("window-height", self.height())
        super().closeEvent(event)

    # ── UI construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_toolbar()
        self._build_search_bar()
        self._build_category_bar()

        # Central stack: grid | empty
        self._stack = QStackedWidget()
        self._build_grid_page()
        self._build_empty_page()

        self._build_selection_bar()

        # Trial banner (hidden until _check_license_state runs)
        self._trial_banner = QLabel()
        self._trial_banner.setAlignment(Qt.AlignCenter)
        self._trial_banner.setStyleSheet(
            "background:#e5a50a; color:#000; padding:4px; font-weight:bold;"
        )
        self._trial_banner.hide()

        # Wrap everything in a vertical layout
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(self._trial_banner)
        vbox.addWidget(self._search_bar_widget)
        vbox.addWidget(self._cat_bar_widget)
        vbox.addWidget(self._stack)
        vbox.addWidget(self._sel_bar)
        self.setCentralWidget(container)

        # Status bar for toasts
        self.statusBar().setSizeGripEnabled(False)

    def _build_toolbar(self):
        tb = QToolBar("Main")
        tb.setMovable(False)
        tb.setFloatable(False)
        self.addToolBar(Qt.TopToolBarArea, tb)

        # Add button
        self._act_add = QAction(_("Add"), self)
        self._act_add.setShortcut(QKeySequence("Ctrl+N"))
        self._act_add.triggered.connect(self._on_add)
        tb.addAction(self._act_add)

        tb.addSeparator()

        # Search toggle
        self._act_search = QAction(_("Search"), self)
        self._act_search.setCheckable(True)
        self._act_search.setShortcut(QKeySequence("Ctrl+F"))
        self._act_search.toggled.connect(self._on_search_toggle)
        tb.addAction(self._act_search)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(
            spacer.sizePolicy().horizontalPolicy(),
            spacer.sizePolicy().verticalPolicy(),
        )
        from PySide6.QtWidgets import QSizePolicy
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        tb.addWidget(spacer)

        # Hamburger menu
        menu_btn = QToolButton()
        menu_btn.setText("☰")
        menu_btn.setPopupMode(QToolButton.InstantPopup)
        menu = QMenu(self)
        menu.addAction(_("Preferences"), self._on_preferences, QKeySequence("Ctrl+,"))
        menu.addAction(_("Manage Machines"), self._on_manage_machines)
        menu.addAction(_("Execution Profiles"), self._on_manage_profiles)
        menu.addSeparator()
        from commandeck_core.platform import get_platform
        aot_ok, aot_reason = get_platform().supports_always_on_top()
        self._act_always_on_top = QAction(_("Always on Top"), self)
        self._act_always_on_top.setCheckable(True)
        self._act_always_on_top.setChecked(self._settings.get_bool("always-on-top") and aot_ok)
        self._act_always_on_top.setEnabled(aot_ok)
        if not aot_ok:
            # e.g. GNOME/Wayland: the compositor forbids apps from forcing
            # stay-on-top. Disable + explain rather than silently do nothing.
            self._act_always_on_top.setToolTip(aot_reason)
        self._act_always_on_top.toggled.connect(self._on_always_on_top)
        menu.addAction(self._act_always_on_top)
        menu.addSeparator()
        menu.addAction(_("Reset to Defaults"), self._on_reset_to_defaults)
        menu.addSeparator()
        menu.addAction(_("Show Execution Log"), self._on_show_execution_log)
        menu.addAction(_("About"), self._on_about)
        menu.addAction(_("Quit"), self.close, QKeySequence("Ctrl+Q"))
        menu_btn.setMenu(menu)
        tb.addWidget(menu_btn)

    def _build_search_bar(self):
        self._search_bar_widget = QWidget()
        self._search_bar_widget.setVisible(False)
        layout = QHBoxLayout(self._search_bar_widget)
        layout.setContentsMargins(8, 4, 8, 4)
        self._search_entry = QLineEdit()
        self._search_entry.setPlaceholderText(_("Search buttons…"))
        self._search_entry.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search_entry)

    def _build_category_bar(self):
        self._cat_bar_widget = QWidget()
        self._cat_bar_widget.setVisible(False)
        self._cat_bar_layout = QHBoxLayout(self._cat_bar_widget)
        self._cat_bar_layout.setContentsMargins(8, 4, 8, 4)
        self._cat_bar_layout.setSpacing(6)
        self._cat_bar_layout.addStretch()

    def _build_selection_bar(self):
        from PySide6.QtWidgets import QSizePolicy as SP
        self._sel_bar = QFrame()
        self._sel_bar.setFrameShape(QFrame.StyledPanel)
        self._sel_bar.setVisible(False)
        hbox = QHBoxLayout(self._sel_bar)
        hbox.setContentsMargins(12, 6, 12, 6)
        self._sel_count_lbl = QLabel()
        hbox.addWidget(self._sel_count_lbl)
        hbox.addStretch()
        cat_btn = QPushButton(_("Change category"))
        cat_btn.clicked.connect(self._on_sel_change_category)
        hbox.addWidget(cat_btn)
        machine_btn = QPushButton(_("Change machine"))
        machine_btn.clicked.connect(self._on_sel_change_machine)
        hbox.addWidget(machine_btn)
        del_btn = QPushButton(_("Delete"))
        del_btn.clicked.connect(self._on_sel_delete)
        hbox.addWidget(del_btn)
        clear_btn = QPushButton("✕")
        clear_btn.setFixedWidth(32)
        clear_btn.clicked.connect(self._clear_selection)
        hbox.addWidget(clear_btn)

    def _build_grid_page(self):
        self._grid_widget = _GridWidget(self)
        self._flow = FlowLayout(self._grid_widget,
                                h_spacing=8, v_spacing=8)
        self._grid_widget.setLayout(self._flow)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setWidget(self._grid_widget)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._stack.addWidget(self._scroll)

    def _build_empty_page(self):
        empty = QWidget()
        vbox = QVBoxLayout(empty)
        vbox.setAlignment(Qt.AlignCenter)
        lbl = QLabel(_("No buttons yet"))
        lbl.setAlignment(Qt.AlignCenter)
        vbox.addWidget(lbl)
        btn = QPushButton(_("Add a button"))
        btn.clicked.connect(self._on_add)
        vbox.addWidget(btn, alignment=Qt.AlignCenter)
        self._stack.addWidget(empty)

    # ── Grid population ────────────────────────────────────────────────────────

    def populate_grid(self):
        # Clear selection before rebuilding tiles
        self._selected_ids.clear()
        self._sel_bar.setVisible(False)
        # Clear existing tiles
        while self._flow.count():
            item = self._flow.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self._tiles.clear()

        buttons = sorted(self._config.load_buttons(), key=lambda b: b.position)
        size = self._settings.get_str("button-size")

        # Free tier: only the first FREE_BUTTON_LIMIT custom (non-default)
        # buttons stay visible; default buttons are always shown. Pro/trial
        # lifts the restriction (None).
        if self._is_pro():
            self._free_visible_ids = None
        else:
            custom = [b for b in buttons if not b.is_default]
            self._free_visible_ids = {b.id for b in custom[:self._free_button_limit()]}

        hidden_cats = self._get_hidden_categories()
        for btn in buttons:
            if not self._matches_filter(btn, hidden_cats):
                continue
            tile = ButtonTile(btn, size=size)
            tile.clicked.connect(lambda b=btn, t=tile: self._on_tile_clicked(b, t))
            tile.rightClicked.connect(lambda pos, b=btn: self._on_tile_right_click(b, pos))
            tile.reordered.connect(self._on_reorder)
            # Add to layout BEFORE apply_theme so any post-attach polish from
            # macOS Cocoa happens first; apply_theme then sets icon tint /
            # shadow on a fully-attached widget.
            self._flow.addWidget(tile)
            tile.apply_theme(self._current_theme_qss, self._current_theme_name)
            self._tiles[btn.id] = tile

        has_tiles = bool(self._tiles)
        self._stack.setCurrentIndex(0 if has_tiles else 1)
        self._update_category_bar(buttons, hidden_cats)

    def _matches_filter(self, btn: CommandButton, hidden_cats: set) -> bool:
        # Free-tier: hide custom buttons beyond the limit (defaults always shown).
        if (self._free_visible_ids is not None and not btn.is_default
                and btn.id not in self._free_visible_ids):
            return False
        if btn.category and btn.category in hidden_cats:
            return False
        if self._active_category is not None and btn.category != self._active_category:
            return False
        if self._search_text:
            text = self._search_text.lower()
            if text not in btn.name.lower() and text not in btn.command.lower():
                return False
        return True

    def _get_hidden_categories(self) -> set[str]:
        return set(self._settings.get_strv("hidden-categories"))

    # ── Category bar ──────────────────────────────────────────────────────────

    def _update_category_bar(self, buttons: list[CommandButton], hidden_cats: set):
        # Remove old category buttons (keep stretch at end)
        for btn in self._cat_buttons:
            self._cat_bar_layout.removeWidget(btn)
            self._cat_group.removeButton(btn)
            btn.deleteLater()
        self._cat_buttons.clear()

        cats = sorted({b.category for b in buttons if b.category and b.category not in hidden_cats})
        self._cat_bar_widget.setVisible(bool(cats))
        if not cats:
            return

        # "All" button
        all_btn = self._make_cat_button(_("All"), None)
        self._cat_bar_layout.insertWidget(0, all_btn)
        self._cat_buttons.append(all_btn)

        for i, cat in enumerate(cats):
            cb = self._make_cat_button(_(cat), cat)
            self._cat_bar_layout.insertWidget(i + 1, cb)
            self._cat_buttons.append(cb)

        # Set initial checked state without triggering populate_grid() again.
        for btn in self._cat_buttons:
            btn.blockSignals(True)
        if self._active_category is None:
            all_btn.setChecked(True)
        else:
            for btn in self._cat_buttons[1:]:
                if btn.text() == _(self._active_category):
                    btn.setChecked(True)
                    break
        for btn in self._cat_buttons:
            btn.blockSignals(False)

    def _make_cat_button(self, label: str, category: str | None) -> QToolButton:
        btn = QToolButton()
        btn.setText(label)
        btn.setCheckable(True)
        btn.setAutoRaise(True)
        self._cat_group.addButton(btn)
        btn.toggled.connect(lambda checked, cat=category: self._on_cat_toggled(cat, checked))
        # Right-click a real category pill to hide it (the "All" pill has no category).
        if category is not None:
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda pos, c=category, b=btn: self._on_cat_right_click(c, b.mapToGlobal(pos)))
        return btn

    def _on_cat_right_click(self, category: str, global_pos: QPoint):
        menu = QMenu(self)
        menu.addAction(_("Hide category"), lambda: self._set_category_hidden(category, True))
        hidden = self._get_hidden_categories()
        if hidden:
            menu.addSeparator()
            for h in sorted(hidden):
                menu.addAction(_("Show category") + f": {_(h)}",
                               lambda c=h: self._set_category_hidden(c, False))
        menu.exec(global_pos)

    def _set_category_hidden(self, category: str, hide: bool):
        current = set(self._get_hidden_categories())
        if hide:
            current.add(category)
            if self._active_category == category:
                self._active_category = None
        else:
            current.discard(category)
        self._settings.set_strv("hidden-categories", sorted(current))
        self.populate_grid()

    def _on_cat_toggled(self, category: str | None, checked: bool):
        if checked:
            self._active_category = category
            self.populate_grid()

    # ── Execution ─────────────────────────────────────────────────────────────

    def _on_tile_clicked(self, btn: CommandButton, tile: ButtonTile):
        _exec_log(f"_on_tile_clicked: btn={btn.name!r} id={btn.id}")
        if QApplication.keyboardModifiers() & Qt.ControlModifier:
            _exec_log("  ctrl held -> selection toggle (no execute)")
            if self._is_pro():
                self._toggle_tile_selection(btn.id)
                self._update_selection_ui()
            return
        if btn.confirm_before_run:
            from commandeck_qt.dialogs.confirm_dialog import show_confirm_dialog
            confirmed = [False]
            def _do_confirm():
                confirmed[0] = True
            show_confirm_dialog(self, btn, _do_confirm)
            if not confirmed[0]:
                _exec_log("  confirm dialog declined")
                return
        if len(btn.machine_ids) > 1:
            self._pick_machine_and_execute(btn, tile)
        else:
            self._execute(btn, tile)

    def _pick_machine_and_execute(self, btn: CommandButton, tile: ButtonTile):
        from commandeck_qt.dialogs.machine_picker_dialog import show_machine_picker
        options = []
        machines_by_id = {m.id: m for m in self._config.load_machines()}
        for mid in btn.machine_ids:
            if mid == "":
                options.append(("", _("Local"), ""))
            else:
                machine = machines_by_id.get(mid)
                if machine:
                    options.append((mid, machine.name, f"{machine.user}@{machine.host}"))
        if not options:
            self._execute(btn, tile)
            return
        def on_chosen(chosen_ids: list[str]):
            for machine_id in chosen_ids:
                self._execute(btn, tile, machine_id_override=machine_id)
        show_machine_picker(self, options, on_chosen)

    def _execute(self, btn: CommandButton, tile: ButtonTile, machine_id_override: str | None = None):
        try:
            from commandeck_core.pro.services.executor_pro import CommandExecutorPro
            executor = CommandExecutorPro(
                self._config,
                get_timeout=self._settings.get_timeout,
            )
        except ImportError:
            from commandeck_core.services.executor import CommandExecutor
            executor = CommandExecutor(
                self._config,
                get_timeout=self._settings.get_timeout,
            )

        if machine_id_override is not None:
            machine_id = machine_id_override
        elif len(btn.machine_ids) == 1:
            machine_id = btn.machine_ids[0]
        else:
            machine_id = None
        tile.set_running(True)

        # Treat unset ("") as "output" — legacy buttons created before the default
        # was added would otherwise always run silently with no visible feedback.
        show_output = btn.execution_mode in ("output", "") or btn.show_output
        _exec_log(f"_execute: btn={btn.name!r} machine_id={machine_id!r} show_output={show_output}")

        def on_done(result):
            _exec_log(f"on_done: result_type={type(result).__name__}")
            tile.set_running(False)
            if isinstance(result, Exception):
                _exec_log(f"  exception result: {result}")
                tile.flash_result(False)
                self.show_toast(f"Error: {result}")
                return
            _exec_log(f"  ExecutionResult: success={result.success} rc={result.return_code} stdout_len={len(result.stdout)} stderr_len={len(result.stderr)} duration_ms={result.duration_ms}")
            tile.flash_result(result.success)
            if show_output or not result.success:
                _exec_log("  -> showing output dialog")
                self._show_output(result, _(btn.name))
            elif result.success:
                _exec_log("  -> showing success toast")
                self.show_toast(f"✓ {_(btn.name)}")

        # executor.execute() already dispatches to a background thread
        # and calls on_done via the core_threading dispatcher (QTimer.singleShot).
        executor.execute(btn, on_done, machine_id)

    def _show_output(self, result: ExecutionResult, button_name: str = ""):
        from commandeck_qt.dialogs.output_dialog import show_output_dialog
        show_output_dialog(self, button_name or _("Command Output"), result)

    # ── Context menu ──────────────────────────────────────────────────────────

    def _on_tile_right_click(self, btn: CommandButton, pos: QPoint):
        menu = QMenu(self)
        menu.addAction(_("Edit"), lambda: self._on_edit(btn))
        menu.addAction(_("Duplicate"), lambda: self._on_duplicate(btn))
        # "Move to category" — quick assignment to an existing category.
        categories = sorted({b.category for b in self._config.load_buttons()
                             if b.category and b.category != btn.category})
        if categories:
            move_menu = menu.addMenu(_("Move to category"))
            for cat in categories:
                move_menu.addAction(_(cat), lambda c=cat: self._assign_category(btn, c))
        menu.addSeparator()
        menu.addAction(_("Delete"), lambda: self._on_delete(btn))
        menu.exec(pos)

    def _assign_category(self, btn: CommandButton, category: str):
        buttons = self._config.load_buttons()
        for b in buttons:
            if b.id == btn.id:
                b.category = category
                break
        self._config.save_buttons(buttons)
        self.populate_grid()

    def _on_reorder(self, dragged_id: str, target_id: str):
        """Swap the positions of two buttons (drag-and-drop reorder)."""
        buttons = self._config.load_buttons()
        dragged = next((b for b in buttons if b.id == dragged_id), None)
        target = next((b for b in buttons if b.id == target_id), None)
        if dragged is None or target is None:
            return
        dragged.position, target.position = target.position, dragged.position
        self._config.save_buttons(buttons)
        self.populate_grid()

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def _on_add(self):
        if self._free_limit_reached():
            self._show_button_limit_dialog()
            return
        from commandeck_qt.dialogs.command_dialog import show_command_dialog
        result = show_command_dialog(self._config, parent=self)
        if result:
            self.populate_grid()

    def _on_edit(self, btn: CommandButton):
        # Editing default buttons is a Pro feature; free users can run them.
        if btn.is_default and not self._is_pro():
            self._show_pro_limit_dialog(_("Editing default buttons requires Commandeck Pro"))
            return
        from commandeck_qt.dialogs.command_dialog import show_command_dialog
        result = show_command_dialog(self._config, command_button=btn, parent=self)
        if result:
            self.populate_grid()

    def _on_duplicate(self, btn: CommandButton):
        if self._free_limit_reached():
            self._show_button_limit_dialog()
            return
        import uuid
        import dataclasses
        buttons = self._config.load_buttons()
        new_btn = dataclasses.replace(
            btn,
            id=str(uuid.uuid4()),
            name=f"{_(btn.name)} (copy)",
            position=max((b.position for b in buttons), default=0) + 1,
            is_default=False,
        )
        self._config.add_button(new_btn)
        self.populate_grid()

    def _on_delete(self, btn: CommandButton):
        answer = QMessageBox.question(
            self,
            _("Delete button"),
            f"{_('Delete')} '{_(btn.name)}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self._config.delete_button(btn.id)
            self.populate_grid()

    # ── Toolbar actions ───────────────────────────────────────────────────────

    def _on_search_toggle(self, checked: bool):
        self._search_bar_widget.setVisible(checked)
        if checked:
            self._search_entry.setFocus()
        else:
            self._search_entry.clear()

    def _on_search_changed(self, text: str):
        self._search_text = text
        self.populate_grid()

    def _on_always_on_top(self, checked: bool):
        self._settings.set_bool("always-on-top", checked)
        flags = self.windowFlags()
        if checked:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
        self.show()

    def _show_pro_limit_dialog(self, message: str) -> None:
        QMessageBox.information(self, _("Commandeck Pro"), message)

    def _on_preferences(self):
        from commandeck_qt.dialogs.preferences_dialog import show_preferences_dialog
        # Non-modal: the dialog itself refreshes us via its finished signal
        # (see show_preferences_dialog). Calling _apply_theme/populate_grid
        # here would fire immediately after show(), before any user change.
        show_preferences_dialog(self._config, self._settings, parent=self)

    def _require_pro(self, message: str) -> bool:
        """True if Pro is active; otherwise show the upgrade dialog and return False.
        On a free build the pro module is absent (ImportError) → treat as not-Pro
        and show the upgrade dialog, so the action is blocked cleanly instead of
        proceeding into a pro-only dialog that would crash on import."""
        try:
            from commandeck_core.pro.license import is_pro_active
            if is_pro_active():
                return True
        except ImportError:
            pass
        self._show_pro_limit_dialog(message)
        return False

    def _on_manage_machines(self):
        if not self._require_pro(
            _("Manage Machines requires Commandeck Pro.\n\n"
              "Upgrade to add SSH machines and run commands remotely.")):
            return
        from commandeck_qt.dialogs.machines_list_dialog import show_machines_list_dialog
        show_machines_list_dialog(self._config, parent=self)

    def _on_manage_profiles(self):
        if not self._require_pro(
            _("Execution Profiles require Commandeck Pro.\n\n"
              "Upgrade to save reusable run-as user and working-directory settings.")):
            return
        from commandeck_qt.dialogs.profiles_list_dialog import show_profiles_list_dialog
        show_profiles_list_dialog(self._config, parent=self)

    def _on_about(self):
        QMessageBox.about(
            self,
            "Commandeck",
            f"<b>Commandeck {QCoreApplication.applicationVersion()}</b><br>"
            "A cross-platform graphical remote control for your local &amp; "
            "remote commands.<br><br>"
            "© 2026 neurocontrarian<br>"
            + _("Provided \"as is\", without warranty of any kind.") + "<br>"
            + _("Free software under the GNU AGPLv3.") + " "
            '<a href="https://github.com/neurocontrarian/commandeck">'
            + _("Source code") + "</a><br><br>"
            '<a href="https://commandeck.app/legal/terms/">'
            + _("Terms") + "</a> &middot; "
            '<a href="https://commandeck.app/legal/privacy/">'
            + _("Privacy") + "</a> &middot; "
            '<a href="https://commandeck.app/legal/refund/">'
            + _("Refund") + "</a>",
        )

    def _on_reset_to_defaults(self):
        reply = QMessageBox.question(
            self,
            _("Reset to Defaults"),
            _("This will replace all buttons with the default set for your platform.\n"
              "Your current buttons will be backed up.\n\nContinue?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        backup = self._config.reset_buttons_to_defaults()
        self.populate_grid()
        if backup:
            QMessageBox.information(
                self, _("Reset to Defaults"),
                _("Done. Your previous buttons were backed up to:\n{path}").format(path=backup),
            )
        else:
            QMessageBox.information(self, _("Reset to Defaults"), _("Default buttons restored."))

    def _on_show_execution_log(self):
        """Open a dialog with the contents of execution.log (last button-click trace)."""
        path = _exec_log_path()
        if path is None or not path.exists():
            QMessageBox.information(
                self, _("Execution Log"),
                _("No log file yet. Click a button first to generate trace output."),
            )
            return
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            QMessageBox.warning(self, _("Execution Log"), f"Cannot read log: {e}")
            return
        dlg = QMessageBox(self)
        dlg.setWindowTitle(_("Execution Log"))
        dlg.setText(str(path))
        dlg.setDetailedText(content or "(empty)")
        # QMessageBox detail viewer is small; resize the underlying text edit.
        from PySide6.QtWidgets import QTextEdit
        for child in dlg.findChildren(QTextEdit):
            child.setMinimumSize(700, 400)
            child.setLineWrapMode(QTextEdit.NoWrap)
        dlg.exec()

    # ── License / trial ───────────────────────────────────────────────────────

    def _check_license_state(self):
        """Reflect the current license/trial state in the persistent top banner."""
        try:
            from commandeck_core.pro.license import get_trial_info, get_license_info
            lic = get_license_info()
            if lic.get("key"):
                # Paid license: persistent notice on imminent expiry / once expired.
                if lic.get("is_expired"):
                    self._show_banner(_("Pro license expired — free tier limits now apply"))
                elif lic.get("expiry_warning"):
                    self._show_banner(
                        _("Pro license expires in {days} days — renew in Preferences").format(
                            days=lic.get("days_until_expiry", 0)))
                return
            info = get_trial_info()
            if info.get("active"):
                days = info.get("days_remaining", 0)
                if days <= 3:
                    self._show_banner(
                        _("Trial expires in {days} day(s) — upgrade to keep Pro access").format(
                            days=days))
                else:
                    self._show_banner(_("Pro trial — {days} day(s) remaining").format(days=days))
            elif info.get("started_at"):
                # Trial fully used and no license → free-tier limits now apply.
                self._show_banner(_("Pro trial ended — free tier limits now apply"))
        except Exception:
            pass

    def _show_banner(self, text: str) -> None:
        """Persistent top banner for license/trial state — stays until the next check."""
        self._trial_banner.setText(text)
        self._trial_banner.show()

    # ── Theme ─────────────────────────────────────────────────────────────────

    def _apply_theme(self):
        self._current_theme_name = self._settings.get_str("button-theme") or "bold"
        self._current_theme_qss = _THEME_QSS.get(self._current_theme_name, "")
        # base.qss is the only app-level stylesheet. Theme QSS lives at widget
        # level and reaches child QLabels via AA_UseStyleSheetPropagationInWidgetStyles
        # (set in app.py before QApplication construction).
        QApplication.instance().setStyleSheet(_load_base_stylesheet())
        for tile in self._tiles.values():
            tile.apply_theme(self._current_theme_qss, self._current_theme_name)

    # ── Pro helpers ───────────────────────────────────────────────────────────

    def _is_pro(self) -> bool:
        try:
            from commandeck_core.pro.license import is_pro_active
            return is_pro_active()
        except ImportError:
            return False

    def _free_button_limit(self) -> int:
        try:
            from commandeck_core.pro.license import FREE_BUTTON_LIMIT
            return FREE_BUTTON_LIMIT
        except ImportError:
            return 3

    def _free_limit_reached(self) -> bool:
        """True when a free user has hit the custom-button cap (Pro: never)."""
        return (not self._is_pro()
                and self._config.count_custom_buttons() >= self._free_button_limit())

    def _show_button_limit_dialog(self) -> None:
        self._show_pro_limit_dialog(
            _("The free tier allows up to {limit} custom buttons.\n"
              "Upgrade to Commandeck Pro for unlimited buttons.").format(
                limit=self._free_button_limit()))

    # ── Multi-select ──────────────────────────────────────────────────────────

    def _toggle_tile_selection(self, btn_id: str):
        tile = self._tiles.get(btn_id)
        if tile is None:
            return
        if btn_id in self._selected_ids:
            self._selected_ids.discard(btn_id)
            tile.set_selected(False)
        else:
            self._selected_ids.add(btn_id)
            tile.set_selected(True)

    def _clear_selection(self):
        for btn_id in list(self._selected_ids):
            tile = self._tiles.get(btn_id)
            if tile:
                tile.set_selected(False)
        self._selected_ids.clear()
        self._update_selection_ui()

    def _update_selection_ui(self):
        n = len(self._selected_ids)
        self._sel_bar.setVisible(n > 0)
        if n > 0:
            self._sel_count_lbl.setText(_(f"{n} selected"))

    def _on_rubber_band_select(self, rect: QRect):
        if not self._is_pro():
            return
        for btn_id, tile in self._tiles.items():
            tile_rect = QRect(tile.pos(), tile.size())
            if rect.intersects(tile_rect):
                if btn_id not in self._selected_ids:
                    self._selected_ids.add(btn_id)
                    tile.set_selected(True)
        self._update_selection_ui()

    def _on_sel_change_category(self):
        from PySide6.QtWidgets import QInputDialog
        cat, ok = QInputDialog.getText(self, _("Change category"), _("New category name:"))
        if not ok:
            return
        buttons = self._config.load_buttons()
        for btn in buttons:
            if btn.id in self._selected_ids:
                btn.category = cat
                self._config.update_button(btn)
        self._clear_selection()
        self.populate_grid()

    def _on_sel_change_machine(self):
        from PySide6.QtWidgets import QInputDialog
        machines = self._config.load_machines()
        if not machines:
            self.show_toast(_("No machines configured"))
            return
        labels = [_("Local (no machine)")] + [m.name for m in machines]
        label, ok = QInputDialog.getItem(
            self, _("Change machine"),
            _("Assign the selected buttons to a machine."),
            labels, 0, False,
        )
        if not ok:
            return
        idx = labels.index(label)
        machine_ids: list[str] = [] if idx == 0 else [machines[idx - 1].id]
        ids = set(self._selected_ids)
        buttons = self._config.load_buttons()
        for btn in buttons:
            if btn.id in ids:
                btn.machine_ids = list(machine_ids)
        self._config.save_buttons(buttons)
        self._clear_selection()
        self.populate_grid()

    def _on_sel_delete(self):
        n = len(self._selected_ids)
        answer = QMessageBox.question(
            self,
            _("Delete buttons"),
            _(f"Delete {n} selected button(s)?"),
            QMessageBox.Yes | QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            for btn_id in list(self._selected_ids):
                self._config.delete_button(btn_id)
            self._clear_selection()
            self.populate_grid()

    # ── Toasts ────────────────────────────────────────────────────────────────

    def show_toast(self, message: str, duration_ms: int = 3000):
        self.statusBar().showMessage(message, duration_ms)
