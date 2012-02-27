import os
from ..constants import CONFIG_HOME
import json

from gi.repository import Gtk


class FilterListStore(Gtk.ListStore):

    """ListStore for Filters.

    0,      1,     2,      
    target, words, expire,
    """

    def __init__(self):
        super(FilterListStore, self).__init__(str, str, str)

        self.save = SaveFilterListStore()
        for entry in self.save.load():
            self.append(entry)

#        self.append(['body', u'yes', 'yes'])
#        self.append(['body', u'linux', 'yes'])

    def append(self, filter_entry, iter=None):
        new_iter = self.insert_before(iter, filter_entry)
        return new_iter

    def update(self, filter_entry, iter):
        new_iter = self.append(filter_entry, iter)
        self.remove(iter)

    def save_settings(self):
        self.save.save(self)

class SaveFilterListStore(object):

    def __init__(self):
        self.save_file = os.path.join(CONFIG_HOME, 'filters.json')

    def load(self):
        source_list = []

        if not self.has_save_file():
            return source_list

        with open(self.save_file, 'r') as f:
            entry = json.load(f)           

        for row in entry:
            data = [row['target'], row['words'], row['expiry']]
            source_list.append(data)

        return source_list

    def save(self, liststore):
        save_data = []

        for i, row in enumerate(liststore):
            save_temp = {'target': row[0],
                         'words': row[1],
                         'expiry': row[2]
                         }


            save_data.append(save_temp)

        #print save_data
        self.save_to_json(save_data)

    def save_to_json(self, save_data):
        "for defaultsource.py"
        with open(self.save_file, mode='w') as f:
            json.dump(save_data, f)      

    def has_save_file(self):
        "for defaultsource.py"
        return os.path.exists(self.save_file)
