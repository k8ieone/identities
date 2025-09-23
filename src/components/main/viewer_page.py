# viewer_page.py
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
from gi.repository import GObject

from pathlib import Path

from . import passutils

from .viewer_page_row import IdViewerPageRow

@Gtk.Template(resource_path='/one/k8ie/Identities/components/main/viewer-page.ui')
class IdViewerPage(Adw.NavigationPage):
    __gtype_name__ = 'IdViewerPage'

    file = GObject.Property(type=str)
    # root is optional, only used to set the password group description
    root = GObject.Property(type=str)

    rows_group = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.root != "":
            rel_path = Path(self.file).relative_to(Path(self.root))
            self.rows_group.set_description(str(rel_path))
        self.rows_group.set_title(Path(self.file).stem)
        decrypted_file = passutils.decrypt(self.file)
        for row in decrypted_file.splitlines():
            self.rows_group.add(IdViewerPageRow(content=row))
