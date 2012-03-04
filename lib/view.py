#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import urllib
import webbrowser
from string import Template

from twisted.internet import reactor
from gi.repository import Gtk, WebKit

from menu import SearchMenuItem, AddFilterMenuItem, ENTRY_POPUP_MENU
from utils.htmlentities import decode_html_entities
from utils.settings import SETTINGS
from constants import SHARED_DATA_FILE
from updatewindow import UpdateWindow


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

    def __init__(self, liststore, notebook, api, name='', page=-1):
        super(FeedView, self).__init__()

        self.name = name
        self.liststore = liststore
        self.window = liststore.window # access from RetweetMenuItem
        self.theme = self.window.theme

        self.append(notebook, page)
        self.webview = FeedWebView(self, api)
        self.notification = self.window.notification

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
        text = self.theme.template.substitute(entry_dict)

        if has_notify and not is_first_call:
            self.notification.notify(entry_dict)

        self.tab_label.set_sensitive(True)
        self.webview.update(text)

    def jump_to_bottom(self, is_bottom=True):
        self.webview.jump_to_bottom(is_bottom)

    def clear_buffer(self):
        self.webview.clear_buffer()
        self.tab_label.set_sensitive(False)

class FeedWebView(WebKit.WebView):

    def __init__(self, scrolled_window, api):
        super(FeedWebView, self).__init__()
        self.scroll = FeedWebViewScroll()
        self.link_on_webview = FeedWebViewLink()
        self.scrolled_window = scrolled_window
        self.theme = scrolled_window.theme

        self.load_uri("file://%s" % SHARED_DATA_FILE('html/base.html')) 
        self.connect("navigation-policy-decision-requested", self.on_click_link)
        self.connect("populate-popup", self.on_popup, api)
        self.connect("hovering-over-link", self.on_hovering_over_link)
        self.connect('scroll-event', self.on_scroll_event)
        self.connect("document-load-finished", self.on_load_finished)

        self.connect("drag-data-received", self.on_drag_data_received)
        self.connect("drag-drop", self.on_drag_drop)

        SETTINGS.connect("changed::theme", self.on_load_finished)

        scrolled_window.add(self)
        self.show_all()

    def on_drag_drop(self, widget, context, x, y, time, *args):
        if self.text:
            updatewindow = UpdateWindow(self)
            updatewindow.text_buffer.set_text(self.text)
            self.text = ""

    def on_drag_data_received(self, widget, context, x, y, selection, info, time):
        if info == 4:
            uri, title = selection.get_data().split('\n')
            self.text = "%s - %s" % (title, uri) if title else uri
 
    def update(self, text=None):
        text = text.replace('\n', '')
        is_descend_js = self._bool_js(self.theme.is_descend())
        is_paused_js = self._bool_js(self.scroll.is_paused)

        js = 'append("%s", %s, %s)' % (text, is_descend_js, is_paused_js)
        # print js
        self.execute_script(js)

        if not self.scroll.is_paused:
            js = 'scrollToBottom(%s)' % is_descend_js
            reactor.callLater(0.2, self.execute_script, js)

    def jump_to_bottom(self, is_bottom=True):
        self.execute_script('jumpToBottom(%s)' % self._bool_js(is_bottom))

    def clear_buffer(self):
        self.execute_script('clearBuffer()')

    def on_hovering_over_link(self, webview, title, uri):
        self.link_on_webview.change(uri)

        if uri:
            self.scroll.is_paused = True
        else:
            self.scroll.pause(delay=3)

    def on_scroll_event(self, webview, event):
        self.scroll.pause()

    def on_popup(self, view, default_menu, api):
        if self.link_on_webview.is_username_link() and api.has_popup_menu:
            for x in default_menu.get_children():
                default_menu.remove(x) 
            for menuitem in ENTRY_POPUP_MENU():
                default_menu.append(menuitem(self.link_on_webview.uri,
                                             self.scrolled_window))
        elif not self.link_on_webview.is_hovering and self.can_copy_clipboard():
            menuitem = SearchMenuItem()
            default_menu.prepend(menuitem)

            menuitem = AddFilterMenuItem(scrolled_window=self.scrolled_window)
            default_menu.append(menuitem)
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

        if button >= 0:
            webbrowser.open(uri)

        return True

    def on_load_finished(self, view, *args):
        self.dom = self.get_dom_document()

        css_file = self.theme.get_css_file()
        js = 'changeCSS("%s");' % css_file
        self.execute_script(js)

    def _bool_js(self, value):
        return 'true' if value else 'false' 

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

import os

class Theme(object):

    def __init__(self):
        SETTINGS.connect("changed::theme", self.on_setting_theme_changed)
        self.on_setting_theme_changed(SETTINGS, 'theme')

        self.all_themes = {}
        path = SHARED_DATA_FILE('html/theme/')

        for root, dirs, files in os.walk(path):
            for file in files:
                name = file.split('.')[0]
                ext = os.path.splitext(file)[1][1:]

                self.all_themes.setdefault(name, {})
                self.all_themes[name][ext] = os.path.join(root, file)

    def is_descend(self):
        theme_name = self._get_theme_name()
        is_descend = True if theme_name == 'Chat' else False
        return is_descend

    def get_all_list(self):
        return self.all_themes.keys()

    def get_css_file(self):
        theme_name = self._get_theme_name()
        css_file = SHARED_DATA_FILE('html/theme/%s.css' % theme_name)
        return css_file

    def _get_theme_name(self):
        return SETTINGS.get_string('theme')

    def on_setting_theme_changed(self, settings, key): # get_status_template
        theme_name = self._get_theme_name()
        template_file = SHARED_DATA_FILE('html/theme/%s.html' % theme_name)

        if not os.path.isfile(template_file):
            template_file = SHARED_DATA_FILE('html/theme/Twitter.html')

        with open(template_file, 'r') as fh:
            file = fh.read()
        self.template = Template(unicode(file, 'utf-8', 'ignore'))
