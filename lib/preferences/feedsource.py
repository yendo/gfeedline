from gi.repository import Gtk

from ..plugins.twitter.api import TwitterAPIDict
from ..constants import SHARED_DATA_FILE, Column


class FeedSourceDialog(object):
    """Feed Source Dialog"""

    def __init__(self, parent, liststore_row=None):
        self.gui = Gtk.Builder()
        self.gui.add_from_file(SHARED_DATA_FILE('feedsource.glade'))

        self.parent = parent
        self.liststore_row = liststore_row

        self.combobox_target = TargetCombobox(self.gui, self.liststore_row)
        self.entry_name = self.gui.get_object('entry_name')
        self.label_argument = self.gui.get_object('label_argument')
        self.entry_argument = ArgumentEntry(self.gui, self.combobox_target)
        self.entry_group = self.gui.get_object('entry_group')

        self.button_ok = self.gui.get_object('button_ok')
        self.button_ok.set_sensitive(False)

        self.on_comboboxtext_target_changed()
        self.gui.connect_signals(self)

    def run(self):
        dialog = self.gui.get_object('feed_source')
        dialog.set_transient_for(self.parent)

        #source_widget = SourceComboBox(self.gui, source_list, self.data)

        if self.liststore_row:
            self.entry_name.set_text(
                self.liststore_row[Column.NAME])
            self.entry_argument.set_text(
                self.liststore_row[Column.ARGUMENT])
            self.entry_group.set_text(self.liststore_row[Column.GROUP])

        checkbutton_notification = self.gui.get_object('checkbutton_notification')
        if self.liststore_row and self.liststore_row[Column.TARGET]:
            status = bool(self.liststore_row[Column.OPTIONS].get('notification'))
            checkbutton_notification.set_active(status)

        # run
        response_id = dialog.run()

        v = { 
#            'source'  : source_widget.get_active_text(),
            'name' : self.entry_name.get_text().decode('utf-8'),
            'target' : self.combobox_target.get_active_text(), #.decode('utf-8'),
            'argument' : self.entry_argument.get_text().decode('utf-8'),
            'group': self.entry_group.get_text().decode('utf-8'),
            'options' : 
            {'notification': checkbutton_notification.get_active()},
        }

        # print v
        dialog.destroy()
#        if response_id == Gtk.ResponseType.OK:
#            SETTINGS_RECENTS.set_string('source', v['source'])
        return response_id , v

    def on_comboboxtext_target_changed(self, *args):
        status = self.combobox_target.has_argument_entry_enabled()
        self.label_argument.set_sensitive(status)
        self.entry_argument.set_sensitive(status)
        self.button_ok.set_sensitive(not status)

    def on_entry_argument_changed(self, entry, *args):
        has_entry = entry.get_text_length() > 0
        self.button_ok.set_sensitive(has_entry)

class TargetCombobox(object):

    def __init__(self, gui, feedliststore):
        self.feedliststore = feedliststore
        self.widget = gui.get_object('comboboxtext_target')

        self.label_list = sorted([x for x in TwitterAPIDict().keys()])

        for text in self.label_list:
            self.widget.append_text(text)

        num = self.label_list.index(
            feedliststore[Column.TARGET].decode('utf-8')) if feedliststore else 0
        self.widget.set_active(num)

    def get_active_text(self):
        label = self.label_list[self.widget.get_active()]
        return label

    def has_argument_entry_enabled(self):
        api_name = self.get_active_text()
        api_class = TwitterAPIDict().get(api_name)
        status = api_class.has_argument

        return status

class ArgumentEntry(object):

    def __init__(self, gui, combobox_target):
        self.widget = gui.get_object('entry_argument')
        self.combobox_target = combobox_target

    def get_text(self):
        has_argument = self.combobox_target.has_argument_entry_enabled() 
        return self.widget.get_text() if has_argument else ''

    def set_text(self, text):
        self.widget.set_text(text)

    def set_sensitive(self, status):
        self.widget.set_sensitive(status)

class FeedSourceTreeview(object):

    def __init__(self, gui, mainwindow):
        self.gui = gui
        self.liststore = mainwindow.liststore

        self.treeview = treeview = gui.get_object('feedsourcetreeview')
        treeview.set_model(self.liststore)

        treeview.set_headers_clickable(False) # Builder bug?
        treeview.connect("drag-begin", self.on_drag_begin)
        treeview.connect("drag-end", self.on_drag_end, mainwindow)

    def get_selection(self):
        return self.treeview.get_selection()

    def set_cursor_to(self, iter):
        model = self.treeview.get_model()
        row = model.get_path(iter)
        self.treeview.set_cursor(row, None, False)

    def on_drag_begin(self, treeview, dragcontext):
        treeselection = treeview.get_selection()
        model, iter = treeselection.get_selected()

        self.api_obj = model.get_value(iter, Column.API)
        self.group = model.get_value(iter, Column.GROUP).decode('utf-8')
        self.old_page = model.get_group_page(self.group)

    def on_drag_end(self, treeview, dragcontext, mainwindow):
        treeselection = treeview.get_selection()
        model, iter = treeselection.get_selected()

        if not iter:
            self.gui.get_object('button_feed_prefs').set_sensitive(False)
            self.gui.get_object('button_feed_del').set_sensitive(False)

        all_obj = [x[Column.API] for x in model 
                   if x[Column.GROUP].decode('utf-8') == self.group]
        page = all_obj.index(self.api_obj)

        notebook = mainwindow.column[self.group]
        notebook.reorder_child(self.api_obj.view, page) # FIXME

        new_page = model.get_group_page(self.group)

        if self.old_page != new_page:
            mainwindow.column.hbox.reorder_child(notebook, new_page)

class FeedSourceAction(object):

    DIALOG = FeedSourceDialog
    TREEVIEW = FeedSourceTreeview
    BUTTON_PREFS = 'button_feed_prefs'
    BUTTON_DEL = 'button_feed_del'

    def __init__(self, gui, mainwindow, liststore, preferences):
        self.liststore = liststore
        self.preferences = preferences
        self.feedsource_treeview = self.TREEVIEW(gui, mainwindow)

        self.button_prefs = gui.get_object(self.BUTTON_PREFS)
        self.button_del = gui.get_object(self.BUTTON_DEL)

    def on_button_feed_new_clicked(self, button):
        dialog = self.DIALOG(self.preferences)
        response_id, v = dialog.run()

        if response_id == Gtk.ResponseType.OK:
            new_iter = self.liststore.append(v)
            self.feedsource_treeview.set_cursor_to(new_iter)

    def on_button_feed_prefs_clicked(self, treeselection):
        model, iter = treeselection.get_selected()

        dialog = self.DIALOG(self.preferences, model[iter])
        response_id, v = dialog.run()

        if response_id == Gtk.ResponseType.OK:
            new_iter = self.liststore.update(v, iter)
            self.feedsource_treeview.set_cursor_to(new_iter)

    def on_button_feed_del_clicked(self, treeselection):
        model, iter = treeselection.get_selected()
        model.remove(iter)

        self.button_prefs.set_sensitive(False)
        self.button_del.set_sensitive(False)

    def on_feedsource_treeview_query_tooltip(self, treeview, *args):
        pass

    def on_feedsource_treeview_cursor_changed(self, treeselection):
        model, iter = treeselection.get_selected()
        if iter:
            self.button_prefs.set_sensitive(True)
            self.button_del.set_sensitive(True)

