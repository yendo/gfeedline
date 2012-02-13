import webbrowser

from gi.repository import Gtk, Gdk

from plugins.twitter.account import AuthorizedTwitterAccount
from updatewindow import UpdateWindow
from constants import SHARED_DATA_FILE

def ENTRY_POPUP_MENU():
    return [OpenMenuItem, ReplyMenuItem, RetweetMenuItem, FavMenuItem]


class PopupMenuItem(Gtk.MenuItem):

    LABEL = ''

    def __init__(self, uri=None, scrolled_window=None):
        super(PopupMenuItem, self).__init__()

        self.uri = uri
        if uri:
            self.user, self.entry_id = uri.split('/')[3:6:2]

        self.parent = scrolled_window

        self.set_label(self.LABEL)
        self.set_use_underline(True)
        self.connect('activate', self.on_activate)
        self.show()

class OpenMenuItem(PopupMenuItem):

    LABEL = _('_Open')
        
    def on_activate(self, menuitem):
        uri = self.uri.replace('gfeedline:', 'https:')
        webbrowser.open(uri)

class ReplyMenuItem(PopupMenuItem):

    LABEL = _('_Reply')
        
    def on_activate(self, menuitem):
        update_window = UpdateWindow(None, self.user, self.entry_id)

class RetweetMenuItem(PopupMenuItem):

    LABEL = _('Re_tweet')
        
    def on_activate(self, menuitem):
        self.dom = self.parent.webview.dom.get_element_by_id(self.entry_id)

        img_url = self._get_first_class('usericon').get_attribute('src')
        user_name = self._get_first_class('username').get_inner_text()
        body = self._get_first_class('body').get_inner_text()
        date_time = self._get_first_class('datetime').get_inner_text()

        entry_dict = dict(
            date_time=date_time,
            id=self.entry_id,
            image_uri=img_url,
            user_name=user_name,
            status_body=body
            )

        print entry_dict

        dialog = RetweetDialog()
        dialog.run(entry_dict, self.parent.window.window)

    def _get_first_class(self, cls_name):
        return self.dom.get_elements_by_class_name(cls_name).item(0)

class RetweetDialog(object):

    def run(self, entry, parent):
        gui = Gtk.Builder()
        gui.add_from_file(SHARED_DATA_FILE('retweet.glade'))
        
        dialog = gui.get_object('messagedialog')
        dialog.set_transient_for(parent)
        dialog.format_secondary_text(
            _("Retweet this %s's tweet to your followers?") % entry['user_name'])

        response_id = dialog.run()

        if response_id == Gtk.ResponseType.YES:
            twitter_account = AuthorizedTwitterAccount()
            twitter_account.api.retweet(entry['id'], self._on_retweet_status)
            
        dialog.destroy()

    def _on_retweet_status(self, *args):
        #print args
        pass

class FavMenuItem(PopupMenuItem):

    LABEL = _('_Favorite')
        
    def on_activate(self, menuitem):
        twitter_account = AuthorizedTwitterAccount()
        twitter_account.api.fav(self.entry_id)
            
class SearchMenuItem(PopupMenuItem):

    LABEL = _('_Search')

    def on_activate(self, menuitem):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        text = clipboard.wait_for_text()
        uri = 'http://www.google.com/search?q=%s' % text
        webbrowser.open(uri)
