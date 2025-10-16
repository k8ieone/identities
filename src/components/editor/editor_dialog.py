# editor_dialog.py
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

@Gtk.Template(resource_path='/one/k8ie/Identities/components/editor/editor-dialog.ui')
class IdEditorDialog(Adw.Dialog):
    __gtype_name__ = 'IdEditorDialog'

    text_content = GObject.Property(type=str, default="")

    text_view = Gtk.Template.Child()

# TODO: Asterisk when changed

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text_view.get_buffer().set_text(self.text_content)
        self.text_view.get_buffer().set_modified(False)
        self.text_view.get_buffer().connect("modified-changed", self.modified)

    @Gtk.Template.Callback()
    def discard(self, widget):
        self.set_can_close(True)
        self.close()

    @Gtk.Template.Callback()
    def save(self, widget):
        # TODO: Saving logic
        self.close()

    def modified(self, *args):
        print("okay, i'm taking away your closing rights!")
        self.set_can_close(False)
