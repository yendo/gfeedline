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

        notebook = gui.get_object('notebook1')
        notebook.remove_page(1)
        recent_page = SETTINGS.get_int('preferences-recent-page')
        notebook.set_current_page(recent_page)

        # account

        self.label_username = gui.get_object('label_confirm_username')
        self.on_setting_username_changed()
        SETTINGS_TWITTER.connect("changed::user-name", 
                                 self.on_setting_username_changed)

        # view & desktop

        self.combobox_theme = ComboboxTheme(gui)
        self.combobox_order = ComboboxTimelineOrder(gui)
        self.fontbutton = TimeLineFontButton(gui, mainwindow)
 
        self.autostart = AutoStartWithCheckButton(gui, 'gfeedline')

        SETTINGS.connect("changed::window-sticky", self.on_settings_sticky_change)
        self.on_settings_sticky_change(SETTINGS, 'window-sticky')
        sticky = SETTINGS.get_boolean('window-sticky')
        checkbutton_sticky = gui.get_object('checkbutton_sticky')
        checkbutton_sticky.set_active(sticky)

        # feeds & filters
        
        self.feedsource_action = FeedSourceAction(
            gui, mainwindow, self.liststore, self.preferences)
        self.filter_action = FilterAction(
            gui, mainwindow, self.liststore.filter_liststore, self.preferences)

        gui.connect_signals(self)
        self.preferences.show_all()

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

        is_theme_changed = self.combobox_theme.check_active()
        is_order_changed = self.combobox_order.check_active()
        if is_theme_changed or is_order_changed:
            self.combobox_theme.update_theme()

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

    def __init__(self, gui):
        theme = Theme()
        self.labels = theme.get_all_list()

        self.combobox = gui.get_object('comboboxtext_theme')
        selected_theme = SETTINGS.get_string('theme')
        num = self.labels.index(selected_theme.decode('utf-8'))
        self.combobox.set_active(num)

    def check_active(self):
        old = SETTINGS.get_string('theme')
        self.new = self.labels[self.combobox.get_active()]
        return old != self.new

    def update_theme(self):
        SETTINGS.set_string('theme', self.new)

dummy = [_('Default'), _('Ascending'), _('Descending')] # for intltool 0.41.1 bug

class ComboboxTimelineOrder(object):

    def __init__(self, gui):
        self.combobox = gui.get_object('comboboxtext_order')
        num = SETTINGS.get_int('timeline-order')
        self.combobox.set_active(num)

    def check_active(self):
        num = self.combobox.get_active()

        theme = Theme()
        old = theme.is_ascending()
        new = theme.is_ascending(num)

        SETTINGS.set_int('timeline-order', num)
        return old != new

class TimeLineFontButton(object):

    def __init__(self, gui, window):
        self.window = window
        self.widget = gui.get_object('fontbutton')
        font_name = SETTINGS.get_string('font')
        self.widget.set_font_name(font_name)

        SETTINGS.connect("changed::font", self.on_settings_font_change)
        #self.on_settings_font_change(SETTINGS, 'window-sticky')

        self.widget.connect('font-set', self.on_button_font_set)

    def on_button_font_set(self, button, *args):
        font_name = button.get_font_name()
        SETTINGS.set_string('font', font_name)

    def on_settings_font_change(self, settings, key):
        font_css = self.window.font.zoom_default()
        self.window.change_font(font_css)

class AutoStartWithCheckButton(AutoStart):

    def __init__(self, gui, app_name):
        super(AutoStartWithCheckButton, self).__init__(app_name)
        
        checkbutton = gui.get_object('checkbutton_autostart')
        checkbutton.set_sensitive(self.check_enable())
        checkbutton.set_active(self.get())
