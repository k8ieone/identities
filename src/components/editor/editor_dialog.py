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

from . import passutils

from pathlib import Path

@Gtk.Template(resource_path='/one/k8ie/Identities/components/editor/editor-dialog.ui')
class IdEditorDialog(Adw.Dialog):
    __gtype_name__ = 'IdEditorDialog'

    text_content = GObject.Property(type=str, default="")
    file = GObject.Property(type=str)
    root = GObject.Property(type=str)

    text_view = Gtk.Template.Child()

# TODO: Asterisk when changed

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        p = Path(self.file)
        self.set_title("Editing " + p.name)
        self.text_view.get_buffer().set_text(self.text_content)
        self.text_view.get_buffer().set_modified(False)
        self.text_view.get_buffer().connect("modified-changed", self.modified)
        self.setup_shortcut()

    def setup_shortcut(self):
        # First create a new action in the dialog
        self.install_action("editor.save", None, self.save_signal)
        editor_controller = Gtk.ShortcutController()
        dialog_controller = Gtk.ShortcutController()
        # Add controller to both the dialog and the editor
        self.add_controller(dialog_controller)
        self.text_view.add_controller(editor_controller)
        # Create new shortcut
        shortcut = Gtk.Shortcut(trigger=Gtk.ShortcutTrigger.parse_string("<Control>Return"), action=Gtk.ShortcutAction.parse_string("action(editor.save)"))
        # Add the shortcut to both controllers
        editor_controller.add_shortcut(shortcut)
        dialog_controller.add_shortcut(shortcut)

    def save_signal(self, *args):
        self.save(self)

    def close_override(self):
        self.set_can_close(True)
        self.close()

    @Gtk.Template.Callback()
    def discard(self, widget):
        self.close_override()

    @Gtk.Template.Callback()
    def save(self, widget):
        buffer = self.text_view.get_buffer()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        result = passutils.encrypt(Path(self.file), Path(self.root), buffer.get_text(start, end))
        if result is not None:
            result += "\n\nYour changes were not saved"
            d = Adw.AlertDialog(heading="Encryption error", body=result)
            d.add_response("ok", "Oh, damn")
            d.present(parent=self)
        self.close_override()

    def modified(self, *args):
        # TODO: Also notice when the text hasn't changed
        if self.text_view.get_buffer().get_modified():
            print("okay, i'm taking away your closing rights!")
            self.set_can_close(False)
        else:
            print("You're good, no changes detected...")
            self.set_can_close(True)
