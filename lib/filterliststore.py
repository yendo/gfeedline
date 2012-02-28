import json
from datetime import datetime
import time

from gi.repository import Gtk
from twisted.internet import reactor
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
        self.expire()

    def append(self, entry, iter=None):
        new_iter = self.insert_before(iter, entry)
        return new_iter

    def update(self, entry, iter):
        new_iter = self.append(entry, iter)
        self.remove(iter)
        return new_iter

    def expire(self):
        now = int(time.mktime(datetime.now().timetuple()))
        for i, entry in enumerate(self):
            if entry[FilterColumn.EXPIRE_EPOCH] - now < 0:
                self.remove(self.get_iter(i))

        reactor.callLater(300, self.expire)

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
            future = datetime.fromtimestamp(row['expire_epoch'])
            timedelta = future - now

            if not row['expire_epoch']:
                expiration_value = ''
            elif timedelta.days:
                expiration_value = timedelta.days
            elif timedelta.seconds >= 3600:
                expiration_value = timedelta.seconds / 3600
            else:
                expiration_value = round(timedelta.seconds / 3600.0, 1)
                if expiration_value == 1.0:
                    expiration_value = 1

            expiration_unit = '' if not row['expire_epoch'] \
                else "days" if timedelta.days else "hours"

            data = [row['target'], row['word'], 
                    str(expiration_value), str(expiration_unit), 
                    row['expire_epoch']]
            source_list.append(data)

        return source_list

    def save(self, liststore):
        save_data = []

        for row in liststore:
            save_temp = {'target': row[FilterColumn.TARGET],
                         'word': row[FilterColumn.WORD],
                         'expire_epoch': row[FilterColumn.EXPIRE_EPOCH]
                         }

            save_data.append(save_temp)

        #print save_data
        self.save_to_json(save_data)
