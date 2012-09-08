import os
import tempfile

from gi.repository import Gtk, GLib, Gio, GdkPixbuf

from constants import SHARED_DATA_FILE
from accountliststore import AccountColumn
from plugins.twitter.account import AuthorizedTwitterAccount
from utils.settings import SETTINGS
from utils.urlgetautoproxy import UrlGetWithAutoProxy


class UpdateWidgetBase(object):

    def _on_error(self, *args):
        print "error", args

    def _download_user_icon_with_callback(self, gui, entry):
        icon_uri = str(entry['image_uri'])
        icon = tempfile.NamedTemporaryFile()

        urlget = UrlGetWithAutoProxy(icon_uri)
        d = urlget.downloadPage(icon_uri, icon.name)
        d.addCallback(self._run, gui, entry, icon).addErrback(self._on_error)

    def _set_ui(self, gui, entry, icon):
        gui.get_object('label_user').set_markup('<b>%s</b>' % entry['user_name'])
        gui.get_object('label_body').set_text(entry['status_body'])
        gui.get_object('image_usericon').set_from_file(icon.name)

class AccountCombobox(object):

    def __init__(self, gui, liststore, account):
        self.account_liststore = liststore.account_liststore
        self.combobox_account = gui.get_object('combobox_account')
        self.combobox_account.set_model(self.account_liststore)

        self.active_num = self.account_liststore.get_account_row_num(
            'Twitter', account.user_name) if account else 0
        self.combobox_account.set_active(self.active_num)

    def get_account_obj(self):
        return self.account_liststore[self.active_num][AccountColumn.ACCOUNT]

class UpdateWindow(UpdateWidgetBase):

    def __init__(self, mainwindow, entry=None, account=None):
        self.entry = entry

        gui = Gtk.Builder()
        gui.add_from_file(SHARED_DATA_FILE('update.glade'))
        self.media = MediaFile(gui)

        self.account_combobox = AccountCombobox(
            gui, mainwindow.liststore, account)

        is_above = SETTINGS.get_boolean('update-window-keep-above')
        self.update_window = gui.get_object('window1')
        self.update_window.set_keep_above(is_above)

        self.label_num = gui.get_object('label_num')
        self.button_tweet = gui.get_object('button_tweet')
        self.text_buffer = gui.get_object('textbuffer')
        self.on_textbuffer_changed(self.text_buffer)

        gui.connect_signals(self)

        if entry:
            if not entry['protected']:
                gui.get_object('image_secret').hide()

            self._download_user_icon_with_callback(gui, entry)
        else:
            gui.get_object('grid_entry').destroy()
            self.update_window.present()

    def _run(self, unknown, gui, entry, icon, *args):
        self._set_ui(gui, entry, icon)

        user = entry['user_name']
        self.update_window.set_title(_('Reply to %s') % user.decode('utf-8'))
        self.text_buffer.set_text('@%s '% user)

        self.update_window.present()

    def set_upload_media(self, file):
        self.media.set(file)
        self.on_textbuffer_changed(self.text_buffer)

    def on_button_tweet_clicked(self, button):
        start, end = self.text_buffer.get_bounds()
        status = self.text_buffer.get_text(start, end, False).decode('utf-8')

        params = {'in_reply_to_status_id': self.entry.get('id')} \
            if self.entry else {}

        twitter_account = self.account_combobox.get_account_obj()

        if self.media.file: # update with media
            is_shrink = True
            size = 1024

            upload_file = self.media.get_upload_file_obj(is_shrink, size)
            twitter_account.api.update_with_media(
                status.encode('utf-8'), upload_file.name, params=params)

        else: # normal update
            twitter_account.api.update(status, params=params)

        self.update_window.destroy()

    def on_button_image_clicked(self, button):
        dialog = FileChooserDialog()
        file = dialog.run(self.update_window)
        self.set_upload_media(file)

    def on_eventbox_attached_press_event(self, image_menu, event):
        if event.button == 3:
            image_menu.popup(None, None, None, None, event.button, event.time)

    def on_menuitem_remove_activate(self, menuitem):
        self.media.clear()
        self.on_textbuffer_changed(self.text_buffer)

    def on_file_activated(self, *args):
        print args

    def on_textbuffer_changed(self, text_buffer):
        num = 140 - text_buffer.get_char_count() - self.media.get_link_letters()
        self.label_num.set_text(str(num))

        status = bool(num != 140)
        self.button_tweet.set_sensitive(status)

class MediaFile(object):

    def __init__(self, gui):
        self.file = None
        self.config = AuthorizedTwitterAccount.CONFIG

        self.button_image = gui.get_object('button_image')
        self.image = gui.get_object('image_attached')
        self.ebox = gui.get_object('eventbox_attached')
        self.ebox.hide()

    def set(self, media_file):
        self.file = media_file

        if self.file:
            self.ebox.show()
            self.button_image.set_sensitive(False)

            size = 80
            pixbuf_creator = RotatedPixbufCreator(self.file, size)
            pixbuf = pixbuf_creator.get()

            self.image.set_from_pixbuf(pixbuf)

    def clear(self):
        self.file = None
        self.ebox.hide()
        self.button_image.set_sensitive(True)

    def get_upload_file_obj(self, is_shrink=False, size=1024):
        temp = tempfile.NamedTemporaryFile()
        image_type = 'jpeg' if Gio.content_type_guess(
            self.file, None)[0] == 'image/jpeg' else 'png'

        pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.file)
        w, h = pixbuf.get_width(), pixbuf.get_height()
        new_size = size if is_shrink and (w > size or h > size) else None

        pixbuf_creator = RotatedPixbufCreator(self.file, new_size)
        pixbuf = pixbuf_creator.get()
        pixbuf.savev(temp.name, image_type, [], [])

        if os.path.getsize(temp.name) > int(self.config.photo_size_limit):
            pixbuf_creator = RotatedPixbufCreator(self.file, 1024)
            pixbuf = pixbuf_creator.get()
            pixbuf.savev(temp.name, image_type, [], [])

        return temp

    def get_link_letters(self):
        media_link_letters = int(self.config.characters_reserved_per_media)
        return media_link_letters if self.file else 0

class FileChooserDialog(object):

    def run(self, parent):
        gui = Gtk.Builder()
        gui.add_from_file(SHARED_DATA_FILE('update.glade'))

        dialog = gui.get_object('filechooserdialog1')
        dialog.set_transient_for(parent)

        folder = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES)
        dialog.set_current_folder(folder)

        filefilter = gui.get_object('image_filefilter')
        filefilter.set_name(_('Supported image files'))
        dialog.add_filter(filefilter)

        preview = gui.get_object('preview_image')
        dialog.connect("update-preview", self.on_update_preview, preview)

        response_id = dialog.run()
        filename = dialog.get_filename() if response_id else None

        # print dialog.get_current_folder()
        dialog.destroy()

        return filename

    def on_update_preview(self, filechooser, preview):
        try:
            filename = filechooser.get_preview_filename()

            pixbuf_creator = RotatedPixbufCreator(filename, 128)
            pixbuf = pixbuf_creator.get()

            preview.set_from_pixbuf(pixbuf)
            has_preview = True
        except:
            has_preview = False

        filechooser.set_preview_widget_active(has_preview)

class RotatedPixbufCreator(object):

    def __init__(self, filename, size=None):
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename) if not size \
            else GdkPixbuf.Pixbuf.new_from_file_at_size(filename, size, size)

        orientation = self.pixbuf.get_option('orientation')
        rotation = self._get_orientation(orientation)

        if rotation != 1:
            self.pixbuf = self.pixbuf.rotate_simple(rotation)

    def get(self):
        return self.pixbuf

    def _get_orientation(self, orientation=1):
        orientation = int(orientation) if orientation else 1

        if orientation == 6:
            rotate = 270
        elif orientation == 8:
            rotate = 90
        else:
            rotate = 0

        return rotate

class RetweetDialog(UpdateWidgetBase):

    def __init__(self, account):
        self.twitter_account = account

    def run(self, entry, parent):
        self.parent = parent

        gui = Gtk.Builder()
        gui.add_from_file(SHARED_DATA_FILE('retweet.glade'))
        self._download_user_icon_with_callback(gui, entry)

    def _run(self, unknown, gui, entry, icon, *args):
        self._set_ui(gui, entry, icon)

        dialog = gui.get_object('messagedialog')
        dialog.set_transient_for(self.parent)
        response_id = dialog.run()

        if response_id == Gtk.ResponseType.YES:
            self.twitter_account.api.retweet(entry['id'], self._on_retweet_status)

        dialog.destroy()

    def _on_retweet_status(self, *args):
        #print args
        pass

class UpdateWindowOLD(UpdateWindow):

    def __init__(self, mainwindow, entry=None):
        self.entry = entry

        gui = Gtk.Builder()
        gui.add_from_file(SHARED_DATA_FILE('update.glade'))
        self.media = MediaFile(gui)
        self.account_combobox = AccountCombobox(
            gui, mainwindow.liststore, account)

        is_above = SETTINGS.get_boolean('update-window-keep-above')
        self.update_window = gui.get_object('window1')
        self.update_window.set_keep_above(is_above)

        self.label_num = gui.get_object('label_num')
        self.button_tweet = gui.get_object('button_tweet')
        self.text_buffer = gui.get_object('textbuffer')
        self.on_textbuffer_changed(self.text_buffer)

        gui.connect_signals(self)

# from: for ubuntu oneiric
        gui.get_object('grid_entry').destroy()

        if entry:
            user = entry['user_name']
            self.update_window.set_title(_('Reply to %s') % user)
            self.text_buffer.set_text('@%s '% user)

        self.update_window.present()
# end

class RetweetDialogOLD(RetweetDialog):

    def run(self, entry, parent):
        self.parent = parent

        gui = Gtk.Builder()

        gui.add_from_file(SHARED_DATA_FILE('retweet.glade'))

        gui.get_object('grid1').destroy()
        self._run("dummy",gui, entry)

    def _run(self, unknown, gui, entry, *args):
        dialog = gui.get_object('messagedialog')
        dialog.set_transient_for(self.parent)
        response_id = dialog.run()

        if response_id == Gtk.ResponseType.YES:
            self.twitter_account.api.retweet(entry['id'], self._on_retweet_status)

        dialog.destroy()
