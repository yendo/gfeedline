#!/usr/bin/python
#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import os
import webbrowser

from twisted.internet import reactor
from gi.repository import Gtk, WebKit, GLib, GObject

from preferences.preferences import Preferences

class MainWindow(object):

    def __init__(self, liststore):
        self.liststore = liststore

        gui = Gtk.Builder()
        gui.add_from_file(os.path.abspath('share/gfeedline.glade'))

        self.window = window = gui.get_object('window1')
        self.notebook = gui.get_object('notebook1')
        self.notebook.remove_page(0)
        menubar = gui.get_object('menubar1')
        self.sw = gui.get_object('scrolledwindow1')

        window.resize(480, 600)
        window.connect("delete-event", self.on_stop)
        window.show_all()

        gui.connect_signals(self)

    def append_page(self):
        sw1 = FeedScrolledWindow()
        main.notebook.append_page(sw1, None)
        view1 = FeedWebView(sw1)
        
    def on_stop(self, *args):
        reactor.stop()

    def on_menuitem_prefs_activate(self, menuitem):
        prefs = Preferences(self)

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

        self.connect("navigation-requested", self.on_click_link)
        self.connect("populate-popup", self.on_popup)

        scrolled_window.add(self)
        self.show_all()

    def update(self, text=None):
        text = text.replace('\n', '')
        js = 'append("%s")' % text
        # print js
        self.execute_script(js)

        GLib.timeout_add(150, self.execute_script, 'scrollToBottom()')

    def on_popup(self, view, menu):
        menu.destroy()

    def on_click_link(self, view, frame, req):
        uri = req.get_uri()
        webbrowser.open(uri)
        return True

class FeedView(object):

    def __init__(self, window, name=''):
        self.sw = FeedScrolledWindow()
        self.notebook = window.notebook
        self.notebook.append_page(self.sw, Gtk.Label.new_with_mnemonic(name))
        self.webview = FeedWebView(self.sw)

    def remove(self):
        page = self.notebook.page_num(self.sw)
        print "removed %s page!" % page
        self.notebook.remove_page(page)
