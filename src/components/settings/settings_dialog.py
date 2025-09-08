# settings.py
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
from gi.repository import GLib

from pathlib import Path

from .settings_store_row import SettingsStoreRow

@Gtk.Template(resource_path='/one/k8ie/Identities/components/settings/settings-dialog.ui')
class SettingsDialog(Adw.PreferencesDialog):
    __gtype_name__ = 'SettingsDialog'

    stores_group = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.children = []

    def show(self, parent):
        self.parent = parent
        self.present(parent=parent)
        self.settings = self.get_root().get_application().settings
        self.build_stores()

    @Gtk.Template.Callback()
    def on_settings_row_add(self, widget):
        """Thanks, ChatGPT 💀"""
        def on_response(dialog, result, _):
            try:
                file = dialog.select_folder_finish(result)
                if file:
                    print("Selected file: {}".format(file.get_path()))
                else:
                    print("No file selected")
            except GLib.Error as e:
                print("Error: {}".format(e.message))
            else:
                stores = self.settings.get_strv("stores")
                stores.append(file.get_path())
                self.settings.set_strv("stores", stores)
                self.build_stores()
        dialog = Gtk.FileDialog()
        dialog.set_title("Select your password store directory")
        dialog.select_folder(self.parent, None, on_response, None)

    def build_stores(self):
        """Builds the rows with stores"""
        for child in self.children:
            self.stores_group.remove(child)
        self.children = []
        for store in self.settings.get_strv("stores"):
            row = SettingsStoreRow(Path(store).stem, store, self.build_stores)
            self.children.append(row)
            self.stores_group.add(row)
