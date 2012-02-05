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
from plugins.twitter.output import TwitterOutputFactory
from plugins.twitter.account import AuthorizedTwitterAccount
from constants import CONFIG_HOME, Column
from utils.settings import SETTINGS


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

        self.save = SaveListStore()
        for entry in self.save.load():
            self.append(entry)

    def append(self, source, iter=None):
        api = self.api_dict[source['target']](self.twitter_account)

        is_multi_column = SETTINGS.get_boolean('multi-column')
        notebook = self.window.get_notebook(source.get('group'), is_multi_column)

        page = int(str(self.get_path(iter))) if iter else -1
        view = FeedView(self.window, notebook, api.name, page)

        factory = TwitterOutputFactory()
        api_obj = factory.create_obj(api, view, 
                                     source.get('argument'), source.get('options'))

        list = [source.get('group'),
                GdkPixbuf.Pixbuf(),
                source.get('source'),
                source.get('name'),
                source['target'], # API 
                source.get('argument'), 
                source.get('options'),
                self.twitter_account, # account_obj
                api_obj]

        new_iter = self.insert_before(iter, list)

        interval = 40 if api.name == 'Home TimeLine' else 180
        api_obj.start(interval)

        return new_iter

    def update(self, source, iter):
        # compare 'target' & 'argument'
        old = [self.get_value(iter, x).decode('utf-8') 
               for x in range(Column.TARGET, Column.OPTIONS)]
        new = [source.get(x) for x in ['target', 'argument']]

        if old == new:
            new_iter = iter

            api_obj = self.get_value(iter, Column.API)
            api_obj.options = source.get('options', {})
            self.set_value(iter, Column.OPTIONS, api_obj.options)

            old_group = self.get_value(iter, Column.GROUP).decode('utf-8')
            new_group = source.get('group') # FIXME
            self.set_value(iter, Column.GROUP, new_group)

            if old_group != new_group:
                notebook = self.window.get_notebook(new_group, True)
                api_obj.view.move(notebook)
        else:
            new_iter = self.append(source, iter)
            self.remove(iter)

        return new_iter

    def remove(self, iter):
        obj = self.get_value(iter, Column.API)
        obj.exit()
        del obj
        super(FeedListStore, self).remove(iter)

    def save_settings(self):
        self.save.save(self)

class SaveListStore(object):

    def __init__(self):

        self.save_file = os.path.join(CONFIG_HOME, 'feed_sources.json')

    def load(self):
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
            save_temp = {'group': row[Column.GROUP]} # fixme

            for num, key in enumerate(data_list):
                value = row[num+Column.SOURCE] # liststore except icon.
                if value is not None:
                    save_temp[key] = value

            if row[Column.OPTIONS]:
                for key, value in row[Column.OPTIONS].iteritems():
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
