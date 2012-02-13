from gi.repository import Gtk

from constants import SHARED_DATA_FILE
from plugins.twitter.account import AuthorizedTwitterAccount
from utils.urlgetautoproxy import UrlGetWithAutoProxy


class UpdateWidgetBase(object):

    def _on_error(self, *args):
        print "error", args

    def _download_user_icon_with_callback(self, gui, entry):
        icon_uri = str(entry['image_uri'])
        entry['icon_path'] = '/tmp/twitter_profile_image2.jpg'
        urlget = UrlGetWithAutoProxy(icon_uri)
        d = urlget.downloadPage(icon_uri, entry['icon_path']).\
            addCallback(self._run, gui, entry).addErrback(self._on_error)


    def _set_ui(self, gui, entry):
        gui.get_object('label_user').set_markup('<b>%s</b>' % entry['user_name'])
        gui.get_object('label_body').set_text(entry['status_body'])
        gui.get_object('image_usericon').set_from_file(entry['icon_path'])

class UpdateWindow(UpdateWidgetBase):

    def __init__(self, mainwindow, entry=None):
        self.entry = entry

        gui = Gtk.Builder()
        gui.add_from_file(SHARED_DATA_FILE('update.glade'))

        self.update_window = gui.get_object('window1')
        self.text_view = gui.get_object('textview')
        self.label_num = gui.get_object('label_num')
        self.button_tweet = gui.get_object('button_tweet')
        self.text_buffer = self.text_view.get_buffer()

        self.on_textbuffer_changed(self.text_buffer)
        gui.connect_signals(self)

        if entry:
            self._download_user_icon_with_callback(gui, entry)
        else:
            gui.get_object('grid_entry').destroy()
            self.update_window.show_all()

    def _run(self, unknown, gui, entry, *args):
        self._set_ui(gui, entry)

        user = entry['user_name']
        self.update_window.set_title(_('Reply to %s') % user)
        self.text_buffer.set_text('@%s '% user)

        self.update_window.show_all()

    def on_button_tweet_clicked(self, button):
        text_buffer = self.text_view.get_buffer()

        start, end = text_buffer.get_bounds()
        status = text_buffer.get_text(start, end, False).decode('utf-8')

        params = {'in_reply_to_status_id': self.entry.get('id')} \
            if self.entry else {}

        twitter_account = AuthorizedTwitterAccount()
        twitter_account.api.update(status, params)

        self.update_window.destroy()

    def on_textbuffer_changed(self, text_buffer):
        num = 140 - text_buffer.get_char_count()
        self.label_num.set_text(str(num))

        status = bool(num != 140)
        self.button_tweet.set_sensitive(status)

class RetweetDialog(UpdateWidgetBase):

    def run(self, entry, parent):
        self.parent = parent

        gui = Gtk.Builder()
        gui.add_from_file(SHARED_DATA_FILE('retweet.glade'))
        self._download_user_icon_with_callback(gui, entry)

    def _run(self, unknown, gui, entry, *args):
        self._set_ui(gui, entry)

        dialog = gui.get_object('messagedialog')
        dialog.set_transient_for(self.parent)
        response_id = dialog.run()

        if response_id == Gtk.ResponseType.YES:
            twitter_account = AuthorizedTwitterAccount()
            twitter_account.api.retweet(entry['id'], self._on_retweet_status)
            
        dialog.destroy()

    def _on_retweet_status(self, *args):
        #print args
        pass
