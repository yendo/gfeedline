import time
from datetime import datetime, timedelta

from gi.repository import Gtk

from ..accountliststore import AccountColumn
from ui import *

class AccountTreeview(TreeviewBase):

    WIDGET = 'filter_treeview'

    def __init__(self, gui, mainwindow):
        super(FilterTreeview, self).__init__(
            gui, mainwindow.liststore.filter_liststore)
        mainwindow.liststore.filter_liststore.update_expire_info()

class AccountAction(ActionBase):

    DIALOG = FilterDialog
    TREEVIEW = AccountTreeview
    BUTTON_PREFS = 'button_filter_prefs'
    BUTTON_DEL = 'button_filter_del'
