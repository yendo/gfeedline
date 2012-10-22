#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

from output import TumblrRestOutput


class TumblrAPIDict(dict):

    def __init__(self):
        all_api = [
             TumblrAPIDashboard,
             ]

        for api in all_api:
            self[api.name] = api

    def get_default(self):
        return TumblrAPIDashboard

class TumblrAPIBase(object):

    output = TumblrRestOutput
    include_rt = True
    has_argument = False
    has_popup_menu = True

    def __init__(self, account):
        self.account = account
        self.api = self._get_api()

    def get_options(self, argument):
        return {}

class TumblrAPIDashboard(TumblrAPIBase):

    name = _('Dashboard')

    def _get_api(self):
        return self.account.api.dashboard
