#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import re
import json
import urllib

from gi.repository import Gtk, Gdk

#from getaccesstoken import FacebookWebKitScrolledWindow
from ..base.authwebkit import AuthWebKitScrolledWindow
from ...constants import SHARED_DATA_FILE
from ...utils.urlgetautoproxy import urlget_with_autoproxy


class FacebookAuthAssistant(Gtk.Assistant):

    def __init__(self, parent=None, cb=None, liststore_row=None):
        super(FacebookAuthAssistant, self).__init__()
        self.liststore_row = liststore_row

        gui = Gtk.Builder()
        gui.add_from_file(SHARED_DATA_FILE('assistant_facebook.glade'))
        self.label_user_fullname = gui.get_object('label_name')

        self.set_title(_('Facebook Account Setup'))
        self.set_default_size(400, 400)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_modal(True)
#        if parent:
#            self.set_transient_for(parent)

        self.connect('cancel', self.on_cancel)
        self.connect('close', self.on_close, cb)

        # page 1
        page1 = gui.get_object('label1')
        page1.set_text(page1.get_text().decode('utf-8') % _('Facebook'))
        self.append_page(page1)

        self.set_page_title(page1, _('Intro'))
        self.set_page_type(page1, Gtk.AssistantPageType.INTRO)
        self.set_page_complete(page1, True)

        # page 2
        self.re_token = re.compile('.*access_token=(.*)&.*')
        page2 = FacebookWebKitScrolledWindow()

        # self.page2.connect("login-started", self._set_webkit_ui_cb)
        page2.connect("token-acquired", self._get_access_token_cb)
        page2.connect("error-occurred", self.on_cancel)
        self.append_page(page2)

        self.set_page_title(page2, _('Authorization'))
        self.set_page_type(page2, Gtk.AssistantPageType.CONTENT)
        self.set_page_complete(page2, False)

        # page 3
        page3 = gui.get_object('box2')
        confirm_label = gui.get_object('label6')
        confirm_label.set_text(confirm_label.get_text().decode('utf-8') 
                               % _('Facebook'))
        self.append_page(page3)

        self.set_page_title(page3, _('Confirm'))
        self.set_page_type(page3, Gtk.AssistantPageType.SUMMARY)
        self.set_page_complete(page3, True)

        self.show_all()

    def _get_access_token_cb(self, w, url):
        self.token = self.re_token.sub("\\1", url)
        url = 'https://graph.facebook.com/me?access_token=%s' % self.token
        urlget_with_autoproxy(url, cb=self._get_userinfo_cb)

    def _get_userinfo_cb(self, data):
        d = json.loads(data)
        self.user_fullname = d['name']
        self.idnum = d['id']
        self.label_user_fullname.set_text(self.user_fullname)

        self.next_page()

    def on_close(self, assistant, cb):
        account = ['Facebook', self.user_fullname, self.token, "", self.idnum]
        cb(account, self.liststore_row)
        self.destroy()

    def on_cancel(self, *args):
        self.destroy()

class FacebookWebKitScrolledWindow(AuthWebKitScrolledWindow):

    LOGIN_URL = 'https://www.facebook.com/login.php?'
    ERROR_URL = 'https://www.facebook.com/connect/login_success.html?error'
    RE_TOKEN = '.*access_token=(.*)&.*'

    def _get_auth_url(self):
        values = { 'client_id': 203600696439990,
                   'redirect_uri': 
                   'https://www.facebook.com/connect/login_success.html',
                   'response_type': 'token',
                   'scope': 'user_photos,friends_photos,read_stream,offline_access,publish_stream',
                   'display': 'popup'}
        url = 'https://www.facebook.com/dialog/oauth?' + urllib.urlencode(values)
        return url
