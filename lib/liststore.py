#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

from gi.repository import Gtk, GdkPixbuf
from window import MainWindow, FeedView
from plugins.twitter.api import TwitterAPIDict
from plugins.twitter.account import AuthorizedTwitterAPI


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
#            {'source': 'Twitter', 'target': 'Home TimeLine', 'argument': ''},
            {'target': 'User Stream', 'argument': ''},
#            {'target': 'Mentions', 'argument': ''},
            {'target': 'List TimeLine', 'argument': 'yendo0206/friends'},
#            {'target': 'Track', 'option': {'params': ['Debian', 'Ubuntu', 'Gnome']} },
            {'target': 'Track', 'argument': 'Debian, Ubuntu, Gnome'},
            ]

        self.authed_twitter = AuthorizedTwitterAPI()

        for i in target:
            self.append(i)

    def append(self, source, iter=None):

        api = self.api_dict[source['target']](self.authed_twitter)
        view = FeedView(self.window, api.name)
        options_obj = source.get('option')
        api_obj = api.create_obj(view, source.get('argument'), options_obj)

        list = [GdkPixbuf.Pixbuf(),
                source.get('source'),
                source['target'], # API 
                source.get('argument'), 
                options_obj,
                self.authed_twitter, # account_obj
                api_obj]

        new_iter = self.insert_before(iter, list)

        interval = 40 if api.name == 'Home TimeLine' else 180
        api_obj.start(interval)

        return new_iter

    def remove(self, iter):
        obj = self.get_value(iter, 6) # stop object, liststore object
        obj.exit()
        del obj
        super(FeedListStore, self).remove(iter)
