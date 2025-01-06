# window.py
#
# Copyright 2024 Kate
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
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Gdk

from pathlib import Path
import passpy

@Gtk.Template(resource_path='/one/k8ie/Identities/window.ui')
class IdentitiesWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'IdentitiesWindow'

    clipboard = Gdk.Display.get_default().get_clipboard()
    toolbarview = Gtk.Template.Child()
    splitview = Gtk.Template.Child()
    password_list_view = Gtk.Template.Child()
    password_page = Gtk.Template.Child()
    password_group = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = Gio.Settings.new("one.k8ie.Identities")
        self.builder = Gtk.Builder()
        self.cur_dir = Path(".")
        print(self.settings.get_strv("stores"))
        if len(self.settings.get_strv("stores")) > 0:
            print("Skipping welcome page...")
            self.toolbarview.set_content(self.splitview)
        self.bind_actions()
        self.store = passpy.store.Store(gpg_bin="gpg")
        self.generate_passwords_list()
        self.password_group_children = []

    def on_start_action(self, widget, _):
        """Callback for the win.start action."""
        if (Path.home() / ".password-store").is_dir():
            print("Default password store detected")
            self.settings.set_strv("stores", ["~/.password-store"])
            self.toolbarview.set_content(self.splitview)

    def on_directory_action(self, widget, _):
        """Callback for the win.directory action."""
        print("Entering directory {}".format("{}".format(_.unpack())))
        self.cur_dir = Path(_.unpack())
        self.generate_passwords_list()

    def on_password_action(self, widget, _):
        """Callback for the win.password action."""
        for child in self.password_group_children:
            self.password_group.remove(child)
        pwd_path = Path(_.unpack())
        print("Showing password {}".format(pwd_path))
        content = self.store.get_key(pwd_path)
        self.password_group.set_title(str(pwd_path.parts[-1]))
        self.password_group.set_description(str(pwd_path))
        for index, line in enumerate(content.splitlines()):
            row = Adw.ActionRow()
            title = line
            subtitle = None
            if index == 0:
                subtitle = "Password"
            elif ": " in line:
                subtitle = line.split(": ")[0]
                title = line.removeprefix(subtitle + ": ")
            row.set_title(title)
            if subtitle is not None:
                row.set_subtitle(subtitle)
            copy_button = Gtk.Button(icon_name="edit-copy-symbolic", has_frame=False, valign=Gtk.Align(3), action_name="win.copy")
            copy_button.set_action_target_value(GLib.Variant("s", title))
            row.add_suffix(copy_button)
            self.password_group_children.append(row)
            self.password_group.add(row)
        self.splitview.set_content(self.password_page)

    def on_back_action(self, widget, _):
        """Callback for the win.password action."""
        print("Back to directory {}".format("{}".format(self.cur_dir.parent)))
        self.cur_dir = self.cur_dir.parent
        self.generate_passwords_list()

    def on_copy_action(self, widget, _):
        """Callback for the win.password action."""
        print("Copying to clipboard")
        self.clipboard.set(_.unpack())

    def generate_passwords_list(self):
        dir_list = self.store.list_dir(self.cur_dir)
        dirs = dir_list[0]
        pwds = dir_list[1]
        self.password_list_view.remove_all()
        for entry in dirs:
            p = Path(entry)
            button = Adw.ButtonRow(title=str(p.parts[-1]), action_name="win.directory", end_icon_name="go-next-symbolic")
            button.set_action_target_value(GLib.Variant("s", entry))
            self.password_list_view.append(button)
        for entry in pwds:
            p = Path(entry)
            button = Adw.ButtonRow(title=str(p.parts[-1]), action_name="win.password")
            button.set_action_target_value(GLib.Variant("s", entry))
            self.password_list_view.append(button)

    def bind_actions(self):
        actions = {
            "start": {
                "method": self.on_start_action,
                "ret": None
            },
            "directory": {
                "method": self.on_directory_action,
                "ret": GLib.VariantType.new("s")
            },
            "password": {
                "method": self.on_password_action,
                "ret": GLib.VariantType.new("s")
            },
            "copy": {
                "method": self.on_copy_action,
                "ret": GLib.VariantType.new("s")
            },
            "back": {
                "method": self.on_back_action,
                "ret": None
            }
        }
        for action in actions:
            act = Gio.SimpleAction.new(action, actions[action]["ret"])
            print("Connecting {} to {}".format(action, actions[action]["method"]))
            act.connect("activate", actions[action]["method"])
            self.add_action(act)
