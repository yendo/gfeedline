class MultiAccountSensitiveWidget(object):

    WIDGET = None

    def __init__(self, gui, liststore):
        self.widget = gui.get_object(self.WIDGET)

        has_multi_account = len(liststore.account_liststore) > 0
        self.widget.set_sensitive(has_multi_account)

        liststore.account_liststore.connect("row-inserted", self._add_account)
        liststore.account_liststore.connect("row-deleted", self._del_account)

    def _add_account(self, liststore, treepath, treeiter):
        self.widget.set_sensitive(True)

    def _del_account(self, liststore, treepath):
        if len(liststore) < 1:
            self.widget.set_sensitive(False)
