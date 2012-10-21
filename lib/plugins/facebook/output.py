#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

"""
TwitterOutputBase --- TwitterRestOutput --- TwitterSearchOutput
                   |
                   \- TwitterFeedOutput

Rest: got_entry-> check_entry-> buffer_entry : print_all_entries-> print_entry
Feed: got_entry-> check_entry-> buffer_entry---------------------> print_entry
              \-> (events)--------------------------------------/
"""

import time
import json

from twisted.internet import reactor

from entry import *
from ...utils.htmlentities import decode_html_entities
from ...utils.settings import SETTINGS_VIEW
from ...filterliststore import FilterColumn
from ...constants import Column
from ...theme import Theme


class FacebookOutputBase(object):

    def __init__(self, api, view=None, argument='', options={}, filters=None):
        self.api = api
        self.view = view
        self.argument = argument
        self.options = options
        self.filters = filters

        self.theme = Theme()

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

    def print_all_entries(self, d, api_interval=10):
        is_first_call = not bool(self.counter)
        for i in reversed(d['data']):
            self.print_entry(i, is_first_call)
            self.since_id =  i['created_time']

        self.counter += 1

    def print_entry(self, entry, is_first_call=False):
        entry_dict = self._get_entry_obj(entry).get_dict(self.api)
        has_notify = self.options.get('notification') 

        style = 'status'
        is_new_update = False

        self.view.update(entry_dict, style, has_notify, 
                         is_first_call, is_new_update)

    def _get_entry_obj(self, entry):
        return FacebookEntry(entry)

    def _set_since_id(self, entry_id):
        entry_id = int(entry_id)

        if self.since_id < entry_id:
            self.since_id = entry_id

    def exit(self):
        self.disconnect()
        self.view.remove()

    def disconnect(self):
        if hasattr(self, 'timeout') and not self.timeout.called:
            self.timeout.cancel()

class FacebookRestOutput(FacebookOutputBase):

    def start(self, interval=60):
        self.params.clear()
        if self.since_id:
            self.params['since'] = self.since_id

        params = self.api.get_options(self.argument)
        self.params.update(params)

        self.d = self.api.api(self.got_entry, params=self.params)
        self.d.addErrback(self._on_error)

        interval = self._get_interval_seconds()
        self.timeout = reactor.callLater(interval, self.start, interval)

    def _get_interval_seconds(self):
        return 120

    def exit(self):
        super(FacebookRestOutput, self).exit()

    def _on_restart_theme_changed(self, *args):
        self.view.clear_buffer()
        self.disconnect()
        self.since_id = 0
        self.counter = 0
        self.start()

    def _on_reconnect_credential(self, *args):
        self._on_restart_theme_changed()

    def _on_error(self, e):
        print "Error: ", e
