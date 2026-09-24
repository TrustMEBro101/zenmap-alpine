#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
import subprocess
import threading
import re
import shlex


PROFILES = {
    "Ping scan": ["-sn"],
    "Quick scan": ["-T4", "-F"],
    "Regular scan": ["-T4"],
    "Intense scan": ["-T4", "-A", "-v"],
    "Service/version detection": ["-T4", "-sV"],
    "OS detection": ["-T4", "-O"],
    "Full TCP": ["-T4", "-p-"],
    "Intense TCP": ["-T4", "-A", "-v", "-p-"],
}


class ZenmapAlpine(Gtk.Window):
    def __init__(self):
        super().__init__(title="Zenmap Alpine")
        self.set_default_size(1000, 680)
        self.set_border_width(8)

        self.process = None
        self.output_lines = []

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(root)

        # Target / profile / controls row
        top = Gtk.Grid()
        top.set_column_spacing(8)
        top.set_row_spacing(6)
        root.pack_start(top, False, False, 0)

        target_label = Gtk.Label(label="Target:")
        target_label.set_halign(Gtk.Align.START)
        top.attach(target_label, 0, 0, 1, 1)

        self.target = Gtk.Entry()
        self.target.set_placeholder_text("IP, hostname, subnet, or range")
        self.target.set_hexpand(True)
        self.target.connect("changed", self.on_target_changed)
        top.attach(self.target, 1, 0, 3, 1)

        profile_label = Gtk.Label(label="Profile:")
        profile_label.set_halign(Gtk.Align.START)
        top.attach(profile_label, 4, 0, 1, 1)

        self.profile = Gtk.ComboBoxText()
        for name in PROFILES:
            self.profile.append_text(name)
        self.profile.set_active(3)  # Intense scan
        self.profile.connect("changed", self.on_profile_changed)
        top.attach(self.profile, 5, 0, 2, 1)

        self.scan_button = Gtk.Button(label="Scan")
        self.scan_button.connect("clicked", self.start_scan)
        top.attach(self.scan_button, 7, 0, 1, 1)

        self.cancel_button = Gtk.Button(label="Cancel")
        self.cancel_button.set_sensitive(False)
        self.cancel_button.connect("clicked", self.cancel_scan)
        top.attach(self.cancel_button, 8, 0, 1, 1)

        # Command row
        command_label = Gtk.Label(label="Command:")
        command_label.set_halign(Gtk.Align.START)
        top.attach(command_label, 0, 1, 1, 1)

        self.command = Gtk.Entry()
        self.command.set_editable(True)
        self.command.set_hexpand(True)
        top.attach(self.command, 1, 1, 8, 1)

        # Notebook like the classic Zenmap layout
        notebook = Gtk.Notebook()
        notebook.set_hexpand(True)
        notebook.set_vexpand(True)
        root.pack_start(notebook, True, True, 0)

        self.output_view = self.make_text_view()
        notebook.append_page(
            self.wrap_scrolled(self.output_view),
            Gtk.Label(label="Nmap Output"),
        )

        self.hosts_view = self.make_text_view()
        notebook.append_page(
            self.wrap_scrolled(self.hosts_view),
            Gtk.Label(label="Hosts"),
        )

        self.services_view = self.make_text_view()
        notebook.append_page(
            self.wrap_scrolled(self.services_view),
            Gtk.Label(label="Services"),
        )

        # Status bar
        self.status = Gtk.Label(label="Ready")
        self.status.set_halign(Gtk.Align.START)
        root.pack_start(self.status, False, False, 0)

        self.update_command()

    def make_text_view(self):
        view = Gtk.TextView()
        view.set_editable(False)
        view.set_cursor_visible(False)
        view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        view.set_monospace(True)
        return view

    def wrap_scrolled(self, widget):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(widget)
        return scrolled

    def get_command(self):
        target = self.target.get_text().strip()
        profile = self.profile.get_active_text() or "Regular scan"
        args = PROFILES.get(profile, ["-T4"])
        return ["nmap", *args, target] if target else ["nmap", *args]

    def update_command(self):
        self.command.set_text(" ".join(self.get_command()))

    def on_target_changed(self, _widget):
        self.update_command()

    def on_profile_changed(self, _widget):
        self.update_command()

    def set_text(self, view, text):
        buffer = view.get_buffer()
        buffer.set_text(text)

    def append_output(self, text):
        self.output_lines.append(text)
        buffer = self.output_view.get_buffer()
        end = buffer.get_end_iter()
        buffer.insert(end, text)

        mark = buffer.create_mark(None, buffer.get_end_iter(), False)
        self.output_view.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)

    def parse_results(self):
        output = "".join(self.output_lines)

        hosts = []
        for match in re.finditer(r"Nmap scan report for (.+)", output):
            host = match.group(1).strip()
            if host not in hosts:
                hosts.append(host)

        services = []
        for line in output.splitlines():
            # Typical Nmap service-table line:
            # 22/tcp open ssh OpenSSH ...
            if re.match(r"^\d+/(tcp|udp)\s+\S+", line.strip()):
                services.append(line.strip())

        self.set_text(self.hosts_view, "\n".join(hosts) or "No hosts parsed yet.")
        self.set_text(self.services_view, "\n".join(services) or "No services parsed yet.")

    def start_scan(self, _button):
        if self.process is not None:
            return

        target = self.target.get_text().strip()
        if not target:
            self.status.set_text("Enter a target first.")
            self.target.grab_focus()
            return

        command_text = self.command.get_text().strip()
        if not command_text:
            self.status.set_text("Enter an Nmap command first.")
            self.command.grab_focus()
            return

        try:
            command = shlex.split(command_text)
        except ValueError as exc:
            self.status.set_text(f"Invalid command: {exc}")
            self.command.grab_focus()
            return

        if not command or command[0] != "nmap":
            self.status.set_text("Command must start with nmap.")
            self.command.grab_focus()
            return

        self.output_lines = []
        self.set_text(self.output_view, "")
        self.set_text(self.hosts_view, "")
        self.set_text(self.services_view, "")

        self.scan_button.set_sensitive(False)
        self.cancel_button.set_sensitive(True)
        self.profile.set_sensitive(False)
        self.target.set_sensitive(False)
        self.status.set_text("Scanning...")

        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except Exception as exc:
            self.append_output(f"Failed to start Nmap:\n{exc}\n")
            self.finish_scan()
            return

        threading.Thread(target=self.read_process, daemon=True).start()

    def read_process(self):
        try:
            for line in self.process.stdout:
                GLib.idle_add(self.append_output, line)
        finally:
            return_code = self.process.wait()
            GLib.idle_add(self.scan_finished, return_code)

    def scan_finished(self, return_code):
        self.parse_results()
        self.finish_scan()

        if return_code == 0:
            self.status.set_text("Scan complete.")
        elif return_code < 0:
            self.status.set_text("Scan terminated.")
        else:
            self.status.set_text(f"Nmap exited with code {return_code}.")

        return False

    def finish_scan(self):
        self.process = None
        self.scan_button.set_sensitive(True)
        self.cancel_button.set_sensitive(False)
        self.profile.set_sensitive(True)
        self.target.set_sensitive(True)

    def cancel_scan(self, _button):
        if self.process is not None:
            try:
                self.process.terminate()
            except ProcessLookupError:
                pass
            self.status.set_text("Stopping scan...")

    def close_window(self, *_args):
        if self.process is not None:
            try:
                self.process.terminate()
            except ProcessLookupError:
                pass
        Gtk.main_quit()


def main():
    window = ZenmapAlpine()
    window.connect("delete-event", window.close_window)
    window.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
