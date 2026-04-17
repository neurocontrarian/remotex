import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk
from typing import Callable

from models.command_button import CommandButton
from models.config import ConfigManager
from button_tile import resolve_icon, _FALLBACK_ICON
from i18n import _

# Module-level cache — built once on first Browse click, reused after.
_icon_cache: list[str] | None = None

# GNOME color palette (40 colors, 5 per row)
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


def _build_icon_cache() -> list[str]:
    """Return icon names: bundled Bootstrap Icons first, then renderable system icons."""
    global _icon_cache
    if _icon_cache is not None:
        return _icon_cache

    # Bundled Bootstrap Icons (always available, shown first)
    bundled: list[str] = []
    try:
        from utils.icon_loader import bundled_icon_names
        bundled = sorted(bundled_icon_names())
    except Exception:
        pass

    # System theme icons that actually render on this machine
    system: list[str] = []
    display = Gdk.Display.get_default()
    if display is not None:
        theme = Gtk.IconTheme.get_for_display(display)
        bundled_set = set(bundled)
        system = sorted(
            name for name in theme.get_icon_names()
            if name not in bundled_set and resolve_icon(name) != _FALLBACK_ICON
        )

    _icon_cache = bundled + system
    return _icon_cache


def show_command_dialog(parent, config: ConfigManager, button: CommandButton | None = None,
                        on_saved: Callable | None = None):
    """Open the Add/Edit button dialog. button=None means 'add new'."""
    is_edit = button is not None
    from utils.desktop import make_floating_window
    dlg = _CommandDialog(parent, config, button, on_saved, is_edit)
    make_floating_window(dlg.dialog, parent, 480, 660)
    dlg.dialog.present()


class _CommandDialog:
    def __init__(self, parent, config: ConfigManager, button: CommandButton | None,
                 on_saved: Callable | None, is_edit: bool):
        self._parent = parent
        self._config = config
        self._button = button
        self._on_saved = on_saved
        self._is_edit = is_edit
        self._picker_search = ""
        self.dialog = Adw.Window(title=_("Edit Button") if is_edit else _("Add Button"))
        self._build_ui()
        self._populate_fields()

    def _build_ui(self):
        toolbar_view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)

        self._save_btn = Gtk.Button(label=_("Save"))
        self._save_btn.add_css_class("suggested-action")
        self._save_btn.connect("clicked", self._on_save)
        header.pack_end(self._save_btn)

        scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True,
                                    hscrollbar_policy=Gtk.PolicyType.NEVER)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24,
                      margin_top=16, margin_bottom=16,
                      margin_start=16, margin_end=16)

        # ── Button details ───────────────────────────────────────────────
        details_group = Adw.PreferencesGroup(title=_("Button"))
        box.append(details_group)

        self._name_row = Adw.EntryRow(title=_("Label"))
        details_group.add(self._name_row)

        self._command_row = Adw.EntryRow(title=_("Command"))
        details_group.add(self._command_row)

        machines = self._config.load_machines()

        machines_group = Adw.PreferencesGroup(title=_("Target machines"))
        machines_group.set_description(
            _("Select where this command can run.\n"
              "If multiple targets are selected, you will be asked which one to use at run time.")
        )
        box.append(machines_group)

        self._local_switch = Adw.SwitchRow(title=_("Local (this machine)"))
        self._local_switch.set_subtitle(_("Run directly on this computer"))
        self._local_switch.set_active(True)  # Default for new buttons
        machines_group.add(self._local_switch)

        self._machine_switches: list[tuple[str, Adw.SwitchRow]] = []
        for m in machines:
            row = Adw.SwitchRow(title=m.name)
            row.set_subtitle(f"{m.user}@{m.host}:{m.port}")
            machines_group.add(row)
            self._machine_switches.append((m.id, row))

        if machines:
            self._all_switch = Adw.SwitchRow(title=_("All machines"))
            self._all_switch.set_subtitle(_("Select / deselect all targets at once"))
            machines_group.add(self._all_switch)
            self._all_switch.connect("notify::active", self._on_all_switch_changed)
            self._local_switch.connect("notify::active", self._on_individual_switch_changed)
            for _mid, row in self._machine_switches:
                row.connect("notify::active", self._on_individual_switch_changed)
        else:
            self._all_switch = None
            hint = Adw.ActionRow(title=_("No remote machines configured"))
            hint.set_subtitle(_("Add machines via menu → Manage Machines"))
            machines_group.add(hint)

        # ── Appearance ───────────────────────────────────────────────────
        appearance_group = Adw.PreferencesGroup(title=_("Appearance"))
        box.append(appearance_group)

        icon_row = Adw.ActionRow(title=_("Icon"))
        icon_row.set_subtitle(_("Click Browse to pick visually, or type a name"))
        self._icon_preview = Gtk.Image(
            icon_name=_FALLBACK_ICON, pixel_size=24, valign=Gtk.Align.CENTER
        )
        icon_row.add_prefix(self._icon_preview)

        self._icon_entry = Gtk.Entry(
            valign=Gtk.Align.CENTER,
            hexpand=True,
            placeholder_text=_FALLBACK_ICON,
            width_chars=24,
        )
        self._icon_entry.connect("changed", self._on_icon_changed)
        icon_row.add_suffix(self._icon_entry)

        browse_btn = Gtk.Button(label=_("Browse"), valign=Gtk.Align.CENTER)
        browse_btn.add_css_class("flat")
        browse_btn.connect("clicked", self._on_browse_icon)
        icon_row.add_suffix(browse_btn)
        appearance_group.add(icon_row)

        bg_row, self._bg_color_entry = self._build_color_row(_("Background color"))
        appearance_group.add(bg_row)

        text_row, self._text_color_entry = self._build_color_row(_("Text color"))
        appearance_group.add(text_row)

        self._hide_label_row = Adw.SwitchRow(title=_("Hide label"))
        self._hide_label_row.set_subtitle(_("Show icon only — no text below"))
        appearance_group.add(self._hide_label_row)

        self._hide_icon_row = Adw.SwitchRow(title=_("Hide icon"))
        self._hide_icon_row.set_subtitle(_("Show label only — no icon above"))
        appearance_group.add(self._hide_icon_row)

        # ── Organisation ─────────────────────────────────────────────────
        org_group = Adw.PreferencesGroup(title=_("Organisation"))
        box.append(org_group)

        self._category_row = Adw.EntryRow(title=_("Category"))
        org_group.add(self._category_row)

        # ── Behaviour ────────────────────────────────────────────────────
        behaviour_group = Adw.PreferencesGroup(title=_("Behaviour"))
        box.append(behaviour_group)

        self._tooltip_row = Adw.EntryRow(title=_("Tooltip"))
        self._tooltip_row.set_tooltip_text(
            _("Text shown when hovering over the button.\n"
              "Leave empty to show the command automatically.")
        )
        behaviour_group.add(self._tooltip_row)

        self._confirm_row = Adw.SwitchRow(title=_("Confirm before running"))
        self._confirm_row.set_subtitle(_("Show a confirmation popup before executing"))
        self._confirm_row.set_tooltip_text(
            _("When enabled, a popup asks 'Run this command?' before anything happens.\n"
              "Recommended for destructive operations like reboots or file deletions.")
        )
        behaviour_group.add(self._confirm_row)

        exec_mode_model = Gtk.StringList()
        self._exec_mode_values = ["silent", "output", "terminal"]
        exec_mode_labels = [
            _("Silent (toast only)"),
            _("Show output"),
            _("Open in terminal"),
        ]
        for label in exec_mode_labels:
            exec_mode_model.append(label)

        self._exec_mode_row = Adw.ComboRow(title=_("Execution mode"))
        self._exec_mode_row.set_subtitle(
            _("How to display results after the command runs")
        )
        self._exec_mode_row.set_tooltip_text(
            _("Silent: only a brief toast notification\n"
              "Show output: open a window with stdout/stderr\n"
              "Open in terminal: run in a new terminal window (supports sudo, interactive commands)")
        )
        self._exec_mode_row.set_model(exec_mode_model)
        behaviour_group.add(self._exec_mode_row)

        self._run_as_user_row = Adw.EntryRow(title=_("Run as user"))
        self._run_as_user_row.set_tooltip_text(
            _("Terminal + remote machine only: execute the command as a different user\n"
              "on the remote machine via sudo -u (e.g. deploy-user).\n"
              "Leave empty to run as the SSH user.")
        )
        behaviour_group.add(self._run_as_user_row)

        scroll.set_child(box)
        toolbar_view.set_content(scroll)
        self.dialog.set_content(toolbar_view)

    def _populate_fields(self):
        if not self._button:
            return
        self._name_row.set_text(self._button.name)
        self._command_row.set_text(self._button.command)

        machine_ids_set = set(self._button.machine_ids)
        self._local_switch.set_active("" in machine_ids_set or not machine_ids_set)
        for mid, row in self._machine_switches:
            row.set_active(mid in machine_ids_set)

        icon = self._button.icon_name or _FALLBACK_ICON
        self._icon_entry.set_text(icon)
        self._set_image_icon(self._icon_preview, icon)

        if self._button.color:
            self._bg_color_entry.set_text(self._button.color)

        if self._button.text_color:
            self._text_color_entry.set_text(self._button.text_color)

        self._hide_label_row.set_active(self._button.hide_label)
        self._hide_icon_row.set_active(self._button.hide_icon)

        if self._button.category:
            self._category_row.set_text(self._button.category)

        if self._button.tooltip:
            self._tooltip_row.set_text(self._button.tooltip)
        self._confirm_row.set_active(self._button.confirm_before_run)
        # Resolve execution mode: explicit mode takes precedence; fall back from show_output
        mode = self._button.execution_mode
        if not mode:
            mode = "output" if self._button.show_output else "silent"
        idx = self._exec_mode_values.index(mode) if mode in self._exec_mode_values else 0
        self._exec_mode_row.set_selected(idx)
        if self._button.run_as_user:
            self._run_as_user_row.set_text(self._button.run_as_user)

    # ── Color picker ─────────────────────────────────────────────────────

    def _build_color_row(self, title: str):
        """ActionRow with a CSS color swatch + hex Entry + GNOME palette popover."""
        row = Adw.ActionRow(title=title)

        swatch = Gtk.Button(valign=Gtk.Align.CENTER)
        swatch.set_size_request(32, 32)
        swatch.set_tooltip_text(_("Click to open color palette"))
        swatch_provider = Gtk.CssProvider()
        swatch.get_style_context().add_provider(
            swatch_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        row.add_prefix(swatch)

        hex_entry = Gtk.Entry(
            valign=Gtk.Align.CENTER,
            placeholder_text="#rrggbb",
            width_chars=9,
            max_width_chars=9,
        )
        hex_entry.add_css_class("monospace")

        clear_btn = Gtk.Button(
            icon_name="edit-clear-symbolic",
            valign=Gtk.Align.CENTER,
            tooltip_text=_("Clear (use theme default)"),
        )
        clear_btn.add_css_class("flat")
        clear_btn.add_css_class("circular")

        row.add_suffix(hex_entry)
        row.add_suffix(clear_btn)

        def update_swatch(color: str):
            if color and color.startswith("#"):
                css = (f"button {{ background: {color}; min-width: 32px;"
                       f" min-height: 32px; padding: 0; border-radius: 4px; }}")
            else:
                css = ("button { background: rgba(128,128,128,0.2); min-width: 32px;"
                       " min-height: 32px; padding: 0; border-radius: 4px; }")
            swatch_provider.load_from_string(css)

        update_swatch("")

        hex_entry.connect('changed', lambda e: update_swatch(e.get_text().strip()))
        clear_btn.connect('clicked', lambda _: hex_entry.set_text(""))
        swatch.connect('clicked', lambda _: self._show_color_popover(swatch, hex_entry))

        return row, hex_entry

    def _show_color_popover(self, parent_widget, hex_entry: Gtk.Entry):
        popover = Gtk.Popover()
        popover.set_parent(parent_widget)
        popover.set_has_arrow(True)
        popover.connect('closed', lambda p: p.unparent())

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8,
                      margin_top=8, margin_bottom=8,
                      margin_start=8, margin_end=8)

        flow = Gtk.FlowBox(
            max_children_per_line=5, min_children_per_line=5,
            selection_mode=Gtk.SelectionMode.NONE,
            homogeneous=True, row_spacing=4, column_spacing=4,
        )

        for color in _GNOME_PALETTE:
            btn = Gtk.Button()
            btn.set_size_request(28, 28)
            btn.set_tooltip_text(color)
            p = Gtk.CssProvider()
            p.load_from_string(
                f"button {{ background: {color}; min-width: 28px;"
                f" min-height: 28px; padding: 0; border-radius: 4px; }}"
            )
            btn.get_style_context().add_provider(p, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            btn.connect('clicked', lambda _, c=color: (
                hex_entry.set_text(c), popover.popdown()
            ))
            flow.append(btn)

        box.append(flow)
        box.append(Gtk.Separator())

        custom_box = Gtk.Box(spacing=6)
        custom_entry = Gtk.Entry(
            placeholder_text=_("Custom: #rrggbb"),
            hexpand=True,
            text=hex_entry.get_text(),
        )
        custom_entry.add_css_class("monospace")
        apply_btn = Gtk.Button(label=_("Apply"))
        apply_btn.add_css_class("suggested-action")

        def apply_custom(_):
            text = custom_entry.get_text().strip()
            rgba = Gdk.RGBA()
            if text and rgba.parse(text):
                hex_entry.set_text(text)
                popover.popdown()

        apply_btn.connect('clicked', apply_custom)
        custom_entry.connect('activate', apply_custom)
        custom_box.append(custom_entry)
        custom_box.append(apply_btn)
        box.append(custom_box)

        popover.set_child(box)
        popover.popup()

    # ── Icon picker ──────────────────────────────────────────────────────

    def _set_image_icon(self, image: Gtk.Image, icon_name: str, size: int = 24):
        """Set a Gtk.Image from an icon name, with Bootstrap Icons support."""
        try:
            from utils.icon_loader import load_icon_texture
            texture = load_icon_texture(icon_name, size)
            if texture:
                image.set_from_paintable(texture)
                image.set_pixel_size(size)
                return
        except Exception:
            pass
        image.set_from_icon_name(resolve_icon(icon_name))
        image.set_pixel_size(size)

    def _on_all_switch_changed(self, switch, _param):
        """When 'All machines' is toggled, set all individual switches to match."""
        active = switch.get_active()
        self._local_switch.handler_block_by_func(self._on_individual_switch_changed)
        self._local_switch.set_active(active)
        self._local_switch.handler_unblock_by_func(self._on_individual_switch_changed)
        for _, row in self._machine_switches:
            row.handler_block_by_func(self._on_individual_switch_changed)
            row.set_active(active)
            row.handler_unblock_by_func(self._on_individual_switch_changed)

    def _on_individual_switch_changed(self, switch, _param):
        """Update 'All machines' state when any individual switch changes."""
        if self._all_switch is None:
            return
        all_rows = [self._local_switch] + [r for _, r in self._machine_switches]
        all_on = all(r.get_active() for r in all_rows)
        self._all_switch.handler_block_by_func(self._on_all_switch_changed)
        self._all_switch.set_active(all_on)
        self._all_switch.handler_unblock_by_func(self._on_all_switch_changed)

    def _on_icon_changed(self, entry):
        icon_name = entry.get_text().strip() or _FALLBACK_ICON
        self._set_image_icon(self._icon_preview, icon_name)

    def _on_browse_icon(self, btn):
        popover = self._build_icon_picker(btn)
        popover.popup()

    def _build_icon_picker(self, parent_widget) -> Gtk.Popover:
        icons = _build_icon_cache()

        popover = Gtk.Popover()
        popover.set_parent(parent_widget)
        popover.set_has_arrow(False)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6,
                        margin_top=8, margin_bottom=8,
                        margin_start=8, margin_end=8)

        if not icons:
            outer.append(Gtk.Label(
                label=_("No renderable icons found on this system.\nType the icon name manually."),
                justify=Gtk.Justification.CENTER,
            ))
            popover.set_child(outer)
            return popover

        # Search bar
        search = Gtk.SearchEntry(placeholder_text=f"Search {len(icons)} icons…")
        outer.append(search)

        # Icon grid
        scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER, vexpand=True)
        scroll.set_size_request(340, 320)

        flow = Gtk.FlowBox(
            selection_mode=Gtk.SelectionMode.NONE,
            max_children_per_line=7,
            homogeneous=True,
            column_spacing=2, row_spacing=2,
        )

        try:
            from utils.icon_loader import load_icon_texture, bundled_icon_names
            _bundled_set = set(bundled_icon_names())
        except Exception:
            load_icon_texture = None
            _bundled_set = set()

        for icon_name in icons:
            ic_btn = Gtk.Button()
            ic_btn.add_css_class("flat")
            ic_btn.set_tooltip_text(icon_name)

            cell = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL, spacing=2,
                margin_top=4, margin_bottom=4,
                margin_start=4, margin_end=4,
            )

            # Bundled Bootstrap icons use texture rendering; system icons use name
            img = None
            if icon_name in _bundled_set and load_icon_texture is not None:
                try:
                    texture = load_icon_texture(icon_name, 22)
                    if texture:
                        img = Gtk.Image.new_from_paintable(texture)
                        img.set_pixel_size(22)
                except Exception:
                    pass
            if img is None:
                img = Gtk.Image(icon_name=icon_name, pixel_size=22)
            cell.append(img)

            short = icon_name.replace("-symbolic", "").replace("-", " ")
            words = short.split()
            label_text = " ".join(words[:2]) if len(words) > 1 else (words[0] if words else "")
            if len(label_text) > 10:
                label_text = label_text[:9] + "…"
            name_lbl = Gtk.Label(label=label_text, xalign=0.5)
            name_lbl.add_css_class("caption")
            cell.append(name_lbl)

            ic_btn.set_child(cell)
            ic_btn.connect("clicked", self._on_icon_picked, icon_name, popover)
            flow.append(ic_btn)

        flow.set_filter_func(self._picker_filter_func)
        search.connect('search-changed', lambda s: self._on_picker_search(s, flow))

        scroll.set_child(flow)
        outer.append(scroll)
        popover.set_child(outer)
        return popover

    def _on_picker_search(self, search_entry, flow):
        self._picker_search = search_entry.get_text().lower()
        flow.invalidate_filter()

    def _picker_filter_func(self, child) -> bool:
        if not self._picker_search:
            return True
        btn = child.get_child()
        return self._picker_search in (btn.get_tooltip_text() or "").lower()

    def _on_icon_picked(self, btn, icon_name, popover):
        self._icon_entry.set_text(icon_name)
        self._set_image_icon(self._icon_preview, icon_name)
        popover.popdown()

    # ── Save ─────────────────────────────────────────────────────────────

    def _build_button_from_fields(self) -> CommandButton | None:
        name = self._name_row.get_text().strip()
        command = self._command_row.get_text().strip()
        if not name or not command:
            return None

        machine_ids = []
        if self._local_switch.get_active():
            machine_ids.append("")
        for mid, row in self._machine_switches:
            if row.get_active():
                machine_ids.append(mid)
        if machine_ids == [""]:
            machine_ids = []

        icon_name = self._icon_entry.get_text().strip() or _FALLBACK_ICON
        color = self._bg_color_entry.get_text().strip()
        text_color = self._text_color_entry.get_text().strip()
        hide_label = self._hide_label_row.get_active()
        hide_icon = self._hide_icon_row.get_active()
        category = self._category_row.get_text().strip()
        tooltip = self._tooltip_row.get_text().strip()

        if self._is_edit and self._button:
            self._button.name = name
            self._button.command = command
            self._button.machine_ids = machine_ids
            self._button.icon_name = icon_name
            self._button.color = color
            self._button.text_color = text_color
            self._button.hide_label = hide_label
            self._button.hide_icon = hide_icon
            self._button.category = category
            self._button.tooltip = tooltip
            self._button.confirm_before_run = self._confirm_row.get_active()
            self._button.execution_mode = self._exec_mode_values[self._exec_mode_row.get_selected()]
            self._button.show_output = (self._button.execution_mode == "output")
            self._button.run_as_user = self._run_as_user_row.get_text().strip()
            return self._button
        else:
            exec_mode = self._exec_mode_values[self._exec_mode_row.get_selected()]
            return CommandButton(
                name=name,
                command=command,
                machine_ids=machine_ids,
                icon_name=icon_name,
                color=color,
                text_color=text_color,
                hide_label=hide_label,
                hide_icon=hide_icon,
                category=category,
                tooltip=tooltip,
                confirm_before_run=self._confirm_row.get_active(),
                execution_mode=exec_mode,
                show_output=(exec_mode == "output"),
                run_as_user=self._run_as_user_row.get_text().strip(),
            )

    def _on_save(self, btn):
        button = self._build_button_from_fields()
        if button is None:
            return
        if self._is_edit:
            self._config.update_button(button)
        else:
            self._config.add_button(button)
        if self._on_saved:
            self._on_saved()
        self.dialog.close()
