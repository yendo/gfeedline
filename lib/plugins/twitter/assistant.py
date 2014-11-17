#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import re
import webbrowser

from gi.repository import Gtk, Gdk

from getauthtoken import TwitterAuthorization
from ...utils.settings import SETTINGS_TWITTER
from ...constants import SHARED_DATA_FILE

class TwitterAuthAssistant(Gtk.Assistant):

    def __init__(self, parent=None, cb=None):
        super(TwitterAuthAssistant, self).__init__()

        gui = Gtk.Builder()
        gui.add_from_file(SHARED_DATA_FILE('assistant_twitter.glade'))

        self.authorization = TwitterAuthorization()
        self.entry = gui.get_object('entry_pin')
        self.entry.connect('changed', self.on_entry_pin_changed)
        self.label_screen_name = gui.get_object('label_name')
        self.pattern_pin = re.compile('^[0-9]{7,}$')

        self.set_title(_('Twitter Account Setup'))
        self.set_default_size(480, 200)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_modal(True)
#        if parent:
#            self.set_transient_for(parent)

        self.connect('apply', self.on_apply_button_clicked, cb)
        self.connect('cancel', self.on_cancel_button_clicked)
        self.connect('prepare', self.on_prepare)
        self.connect('close', self.on_close)

        # page 1
        page1 = gui.get_object('label1')
        self.append_page(page1)

        self.set_page_title(page1, _('Intro'))
        self.set_page_type(page1, Gtk.AssistantPageType.INTRO)
        self.set_page_complete(page1, True)

        # page 2
        page2 = gui.get_object('box1')
        self.append_page(page2)

        self.set_page_title(page2, _('Enter PIN'))
        self.set_page_type(page2, Gtk.AssistantPageType.CONTENT)
        self.set_page_complete(page2, False)

        # page 3
        page3 = gui.get_object('box2')
        self.append_page(page3)

        self.set_page_title(page3, _('Confirm'))
        self.set_page_type(page3, Gtk.AssistantPageType.CONFIRM)
        self.set_page_complete(page3, False)

        self.show_all()

    def on_entry_pin_changed(self, entry):
        pin = entry.get_text()
        status = bool(self.pattern_pin.match(pin))

        page_widget = self.get_nth_page(1)
        self.set_page_complete(page_widget, status)

    def on_prepare(self, assistant, page):
        page_num = self.get_current_page()

        if page_num == 1:
            uri, self.token = self.authorization.open_authorize_uri()
            webbrowser.open(uri)
        elif page_num == 2:
            pin = self.entry.get_text()
            token, params = self.authorization.get_access_token(pin, self.token)

            screen_name = params['screen_name'][0]
            self.result = {'screen-name': screen_name,
                           'access-token': token.key,
                           'access-secret': token.secret}
            # print self.result

            self.label_screen_name.set_text(self.result['screen-name'])
            self.set_page_complete(self.get_nth_page(page_widget), True)

    def on_apply_button_clicked(self, assistant, cb):
        # print "apply"

        account = [
            'Twitter',
            self.result['screen-name'],
            self.result['access-token'],
            self.result['access-secret'],
            ''
            ]

        cb(account)

    def on_cancel_button_clicked(self, assistant):
        self.destroy()

    def on_close(self, assistant):
        # print "close"
        self.destroy()
