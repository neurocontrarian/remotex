project('remotex',
  version: '1.6.0',
  meson_version: '>= 0.62.0',
  default_options: ['warning_level=2'],
)

gnome = import('gnome')
python = import('python')
i18n = import('i18n')

py = python.find_installation('python3', required: true)

pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
schemadir = get_option('prefix') / get_option('datadir') / 'glib-2.0' / 'schemas'
localedir = get_option('prefix') / get_option('localedir')

subdir('data')
subdir('src')
# `po/` is a stub from the GNOME template; RemoteX uses its own JSON i18n
# in src/translations/. The gettext pipeline is intentionally not wired up.
# subdir('po')
