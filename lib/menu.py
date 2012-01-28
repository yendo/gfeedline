import webbrowser

from gi.repository import Gtk, Gdk
from updatewindow import UpdateWindow

def get_status_menuitems():
    return [OpenMenuItem, ReplyMenuItem, RetweetMenuItem]

class PopupMenuItem(Gtk.MenuItem):

    def __init__(self, uri=None):
        super(PopupMenuItem, self).__init__()

        self. uri = uri
        self.set_label(self._get_label())
        self.set_use_underline(True)
        self.connect('activate', self.on_activate)
        self.show()

class OpenMenuItem(PopupMenuItem):

    def _get_label(self):
        return '_Open'
        
    def on_activate(self, menuitem):
        uri = self.uri.replace('gfeedline:', 'https:')
        webbrowser.open(uri)

class ReplyMenuItem(PopupMenuItem):

    def _get_label(self):
        return '_Reply'
        
    def on_activate(self, menuitem):
        uri_schme =self.uri.split('/')
        user, id = uri_schme[3:6:2]
        update_window = UpdateWindow(None, user, id)

class RetweetMenuItem(PopupMenuItem):

    def __init__(self, uri):
        super(RetweetMenuItem, self).__init__(uri)
        self.set_sensitive(False)

    def _get_label(self):
        return '_Retweet'
        
    def on_activate(self, menuitem):
        uri_schme =self.uri.split('/')
        user, id = uri_schme[3:6:2]
        update_window = UpdateWindow(None, user, id)

class SearchMenuItem(PopupMenuItem):

    def _get_label(self):
        return '_Search'

    def on_activate(self, menuitem):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        text = clipboard.wait_for_text()
        uri = 'http://www.google.com/search?q=%s' % text
        webbrowser.open(uri)
