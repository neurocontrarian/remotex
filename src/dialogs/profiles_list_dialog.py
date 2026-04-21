import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

from i18n import _
from dialogs.profile_dialog import show_profile_dialog


def show_profiles_list(parent, config):
    dlg = _ProfilesListDialog(parent, config)
    dlg.dialog.set_transient_for(parent)
    dlg.dialog.present()


class _ProfilesListDialog:
    def __init__(self, parent, config):
        self._config = config
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        self.dialog = Adw.Window(
            title=_("Execution Profiles"),
            modal=False,
            default_width=500,
            default_height=500,
        )
        toolbar_view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.set_tooltip_text(_("Add profile"))
        add_btn.connect("clicked", self._on_add)
        header.pack_end(add_btn)
        toolbar_view.add_top_bar(header)

        self._stack = Gtk.Stack()

        empty = Adw.StatusPage(
            icon_name="system-run-symbolic",
            title=_("No Profiles"),
            description=_("Click + to create an execution profile."),
        )
        self._stack.add_named(empty, "empty")

        scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER, vexpand=True)
        self._list_box = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        self._list_box.add_css_class("boxed-list")
        self._list_box.set_margin_top(12)
        self._list_box.set_margin_bottom(12)
        self._list_box.set_margin_start(12)
        self._list_box.set_margin_end(12)
        scroll.set_child(self._list_box)
        self._stack.add_named(scroll, "list")

        toolbar_view.set_content(self._stack)
        self.dialog.set_content(toolbar_view)

    def _refresh(self):
        while self._list_box.get_first_child():
            self._list_box.remove(self._list_box.get_first_child())

        profiles = sorted(self._config.load_profiles(), key=lambda p: p.name)
        if not profiles:
            self._stack.set_visible_child_name("empty")
            return

        self._stack.set_visible_child_name("list")
        for profile in profiles:
            self._list_box.append(self._make_row(profile))

    def _make_row(self, profile) -> Adw.ActionRow:
        row = Adw.ActionRow(title=GLib.markup_escape_text(profile.name))
        parts = []
        if profile.run_as_user:
            parts.append(profile.run_as_user)
        if profile.working_dir:
            parts.append(profile.working_dir)
        if profile.description and not parts:
            parts.append(profile.description)
        if parts:
            row.set_subtitle(GLib.markup_escape_text("  •  ".join(parts)))

        edit_btn = Gtk.Button(label=_("Edit"), valign=Gtk.Align.CENTER)
        edit_btn.add_css_class("flat")
        edit_btn.connect("clicked", lambda _, p=profile: self._on_edit(p))
        row.add_suffix(edit_btn)

        del_btn = Gtk.Button(icon_name="user-trash-symbolic", valign=Gtk.Align.CENTER)
        del_btn.add_css_class("flat")
        del_btn.add_css_class("destructive-action")
        del_btn.set_tooltip_text(_("Delete"))
        del_btn.connect("clicked", lambda _, p=profile: self._on_delete(p))
        row.add_suffix(del_btn)
        return row

    def _on_add(self, btn):
        show_profile_dialog(self.dialog, self._config, on_saved=self._refresh)

    def _on_edit(self, profile):
        show_profile_dialog(self.dialog, self._config, profile=profile, on_saved=self._refresh)

    def _on_delete(self, profile):
        confirm = Adw.AlertDialog(
            heading=_("Delete Profile?"),
            body=_("'{name}' will be removed. Buttons using it will fall back "
                   "to their own settings.").format(name=profile.name),
        )
        confirm.add_response("cancel", _("Cancel"))
        confirm.add_response("delete", _("Delete"))
        confirm.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)

        def on_response(dlg, response):
            if response == "delete":
                self._config.delete_profile(profile.id)
                self._refresh()

        confirm.connect("response", on_response)
        confirm.present(self.dialog)
