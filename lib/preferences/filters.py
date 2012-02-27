import os
import json
import time
from datetime import datetime, timedelta

from gi.repository import Gtk
from ..constants import SHARED_DATA_FILE, CONFIG_HOME


class FilterDialog(object):
    """Filter Dialog"""

    def __init__(self, parent, liststore_row=None):
        self.gui = Gtk.Builder()
        self.gui.add_from_file(SHARED_DATA_FILE('filters.glade'))

        self.parent = parent
        self.liststore_row = liststore_row

        self.combobox_target = self.gui.get_object('comboboxtext_target')
        self.combobox_target.set_active(0)
        self.combobox_model = self.combobox_target.get_model()
        self.entry_word = self.gui.get_object('entry_word')
        self.spinbutton_expiry= self.gui.get_object('spinbutton_expiry')

#        self.on_comboboxtext_target_changed()
        self.gui.connect_signals(self)

    def run(self):
        dialog = self.gui.get_object('filter_dialog')
        dialog.set_transient_for(self.parent)

        #source_widget = SourceComboBox(self.gui, source_list, self.data)

        if self.liststore_row:

            labels = [i[0] for i in self.combobox_model]
            target = labels.index(self.liststore_row[0])
            self.combobox_target.set_active(target)

            self.entry_word.set_text(self.liststore_row[1])

            expire_epoch = int(self.liststore_row[3])
            future = datetime.fromtimestamp(expire_epoch)
            now = datetime.now()
            delta = future - now

            self.spinbutton_expiry.set_value(delta.days)

        # run
        response_id = dialog.run()

        expire_days = self.spinbutton_expiry.get_value_as_int()
        now = datetime.now()
        expire_days = timedelta(days=expire_days)
        future = now + expire_days
        expire_epoch = int(time.mktime(future.timetuple()))

        expiration =  "%s days" % expire_days.days if expire_days.days \
            else "%s hours" % (expire_days.seconds / 3600)


        v = [
            self.combobox_model[self.combobox_target.get_active()][0],
            self.entry_word.get_text().decode('utf-8'),
            expiration, expire_epoch,
        ]



        print v
        dialog.destroy()
#        if response_id == Gtk.ResponseType.OK:
#            SETTINGS_RECENTS.set_string('source', v['source'])
        return response_id , v

class FilterListStore(Gtk.ListStore):

    """ListStore for Filters.

    0,      1,     2,           3,
    target, words, expire days, expire datetime
    """

    def __init__(self):
        super(FilterListStore, self).__init__(str, str, str, int)

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
            now = datetime.now()
            future = datetime.fromtimestamp(row['expire_datetime'])
            expire_days = future - now
            expiration =  "%s days" % expire_days.days if expire_days.days \
                else "%s hours" % (expire_days.seconds / 3600)

            print expiration

            data = [row['target'], row['words'], 
                    str(expiration), row['expire_datetime']]
            source_list.append(data)

        return source_list

    def save(self, liststore):
        save_data = []

        for i, row in enumerate(liststore):
            save_temp = {'target': row[0],
                         'words': row[1],
                         'expire_datetime': row[3]
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
