pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()

gnome.compile_resources('remotex',
  'resources/remotex.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  source_dir: meson.current_source_dir() / 'resources',
)

install_data(
  'com.github.remotex.RemoteX.gschema.xml',
  install_dir: get_option('prefix') / get_option('datadir') / 'glib-2.0' / 'schemas',
)

desktop_conf = configuration_data()
desktop_conf.set('icon', 'utilities-terminal-symbolic')

configure_file(
  input: 'com.github.remotex.RemoteX.desktop.in',
  output: 'com.github.remotex.RemoteX.desktop',
  configuration: desktop_conf,
  install: true,
  install_dir: get_option('prefix') / get_option('datadir') / 'applications',
)
