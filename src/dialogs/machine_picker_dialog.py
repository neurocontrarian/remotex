import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
from typing import Callable

from i18n import _


def show_machine_picker(
    parent,
    options: list[tuple[str, str, str]],
    on_chosen: Callable[[list[str]], None],
):
    """Show a dialog to pick one or more machines, then call on_chosen(machine_ids).

    options: list of (machine_id, title, subtitle).
             machine_id="" represents local execution.
    on_chosen: called with the list of selected machine_ids (at least one).
    """
    from utils.desktop import make_floating_window
    dlg = _MachinePickerDialog(parent, options, on_chosen)
    make_floating_window(dlg.dialog, parent, 380, 450)
    dlg.dialog.present()


class _MachinePickerDialog:
    def __init__(self, parent, options: list[tuple[str, str, str]],
                 on_chosen: Callable[[list[str]], None]):
        self._options = options
        self._on_chosen = on_chosen
        self._checks: list[tuple[str, Gtk.CheckButton]] = []

        self.dialog = Adw.Window(title=_("Choose machines"))
        self._build_ui()

    def _build_ui(self):
        toolbar_view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)

        self._run_btn = Gtk.Button(label=_("Run"))
        self._run_btn.add_css_class("suggested-action")
        self._run_btn.connect("clicked", self._on_run)
        header.pack_end(self._run_btn)

        self._select_all_btn = Gtk.Button(label=_("Select all"))
        self._select_all_btn.add_css_class("flat")
        self._select_all_btn.connect("clicked", self._on_toggle_all)
        header.pack_start(self._select_all_btn)

        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=24,
            margin_top=16, margin_bottom=16,
            margin_start=16, margin_end=16,
        )

        group = Adw.PreferencesGroup(title=_("Target machines"))
        group.set_description(
            _("Select the machines to run this command on.\n"
              "One output window will open per machine.")
        )
        box.append(group)

        for machine_id, title, subtitle in self._options:
            row = Adw.ActionRow(title=title)
            row.set_subtitle(subtitle)

            check = Gtk.CheckButton()
            check.set_active(False)
            check.connect("toggled", lambda _c: self._update_state())
            row.add_prefix(check)
            row.set_activatable_widget(check)
            group.add(row)
            self._checks.append((machine_id, check))

        self._update_state()
        toolbar_view.set_content(box)
        self.dialog.set_content(toolbar_view)

    def _update_state(self):
        count = sum(1 for _mid, c in self._checks if c.get_active())
        total = len(self._checks)
        self._run_btn.set_sensitive(count > 0)
        self._run_btn.set_label(
            _("Run on {count}").format(count=count) if count > 1 else _("Run")
        )
        self._select_all_btn.set_label(
            _("Deselect all") if count == total else _("Select all")
        )

    def _on_toggle_all(self, _btn):
        count = sum(1 for _mid, c in self._checks if c.get_active())
        select = count < len(self._checks)
        for _mid, c in self._checks:
            c.set_active(select)

    def _on_run(self, _btn):
        chosen = [mid for mid, c in self._checks if c.get_active()]
        if chosen:
            self.dialog.close()
            self._on_chosen(chosen)
