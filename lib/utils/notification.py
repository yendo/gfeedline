# -*- coding: utf-8 -*-

import sys

from gi.repository import Gio, GLib


class Notification(object):

    def __init__(self, app_name):
        self.app_name = app_name

        try:
            bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            self.proxy = Gio.DBusProxy.new_sync(
                bus, Gio.DBusProxyFlags.NONE, None, 
                'org.freedesktop.Notifications',
                '/org/freedesktop/Notifications', 
                'org.freedesktop.Notifications', None)

            self.proxy.connect('g-signal', self.on_dbus_signal)
        except:
            print "Exception: %s" % sys.exc_info()[1]

    def notify(self, icon, summary, body, entry=None):
        actions = self._get_actions(entry)
        hints = self._get_hints(entry)

        self.proxy.Notify(
            '(susssasa{sv}i)', 
            self.app_name, 0, icon, summary, body, actions, hints, -1)

    def get_capabilities(self):
        return self.proxy.GetCapabilities()

    def on_dbus_signal(self, proxy, sender_name, signal_name, params):
        pass

    def _get_actions(self, entry):
        return []

    def _get_hints(self, entry):
        #hints = {'urgency':  GLib.Variant.new_int16(1),
        #         'category': GLib.Variant.new_string('im.received')}
        return {}

if __name__ == '__main__':
    n = Notification('app')
    body = 'body'
    print type(body)
    print n.notify('', 'sum', body)
    print n.get_capabilities()
