import os

from gi.repository import Gtk
from ..plugins.twitter.api import TwitterAPIDict

class FeedSourceDialog(object):
    """Feed Source Dialog"""

    def __init__(self, parent, liststore_row=None):
        self.gui = Gtk.Builder()
        self.gui.add_from_file(os.path.abspath('share/feedsource.glade'))

        self.parent = parent
        self.liststore_row = liststore_row

    def run(self):
        dialog = self.gui.get_object('feed_source')
        dialog.set_transient_for(self.parent)


        combobox_target = TargetCombobox(self.gui, self.liststore_row)
        


        #source_widget = SourceComboBox(self.gui, source_list, self.data)
        #argument_widget = ArgumentEntry(self.gui, self.data)
        #weight_widget = WeightEntry(self.gui, self.data)

        # run
        response_id = dialog.run()

        v = { 
#            'source'  : source_widget.get_active_text(),
            'target'  : combobox_target.get_active_text(),
#            'argument': argument_widget.get_text(),
#            'options' : source_widget.ui.get_options() 
        }

#        print v
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
