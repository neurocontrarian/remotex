import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from contextlib import contextmanager
from gi.repository import Gtk, Adw, Gdk
from typing import Callable

@contextmanager
def _block_handler(widget, handler):
    widget.handler_block_by_func(handler)
    try:
        yield
    finally:
        widget.handler_unblock_by_func(handler)

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

        box.append(self._build_details_group())
        box.append(self._build_machines_group())
        box.append(self._build_appearance_group())
        box.append(self._build_organisation_group())
        box.append(self._build_behaviour_group())

        scroll.set_child(box)
        toolbar_view.set_content(scroll)
        self.dialog.set_content(toolbar_view)

    def _build_details_group(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup(title=_("Button"))
        self._name_row = Adw.EntryRow(title=_("Label"))
        group.add(self._name_row)
        self._command_row = Adw.EntryRow(title=_("Command"))
        group.add(self._command_row)
        return group

    def _build_machines_group(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup(title=_("Target machines"))
        group.set_description(
            _("Select where this command can run.\n"
              "If multiple targets are selected, you will be asked which one to use at run time.")
        )
        self._local_switch = Adw.SwitchRow(title=_("Local (this machine)"))
        self._local_switch.set_subtitle(_("Run directly on this computer"))
        self._local_switch.set_active(True)
        group.add(self._local_switch)

        self._machine_switches: list[tuple[str, Adw.SwitchRow]] = []
        machines = self._config.load_machines()

        # Build group map first so we know which machines belong to a group
        group_map: dict[str, set] = {}
        grouped_ids: set[str] = set()
        for m in machines:
            if m.group:
                group_map.setdefault(m.group, set()).add(m.id)
                grouped_ids.add(m.id)

        # Ungrouped machines appear as individual rows; grouped ones are hidden (controlled via group row)
        for m in machines:
            row = Adw.SwitchRow(title=m.name)
            row.set_subtitle(f"{m.user}@{m.host}:{m.port}")
            if m.id not in grouped_ids:
                group.add(row)
            self._machine_switches.append((m.id, row))

        # Group toggle rows — one per distinct group name
        self._group_switches: list[tuple[set, Adw.SwitchRow]] = []
        for gname, mids in sorted(group_map.items()):
            row = Adw.SwitchRow(title=_("Group: {name}").format(name=gname))
            row.set_subtitle(_("{n} machines").format(n=len(mids)))
            group.add(row)
            self._group_switches.append((mids, row))
            row.connect("notify::active", self._on_group_switch_changed, mids)

        if machines:
            self._all_switch = Adw.SwitchRow(title=_("All machines"))
            self._all_switch.set_subtitle(_("Select / deselect all targets at once"))
            group.add(self._all_switch)
            self._all_switch.connect("notify::active", self._on_all_switch_changed)
            self._local_switch.connect("notify::active", self._on_individual_switch_changed)
            for _mid, row in self._machine_switches:
                row.connect("notify::active", self._on_individual_switch_changed)
        else:
            self._all_switch = None
            hint = Adw.ActionRow(title=_("No remote machines configured"))
            hint.set_subtitle(_("Add machines via menu → Manage Machines"))
            group.add(hint)
        return group

    def _build_appearance_group(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup(title=_("Appearance"))

        icon_row = Adw.ActionRow(title=_("Icon"))
        icon_row.set_subtitle(_("Click Browse to pick visually, or type a name"))
        self._icon_preview = Gtk.Image(
            icon_name=_FALLBACK_ICON, pixel_size=24, valign=Gtk.Align.CENTER
        )
        icon_row.add_prefix(self._icon_preview)
        self._icon_entry = Gtk.Entry(
            valign=Gtk.Align.CENTER, hexpand=True,
            placeholder_text=_FALLBACK_ICON, width_chars=24,
        )
        self._icon_entry.connect("changed", self._on_icon_changed)
        icon_row.add_suffix(self._icon_entry)
        browse_btn = Gtk.Button(label=_("Browse"), valign=Gtk.Align.CENTER)
        browse_btn.add_css_class("flat")
        browse_btn.connect("clicked", self._on_browse_icon)
        icon_row.add_suffix(browse_btn)
        group.add(icon_row)

        bg_row, self._bg_color_entry = self._build_color_row(_("Background color"))
        group.add(bg_row)
        text_row, self._text_color_entry = self._build_color_row(_("Text color"))
        group.add(text_row)

        self._hide_label_row = Adw.SwitchRow(title=_("Hide label"))
        self._hide_label_row.set_subtitle(_("Show icon only — no text below"))
        group.add(self._hide_label_row)
        self._hide_icon_row = Adw.SwitchRow(title=_("Hide icon"))
        self._hide_icon_row.set_subtitle(_("Show label only — no icon above"))
        group.add(self._hide_icon_row)
        return group

    def _build_organisation_group(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup(title=_("Organisation"))
        self._category_row = Adw.EntryRow(title=_("Category"))
        group.add(self._category_row)
        return group

    def _build_behaviour_group(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup(title=_("Behaviour"))

        self._tooltip_row = Adw.EntryRow(title=_("Tooltip"))
        self._tooltip_row.set_tooltip_text(
            _("Text shown when hovering over the button.\n"
              "Leave empty to show the command automatically.")
        )
        group.add(self._tooltip_row)

        self._confirm_row = Adw.SwitchRow(title=_("Confirm before running"))
        self._confirm_row.set_subtitle(_("Show a confirmation popup before executing"))
        self._confirm_row.set_tooltip_text(
            _("When enabled, a popup asks 'Run this command?' before anything happens.\n"
              "Recommended for destructive operations like reboots or file deletions.")
        )
        group.add(self._confirm_row)

        from feature_gate import is_pro_active as _is_pro_for_mcp
        self._mcp_executable_row = Adw.SwitchRow(title=_("Allow AI to run this button"))
        self._mcp_executable_row.set_subtitle(
            _("Permit MCP-connected AI clients to trigger this button")
        )
        self._mcp_executable_row.set_tooltip_text(
            _("When enabled, AI clients connected via MCP can execute this button's command.\n"
              "Only enable for safe, idempotent commands. Combine with 'Confirm before running'\n"
              "for sensitive operations — the AI will be required to ask the user first.")
        )
        if not _is_pro_for_mcp():
            self._mcp_executable_row.set_sensitive(False)
            lock = Gtk.Image.new_from_icon_name("changes-prevent-symbolic")
            lock.set_tooltip_text(_("Upgrade to Pro to use the MCP server"))
            lock.add_css_class("dim-label")
            self._mcp_executable_row.add_suffix(lock)
        group.add(self._mcp_executable_row)

        exec_mode_model = Gtk.StringList()
        self._exec_mode_values = ["silent", "output", "terminal"]
        for label in [_("Silent (toast only)"), _("Show output"), _("Open in terminal")]:
            exec_mode_model.append(label)
        self._exec_mode_row = Adw.ComboRow(title=_("Execution mode"))
        self._exec_mode_row.set_subtitle(_("How to display results after the command runs"))
        self._exec_mode_row.set_tooltip_text(
            _("Silent: only a brief toast notification\n"
              "Show output: open a window with stdout/stderr\n"
              "Open in terminal: run in a new terminal window (supports sudo, interactive commands)")
        )
        self._exec_mode_row.set_model(exec_mode_model)
        group.add(self._exec_mode_row)

        # --- Privileges ---
        priv_model = Gtk.StringList()
        self._priv_values = ["", "root", "__other__"]
        for label in [_("Current user (no sudo)"), _("Root (sudo)"), _("Other user…")]:
            priv_model.append(label)
        self._priv_row = Adw.ComboRow(title=_("Run as"))
        self._priv_row.set_model(priv_model)
        self._priv_row.connect("notify::selected", self._on_priv_changed)
        group.add(self._priv_row)

        self._run_as_user_row = Adw.EntryRow(title=_("Username"))
        self._run_as_user_row.set_tooltip_text(_("System user to run the command as (e.g. www-data, postgres)"))
        self._run_as_user_row.set_visible(False)
        group.add(self._run_as_user_row)

        self._sudo_pwd_row = Adw.PasswordEntryRow(title=_("Sudo password"))
        self._sudo_pwd_row.set_show_apply_button(False)
        self._sudo_pwd_row.set_tooltip_text(
            _("Your sudo password — stored locally, encoded with a machine-specific key.\n"
              "Leave empty to keep the existing password, or to be prompted each time.")
        )
        self._sudo_pwd_row.set_visible(False)
        self._sudo_pwd_stored_row = Adw.ActionRow(
            title=_("Password stored"),
            subtitle=_("Leave the field empty to keep it, or type a new one to replace it."),
        )
        sudo_clear_btn = Gtk.Button(label=_("Clear"), valign=Gtk.Align.CENTER)
        sudo_clear_btn.add_css_class("destructive-action")
        sudo_clear_btn.connect("clicked", self._on_clear_sudo_pwd)
        self._sudo_pwd_stored_row.add_suffix(sudo_clear_btn)
        self._sudo_pwd_stored_row.set_visible(False)
        group.add(self._sudo_pwd_row)
        group.add(self._sudo_pwd_stored_row)

        from feature_gate import is_pro_active as _is_pro
        _pro = _is_pro()
        profiles = self._config.load_profiles() if _pro else []
        profile_model = Gtk.StringList()
        self._profile_id_values = [""]
        profile_model.append(_("None (use button settings)"))
        for p in profiles:
            profile_model.append(p.name)
            self._profile_id_values.append(p.id)
        self._profile_row = Adw.ComboRow(title=_("Execution profile"))
        self._profile_row.set_subtitle(
            _("Apply a saved profile (user + directory) to this button")
        )
        self._profile_row.set_model(profile_model)
        if not _pro:
            self._profile_row.set_sensitive(False)
            lock = Gtk.Image.new_from_icon_name("changes-prevent-symbolic")
            lock.set_tooltip_text(_("Upgrade to Pro to use execution profiles"))
            lock.add_css_class("dim-label")
            self._profile_row.add_suffix(lock)
        else:
            self._profile_row.connect("notify::selected", self._on_profile_changed)
        group.add(self._profile_row)
        return group

    def _on_priv_changed(self, row, _param):
        val = self._priv_values[row.get_selected()]
        self._run_as_user_row.set_visible(val == "__other__")
        has_sudo = val in ("root", "__other__")
        self._sudo_pwd_row.set_visible(has_sudo)
        # keep stored indicator visible only if there was already a password
        if not has_sudo:
            self._sudo_pwd_stored_row.set_visible(False)

    def _on_clear_sudo_pwd(self, btn):
        if self._button:
            self._button.set_sudo_password("")
        self._sudo_pwd_stored_row.set_visible(False)
        self._sudo_pwd_row.set_text("")

    def _on_profile_changed(self, row, _param):
        has_profile = self._profile_id_values[row.get_selected()] != ""
        for w in (self._priv_row, self._run_as_user_row,
                  self._sudo_pwd_row, self._sudo_pwd_stored_row):
            w.set_sensitive(not has_profile)
        if has_profile:
            self._sudo_pwd_row.set_visible(False)
            self._sudo_pwd_stored_row.set_visible(False)

    def _populate_fields(self):
        if not self._button:
            try:
                from gi.repository import Gio
                _s = Gio.Settings.new('com.github.remotex.RemoteX')
                user_val = _s.get_user_value('confirm-before-run')
                default = user_val.get_boolean() if user_val is not None else True
                self._confirm_row.set_active(default)
            except Exception:
                self._confirm_row.set_active(True)
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
        self._mcp_executable_row.set_active(self._button.mcp_executable)
        # Resolve execution mode: explicit mode takes precedence; fall back from show_output
        mode = self._button.execution_mode
        if not mode:
            mode = "output" if self._button.show_output else "silent"
        idx = self._exec_mode_values.index(mode) if mode in self._exec_mode_values else 0
        self._exec_mode_row.set_selected(idx)
        # Populate privileges dropdown
        run_as = self._button.run_as_user
        if run_as == "root":
            self._priv_row.set_selected(1)
        elif run_as:
            self._priv_row.set_selected(2)
            self._run_as_user_row.set_text(run_as)
        # else stays at 0 (current user)
        self._on_priv_changed(self._priv_row, None)
        if self._button.sudo_password_encoded:
            self._sudo_pwd_stored_row.set_visible(True)
        if hasattr(self, '_profile_id_values') and self._button.profile_id:
            try:
                idx = self._profile_id_values.index(self._button.profile_id)
                self._profile_row.set_selected(idx)
                self._on_profile_changed(self._profile_row, None)
            except ValueError:
                pass

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
            rgba = Gdk.RGBA()
            if color and color.startswith("#") and rgba.parse(color):
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
        with _block_handler(self._local_switch, self._on_individual_switch_changed):
            self._local_switch.set_active(active)
        for _, row in self._machine_switches:
            with _block_handler(row, self._on_individual_switch_changed):
                row.set_active(active)

    def _on_group_switch_changed(self, switch, _param, machine_ids: set):
        """When a group toggle is flipped, update all machines in that group."""
        active = switch.get_active()
        for mid, row in self._machine_switches:
            if mid in machine_ids:
                with _block_handler(row, self._on_individual_switch_changed):
                    row.set_active(active)
        # Sync the All switch
        self._on_individual_switch_changed(None, None)

    def _on_individual_switch_changed(self, switch, _param):
        """Update 'All machines' state when any individual switch changes."""
        if self._all_switch is None:
            return
        all_rows = [self._local_switch] + [r for _, r in self._machine_switches]
        all_on = all(r.get_active() for r in all_rows)
        with _block_handler(self._all_switch, self._on_all_switch_changed):
            self._all_switch.set_active(all_on)
        # Keep group switches in sync
        for mids, grow in self._group_switches:
            group_on = all(
                row.get_active() for mid, row in self._machine_switches if mid in mids
            )
            with _block_handler(grow, self._on_group_switch_changed):
                grow.set_active(group_on)

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
            self._button.mcp_executable = self._mcp_executable_row.get_active()
            self._button.execution_mode = self._exec_mode_values[self._exec_mode_row.get_selected()]
            self._button.show_output = (self._button.execution_mode == "output")
            self._button.run_as_user = self._resolve_run_as_user()
            self._button.profile_id = self._profile_id_values[
                self._profile_row.get_selected()
            ] if hasattr(self, '_profile_id_values') else ""
            pwd = self._sudo_pwd_row.get_text()
            if pwd:
                self._button.set_sudo_password(pwd)
            elif not self._button.sudo_password_encoded:
                self._button.set_sudo_password("")
            return self._button
        else:
            exec_mode = self._exec_mode_values[self._exec_mode_row.get_selected()]
            btn = CommandButton(
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
                mcp_executable=self._mcp_executable_row.get_active(),
                execution_mode=exec_mode,
                show_output=(exec_mode == "output"),
                run_as_user=self._resolve_run_as_user(),
                profile_id=self._profile_id_values[
                    self._profile_row.get_selected()
                ] if hasattr(self, '_profile_id_values') else "",
            )
            pwd = self._sudo_pwd_row.get_text()
            if pwd:
                btn.set_sudo_password(pwd)
            return btn

    def _resolve_run_as_user(self) -> str:
        val = self._priv_values[self._priv_row.get_selected()]
        if val == "root":
            return "root"
        if val == "__other__":
            return self._run_as_user_row.get_text().strip()
        return ""

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
