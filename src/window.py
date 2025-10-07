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

from .passutils import Store
from .settings_dialog import SettingsDialog
from .menu_button import IdMenuButton
from .browser import IdBrowser
from .viewer import IdViewer

@Gtk.Template(resource_path='/one/k8ie/Identities/window.ui')
class IdentitiesWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'IdentitiesWindow'

    clipboard = Gdk.Display.get_default().get_clipboard()

    splitview = Gtk.Template.Child()

    def __init__(self, store_path, **kwargs):
        super().__init__(**kwargs)
        self.settings = self.get_application().settings
        self.bind_actions()
        self.browser = IdBrowser(root=store_path)
        self.viewer = IdViewer(root=store_path)
        self.store_selection_done(store_path)

    def on_open_settings(self, widget, nothing=_):
        SettingsDialog().show(parent=self)

    def store_selection_done(self, store):
        self.cur_dir = Path(store)
        self.cur_viewer_page = None
        self.password_store_dir = Path(store)
        self.store = Store(store_dir=self.password_store_dir)
        self.splitview.set_sidebar(self.browser)
        self.splitview.set_content(self.viewer)

    def on_directory_action(self, widget, _):
        """Callback for the win.directory action."""
        self.browser.change_dir(_.unpack())

    def on_password_action(self, widget, _):
        """Callback for the win.password action."""
        # TODO: Check for existence (file could have been removed)
        self.viewer.show_pass(_.unpack())

    @Gtk.Template.Callback()
    def on_collapse(self, widget):
        """Called when the split-navigation view is collapsed"""
        if self.cur_viewer_page is not None:
            self.viewer_nav_view.pop()
            self.browser.browser_nav_view.push(self.cur_viewer_page)
        # Debug - to be removed
        print("Collapsed")

    @Gtk.Template.Callback()
    def on_uncollapse(self, widget):
        """Called when the split-navigation view is uncollapsed"""
        if self.cur_viewer_page is not None:
            self.browser.browser_nav_view.pop()
            self.viewer_nav_view.push(self.cur_viewer_page)
        # Debug - to be removed
        print("Uncollapsed")

    def bind_actions(self):
        actions = {
            "directory": {
                "method": self.on_directory_action,
                "ret": GLib.VariantType.new("s")
            },
            "password": {
                "method": self.on_password_action,
                "ret": GLib.VariantType.new("s")
            }
        }
        for action in actions:
            act = Gio.SimpleAction.new(action, actions[action]["ret"])
            # Debug - to be removed
            #print("Connecting {} to {}".format(action, actions[action]["method"]))
            act.connect("activate", actions[action]["method"])
            self.add_action(act)
