import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib
from pathlib import Path
from typing import Callable

from models.machine import Machine
from models.config import ConfigManager
from services.ssh_key_service import SSHKeyService
from utils.threading import run_in_thread
from utils.icon_loader import load_icon_texture
from i18n import _

_MACHINE_ICONS = [
    ("pc-display", "Desktop"),
    ("pc-display-horizontal", "Desktop (wide)"),
    ("laptop", "Laptop"),
    ("server", "Server"),
    ("router", "Router"),
    ("wifi", "Wi-Fi"),
    ("ethernet", "Network"),
    ("terminal", "Terminal"),
]


def show_machine_dialog(parent, config: ConfigManager, machine: Machine | None = None,
                        on_saved: Callable | None = None):
    """Open the Add/Edit machine dialog. machine=None means 'add new'."""
    is_edit = machine is not None
    from utils.desktop import make_floating_window
    dlg = _MachineDialog(parent, config, machine, on_saved, is_edit)
    make_floating_window(dlg.dialog, parent, 520, 640)
    dlg.dialog.present()


class _MachineDialog:
    def __init__(self, parent, config: ConfigManager, machine: Machine | None,
                 on_saved: Callable | None, is_edit: bool):
        self._parent = parent
        self._config = config
        self._machine = machine
        self._on_saved = on_saved
        self._is_edit = is_edit
        self._ssh_key_svc = SSHKeyService()

        self.dialog = Adw.Window(title=_("Edit Machine") if is_edit else _("Add Machine"))
        self._build_ui()
        self._populate_fields()
        self._refresh_key_status()

    def _build_ui(self):
        toolbar_view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)

        # Save button
        self._save_btn = Gtk.Button(label=_("Save"))
        self._save_btn.add_css_class("suggested-action")
        self._save_btn.connect("clicked", self._on_save)
        header.pack_end(self._save_btn)

        scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True,
                                    hscrollbar_policy=Gtk.PolicyType.NEVER)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24,
                      margin_top=16, margin_bottom=16,
                      margin_start=16, margin_end=16)

        # ── Connection details ──────────────────────────────────────────
        conn_group = Adw.PreferencesGroup(title=_("Connection"))
        box.append(conn_group)

        self._name_row = Adw.EntryRow(title=_("Name"))
        conn_group.add(self._name_row)

        self._host_row = Adw.EntryRow(title=_("Host / IP"))
        conn_group.add(self._host_row)

        self._user_row = Adw.EntryRow(title=_("SSH User"))
        conn_group.add(self._user_row)

        self._port_row = Adw.EntryRow(title=_("Port"))
        self._port_row.set_text("22")
        conn_group.add(self._port_row)

        self._key_row = Adw.EntryRow(title=_("SSH Key Path"))
        self._key_row.set_text(str(Path.home() / ".ssh" / "id_ed25519"))
        conn_group.add(self._key_row)

        # ── Appearance ──────────────────────────────────────────────────
        appearance_group = Adw.PreferencesGroup(title=_("Appearance"))
        box.append(appearance_group)

        icon_row = Adw.ActionRow(title=_("Icon"))
        icon_row.set_subtitle(_("Choose an icon to represent this machine"))
        self._icon_name = "pc-display"

        self._icon_preview = Gtk.Picture(valign=Gtk.Align.CENTER)
        self._icon_preview.set_size_request(32, 32)
        icon_row.add_prefix(self._icon_preview)

        icon_flow = Gtk.FlowBox(
            max_children_per_line=8,
            min_children_per_line=4,
            selection_mode=Gtk.SelectionMode.NONE,
            hexpand=True,
            margin_top=6,
            margin_bottom=6,
        )
        self._icon_btns: list[tuple[str, Gtk.ToggleButton]] = []
        for icon_id, label in _MACHINE_ICONS:
            btn = Gtk.ToggleButton(tooltip_text=label)
            btn.add_css_class("flat")
            texture = load_icon_texture(icon_id, 24)
            if texture:
                pic = Gtk.Picture()
                pic.set_paintable(texture)
                pic.set_size_request(24, 24)
                btn.set_child(pic)
            else:
                btn.set_label(label[:3])
            btn.connect("toggled", self._on_icon_btn_toggled, icon_id)
            icon_flow.append(btn)
            self._icon_btns.append((icon_id, btn))

        icon_row.set_activatable_widget(None)
        appearance_group.add(icon_row)

        icon_flow_row = Adw.ActionRow()
        icon_flow_row.set_child(icon_flow)
        appearance_group.add(icon_flow_row)

        self._update_icon_preview("pc-display")
        if self._icon_btns:
            self._icon_btns[0][1].set_active(True)

        # ── Test connection ─────────────────────────────────────────────
        test_group = Adw.PreferencesGroup()
        box.append(test_group)

        test_row = Adw.ActionRow(title=_("Test Connection"),
                                 subtitle=_("Verify that SSH key authentication works"))
        self._test_btn = Gtk.Button(label=_("Test"), valign=Gtk.Align.CENTER)
        self._test_btn.connect("clicked", self._on_test_connection)
        test_row.add_suffix(self._test_btn)
        test_group.add(test_row)

        self._test_status = Gtk.Label(label="", xalign=0, wrap=True)
        self._test_status.add_css_class("caption")
        test_group.add(self._test_status)

        # ── SSH Key Setup ───────────────────────────────────────────────
        key_group = Adw.PreferencesGroup(
            title=_("SSH Key Setup"),
            description=_("One-time setup — copies your key to the remote machine "
                          "so you never need a password again."),
        )
        box.append(key_group)

        self._key_status_row = Adw.ActionRow(title=_("SSH Key Status"))
        key_group.add(self._key_status_row)

        self._gen_row = Adw.ActionRow(
            title=_("No key found"),
            subtitle=_("Generate a new ed25519 key pair"),
        )
        self._gen_btn = Gtk.Button(label=_("Generate"), valign=Gtk.Align.CENTER)
        self._gen_btn.connect("clicked", self._on_generate_key)
        self._gen_row.add_suffix(self._gen_btn)
        self._gen_row.set_visible(False)
        key_group.add(self._gen_row)

        # Password + copy row
        self._pwd_row = Adw.PasswordEntryRow(title=_("Remote Password"))
        self._pwd_row.set_show_apply_button(False)
        key_group.add(self._pwd_row)

        pwd_note = Gtk.Label(
            label=_("Password is used once to copy your SSH key — never stored"),
            xalign=0,
            wrap=True,
            margin_start=12,
            margin_end=12,
            margin_top=2,
            margin_bottom=4,
        )
        pwd_note.add_css_class("caption")
        pwd_note.add_css_class("dim-label")
        key_group.add(pwd_note)

        copy_row = Adw.ActionRow(
            title=_("Copy Key to Machine"),
            subtitle=_("Installs your public key on the remote machine (one-time)"),
        )
        self._copy_btn = Gtk.Button(label=_("Copy Key"), valign=Gtk.Align.CENTER)
        self._copy_btn.add_css_class("suggested-action")
        self._copy_btn.connect("clicked", self._on_copy_key)
        copy_row.add_suffix(self._copy_btn)
        key_group.add(copy_row)

        self._copy_status = Gtk.Label(label="", xalign=0, wrap=True)
        self._copy_status.add_css_class("caption")
        key_group.add(self._copy_status)

        scroll.set_child(box)
        toolbar_view.set_content(scroll)
        self.dialog.set_content(toolbar_view)

    def _update_icon_preview(self, icon_name: str):
        texture = load_icon_texture(icon_name, 32)
        if texture:
            self._icon_preview.set_paintable(texture)
        self._icon_name = icon_name

    def _on_icon_btn_toggled(self, btn: Gtk.ToggleButton, icon_id: str):
        if not btn.get_active():
            return
        # Deactivate other buttons
        for other_id, other_btn in self._icon_btns:
            if other_id != icon_id and other_btn.get_active():
                other_btn.handler_block_by_func(self._on_icon_btn_toggled)
                other_btn.set_active(False)
                other_btn.handler_unblock_by_func(self._on_icon_btn_toggled)
        self._update_icon_preview(icon_id)

    def _populate_fields(self):
        if self._machine:
            self._name_row.set_text(self._machine.name)
            self._host_row.set_text(self._machine.host)
            self._user_row.set_text(self._machine.user)
            self._port_row.set_text(str(self._machine.port))
            if self._machine.identity_file:
                self._key_row.set_text(self._machine.identity_file)
            # Set icon
            icon_to_set = self._machine.icon_name or "pc-display"
            self._update_icon_preview(icon_to_set)
            for icon_id, btn in self._icon_btns:
                active = (icon_id == icon_to_set)
                btn.handler_block_by_func(self._on_icon_btn_toggled)
                btn.set_active(active)
                btn.handler_unblock_by_func(self._on_icon_btn_toggled)

    def _refresh_key_status(self):
        keys = self._ssh_key_svc.find_existing_keys()
        if keys:
            names = ", ".join(k.name for k in keys)
            self._key_status_row.set_title(_("SSH Key Found"))
            self._key_status_row.set_subtitle(f"~/.ssh/{names} — ready to copy")
            self._gen_row.set_visible(False)
            self._key_row.set_text(str(self._ssh_key_svc.preferred_key()))
        else:
            self._key_status_row.set_title(_("No SSH Key Found"))
            self._key_status_row.set_subtitle(_("Generate a key pair first"))
            self._gen_row.set_visible(True)

    def _build_machine_from_fields(self) -> Machine | None:
        name = self._name_row.get_text().strip()
        host = self._host_row.get_text().strip()
        user = self._user_row.get_text().strip()
        port_text = self._port_row.get_text().strip()
        key = self._key_row.get_text().strip()

        if not name or not host or not user:
            return None

        try:
            port = int(port_text) if port_text else 22
        except ValueError:
            port = 22

        if self._is_edit and self._machine:
            self._machine.name = name
            self._machine.host = host
            self._machine.user = user
            self._machine.port = port
            self._machine.identity_file = key
            self._machine.icon_name = self._icon_name
            return self._machine
        else:
            return Machine(name=name, host=host, user=user, port=port,
                           identity_file=key, icon_name=self._icon_name)

    def _on_save(self, btn):
        machine = self._build_machine_from_fields()
        if machine is None:
            return
        if self._is_edit:
            self._config.update_machine(machine)
        else:
            self._config.add_machine(machine)
        if self._on_saved:
            self._on_saved()
        self.dialog.close()

    def _on_test_connection(self, btn):
        machine = self._build_machine_from_fields()
        if machine is None:
            self._test_status.set_text(_("Fill in Name, Host and User first."))
            return

        self._test_btn.set_sensitive(False)
        self._test_status.set_text(_("Testing connection…"))

        from services.executor import CommandExecutor
        executor = CommandExecutor(self._config)
        executor.test_connection(machine, self._on_test_result)

    def _on_test_result(self, success: bool, message: str):
        self._test_btn.set_sensitive(True)
        icon = "✓" if success else "✗"
        self._test_status.set_text(f"{icon}  {message}")

    def _on_generate_key(self, btn):
        self._gen_btn.set_sensitive(False)
        ok, msg, _ = self._ssh_key_svc.generate_key()
        self._gen_btn.set_sensitive(True)
        self._copy_status.set_text(f"{'✓' if ok else '✗'}  {msg}")
        self._refresh_key_status()

    def _on_copy_key(self, btn):
        machine = self._build_machine_from_fields()
        if machine is None:
            self._copy_status.set_text("Fill in Host and User first.")
            return

        password = self._pwd_row.get_text()
        if not password:
            self._copy_status.set_text("Enter the remote user's password.")
            return

        key = self._ssh_key_svc.preferred_key()
        if key is None:
            self._copy_status.set_text("No SSH key found. Generate one first.")
            return

        self._copy_btn.set_sensitive(False)
        self._copy_status.set_text("Copying key…")

        run_in_thread(
            self._ssh_key_svc.copy_key_to_machine,
            self._on_copy_result,
            machine, password, key,
        )

    def _on_copy_result(self, result: tuple[bool, str]):
        success, message = result
        self._copy_btn.set_sensitive(True)
        self._pwd_row.set_text("")
        icon = "✓" if success else "✗"
        self._copy_status.set_text(f"{icon}  {message}")
        if success:
            self._refresh_key_status()
