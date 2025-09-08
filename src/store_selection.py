# store_selection.py
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

from pathlib import Path

from .settings_dialog import SettingsDialog
from .selection_store_row import SelectionStoreRow

@Gtk.Template(resource_path='/one/k8ie/Identities/store-selection.ui')
class StoreSelectionWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'StoreSelectionWindow'

    stores_group = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.children = []
        self.settings = self.get_application().settings
        self.build_stores()

    @Gtk.Template.Callback()
    def do_activate_settings(self, widget):
        d = SettingsDialog()
        d.connect("closed", self.build_stores)
        d.show(self)

    def build_stores(self, *args):
        """Builds the rows with stores"""
        for child in self.children:
            self.stores_group.remove(child)
        self.children = []
        for store in self.settings.get_strv("stores"):
            row = SelectionStoreRow(Path(store).stem, store, self.build_stores)
            self.children.append(row)
            self.stores_group.add(row)
