import os

from gi.repository import Gtk
from ..plugins.twitter.api import TwitterAPIDict
from ..constants import SHARED_DATA_DIR

class FeedSourceDialog(object):
    """Feed Source Dialog"""

    def __init__(self, parent, liststore_row=None):
        self.gui = Gtk.Builder()
        self.gui.add_from_file(os.path.join(SHARED_DATA_DIR, 'feedsource.glade'))

        self.parent = parent
        self.liststore_row = liststore_row

        self.combobox_target = TargetCombobox(self.gui, self.liststore_row)
        self.label_argument = self.gui.get_object('label_argument')
        self.entry_argument = self.gui.get_object('entry_argument')

        self.on_comboboxtext_target_changed()
        self.gui.connect_signals(self)

    def run(self):
        dialog = self.gui.get_object('feed_source')
        dialog.set_transient_for(self.parent)

        #source_widget = SourceComboBox(self.gui, source_list, self.data)

        if self.liststore_row:
            self.entry_argument.set_text(self.liststore_row[3])

        checkbutton_notification = self.gui.get_object('checkbutton_notification')
        if self.liststore_row and self.liststore_row[4]:
            status = bool(self.liststore_row[4].get('notification')) # liststore obj
            checkbutton_notification.set_active(status)

        # run
        response_id = dialog.run()

        v = { 
#            'source'  : source_widget.get_active_text(),
            'target'  : self.combobox_target.get_active_text(),
            'argument': self.entry_argument.get_text().decode('utf-8'),
            'options' : 
            {'notification': checkbutton_notification.get_active()},
        }

        # print v
        dialog.destroy()
#        if response_id == Gtk.ResponseType.OK:
#            SETTINGS_RECENTS.set_string('source', v['source'])
        return response_id , v

    def on_comboboxtext_target_changed(self, *args):
        api_name = self.combobox_target.get_active_text()
        api_class = TwitterAPIDict().get(api_name)
        status= api_class().has_argument

        self.label_argument.set_sensitive(status)
        self.entry_argument.set_sensitive(status)

class TargetCombobox(object):

    def __init__(self, gui, feedliststore):
        self.feedliststore = feedliststore
        self.widget = gui.get_object('comboboxtext_target')

        self.label_list = sorted([x for x in TwitterAPIDict().keys()])

        for text in self.label_list:
            self.widget.append_text(text)

        num = self.label_list.index(feedliststore[2]) \ # listsire obj
            if feedliststore else 0
        self.widget.set_active(num)

    def get_active_text(self):
        label = self.label_list[self.widget.get_active()]
        return label
