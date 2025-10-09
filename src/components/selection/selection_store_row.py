# selection_store_row.py
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

from .window import IdentitiesWindow

@Gtk.Template(resource_path='/one/k8ie/Identities/components/selection/selection-store-row.ui')
class SelectionStoreRow(Adw.ActionRow):
    __gtype_name__ = 'SelectionStoreRow'

    def __init__(self, title, subtitle, removal_callback, **kwargs):
        super().__init__(**kwargs)
        self.set_title(title)
        self.set_subtitle(subtitle)
        self.removal_callback = removal_callback

    @Gtk.Template.Callback()
    def on_store_selected(self, widget):
        store_path = widget.get_subtitle()
        IdentitiesWindow(store_path, application=self.get_root().get_application()).present()
        self.get_root().close()
