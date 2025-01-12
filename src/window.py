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
import pyotp
import datetime
import math
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
            #self.viewer_nav_view.connect("popped", self.page_hidden)
        self.bind_actions()
        self.store = passpy.store.Store(gpg_bin="gpg")
        page = self.build_navigation_page(self.cur_dir)
        self.browser_nav_view.add(page)
        self.generate_passwords_list()
        self.otp_rows = {}

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
        self.toast_overlay.add_toast(Adw.Toast(title="Entry copied to clipboard!", timeout=2))
        self.clipboard.set(_.unpack())

    def map_value(self, value, from_min, from_max, to_min, to_max):
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
            row.bar.set_fraction(remapped)
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
            print("Cancelling task")
            widget.otp_task.get_cancellable().cancel()
            del self.otp_rows[id(widget)]

    def build_password_group(self, pwd_path):
        rel_path = pwd_path.relative_to(self.password_store_dir)
        content = self.store.get_key(str(rel_path).removesuffix(".gpg"))
        password_group = Adw.PreferencesGroup(separate_rows=False)
        password_group.set_title(rel_path.stem)
        password_group.set_description(str(rel_path))
        otp_rows = []
        for index, line in enumerate(content.splitlines()):
            row = Adw.PasswordEntryRow(title_selectable=False, selectable=False)
            text = line
            title = None
            otp = False
            if text.startswith("otpauth://totp"):
                title = "OTP"
                otp = True
                bar = Gtk.ProgressBar(inverted=False)
                row.otp = pyotp.parse_uri(text)
                expires_in = row.otp.interval - datetime.datetime.now().timestamp() % row.otp.interval
                bar.set_fraction(self.map_value(expires_in, 0, row.otp.interval, 0.0, 1.0))
                text = row.otp.now()
                otp_rows.append(row)
                self.otp_rows[id(row)] = row
                row.otp_task = self.create_new_task(self.otp_generated, row, id(row))
                row.bar = bar
            elif index == 0:
                title = "Password"
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
        #print("Build page: {}".format(path))
        page = Adw.NavigationPage(title=path.stem, child=toolbarview)
        page.connect("hidden", self.password_page_hidden)
        page.connect("shown", self.password_page_shown)
        page.otp_rows = group_tuple[-1]
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
            #print("Connecting {} to {}".format(action, actions[action]["method"]))
            act.connect("activate", actions[action]["method"])
            self.add_action(act)
