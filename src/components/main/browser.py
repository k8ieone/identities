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

from pathlib import Path

from .browser_page import IdBrowserPage

@Gtk.Template(resource_path='/one/k8ie/Identities/components/main/browser.ui')
class IdBrowser(Adw.NavigationPage):
    __gtype_name__ = 'IdBrowser'

    browser_nav_view = Gtk.Template.Child()

    root = GObject.Property(type=str, default="/")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("Store root directory: {}".format(self.root))
        self.browser_nav_view.add(IdBrowserPage(title=Path(self.root).stem, directory=self.root))

    def change_dir(self, directory):
        print("Entering directory {}".format(directory))
        if self.browser_nav_view.find_page(directory) is None:
            print("Page doesn't exist yet")
            self.browser_nav_view.add(IdBrowserPage(title=Path(directory).stem, directory=directory, tag=directory))
        self.browser_nav_view.push_by_tag(directory)
