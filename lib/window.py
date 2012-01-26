#!/usr/bin/python
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
from gi.repository import Gtk, WebKit, GLib, GObject, Gdk

from preferences.preferences import Preferences
from updatewindow import UpdateWindow
from utils.notification import Notification
from utils.htmlentities import decode_html_entities
from constants import VERSION

class MainWindow(object):

    def __init__(self, liststore):
        self.liststore = liststore

        gui = Gtk.Builder()
        gui.add_from_file(os.path.abspath('share/gfeedline.glade'))

        self.window = window = gui.get_object('window1')
        self.notebook = gui.get_object('notebook1')
        self.notebook.remove_page(0)
        # self.notebook.connect('page-reordered', self.on_page_reordered)
        menubar = gui.get_object('menubar1')
        self.sw = gui.get_object('scrolledwindow1')

        self.notification = Notification('Gnome Feed Line')

        window.set_default_icon()
        window.resize(480, 600)
        window.connect("delete-event", self.on_stop)
        window.show_all()

        gui.connect_signals(self)

    def on_stop(self, *args):
        reactor.stop()

    def on_menuitem_update_activate(self, menuitem):
        prefs = UpdateWindow(self)

    def on_menuitem_prefs_activate(self, menuitem):
        prefs = Preferences(self)

    def on_menuitem_about_activate(self, menuitem):
        about = AboutDialog(self.window)
        
class FeedScrolledWindow(Gtk.ScrolledWindow):

    def __init__(self):
        super(FeedScrolledWindow, self).__init__()

        self.set_margin_top(4)
        self.set_margin_bottom(4)
        self.set_margin_right(4)
        self.set_margin_left(4)

        self.set_shadow_type(Gtk.ShadowType.IN)
        self.show()

class FeedWebView(WebKit.WebView):

    def __init__(self, scrolled_window):
        super(FeedWebView, self).__init__()
        self.load_uri("file://%s" % os.path.abspath('html/base.html')) 

        self.connect("navigation-policy-decision-requested", self.on_click_link)
        self.connect("populate-popup", self.on_popup)

        scrolled_window.add(self)
        self.show_all()

    def update(self, text=None):
        text = text.replace('\n', '')
        js = 'append("%s")' % text
        # print js
        self.execute_script(js)

        GLib.timeout_add(200, self.execute_script, 'scrollToBottom()')

    def on_popup(self, view, default_menu):
        if self.can_copy_clipboard():
            menuitem = SearchMenuItem()
            default_menu.prepend(menuitem)
        else:
            default_menu.destroy()

    def on_click_link(self, view, frame, req, action, decison):
        button = action.get_button()
        uri = action.get_original_uri()

        if uri.startswith('gfeedline:'):
            menu = PopupMenu(uri)
            menu.menu.popup(None, None, None, None, button, Gdk.CURRENT_TIME)
        else:
            uri = decode_html_entities(urllib.unquote(uri))
            uri = uri.replace('#', '%23') # for Twitter hash tags
            webbrowser.open(uri)

        return True

class SearchMenuItem(Gtk.MenuItem):

    def __init__(self):
        super(SearchMenuItem, self).__init__()
        self.set_label('_Search')
        self.set_use_underline(True)
        self.connect('activate', self.on_search)
        self.show()
        
    def on_search(self, menuitem):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY)
        text = clipboard.wait_for_text()
        uri = 'http://www.google.com/search?q=%s' % text
        webbrowser.open(uri)

class FeedView(object):

    def __init__(self, window, name='', page=-1):
        self.sw = FeedScrolledWindow()
        self.notebook = window.notebook
        self.notebook.append_page(self.sw, Gtk.Label.new_with_mnemonic(name))
        self.notebook.reorder_child(self.sw, page)
        # self.notebook.set_tab_reorderable(self.sw, True)
        self.webview = FeedWebView(self.sw)

        self.notification = window.notification

        template_file = os.path.abspath('html/status.html')
        with open(template_file, 'r') as fh:
            file = fh.read()
        self.temp = Template(unicode(file, 'utf-8', 'ignore'))

    def remove(self):
        page = self.notebook.page_num(self.sw)
        print "removed %s page!" % page
        self.notebook.remove_page(page)

    def update(self, entry, has_notify=False, is_first_call=False):
        text = self.temp.substitute(
            datetime=entry['datetime'],
            id=entry['id'],
            image_uri=entry['image_uri'],
            user_name=entry['user_name'],
            user_color=entry['user_color'],
            status_body=entry['status_body'])

        if has_notify and not is_first_call:
            self.notification.notify('', #entry.user.profile_image_url, 
                                     entry['user_name'], entry['popup_body'])
        self.webview.update(text)

class PopupMenu(object):

    def __init__(self, uri):
        self.uri = uri

        gui = Gtk.Builder()
        gui.add_from_file(os.path.abspath('share/menu.glade'))

        self.menu = gui.get_object('menu1')
        self.menu.show_all()

        gui.connect_signals(self)

    def on_menuitem_open_activate(self, menuitem):
        uri = self.uri.replace('gfeedline:', 'https:')
        webbrowser.open(uri)

    def on_menuitem_reply_activate(self, menuitem):
        uri_schme =self.uri.split('/')
        user, id = uri_schme[3:6:2]
        update_window = UpdateWindow(None, user, id)

    def on_menuitem_retweet_activate(self, menuitem):
        pass


class AboutDialog(object):

    def __init__(self, parent):
        gui = Gtk.Builder()
        gui.add_from_file(os.path.abspath('share/gfeedline.glade'))
        about = gui.get_object('aboutdialog')
        about.set_transient_for(parent)
        about.set_property('version', VERSION)
        # about.set_program_name('GNOME Feed Line')

        about.run()
        about.destroy()
