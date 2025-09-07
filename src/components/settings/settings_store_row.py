# settings_store_row.py
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

@Gtk.Template(resource_path='/one/k8ie/Identities/components/settings/settings-store-row.ui')
class SettingsStoreRow(Adw.ActionRow):
    __gtype_name__ = 'SettingsStoreRow'

    def __init__(self, title, subtitle, removal_callback, **kwargs):
        super().__init__(**kwargs)
        self.set_title(title)
        self.set_subtitle(subtitle)
        self.removal_callback = removal_callback

    @Gtk.Template.Callback()
    def on_settings_row_removal(self, widget):
        settings = self.get_root().get_application().settings
        # Gets the parent action row
        row = widget.get_parent().get_parent().get_parent()
        removed_store = row.get_subtitle()
        stores = settings.get_strv("stores")
        for index, store in enumerate(stores):
            if store == removed_store:
                del stores[index]
                settings.set_strv("stores", stores)
                break
        self.removal_callback()
