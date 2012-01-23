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
        except:
            print "Exception: %s" % sys.exc_info()[1]

    def notify(self, icon, summary, body):
        # print type(body)

        #hints = {'urgency':  GLib.Variant.new_int16(1),
        #         'category': GLib.Variant.new_string('im.received')}
        hints = {}

        self.proxy.Notify(
            '(susssasa{sv}i)', 
            self.app_name, 0, icon, summary, body, [], hints, 0)

    def get_capabilities(self):
        return self.proxy.GetCapabilities()


if __name__ == '__main__':
    n = Notification('app')
    body = 'body'
    print type(body)
    print n.notify('', 'sum', body)
    print n.get_capabilities()
