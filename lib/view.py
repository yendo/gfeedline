#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import os
import urllib
import webbrowser

from twisted.internet import reactor
from gi.repository import Gtk, Gio, WebKit

from menu import SearchMenuItem, AddFilterMenuItem, ENTRY_POPUP_MENU
from utils.htmlentities import decode_html_entities
from utils.settings import SETTINGS_VIEW
from constants import SHARED_DATA_FILE, CONFIG_HOME
from updatewindow import UpdateWindow
from theme import FontSet

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

    def update(self, entry_dict, style='status', has_notify=False, 
               is_first_call=False, is_new_update=True):
        text = self.theme.template[style].substitute(entry_dict)

        if has_notify and not is_first_call:
            self.notification.notify(entry_dict)

        self.tab_label.set_sensitive(is_new_update)
        self.webview.update(text)

    def jump_to_bottom(self, is_bottom=True):
        self.webview.jump_to_bottom(is_bottom)

    def change_font(self, font, size):
        self.webview.change_font(font, size)

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
        self.dnd = DnDFile()

        self.load_uri("file://%s" % SHARED_DATA_FILE('html/base.html'))
        self.connect("navigation-policy-decision-requested", self.on_click_link)
        self.connect("populate-popup", self.on_popup, api)
        self.connect("hovering-over-link", self.on_hovering_over_link)
        self.connect('scroll-event', self.on_scroll_event)
        self.connect("document-load-finished", self.on_load_finished)

        self.connect("drag-data-received", self.on_drag_data_received)
        self.connect("drag-drop", self.on_drag_drop)

        SETTINGS_VIEW.connect("changed::theme", self.on_load_finished)

        scrolled_window.add(self)
        self.show_all()

    def on_drag_drop(self, widget, context, x, y, time, *args):
        if self.dnd.text or self.dnd.file:
            updatewindow = UpdateWindow(self)

            if self.dnd.text:
                updatewindow.text_buffer.set_text(self.dnd.text)
            elif self.dnd.file:
                updatewindow.set_upload_media(self.dnd.file)

            self.dnd.clear()

    def on_drag_data_received(self, widget, context, x, y, selection, info, time):
        self.dnd.set(info, selection)

    def update(self, text=None):
        text = text.replace('\n', '')
        is_ascending_js = self._bool_js(self.theme.is_ascending())
        is_paused_js = self._bool_js(self.scroll.is_paused)

        js = 'append("%s", %s, %s)' % (text, is_ascending_js, is_paused_js)
        # print js
        self.execute_script(js)

        if not self.scroll.is_paused:
            js = 'scrollToBottom(%s)' % is_ascending_js
            reactor.callLater(0.2, self.execute_script, js)

    def jump_to_bottom(self, is_bottom=True):
        self.execute_script('jumpToBottom(%s)' % self._bool_js(is_bottom))

    def clear_buffer(self):
        self.execute_script('clearBuffer()')

    def change_font(self, family=None, size=None):
        if not family and not size:
            family = FontSet().zoom_default()

        js = 'changeFont("%s")' % family
        self.execute_script(js)

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
                default_menu.append(menuitem(self.link_on_webview.uri, api,
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

        theme_css = self.theme.get_css_file()
        custom_css = os.path.join(CONFIG_HOME, 'theme/custom.css')
        js =  'changeCSS("%s", "%s");' % ('theme', theme_css)
        js += 'changeCSS("%s", "%s");' % ('custom', custom_css)
        self.execute_script(js)

        self.change_font()

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

class DnDFile(object):

    def __init__(self):
        self.clear()

    def clear(self):
        self.file = None
        self.text = None

    def set(self, info, selection):
        #text, image_file = self.parse_dnd_object(info, selection)
        text, image_file = DnDSelection.parse(info, selection)

        if info == 1:
            self.file = image_file
        elif info == 4 and selection.get_data():
            self.text = text

class DnDSelection(object):

    @classmethod
    def parse(self, info, selection, need_decode=False):
        text = image_file = None
        data = selection.get_data()

        if info == 1:
            uri = data.rstrip()
            filename = uri.replace('file://', '')
            mime_type = Gio.content_type_guess(filename, None)[0]

            target = ('image/jpeg', 'image/png', 'image/gif')
            image_file = filename if mime_type in target else None

        elif info == 4 and data:
            if need_decode:
                data = data.decode('utf16', 'replace')

            uri, title = data.split('\n')
            link_style = "%(title)s %(uri)s"
            text = link_style % {'title': title, 'uri': uri} if title else uri

        return text, image_file
