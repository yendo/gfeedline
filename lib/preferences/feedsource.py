import os

from gi.repository import Gtk

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

        #source_list = plugin_liststore.available_list()


        combobox_target = TargetCombobox(self.gui, self.liststore_row)
        


        #source_widget = SourceComboBox(self.gui, source_list, self.data)
        #argument_widget = ArgumentEntry(self.gui, self.data)
        #weight_widget = WeightEntry(self.gui, self.data)

        # run
        response_id = dialog.run()

        v = {}
#        v = { 'source'  : source_widget.get_active_text(),
#              'target'  : source_widget.get_target(),
#              'argument': argument_widget.get_text(),
#              'weight'  : weight_widget.get_value(),
#              'options' : source_widget.ui.get_options() }

        dialog.destroy()
#        if response_id == Gtk.ResponseType.OK:
#            SETTINGS_RECENTS.set_string('source', v['source'])
        return response_id , v


class TargetCombobox(object):

    def __init__(self, gui, feedliststore):
        self.feedliststore = feedliststore
        self.widget = gui.get_object('comboboxtext_target')

        label_list = ['a','b','c']
        for text in label_list:
            self.widget.append_text(text)
