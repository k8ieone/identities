# viewer_page_row.py
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
from gi.repository import Gio, Gdk

from pathlib import Path

import pyotp
import datetime
import time

@Gtk.Template(resource_path='/one/k8ie/Identities/components/main/viewer-page-row.ui')
class IdViewerPageRow(Adw.ActionRow):
    __gtype_name__ = 'IdViewerPageRow'

    content = GObject.Property(type=str)
    index = GObject.Property(type=int)
    toast_overlay = GObject.Property(type=Adw.ToastOverlay)

    row = Gtk.Template.Child()
    otp_bar = Gtk.Template.Child()

    clipboard = Gdk.Display.get_default().get_clipboard()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.obliterate_edit_button()
        if self.index == 0:
            self.row.set_title("password")
            self.row.set_text(self.content)
        elif self.content.startswith("otpauth://totp"):
            self.row.set_title("OTP")
            self.otp_bar.set_visible(True)
            self.otp = pyotp.parse_uri(self.content)
            self.otp_init()
            self.otp_task = self.create_otp_task()
        elif ": " in self.content:
            title = self.content.split(": ")[0]
            self.row.set_title(title)
            self.row.set_text(self.content.removeprefix(title + ": "))

    @Gtk.Template.Callback()
    def on_copy(self, widget):
        self.clipboard.set(self.row.get_text())
        self.toast_overlay.add_toast(Adw.Toast(title="Entry copied to clipboard!", timeout=2))

    def map_value(self, value, from_min, from_max, to_min, to_max):
        """Helper function - remaps a value from one range to a different range"""
        return to_min + (value - from_min) * (to_max - to_min) / (from_max - from_min)

    def otp_init(self):
        """Prepares the various animation objects and sets the bar
        to the right position before starting the OTP task"""
        bar = self.otp_bar
        fraction_target = Adw.PropertyAnimationTarget.new(bar, "fraction")
        progressbar_animation = Adw.TimedAnimation.new(bar, 0, 1, 1 * 1000, fraction_target)
        progressbar_animation.set_easing(0)
        expires_in = self.otp.interval - datetime.datetime.now().timestamp() % self.otp.interval
        #bar.set_fraction(self.map_value(expires_in, 0, self.otp.interval, 0.0, 1.0))
        self.otp_bar.fraction_target = fraction_target
        self.otp_bar.progressbar_animation = progressbar_animation
        self.update_otp()

    def create_otp_task(self):
        """Called whenever creating a new task. Starts _task_internal_method in a thread"""
        task = Gio.Task.new(self, Gio.Cancellable(), self.cancel_checker, None)
        task.set_return_on_cancel(False)
        task.run_in_thread(self._task_internal_method)
        return task

    def cancel_checker(self, window, task, _):
        """Callback - function called after _task_internal_method finishes running"""
        self.update_otp()
        if not task.get_cancellable().is_cancelled():
            new_task = self.create_otp_task()
            self.otp_task = new_task

    def update_otp(self):
        expires_in = self.otp.interval - datetime.datetime.now().timestamp() % self.otp.interval
        remapped = self.map_value(expires_in, 0, self.otp.interval, 0.0, 1.0)
        animating_to = self.map_value(expires_in - 1, 0, self.otp.interval, 0.0, 1.0)
        if animating_to < 0:
            animating_to = 0
        animating_from = self.map_value(expires_in, 0, self.otp.interval, 0.0, 1.0)
        self.otp_bar.progressbar_animation.set_value_to(animating_to)
        self.otp_bar.progressbar_animation.set_value_from(animating_from)
        self.otp_bar.progressbar_animation.play()
        self.row.set_text(self.otp.now())

    def _task_internal_method (self, task, source_object, task_data, cancellable):
        """Called by create_new_task in a thread"""
        time.sleep(1)
        task.return_value(None)

    def cancel_task(self):
        """Called by IdViewerPage when hiding the viewer page"""
        self.otp_task.get_cancellable().cancel()

    def obliterate_edit_button(self):
        """Hack to hide the edit button"""
        box = self.row.get_first_child()
        if box and isinstance(box, Gtk.Box):
            # Traverse all children of box to find the target widget
            child = box.get_first_child()
            while child:
                # Check if the child contains the expected structure
                # Look for a widget that contains a Gtk.Image as its last child
                if isinstance(child, Gtk.Widget):
                    last_child = child.get_last_child()
                    if last_child and isinstance(last_child, Gtk.Image):
                        # Hide the Gtk.Image (edit button)
                        last_child.set_visible(False)
                        break
                child = child.get_next_sibling()
