#!/usr/bin/python
#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

from lib.utils import gtk3reactor
gtk3reactor.install()
from twisted.internet import reactor

from gi.repository import Gtk, GdkPixbuf
from lib.window import MainWindow, FeedView
from lib.plugins.twitter.api import TwitterAPIDict
from lib.plugins.twitter.account import AuthorizedTwitterAPI


class FeedListStore(Gtk.ListStore):

    """ListStore for Feed Sources.

    0,    1,      2,        3,      4,           5,           6
    icon, source, target, argument, options_obj, account_obj, api_obj
    """

    def __init__(self):
        super(FeedListStore, self).__init__(
            GdkPixbuf.Pixbuf, str, str, str, object, object, object)
        self.window = MainWindow(self)
        self.api_dict = TwitterAPIDict()

        target = [
#            {'source': 'Twitter', 'api': 'Home TimeLine', 'argument': ''},
            {'api': 'User Stream', 'argument': ''},
#            {'api': 'Mentions', 'argument': ''},
            {'api': 'List TimeLine', 'option': 
             {'params':
                  {'slug':'friends', 'owner_screen_name': 'yendo0206'}}},
            {'api': 'Track', 'option': {'params': ['Debian', 'Ubuntu', 'Gnome']} },
            ]

        self.authed_twitter = AuthorizedTwitterAPI()

        for i in target:
            self.append(i)

    def append(self, source, iter=None):

        api = self.api_dict[source['api']](self.authed_twitter)
        view = FeedView(self.window, api.name)
        options_obj = source.get('option')
        api_obj = api.create_obj(view, source.get('argument'), options_obj)

        list = [GdkPixbuf.Pixbuf(),
                source.get('source'),
                source['api'], 
                source.get('argument'), 
                options_obj,
                self.authed_twitter, # account_obj
                api_obj]

        new_iter = self.insert_before(iter, list)

        interval = 40 if api.name == 'Home TimeLine' else 180
        api_obj.start(interval)

        return new_iter

if __name__ == '__main__':

    liststore = FeedListStore()
    reactor.run()
