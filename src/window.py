# window.py
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

    splitview = Gtk.Template.Child()
    browser_nav_view = Gtk.Template.Child()
    viewer_nav_view = Gtk.Template.Child()
    brkpoint = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings = Gio.Settings.new("one.k8ie.Identities")
        self.builder = Gtk.Builder()
        self.password_store_dir = Path.home() / Path(".password-store")
        self.cur_dir = Path(".")
        self.cur_viewer_page = None
        print(self.settings.get_strv("stores"))
        if len(self.settings.get_strv("stores")) > 0:
            print("Skipping welcome page...")
            self.set_content(self.splitview)
            self.brkpoint.connect("apply", self.on_collapse)
            self.brkpoint.connect("unapply", self.on_uncollapse)
        self.bind_actions()
        self.store = passpy.store.Store(gpg_bin="gpg")
        page = self.build_navigation_page(self.cur_dir)
        self.browser_nav_view.add(page)
        self.generate_passwords_list()
        self.password_group_children = []

    def on_start_action(self, widget, _):
        """Callback for the win.start action."""
        if (Path.home() / ".password-store").is_dir():
            print("Default password store detected")
            self.settings.set_strv("stores", ["~/.password-store"])
            self.set_content(self.splitview)

    def on_directory_action(self, widget, _):
        """Callback for the win.directory action."""
        print("Entering directory {}".format("{}".format(_.unpack())))
        self.browser_nav_view.push_by_tag(_.unpack())
        self.cur_dir = Path(_.unpack())
        self.generate_passwords_list()

    def on_password_action(self, widget, _):
        """Callback for the win.password action."""
        pwd_path = Path(_.unpack())
        print("Showing password {}".format(str(pwd_path)))
        #self.tst.set_child(self.build_password_group(pwd_path))
        self.cur_viewer_page = self.build_viewer_page(pwd_path)
        if self.splitview.get_collapsed():
            self.browser_nav_view.push(self.cur_viewer_page)
        else:
            self.viewer_nav_view.push(self.cur_viewer_page)
        #self.splitview.push(self.password_page)
        #self.splitview.set_content(self.password_page)

    def on_collapse(self, widget):
        if self.cur_viewer_page is not None:
            self.viewer_nav_view.pop()
            self.browser_nav_view.push(self.cur_viewer_page)
        print("Collapsed")

    def on_uncollapse(self, widget):
        if self.cur_viewer_page is not None:
            self.browser_nav_view.pop()
            self.viewer_nav_view.push(self.cur_viewer_page)
        print("Uncollapsed")

    def on_copy_action(self, widget, _):
        """Callback for the win.password action."""
        print("Copying to clipboard")
        self.toast_overlay.add_toast(Adw.Toast(title="Entry copied to clipboard!"))
        self.clipboard.set(_.unpack())

    def build_password_group(self, pwd_path):
        rel_path = pwd_path.relative_to(self.password_store_dir)
        content = self.store.get_key(str(rel_path).removesuffix(".gpg"))
        password_group = Adw.PreferencesGroup()
        password_group.set_title(rel_path.stem)
        password_group.set_description(str(rel_path))
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
            password_group.add(row)
        return password_group

    def build_viewer_page(self, path):
        """Creates a new password viewer Adw.NavigationPage for a given entry."""
        pp = self.password_store_dir / path
        bar = Adw.HeaderBar()
        button = Gtk.Button(css_classes=["suggested-action", "pill"], label="Edit", action_name="win.edit")
        box = Gtk.Box(orientation=Gtk.Orientation(1), spacing=20)
        box.append(self.build_password_group(pp))
        box.append(button)
        clamp = Adw.Clamp(maximum_size=450, child=box)
        status = Adw.StatusPage(child=clamp)
        self.toast_overlay = Adw.ToastOverlay(child=status)
        toolbarview = Adw.ToolbarView(content=self.toast_overlay)
        toolbarview.add_top_bar(bar)
        #print("Build page: {}".format(path))
        page = Adw.NavigationPage(title=path.stem, child=toolbarview)
        return page

    def build_passwords_list_box(self, directory):
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

    def build_navigation_page(self, path):
        """Creates a new password browser Adw.NavigationPage for a given directory."""
        pp = self.password_store_dir / path
        bar = Adw.HeaderBar()
        scrolledwindow = Gtk.ScrolledWindow(child=self.build_passwords_list_box(pp))
        toolbarview = Adw.ToolbarView(content=scrolledwindow)
        toolbarview.add_top_bar(bar)
        #print("Build page: {}".format(path))
        page = Adw.NavigationPage(title=pp.stem, tag=str(pp.absolute()), child=toolbarview)
        return page

    def generate_passwords_list(self):
        """Ran every time the working directory changes, iterates through all directories and builds their pages."""
        dir_list = self.store.list_dir(self.cur_dir)
        dirs = dir_list[0]
        pwds = dir_list[1]
        for entry in dirs:
            p = Path(entry)
            pp = self.password_store_dir / p
            if self.browser_nav_view.find_page(str(pp.absolute())) is None:
                page = self.build_navigation_page(p)
                self.browser_nav_view.add(page)

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
