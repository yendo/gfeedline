from ..accountliststore import AccountColumn
from ui import *


class AccountTreeview(TreeviewBase):

    WIDGET = 'account_treeview'

    def __init__(self, gui, mainwindow):
        super(AccountTreeview, self).__init__(
            gui, mainwindow.liststore.account_liststore)

class AccountAction(ActionBase):

    DIALOG = ''
    TREEVIEW = AccountTreeview
    BUTTON_PREFS = 'button_filter_prefs'
    BUTTON_DEL = 'button_filter_del'
