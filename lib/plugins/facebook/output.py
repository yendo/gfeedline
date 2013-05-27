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
