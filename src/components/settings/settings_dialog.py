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

from pathlib import Path

@Gtk.Template(resource_path='/one/k8ie/Identities/components/settings/settings-dialog.ui')
class SettingsDialog(Adw.PreferencesDialog):
    __gtype_name__ = 'SettingsDialog'

    stores_editor_clamp = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def show(self, parent):
        self.parent = parent
        self.settings = parent.settings
        self.build_stores(self.stores_editor_clamp, True)
        self.present(parent=parent)

    def on_settings_row_removal(self, widget):
        # Gets the parent action row
        row = widget.get_parent().get_parent().get_parent()
        removed_store = row.get_subtitle()
        stores = self.settings.get_strv("stores")
        for index, store in enumerate(stores):
            if store == removed_store:
                del stores[index]
                self.settings.set_strv("stores", stores)
                # More efficient option - only remove the row
                #self.edit_group.remove(row)
                break
        # Easier solution - rebuild the page
        self.build_stores(self.stores_editor_clamp, True)
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
                self.build_stores(self.stores_editor_clamp, True)

        dialog = Gtk.FileDialog()
        dialog.set_title("Select your password store directory")
        dialog.select_folder(self.parent, None, on_response, None)

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
            manage_button.connect("activated", self.on_open_settings)
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
