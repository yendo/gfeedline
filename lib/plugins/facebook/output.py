#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

from entry import *
from ..base.output import OutputBase

class FacebookRestOutput(OutputBase):

    SINCE = 'since'
    SINCE_KEY = 'created_time'

    def _get_all_entries(self, d):
        return d['data']

    def _get_entry_obj(self, entry):
        return FacebookEntry(entry)

    def print_entry(self, entry, is_first_call=False):
        entry_dict = self._get_entry_obj(entry).get_dict(self.api)
        if not entry_dict:
            return

        has_notify = self.options.get('notification') 
        style = 'status'

        is_new_update = self.last_id < entry_dict['epoch']
        if not str(self.last_id).isdigit() or is_new_update:
            self.last_id = entry_dict['epoch']

        self.view.update(entry_dict, style, has_notify, 
                         is_first_call, is_new_update)

