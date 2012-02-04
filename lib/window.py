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
from menu import SearchMenuItem, get_status_menuitems
from updatewindow import UpdateWindow
from utils.notification import Notification
from utils.htmlentities import decode_html_entities
from utils.urlgetautoproxy import UrlGetWithAutoProxy
from utils.settings import SETTINGS, SETTINGS_GEOMETRY
from constants import VERSION, SHARED_DATA_DIR

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

    def get_notebook(self, group_name):
        if group_name in self.column:
            notebook = self.column[group_name]
        else:
            notebook = FeedNotebook(self.hbox)
            self.column[group_name] = notebook
        
        return notebook

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

    def on_menuitem_about_activate(self, menuitem):
        about = AboutDialog(self.window)

    def on_settings_sticky_change(self, settings, key):
        if settings.get_boolean(key):
            self.window.stick()
        else:
            self.window.unstick()

class FeedNotebook(Gtk.Notebook):

    def __init__(self, parent):
        super(FeedNotebook, self).__init__()
        self.connect('switch-page', self.on_update_tablabel_sensitive)
        self.connect('button-press-event', self.on_update_tablabel_sensitive)
        # self.connect('page-reordered', self.on_page_reordered)

        parent.add(self)
        self.show()

    def on_update_tablabel_sensitive(self, notebook, *args):
        page = notebook.get_current_page() # get previous page
        sw = notebook.get_nth_page(page)
        if hasattr(sw.feedview, 'tab_label'):
            sw.feedview.tab_label.set_sensitive(False)

class FeedScrolledWindow(Gtk.ScrolledWindow):

    def __init__(self, feedview):
        super(FeedScrolledWindow, self).__init__()
        self.feedview = feedview

        self.set_margin_top(4)
        self.set_margin_bottom(4)
        self.set_margin_right(4)
        self.set_margin_left(4)

        self.set_shadow_type(Gtk.ShadowType.IN)

        self.show()

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
            GLib.timeout_add(200, self.execute_script, 'scrollToBottom()')

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

        if self._timer:
            GObject.source_remove(self._timer)
        self._timer = GLib.timeout_add_seconds(delay, self._resume)

    def _resume(self):
        # print "play!"
        self.is_paused = False

class FeedView(object):

    def __init__(self, window, notebook, name='', page=-1):
        self.sw = FeedScrolledWindow(self)
        self.name = name

        self.notebook = notebook
        self.notebook.append_page(self.sw, Gtk.Label.new_with_mnemonic(name))
        self.notebook.reorder_child(self.sw, page)

        # self.notebook.set_tab_reorderable(self.sw, True)
        self.webview = FeedWebView(self.sw)

        self.tab_label = self.notebook.get_tab_label(self.sw)
        self.tab_label.set_sensitive(False)

        self.notification = window.notification

        template_file = os.path.join(SHARED_DATA_DIR, 'html/status.html')
        with open(template_file, 'r') as fh:
            file = fh.read()
        self.temp = Template(unicode(file, 'utf-8', 'ignore'))


    def move(self, notebook, page=-1):
        self.remove()

        self.notebook = notebook
        self.notebook.append_page(self.sw, Gtk.Label.new_with_mnemonic(self.name))
        self.notebook.reorder_child(self.sw, page)

        # self.notebook.set_tab_reorderable(self.sw, True)
        # self.webview = FeedWebView(self.sw)
        # self.webview = webview

        self.tab_label = self.notebook.get_tab_label(self.sw)
        self.tab_label.set_sensitive(False)

    def remove(self):
        page = self.notebook.page_num(self.sw)
        print "removed %s page!" % page
        self.notebook.remove_page(page)

    def update(self, entry, has_notify=False, is_first_call=False):
        text = self.temp.substitute(
            datetime=entry['datetime'],
            id=entry['id'],
            image_uri=entry['image_uri'],
            retweet=entry['retweet'],
            user_name=entry['user_name'],
            user_color=entry['user_color'],
            status_body=entry['status_body'])

        if has_notify and not is_first_call:
            self.notification.notify(entry)

        self.tab_label.set_sensitive(True)
        self.webview.update(text)

class StatusNotification(object):

    def __init__(self, notification):
        self.notification = Notification('Gnome Feed Line')

    def notify(self, entry):
        icon_uri = str(entry['image_uri'])
        entry['icon_path'] = '/tmp/twitter_profile_image.jpg'
 
        urlget = UrlGetWithAutoProxy(icon_uri)
        d = urlget.downloadPage(icon_uri, entry['icon_path']).\
            addCallback(self._notify, entry).addErrback(self._error)
 
    def _notify(self, unknown, entry):
        self.notification.notify(entry['icon_path'],
                                 entry['user_name'], entry['popup_body'])

    def _error(self, *e):
        print "icon get error!", e

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
