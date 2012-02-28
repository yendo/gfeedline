import os
import json
from gi.repository import Gtk

from ..constants import CONFIG_HOME


class ListStoreBase(Gtk.ListStore):

    def save_settings(self):
        self.save.save(self)

class SaveListStoreBase(object):

    def __init__(self):
        self.save_file = os.path.join(CONFIG_HOME, self.SAVE_FILE)

    def save_to_json(self, save_data):
        "for defaultsource.py"
        with open(self.save_file, mode='w') as f:
            json.dump(save_data, f)      

    def has_save_file(self):
        "for defaultsource.py"
        return os.path.exists(self.save_file)
