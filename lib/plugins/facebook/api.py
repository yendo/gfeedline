#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012-2013, Yoshizumi Endo.
# Licence: GPL3

from output import FacebookRestOutput
from ..base.api import APIBase


class FacebookAPIDict(dict):

    def __init__(self):
        all_api = [
             FacebookAPIHome,
             FacebookAPIWall,
             ]

        for api in all_api:
            self[api.name] = api

    def get_default(self):
        return FacebookAPIHome

class FacebookAPIBase(APIBase):

    output = FacebookRestOutput

class FacebookAPIHome(FacebookAPIBase):

    name = _('News Feed')

    def _get_api(self):
        return self.account.api.home

class FacebookAPIWall(FacebookAPIBase):

    name = _('Wall')
    has_argument = True

    def _get_api(self):
        return self.account.api.feed

    def get_options(self, argument):
        return {'user': argument}
