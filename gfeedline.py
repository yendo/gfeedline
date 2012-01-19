#!/usr/bin/python
#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

from lib.utils import gtk3reactor
gtk3reactor.install()
from twisted.internet import reactor

from gi.repository import Gtk
from lib.window import MainWindow, FeedView
from lib.plugins.twitter.api import *

class FeedListStore(Gtk.ListStore):

    """ListStore for Feed Sources.

    0,      1,        2,
    target, argument, api_object
    """

    def __init__(self):
        super(FeedListStore, self).__init__(object, object, object)
        self.window = MainWindow()
        self.api_token = TwitterAPIToken().api

        target = [
            {'api': 'Home TimeLine', 'argument': {}},
            {'api': 'User Stream', 'argument': []},
#            {'api': 'Mentions', 'argument': {}},
            {'api': 'List TimeLine', 'argument': 
             {'slug':'friends', 'owner_screen_name': 'yendo0206'}},
            {'api': 'Track', 'argument': ['Debian', 'Ubuntu']},
            ]
        
        for i in target:
            self.append(i)

    def append(self, source, iter=None):

        api = self.api_token[source['api']]()
        view = FeedView(self.window, api.name)
        obj = api.create_obj(view, source['argument'])

        list = [source['api'], source['argument'], obj]
        new_iter = self.insert_before(iter, list)

        interval = 40 if api.name == 'Home TimeLine' else 180
        obj.start(interval)

        return new_iter

if __name__ == '__main__':

    liststore = FeedListStore()
    reactor.run()
