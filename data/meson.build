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

# App icons — installed to the system icon theme (separate from the gresource
# bundle) so that GNOME Software, the app launcher, and the taskbar can display them.
foreach size : ['48', '128', '256', '512']
  install_data(
    'resources/icons/hicolor' / size + 'x' + size / 'apps/com.github.remotex.RemoteX.png',
    install_dir: get_option('prefix') / get_option('datadir') / 'icons/hicolor' / size + 'x' + size / 'apps',
  )
endforeach

configure_file(
  input: 'com.github.remotex.RemoteX.desktop.in',
  output: 'com.github.remotex.RemoteX.desktop',
  configuration: {'icon': 'com.github.remotex.RemoteX'},
  install: true,
  install_dir: get_option('prefix') / get_option('datadir') / 'applications',
)

configure_file(
  input: 'com.github.remotex.RemoteX.metainfo.xml.in',
  output: 'com.github.remotex.RemoteX.metainfo.xml',
  configuration: configuration_data(),
  install: true,
  install_dir: get_option('prefix') / get_option('datadir') / 'metainfo',
)
