#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import os
import json

from gi.repository import Gtk, GdkPixbuf

from window import MainWindow, FeedView
from plugins.twitter.api import TwitterAPIDict
from plugins.twitter.account import AuthorizedTwitterAPI
from constants import CONFIG_HOME

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
        self.authed_twitter = AuthorizedTwitterAPI()

#        target = [
##            {'source': 'Twitter', 'target': 'Home TimeLine', 'argument': ''},
#            {'target': 'User Stream', 'argument': ''},
##            {'target': 'Mentions', 'argument': ''},
#            {'target': 'List TimeLine', 'argument': 'yendo0206/friends'},
##            {'target': 'Track', 'option': {'params': ['Debian', 'Ubuntu', 'Gnome']} },
#            {'target': 'Track', 'argument': 'Debian, Ubuntu, Gnome'},
#            ]
#
#
#        for i in target:
#            self.append(i)
#

        self.save = SaveListStore()
        for entry in self.save.load():
            self.append(entry)

    def append(self, source, iter=None):

        api = self.api_dict[source['target']](self.authed_twitter)

        page = int(str(self.get_path(iter))) if iter else -1
        view = FeedView(self.window, api.name, page)

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

    def save_settings(self):
        self.save.save(self)

class SaveListStore(object):

    def __init__(self):

        self.save_file = os.path.join(CONFIG_HOME, 'feed_sources.json')

    def load(self):
        #weight = SETTINGS.get_int('default-weight')
        source_list = []

        if not self.has_save_file():
            return source_list

        with open(self.save_file, 'r') as f:
            entry = json.load(f)           

        for dir in entry:
            data = { 'target' : '', 'argument' : '',
                     'source' : 'Twitter', 
                     'options' : {} }

            for key, value in dir.items():
                if key in ['source', 'target', 'argument', 'weight']:
                    data[key] = value
                else:
                    data['options'][key] = value

            source_list.append(data)

        print source_list
        return source_list

    def save(self, liststore):
        data_list = ['source', 'target', 'argument']
        save_data = []

        for i, row in enumerate(liststore):
            save_temp = {}
            for num, key in enumerate(data_list):
                value = row[num+1] # liststore except icon.
                if value is not None:
                    save_temp[key] = value

            if row[4]: # liststore options
                for key, value in row[4].iteritems():
                    save_temp[key] = value
                    # print key, value
            save_data.append(save_temp)

        print save_data
        self.save_to_json(save_data)

    def save_to_json(self, save_data):
        "for defaultsource.py"
        with open(self.save_file, mode='w') as f:
            json.dump(save_data, f)      

    def has_save_file(self):
        "for defaultsource.py"
        return os.path.exists(self.save_file)
