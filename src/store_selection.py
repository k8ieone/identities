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
from .window import IdentitiesWindow

@Gtk.Template(resource_path='/one/k8ie/Identities/store-selection.ui')
class StoreSelectionWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'StoreSelectionWindow'

    stores_selector_clamp = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = self.get_application().settings
        self.build_stores(self.stores_selector_clamp, False)

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
                self.build_stores(self.stores_selector_clamp, False)

        dialog = Gtk.FileDialog()
        dialog.set_title("Select your password store directory")
        dialog.select_folder(self.parent, None, on_response, None)

    def do_activate_settings(self, widget):
        SettingsDialog().show(self)

    def build_stores(self, parent, editable):
        """Builds stores list for the preferences and store selection"""
        box = Gtk.Box(spacing=20, orientation=Gtk.Orientation(1))
        if editable:
            add_button = Gtk.Button(css_classes=["flat"], icon_name="list-add-symbolic")
            add_button.connect("clicked", self.on_settings_row_add)
            group = Adw.PreferencesGroup(title="Stores", header_suffix=add_button)
            box.append(group)
        else:
            group = Adw.PreferencesGroup()
            box.append(group)
            buttons_group = Adw.PreferencesGroup()
            manage_button = Adw.ButtonRow(title="Manage password stores")
            manage_button.connect("activated", self.do_activate_settings)
            buttons_group.add(manage_button)
            box.append(buttons_group)
        for store in self.settings.get_strv("stores"):
            row = Adw.ActionRow(title=Path(store).stem, subtitle=store)
            if editable:
                remove_button = Gtk.Button(icon_name="list-remove-symbolic", css_classes=["flat"], halign=Gtk.Align(3), valign=Gtk.Align(3))
                remove_button.connect("clicked", self.on_settings_row_removal)
                row.add_suffix(remove_button)
                row.set_activatable(False)
            else:
                row.add_suffix(Gtk.Image(icon_name="go-next-symbolic"))
                row.set_activatable(True)
                row.connect("activated", self.on_store_selected)
            group.add(row)
        parent.set_child(box)

    def on_store_selected(self, widget):
        store_path = widget.get_subtitle()
        IdentitiesWindow(store_path, application=self.get_application()).present()
        self.close()
