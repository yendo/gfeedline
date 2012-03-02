import webbrowser

from gi.repository import Gtk, Gdk

from plugins.twitter.account import AuthorizedTwitterAccount
from updatewindow import UpdateWindow, RetweetDialog
from preferences.filters import FilterDialog

# for old WebKit (<= 1.6)
from gi.repository import WebKit
from updatewindow import UpdateWindowOLD, RetweetDialogOLD
CAN_ACCESS_DOM = WebKit.MAJOR_VERSION >= 1 and WebKit.MINOR_VERSION >= 6


def ENTRY_POPUP_MENU():
    return [OpenMenuItem, ReplyMenuItem, RetweetMenuItem, FavMenuItem]


class PopupMenuItem(Gtk.MenuItem):

    LABEL = ''

    def __init__(self, uri=None, scrolled_window=None):
        super(PopupMenuItem, self).__init__()

        self.uri = uri
        self.user, entry_id = uri.split('/')[3:6:2] if uri else [None]*2
        self.parent = scrolled_window

        self.set_label(self.LABEL)
        self.set_use_underline(True)
        self.connect('activate', self.on_activate, entry_id)
        self.show()

    def _get_entry_from_dom(self, entry_id):
        dom = self.parent.webview.dom.get_element_by_id(entry_id)

        def _get_first_class(cls_name):
            return dom.get_elements_by_class_name(cls_name).item(0)

        img_url = _get_first_class('usericon').get_attribute('src')
        user_name = _get_first_class('username').get_inner_text()
        body = _get_first_class('body').get_inner_text()
        date_time = _get_first_class('datetime').get_inner_text()
        is_protected = bool(_get_first_class('protected'))

        entry_dict = dict(
            date_time=date_time,
            id=entry_id,
            image_uri=img_url,
            user_name=user_name,
            is_protected=is_protected,
            status_body=body
            )

        # print entry_dict
        return entry_dict

class OpenMenuItem(PopupMenuItem):

    LABEL = _('_Open')
        
    def on_activate(self, menuitem, entry_id):
        uri = self.uri.replace('gfeedline:', 'https:')
        webbrowser.open(uri)

class ReplyMenuItem(PopupMenuItem):

    LABEL = _('_Reply')
        
    def on_activate(self, menuitem, entry_id):
        if CAN_ACCESS_DOM:
            entry_dict = self._get_entry_from_dom(entry_id)
            update_window = UpdateWindow(None, entry_dict)
        else:
            entry_dict = {'id': entry_id, 'user_name': self.user}
            update_window = UpdateWindowOLD(None, entry_dict)

class RetweetMenuItem(PopupMenuItem):

    LABEL = _('Re_tweet')

    def __init__(self, uri=None, scrolled_window=None):
        super(RetweetMenuItem, self).__init__(uri, scrolled_window)
  
        if CAN_ACCESS_DOM:
            entry_id = uri.split('/')[-1]
            dom = self.parent.webview.dom.get_element_by_id(entry_id)
            is_protected = bool(dom.get_elements_by_class_name('protected').item(0))

            self.set_sensitive(not is_protected)

    def on_activate(self, menuitem, entry_id):
        if CAN_ACCESS_DOM:
            entry_dict = self._get_entry_from_dom(entry_id)
            dialog = RetweetDialog()
        else:
            entry_dict = {'id': entry_id, 'user_name': self.user}
            dialog = RetweetDialogOLD()

        dialog.run(entry_dict, self.parent.window.window)

class FavMenuItem(PopupMenuItem):

    LABEL = _('_Favorite')
        
    def on_activate(self, menuitem, entry_id):
        twitter_account = AuthorizedTwitterAccount()
        twitter_account.api.fav(entry_id)
            
class SearchMenuItem(PopupMenuItem):

    LABEL = _('_Search')

    def on_activate(self, menuitem, entry_id):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        text = clipboard.wait_for_text()

        uri = 'http://www.google.com/search?q=%s' % text
        webbrowser.open(uri)

class AddFilterMenuItem(PopupMenuItem):

    LABEL = _('_Add Filter')

    def on_activate(self, menuitem, entry_id):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        text = clipboard.wait_for_text()

        filter_liststore = self.parent.liststore.filter_liststore

        dialog = FilterDialog(None, text=text)
        response_id, v = dialog.run()

        if response_id == Gtk.ResponseType.OK:
            new_iter = filter_liststore.append(v)
