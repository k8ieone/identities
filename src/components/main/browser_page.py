# browser_page.py
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

@Gtk.Template(resource_path='/one/k8ie/Identities/components/main/browser-page.ui')
class IdBrowserPage(Adw.NavigationPage):
    __gtype_name__ = 'IdBrowserPage'

    browser_list_box = Gtk.Template.Child()

    directory = GObject.Property(type=str, default="/")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_list_box()

    # def do_realize(self):
    #     Adw.NavigationPage.do_realize(self)

    def build_list_box(self):
        """Populates the page listbox with buttons"""
        pp = Path(self.directory)
        dirs = sorted([x for x in pp.iterdir() if x.is_dir() and not x.name.startswith('.')], key=str)
        pwds = sorted([x for x in pp.iterdir() if x.is_file() and not x.name.startswith('.')], key=str)
        for entry in dirs:
            button = Adw.ButtonRow(action_name="win.directory", title=str(entry.parts[-1]), end_icon_name="go-next-symbolic")
            button.set_action_target_value(GLib.Variant("s", str(entry)))
            self.browser_list_box.append(button)
        for entry in pwds:
            button = Adw.ButtonRow(action_name="win.password", title=str(entry.stem))
            button.set_action_target_value(GLib.Variant("s", str(entry)))
            self.browser_list_box.append(button)
