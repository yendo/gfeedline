import sys

from gi.repository import Gio, GdkX11, GLib


class NautilusPreviewer(object):

    def __init__(self):
        try:
            bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            self.proxy = Gio.DBusProxy.new_sync(
                bus, Gio.DBusProxyFlags.NONE, None, 
                'org.gnome.NautilusPreviewer',
                '/org/gnome/NautilusPreviewer', 
                'org.gnome.NautilusPreviewer', None)
        except:
            print "Exception: %s" % sys.exc_info()[1]

    def show_file(self, url, parent):
        try:
            xid = parent.get_window().get_xid()
            self.proxy.ShowFile('(sib)', url, xid, 0)
            return True
        except:
            # print "Exception: %s" % sys.exc_info()[1]
            return False

