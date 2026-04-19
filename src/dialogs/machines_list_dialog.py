import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from models.config import ConfigManager
from dialogs.machine_dialog import show_machine_dialog
from utils.icon_loader import load_icon_texture
from i18n import _


def show_machines_list(parent, config: ConfigManager):
    """Open the machine management dialog."""
    from utils.desktop import make_floating_window
    dlg = _MachinesListDialog(parent, config)
    make_floating_window(dlg.dialog, parent, 500, 500)
    dlg.dialog.present()


class _MachinesListDialog:
    def __init__(self, parent, config: ConfigManager):
        self._parent = parent
        self._config = config

        self.dialog = Adw.Window(title=_("Manage Machines"))
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        toolbar_view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)

        add_btn = Gtk.Button(icon_name="list-add-symbolic",
                             tooltip_text=_("Add Machine"))
        add_btn.add_css_class("flat")
        add_btn.connect("clicked", self._on_add)
        header.pack_end(add_btn)

        self._list_box = Gtk.ListBox()
        self._list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self._list_box.add_css_class("boxed-list")

        self._empty_label = Gtk.Label(
            label=_("No machines configured yet.\nClick + to add one."),
            justify=Gtk.Justification.CENTER,
            vexpand=True,
        )
        self._empty_label.add_css_class("dim-label")

        self._stack = Gtk.Stack()
        self._stack.add_named(self._empty_label, "empty")

        scrolled = Gtk.ScrolledWindow(hexpand=True, vexpand=True,
                                      hscrollbar_policy=Gtk.PolicyType.NEVER,
                                      margin_top=12, margin_bottom=12,
                                      margin_start=12, margin_end=12)
        scrolled.set_child(self._list_box)
        self._stack.add_named(scrolled, "list")

        toolbar_view.set_content(self._stack)
        self.dialog.set_content(toolbar_view)

    def _refresh(self):
        while child := self._list_box.get_first_child():
            self._list_box.remove(child)

        machines = self._config.load_machines()

        if not machines:
            self._stack.set_visible_child_name("empty")
            return

        self._stack.set_visible_child_name("list")
        # Sort: grouped machines first (by group name), then ungrouped
        machines_sorted = sorted(machines, key=lambda m: (not m.group, m.group, m.name))
        current_group = object()  # sentinel
        for machine in machines_sorted:
            if machine.group != current_group:
                current_group = machine.group
                if current_group:
                    lbl = Gtk.Label(label=current_group, xalign=0,
                                    margin_start=12, margin_top=8, margin_bottom=2)
                    lbl.add_css_class("caption")
                    lbl.add_css_class("dim-label")
                    hdr = Gtk.ListBoxRow()
                    hdr.set_selectable(False)
                    hdr.set_activatable(False)
                    hdr.set_child(lbl)
                    self._list_box.append(hdr)
            row = self._make_row(machine)
            self._list_box.append(row)

    def _make_row(self, machine):
        row = Adw.ActionRow(
            title=machine.name,
            subtitle=f"{machine.user}@{machine.host}:{machine.port}",
        )
        icon_name = machine.icon_name if machine.icon_name else 'pc-display'
        texture = load_icon_texture(icon_name, 32)
        if texture:
            pic = Gtk.Picture(valign=Gtk.Align.CENTER)
            pic.set_paintable(texture)
            pic.set_size_request(32, 32)
            row.add_prefix(pic)
        else:
            row.add_prefix(Gtk.Image(icon_name="computer-symbolic",
                                     pixel_size=32, valign=Gtk.Align.CENTER))

        edit_btn = Gtk.Button(tooltip_text=_("Edit"), valign=Gtk.Align.CENTER)
        edit_btn.add_css_class("flat")
        _edit_texture = load_icon_texture('pencil', 16)
        if _edit_texture:
            _pic = Gtk.Picture(
                halign=Gtk.Align.CENTER,
                valign=Gtk.Align.CENTER,
                hexpand=False,
                vexpand=False,
            )
            _pic.set_paintable(_edit_texture)
            _pic.set_size_request(16, 16)
            _pic.set_content_fit(Gtk.ContentFit.SCALE_DOWN)
            edit_btn.set_child(_pic)
        else:
            edit_btn.set_child(Gtk.Image.new_from_icon_name("document-edit-symbolic"))
        edit_btn.connect("clicked", self._on_edit, machine)

        delete_btn = Gtk.Button(icon_name="user-trash-symbolic",
                                tooltip_text=_("Delete"),
                                valign=Gtk.Align.CENTER)
        delete_btn.add_css_class("flat")
        delete_btn.add_css_class("destructive-action")
        delete_btn.connect("clicked", self._on_delete, machine)

        row.add_suffix(edit_btn)
        row.add_suffix(delete_btn)
        return row

    def _on_add(self, btn):
        show_machine_dialog(self.dialog, self._config, on_saved=self._refresh)

    def _open_url(self, url: str):
        """Open a URL in the default browser."""
        try:
            launcher = Gtk.UriLauncher(uri=url)
            launcher.launch(self.dialog, None, None)
        except Exception:
            import subprocess
            subprocess.Popen(
                ["/usr/bin/xdg-open", url],
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    def _on_edit(self, btn, machine):
        show_machine_dialog(self.dialog, self._config, machine=machine,
                            on_saved=self._refresh)

    def _on_delete(self, btn, machine):
        confirm = Adw.AlertDialog(
            heading=_('Delete "{name}"?').format(name=machine.name),
            body=_("This will remove the machine from RemoteX. "
                   "Buttons linked to it will no longer work."),
        )
        confirm.add_response("cancel", _("Cancel"))
        confirm.add_response("delete", _("Delete"))
        confirm.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        confirm.set_default_response("cancel")
        confirm.set_close_response("cancel")

        def on_response(dlg, response):
            if response == "delete":
                self._config.delete_machine(machine.id)
                self._refresh()

        confirm.connect("response", on_response)
        confirm.present(self.dialog)
