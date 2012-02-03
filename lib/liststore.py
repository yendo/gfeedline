#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

import os
import json

from gi.repository import Gtk, GdkPixbuf

from window import MainWindow, FeedNotebook, FeedView
from plugins.twitter.api import TwitterAPIDict
from plugins.twitter.account import AuthorizedTwitterAccount
from constants import CONFIG_HOME

class FeedListStore(Gtk.ListStore):

    """ListStore for Feed Sources.

    0,    1,      2,        3,      4,            5,           6
    icon, source, target, argument, options_dict, account_obj, api_obj

    0,     1,    2,      3,    4,      5,        6,            7,           8
    group, icon, source, name, target, argument, options_dict, account_obj, api_obj
    """

    def __init__(self):
        super(FeedListStore, self).__init__(
            str, GdkPixbuf.Pixbuf, str, str, str, str, object, object, object)
        self.window = MainWindow(self)
        self.api_dict = TwitterAPIDict()
        self.twitter_account = AuthorizedTwitterAccount()

        self.column = {}

        self.save = SaveListStore()
        for entry in self.save.load():
            self.append(entry)

    def append(self, source, iter=None):

        api = self.api_dict[source['target']](self.twitter_account)

        group_name = source.get('group')
        if group_name in self.column:
            notebook = self.column[group_name]
        else:
            notebook = FeedNotebook(self.window.hbox)
            self.column[group_name] = notebook

        page = int(str(self.get_path(iter))) if iter else -1
        view = FeedView(self.window, notebook, api.name, page)

        options_dict = source.get('options')
        api_obj = api.create_obj(view, source.get('argument'), options_dict)

        list = [source.get('group'),
                GdkPixbuf.Pixbuf(),
                source.get('source'),
                source.get('name'),
                source['target'], # API 
                source.get('argument'), 
                options_dict,
                self.twitter_account, # account_obj
                api_obj]

        new_iter = self.insert_before(iter, list)

        interval = 40 if api.name == 'Home TimeLine' else 180
        api_obj.start(interval)

        return new_iter

    def update(self, source, iter):
        # compare 'target' & 'argument'
        old = [self.get_value(iter, x).decode('utf-8') 
               for x in range(4, 6)] # liststore object
        new = [source.get(x) for x in ['target', 'argument']]

        if old == new:
            options = source.get('options', {})
            self.set_value(iter, 6, options) # liststore object

            api_obj = self.get_value(iter, 8) # liststore object
            api_obj.options = options
            new_iter = iter
        else:
            new_iter = self.append(source, iter)
            self.remove(iter)

        return new_iter

    def remove(self, iter):
        obj = self.get_value(iter, 8) # stop object, liststore object
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
                if key in ['group', 'source', 'target', 'argument', 'weight']:
                    data[key] = value
                else:
                    data['options'][key] = value

            source_list.append(data)

        # print source_list
        return source_list

    def save(self, liststore):
        data_list = ['source', 'name', 'target', 'argument']
        save_data = []

        for i, row in enumerate(liststore):
            save_temp = {'group': row[0]} # fixme

            for num, key in enumerate(data_list):
                value = row[num+2] # liststore except icon.
                if value is not None:
                    save_temp[key] = value

            if row[6]: # liststore options
                for key, value in row[6].iteritems():
                    save_temp[key] = value
                    # print key, value
            save_data.append(save_temp)

        # print save_data
        self.save_to_json(save_data)

    def save_to_json(self, save_data):
        "for defaultsource.py"
        with open(self.save_file, mode='w') as f:
            json.dump(save_data, f)      

    def has_save_file(self):
        "for defaultsource.py"
        return os.path.exists(self.save_file)
