from gi.repository import Gtk

from ..constants import Column
from ..accountliststore import AccountColumn
from ..utils.commonui import MultiAccountSensitiveWidget
from ..utils.settings import SETTINGS, SETTINGS_VIEW
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
        self.entry_argument = ArgumentEntry(self.gui, self.combobox_target,
                                            self.combobox_source)
        self.entry_group = self.gui.get_object('entry_group')

        self.options_tab = OptionsTab(self.gui, self.liststore_row)

        self.on_combobox_source_changed()
        self.on_comboboxtext_target_changed()

    def run(self):

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
            account_obj = self.combobox_source.get_active_account_obj()

            self.combobox_source.set_recent()
            self.combobox_target.set_recent(account_obj)

        self.dialog.destroy()

        return response_id , v

    def on_combobox_source_changed(self, combobox=None):
        account_obj = self.combobox_source.get_active_account_obj()
        self.combobox_target.set_label_text(account_obj)

    def on_comboboxtext_target_changed(self, *args):
        api_dict = self.combobox_source.get_active_account_obj().api_dict
        status = self.combobox_target.has_argument_entry_enabled(api_dict)
        tooltip = self.combobox_target.get_tooltip_for_argument(api_dict)

        self.label_argument.set_sensitive(status)
        self.entry_argument.set_sensitive(status)
        self.entry_argument.set_tooltip_text(tooltip)
 
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

        dic = {_('User Stream'): OptionsTabUserStream,
               _('List TimeLine'): OptionsTabIncludeRTS,
               _('User TimeLine'): OptionsTabShowProfile}

        child_class = dic.get(target) or OptionsTabChild
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

    LABEL = _('_Notify events')
    OPTION_NAME = 'notify_events'

    def __init__(self, gui, feedliststore):
        super(OptionsTabUserStream, self).__init__(gui, feedliststore)

        self.widget = gui.get_object('grid_option')
        self.checkbutton = gui.get_object('checkbutton_option')
        self.notebook.append_page(self.widget, Gtk.Label.new(_('Options')))

        self._set_checkbutton(feedliststore, self.checkbutton, 
                              self.OPTION_NAME, self.LABEL)

    def _set_checkbutton(self, feedliststore, checkbutton, option, label):
        state = feedliststore[Column.OPTIONS].get(option) \
            if feedliststore else True
        if state is None:
            state = True

        checkbutton.set_label(label)
        checkbutton.set_active(state)

    def get(self):
        state = self.checkbutton.get_active()
        result = {self.OPTION_NAME: state}
        print result
        return result

class OptionsTabIncludeRTS(OptionsTabUserStream):

    LABEL = _('_Include Retweets')
    OPTION_NAME = 'include_rts'

class OptionsTabShowProfile(OptionsTabUserStream):

    LABEL = _('_Show user profile')
    OPTION_NAME = 'has_profile'

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
        else:
            num = SETTINGS.get_int('feedsource-recent-account')

        self.widget.set_active(num)

    def get_active_account(self):
        account = self.widget.get_model()[self.widget.get_active()]
        source = account[AccountColumn.SOURCE].decode('utf-8')
        user_name = account[AccountColumn.ID].decode('utf-8')
        return source, user_name

    def get_active_account_obj(self):
        account = self.widget.get_model()[self.widget.get_active()]
        return account[AccountColumn.ACCOUNT]

    def set_recent(self):
        num = self.widget.get_active()
        SETTINGS.set_int('feedsource-recent-account', num)
        

class TargetCombobox(object):

    def __init__(self, gui, feedliststore):
        self.widget = gui.get_object('comboboxtext_target')
        self.feedliststore = feedliststore

    def set_label_text(self, account_obj):
        labels = account_obj.api_dict.keys()
        self.label_list = sorted([x for x in labels])

        self.widget.remove_all()
        for text in self.label_list:
            self.widget.append_text(text)

        num = account_obj.get_recent_api(self.label_list, self.feedliststore)
        self.widget.set_active(num)

    def get_active_text(self):
        label = self.label_list[self.widget.get_active()]
        return label

    def set_recent(self, account_obj):
        num = self.widget.get_active()
        account_obj.set_recent_api(num)

    def has_argument_entry_enabled(self, api_dict):
        api_class = self._get_api_class(api_dict)
        status = api_class.has_argument
        return status

    def get_tooltip_for_argument(self, api_dict):
        api_class = self._get_api_class(api_dict)
        tooltip = api_class.tooltip_for_argument \
            if hasattr(api_class, 'tooltip_for_argument') else ''
        return tooltip

    def _get_api_class(self, api_dict):
        api_name = self.get_active_text()
        api_class = api_dict.get(api_name)
        return api_class

class ArgumentEntry(object):

    def __init__(self, gui, combobox_target, combobox_source):
        self.widget = gui.get_object('entry_argument')
        self.combobox_target = combobox_target
        self.combobox_source = combobox_source

    def get_text(self):
        api_dict = self.combobox_source.get_active_account_obj().api_dict
        has_argument = self.combobox_target.has_argument_entry_enabled(api_dict)
        return self.widget.get_text() if has_argument else ''

    def set_text(self, text):
        self.widget.set_text(text)

    def set_sensitive(self, status):
        self.widget.set_sensitive(status)

    def set_tooltip_text(self, text):
        self.widget.set_tooltip_text(text)

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
        model, treeiter = treeselection.get_selected()

        self.api_obj = model.get_value(treeiter, Column.API)
        self.group = model.get_value(treeiter, Column.GROUP).decode('utf-8')
        self.old_page = model.get_group_page(self.group)

    def on_drag_end(self, treeview, dragcontext, mainwindow):
        treeselection = treeview.get_selection()
        model, treeiter = treeselection.get_selected()

        if not treeiter:
            self.gui.get_object('button_feed_prefs').set_sensitive(False)
            self.gui.get_object('button_feed_del').set_sensitive(False)

        is_multi_column = SETTINGS_VIEW.get_boolean('multi-column')
        all_view = [x[Column.API].view for x in model if not is_multi_column 
                    or x[Column.GROUP].decode('utf-8') == self.group]
        all_view = sorted(set(all_view), key=all_view.index)
        page = all_view.index(self.api_obj.view)

        notebook = mainwindow.column.get_notebook_object(self.group)
        notebook.reorder_child(self.api_obj.view.box, page) # FIXME FIXBOX

        new_page = model.get_group_page(self.group)

        if self.old_page != new_page:
            mainwindow.column.hbox.reorder_child(notebook, new_page)

class FeedSourceAction(ActionBase):

    DIALOG = FeedSourceDialog
    TREEVIEW = FeedSourceTreeview
    BUTTON_PREFS = 'button_feed_prefs'
    BUTTON_DEL = 'button_feed_del'
