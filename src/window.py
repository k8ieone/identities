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
import time

@Gtk.Template(resource_path='/one/k8ie/Identities/window.ui')
class IdentitiesWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'IdentitiesWindow'

    clipboard = Gdk.Display.get_default().get_clipboard()

    toolbarview = Gtk.Template.Child()
    splitview = Gtk.Template.Child()
    password_page = Gtk.Template.Child()
    password_group = Gtk.Template.Child()
    nav_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = Gio.Settings.new("one.k8ie.Identities")
        self.builder = Gtk.Builder()
        self.password_store_dir = Path.home() / Path(".password-store")
        self.cur_dir = Path(".")
        print(self.settings.get_strv("stores"))
        if len(self.settings.get_strv("stores")) > 0:
            print("Skipping welcome page...")
            self.toolbarview.set_content(self.splitview)
        self.bind_actions()
        self.store = passpy.store.Store(gpg_bin="gpg")
        page = self.build_navigation_page(self.cur_dir)
        self.nav_view.add(page)
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
        self.nav_view.push_by_tag(_.unpack())
        self.cur_dir = Path(_.unpack())
        self.generate_passwords_list()

    def on_password_action(self, widget, _):
        """Callback for the win.password action."""
        for child in self.password_group_children:
            self.password_group.remove(child)
        self.password_group_children = []
        pwd_path = Path(_.unpack())
        rel_path = pwd_path.relative_to(self.password_store_dir)
        print("Showing password {}".format(str(rel_path)))
        content = self.store.get_key(str(rel_path).removesuffix(".gpg"))
        self.password_group.set_title(rel_path.stem)
        self.password_group.set_description(str(rel_path))
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

    def on_copy_action(self, widget, _):
        """Callback for the win.password action."""
        print("Copying to clipboard")
        self.clipboard.set(_.unpack())

    def build_list_box(self, directory):
        """Creates a new list box populated with buttons for a given directory."""
        box = Gtk.ListBox()
        pp = self.password_store_dir / directory
        dirs = sorted([x for x in pp.iterdir() if x.is_dir() and not x.name.startswith('.')], key=str)
        pwds = sorted([x for x in pp.iterdir() if x.is_file() and not x.name.startswith('.')], key=str)
        for entry in dirs:
            #print("Add button: {}".format(entry))
            #button = Adw.ButtonRow(action_name="navigation.push", action_target=GLib.Variant("s", str(entry)), title=str(entry.parts[-1]))
            button = Adw.ButtonRow(action_name="win.directory", title=str(entry.parts[-1]), end_icon_name="go-next-symbolic")
            button.set_action_target_value(GLib.Variant("s", str(entry)))
            box.append(button)
        for entry in pwds:
            #print("Add button: {}".format(entry))
            button = Adw.ButtonRow(action_name="win.password", title=str(entry.stem))
            button.set_action_target_value(GLib.Variant("s", str(entry)))
            box.append(button)
        return box

    def build_navigation_page(self, directory):
        """Creates a new Adw.NavigationPage for the password browser for a given directory."""
        pp = self.password_store_dir / directory
        bar = Adw.HeaderBar()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        #print("Build page: {}".format(directory))
        page = Adw.NavigationPage(tag=str(pp.absolute()), child=box)
        box.append(bar)
        box.append(self.build_list_box(directory))
        return page

    def generate_passwords_list(self):
        """Ran every time the working directory changes, iterates through all directories and builds their pages."""
        dir_list = self.store.list_dir(self.cur_dir)
        dirs = dir_list[0]
        pwds = dir_list[1]
        for entry in dirs:
            p = Path(entry)
            pp = self.password_store_dir / p
            if self.nav_view.find_page(str(pp.absolute())) is None:
                page = self.build_navigation_page(p)
                self.nav_view.add(page)

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
            }
        }
        for action in actions:
            act = Gio.SimpleAction.new(action, actions[action]["ret"])
            print("Connecting {} to {}".format(action, actions[action]["method"]))
            act.connect("activate", actions[action]["method"])
            self.add_action(act)
