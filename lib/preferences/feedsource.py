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

    def run(self):
        dialog = self.gui.get_object('feed_source')
        dialog.set_transient_for(self.parent)

        #source_widget = SourceComboBox(self.gui, source_list, self.data)

        combobox_target = TargetCombobox(self.gui, self.liststore_row)

        entry_argument = self.gui.get_object('entry_argument')
        if self.liststore_row:
            entry_argument.set_text(self.liststore_row[3])

        checkbutton_notification = self.gui.get_object('checkbutton_notification')
        if self.liststore_row and self.liststore_row[4]:
            status = bool(self.liststore_row[4].get('notification'))
            checkbutton_notification.set_active(status)

        # run
        response_id = dialog.run()

        v = { 
#            'source'  : source_widget.get_active_text(),
            'target'  : combobox_target.get_active_text(),
            'argument': entry_argument.get_text().decode('utf-8'),
            'options' : 
            {'notification': checkbutton_notification.get_active()},
        }

        # print v
        dialog.destroy()
#        if response_id == Gtk.ResponseType.OK:
#            SETTINGS_RECENTS.set_string('source', v['source'])
        return response_id , v

class TargetCombobox(object):

    def __init__(self, gui, feedliststore):
        self.feedliststore = feedliststore
        self.widget = gui.get_object('comboboxtext_target')

        self.label_list = sorted([x for x in TwitterAPIDict().keys()])

        for text in self.label_list:
            self.widget.append_text(text)

        num = self.label_list.index(feedliststore[2]) if feedliststore else 0
        self.widget.set_active(num)

    def get_active_text(self):
        label = self.label_list[self.widget.get_active()]
        return label
