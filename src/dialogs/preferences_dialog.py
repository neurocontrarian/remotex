import sys
from pathlib import Path

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib

from pro.license import (
    is_pro_active, get_license_key, get_license_info,
    clear_license_key, validate_license_online,
    FREE_BUTTON_LIMIT, FREE_MACHINE_LIMIT, PRO_INFO_URL, PRO_BUY_URL,
)
from i18n import _, set_language, SUPPORTED_LANGUAGES


def show_preferences_dialog(parent, config=None):
    try:
        settings = Gio.Settings.new('com.github.remotex.RemoteX')
    except Exception:
        settings = None

    dialog = Adw.Window(title=_("Preferences"))
    from utils.desktop import make_floating_window
    make_floating_window(dialog, parent, 480, 660)

    toolbar_view = Adw.ToolbarView()
    toolbar_view.add_top_bar(Adw.HeaderBar())
    dialog.set_content(toolbar_view)

    page = Adw.PreferencesPage()
    toolbar_view.set_content(page)

    # ── Command Execution ────────────────────────────────────────────────
    exec_group = Adw.PreferencesGroup(title=_("Command Execution"))
    page.add(exec_group)

    timeout_row = Adw.SpinRow.new_with_range(5, 300, 5)
    timeout_row.set_title(_("Command timeout"))
    timeout_row.set_subtitle(_("Maximum duration before a command is killed (seconds)"))
    timeout_row.set_value(settings.get_int('command-timeout') if settings else 30)
    if settings:
        timeout_row.connect(
            'notify::value',
            lambda row, _: settings.set_int('command-timeout', int(row.get_value())),
        )
    exec_group.add(timeout_row)

    confirm_row = Adw.SwitchRow()
    confirm_row.set_title(_("Default confirmation"))
    confirm_row.set_subtitle(_("Pre-tick 'Confirm before running' for all new buttons"))
    confirm_row.set_active(settings.get_boolean('confirm-before-run') if settings else False)
    if settings:
        confirm_row.connect(
            'notify::active',
            lambda row, _: settings.set_boolean('confirm-before-run', row.get_active()),
        )
    exec_group.add(confirm_row)

    # ── Interface ────────────────────────────────────────────────────────
    interface_group = Adw.PreferencesGroup(title=_("Interface"))
    page.add(interface_group)

    lang_codes = list(SUPPORTED_LANGUAGES.keys())
    lang_model = Gtk.StringList()
    for label in SUPPORTED_LANGUAGES.values():
        lang_model.append(label)

    lang_row = Adw.ComboRow(title=_("Language"))
    lang_row.set_subtitle(_("Interface language — restart required"))
    lang_row.set_tooltip_text(_("Restart RemoteX to apply the language change"))
    lang_row.set_model(lang_model)
    current_lang = settings.get_string('language') if settings else "system"
    lang_row.set_selected(lang_codes.index(current_lang) if current_lang in lang_codes else 0)
    _lang_handler_active = False

    def _on_lang_changed(row, _param):
        nonlocal _lang_handler_active
        if not _lang_handler_active:
            return
        lang = lang_codes[row.get_selected()]
        if lang == current_lang:
            return
        if settings:
            settings.set_string('language', lang)
        set_language(lang)
        dialog.close()
        if hasattr(parent, 'show_toast'):
            parent.show_toast(_("Language changed — restart RemoteX to apply"))

    def _activate_lang_handler():
        nonlocal _lang_handler_active
        _lang_handler_active = True
        return False

    lang_row.connect('notify::selected', _on_lang_changed)
    # Adw.ComboRow emits spurious notify::selected after set_model()/set_selected().
    # Block the handler until signals have settled; 300ms covers deferred emissions.
    GLib.timeout_add(300, _activate_lang_handler)
    interface_group.add(lang_row)

    scheme_model = Gtk.StringList()
    scheme_labels = [_("Follow system"), _("Light"), _("Dark")]
    scheme_values = ["system", "light", "dark"]
    for label in scheme_labels:
        scheme_model.append(label)

    scheme_row = Adw.ComboRow(title=_("Color scheme"))
    scheme_row.set_subtitle(_("Override the system dark/light mode"))
    scheme_row.set_model(scheme_model)
    current_scheme = settings.get_string('color-scheme') if settings else "system"
    scheme_row.set_selected(scheme_values.index(current_scheme) if current_scheme in scheme_values else 0)
    if settings:
        scheme_row.connect(
            'notify::selected',
            lambda row, _: settings.set_string('color-scheme', scheme_values[row.get_selected()]),
        )
    interface_group.add(scheme_row)

    # ── Button Grid Layout ───────────────────────────────────────────────
    grid_group = Adw.PreferencesGroup(title=_("Button Grid Layout"))
    page.add(grid_group)

    cols_row = Adw.SpinRow.new_with_range(1, 20, 1)
    cols_row.set_title(_("Buttons per row"))
    cols_row.set_subtitle(_("Fixed number of buttons on each row"))
    cols_row.set_value(settings.get_int('grid-columns') if settings else 4)
    if settings:
        cols_row.connect(
            'notify::value',
            lambda row, _: settings.set_int('grid-columns', int(row.get_value())),
        )
    grid_group.add(cols_row)

    # ── Button Appearance ────────────────────────────────────────────────
    appearance_group = Adw.PreferencesGroup(title=_("Button Appearance"))
    page.add(appearance_group)

    size_model = Gtk.StringList()
    size_model.append(_("Small  (80×80)"))
    size_model.append(_("Medium  (120×120)"))
    size_model.append(_("Large  (160×160)"))
    size_values = ["small", "medium", "large"]

    size_row = Adw.ComboRow(title=_("Button size"))
    size_row.set_subtitle(_("Size of each button tile in the grid"))
    size_row.set_model(size_model)
    current_size = settings.get_string('button-size') if settings else "medium"
    size_row.set_selected(size_values.index(current_size) if current_size in size_values else 1)
    if settings:
        size_row.connect(
            'notify::selected',
            lambda row, _: settings.set_string('button-size', size_values[row.get_selected()]),
        )
    appearance_group.add(size_row)

    theme_model = Gtk.StringList()
    theme_labels = [_("Bold (default)"), _("Cards"), _("Phone keys"), _("Neon"), _("Retro"), _("Custom CSS…")]
    theme_values = ["bold", "cards", "phone", "neon", "retro", "custom"]
    for label in theme_labels:
        theme_model.append(label)

    theme_row = Adw.ComboRow(title=_("Button theme"))
    theme_row.set_subtitle(_("Visual style of button tiles — Pro feature"))
    theme_row.set_model(theme_model)

    _pro = is_pro_active()
    current_theme = settings.get_string('button-theme') if (settings and _pro) else "bold"
    if settings and _pro:
        _idx = theme_values.index(current_theme) if current_theme in theme_values else 0
        theme_row.set_selected(_idx)
    else:
        theme_row.set_selected(0)
        theme_row.set_sensitive(False)
        lock_icon = Gtk.Image.new_from_icon_name("changes-prevent-symbolic")
        lock_icon.set_tooltip_text(_("Upgrade to Pro to unlock custom themes"))
        lock_icon.add_css_class("dim-label")
        theme_row.add_suffix(lock_icon)
    appearance_group.add(theme_row)

    # ── Custom CSS file row (shown/sensitive only when "Custom CSS" is active) ──
    _custom_path = settings.get_string('custom-theme-path') if (settings and _pro) else ""
    _path_subtitle = _custom_path if _custom_path else _("No file selected")

    custom_file_row = Adw.ActionRow(title=_("Custom CSS file"))
    custom_file_row.set_subtitle(_path_subtitle)
    custom_file_row.set_tooltip_text(
        _("A CSS file targeting .button-tile to style your buttons.\n"
          "Export a template to see the available selectors and named colors.")
    )
    # Always sensitive for Pro — browsing/exporting a template is independent of
    # which theme is currently active. Free users see the row grayed out.
    custom_file_row.set_sensitive(_pro)

    browse_btn = Gtk.Button(icon_name="document-open-symbolic", valign=Gtk.Align.CENTER,
                            tooltip_text=_("Browse for a CSS file"))
    browse_btn.add_css_class("flat")
    browse_btn.add_css_class("circular")

    template_btn = Gtk.Button(icon_name="document-save-symbolic", valign=Gtk.Align.CENTER,
                              tooltip_text=_("Export a starter template CSS file"))
    template_btn.add_css_class("flat")
    template_btn.add_css_class("circular")

    custom_file_row.add_suffix(template_btn)
    custom_file_row.add_suffix(browse_btn)
    appearance_group.add(custom_file_row)

    def _on_theme_changed(row, _):
        val = theme_values[row.get_selected()]
        if settings:
            settings.set_string('button-theme', val)

    if settings and _pro:
        theme_row.connect('notify::selected', _on_theme_changed)

    def _on_browse_css(_btn):
        file_dialog = Gtk.FileDialog(title=_("Select CSS theme file"))
        filter_ = Gtk.FileFilter()
        filter_.set_name("CSS files (*.css)")
        filter_.add_pattern("*.css")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_)
        file_dialog.set_filters(filters)

        def _on_done(dlg, result):
            try:
                gfile = dlg.open_finish(result)
                if gfile and settings:
                    path = gfile.get_path()
                    settings.set_string('custom-theme-path', path)
                    custom_file_row.set_subtitle(path)
            except Exception:
                pass

        file_dialog.open(dialog, None, _on_done)

    browse_btn.connect('clicked', _on_browse_css)

    def _on_export_template(_btn):
        file_dialog = Gtk.FileDialog(title=_("Export CSS template"))
        filter_ = Gtk.FileFilter()
        filter_.set_name("CSS files (*.css)")
        filter_.add_pattern("*.css")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_)
        file_dialog.set_filters(filters)
        file_dialog.set_initial_name("remotex-theme.css")

        def _on_save(dlg, result):
            try:
                gfile = dlg.save_finish(result)
                if gfile:
                    from pathlib import Path
                    Path(gfile.get_path()).write_text(_THEME_TEMPLATE)
            except Exception:
                pass

        file_dialog.save(dialog, None, _on_save)

    template_btn.connect('clicked', _on_export_template)

    # ── Categories ───────────────────────────────────────────────────────
    categories = []
    if config:
        buttons = config.load_buttons()
        categories = sorted({b.category for b in buttons if b.category})

    if categories and settings:
        cat_group = Adw.PreferencesGroup(title=_("Categories"))
        cat_group.set_description(_("Hidden categories and their buttons will not appear in the grid"))
        page.add(cat_group)

        hidden = set(settings.get_strv('hidden-categories'))

        def make_toggle_handler(cat_name):
            def on_toggle(row, _):
                current_hidden = set(settings.get_strv('hidden-categories'))
                if row.get_active():
                    current_hidden.discard(cat_name)
                else:
                    current_hidden.add(cat_name)
                settings.set_strv('hidden-categories', sorted(current_hidden))
            return on_toggle

        for cat in categories:
            row = Adw.SwitchRow()
            row.set_title(cat)
            row.set_active(cat not in hidden)
            row.connect('notify::active', make_toggle_handler(cat))
            cat_group.add(row)

    # ── Custom Icon Directories ──────────────────────────────────────────
    if settings:
        icons_group = Adw.PreferencesGroup(title=_("Custom Icon Directories"))
        icons_group.set_description(
            _("Directories searched for icons before the bundled Bootstrap Icons set.\n"
              "Place .png or .svg files named after the icon (e.g. my-icon.svg) in any listed folder.")
        )
        page.add(icons_group)

        _icon_rows = []

        def _refresh_icon_rows():
            for row in _icon_rows:
                icons_group.remove(row)
            _icon_rows.clear()

            paths = settings.get_strv('icon-search-paths')
            for path in paths:
                row = Adw.ActionRow(title=path)
                row.set_subtitle(_("Click × to remove"))
                remove_btn = Gtk.Button(icon_name="user-trash-symbolic",
                                        valign=Gtk.Align.CENTER,
                                        tooltip_text=_("Remove this directory"))
                remove_btn.add_css_class("flat")
                remove_btn.add_css_class("circular")

                def _on_remove(_btn, p=path):
                    current = list(settings.get_strv('icon-search-paths'))
                    if p in current:
                        current.remove(p)
                        settings.set_strv('icon-search-paths', current)
                    _refresh_icon_rows()

                remove_btn.connect('clicked', _on_remove)
                row.add_suffix(remove_btn)
                _icon_rows.append(row)
                icons_group.add(row)

            add_row = Adw.ActionRow(title=_("Add directory…"))
            add_row.set_subtitle(_("Browse for a folder containing icon files"))
            add_row.set_activatable(True)
            add_btn = Gtk.Button(icon_name="folder-new-symbolic",
                                 valign=Gtk.Align.CENTER,
                                 tooltip_text=_("Browse for a folder containing icon files"))
            add_btn.add_css_class("flat")
            add_btn.add_css_class("circular")
            add_row.add_suffix(add_btn)

            def _on_add(_widget):
                file_dialog = Gtk.FileDialog(title="Select icon directory")
                file_dialog.select_folder(parent, None, _on_folder_chosen)

            def _on_folder_chosen(dlg, result):
                try:
                    folder = dlg.select_folder_finish(result)
                    if folder:
                        current = list(settings.get_strv('icon-search-paths'))
                        new_path = folder.get_path()
                        if new_path and new_path not in current:
                            current.append(new_path)
                            settings.set_strv('icon-search-paths', current)
                        _refresh_icon_rows()
                except Exception:
                    pass

            add_btn.connect('clicked', _on_add)
            add_row.connect('activated', _on_add)
            _icon_rows.append(add_row)
            icons_group.add(add_row)

        _refresh_icon_rows()

    # ── Desktop Integration ──────────────────────────────────────────────
    desktop_group = Adw.PreferencesGroup(title=_("Desktop Integration"))
    page.add(desktop_group)

    always_on_top_row = Adw.SwitchRow()
    always_on_top_row.set_title(_("Always on top"))
    always_on_top_row.set_subtitle(_("Keep RemoteX above all other windows"))
    always_on_top_row.set_active(settings.get_boolean('always-on-top') if settings else False)
    if settings:
        always_on_top_row.connect(
            'notify::active',
            lambda row, _: settings.set_boolean('always-on-top', row.get_active()),
        )
    desktop_group.add(always_on_top_row)

    autostart_path = Path.home() / '.config' / 'autostart' / 'remotex.desktop'
    autostart_row = Adw.SwitchRow()
    autostart_row.set_title(_("Launch at login"))
    autostart_row.set_subtitle(_("Start RemoteX automatically when you log in"))
    autostart_row.set_active(autostart_path.exists())

    def _on_autostart_toggle(row, _):
        if row.get_active():
            autostart_path.parent.mkdir(parents=True, exist_ok=True)
            exe = sys.argv[0]
            exec_line = f'{sys.executable} {exe}' if exe.endswith('.py') else exe
            autostart_path.write_text(
                '[Desktop Entry]\n'
                'Type=Application\n'
                'Name=RemoteX\n'
                f'Exec={exec_line}\n'
                'Hidden=false\n'
                'NoDisplay=false\n'
                'X-GNOME-Autostart-enabled=true\n'
            )
        else:
            autostart_path.unlink(missing_ok=True)

    autostart_row.connect('notify::active', _on_autostart_toggle)
    desktop_group.add(autostart_row)

    mcp_flag = Path.home() / '.config' / 'remotex' / '.mcp_enabled'
    mcp_row = Adw.SwitchRow()
    mcp_row.set_title(_("Allow MCP access"))
    mcp_row.set_subtitle(_("Let AI assistants (Claude Desktop, Cursor…) read and edit your buttons via MCP"))
    mcp_row.set_active(mcp_flag.exists())

    def _on_mcp_toggle(row, _):
        if row.get_active():
            mcp_flag.parent.mkdir(parents=True, exist_ok=True)
            mcp_flag.touch()
        else:
            mcp_flag.unlink(missing_ok=True)

    mcp_row.connect('notify::active', _on_mcp_toggle)
    desktop_group.add(mcp_row)

    # ── Backup & Restore (Pro) ────────────────────────────────────────────
    if is_pro_active() and config:
        # Buttons + Settings
        buttons_group = Adw.PreferencesGroup(title=_("Buttons &amp; Settings Backup"))
        buttons_group.set_description(
            _("Export your buttons and settings to a .rxbackup file. "
              "Machines are not included — export them separately below.")
        )
        page.add(buttons_group)

        export_row = Adw.ActionRow(title=_("Export buttons &amp; settings"))
        export_row.set_subtitle(_("Save buttons and preferences to a .rxbackup file"))
        export_row.set_activatable(True)
        export_row.add_suffix(Gtk.Image.new_from_icon_name("document-save-symbolic"))
        export_row.connect("activated", lambda _: _on_export(parent, config, settings))
        buttons_group.add(export_row)

        import_row = Adw.ActionRow(title=_("Import buttons &amp; settings"))
        import_row.set_subtitle(_("Restore from a .rxbackup file"))
        import_row.set_activatable(True)
        import_row.add_suffix(Gtk.Image.new_from_icon_name("document-open-symbolic"))
        import_row.connect("activated", lambda _: _on_import(parent, config, settings))
        buttons_group.add(import_row)

        # Machines
        machines_group = Adw.PreferencesGroup(title=_("Machines Backup"))
        machines_group.set_description(
            _("Export SSH machine definitions (hosts, usernames, ports) to a .rxmachines file. "
              "SSH private keys are never stored — reconfigure them after restoring.")
        )
        page.add(machines_group)

        export_machines_row = Adw.ActionRow(title=_("Export machines"))
        export_machines_row.set_subtitle(_("Save machine list to a .rxmachines file"))
        export_machines_row.set_activatable(True)
        export_machines_row.add_suffix(Gtk.Image.new_from_icon_name("document-save-symbolic"))
        export_machines_row.connect("activated", lambda _: _on_export_machines(parent, config))
        machines_group.add(export_machines_row)

        import_machines_row = Adw.ActionRow(title=_("Import machines"))
        import_machines_row.set_subtitle(_("Restore machine list from a .rxmachines file"))
        import_machines_row.set_activatable(True)
        import_machines_row.add_suffix(Gtk.Image.new_from_icon_name("document-open-symbolic"))
        import_machines_row.connect("activated", lambda _: _on_import_machines(parent, config))
        machines_group.add(import_machines_row)

    # ── License ──────────────────────────────────────────────────────────
    license_group = Adw.PreferencesGroup(title=_("License"))
    page.add(license_group)

    def _on_license_changed():
        dialog.close()
        def _reopen():
            show_preferences_dialog(parent, config)
        GLib.idle_add(_reopen)

    license_rows: list = []
    _build_license_section(license_group, license_rows, on_change=_on_license_changed)

    dialog.present()
    return dialog


def _on_export(parent, config, settings):
    from pathlib import Path
    file_dialog = Gtk.FileDialog(title=_("Export config backup"))
    filter_ = Gtk.FileFilter()
    filter_.set_name("RemoteX backup (*.rxbackup)")
    filter_.add_pattern("*.rxbackup")
    filters = Gio.ListStore.new(Gtk.FileFilter)
    filters.append(filter_)
    file_dialog.set_filters(filters)
    file_dialog.set_initial_name("remotex.rxbackup")

    def on_done(dlg, result):
        try:
            gfile = dlg.save_finish(result)
            if gfile:
                config.export_backup(Path(gfile.get_path()), settings)
                _show_toast(parent, _("Config exported successfully"))
        except Exception as e:
            _show_toast(parent, _("Export failed: {error}").format(error=e))

    file_dialog.save(parent, None, on_done)


def _on_import(parent, config, settings):
    from pathlib import Path
    file_dialog = Gtk.FileDialog(title=_("Import config backup"))
    filter_ = Gtk.FileFilter()
    filter_.set_name("RemoteX backup (*.rxbackup)")
    filter_.add_pattern("*.rxbackup")
    filters = Gio.ListStore.new(Gtk.FileFilter)
    filters.append(filter_)
    file_dialog.set_filters(filters)

    def on_done(dlg, result):
        try:
            gfile = dlg.open_finish(result)
            if gfile:
                config.import_backup(Path(gfile.get_path()), settings)
                _show_toast(parent, _("Config imported — restart RemoteX to apply all changes"))
        except Exception as e:
            _show_toast(parent, _("Import failed: {error}").format(error=e))

    file_dialog.open(parent, None, on_done)


def _on_export_machines(parent, config):
    from pathlib import Path
    file_dialog = Gtk.FileDialog(title=_("Export machines"))
    filter_ = Gtk.FileFilter()
    filter_.set_name("RemoteX machines (*.rxmachines)")
    filter_.add_pattern("*.rxmachines")
    filters = Gio.ListStore.new(Gtk.FileFilter)
    filters.append(filter_)
    file_dialog.set_filters(filters)
    file_dialog.set_initial_name("remotex.rxmachines")

    def on_done(dlg, result):
        try:
            gfile = dlg.save_finish(result)
            if gfile:
                config.export_machines_backup(Path(gfile.get_path()))
                _show_toast(parent, _("Machines exported successfully"))
        except Exception as e:
            _show_toast(parent, _("Export failed: {error}").format(error=e))

    file_dialog.save(parent, None, on_done)


def _on_import_machines(parent, config):
    from pathlib import Path
    file_dialog = Gtk.FileDialog(title=_("Import machines"))
    filter_ = Gtk.FileFilter()
    filter_.set_name("RemoteX machines (*.rxmachines)")
    filter_.add_pattern("*.rxmachines")
    filters = Gio.ListStore.new(Gtk.FileFilter)
    filters.append(filter_)
    file_dialog.set_filters(filters)

    def on_done(dlg, result):
        try:
            gfile = dlg.open_finish(result)
            if gfile:
                config.import_machines_backup(Path(gfile.get_path()))
                _show_toast(parent, _("Machines imported — restart RemoteX to apply"))
        except Exception as e:
            _show_toast(parent, _("Import failed: {error}").format(error=e))

    file_dialog.open(parent, None, on_done)


def _show_toast(parent, message: str):
    """Show a toast on the parent window if it has a toast overlay."""
    try:
        parent.show_toast(message)
    except AttributeError:
        pass


def _build_license_section(group: Adw.PreferencesGroup, rows: list, on_change=None):
    """Build (or rebuild) the license rows inside the given group."""
    for row in rows:
        group.remove(row)
    rows.clear()

    info = get_license_info()

    def _do_deactivate(_):
        clear_license_key()
        if on_change:
            on_change()
        else:
            _build_license_section(group, rows)

    if info['active']:
        # ── Pro active ───────────────────────────────────────────────────
        is_yearly = info['type'] == 'yearly'
        days = info['days_until_expiry']

        if is_yearly:
            title = _("RemoteX Pro — Yearly")
            if days is not None and days <= 30:
                subtitle = _("Expires in {days} days ({date}) — renew to keep Pro access").format(
                    days=max(0, days), date=info['expires'])
            else:
                subtitle = _("Yearly license — expires on {date}").format(date=info['expires'] or '—')
        else:
            title = _("RemoteX Pro — Lifetime")
            subtitle = _("Lifetime license — enjoy all Pro features!")

        status_row = Adw.ActionRow(title=title)
        status_row.set_subtitle(subtitle)
        icon = Gtk.Image.new_from_icon_name("object-select-symbolic")
        icon.add_css_class("success" if not (is_yearly and days is not None and days <= 30) else "warning")
        status_row.add_suffix(icon)
        rows.append(status_row)

        key_row = Adw.ActionRow(title=_("License key"))
        key = info['key']
        masked = key[:4] + "·" * max(0, len(key) - 8) + key[-4:] if len(key) > 8 else key
        key_row.set_subtitle(masked)
        rows.append(key_row)

        if is_yearly:
            renew_row = Adw.ActionRow(title=_("Renew license"))
            renew_row.set_subtitle(_("Get a new yearly key at the same price"))
            renew_row.set_activatable(True)
            renew_row.add_css_class("suggested-action")
            renew_row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
            renew_row.connect("activated", lambda _: _open_url(PRO_BUY_URL))
            rows.append(renew_row)

        deactivate_row = Adw.ActionRow(title=_("Deactivate license"))
        deactivate_row.set_subtitle(_("Remove the license key from this device"))
        deactivate_row.set_activatable(True)
        deactivate_row.add_css_class("error")
        deactivate_row.connect("activated", _do_deactivate)
        rows.append(deactivate_row)

    elif info['is_expired']:
        # ── Yearly license expired ───────────────────────────────────────
        status_row = Adw.ActionRow(title=_("License expired"))
        status_row.set_subtitle(
            _("Your yearly license expired on {date}. Free tier limits now apply.").format(
                date=info['expires'] or '—')
        )
        icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
        icon.add_css_class("error")
        status_row.add_suffix(icon)
        rows.append(status_row)

        key_row = Adw.ActionRow(title=_("License key"))
        key = info['key']
        masked = key[:4] + "·" * max(0, len(key) - 8) + key[-4:] if len(key) > 8 else key
        key_row.set_subtitle(masked)
        rows.append(key_row)

        renew_row = Adw.ActionRow(title=_("Renew license"))
        renew_row.set_subtitle(_("Restore Pro access with a new license key"))
        renew_row.set_activatable(True)
        renew_row.add_css_class("suggested-action")
        renew_row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
        renew_row.connect("activated", lambda _: _open_url(PRO_BUY_URL))
        rows.append(renew_row)

        deactivate_row = Adw.ActionRow(title=_("Remove expired key"))
        deactivate_row.set_activatable(True)
        deactivate_row.add_css_class("error")
        deactivate_row.connect("activated", _do_deactivate)
        rows.append(deactivate_row)

    else:
        # ── Free tier ────────────────────────────────────────────────────
        status_row = Adw.ActionRow(title=_("Free tier"))
        status_row.set_subtitle(
            _("Limited to {btn_limit} custom buttons and {machine_limit} SSH machine. "
              "Upgrade to Pro for unlimited access.").format(
                btn_limit=FREE_BUTTON_LIMIT, machine_limit=FREE_MACHINE_LIMIT)
        )
        rows.append(status_row)

        key_entry = Adw.EntryRow(title=_("License key"))
        key_entry.set_input_purpose(Gtk.InputPurpose.FREE_FORM)
        key_entry.set_show_apply_button(False)
        rows.append(key_entry)

        activate_row = Adw.ActionRow(title=_("Activate Pro"))
        activate_row.set_subtitle(_("Enter your license key above, then click Activate"))
        activate_row.set_activatable(True)
        activate_row.add_css_class("suggested-action")
        activate_row.connect("activated", lambda _: _on_activate(key_entry, group, rows, on_change))
        rows.append(activate_row)

        buy_row = Adw.ActionRow(title=_("Get RemoteX Pro — $20/year or $40 lifetime"))
        buy_row.set_activatable(True)
        buy_row.connect("activated", lambda _: _open_url(PRO_BUY_URL))
        buy_row.add_suffix(Gtk.Image.new_from_icon_name("go-next-symbolic"))
        rows.append(buy_row)

    for row in rows:
        group.add(row)


def _on_activate(key_entry: Adw.EntryRow, group: Adw.PreferencesGroup, rows: list, on_change=None):
    key = key_entry.get_text().strip()
    if not key:
        key_entry.add_css_class("error")
        GLib.timeout_add(1500, lambda: key_entry.remove_css_class("error") or False)
        return

    # validate_license_online activates on LemonSqueezy and saves locally if valid
    valid, license_type, expires = validate_license_online(key)
    if not valid:
        key_entry.add_css_class("error")
        if license_type == 'network_error':
            orig_title = key_entry.get_title()
            key_entry.set_title(_("Internet connection required for activation"))
            def _reset(entry=key_entry, t=orig_title):
                entry.remove_css_class("error")
                entry.set_title(t)
                return False
            GLib.timeout_add(3000, _reset)
        else:
            GLib.timeout_add(1500, lambda: key_entry.remove_css_class("error") or False)
        return

    if on_change:
        on_change()
    else:
        _build_license_section(group, rows)




_THEME_TEMPLATE = """\
/* RemoteX Custom Button Theme
 *
 * Selectors you can style:
 *   .button-tile          — each button tile (background, border, shadow…)
 *   .button-tile:hover    — mouse hover state
 *   .button-tile:active   — pressed state
 *   .button-tile .tile-label — text label
 *
 * Useful GTK named colors (adapt to the active system theme):
 *   @accent_color         — accent color (e.g. blue on GNOME)
 *   @accent_bg_color      — accent background
 *   @accent_fg_color      — foreground on accent background (usually white)
 *   @card_bg_color        — card surface color
 *   @window_bg_color      — main window background
 *   @borders              — border/separator color
 *
 * GTK CSS functions: shade(color, factor), alpha(color, factor), mix(a, b, factor)
 *
 * Example — purple gradient theme:
 */

.button-tile {
  background: linear-gradient(135deg, #6a0dad 0%, #9b30d9 100%);
  border-radius: 12px;
  border: 2px solid rgba(255,255,255,0.2);
  box-shadow: 0 4px 12px rgba(0,0,0,0.35);
}

.button-tile:hover {
  background: linear-gradient(135deg, #7a1dbd 0%, #ab40e9 100%);
  box-shadow: 0 6px 18px rgba(0,0,0,0.4);
}

.button-tile:active {
  background: linear-gradient(135deg, #5a0090 0%, #8020c0 100%);
  box-shadow: 0 2px 6px rgba(0,0,0,0.3);
}

.button-tile .tile-label {
  color: #ffffff;
  font-weight: bold;
}
"""


def _load_pencil_icon():
    """Return a Gdk.Texture for the bundled pencil Bootstrap icon, or None."""
    try:
        from utils.icon_loader import load_icon_texture
        return load_icon_texture('pencil', 16)
    except Exception:
        return None


def _open_url(url: str):
    try:
        launcher = Gtk.UriLauncher(uri=url)
        launcher.launch(None, None, None)
    except Exception:
        import subprocess
        subprocess.Popen(
            ["/usr/bin/xdg-open", url],
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
