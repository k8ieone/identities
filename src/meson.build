pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'identities'
gnome = import('gnome')
blueprints = custom_target('blueprints',
  input: files(
    'window.blp',
    'shortcuts-dialog.blp',
    'components/menu-button.blp',
    'components/settings/settings-dialog.blp',
    'components/settings/settings-store-row.blp',
    'components/selection/selection-store-row.blp',
    'components/main/browser.blp',
    'components/main/browser-page.blp',
    'components/main/viewer.blp',
    'components/main/viewer-page.blp',
    'components/main/viewer-page-row.blp',
    'components/editor/editor-dialog.blp',
    'setup-wizard.blp',
    'store-selection.blp'
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
  'components/menu_button.py',
  'components/settings/settings_dialog.py',
  'components/settings/settings_store_row.py',
  'components/selection/selection_store_row.py',
  'components/main/browser.py',
  'components/main/browser_page.py',
  'components/main/viewer.py',
  'components/main/viewer_page.py',
  'components/main/viewer_page_row.py',
  'components/editor/editor_dialog.py',
  'setup_wizard.py',
  'store_selection.py'
]

install_data(identities_sources, install_dir: moduledir)
