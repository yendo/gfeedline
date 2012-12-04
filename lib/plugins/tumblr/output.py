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

    ENTRY_TYPE = {
        'text': TumblrTextEntry,
        'photo': TumblrPhotosEntry,
        'quote': TumblrEntry,
        'link': TumblrLinkEntry,
        'chat': TumblrChatEntry,
        'audio': TumblrAudioEntry,
        'video': TumblrVideoEntry,
        'answer': TumblrAnswerEntry,
        }

    def _get_all_entries(self, d):
        return d['response']['posts']

    def _get_entry_obj(self, entry):
        entry_class = self.ENTRY_TYPE.get(entry['type']) or TumblrEntry
        return entry_class(entry)

    def _get_interval_seconds(self):
        return 120
