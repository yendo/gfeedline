#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012-2013, Yoshizumi Endo.
# Licence: GPL3

from output import TumblrRestOutput
from ..base.api import APIBase


class TumblrAPIDict(dict):

    def __init__(self):
        all_api = [
             TumblrAPIDashboard,
             TumblrAPIPosts,
             ]

        for api in all_api:
            self[api.name] = api

    def get_default(self):
        return TumblrAPIDashboard

class TumblrAPIBase(APIBase):

    output = TumblrRestOutput

class TumblrAPIDashboard(TumblrAPIBase):

    name = _('Dashboard')

    def _get_api(self):
        return self.account.api.dashboard

class TumblrAPIPosts(TumblrAPIBase):

    name = _('Posts')
    has_argument = True

    def _get_api(self):
        return self.account.api.posts

    def get_options(self, argument):
        return {'hostname': argument}
