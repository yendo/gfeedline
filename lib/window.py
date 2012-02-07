#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import os
import urllib
import webbrowser
from string import Template

from twisted.internet import reactor
from gi.repository import Gtk, WebKit

from preferences.preferences import Preferences
from menu import SearchMenuItem, get_status_menuitems
from updatewindow import UpdateWindow
from notification import StatusNotification
from utils.htmlentities import decode_html_entities
from utils.settings import SETTINGS, SETTINGS_GEOMETRY
from constants import VERSION, SHARED_DATA_DIR, Column


class MainWindow(object):

    def __init__(self, liststore):
        self.liststore = liststore

        gui = Gtk.Builder()
        gui.add_from_file(os.path.join(SHARED_DATA_DIR, 'gfeedline.glade'))

        self.window = window = gui.get_object('window1')
        self.hbox = gui.get_object('hbox1')
        self.column = {} # multi-columns for Notebooks

        menubar = gui.get_object('menubar1')
        self.notification = StatusNotification('Gnome Feed Line')

        SETTINGS.connect("changed::window-sticky", self.on_settings_sticky_change)
        self.on_settings_sticky_change(SETTINGS, 'window-sticky')

        is_multi_column = SETTINGS.get_boolean('multi-column')
        menuitem_multicolumn = gui.get_object('menuitem_multicolumn')
        menuitem_multicolumn.set_active(is_multi_column)

        x = SETTINGS_GEOMETRY.get_int('window-x')
        y = SETTINGS_GEOMETRY.get_int('window-y')
        w = SETTINGS_GEOMETRY.get_int('window-width')
        h = SETTINGS_GEOMETRY.get_int('window-height')

        if x >=0 and y >= 0:
            window.move(x, y)

        window.resize(w, h)
        window.connect("delete-event", self.on_stop)
        window.show_all()

        gui.connect_signals(self)

    def get_notebook(self, group_name, is_multi_column):
        if not is_multi_column:
            group_name = 'main'

        if group_name in self.column:
            notebook = self.column[group_name]
        else:
            notebook = FeedNotebook(self.hbox, self.column, group_name)
            self.column[group_name] = notebook
        
        return notebook

    def toggle_multicolumn_mode(self, is_multi_column):
        self.column = {}

        for row in self.liststore:
            notebook = self.get_notebook(row[Column.GROUP], is_multi_column)
            view = row[Column.API].view
            view.remove()
            view.append(notebook, -1)

        timeout = reactor.callLater(0.1, self.on_menuitem_bottom_activate)

    def on_stop(self, *args):
        print "save!"
        x, y = self.window.get_position()
        w, h = self.window.get_size()

        SETTINGS_GEOMETRY.set_int('window-x', x)
        SETTINGS_GEOMETRY.set_int('window-y', y)
        SETTINGS_GEOMETRY.set_int('window-width', w)
        SETTINGS_GEOMETRY.set_int('window-height', h)

        reactor.stop()

    def on_menuitem_quit_activate(self, menuitem):
        self.on_stop()
        # self.window.destroy()

    def on_menuitem_update_activate(self, menuitem):
        prefs = UpdateWindow(self)

    def on_menuitem_prefs_activate(self, menuitem):
        prefs = Preferences(self)

    def on_menuitem_multicolumn_toggled(self, menuitem):
        is_multi_column = menuitem.get_active()
        self.toggle_multicolumn_mode(is_multi_column)
        SETTINGS.set_boolean('multi-column', is_multi_column)

    def on_menuitem_about_activate(self, menuitem):
        about = AboutDialog(self.window)

    def on_menuitem_bottom_activate(self, menuitem=None):
        for notebook in self.column.values():
            notebook.jump_all_tabs_to_bottom()

    def on_settings_sticky_change(self, settings, key):
        if settings.get_boolean(key):
            self.window.stick()
        else:
            self.window.unstick()

class FeedNotebook(Gtk.Notebook):

    def __init__(self, parent, column, group_name):
        self.column = column
        self.group_name = group_name

        super(FeedNotebook, self).__init__()
        self.set_scrollable(True)
        self.popup_enable()

        self.connect('switch-page', self.on_update_tablabel_sensitive)
        self.connect('button-press-event', self.on_update_tablabel_sensitive)
        # self.connect('page-reordered', self.on_page_reordered)

        parent.add(self)
        self.show()

    def on_update_tablabel_sensitive(self, notebook, *args):
        page = notebook.get_current_page() # get previous page
        feedview = notebook.get_nth_page(page) # get child
        if hasattr(feedview, 'tab_label'):
            feedview.tab_label.set_sensitive(False)

    def append_page(self, child, name, page=-1):
        super(FeedNotebook, self).append_page(
            child, Gtk.Label.new_with_mnemonic(name))
        self.reorder_child(child, page)
        # self.set_tab_reorderable(child, True)

        tab_label = self.get_tab_label(child)
        return tab_label

    def remove_page(self, page):
        super(FeedNotebook, self).remove_page(page)

        if self.get_n_pages() == 0:
            self.destroy()
            del self.column[self.group_name]

    def jump_all_tabs_to_bottom(self):
        for feedview in self.get_children():
            feedview.jump_to_bottom()

class FeedScrolledWindow(Gtk.ScrolledWindow):

    def __init__(self):
        super(FeedScrolledWindow, self).__init__()

        self.set_margin_top(4)
        self.set_margin_bottom(4)
        self.set_margin_right(4)
        self.set_margin_left(4)

        self.set_shadow_type(Gtk.ShadowType.IN)
        self.show()

class FeedView(FeedScrolledWindow):

    def __init__(self, window, notebook, name='', page=-1):
        super(FeedView, self).__init__()

        self.name = name
        self.append(notebook, page)
        self.webview = FeedWebView(self)

        self.notification = window.notification

        template_file = os.path.join(SHARED_DATA_DIR, 'html/status.html')
        with open(template_file, 'r') as fh:
            file = fh.read()
        self.temp = Template(unicode(file, 'utf-8', 'ignore'))

    def append(self, notebook, page=-1):
        self.notebook = notebook
        self.tab_label = notebook.append_page(self, self.name, page)
        self.tab_label.set_sensitive(False)

    def move(self, notebook, page=-1):
        self.remove()
        self.append(notebook, page)

    def remove(self):
        page = self.notebook.page_num(self)
        print "removed %s page!" % page
        self.notebook.remove_page(page)

    def update(self, entry_dict, has_notify=False, is_first_call=False):
        text = self.temp.substitute(entry_dict)

        if has_notify and not is_first_call:
            self.notification.notify(entry_dict)

        self.tab_label.set_sensitive(True)
        self.webview.update(text)

    def jump_to_bottom(self):
        self.webview.jump_to_bottom()

class FeedWebView(WebKit.WebView):

    def __init__(self, scrolled_window):
        super(FeedWebView, self).__init__()
        self.scroll = FeedWebViewScroll()
        self.link_on_webview = FeedWebViewLink()

        self.load_uri("file://%s" % os.path.join(SHARED_DATA_DIR, 'html/base.html')) 
        self.connect("navigation-policy-decision-requested", self.on_click_link)
        self.connect("populate-popup", self.on_popup)
        self.connect("hovering-over-link", self.on_hovering_over_link)
        self.connect('scroll-event', self.on_scroll_event)

        scrolled_window.add(self)
        self.show_all()

    def update(self, text=None):
        text = text.replace('\n', '')
        js = 'append("%s")' % text
        # print js
        self.execute_script(js)

        if not self.scroll.is_paused:
            reactor.callLater(0.2, self.execute_script, 'scrollToBottom()')

    def jump_to_bottom(self):
        self.execute_script('JumpToBottom()')

    def on_hovering_over_link(self, webview, title, uri):
        self.link_on_webview.change(uri)

        if uri:
            self.scroll.is_paused = True
        else:
            self.scroll.pause(delay=3)

    def on_scroll_event(self, webview, event):
        self.scroll.pause()

    def on_popup(self, view, default_menu):
        if self.link_on_webview.is_username_link():
            for x in default_menu.get_children():
                default_menu.remove(x) 
            for menuitem in get_status_menuitems():
                default_menu.append(menuitem(self.link_on_webview.uri))
        elif not self.link_on_webview.is_hovering and self.can_copy_clipboard():
            menuitem = SearchMenuItem()
            default_menu.prepend(menuitem)
        else:
            default_menu.destroy()

    def on_click_link(self, view, frame, req, action, decison):
        button = action.get_button()
        uri = action.get_original_uri()

        if uri.startswith('gfeedline:'):
            uri = uri.replace('gfeedline:', 'https:')
        else:
            uri = decode_html_entities(urllib.unquote(uri))
            uri = uri.replace('#', '%23') # for Twitter hash tags

        webbrowser.open(uri)

        return True

class FeedWebViewLink(object):

    def __init__(self):
        self.uri = None
        self.is_hovering = False

    def change(self, uri):
        self.uri = uri
        self.is_hovering = bool(self.uri)

    def is_username_link(self):
        return self.is_hovering and self.uri.startswith('gfeedline:')

class FeedWebViewScroll(object):

    def __init__(self):
        self.is_paused = False
        self._timer = None

    def pause(self, delay=10):
        # print "pause!", delay
        self.is_paused = True

        if self._timer and not self._timer.called:
            # print "cancel"
            self._timer.cancel()
        self._timer = reactor.callLater(delay, self._resume)

    def _resume(self):
        # print "play!"
        self.is_paused = False

class AboutDialog(object):

    def __init__(self, parent):
        gui = Gtk.Builder()
        gui.add_from_file(os.path.join(SHARED_DATA_DIR, 'gfeedline.glade'))
        about = gui.get_object('aboutdialog')
        about.set_transient_for(parent)
        about.set_property('version', VERSION)
        # about.set_program_name('GNOME Feed Line')

        about.run()
        about.destroy()
