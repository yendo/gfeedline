import webbrowser

from gi.repository import Gtk, Gdk

from plugins.twitter.account import AuthorizedTwitterAccount
from updatewindow import UpdateWindow
from constants import SHARED_DATA_FILE
from utils.urlgetautoproxy import UrlGetWithAutoProxy

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

    def _get_entry_from_dom(self, entry_id):
        dom = self.parent.webview.dom.get_element_by_id(entry_id)

        def _get_first_class(cls_name):
            return dom.get_elements_by_class_name(cls_name).item(0)

        img_url = _get_first_class('usericon').get_attribute('src')
        user_name = _get_first_class('username').get_inner_text()
        body = _get_first_class('body').get_inner_text()
        date_time = _get_first_class('datetime').get_inner_text()

        entry_dict = dict(
            date_time=date_time,
            id=entry_id,
            image_uri=img_url,
            user_name=user_name,
            status_body=body
            )

        # print entry_dict
        return entry_dict

class OpenMenuItem(PopupMenuItem):

    LABEL = _('_Open')
        
    def on_activate(self, menuitem):
        uri = self.uri.replace('gfeedline:', 'https:')
        webbrowser.open(uri)

class ReplyMenuItem(PopupMenuItem):

    LABEL = _('_Reply')
        
    def on_activate(self, menuitem):
        entry_dict = self._get_entry_from_dom(self.entry_id)
        update_window = UpdateWindow(None, entry_dict)

class RetweetMenuItem(PopupMenuItem):

    LABEL = _('Re_tweet')
        
    def on_activate(self, menuitem):
        entry_dict = self._get_entry_from_dom(self.entry_id)
        dialog = RetweetDialog()
        dialog.run(entry_dict, self.parent.window.window)

class RetweetDialog(object):

    def run(self, entry, parent):
        self.parent = parent

        gui = Gtk.Builder()
        gui.add_from_file(SHARED_DATA_FILE('retweet.glade'))

        icon_uri = str(entry['image_uri'])
        entry['icon_path'] = '/tmp/twitter_profile_image2.jpg'
        urlget = UrlGetWithAutoProxy(icon_uri)
        d = urlget.downloadPage(icon_uri, entry['icon_path']).\
            addCallback(self._run, gui, entry).addErrback(self._on_error)

    def _run(self, unknown, gui, entry, *args):
        gui.get_object('label_user').set_markup('<b>%s</b>' % entry['user_name'])
        gui.get_object('label_body').set_text(entry['status_body'])
        gui.get_object('image_usericon').set_from_file(entry['icon_path'])

        dialog = gui.get_object('messagedialog')
        dialog.set_transient_for(self.parent)

        response_id = dialog.run()

        if response_id == Gtk.ResponseType.YES:
            twitter_account = AuthorizedTwitterAccount()
            twitter_account.api.retweet(entry['id'], self._on_retweet_status)
            
        dialog.destroy()

    def _on_error(self, *args):
        print "error", args

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
