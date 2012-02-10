import webbrowser

from gi.repository import Gtk, Gdk

from plugins.twitter.account import AuthorizedTwitterAccount
from updatewindow import UpdateWindow
from constants import SHARED_DATA_FILE

def ENTRY_POPUP_MENU():
    return [OpenMenuItem, ReplyMenuItem, RetweetMenuItem, FavMenuItem]


class PopupMenuItem(Gtk.MenuItem):

    def __init__(self, uri=None, scrolled_window=None):
        super(PopupMenuItem, self).__init__()

        self.uri = uri
        self.user, self.entry_id = uri.split('/')[3:6:2]
        self.parent = scrolled_window

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
        update_window = UpdateWindow(None, self.user, self.entry_id)

class RetweetMenuItem(PopupMenuItem):

    def _get_label(self):
        return _('Re_tweet')
        
    def on_activate(self, menuitem):
        dialog = RetweetDialog()
        dialog.run(self.user, self.entry_id, self.parent.window.window)

class RetweetDialog(object):

    def run(self, user, entry_id, parent):
        gui = Gtk.Builder()
        gui.add_from_file(SHARED_DATA_FILE('retweet.glade'))
        
        dialog = gui.get_object('messagedialog')
        dialog.set_transient_for(parent)
        dialog.format_secondary_text(
            _("Retweet this %s's tweet to your followers?") % user)

        response_id = dialog.run()

        if response_id == Gtk.ResponseType.YES:
            twitter_account = AuthorizedTwitterAccount()
            twitter_account.api.retweet(entry_id, self._on_retweet_status)
            
        dialog.destroy()

    def _on_retweet_status(self, *args):
        #print args
        pass

class FavMenuItem(PopupMenuItem):

    def _get_label(self):
        return _('_Favorite')
        
    def on_activate(self, menuitem):
        twitter_account = AuthorizedTwitterAccount()
        twitter_account.api.fav(self.entry_id)
            
class SearchMenuItem(PopupMenuItem):

    def _get_label(self):
        return _('_Search')

    def on_activate(self, menuitem):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        text = clipboard.wait_for_text()
        uri = 'http://www.google.com/search?q=%s' % text
        webbrowser.open(uri)
