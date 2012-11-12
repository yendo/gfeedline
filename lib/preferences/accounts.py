from ..accountliststore import AccountColumn
from ui import *

from ..plugins.twitter.assistant import TwitterAuthAssistant
from ..plugins.facebook.assistant import FacebookAuthAssistant
from ..plugins.tumblr.assistant import TumblrAuthAssistant


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

    def on_button_new_clicked(self, parent):
        gui = Gtk.Builder()
        gui.add_from_file(SHARED_DATA_FILE('select_assistant.glade'))
        dialog = gui.get_object('dialog1')
        dialog.set_transient_for(parent)

        # Tumblr will be officially support from ver.2.1.
        gui.get_object('radiobutton_tl').hide()

        response_id = dialog.run()
        dialog.destroy()

        if response_id == Gtk.ResponseType.OK:
            if gui.get_object('radiobutton_tw').get_active():
                TwitterAuthAssistant(self.preferences, cb=self.assistant_cb)
            elif gui.get_object('radiobutton_fb').get_active():
                FacebookAuthAssistant(self.preferences, cb=self.assistant_cb)
            elif gui.get_object('radiobutton_tl').get_active():
                TumblrAuthAssistant(self.preferences, cb=self.assistant_cb)

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
