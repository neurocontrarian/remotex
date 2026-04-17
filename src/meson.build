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

sources = [
  'main.py',
  'window.py',
  'button_tile.py',
]

install_data(sources, install_dir: pkgdatadir)

model_sources = [
  'models/__init__.py',
  'models/machine.py',
  'models/command_button.py',
  'models/config.py',
]

install_data(model_sources, install_dir: pkgdatadir / 'models')

service_sources = [
  'services/__init__.py',
  'services/executor.py',
  'services/ssh_service.py',
  'services/ssh_key_service.py',
]

install_data(service_sources, install_dir: pkgdatadir / 'services')

dialog_sources = [
  'dialogs/__init__.py',
  'dialogs/confirm_dialog.py',
  'dialogs/output_dialog.py',
  'dialogs/machine_dialog.py',
  'dialogs/machines_list_dialog.py',
  'dialogs/command_dialog.py',
  'dialogs/preferences_dialog.py',
]

install_data(dialog_sources, install_dir: pkgdatadir / 'dialogs')

util_sources = [
  'utils/__init__.py',
  'utils/threading.py',
]

install_data(util_sources, install_dir: pkgdatadir / 'utils')

pro_sources = [
  'pro/__init__.py',
  'pro/license.py',
]

install_data(pro_sources, install_dir: pkgdatadir / 'pro')
