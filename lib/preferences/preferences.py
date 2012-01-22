#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import os

from gi.repository import Gtk

from ..plugins.twitter.assistant import TwitterAuthAssistant
from ..utils.settings import SETTINGS_TWITTER
from feedsource import FeedSourceDialog

class Preferences(object):

    def __init__(self, liststore):
        self.liststore = liststore

        gui = Gtk.Builder()
        gui.add_from_file(os.path.abspath('share/preferences.glade'))
        self.preferences = gui.get_object('preferences')
        self.preferences.show_all()

        self.notebook = gui.get_object('notebook1')
        self.notebook.remove_page(1)
        frame = gui.get_object('frame5')
        frame.hide()

        self.label_username = gui.get_object('label_confirm_username')
        self.on_setting_username_changed()
        SETTINGS_TWITTER.connect("changed::user-name", 
                                 self.on_setting_username_changed)

        self.feedsource_treeview = gui.get_object('feedsourcetreeview')
        self.feedsource_treeview.set_model(liststore)
        
        
        gui.connect_signals(self)

    def on_setting_username_changed(self, *args):
        user_name = SETTINGS_TWITTER.get_string('user-name') or 'none'
        self.label_username.set_text(user_name)

    def on_button_twitter_auth_clicked(self, button):
        assistant = TwitterAuthAssistant() 

    def on_button_close_clicked(self, button):
        self.liststore.save_settings()
        self.preferences.destroy()

    def on_checkbutton_always_toggled_cb(self, button):
        pass

    def on_checkbutton_auto_toggled_cb(self, button):
        pass

    def on_button_feed_new_clicked(self, button):
        dialog = FeedSourceDialog(self.preferences)
        (response_id, v) = dialog.run()

        if response_id == Gtk.ResponseType.OK:
            new_iter = self.liststore.append(v)
            self._set_coursor_to(new_iter)

    def on_button_feed_prefs_clicked(self, button):
        treeselection = self.feedsource_treeview.get_selection()
        (model, iter) = treeselection.get_selected()

        dialog = FeedSourceDialog(self.preferences, model[iter])
        (response_id, v) = dialog.run()

        if response_id == Gtk.ResponseType.OK:
            new_iter = self.liststore.append(v, iter)

            self.liststore.remove(iter)
            self._set_coursor_to(new_iter)

    def on_button_feed_del_clicked(self, button):
        treeselection = self.feedsource_treeview.get_selection()
        (model, iter) = treeselection.get_selected()

        self.liststore.remove(iter)
        #self._set_button_sensitive(False)

    def on_treeview1_query_tooltip(self, w, *args):
        pass

    def on_treeview1_cursor_changed(self, w):
        pass

    def on_treeview1_button_press_event(self, w):
        pass

    def on_treeview2_cursor_changed(self, w):
        pass

    def _set_coursor_to(self, iter):
        model = self.feedsource_treeview.get_model()
        row = model.get_path(iter)
        self.feedsource_treeview.set_cursor(row, None, False)
