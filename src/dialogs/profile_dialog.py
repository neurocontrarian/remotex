import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

from i18n import _
from models.execution_profile import ExecutionProfile


def show_profile_dialog(parent, config, profile=None, on_saved=None):
    dlg = _ProfileDialog(parent, config, profile, on_saved)
    dlg.dialog.set_transient_for(parent)
    dlg.dialog.present()


class _ProfileDialog:
    def __init__(self, parent, config, profile, on_saved):
        self._config = config
        self._profile = profile
        self._is_edit = profile is not None
        self._on_saved = on_saved
        self._build_ui()
        if self._is_edit:
            self._populate_fields()

    def _build_ui(self):
        self.dialog = Adw.Window(
            title=_("Edit Profile") if self._is_edit else _("New Profile"),
            modal=True,
            default_width=480,
            default_height=420,
        )
        toolbar_view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        self._save_btn = Gtk.Button(label=_("Save"))
        self._save_btn.add_css_class("suggested-action")
        self._save_btn.connect("clicked", self._on_save)
        header.pack_end(self._save_btn)
        toolbar_view.add_top_bar(header)

        scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER, vexpand=True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin_top=12,
                      margin_bottom=12, margin_start=12, margin_end=12, spacing=12)

        group = Adw.PreferencesGroup(title=_("Execution Profile"))
        box.append(group)

        self._name_row = Adw.EntryRow(title=_("Profile name"))
        self._name_row.set_tooltip_text(
            _("A short descriptive name, e.g. 'As www-data in /var/www'")
        )
        group.add(self._name_row)

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

        self._working_dir_row = Adw.EntryRow(title=_("Working directory"))
        self._working_dir_row.set_tooltip_text(
            _("cd into this directory before running the command.\n"
              "Leave empty to use the default working directory.")
        )
        group.add(self._working_dir_row)

        self._description_row = Adw.EntryRow(title=_("Description (optional)"))
        group.add(self._description_row)

        # --- Sudo password group ---
        self._sudo_group = Adw.PreferencesGroup(title=_("Sudo Password"))
        self._sudo_group.set_description(
            _("Stored locally, encoded with a machine-specific key.\n"
              "Required to run commands without a password prompt.")
        )
        box.append(self._sudo_group)

        self._pwd_row = Adw.PasswordEntryRow(title=_("Sudo password"))
        self._pwd_row.set_show_apply_button(False)
        self._pwd_row.set_tooltip_text(
            _("Your sudo password (the one you type after 'sudo').\n"
              "Leave empty to keep the existing password.")
        )
        self._sudo_group.add(self._pwd_row)

        self._clear_btn_row = Adw.ActionRow(
            title=_("Password stored"),
            subtitle=_("Leave the field above empty to keep it, or type a new one to replace it."),
        )
        clear_btn = Gtk.Button(label=_("Clear"), valign=Gtk.Align.CENTER)
        clear_btn.add_css_class("destructive-action")
        clear_btn.connect("clicked", self._on_clear_password)
        self._clear_btn_row.add_suffix(clear_btn)
        self._clear_btn_row.set_visible(False)
        self._sudo_group.add(self._clear_btn_row)

        self._on_priv_changed(self._priv_row, None)

        scroll.set_child(box)
        toolbar_view.set_content(scroll)
        self.dialog.set_content(toolbar_view)

    def _populate_fields(self):
        p = self._profile
        self._name_row.set_text(p.name)
        if p.run_as_user == "root":
            self._priv_row.set_selected(1)
        elif p.run_as_user:
            self._priv_row.set_selected(2)
            self._run_as_user_row.set_text(p.run_as_user)
        self._on_priv_changed(self._priv_row, None)
        if p.working_dir:
            self._working_dir_row.set_text(p.working_dir)
        if p.description:
            self._description_row.set_text(p.description)
        if p.has_sudo_password:
            self._clear_btn_row.set_visible(True)

    def _on_priv_changed(self, row, _param):
        val = self._priv_values[row.get_selected()]
        self._run_as_user_row.set_visible(val == "__other__")
        self._sudo_group.set_visible(val in ("root", "__other__"))

    def _on_clear_password(self, btn):
        if self._profile:
            self._profile.set_sudo_password("")
            self._config.update_profile(self._profile)
        self._clear_btn_row.set_visible(False)
        self._pwd_row.set_text("")

    def _build_profile_from_fields(self) -> ExecutionProfile | None:
        name = self._name_row.get_text().strip()
        if not name:
            self._name_row.add_css_class("error")
            return None
        self._name_row.remove_css_class("error")

        run_as = self._resolve_run_as_user()
        if self._is_edit and self._profile:
            self._profile.name = name
            self._profile.run_as_user = run_as
            self._profile.working_dir = self._working_dir_row.get_text().strip()
            self._profile.description = self._description_row.get_text().strip()
            return self._profile
        return ExecutionProfile(
            name=name,
            run_as_user=run_as,
            working_dir=self._working_dir_row.get_text().strip(),
            description=self._description_row.get_text().strip(),
        )

    def _resolve_run_as_user(self) -> str:
        val = self._priv_values[self._priv_row.get_selected()]
        if val == "root":
            return "root"
        if val == "__other__":
            return self._run_as_user_row.get_text().strip()
        return ""

    def _on_save(self, btn):
        profile = self._build_profile_from_fields()
        if profile is None:
            return

        if not profile.run_as_user:
            profile.set_sudo_password("")

        password = self._pwd_row.get_text()
        if password:
            profile.set_sudo_password(password)

        if self._is_edit:
            self._config.update_profile(profile)
        else:
            self._config.add_profile(profile)
        if self._on_saved:
            self._on_saved()
        self.dialog.close()
