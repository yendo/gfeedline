import os

from xdg.DesktopEntry import *
from xdg.BaseDirectory import xdg_config_home


class AutoStart(object):
    """Read and Write Desktop Entry for Autostart

    Desktop Application Autostart Specification
    http://standards.freedesktop.org/autostart-spec/latest/
    """

    def __init__(self, app_name):
        self.entry = DesktopEntry()

        filename = '%s.desktop' % app_name
        system_entry = os.path.join('/usr/share/applications/', filename)
        self.local_entry = os.path.join(xdg_config_home, 'autostart', filename)
        self.key = 'X-GNOME-Autostart-enabled'

        self.load_file = self.local_entry \
            if os.access(self.local_entry, os.R_OK) else system_entry \
            if os.access(system_entry, os.R_OK) else None

        if self.load_file:
            self.entry.parse(self.load_file)
        else:
            print "Warning: the desktop entry of %s is not found." % app_name

    def check_enable(self):
        state = bool(self.load_file)
        return state

    def get(self):
        state = bool(self.entry.get(self.key) == 'true')
        return state

    def set(self, state):
        if self.check_enable():
            state_str = 'true' if state else 'false'
            self.entry.set(self.key, state_str, 'Desktop Entry')
            self.entry.write(self.local_entry)

if __name__ == "__main__":
    import unittest

    class TestAutoStart(unittest.TestCase):

        def setUp(self):
            self.autostart = AutoStart("gphotoframe")

        def test_get(self):
            self.autostart.set(True)
            result = self.autostart.get()
            self.assertEqual(result, True)

        def test_get2(self):
            self.autostart.set(False)
            result = self.autostart.get()
            self.assertEqual(result, False)

        def test_badentry(self):
            autostart = AutoStart("gphotoframe-foobar")

            autostart.set(True)
            result = autostart.get()
            self.assertEqual(result, False)

    unittest.main()
