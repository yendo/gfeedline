#!/usr/bin/python
#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

from lib import gtk3reactor
gtk3reactor.install()
from twisted.internet import reactor

import os
import sys
from BeautifulSoup import BeautifulStoneSoup
from lib.usercolor import UserColor

from gi.repository import Gtk, WebKit, GLib, GObject

import dateutil.parser
from twittytwister import twitter
from oauth import oauth

consumer = oauth.OAuthConsumer(sys.argv[1], sys.argv[2])
token = oauth.OAuthToken(sys.argv[3], sys.argv[4])

TwitterOauth = twitter.Twitter(consumer=consumer, token=token)
TwitterFeedOauth = twitter.TwitterFeed(consumer=consumer, token=token)


class MainWindow(object):

    def __init__(self):

        gui = Gtk.Builder()
        gui.add_from_file(os.path.abspath('gfeedline.glade'))

        self.window = window = gui.get_object('window1')
        self.notebook = gui.get_object('notebook1')
        menubar = gui.get_object('menubar1')
        self.sw = gui.get_object('scrolledwindow1')

        window.resize(480, 600)
        window.connect("delete-event", self.stop)
        window.show_all()
        menubar.hide()

    def append_page(self):
        sw1 = FeedScrolledWindow()
        main.notebook.append_page(sw1, None)
        view1 = FeedWebView(sw1)
        

    def stop(self, *args):
        reactor.stop()

class FeedScrolledWindow(Gtk.ScrolledWindow):

    def __init__(self):
        super(FeedScrolledWindow, self).__init__()

        self.set_margin_top(4)
        self.set_margin_bottom(4)
        self.set_margin_right(4)
        self.set_margin_bottom(4)

        self.set_shadow_type(Gtk.ShadowType.IN)
        self.show()

class FeedWebView(WebKit.WebView):

    def __init__(self, scrolled_window):
        super(FeedWebView, self).__init__()
        self.load_uri("file://%s" % os.path.abspath('base.html')) 

        scrolled_window.add(self)
        self.show_all()

    def update(self, text=None):
        text = text.replace('\n', '<br>')
        js = 'append("%s")' % text
        # print js
        self.execute_script(js)

class TwitterTime(object):

    def __init__(self, utc_str):
        dt = dateutil.parser.parse(utc_str)
        self.datetime = dt.replace(tzinfo=dateutil.tz.tzutc()
                                   ).astimezone(dateutil.tz.tzlocal())

    def get_local_time(self):
        return self.datetime.strftime('%H:%M:%S')

class TwitterAPI(object):

    def __init__(self, api, view=None):
        self.all_entries = []
        self.last_id = 0
        self.view = view.webview
        self.api = api

    def got_entry(self, msg, *args):
        self.all_entries.append(msg)

    def conv(self, text):
        return BeautifulStoneSoup(
            text, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)

    def print_all_entries(self):
        for entry in reversed(self.all_entries):
            self.print_entry(entry)
        self.all_entries = []

    def print_entry(self, entry):
        time = TwitterTime(entry.created_at)

        text = ("<div style='line-height: 1.4;'>"
                "<span style='color: gray'>%s</span> "
                "<span style='color: #%s; font-weight: bold;'>%s</span> " 
                "%s"
                "</div>"
                ) % (
            time.get_local_time(), 
            user_color.get(entry.user.id), entry.user.screen_name,  
            self.conv(entry.text))

        #print text
        self.last_id = entry.id
        self.view.update(text)

    def error(self, e):
        print e

    def start(self):
        params = {'since_id': str(self.last_id)} if self.last_id else {}
        self.api(self.got_entry, params).\
            addErrback(self.error).\
            addBoth(lambda x: self.print_all_entries())

        print TwitterOauth.rate_limit_remaining
        # print TwitterOauth.rate_limit_limit
        # print TwitterOauth.rate_limit_reset

        GLib.timeout_add_seconds(30, self.start)

class TwitterFeedAPI(TwitterAPI):

    def got_entry(self, msg, *args):
        self.print_entry(msg)

    def conv(self, text):
        return text

    def start(self):
        self.api(self.got_entry, ['linux']).\
            addErrback(self.error)#.\
#            addBoth(lambda x: self.print_entry())


class FeedView(object):

    def __init__(self):
        sw = FeedScrolledWindow()
        main.notebook.append_page(sw, None)
        self.webview = FeedWebView(sw)

class FeedListStore(Gtk.ListStore):

    """ListStore for Feed Sources.

    0,      1,        2,
    target, argument, api_object
    """

    def __init__(self):
        super(FeedListStore, self).__init__(object, str, object)

        target = [{'api': TwitterOauth.home_timeline, 'argument': ''},
                  {'api': TwitterOauth.mentions, 'argument': ''}]
        
        for i in target:
            self.append(i)


    def append(self, source, iter=None):
        view = FeedView()
        obj = TwitterAPI(source['api'], view)

        list = [source['api'], '', obj]
        new_iter = self.insert_before(iter, list)
        obj.start()

        return new_iter

if __name__ == '__main__':
    user_color = UserColor()
    main = MainWindow()

    liststore = FeedListStore()
    reactor.run()
