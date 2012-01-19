#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import os

from gi.repository import Gtk
from lib.plugins.twitter.assistant import TwitterAuthAssistant

class Preferences(object):

    def __init__(self):

        gui = Gtk.Builder()
        gui.add_from_file(os.path.abspath('share/preferences.glade'))
        self.preferences = gui.get_object('preferences')
        self.preferences.show_all()

        self.notebook = gui.get_object('notebook1')
        self.notebook.remove_page(1)
        frame = gui.get_object('frame5')
        frame.hide()

        gui.connect_signals(self)

    def on_button_twitter_auth_clicked(self, button):
        assistant = TwitterAuthAssistant() 

    def on_button_close_clicked(self, button):
        self.preferences.destroy()

    def on_checkbutton_always_toggled_cb(self, button):
        pass

    def on_checkbutton_auto_toggled_cb(self, button):
        pass

    def on_button_feed_new_clicked(self, button):
        pass

    def on_button_feed_prefs_clicked(self, button):
        pass

    def on_button_feed_del_clicked(self, button):
        pass

    def on_treeview1_query_tooltip(self, w, *args):
        pass

    def on_treeview1_cursor_changed(self, w):
        pass

    def on_treeview1_button_press_event(self, w):
        pass

    def on_treeview2_cursor_changed(self, w):
        pass
