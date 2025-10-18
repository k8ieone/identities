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
from .editor_dialog import IdEditorDialog

@Gtk.Template(resource_path='/one/k8ie/Identities/components/main/viewer-page.ui')
class IdViewerPage(Adw.NavigationPage):
    __gtype_name__ = 'IdViewerPage'

    file = GObject.Property(type=str)
    root = GObject.Property(type=str)

    rows_group = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rows = []
        if self.root != "":
            rel_path = Path(self.file).relative_to(Path(self.root))
            self.rows_group.set_description(str(rel_path))
        self.rows_group.set_title(Path(self.file).stem)
        self.decrypted_text = passutils.decrypt(self.file)
        self.create_children()

    def delete_children(self):
        for widget in self.rows:
            self.rows_group.remove(widget)
        self.rows = []

    def create_children(self):
        for index, row in enumerate(self.decrypted_text.splitlines()):
            row_widget = IdViewerPageRow(content=row, index=index, toast_overlay=self.toast_overlay)
            self.rows_group.add(row_widget)
            self.rows.append(row_widget)

    def refresh(self, *args):
        self.decrypted_text = passutils.decrypt(self.file)
        self.delete_children()
        self.create_children()

    @Gtk.Template.Callback()
    def on_page_hiden(self, page):
        for widget in self.rows:
            widget.cancel_task()

    @Gtk.Template.Callback()
    def edit_password(self, widget):
        d = IdEditorDialog(text_content=self.decrypted_text, file=self.file, root=self.root)
        d.connect("closed", self.refresh)
        d.present(parent=self.get_root())

    # TODO: Add shortcut to edit a password
