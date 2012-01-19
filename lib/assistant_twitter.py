#!/usr/bin/python
#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import os

from gi.repository import Gtk, WebKit, GLib, GObject

from twitterauthorize import TwitterAuthorization
from utils.settings import SETTINGS_TWITTER


class TwitterAuthAssistant(Gtk.Assistant):

    def __init__(self):
        super(TwitterAuthAssistant, self).__init__()

        gui = Gtk.Builder()
        gui.add_from_file(os.path.abspath('share/assistant_twitter.glade'))

        self.authorization = TwitterAuthorization()
        self.entry = gui.get_object('entry_pin')
        self.label_screen_name = gui.get_object('label_name')

        self.set_title('Twitter Account Setup')
        self.set_default_size(480, 200)

        self.connect('apply', self.on_apply_button_clicked)
        self.connect('cancel', self.on_cancel_button_clicked)
        self.connect('prepare', self.on_prepare)
        self.connect('close', self.on_close)

        # page 1
        page1 = gui.get_object('label1')
        self.append_page(page1)

        self.set_page_title(page1, 'Intro')
        self.set_page_type(page1, Gtk.AssistantPageType.INTRO)
        self.set_page_complete(page1, True)

        # page 2
        page2 = gui.get_object('box1')
        self.append_page(page2)

        self.set_page_title(page2, 'Enter PIN')
        self.set_page_type(page2, Gtk.AssistantPageType.CONTENT)
        self.set_page_complete(page2, True)

        # page 3
        page3 = gui.get_object('box2')
        self.append_page(page3)

        self.set_page_title(page3, 'Confirm')
        self.set_page_type(page3, Gtk.AssistantPageType.CONFIRM)
        self.set_page_complete(page3, True)

        self.show_all()

    def on_prepare(self, assistant, page):
        page_num = self.get_current_page()

        if page_num == 1:
            self.token = self.authorization.open_authorize_uri()
        elif page_num == 2:
            pin = self.entry.get_text()

            self.result = self.authorization.get_access_token(pin, self.token)
            print self.result

            self.label_screen_name.set_text(self.result['screen-name'])

    def on_apply_button_clicked(self, assistant):
        # GSettings.

        SETTINGS_TWITTER.set_string('access-token', self.result['access-token'])
        SETTINGS_TWITTER.set_string('access-secret', self.result['access-secret'])
        SETTINGS_TWITTER.set_string('user-name', self.result['screen-name'])

        print "apply"

    def on_cancel_button_clicked(self, assistant):
        self.destroy()

    def on_close(self, assistant):
        print "close"
        self.destroy()

