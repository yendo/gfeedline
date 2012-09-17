from gi.repository import Gtk

from ..plugins.twitter.api import TwitterAPIDict
from ..constants import Column
from ..accountliststore import AccountColumn
from ..utils.commonui import MultiAccountSensitiveWidget
from ..utils.settings import SETTINGS_TWITTER
from ui import *

class FeedSourceDialog(DialogBase):
    """Feed Source Dialog"""

    GLADE = 'feedsource.glade'
    DIALOG = 'feed_source'

    def _setup_ui(self):
        self.combobox_source = SourceCombobox(self.gui, self.liststore_row, 
                                              self.liststore)
        self.combobox_target = TargetCombobox(self.gui, self.liststore_row)
        self.entry_name = self.gui.get_object('entry_name')
        self.label_argument = self.gui.get_object('label_argument')
        self.entry_argument = ArgumentEntry(self.gui, self.combobox_target)
        self.entry_group = self.gui.get_object('entry_group')

        self.options_tab = OptionsTab(self.gui, self.liststore_row)
        self.on_comboboxtext_target_changed()

    def run(self):
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
        response_id = self.dialog.run()

        source, username = self.combobox_source.get_active_account()
        target = self.combobox_target.get_active_text()

        v = {
            'source' : source,
            'username': username,
            'name' : self.entry_name.get_text().decode('utf-8'),
            'target' : target, #.decode('utf-8'),
            'argument' : self.entry_argument.get_text().decode('utf-8'),
            'group': self.entry_group.get_text().decode('utf-8'),
            'options' : 
            {'notification': checkbutton_notification.get_active()},
        }

        options = self.options_tab.get(target)
        v['options'].update(options)

        if response_id == Gtk.ResponseType.OK:
            self.combobox_target.set_recent()
        self.dialog.destroy()

        return response_id , v

    def on_comboboxtext_target_changed(self, *args):
        status = self.combobox_target.has_argument_entry_enabled()
        self.label_argument.set_sensitive(status)
        self.entry_argument.set_sensitive(status)

        button_status = not status
        if not button_status and self.entry_argument.get_text():
            button_status = True

        self.button_ok.set_sensitive(button_status)

        # Options Tab
        target = self.combobox_target.get_active_text()
        self.options_tab.change(target)

class OptionsTab(object):

    def __init__(self, gui, feedliststore):
        self.gui = gui
        self._options_child = None
        self.feedliststore = feedliststore

    def change(self, target):
        if self._options_child:
            self._options_child.clear()

        child_class = OptionsTabUserStream if target == _('User Stream') \
            else OptionsTabChild
        self._options_child = child_class(self.gui, self.feedliststore)

    def get(self, target):
        return self._options_child.get()

class OptionsTabChild(object):

    def __init__(self, gui, feedliststore):
        self.widget = None
        self.notebook = gui.get_object('notebook_feedsource')

    def get(self):
        return {}

    def clear(self):
        if self.widget:
            page_num = self.notebook.page_num(self.widget)
            self.notebook.remove_page(page_num)

class OptionsTabUserStream(OptionsTabChild):

    def __init__(self, gui, feedliststore):
        super(OptionsTabUserStream, self).__init__(gui, feedliststore)

        self.widget = gui.get_object('grid_option')
        self.checkbutton = gui.get_object('checkbutton_option')
        self.notebook.append_page(self.widget, Gtk.Label.new(_('Options')))

        state = feedliststore[Column.OPTIONS].get('notify_events') \
            if feedliststore else True

        self.checkbutton.set_label(_('_Notify events'))
        self.checkbutton.set_active(state)

    def get(self):
        state = self.checkbutton.get_active()
        result = {'notify_events': state}
        return result

class SourceCombobox(object):

    def __init__(self, gui, feedliststore, liststore):
        self.widget = gui.get_object('combobox_source')
        self.widget.set_model(liststore.account_liststore)
        
        num = 0
        if feedliststore:
            for i, v in enumerate(liststore.account_liststore):
                if v[AccountColumn.SOURCE] == feedliststore[Column.SOURCE] and \
                        v[AccountColumn.ID] == feedliststore[Column.USERNAME]:
                    num = i

        self.widget.set_active(num)

    def get_active_account(self):
        account = self.widget.get_model()[self.widget.get_active()]
        source, user_name = account[AccountColumn.SOURCE], \
            account[AccountColumn.ID]
        return source, user_name

class TargetCombobox(object):

    def __init__(self, gui, feedliststore):
        self.widget = gui.get_object('comboboxtext_target')

        self.label_list = sorted([x for x in TwitterAPIDict().keys()])

        for text in self.label_list:
            self.widget.append_text(text)

        recent = SETTINGS_TWITTER.get_int('recent-target')
        num = self.label_list.index(feedliststore[Column.TARGET].decode('utf-8')) \
            if feedliststore else recent if recent >= 0 else \
            self.label_list.index(_("User Stream"))

        self.widget.set_active(num)

    def get_active_text(self):
        label = self.label_list[self.widget.get_active()]
        return label

    def set_recent(self):
        num = self.widget.get_active()
        SETTINGS_TWITTER.set_int('recent-target', num)

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

class ButtonFeedNew(MultiAccountSensitiveWidget):

    WIDGET = 'button_feed_new'

class FeedSourceTreeview(TreeviewBase):

    WIDGET = 'feedsourcetreeview'

    def __init__(self, gui, mainwindow):
        super(FeedSourceTreeview, self).__init__(gui, mainwindow.liststore)

        self.treeview.set_headers_clickable(False) # Builder bug?
        self.treeview.connect("drag-begin", self.on_drag_begin)
        self.treeview.connect("drag-end", self.on_drag_end, mainwindow)

        button_feed_new = ButtonFeedNew(gui, mainwindow.liststore)

    def get_selection(self):
        return self.treeview.get_selection()

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

class FeedSourceAction(ActionBase):

    DIALOG = FeedSourceDialog
    TREEVIEW = FeedSourceTreeview
    BUTTON_PREFS = 'button_feed_prefs'
    BUTTON_DEL = 'button_feed_del'
