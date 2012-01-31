import webbrowser

from gi.repository import Gtk, Gdk

from plugins.twitter.account import AuthorizedTwitterAccount
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
        return _('_Open')
        
    def on_activate(self, menuitem):
        uri = self.uri.replace('gfeedline:', 'https:')
        webbrowser.open(uri)

class ReplyMenuItem(PopupMenuItem):

    def _get_label(self):
        return _('_Reply')
        
    def on_activate(self, menuitem):
        uri_schme =self.uri.split('/')
        user, id = uri_schme[3:6:2]
        update_window = UpdateWindow(None, user, id)

class RetweetMenuItem(PopupMenuItem):

    def _get_label(self):
        return _('Re_tweet')
        
    def on_activate(self, menuitem):
        uri_schme =self.uri.split('/')
        user, id = uri_schme[3:6:2]

        twitter_account = AuthorizedTwitterAccount()
        twitter_account.api.retweet(id, self._on_retweet_status)

    def _on_retweet_status(self, *args):
        #print args
        pass

class SearchMenuItem(PopupMenuItem):

    def _get_label(self):
        return _('_Search')

    def on_activate(self, menuitem):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        text = clipboard.wait_for_text()
        uri = 'http://www.google.com/search?q=%s' % text
        webbrowser.open(uri)
