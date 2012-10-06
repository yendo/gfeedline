#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

from output import FacebookRestOutput


class FacebookAPIDict(dict):

    def __init__(self):
        all_api = [
             FacebookAPIHome,
             ]

        for api in all_api:
            self[api.name] = api

class FacebookAPIBase(object):

    output = FacebookRestOutput
    include_rt = True
    has_argument = False
    has_popup_menu = True

    def __init__(self, account):
        self.account = account
        self.api = self._get_api()

    def get_options(self, argument):
        return {}

    def print_to_other_view(self, entry_dict):
        return None

class FacebookAPIHome(FacebookAPIBase):

    name = _('Home TimeLine') # FIXME

    def _get_api(self):
        return self.account.api.home_timeline
