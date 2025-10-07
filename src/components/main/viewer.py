# viewer.py
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
from gi.repository import GObject
from gi.repository import GLib

from pathlib import Path

from .viewer_page import IdViewerPage

import pyotp
import datetime
import time

@Gtk.Template(resource_path='/one/k8ie/Identities/components/main/viewer.ui')
class IdViewer(Adw.NavigationPage):
    __gtype_name__ = 'IdViewer'

    root = GObject.Property(type=str, default="/")

    viewer_nav_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cur_page = None
        self.otp_rows = {}

    def show_pass(self, file):
        print("Showing password {}".format(file))
        self.cur_page = IdViewerPage(title=Path(file).stem, file=file, root=self.root)
        self.viewer_nav_view.push(self.cur_page)
        # TODO: collapsing and uncollapsing
        # if self.splitview.get_collapsed():
        #     self.browser.browser_nav_view.push(self.cur_viewer_page)
        # else:
        #     self.viewer_nav_view.push(self.cur_viewer_page)
