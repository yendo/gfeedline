import time
from datetime import datetime, timedelta

from gi.repository import Gtk
from ..constants import SHARED_DATA_FILE
from ..filterliststore import FilterColumn

class FilterDialog(object):
    """Filter Dialog"""

    def __init__(self, parent, liststore_row=None):
        self.gui = Gtk.Builder()
        self.gui.add_from_file(SHARED_DATA_FILE('filters.glade'))

        self.parent = parent
        self.liststore_row = liststore_row

        self.combobox_target = ComboboxTarget(self.gui)
        self.entry_word = self.gui.get_object('entry_word')
        self.spinbutton_expiry = self.gui.get_object('spinbutton_expiry')
        self.combobox_expire_unit = ComboboxExpireUnit(self.gui)

        self.gui.connect_signals(self)

    def run(self):
        dialog = self.gui.get_object('filter_dialog')
        dialog.set_transient_for(self.parent)

        if self.liststore_row:
            self.combobox_target.set_active_text(
                self.liststore_row[FilterColumn.TARGET])
            self.entry_word.set_text(self.liststore_row[FilterColumn.WORD])
            self.spinbutton_expiry.set_value(
                int(self.liststore_row[FilterColumn.EXPIRE_TIME]))
            self.combobox_expire_unit.set_active_text(
                self.liststore_row[FilterColumn.EXPIRE_UNIT])

        # run
        response_id = dialog.run()

        expire_time = ExpireTime(self.spinbutton_expiry.get_value_as_int(),
                                 self.combobox_expire_unit.get_active())

        v = [
            self.combobox_target.get_active_text(),
            self.entry_word.get_text().decode('utf-8'),
            str(self.spinbutton_expiry.get_value_as_int()), 
            self.combobox_expire_unit.get_active_text(), 
            expire_time.get_epoch(),
        ]

#        print v
        dialog.destroy()
#        if response_id == Gtk.ResponseType.OK:
#            SETTINGS_RECENTS.set_string('source', v['source'])
        return response_id , v

class ExpireTime(object):

    def __init__(self, expire_timedelta, is_hours):
        self.expire_timedelta = expire_timedelta
        if not is_hours:
            self.expire_timedelta *= 24

    def get_epoch(self):
        now = datetime.now()
        future = now + self._get_timedelta()
        expire_epoch = int(time.mktime(future.timetuple()))

    def _get_timedelta(self):
        return timedelta(hours=self.expire_timedelta)

class ComboboxTarget(object):

    WIDGET = 'comboboxtext_target'

    def __init__(self, gui):
        self.widget = gui.get_object(self.WIDGET)
        self.widget.set_active(0) # glade bug
        self.model = self.widget.get_model()

    def get_active(self):
        return self.widget.get_active()

    def get_active_text(self):
        return self.model[self.widget.get_active()][0]

    def set_active_text(self, text):
        labels = [i[0] for i in self.model]
        target = labels.index(text)
        self.widget.set_active(target)

class ComboboxExpireUnit(ComboboxTarget):

    WIDGET = 'comboboxtext_expire_unit'

    def get_active_text(self):
        return 'hours' if self.widget.get_active() else 'days'

    def set_active_text(self, text):
        active = text == "hours"
        self.widget.set_active(active)
