project('remotex',
  version: '0.1.0',
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
subdir('po')
