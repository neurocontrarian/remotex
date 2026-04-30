pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
schemadir = get_option('prefix') / get_option('datadir') / 'glib-2.0' / 'schemas'
localedir = get_option('prefix') / get_option('localedir')

conf = configuration_data()
conf.set('PYTHON', py.full_path())
conf.set('pkgdatadir', pkgdatadir)
conf.set('localedir', localedir)
conf.set('schemadir', schemadir)

configure_file(
  input: 'remotex.in',
  output: 'remotex',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
)

# ── Free / open-source sources (always installed) ───────────────────────────

free_sources = [
  'main.py',
  'window.py',
  'button_tile.py',
  'i18n.py',
  'feature_gate.py',
]

install_data(free_sources, install_dir: pkgdatadir)

free_model_sources = [
  'models/__init__.py',
  'models/command_button.py',
  'models/config.py',
  'models/_default_buttons.py',
]

install_data(free_model_sources, install_dir: pkgdatadir / 'models')

free_service_sources = [
  'services/__init__.py',
  'services/executor.py',
  'services/keyring_service.py',
  'services/password_store.py',
]

install_data(free_service_sources, install_dir: pkgdatadir / 'services')

free_dialog_sources = [
  'dialogs/__init__.py',
  'dialogs/confirm_dialog.py',
  'dialogs/output_dialog.py',
  'dialogs/command_dialog.py',
  'dialogs/preferences_dialog.py',
]

install_data(free_dialog_sources, install_dir: pkgdatadir / 'dialogs')

util_sources = [
  'utils/__init__.py',
  'utils/threading.py',
  'utils/desktop.py',
  'utils/icon_loader.py',
]

install_data(util_sources, install_dir: pkgdatadir / 'utils')

translation_sources = [
  'translations/ar.json',
  'translations/de.json',
  'translations/es.json',
  'translations/fr.json',
  'translations/hi.json',
  'translations/it.json',
  'translations/ja.json',
  'translations/ko.json',
  'translations/pt.json',
  'translations/ru.json',
  'translations/zh.json',
]

install_data(translation_sources, install_dir: pkgdatadir / 'translations')

# ── Pro / proprietary sources (installed only when -Dpro=true) ──────────────

if get_option('pro')
  pro_sources = [
    'pro/__init__.py',
    'pro/license.py',
    'pro/mcp_server.py',
  ]
  install_data(pro_sources, install_dir: pkgdatadir / 'pro')

  pro_model_sources = [
    'pro/models/__init__.py',
    'pro/models/machine.py',
    'pro/models/execution_profile.py',
  ]
  install_data(pro_model_sources, install_dir: pkgdatadir / 'pro' / 'models')

  pro_service_sources = [
    'pro/services/__init__.py',
    'pro/services/ssh_service.py',
    'pro/services/ssh_key_service.py',
    'pro/services/executor_pro.py',
  ]
  install_data(pro_service_sources, install_dir: pkgdatadir / 'pro' / 'services')

  pro_dialog_sources = [
    'pro/dialogs/__init__.py',
    'pro/dialogs/machine_dialog.py',
    'pro/dialogs/machines_list_dialog.py',
    'pro/dialogs/machine_picker_dialog.py',
    'pro/dialogs/profile_dialog.py',
    'pro/dialogs/profiles_list_dialog.py',
  ]
  install_data(pro_dialog_sources, install_dir: pkgdatadir / 'pro' / 'dialogs')
endif
