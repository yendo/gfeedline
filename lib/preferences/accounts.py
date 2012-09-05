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

    def on_button_feed_new_clicked(self, button):
        TwitterAuthAssistant(self.preferences, cb=self.assistant_cb)

    def assistant_cb(self, account):
        new_iter = self.liststore.account_liststore.append(account)
        self.feedsource_treeview.set_cursor_to(new_iter)
