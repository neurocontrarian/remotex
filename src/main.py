import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib

APP_VERSION = "1.3.8"


def _suppress_svg_icon_warnings(log_domain, log_level, message, user_data):
    """Drop 'Failed to load icon ... .svg' warnings — resolve_icon() handles fallback."""
    if message and 'Failed to load icon' in message and '.svg' in message:
        return
    GLib.log_default_handler(log_domain, log_level, message, user_data)


# Old-style g_log() handler
GLib.log_set_handler('Gtk', GLib.LogLevelFlags.LEVEL_WARNING,
                     _suppress_svg_icon_warnings, None)

# New-style g_log_structured() handler (GTK4 uses this for some warnings)
import ctypes as _ctypes

def _is_svg_load_warning(fields) -> bool:
    try:
        for field in fields:
            if field.key == 'MESSAGE' and field.value:
                ptr = field.value
                length = field.length
                try:
                    raw = _ctypes.string_at(ptr) if length == -1 else _ctypes.string_at(ptr, length)
                    msg = raw.decode('utf-8', errors='replace')
                    return 'Failed to load icon' in msg and '.svg' in msg
                except Exception:
                    pass
    except Exception:
        pass
    return False

try:
    def _structured_log_writer(log_level, fields, n_fields, user_data):
        if _is_svg_load_warning(fields):
            return GLib.LogWriterOutput.HANDLED
        return GLib.log_writer_default(log_level, fields, user_data)

    GLib.log_set_writer_func(_structured_log_writer, None)
except (AttributeError, TypeError):
    pass  # not available in this GLib version — old handler still active

Gtk.Window.set_default_icon_name('com.github.remotex.RemoteX')

from window import RemotexWindow
from dialogs.preferences_dialog import show_preferences_dialog
from i18n import _


class RemotexApplication(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id='com.github.remotex.RemoteX',
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
            resource_base_path='/com/github/remotex/RemoteX',
        )

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = RemotexWindow(application=self)
            self._load_css()
        win.present()

    def do_startup(self):
        Adw.Application.do_startup(self)
        self._migrate_settings()
        self._load_language()
        self._setup_actions()
        self._schedule_license_revalidation()

    def _migrate_settings(self):
        """Apply one-time migrations when schema defaults change across versions.

        HOW TO ADD A MIGRATION:
          1. Increment CURRENT_VERSION below.
          2. Add an `if v < N:` block with the reset/set calls.
          3. Document the change in CLAUDE.md under GSettings migrations.
        Never change a schema <default> without adding a migration here.
        """
        CURRENT_VERSION = 1
        try:
            s = Gio.Settings.new('com.github.remotex.RemoteX')
            v = s.get_int('settings-version')

            if v < 1:
                # confirm-before-run default changed false → true.
                # Reset users who inherited the old false default without
                # explicitly choosing it (best-effort: indistinguishable from
                # an intentional false, but the schema intent is true).
                user_val = s.get_user_value('confirm-before-run')
                if user_val is not None and not user_val.get_boolean():
                    s.reset('confirm-before-run')

            if v < CURRENT_VERSION:
                s.set_int('settings-version', CURRENT_VERSION)
        except Exception:
            pass

    def _schedule_license_revalidation(self):
        """Re-check the stored license with LemonSqueezy in a background thread."""
        from utils.threading import run_in_thread
        from pro.license import revalidate_license
        run_in_thread(revalidate_license, lambda _: None)

    def _load_language(self):
        try:
            from i18n import set_language
            settings = Gio.Settings.new('com.github.remotex.RemoteX')
            lang = settings.get_string('language')
            set_language(lang)
        except Exception:
            pass

    def _setup_actions(self):
        about_action = Gio.SimpleAction.new('about', None)
        about_action.connect('activate', self._on_about)
        self.add_action(about_action)

        manage_machines_action = Gio.SimpleAction.new('manage-machines', None)
        manage_machines_action.connect('activate', self._on_manage_machines)
        self.add_action(manage_machines_action)

        manage_profiles_action = Gio.SimpleAction.new('manage-profiles', None)
        manage_profiles_action.connect('activate', self._on_manage_profiles)
        self.add_action(manage_profiles_action)

        preferences_action = Gio.SimpleAction.new('preferences', None)
        preferences_action.connect('activate', self._on_preferences)
        self.add_action(preferences_action)
        self.set_accels_for_action('app.preferences', ['<primary>comma'])

        shortcuts_action = Gio.SimpleAction.new('shortcuts', None)
        shortcuts_action.connect('activate', self._on_shortcuts)
        self.add_action(shortcuts_action)
        self.set_accels_for_action('app.shortcuts', ['<primary>question'])

        quit_action = Gio.SimpleAction.new('quit', None)
        quit_action.connect('activate', lambda *_: self.quit())
        self.add_action(quit_action)
        self.set_accels_for_action('app.quit', ['<primary>q'])

        add_button_action = Gio.SimpleAction.new('add-button', None)
        add_button_action.connect('activate', self._on_add_button)
        self.add_action(add_button_action)
        self.set_accels_for_action('app.add-button', ['<primary>n'])

        refresh_action = Gio.SimpleAction.new('refresh', None)
        refresh_action.connect('activate', self._on_refresh)
        self.add_action(refresh_action)
        self.set_accels_for_action('app.refresh', ['F5'])

    def _load_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_resource('/com/github/remotex/RemoteX/style.css')
        display = self.props.active_window.get_display()
        Gtk.StyleContext.add_provider_for_display(
            display,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
        # Register our gresource icons so symbolic icons (rendered via Cairo,
        # not GdkPixbuf) are available to GTK — fixes missing icons in About dialog
        # on distros like Linux Mint where the system theme lacks some symbolics.
        Gtk.IconTheme.get_for_display(display).add_resource_path(
            '/com/github/remotex/RemoteX'
        )

    def _on_about(self, action, param):
        from i18n import _
        about = Adw.AboutWindow(
            application_name='RemoteX',
            application_icon='com.github.remotex.RemoteX',
            developer_name='neurocontrarian',
            version=APP_VERSION,
            comments=_("Visual command launcher for Linux — run local and SSH commands with one click."),
            license_type=Gtk.License.MIT_X11,
            developers=['neurocontrarian'],
            website='https://github.com/neurocontrarian/remotex',
            transient_for=self.props.active_window,
            modal=True,
        )
        about.add_link(_("Report an Issue"), 'https://github.com/neurocontrarian/remotex/issues')
        about.present()

    def _on_manage_machines(self, action, param):
        from pro.license import is_pro_active
        win = self.props.active_window
        if not win:
            return
        if not is_pro_active():
            win._show_pro_limit_dialog(
                _("Pro feature"),
                _("Manage Machines requires RemoteX Pro.\n"
                  "Upgrade to connect to remote machines via SSH."),
            )
            return
        win.show_machines_dialog()

    def _on_manage_profiles(self, action, param):
        from pro.license import is_pro_active
        win = self.props.active_window
        if not win:
            return
        if not is_pro_active():
            win._show_pro_limit_dialog(
                _("Pro feature"),
                _("Execution Profiles require RemoteX Pro.\n"
                  "Upgrade to use named execution contexts on your buttons."),
            )
            return
        from dialogs.profiles_list_dialog import show_profiles_list
        show_profiles_list(win, win._config)

    def _on_preferences(self, action, param):
        win = self.props.active_window
        if win:
            dlg = show_preferences_dialog(win, win._config)
            dlg.connect('destroy', lambda _: win.populate_grid())

    def _on_shortcuts(self, action, param):
        win = self.props.active_window
        if not win:
            return
        builder = Gtk.Builder.new_from_resource(
            '/com/github/remotex/RemoteX/ui/shortcuts_window.ui'
        )
        shortcuts_win = builder.get_object('shortcuts_window')
        shortcuts_win.set_transient_for(win)
        shortcuts_win.present()

    def _on_refresh(self, action, param):
        win = self.props.active_window
        if win:
            win.populate_grid(flash=True)

    def _on_add_button(self, action, param):
        win = self.props.active_window
        if win:
            win._on_add_button(action, param)


def main():
    app = RemotexApplication()
    return app.run(sys.argv)


if __name__ == '__main__':
    sys.exit(main())
