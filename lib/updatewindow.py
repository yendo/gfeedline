import os

from gi.repository import Gtk, Gdk
from plugins.twitter.account import AuthorizedTwitterAPI
from constants import SHARED_DATA_DIR

class UpdateWindow(object):

    def __init__(self, mainwindow, user=None, id=None):
        self.user = user
        self.id = id

        gui = Gtk.Builder()
        gui.add_from_file(os.path.join(SHARED_DATA_DIR, 'update.glade'))

        self.update_window = gui.get_object('window1')
        self.text_view =  gui.get_object('textview')
        self.label_num =  gui.get_object('label_num')

        if self.user and self.id:
            self.update_window.set_title('Reply to %s' % user)
            text_buffer = self.text_view.get_buffer()
            text_buffer.set_text('@%s '% user)
            self.on_textbuffer_changed(text_buffer)

        self.update_window.show_all()
        gui.connect_signals(self)

    def on_button_tweet_clicked(self, button):
        text_buffer = self.text_view.get_buffer()

        start, end = text_buffer.get_bounds()
        status = text_buffer.get_text(start, end, False).decode('utf-8')

        params = {'in_reply_to_status_id': self.id} \
            if self.user and self.id else {}

        twitter_account = AuthorizedTwitterAPI()
        twitter_account.api.update(status, params)

        self.update_window.destroy()

    def on_textbuffer_changed(self, text_buffer):
        num = 140 - text_buffer.get_char_count()
        self.label_num.set_text(str(num))
