from ..accountliststore import AccountColumn
from ui import *

from ..plugins.twitter.assistant import TwitterAuthAssistant


class AccountTreeview(TreeviewBase):

    WIDGET = 'account_treeview'

    def __init__(self, gui, mainwindow):
        super(AccountTreeview, self).__init__(
            gui, mainwindow.liststore.account_liststore)

class AccountAction(ActionBase):

    TREEVIEW = AccountTreeview
    BUTTON_PREFS = 'button_account_new'
    BUTTON_PREFS = 'button_account_prefs'
    BUTTON_DEL = 'button_account_del'

    def on_button_new_clicked(self, button):
        TwitterAuthAssistant(self.preferences, cb=self.assistant_cb)

    def assistant_cb(self, account):
        account_liststore = self.liststore.account_liststore

        source, user_name = account[0:2]
        num = account_liststore.get_account_row_num(source, user_name)

        if num:
            path = Gtk.TreePath(num)
            treeiter = account_liststore.get_iter(path)
            account_liststore.remove(treeiter)

        new_iter = account_liststore.append(account)
        self.feedsource_treeview.set_cursor_to(new_iter)
