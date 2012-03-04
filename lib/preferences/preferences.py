#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

from gi.repository import Gtk, Gdk

from ..plugins.twitter.assistant import TwitterAuthAssistant
from ..utils.settings import SETTINGS, SETTINGS_TWITTER
from ..utils.autostart import AutoStart
from ..constants import SHARED_DATA_FILE, Column
from ..theme import Theme
from feedsource import FeedSourceDialog, FeedSourceAction
from filters import FilterDialog, FilterAction

class Preferences(object):

    def __init__(self, mainwindow):
        self.liststore = mainwindow.liststore

        gui = Gtk.Builder()
        gui.add_from_file(SHARED_DATA_FILE('preferences.glade'))
        self.preferences = gui.get_object('preferences')
        self.preferences.show_all()

        notebook = gui.get_object('notebook1')
        notebook.remove_page(1)
        recent_page = SETTINGS.get_int('preferences-recent-page')
        notebook.set_current_page(recent_page)

        self.label_username = gui.get_object('label_confirm_username')
        self.on_setting_username_changed()
        SETTINGS_TWITTER.connect("changed::user-name", 
                                 self.on_setting_username_changed)

        self.feedsource_action = FeedSourceAction(
            gui, mainwindow, self.liststore, self.preferences)
        self.filter_action = FilterAction(
            gui, mainwindow, self.liststore.filter_liststore, self.preferences)

        self.combobox_theme = ComboboxTheme(gui, self.liststore)
        self.autostart = AutoStartWithCheckButton(gui, 'gfeedline')

        SETTINGS.connect("changed::window-sticky", self.on_settings_sticky_change)
        self.on_settings_sticky_change(SETTINGS, 'window-sticky')
        sticky = SETTINGS.get_boolean('window-sticky')
        checkbutton_sticky = gui.get_object('checkbutton_sticky')
        checkbutton_sticky.set_active(sticky)

        gui.connect_signals(self)

    def on_setting_username_changed(self, *args):
        user_name = SETTINGS_TWITTER.get_string('user-name') or 'none'
        self.label_username.set_text(user_name)

    def on_settings_sticky_change(self, settings, key):
        if settings.get_boolean(key):
            self.preferences.stick()
        else:
            self.preferences.unstick()

    def on_button_twitter_auth_clicked(self, button):
        assistant = TwitterAuthAssistant(self.preferences) 

    def on_button_close_clicked(self, notebook):
        page = notebook.get_current_page()
        SETTINGS.set_int('preferences-recent-page', page)

        self.combobox_theme.check_active()
        self.liststore.save_settings()
        self.liststore.filter_liststore.save_settings()
        self.preferences.destroy()

    def on_checkbutton_sticky_toggled(self, button):
        sticky = button.get_active()
        SETTINGS.set_boolean('window-sticky', sticky)

    def on_checkbutton_autostart_toggled(self, button):
        state = button.get_active()
        self.autostart.set(state)


    def on_button_feed_new_clicked(self, button):
        self.feedsource_action.on_button_feed_new_clicked(button)

    def on_button_feed_prefs_clicked(self, treeselection):
        self.feedsource_action.on_button_feed_prefs_clicked(treeselection)

    def on_button_feed_del_clicked(self, treeselection):
        self.feedsource_action.on_button_feed_del_clicked(treeselection)

    def on_feedsource_treeview_cursor_changed(self, treeselection):
        self.feedsource_action.on_feedsource_treeview_cursor_changed(treeselection)

    def on_feedsource_treeview_query_tooltip(self, treeview, *args):
        self.feedsource_action.on_feedsource_treeview_query_tooltip(treeview, args)


    def on_button_filter_new_clicked(self, button):
        self.filter_action.on_button_feed_new_clicked(button)

    def on_button_filter_prefs_clicked(self, treeselection):
        self.filter_action.on_button_feed_prefs_clicked(treeselection)

    def on_button_filter_del_clicked(self, treeselection):
        self.filter_action.on_button_feed_del_clicked(treeselection)

    def on_filter_treeview_cursor_changed(self, treeselection):
        self.filter_action.on_feedsource_treeview_cursor_changed(treeselection)

#    def on_filter_treeview_query_tooltip(self, treeview, *args):
#        self.filter_action.on_feedsource_treeview_query_tooltip(treeview, args)


    def on_plugin_treeview_cursor_changed(self, treeview):
        pass

class ComboboxTheme(object):

    def __init__(self, gui, liststore):
        self.liststore = liststore
        theme = Theme()
        self.labels = theme.get_all_list()

        self.combobox = gui.get_object('comboboxtext_theme')
        selected_theme = SETTINGS.get_string('theme')
        num = self.labels.index(selected_theme.decode('utf-8'))
        self.combobox.set_active(num)

    def check_active(self):
        old = SETTINGS.get_string('theme')
        new = self.labels[self.combobox.get_active()]

        if old != new:
            SETTINGS.set_string('theme', new)

class AutoStartWithCheckButton(AutoStart):

    def __init__(self, gui, app_name):
        super(AutoStartWithCheckButton, self).__init__(app_name)
        
        checkbutton = gui.get_object('checkbutton_autostart')
        checkbutton.set_sensitive(self.check_enable())
        checkbutton.set_active(self.get())
