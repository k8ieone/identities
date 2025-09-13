# browser.py
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
from gi.repository import GLib

from pathlib import Path

from .menu_button import IdMenuButton

@Gtk.Template(resource_path='/one/k8ie/Identities/components/main/browser.ui')
class IdBrowserPage(Adw.NavigationPage):
    __gtype_name__ = 'IdBrowserPage'

    browser_nav_view = Gtk.Template.Child()

    path = GObject.Property(type=str, default="/")
    root = GObject.Property(type=str, default="/")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# The way to do this is as follows:

# First, generate the folder/entry list for the store root
# Each directory button press will first check if the next page already exists, if it doesn't generate a page for the subridectory
# and navigate to it in either case
# We'll basically be doing these thing on the fly

# Later if it's not too complex, we could create a watch mechanism that only rebuilds the page if it detects filesystem changes, but we'll see

    def build_navigation_page(self, path="/"):
        """Creates a new password browser Adw.NavigationPage for a given directory."""
        # TODO: Create a template for this
        if path == "/":
            pp = Path(self.root)
        else:
            pp = Path(self.root) / path
        bar = Adw.HeaderBar()
        bar.pack_end(IdMenuButton())
        scrolledwindow = Gtk.ScrolledWindow(child=self.build_passwords_list_box(pp))
        toolbarview = Adw.ToolbarView(content=scrolledwindow)
        toolbarview.add_top_bar(bar)
        print("Build page: {}".format(path))
        page = Adw.NavigationPage(title=pp.stem, tag=str(pp.absolute()), child=toolbarview)
        return page

    def build_passwords_list_box(self, directory):
        """Creates a new list box populated with buttons for a given directory."""
        # TODO: Create a template for this
        box = Gtk.ListBox()
        pp = Path(self.root) / directory
        dirs = sorted([x for x in pp.iterdir() if x.is_dir() and not x.name.startswith('.')], key=str)
        pwds = sorted([x for x in pp.iterdir() if x.is_file() and not x.name.startswith('.')], key=str)
        for entry in dirs:
            # Debug - to be removed
            #print("Add button: {}".format(entry))
            #button = Adw.ButtonRow(action_name="navigation.push", action_target=GLib.Variant("s", str(entry)), title=str(entry.parts[-1]))
            button = Adw.ButtonRow(action_name="win.directory", title=str(entry.parts[-1]), end_icon_name="go-next-symbolic")
            button.set_action_target_value(GLib.Variant("s", str(entry)))
            box.append(button)
        for entry in pwds:
            # Debug - to be removed
            #print("Add button: {}".format(entry))
            button = Adw.ButtonRow(action_name="win.password", title=str(entry.stem))
            button.set_action_target_value(GLib.Variant("s", str(entry)))
            box.append(button)
        return box
