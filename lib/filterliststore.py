import os
import json
from datetime import datetime

from gi.repository import Gtk
from utils.liststorebase import ListStoreBase, SaveListStoreBase


class FilterColumn(object):

    (TARGET, WORD, EXPIRE_TIME, EXPIRE_UNIT, EXPIRE_EPOCH) = range(5)

class FilterListStore(ListStoreBase):

    """ListStore for Filters.

    0,      1,    2,           3,           4,
    target, word, expire days, expire unit, expire datetime
    """

    def __init__(self):
        super(FilterListStore, self).__init__(str, str, str, str, int)

        self.save = SaveFilterListStore()
        for entry in self.save.load():
            self.append(entry)

    def append(self, entry, iter=None):
        new_iter = self.insert_before(iter, entry)
        return new_iter

    def update(self, entry, iter):
        new_iter = self.append(entry, iter)
        self.remove(iter)
        return new_iter

class SaveFilterListStore(SaveListStoreBase):

    SAVE_FILE = 'filters.json'

    def load(self):
        source_list = []

        if not self.has_save_file():
            return source_list

        with open(self.save_file, 'r') as f:
            entry = json.load(f)           

        for row in entry:
            now = datetime.now()
            future = datetime.fromtimestamp(row['expire_datetime'])
            expire_timedelta = future - now

            expiration = '' if not row['expire_datetime'] \
                else expire_timedelta.days if expire_timedelta.days \
                else expire_timedelta.seconds / 3600

            expiration_unit = '' if not row['expire_datetime'] \
                else "days" if expire_timedelta.days else "hours"

            data = [row['target'], row['word'], 
                    str(expiration), str(expiration_unit), 
                    row['expire_datetime']]
            source_list.append(data)

        return source_list

    def save(self, liststore):
        save_data = []

        for row in liststore:
            save_temp = {'target': row[FilterColumn.TARGET],
                         'word': row[FilterColumn.WORD],
                         'expire_datetime': row[FilterColumn.EXPIRE_EPOCH]
                         }

            save_data.append(save_temp)

        #print save_data
        self.save_to_json(save_data)
