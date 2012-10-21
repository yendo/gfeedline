#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

from twisted.internet import reactor

from entry import *
from ..base.output import OutputBase

class TumblrRestOutput(OutputBase):

    SINCE = 'since_id'
    SINCE_KEY = 'id'

    def _get_all_entries(self, d):
        return d['response']['posts']

    def _get_entry_obj(self, entry):
        return TumblrEntry(entry)

    def _get_interval_seconds(self):
        return 120
