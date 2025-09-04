# setup_wizard.py
#
# Copyright 2025 Kate
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw
from gi.repository import Gtk

from .settings import SettingsDialog
from .store_selection import StoreSelectionWindow

@Gtk.Template(resource_path='/one/k8ie/Identities/setup_wizard.ui')
class OnboardingWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'OnboardingWindow'

    setup_wizard = Gtk.Template.Child()
    store_setup = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = self.get_application().settings

    @Gtk.Template.Callback()
    def on_wizard_started(self, widget):
        """Callback for the win.start action."""
        self.setup_wizard.push(self.store_setup)

    @Gtk.Template.Callback()
    def on_settings_open(self, widget):
        #self.build_stores(self.stores_editor_clamp, True)
        SettingsDialog().show(self)
        #self.options_dialog.present(parent=self)

    @Gtk.Template.Callback()
    def on_wizard_done(self, widget):
        if len(self.settings.get_strv("stores")) > 0:
            StoreSelectionWindow(application=self.get_application()).present()
            self.close()
        else:
            dialog = Adw.AlertDialog(heading="No stores configured", body="You must first configure at least one password store in the settings.")
            dialog.add_response(id="ok", label="Okay, I'll add one")
            dialog.present(parent=self)
