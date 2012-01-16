#!/usr/bin/python
#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

from lib import gtk3reactor
gtk3reactor.install()
from twisted.internet import reactor

from gi.repository import Gtk
from lib.window import MainWindow, FeedView
from lib.twitter import *

class FeedListStore(Gtk.ListStore):

    """ListStore for Feed Sources.

    0,      1,        2,
    target, argument, api_object
    """

    def __init__(self):
        super(FeedListStore, self).__init__(object, object, object)
        self.window = MainWindow()

        target = [
            {'api': TwitterOauth.home_timeline, 'argument': {}},
            {'api': TwitterOauth.mentions, 'argument': {}},
            {'api': TwitterOauth.list_timeline, 'argument': 
             {'slug':'friends', 'owner_screen_name': 'yendo0206'}}
            ]
        
        for i in target:
            self.append(i)

    def append(self, source, iter=None):
        view = FeedView(self.window)
        obj = TwitterAPI(source['api'], view, source['argument'])

        list = [source['api'], source['argument'], obj]
        new_iter = self.insert_before(iter, list)

        interval = 40 if source['api'] == TwitterOauth.home_timeline else 180
        obj.start(interval)

        return new_iter

if __name__ == '__main__':

    liststore = FeedListStore()
    reactor.run()
