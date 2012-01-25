import os

from gi.repository import Gtk, Gdk
from plugins.twitter.account import AuthorizedTwitterAPI

class UpdateWindow(object):

    def __init__(self, mainwindow):

        gui = Gtk.Builder()
        gui.add_from_file(os.path.abspath('share/update.glade'))

        self.update_window = gui.get_object('window1')
        self.text_view =  gui.get_object('textview')
        self.label_num =  gui.get_object('label_num')

        self.update_window.show_all()
        gui.connect_signals(self)

    def on_button_tweet_clicked(self, button):
        text_buffer = self.text_view.get_buffer()

        start, end = text_buffer.get_bounds()
        status = text_buffer.get_text(start, end, False).decode('utf-8')

        twitter_account = AuthorizedTwitterAPI()
        twitter_account.api.update(status)

        self.update_window.destroy()

    def on_textbuffer_changed(self, text_buffer):
        num = 140 - text_buffer.get_char_count()
        self.label_num.set_text(str(num))
