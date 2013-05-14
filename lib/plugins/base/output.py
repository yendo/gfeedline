#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012-2013, Yoshizumi Endo.
# Licence: GPL3

"""
Output: got_entry-> print_all_entries-> print_entry
"""

import time
import json

from twisted.internet import reactor

from ...utils.htmlentities import decode_html_entities
from ...utils.settings import SETTINGS_VIEW
from ...filterliststore import FilterColumn
from ...constants import Column
from ...theme import Theme


class OutputBase(object):

    def __init__(self, api, view=None, argument='', options={}, filters=None):
        self.api = api
        self.view = view
        self.argument = argument
        self.options = options
        self.filters = filters
        self.theme = Theme()

        self.delayed = DelayedPool()

        self.since_id = 0
        self.last_id = options.get('last_id') or 0
        self.params = {}
        self.counter = 0

        SETTINGS_VIEW.connect_after("changed::theme", self._on_restart_theme_changed)

    def got_entry(self, entries, *args):
        if entries:
            d = json.loads(entries)
            self.print_all_entries(d)

    def check_entry(self, entry, text, *args):
        pass

    def print_all_entries(self, d):
        self.all_entries = self._get_all_entries(d)
        is_first_call = not bool(self.counter)

        self.delayed.delete_called()

        if not self.all_entries:
            return

        api_interval = self._get_interval_seconds()
        interval = api_interval*1.0 / len(self.all_entries)
        # print "interval: ", interval, api_interval, len(self.all_entries)
        for i, entry in enumerate(reversed(self.all_entries)):
            if self._check_duplicate(entry):
                print "skip!"
                continue
            elif self.counter:
                self.delayed.append(
                    reactor.callLater(interval*i, self.print_entry, entry))
            else:
                self.print_entry(entry, is_first_call=True)

            self.since_id =  entry[self.SINCE_KEY]
        self.counter += 1

    def print_entry(self, entry, is_first_call=False):
        entry_dict = self._get_entry_obj(entry).get_dict(self.api)
        if not entry_dict:
            return

        has_notify = self.options.get('notification') 
        style = 'status'

        is_new_update = self.last_id < entry_dict['id']
        if is_new_update:
            self.last_id = entry_dict['id']

        self.view.update(entry_dict, style, has_notify, 
                         is_first_call, is_new_update)

    def _check_duplicate(self, entry):
        return False

    def _get_entry_obj(self, entry):
        pass

    def _set_since_id(self, entry_id):
        entry_id = int(entry_id)

        if self.since_id < entry_id:
            self.since_id = entry_id

    def start(self, interval=60):
        self.params.clear()
        if self.since_id:
            self.params[self.SINCE] = self.since_id

        params = self.api.get_options(self.argument)
        self.params.update(params)

        self.d = self.api.api(self.got_entry, params=self.params)
        self.d.addErrback(self._on_error)

        interval = self._get_interval_seconds()
        self.timeout = reactor.callLater(interval, self.start, interval)

    def _get_interval_seconds(self):
        return 30

    def exit(self):
        self.disconnect()
        self.view.remove()

    def disconnect(self):
        self.delayed.clear()
        if hasattr(self, 'd'):
            self.d.cancel()
        if hasattr(self, 'timeout') and not self.timeout.called:
            self.timeout.cancel()

    def _on_restart_theme_changed(self, *args):
        self.view.clear_buffer()
        self.disconnect()
        self.since_id = 0
        self.counter = 0
        self.start()

    def _on_reconnect_credential(self, *args):
        self._on_restart_theme_changed()

    def _on_error(self, e):
        print "Error (%s): %s" % (self.api.name, e)

class DelayedPool(list):

    def delete_called(self):
        for i in self:
            if i.called:
                self.remove(i)

    def clear(self):
        for i in self:
            if not i.called:
                i.cancel()
