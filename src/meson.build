pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'identities'
gnome = import('gnome')
blueprints = custom_target('blueprints',
  input: files(
    'window.blp',
    'gtk/help-overlay.blp',
    'components/menu-button.blp',
    'setup-wizard.blp',
    'store-selection.blp',
    'settings.blp'
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('identities',
  'identities.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'identities.in',
  output: 'identities',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)

identities_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'passutils.py',
  'components/menu-button.py',
  'setup-wizard.py',
  'store-selection.py',
  'settings.py'
]

install_data(identities_sources, install_dir: moduledir)
