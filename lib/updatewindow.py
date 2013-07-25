import os
import re
import tempfile
import locale

from gi.repository import Gtk, GLib, Gio, Gdk, GdkPixbuf

try:
    from gtkspellcheck import SpellChecker
except ImportError:
    SpellChecker = False

from constants import SHARED_DATA_FILE
from accountliststore import AccountColumn
from plugins.twitter.account import AuthorizedTwitterAccount
from utils.settings import SETTINGS, SETTINGS_TWITTER
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
        gui.get_object('label_user').set_markup('<b>%s</b> <small>@%s</small>' % (
                entry['full_name'], entry['user_name']))
        gui.get_object('label_body').set_text(entry['status_body'])
        gui.get_object('image_usericon').set_from_file(icon.name)

class UpdateWindow(UpdateWidgetBase):

    def __init__(self, mainwindow, entry=None, account=None):
        self.entry = entry
        self.child = None # for GtkGrid.get_child_at no available

        gui = Gtk.Builder()
        gui.add_from_file(SHARED_DATA_FILE('update.glade'))
        self.media = MediaFile(gui)
        self.config = AuthorizedTwitterAccount.CONFIG

        host_re = '//[A-Za-z0-9\'~+\-=_.,/%\?!;:@#\*&\(\)]+'
        self.http_re = re.compile("(http:%s)" % host_re)
        self.https_re = re.compile("(https:%s)" % host_re)
        self.screen_name_pattern = re.compile('\B@[0-9A-Za-z_]{1,15}')

        self.account_combobox = AccountCombobox(
            gui, mainwindow.liststore, account)

        is_above = SETTINGS.get_boolean('update-window-keep-above')
        self.update_window = gui.get_object('window1')
        self.update_window.set_keep_above(is_above)

        self.button_image = gui.get_object('button_image')

        self.label_num = gui.get_object('label_num')
        self.comboboxtext_privacy = FacebookPrivacyCombobox(gui)
        self.grid_button = gui.get_object('grid_button')
        self.on_combobox_account_changed()

        self.button_tweet = gui.get_object('button_tweet')
        self.text_buffer = gui.get_object('textbuffer')
        self.on_textbuffer_changed(self.text_buffer)

        textview = gui.get_object('textview')

        if SpellChecker:
            self.spellchecker = SpellChecker(textview, locale.getdefaultlocale()[0])
            if not SETTINGS.get_boolean('spell-checker'):
                self.spellchecker.disable()

        gui.connect_signals(self)

        if entry:
            widget = 'buttonbox1' if entry.get('protected') else 'image_secret'
            gui.get_object(widget).hide()
            self._download_user_icon_with_callback(gui, entry)
        else:
            gui.get_object('grid_entry').destroy()
            self.update_window.present()

    def _run(self, unknown, gui, entry, icon, *args):
        self._set_ui(gui, entry, icon)

        user = entry['user_name']
        self.update_window.set_title(_('Reply to %s') % user.decode('utf-8'))
        self.text_buffer.set_text(self._get_all_mentions_from(entry))

        self.update_window.present()

    def _get_all_mentions_from(self, entry):
        account_user = '@' + self.account_combobox.get_account_obj().user_name
        users = '@%s ' % entry['user_name']

        matches = self.screen_name_pattern.finditer(entry['status_body'])
        other_users = ' '.join([x.group() for x in matches 
                                if x.group() != account_user])
        if other_users:
            users += ' %s ' % other_users

        return users

    def set_upload_media(self, file):
        self.media.set(file)
        self.on_textbuffer_changed(self.text_buffer)

    def on_textview_populate_popup(self, textview, default_menu):
        if not SpellChecker:
            return

        menuitem = Gtk.CheckMenuItem.new_with_mnemonic(_('Check _Spelling'))
        menuitem.connect("toggled", self._toggle)

        is_enbled = SETTINGS.get_boolean('spell-checker')
        menuitem.set_active(is_enbled)

        if not menuitem.get_active():
            separator = Gtk.SeparatorMenuItem.new()
            default_menu.prepend(separator)

        default_menu.prepend(menuitem)
        default_menu.show_all()

    def _toggle(self, menuitem):
        state = menuitem.get_active()
        SETTINGS.set_boolean('spell-checker', state)
        if state:
            self.spellchecker.enable()
        else:
            self.spellchecker.disable()

    def on_button_tweet_clicked(self, button):
        start, end = self.text_buffer.get_bounds()
        status = self.text_buffer.get_text(start, end, False).decode('utf-8')

        account_obj = self.account_combobox.get_account_obj()
        account_source = self.account_combobox.get_account_source()

        params = {'in_reply_to_status_id': self.entry.get('id')} \
            if self.entry else {}

        if account_source == 'Facebook':
            params = self.comboboxtext_privacy.get_params()

        if self.media.file: # update with media
            is_shrink = True
            size = 1024

            upload_file = self.media.get_upload_file_obj(is_shrink, size)
            account_obj.api.update_with_media(
                status.encode('utf-8'), upload_file.name, params=params)

        else: # normal update
            account_obj.api.update(status, params=params)

        if not self.entry:
            num = self.account_combobox.combobox_account.get_active()
            SETTINGS.set_int('recent-account', num)

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

    def on_combobox_account_changed(self, *args):
        source = self.account_combobox.get_account_source()

        self.button_image.set_sensitive(source == 'Twitter')

        widget = self.label_num if source == 'Twitter' \
            else self.comboboxtext_privacy.widget if source == 'Facebook' \
            else None

        if self.child: # for GtkGrid.get_child_at no available
            self.grid_button.remove(self.child)
        if widget:
            self.grid_button.attach(widget, 0, 0, 1, 1)
        self.child = widget

    def on_textbuffer_changed(self, text_buffer):
        start, end = self.text_buffer.get_bounds()

        status = self.text_buffer.get_text(start, end, False).decode('utf-8')
        status = self.http_re.sub("*"*self.config.short_url_length, status)
        status = self.https_re.sub("*"*self.config.short_url_length_https, status)

        num = 140 - len(status) - self.media.get_link_letters()

        color = 'red' if num <= 10 else 'black'
        text = '<span fgcolor="%s">%s</span>' % (color, str(num))
        self.label_num.set_markup(text)

        status = bool(0 <= num < 140)
        self.button_tweet.set_sensitive(status)

    def on_textview_key_press_event(self, textview, event):
        key = event.keyval
        masks = event.state.value_names

        if key == Gdk.KEY_Return and 'GDK_CONTROL_MASK' in masks:
            if self.button_tweet.get_sensitive():
                self.on_button_tweet_clicked(None)
        else:
            return False

        return True

    def on_button_link_clicked(self, textbuffer):
        text = ' https://twitter.com/%s/status/%s' % (
            self.entry['user_name'], self.entry['id'])
        textbuffer.place_cursor(textbuffer.get_end_iter())
        textbuffer.insert_at_cursor(text)

    def on_button_quote_clicked(self, textbuffer):
        quote_format = SETTINGS_TWITTER.get_string('quote-format')
        text = quote_format.format(user=self.entry.get('user_name'), 
                                   status=self.entry.get('status_body'))

        textbuffer.delete(textbuffer.get_start_iter(), textbuffer.get_end_iter(),)
        textbuffer.insert_at_cursor(text)
        textbuffer.place_cursor(textbuffer.get_start_iter())

class AccountCombobox(object):

    def __init__(self, gui, liststore, account):
        self.account_liststore = liststore.account_liststore
        self.combobox_account = gui.get_object('combobox_account')
        self.combobox_account.set_model(self.account_liststore)

        if account: # for reply or retweet
            self.active_num = self.account_liststore.get_account_row_num(
                account.source, account.user_name) 
            self.combobox_account.set_sensitive(False)
        else:
            recent = SETTINGS.get_int('recent-account')
            self.active_num = recent \
                if len(self.account_liststore) > recent else 0

        self.combobox_account.set_active(self.active_num)

    def get_account_obj(self):
        return self._get_account(AccountColumn.ACCOUNT)

    def get_account_source(self):
        return self._get_account(AccountColumn.SOURCE)

    def _get_account(self, column):
        active_num = self.combobox_account.get_active()
        return self.account_liststore[active_num][column]

class FacebookPrivacyCombobox(object):

    def __init__(self, gui):
        self.widget = gui.get_object('comboboxtext_privacy')
        self.widget.set_active(0)

    def get_params(self):
        num = self.widget.get_active()
        values = ['EVERYONE', 'ALL_FRIENDS', 'CUSTOM']
        privacy = {'value': values[num]}
        if values[num] == 'CUSTOM': # 'Only Me'
            privacy['friends'] = 'SELF'

        return privacy

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

        if os.path.getsize(temp.name) > self.config.photo_size_limit:
            pixbuf_creator = RotatedPixbufCreator(self.file, 1024)
            pixbuf = pixbuf_creator.get()
            pixbuf.savev(temp.name, image_type, [], [])

        return temp

    def get_link_letters(self):
        return self.config.characters_reserved_per_media if self.file else 0

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
        self.window = parent
        self.parent = parent.window
        self.has_multi_account = len(parent.liststore.account_liststore) > 1

        gui = Gtk.Builder()
        gui.add_from_file(SHARED_DATA_FILE('retweet.glade'))
        self._download_user_icon_with_callback(gui, entry)

    def _run(self, unknown, gui, entry, icon, *args):
        self._set_ui(gui, entry, icon)

        dialog = gui.get_object('messagedialog')
        screen_name = self.twitter_account.user_name

        text1, text2 = self._get_messages()
        dialog.set_markup('<big><b>%s</b></big>' % text1)
        dialog.format_secondary_text(text2)
        dialog.set_transient_for(self.parent)
        response_id = dialog.run()

        if response_id == Gtk.ResponseType.YES:
            self._delete_method(entry['id'])
        dialog.destroy()

    def _delete_method(self, entry_id):
        self.twitter_account.api.retweet(entry_id, self._cb)

    def _get_messages(self):
        screen_name = self.twitter_account.user_name
        text1 = _('Retweet?')
        text2 = _("Retweet this to your (%s's) followers?") % screen_name \
            if self.has_multi_account else _("Retweet this to your followers?") 

        return text1, text2

    def _cb(self, *args):
        #print args
        pass

class DeleteDialog(RetweetDialog):

    def _get_messages(self):
        text1 = _('Delete this tweet?')
        text2 = _('Are you sure you want to delete this Tweet?')
        return text1, text2

    def _delete_method(self, entry_id):
        self.twitter_account.api.destroy(entry_id, self._cb)

    def _cb(self, data, *args):
        status_id = data['id']
        self.window.delete_status(status_id)

class DeleteDirectMessageDialog(DeleteDialog):

    def _get_messages(self):
        text1 = _('Delete this message?')
        text2 = _('Are you sure you want to delete this message?')
        return text1, text2

    def _delete_method(self, entry_id):
        self.twitter_account.api.dm_destroy(entry_id, self._cb)
