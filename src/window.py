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

import pyotp
import datetime
import math
import time

@Gtk.Template(resource_path='/one/k8ie/Identities/window.ui')
class IdentitiesWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'IdentitiesWindow'

    clipboard = Gdk.Display.get_default().get_clipboard()

    splitview = Gtk.Template.Child()
    #browser_nav_view = Gtk.Template.Child()
    viewer_nav_view = Gtk.Template.Child()
    brkpoint = Gtk.Template.Child()

    def __init__(self, store_path, **kwargs):
        super().__init__(**kwargs)
        self.settings = self.get_application().settings
        self.bind_actions()
        self.otp_rows = {}
        self.browser = IdBrowser(root=store_path)
        self.store_selection_done(store_path)

    def on_open_settings(self, widget, nothing=_):
        SettingsDialog().show(parent=self)

    def store_selection_done(self, store):
        self.cur_dir = Path(store)
        self.cur_viewer_page = None
        self.password_store_dir = Path(store)
        self.store = Store(store_dir=self.password_store_dir)
        self.splitview.set_sidebar(self.browser)
        self.brkpoint.connect("apply", self.on_collapse)
        self.brkpoint.connect("unapply", self.on_uncollapse)

    def on_directory_action(self, widget, _):
        """Callback for the win.directory action."""
        self.browser.change_dir(_.unpack())

    def on_password_action(self, widget, _):
        """Callback for the win.password action."""
        pwd_path = Path(_.unpack())
        # Debug - to be removed
        print("Showing password {}".format(str(pwd_path)))
        self.cur_viewer_page = self.build_viewer_page(pwd_path)
        if self.splitview.get_collapsed():
            self.browser.browser_nav_view.push(self.cur_viewer_page)
        else:
            self.viewer_nav_view.push(self.cur_viewer_page)

    def on_collapse(self, widget):
        """Called when the split-navigation view is collapsed"""
        if self.cur_viewer_page is not None:
            self.viewer_nav_view.pop()
            self.browser.browser_nav_view.push(self.cur_viewer_page)
        # Debug - to be removed
        print("Collapsed")

    def on_uncollapse(self, widget):
        """Called when the split-navigation view is uncollapsed"""
        if self.cur_viewer_page is not None:
            self.browser.browser_nav_view.pop()
            self.viewer_nav_view.push(self.cur_viewer_page)
        # Debug - to be removed
        print("Uncollapsed")

    def on_copy_action(self, widget, _):
        """Callback for the win.copy action."""
        self.toast_overlay.add_toast(Adw.Toast(title="Entry copied to clipboard!", timeout=2))
        self.clipboard.set(_.unpack())

    def map_value(self, value, from_min, from_max, to_min, to_max):
        """Helper function - remaps a value from one range to another"""
        return to_min + (value - from_min) * (to_max - to_min) / (from_max - from_min)

    def monitor_otp(self, row):
        """Called by _task_internal_method. For some reason everything breaks if the UI is updated from here."""
        time.sleep(1)

    def otp_generated(self, window, task, whatevs):
        """Callback - function called after monitor_otp finishes running"""
        if not task.get_cancellable().is_cancelled():
            task_data = task.get_task_data()
            row = self.otp_rows[task_data]
            expires_in = row.otp.interval - datetime.datetime.now().timestamp() % row.otp.interval
            remapped = self.map_value(expires_in, 0, row.otp.interval, 0.0, 1.0)
            animating_to = self.map_value(expires_in - 1, 0, row.otp.interval, 0.0, 1.0)
            if animating_to < 0:
                animating_to = 0
            animating_from = self.map_value(expires_in, 0, row.otp.interval, 0.0, 1.0)
            row.progressbar_animation.set_value_to(animating_to)
            row.progressbar_animation.set_value_from(animating_from)
            row.progressbar_animation.play()
            row.set_text(row.otp.now())
            new_task = self.create_new_task(self.otp_generated, row, id(row))
            row.otp_task = new_task

    def create_new_task(self, callback, row, row_id):
        """Called whenever creating a new task. Starts _task_internal_method in a thread"""
        task = Gio.Task.new(self, Gio.Cancellable(), callback, None)
        task.set_return_on_cancel(False)
        task.run_in_thread(self._task_internal_method)
        task.set_task_data(row_id)
        return task

    def _task_internal_method (self, task, source_object, task_data, cancellable):
        """Called by create_new_task in a thread"""

        if task.return_error_if_cancelled():
            task.return_value(None)
        # Value of argument 'task_data' is always None for some reason.
        # So, we need to get task_data using task.get_task_data() method.
        task_data = task.get_task_data()

        # Task data is just an id of the actual data. So, we need to get
        # the actual data from our instance-wide dictionary
        row = self.otp_rows[task_data]
        outcome = self.monitor_otp(row)

        task.return_value(outcome)

    def password_page_shown(self, page):
        otp_widgets = page.otp_rows
        for widget in otp_widgets:
            if widget.otp_task.get_cancellable().is_cancelled():
                # Debug - to be removed
                print("STARTING NEW TASK")
                self.otp_rows[id(widget)] = widget
                widget.otp_task = self.create_new_task(self.otp_generated, widget, id(widget))

    def password_page_hidden(self, page):
        otp_widgets = page.otp_rows
        for widget in otp_widgets:
            # Debug - to be removed
            print("CANCELLING TASK")
            widget.otp_task.get_cancellable().cancel()
            del self.otp_rows[id(widget)]

    def build_password_group(self, pwd_path):
        rel_path = pwd_path.relative_to(self.password_store_dir)
        content = self.store.get_key(pwd_path)
        password_group = Adw.PreferencesGroup(separate_rows=False)
        password_group.set_title(rel_path.stem)
        password_group.set_description(str(rel_path))
        otp_rows = []
        for index, line in enumerate(content.splitlines()):
            row = Adw.PasswordEntryRow()
            text = line
            title = None
            otp = False
            if text.startswith("otpauth://totp"):
                title = "OTP"
                otp = True
                bar = Gtk.ProgressBar(inverted=False)
                row.otp = pyotp.parse_uri(text)
                fraction_target = Adw.PropertyAnimationTarget.new(bar, "fraction")
                expires_in = row.otp.interval - datetime.datetime.now().timestamp() % row.otp.interval
                progressbar_animation = Adw.TimedAnimation.new(bar, 0, 1, 1 * 1000, fraction_target)
                progressbar_animation.set_easing(0)
                bar.set_fraction(self.map_value(expires_in, 0, row.otp.interval, 0.0, 1.0))
                text = row.otp.now()
                otp_rows.append(row)
                self.otp_rows[id(row)] = row
                row.otp_task = self.create_new_task(self.otp_generated, row, id(row))
                row.bar = bar
                row.fraction_target = fraction_target
                row.progressbar_animation = progressbar_animation
            elif index == 0:
                title = "password"
            elif ": " in line:
                title = line.split(": ")[0]
                text = line.removeprefix(title + ": ")
            row.set_editable(False)
            row.set_text(text)
            if title is not None:
                row.set_title(title)
            # Workaround to hide the edit button
            box = row.get_first_child()
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
            copy_button = Gtk.Button(icon_name="edit-copy-symbolic", has_frame=False, valign=Gtk.Align(3), action_name="win.copy")
            copy_button.set_action_target_value(GLib.Variant("s", text))
            row.add_suffix(copy_button)
            if otp:
                another_box = Gtk.Box(orientation=Gtk.Orientation(1))
                another_box.append(row)
                another_box.append(bar)
                another_row = Adw.ActionRow(child=another_box)
                password_group.add(another_row)
            else:
                password_group.add(row)
        return (password_group, otp_rows)

    def build_viewer_page(self, path):
        """Creates a new password viewer Adw.NavigationPage for a given entry."""
        pp = self.password_store_dir / path
        bar = Adw.HeaderBar()
        button = Gtk.Button(css_classes=["suggested-action", "pill"], label="Edit", action_name="win.edit")
        box = Gtk.Box(orientation=Gtk.Orientation(1), spacing=20)
        group_tuple = (self.build_password_group(pp))
        box.append(group_tuple[0])
        box.append(button)
        clamp = Adw.Clamp(maximum_size=450, child=box)
        status = Adw.StatusPage(child=clamp)
        self.toast_overlay = Adw.ToastOverlay(child=status)
        toolbarview = Adw.ToolbarView(content=self.toast_overlay)
        toolbarview.add_top_bar(bar)
        # Debug - to be removed
        #print("Build page: {}".format(path))
        page = Adw.NavigationPage(title=path.stem, child=toolbarview)
        page.connect("hidden", self.password_page_hidden)
        page.connect("shown", self.password_page_shown)
        page.otp_rows = group_tuple[-1]
        return page

    def bind_actions(self):
        actions = {
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
            # Debug - to be removed
            #print("Connecting {} to {}".format(action, actions[action]["method"]))
            act.connect("activate", actions[action]["method"])
            self.add_action(act)
