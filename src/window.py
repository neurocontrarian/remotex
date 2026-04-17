import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, GObject, GLib

from models.config import ConfigManager
from models.command_button import CommandButton
from button_tile import ButtonTile
from services.executor import CommandExecutor, ExecutionResult
from dialogs.confirm_dialog import show_confirm_dialog
from dialogs.output_dialog import show_output_dialog
from dialogs.machines_list_dialog import show_machines_list
from dialogs.command_dialog import show_command_dialog
from dialogs.machine_picker_dialog import show_machine_picker
from pro.license import is_pro_active, FREE_BUTTON_LIMIT, PRO_INFO_URL, PRO_BUY_URL
from i18n import _


@Gtk.Template(resource_path='/com/github/remotex/RemoteX/ui/window.ui')
class RemotexWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'RemotexWindow'

    header_bar = Gtk.Template.Child()
    add_button = Gtk.Template.Child()
    menu_button = Gtk.Template.Child()
    search_button = Gtk.Template.Child()
    search_bar = Gtk.Template.Child()
    search_entry = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    main_stack = Gtk.Template.Child()
    flow_box = Gtk.Template.Child()
    grid_overlay = Gtk.Template.Child()
    placeholder_page = Gtk.Template.Child()
    toolbar_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._config = ConfigManager()
        self._executor = CommandExecutor(self._config)
        self._search_text = ''
        self._active_category: str | None = None  # None = "All"
        self._cat_buttons: list[Gtk.ToggleButton] = []
        self._updating_cats = False
        self._tiles: dict[str, ButtonTile] = {}
        self._custom_css_provider = None
        # ── Multi-select state ───────────────────────────────────────────
        self._select_mode = False
        self._selected_ids: set[str] = set()
        self._rb_active = False
        self._rb_start_fb = (0.0, 0.0)
        self._rb_current_fb = (0.0, 0.0)
        self._rb_da = None
        self._select_button = None
        self._action_bar_revealer = None
        self._select_count_label = None
        self._settings = self._load_settings()
        self._category_revealer = self._build_category_revealer()
        self.toolbar_view.add_top_bar(self._category_revealer)
        self._setup_window_actions()
        self._connect_signals()
        if self._settings:
            self._settings.connect('changed::hidden-categories', self._on_hidden_categories_changed)
            self._settings.connect('changed::button-size', lambda s, k: self.populate_grid())
            self._settings.connect('changed::grid-columns', lambda s, k: self.populate_grid())
            self._settings.connect('changed::always-on-top', self._on_always_on_top_changed)
            self._settings.connect('changed::button-theme', lambda s, k: self._apply_button_theme())
            self._settings.connect('changed::custom-theme-path', lambda s, k: self._apply_button_theme())
            self._settings.connect('changed::color-scheme', lambda s, k: self._apply_color_scheme())
        self._restore_window_state()
        self._apply_startup_desktop_settings()
        self._apply_color_scheme()
        self._apply_button_theme()
        self.populate_grid()
        self._build_select_ui()
        GLib.idle_add(self._check_license_expiry)

    def _load_settings(self):
        try:
            return Gio.Settings.new('com.github.remotex.RemoteX')
        except Exception:
            return None

    def _restore_window_state(self):
        if not self._settings:
            return
        width = self._settings.get_int('window-width')
        height = self._settings.get_int('window-height')
        self.set_default_size(width, height)
        if self._settings.get_boolean('window-maximized'):
            self.maximize()

    def _save_window_state(self):
        if not self._settings:
            return
        maximized = self.is_maximized()
        self._settings.set_boolean('window-maximized', maximized)
        if not maximized:
            self._settings.set_int('window-width', self.get_width())
            self._settings.set_int('window-height', self.get_height())

    def _apply_button_theme(self):
        from pro.license import is_pro_active
        from pathlib import Path
        _themes = ("bold", "cards", "phone", "neon", "retro", "custom")
        for t in _themes:
            self.remove_css_class(f"theme-{t}")

        # Remove previous custom CSS provider
        if self._custom_css_provider is not None:
            try:
                display = self.get_display()
                if display:
                    Gtk.StyleContext.remove_provider_for_display(display, self._custom_css_provider)
            except Exception:
                pass
            self._custom_css_provider = None

        theme = "bold"
        if self._settings and is_pro_active():
            theme = self._settings.get_string('button-theme')

        if theme == "custom" and is_pro_active() and self._settings:
            path = self._settings.get_string('custom-theme-path')
            if path and Path(path).is_file():
                provider = Gtk.CssProvider()
                try:
                    provider.load_from_path(path)
                    display = self.get_display()
                    if display:
                        Gtk.StyleContext.add_provider_for_display(
                            display, provider,
                            Gtk.STYLE_PROVIDER_PRIORITY_USER,
                        )
                    self._custom_css_provider = provider
                    self.add_css_class("theme-custom")
                    return
                except Exception:
                    pass
            # Fallback if path missing or CSS error
            theme = "bold"

        self.add_css_class(f"theme-{theme}")

    def _apply_color_scheme(self):
        from gi.repository import Adw
        scheme_map = {
            "system": Adw.ColorScheme.DEFAULT,
            "light": Adw.ColorScheme.FORCE_LIGHT,
            "dark": Adw.ColorScheme.FORCE_DARK,
        }
        scheme = self._settings.get_string('color-scheme') if self._settings else "system"
        Adw.StyleManager.get_default().set_color_scheme(scheme_map.get(scheme, Adw.ColorScheme.DEFAULT))

    def _apply_grid_settings(self):
        cols = self._settings.get_int('grid-columns') if self._settings else 4
        self.flow_box.set_min_children_per_line(cols)
        self.flow_box.set_max_children_per_line(cols)

    # ── Category bar ────────────────────────────────────────────────────

    def _build_category_revealer(self) -> Gtk.Revealer:
        revealer = Gtk.Revealer(
            transition_type=Gtk.RevealerTransitionType.SLIDE_DOWN,
            reveal_child=False,
        )
        scroll = Gtk.ScrolledWindow(
            hscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
            vscrollbar_policy=Gtk.PolicyType.NEVER,
            height_request=48,
        )
        self._cat_box = Gtk.Box(
            spacing=6,
            margin_start=12, margin_end=12,
            margin_top=6, margin_bottom=6,
        )
        scroll.set_child(self._cat_box)
        revealer.set_child(scroll)
        return revealer

    def _get_hidden_categories(self) -> set[str]:
        if self._settings:
            return set(self._settings.get_strv('hidden-categories'))
        return set()

    def _on_hidden_categories_changed(self, settings, key):
        buttons = self._config.load_buttons()
        hidden = self._get_hidden_categories()
        if self._active_category in hidden:
            self._active_category = None
        self._refresh_category_bar(buttons)
        self.flow_box.invalidate_filter()

    def _refresh_category_bar(self, buttons: list[CommandButton]):
        hidden = self._get_hidden_categories()
        categories = sorted({b.category for b in buttons if b.category and b.category not in hidden})

        # Clear existing buttons
        self._cat_buttons.clear()
        while child := self._cat_box.get_first_child():
            self._cat_box.remove(child)

        if not categories:
            self._category_revealer.set_reveal_child(False)
            self._active_category = None
            return

        self._category_revealer.set_reveal_child(True)

        all_btn = Gtk.ToggleButton(label=_("All"))
        all_btn.add_css_class("pill")
        all_btn.set_active(self._active_category is None)
        all_btn.connect('toggled', self._on_cat_toggled, None)
        self._cat_box.append(all_btn)
        self._cat_buttons.append(all_btn)

        for cat in categories:
            btn = Gtk.ToggleButton(label=_(cat))
            btn.add_css_class("pill")
            btn.set_active(self._active_category == cat)
            btn.connect('toggled', self._on_cat_toggled, cat)
            self._attach_cat_right_click(btn, cat)
            self._cat_box.append(btn)
            self._cat_buttons.append(btn)

        # Ensure exactly one is active
        if self._active_category not in ([None] + categories):
            self._active_category = None
            all_btn.set_active(True)

    def _on_cat_toggled(self, btn: Gtk.ToggleButton, category: str | None):
        if self._updating_cats:
            return
        if not btn.get_active():
            # Prevent deselecting without selecting another
            self._updating_cats = True
            btn.set_active(True)
            self._updating_cats = False
            return
        self._updating_cats = True
        for b in self._cat_buttons:
            if b is not btn:
                b.set_active(False)
        self._updating_cats = False
        self._active_category = category
        self.flow_box.invalidate_filter()

    def _attach_cat_right_click(self, btn: Gtk.ToggleButton, category: str):
        gesture = Gtk.GestureClick(button=3)
        gesture.connect('pressed', self._on_cat_right_click, btn, category)
        btn.add_controller(gesture)

    def _on_cat_right_click(self, gesture, n_press, x, y, pill: Gtk.ToggleButton, category: str):
        gesture.set_state(Gtk.EventSequenceState.CLAIMED)
        hidden = self._get_hidden_categories()
        is_hidden = category in hidden

        popover = Gtk.Popover()
        popover.set_parent(pill)
        popover.connect('closed', lambda p: p.unparent())

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_size_request(180, -1)

        def menu_btn(label_text, icon_name, callback, destructive=False):
            b = Gtk.Button()
            b.add_css_class("flat")
            inner = Gtk.Box(spacing=8,
                            margin_start=8, margin_end=8,
                            margin_top=4, margin_bottom=4)
            lbl = Gtk.Label(label=label_text, xalign=0, hexpand=True)
            if destructive:
                lbl.add_css_class("error")
            inner.append(Gtk.Image(icon_name=icon_name))
            inner.append(lbl)
            b.set_child(inner)
            b.connect("clicked", lambda _: (popover.popdown(), callback()))
            return b

        if is_hidden:
            box.append(menu_btn(
                _("Show category"), "view-reveal-symbolic",
                lambda: self._set_category_hidden(category, False),
            ))
        else:
            box.append(menu_btn(
                _("Hide category"), "view-conceal-symbolic",
                lambda: self._set_category_hidden(category, True),
            ))

        popover.set_child(box)
        rect = Gdk.Rectangle()
        rect.x = int(x)
        rect.y = int(y)
        rect.width = 0
        rect.height = 0
        popover.set_pointing_to(rect)
        popover.popup()

    def _set_category_hidden(self, category: str, hide: bool):
        if not self._settings:
            return
        current = set(self._settings.get_strv('hidden-categories'))
        if hide:
            current.add(category)
        else:
            current.discard(category)
        self._settings.set_strv('hidden-categories', sorted(current))

    # ── Grid ─────────────────────────────────────────────────────────────

    def _apply_startup_desktop_settings(self):
        if self._settings and self._settings.get_boolean('always-on-top'):
            # Defer until realize so the GDK surface exists
            self.connect('realize', self._on_realize)

    def _on_realize(self, _):
        self._apply_always_on_top(True)

    def _apply_always_on_top(self, enabled: bool):
        """Set always-on-top via wmctrl (X11). No-op on Wayland or if wmctrl missing."""
        import subprocess
        action = 'add' if enabled else 'remove'
        try:
            xid = None
            try:
                from gi.repository import GdkX11
                surface = self.get_surface()
                if isinstance(surface, GdkX11.X11Surface):
                    xid = surface.get_xid()
            except Exception:
                pass
            if xid:
                cmd = ['wmctrl', '-i', '-r', hex(xid), '-b', f'{action},above']
            else:
                cmd = ['wmctrl', '-r', 'RemoteX', '-b', f'{action},above']
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            self.show_toast(_("Install wmctrl to use 'Always on top'"))
        except Exception:
            pass

    def _on_always_on_top_changed(self, settings, key):
        val = settings.get_boolean(key)
        self._apply_always_on_top(val)
        action = self.lookup_action('always-on-top')
        if action:
            action.set_state(GLib.Variant('b', val))

    def _setup_window_actions(self):
        add_button_action = Gio.SimpleAction.new('add-button', None)
        add_button_action.connect('activate', self._on_add_button)
        self.add_action(add_button_action)

        always_on_top_val = self._settings.get_boolean('always-on-top') if self._settings else False
        always_on_top_action = Gio.SimpleAction.new_stateful(
            'always-on-top', None, GLib.Variant('b', always_on_top_val)
        )
        always_on_top_action.connect('activate', self._on_toggle_always_on_top)
        self.add_action(always_on_top_action)

    def _on_toggle_always_on_top(self, action, param):
        new_val = not action.get_state().get_boolean()
        if self._settings:
            self._settings.set_boolean('always-on-top', new_val)
        else:
            action.set_state(GLib.Variant('b', new_val))
            self._apply_always_on_top(new_val)

    def _connect_signals(self):
        self.search_entry.connect('search-changed', self._on_search_changed)
        self.connect('close-request', lambda _: self._save_window_state() or False)

    def _update_add_button_state(self):
        if is_pro_active():
            self.add_button.set_tooltip_text(_("Add a button (Ctrl+N)"))
        else:
            count = self._config.count_custom_buttons()
            remaining = FREE_BUTTON_LIMIT - count
            if remaining > 0:
                self.add_button.set_tooltip_text(
                    _("Add a button (Ctrl+N) — {remaining} of {limit} free slots remaining").format(
                        remaining=remaining, limit=FREE_BUTTON_LIMIT)
                )
            else:
                self.add_button.set_tooltip_text(
                    _("Button limit reached — upgrade to Pro for unlimited buttons")
                )

    def populate_grid(self):
        """Load buttons from config and rebuild the FlowBox grid."""
        while child := self.flow_box.get_first_child():
            self.flow_box.remove(child)
        self._tiles.clear()

        self._update_add_button_state()

        buttons = self._config.load_buttons()
        self._refresh_category_bar(buttons)
        self._apply_grid_settings()

        if not buttons:
            self.main_stack.set_visible_child_name('empty')
            return

        self.main_stack.set_visible_child_name('grid')
        size = self._settings.get_string('button-size') if self._settings else "medium"
        for btn in buttons:
            tile = ButtonTile(btn, size=size)
            tile.set_halign(Gtk.Align.CENTER)
            tile.set_valign(Gtk.Align.CENTER)
            tile.connect('clicked', self._on_tile_clicked)
            self._attach_tile_controllers(tile)
            self.flow_box.append(tile)
            self._tiles[btn.id] = tile

        self.flow_box.set_filter_func(self._filter_func)

        # Restore visual selection for tiles that still exist
        self._selected_ids = {bid for bid in self._selected_ids if bid in self._tiles}
        for bid in self._selected_ids:
            self._tiles[bid].set_selected(True)
        if hasattr(self, '_action_bar_revealer') and self._action_bar_revealer:
            self._action_bar_revealer.set_reveal_child(
                self._select_mode and bool(self._selected_ids)
            )

    # ── Tile controllers (right-click + drag-and-drop) ───────────────────

    def _attach_tile_controllers(self, tile: ButtonTile):
        right_click = Gtk.GestureClick(button=3)
        right_click.connect('pressed', self._on_tile_right_click, tile)
        tile.add_controller(right_click)

        drag_source = Gtk.DragSource(actions=Gdk.DragAction.MOVE)
        drag_source.connect('prepare', self._on_drag_prepare, tile)
        drag_source.connect('drag-begin', self._on_drag_begin, tile)
        drag_source.connect('drag-end', self._on_drag_end, tile)
        tile.add_controller(drag_source)

        drop_target = Gtk.DropTarget.new(GObject.TYPE_STRING, Gdk.DragAction.MOVE)
        drop_target.connect('drop', self._on_drop, tile)
        tile.add_controller(drop_target)

    # ── Right-click context menu ─────────────────────────────────────────

    def _on_tile_right_click(self, gesture, n_press, x, y, tile: ButtonTile):
        gesture.set_state(Gtk.EventSequenceState.CLAIMED)
        popover = self._build_context_popover(tile)
        rect = Gdk.Rectangle()
        rect.x = int(x)
        rect.y = int(y)
        rect.width = 0
        rect.height = 0
        popover.set_pointing_to(rect)
        popover.popup()

    def _build_context_popover(self, tile: ButtonTile) -> Gtk.Popover:
        popover = Gtk.Popover()
        popover.set_parent(tile)
        popover.connect('closed', lambda p: p.unparent())

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        box.set_size_request(160, -1)

        def menu_item(label_text, icon_name, callback, destructive=False, locked=False):
            btn = Gtk.Button()
            btn.add_css_class("flat")
            inner = Gtk.Box(spacing=8,
                            margin_start=8, margin_end=8,
                            margin_top=4, margin_bottom=4)
            lbl = Gtk.Label(label=label_text, xalign=0, hexpand=True)
            if destructive:
                lbl.add_css_class("error")
            inner.append(Gtk.Image(icon_name="changes-prevent-symbolic" if locked else icon_name))
            inner.append(lbl)
            if locked:
                badge = Gtk.Label(label=_("Pro"))
                badge.add_css_class("caption")
                badge.add_css_class("dim-label")
                inner.append(badge)
            btn.set_child(inner)
            btn.connect("clicked", lambda b: (popover.popdown(), callback()))
            return btn

        is_default_locked = tile.command_button.is_default and not is_pro_active()

        edit_btn = menu_item(_("Edit"), "document-edit-symbolic",
                             lambda: self._on_edit_tile(tile),
                             locked=is_default_locked)
        if is_default_locked:
            edit_btn.set_sensitive(False)
            edit_btn.set_tooltip_text(_("Editing default buttons requires RemoteX Pro"))
        box.append(edit_btn)
        box.append(menu_item(_("Duplicate"), "edit-copy-symbolic",
                             lambda: self._on_duplicate_tile(tile)))

        # Category assignment section
        all_buttons = self._config.load_buttons()
        categories = sorted({b.category for b in all_buttons if b.category})
        if categories:
            box.append(Gtk.Separator())
            move_lbl = Gtk.Label(label=_("Move to category"), xalign=0)
            move_lbl.add_css_class("caption")
            move_lbl.add_css_class("dim-label")
            move_lbl.set_margin_start(12)
            move_lbl.set_margin_top(4)
            move_lbl.set_margin_bottom(2)
            box.append(move_lbl)

            for cat in categories:
                if cat != tile.command_button.category:
                    box.append(menu_item(_(cat), "folder-symbolic",
                                         lambda c=cat: self._assign_category(tile, c)))

        box.append(Gtk.Separator())
        box.append(menu_item(_("Delete"), "user-trash-symbolic",
                             lambda: self._on_delete_tile(tile),
                             destructive=True))

        popover.set_child(box)
        return popover

    def _assign_category(self, tile: ButtonTile, category: str):
        tile.command_button.category = category
        buttons = self._config.load_buttons()
        for b in buttons:
            if b.id == tile.command_button.id:
                b.category = category
                break
        self._config.save_buttons(buttons)
        self.populate_grid()

    def _on_edit_tile(self, tile: ButtonTile):
        show_command_dialog(self, self._config, button=tile.command_button,
                            on_saved=self.populate_grid)

    def _on_duplicate_tile(self, tile: ButtonTile):
        if not is_pro_active():
            count = self._config.count_custom_buttons()
            if count >= FREE_BUTTON_LIMIT:
                self._show_pro_limit_dialog(
                    _("Button limit reached"),
                    _("The free tier allows up to {limit} custom buttons.\n"
                      "Upgrade to RemoteX Pro for unlimited buttons.").format(
                        limit=FREE_BUTTON_LIMIT),
                )
                return
        src = tile.command_button
        dup = CommandButton(
            name=f"{src.name} (copy)",
            command=src.command,
            machine_ids=list(src.machine_ids),
            icon_name=src.icon_name,
            color=src.color,
            text_color=src.text_color,
            confirm_before_run=src.confirm_before_run,
            show_output=src.show_output,
            execution_mode=src.execution_mode,
            run_as_user=src.run_as_user,
            category=src.category,
            tooltip=src.tooltip,
            hide_label=src.hide_label,
            hide_icon=src.hide_icon,
        )
        self._config.add_button(dup)
        self.populate_grid()
        self.show_toast(_('Duplicated "{name}"').format(name=src.name))

    def _on_delete_tile(self, tile: ButtonTile):
        button = tile.command_button
        confirm = Adw.AlertDialog(
            heading=_('Delete "{name}"?').format(name=button.name),
            body=_("This button will be permanently removed."),
        )
        confirm.add_response("cancel", _("Cancel"))
        confirm.add_response("delete", _("Delete"))
        confirm.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        confirm.set_default_response("cancel")
        confirm.set_close_response("cancel")

        def on_response(dlg, response):
            if response == "delete":
                self._config.delete_button(button.id)
                self.populate_grid()

        confirm.connect("response", on_response)
        confirm.present(self)

    # ── Drag-and-drop reordering ─────────────────────────────────────────

    def _on_drag_prepare(self, source, x, y, tile: ButtonTile):
        if self._select_mode:
            return None
        return Gdk.ContentProvider.new_for_value(tile.command_button.id)

    def _on_drag_begin(self, source, drag, tile: ButtonTile):
        tile.add_css_class('dragging')
        paintable = Gtk.WidgetPaintable(widget=tile)
        source.set_icon(paintable, int(tile.get_width() / 2), int(tile.get_height() / 2))

    def _on_drag_end(self, source, drag, delete_data, tile: ButtonTile):
        tile.remove_css_class('dragging')

    def _on_drop(self, target, value, x, y, tile: ButtonTile) -> bool:
        dragged_id = value
        target_id = tile.command_button.id
        if dragged_id == target_id:
            return False

        buttons = self._config.load_buttons()
        dragged = next((b for b in buttons if b.id == dragged_id), None)
        dropped_on = next((b for b in buttons if b.id == target_id), None)
        if dragged is None or dropped_on is None:
            return False

        dragged.position, dropped_on.position = dropped_on.position, dragged.position
        self._config.save_buttons(buttons)
        self.populate_grid()
        return True

    # ── FlowBox filter ───────────────────────────────────────────────────

    def _filter_func(self, child: Gtk.FlowBoxChild) -> bool:
        tile = child.get_child()
        if not isinstance(tile, ButtonTile):
            return True

        if tile.command_button.category in self._get_hidden_categories():
            return False

        if self._active_category is not None:
            if tile.command_button.category != self._active_category:
                return False

        if self._search_text:
            return self._search_text.lower() in tile.command_button.name.lower()

        return True

    def _on_search_changed(self, entry: Gtk.SearchEntry):
        self._search_text = entry.get_text()
        self.flow_box.invalidate_filter()

    # ── Button execution ─────────────────────────────────────────────────

    def _on_tile_clicked(self, tile: ButtonTile):
        if self._select_mode:
            return  # handled by capture gesture
        button = tile.command_button
        if button.confirm_before_run:
            show_confirm_dialog(self, button, lambda: self._pick_machine_and_run(tile, button))
        else:
            self._pick_machine_and_run(tile, button)

    def _pick_machine_and_run(self, tile: ButtonTile, button: CommandButton):
        """Resolve which machine(s) to use. Shows a picker if multiple targets."""
        candidates = button.machine_ids  # list of IDs; "" = local

        if not candidates:
            self._run_button(tile, button, None)
            return

        if len(candidates) == 1:
            self._run_button(tile, button, candidates[0])
            return

        # Multiple targets — build options and show picker
        all_machines = self._config.load_machines()
        options = []
        for mid in candidates:
            if mid == "":
                options.append(("", "Local (this machine)", "Run directly on this computer"))
            else:
                m = next((m for m in all_machines if m.id == mid), None)
                if m:
                    options.append((mid, m.name, f"{m.user}@{m.host}:{m.port}"))

        if len(options) > 1:
            show_machine_picker(
                self, options,
                lambda chosen_ids: self._run_on_machines(tile, button, chosen_ids),
            )
        elif options:
            self._run_button(tile, button, options[0][0])

    def _run_on_machines(self, tile: ButtonTile, button: CommandButton,
                         machine_ids: list[str]):
        """Run on multiple machines in parallel, one output window per result."""
        if len(machine_ids) == 1:
            self._run_button(tile, button, machine_ids[0])
            return

        all_machines = self._config.load_machines()
        pending = {"count": len(machine_ids)}
        tile.set_running(True)

        for machine_id in machine_ids:
            if machine_id == "":
                label = f"{button.name} — Local"
            else:
                m = next((m for m in all_machines if m.id == machine_id), None)
                label = f"{button.name} — {m.name}" if m else button.name

            def on_done(result, lbl=label):
                pending["count"] -= 1
                if pending["count"] == 0:
                    tile.set_running(False)
                    tile.flash_result(result.success)
                mode = button.execution_mode
                show_output = (
                    mode == "output"
                    or (mode == "" and button.show_output)
                    or not result.success
                )
                if show_output:
                    show_output_dialog(None, lbl, result)
                else:
                    self.show_toast(
                        f'{"✓" if result.success else "✗"}  {lbl}  ({result.duration_ms}ms)'
                    )

            self._executor.execute(button, on_done, machine_id)

    def _run_button(self, tile: ButtonTile, button: CommandButton,
                    machine_id: str | None = None):
        tile.set_running(True)
        self._executor.execute(
            button,
            lambda result: self._on_execution_done(tile, button, result),
            machine_id,
        )

    def _on_execution_done(self, tile: ButtonTile, button: CommandButton, result: ExecutionResult):
        tile.set_running(False)
        tile.flash_result(result.success)

        mode = button.execution_mode
        if mode == "terminal":
            # Terminal handles its own output; only show a toast on launch failure.
            if not result.success:
                show_output_dialog(self, button.name, result)
            return

        if result.success:
            self.show_toast(f'✓  {button.name}  ({result.duration_ms}ms)')
        else:
            self.show_toast(f'✗  {button.name} failed')

        show_output = (
            mode == "output"
            or (mode == "" and button.show_output)
            or not result.success
        )
        if show_output:
            show_output_dialog(self, button.name, result)

    # ── Dialogs ──────────────────────────────────────────────────────────

    def show_machines_dialog(self):
        show_machines_list(self, self._config)

    def _on_add_button(self, action, param):
        if not is_pro_active():
            count = self._config.count_custom_buttons()
            if count >= FREE_BUTTON_LIMIT:
                self._show_pro_limit_dialog(
                    _("Button limit reached"),
                    _("The free tier allows up to {limit} custom buttons.\n"
                      "Upgrade to RemoteX Pro for unlimited buttons.").format(
                        limit=FREE_BUTTON_LIMIT),
                )
                return
        show_command_dialog(self, self._config, on_saved=self.populate_grid)

    def _show_pro_limit_dialog(self, heading: str, body: str):
        dlg = Adw.AlertDialog(heading=heading, body=body)
        dlg.add_response("ok", _("OK"))
        dlg.add_response("pro", _("Get Pro →"))
        dlg.set_response_appearance("pro", Adw.ResponseAppearance.SUGGESTED)
        dlg.set_default_response("ok")
        dlg.set_close_response("ok")

        def on_response(d, response):
            if response == "pro":
                self._open_url(PRO_BUY_URL)

        dlg.connect("response", on_response)
        dlg.present(self)

    # ── Multi-select (Pro) ───────────────────────────────────────────────

    def _build_select_ui(self):
        if not is_pro_active():
            return
        self._build_select_button()
        self._build_action_bar()
        self._build_rubber_band_overlay()
        self._setup_selection_gestures()
        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.connect('key-pressed', self._on_select_key_pressed)
        self.add_controller(key_ctrl)

    def _build_select_button(self):
        btn = Gtk.ToggleButton()
        btn.set_icon_name("object-select-symbolic")
        btn.set_tooltip_text(_("Select multiple buttons"))
        btn.connect("toggled", self._on_select_button_toggled)
        self.header_bar.pack_end(btn)
        self._select_button = btn

    def _build_action_bar(self):
        revealer = Gtk.Revealer(
            transition_type=Gtk.RevealerTransitionType.SLIDE_UP,
            reveal_child=False,
        )
        action_bar = Gtk.ActionBar()

        self._select_count_label = Gtk.Label()
        self._select_count_label.add_css_class("caption")
        action_bar.pack_start(self._select_count_label)

        del_btn = Gtk.Button(label=_("Delete"))
        del_btn.add_css_class("destructive-action")
        del_btn.connect("clicked", self._on_select_delete)
        action_bar.pack_end(del_btn)

        machine_btn = Gtk.Button(label=_("Machine"))
        machine_btn.connect("clicked", self._on_select_change_machine)
        action_bar.pack_end(machine_btn)

        cat_btn = Gtk.Button(label=_("Category"))
        cat_btn.connect("clicked", self._on_select_change_category)
        action_bar.pack_end(cat_btn)

        revealer.set_child(action_bar)
        self.toolbar_view.add_bottom_bar(revealer)
        self._action_bar_revealer = revealer

    def _build_rubber_band_overlay(self):
        da = Gtk.DrawingArea()
        da.set_can_target(False)
        da.set_hexpand(True)
        da.set_vexpand(True)
        da.set_draw_func(self._draw_rubber_band)
        self.grid_overlay.add_overlay(da)
        self._rb_da = da

    def _setup_selection_gestures(self):
        # CAPTURE click: toggles tile selection in select mode (prevents tile execution)
        click = Gtk.GestureClick(button=1)
        click.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        click.connect('pressed', self._on_fb_pressed)
        self.flow_box.add_controller(click)

        # Drag: rubber-band on grid_overlay so empty margins are covered too
        drag = Gtk.GestureDrag(button=1)
        drag.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        drag.connect('drag-begin', self._on_rb_drag_begin)
        drag.connect('drag-update', self._on_rb_drag_update)
        drag.connect('drag-end', self._on_rb_drag_end)
        self.grid_overlay.add_controller(drag)

    def _on_select_key_pressed(self, ctrl, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape and self._select_mode:
            self._exit_select_mode()
            return True
        return False

    def _on_select_button_toggled(self, btn):
        if btn.get_active():
            self._enter_select_mode()
        else:
            self._exit_select_mode()

    def _enter_select_mode(self):
        if self._select_mode:
            return
        self._select_mode = True
        if self._select_button:
            self._select_button.set_active(True)
        if self._action_bar_revealer:
            self._action_bar_revealer.set_reveal_child(True)
        self._on_selection_changed()

    def _exit_select_mode(self):
        if not self._select_mode:
            return
        self._select_mode = False
        for tile in self._tiles.values():
            tile.set_selected(False)
        self._selected_ids.clear()
        if self._select_button:
            self._select_button.set_active(False)
        if self._action_bar_revealer:
            self._action_bar_revealer.set_reveal_child(False)

    def _toggle_tile_selection(self, btn_id: str):
        if btn_id in self._selected_ids:
            self._selected_ids.discard(btn_id)
            if tile := self._tiles.get(btn_id):
                tile.set_selected(False)
        else:
            self._selected_ids.add(btn_id)
            if tile := self._tiles.get(btn_id):
                tile.set_selected(True)
        self._on_selection_changed()

    def _on_selection_changed(self):
        n = len(self._selected_ids)
        if self._select_count_label:
            self._select_count_label.set_text(
                _("{n} selected").format(n=n) if n else _("No selection")
            )

    def _find_tile_ancestor(self, widget) -> ButtonTile | None:
        w = widget
        while w is not None:
            if isinstance(w, ButtonTile):
                return w
            w = w.get_parent()
        return None

    def _on_fb_pressed(self, gesture, n_press, x, y):
        if not self._select_mode:
            return
        picked = self.flow_box.pick(x, y, Gtk.PickFlags.DEFAULT)
        tile = self._find_tile_ancestor(picked)
        if tile:
            self._toggle_tile_selection(tile.command_button.id)
            gesture.set_state(Gtk.EventSequenceState.CLAIMED)

    def _on_rb_drag_begin(self, gesture, start_x, start_y):
        if not self._select_mode:
            gesture.set_state(Gtk.EventSequenceState.DENIED)
            return
        # Coords are in grid_overlay space — pick directly from there
        picked = self.grid_overlay.pick(start_x, start_y, Gtk.PickFlags.DEFAULT)
        if self._find_tile_ancestor(picked) is not None:
            gesture.set_state(Gtk.EventSequenceState.DENIED)
            return
        self._rb_active = True
        self._rb_start_fb = (start_x, start_y)
        self._rb_current_fb = (start_x, start_y)
        gesture.set_state(Gtk.EventSequenceState.CLAIMED)

    def _on_rb_drag_update(self, gesture, offset_x, offset_y):
        if not self._rb_active:
            return
        sx, sy = self._rb_start_fb
        self._rb_current_fb = (sx + offset_x, sy + offset_y)
        self._update_rb_selection()
        if self._rb_da:
            self._rb_da.queue_draw()

    def _on_rb_drag_end(self, gesture, offset_x, offset_y):
        if self._rb_active:
            self._rb_active = False
            if self._rb_da:
                self._rb_da.queue_draw()

    def _update_rb_selection(self):
        x1, y1 = self._rb_start_fb
        x2, y2 = self._rb_current_fb
        rx = min(x1, x2); ry = min(y1, y2)
        rw = abs(x2 - x1); rh = abs(y2 - y1)
        if rw < 5 and rh < 5:
            return

        from gi.repository import Graphene
        for btn_id, tile in self._tiles.items():
            p = Graphene.Point()
            p.x, p.y = 0.0, 0.0
            ok, tile_pos = tile.compute_point(self.grid_overlay, p)
            if not ok:
                continue
            tx, ty = tile_pos.x, tile_pos.y
            tw, th = tile.get_width(), tile.get_height()
            overlaps = tx < rx + rw and tx + tw > rx and ty < ry + rh and ty + th > ry
            if overlaps and btn_id not in self._selected_ids:
                self._selected_ids.add(btn_id)
                tile.set_selected(True)
        self._on_selection_changed()

    def _draw_rubber_band(self, da, cr, width, height):
        if not self._rb_active:
            return
        # Coords are already in grid_overlay space (same as DrawingArea overlay)
        x1, y1 = self._rb_start_fb
        x2, y2 = self._rb_current_fb
        rx = min(x1, x2); ry = min(y1, y2)
        rw = abs(x2 - x1); rh = abs(y2 - y1)

        cr.set_source_rgba(0.3, 0.5, 1.0, 0.12)
        cr.rectangle(rx, ry, rw, rh)
        cr.fill()
        cr.set_source_rgba(0.3, 0.5, 1.0, 0.75)
        cr.set_line_width(1.5)
        cr.rectangle(rx, ry, rw, rh)
        cr.stroke()

    # ── Group actions ─────────────────────────────────────────────────────

    def _on_select_delete(self, btn):
        if not self._selected_ids:
            return
        n = len(self._selected_ids)
        dlg = Adw.AlertDialog(
            heading=_("Delete {n} buttons?").format(n=n),
            body=_("These buttons will be permanently removed."),
        )
        dlg.add_response("cancel", _("Cancel"))
        dlg.add_response("delete", _("Delete"))
        dlg.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dlg.set_default_response("cancel")
        dlg.set_close_response("cancel")

        def on_response(d, response):
            if response == "delete":
                ids = set(self._selected_ids)
                self._exit_select_mode()
                buttons = self._config.load_buttons()
                self._config.save_buttons([b for b in buttons if b.id not in ids])
                self.populate_grid()
                self.show_toast(_("{n} buttons deleted").format(n=len(ids)))

        dlg.connect("response", on_response)
        dlg.present(self)

    def _on_select_change_category(self, btn):
        if not self._selected_ids:
            return
        all_buttons = self._config.load_buttons()
        categories = sorted({b.category for b in all_buttons if b.category})

        dlg = Adw.AlertDialog(
            heading=_("Change category"),
            body=_("Type a category name or choose an existing one."),
        )
        dlg.add_response("cancel", _("Cancel"))
        dlg.add_response("apply", _("Apply"))
        dlg.set_response_appearance("apply", Adw.ResponseAppearance.SUGGESTED)
        dlg.set_default_response("apply")
        dlg.set_close_response("cancel")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        entry = Gtk.Entry()
        entry.set_placeholder_text(_("Category name (empty = no category)"))
        box.append(entry)

        if categories:
            lbl = Gtk.Label(label=_("Or pick existing:"), xalign=0)
            lbl.add_css_class("caption")
            lbl.add_css_class("dim-label")
            box.append(lbl)
            for cat in categories:
                pill = Gtk.Button(label=cat)
                pill.add_css_class("pill")
                pill.connect("clicked", lambda b, c=cat: entry.set_text(c))
                box.append(pill)

        dlg.set_extra_child(box)

        def on_response(d, response):
            if response == "apply":
                cat = entry.get_text().strip()
                ids = set(self._selected_ids)
                self._exit_select_mode()
                buttons = self._config.load_buttons()
                for b in buttons:
                    if b.id in ids:
                        b.category = cat
                self._config.save_buttons(buttons)
                self.populate_grid()

        dlg.connect("response", on_response)
        dlg.present(self)

    def _on_select_change_machine(self, btn):
        if not self._selected_ids:
            return
        machines = self._config.load_machines()
        if not machines:
            self.show_toast(_("No machines configured"))
            return

        dlg = Adw.AlertDialog(
            heading=_("Change machine"),
            body=_("Assign the selected buttons to a machine."),
        )
        dlg.add_response("cancel", _("Cancel"))
        dlg.add_response("apply", _("Apply"))
        dlg.set_response_appearance("apply", Adw.ResponseAppearance.SUGGESTED)
        dlg.set_default_response("apply")
        dlg.set_close_response("cancel")

        model = Gtk.StringList()
        model.append(_("Local (no machine)"))
        for m in machines:
            model.append(m.name)

        combo = Gtk.DropDown()
        combo.set_model(model)
        combo.set_selected(0)
        dlg.set_extra_child(combo)

        def on_response(d, response):
            if response == "apply":
                idx = combo.get_selected()
                machine_ids = [] if idx == 0 else [machines[idx - 1].id]
                ids = set(self._selected_ids)
                self._exit_select_mode()
                buttons = self._config.load_buttons()
                for b in buttons:
                    if b.id in ids:
                        b.machine_ids = machine_ids
                self._config.save_buttons(buttons)
                self.populate_grid()

        dlg.connect("response", on_response)
        dlg.present(self)

    def _check_license_expiry(self):
        """Show a toast if a yearly license is expiring within 30 days."""
        try:
            from pro.license import get_license_info
            info = get_license_info()
            if info.get('expiry_warning'):
                days = info['days_until_expiry']
                self.show_toast(
                    _("Pro license expires in {days} days — renew in Preferences").format(days=days)
                )
            elif info.get('is_expired'):
                self.show_toast(_("Pro license expired — free tier limits now apply"))
        except Exception:
            pass
        return False  # GLib.idle_add one-shot

    def _open_url(self, url: str):
        """Open a URL in the default browser using GTK4 UriLauncher."""
        try:
            launcher = Gtk.UriLauncher(uri=url)
            launcher.launch(self, None, None)
        except Exception:
            import subprocess
            subprocess.Popen(
                ["/usr/bin/xdg-open", url],
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def show_toast(self, message: str):
        toast = Adw.Toast(title=message)
        self.toast_overlay.add_toast(toast)
