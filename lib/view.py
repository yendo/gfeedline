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

from menu import SearchMenuItem, get_status_menuitems
from utils.htmlentities import decode_html_entities
from utils.settings import SETTINGS
from constants import SHARED_DATA_DIR


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
        self.window = window
        self.theme = window.theme

        self.append(notebook, page)
        self.webview = FeedWebView(self)
        self.notification = window.notification

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

    def __init__(self, scrolled_window):
        super(FeedWebView, self).__init__()
        self.scroll = FeedWebViewScroll()
        self.link_on_webview = FeedWebViewLink()
        self.scrolled_window = scrolled_window
        self.theme = scrolled_window.theme

        self.load_uri("file://%s" % os.path.join(SHARED_DATA_DIR, 'html/base.html')) 
        self.connect("navigation-policy-decision-requested", self.on_click_link)
        self.connect("populate-popup", self.on_popup)
        self.connect("hovering-over-link", self.on_hovering_over_link)
        self.connect('scroll-event', self.on_scroll_event)
        self.connect("document-load-finished", self.on_load_finished)
        SETTINGS.connect("changed::theme", self.on_load_finished)

        scrolled_window.add(self)
        self.show_all()

    def update(self, text=None):
        is_descend_js = self._bool_js(self.theme.is_descend())
        
        text = text.replace('\n', '')
        js = 'append("%s", %s)' % (text, is_descend_js)
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

    def on_popup(self, view, default_menu):
        if self.link_on_webview.is_username_link():
            for x in default_menu.get_children():
                default_menu.remove(x) 
            for menuitem in get_status_menuitems():
                default_menu.append(menuitem(self.link_on_webview.uri,
                                             self.scrolled_window))
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

    def on_load_finished(self, view, *args):
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

class Theme(object):

    def __init__(self):
        SETTINGS.connect("changed::theme", self.on_setting_theme_changed)
        self.on_setting_theme_changed(SETTINGS, 'theme')

    def is_descend(self):
        theme_name = self._get_theme_name()
        is_descend = True if theme_name == 'chat' else False
        return is_descend

    def get_css_file(self):
        theme_name = self._get_theme_name()
        css_file = os.path.join(SHARED_DATA_DIR, 
                                     'html/theme/%s.css' % theme_name)
        return css_file

    def _get_theme_name(self):
        return SETTINGS.get_string('theme').lower()

    def on_setting_theme_changed(self, settings, key): # get_status_template
        theme_name = self._get_theme_name()
        template_file = os.path.join(SHARED_DATA_DIR, 
                                     'html/theme/%s.html' % theme_name)

        with open(template_file, 'r') as fh:
            file = fh.read()
        self.template = Template(unicode(file, 'utf-8', 'ignore'))
