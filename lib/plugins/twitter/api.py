#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

from ...utils.nullobject import Null
from output import TwitterRestOutput, TwitterSearchOutput, TwitterFeedOutput


class TwitterAPIDict(dict):

    def __init__(self):
        all_api = [
             TwitterAPIHomeTimeLine,
             TwitterAPIListTimeLine,
             TwitterAPIMentions,
             TwitterAPIDirectMessages,
             TwitterSearchAPI,

             TwitterAPIUserStream,
             TwitterAPITrack,
             ]

        for api in all_api:
            self[api().name] = api

class TwitterAPIBase(object):

    output = TwitterRestOutput
    include_rt = True
    has_argument = False
    has_popup_menu = True

    def __init__(self, account=None):
        self.account = account or Null()
        self.api = self._get_api()

    def get_options(self, argument):
        return {}


class TwitterFeedAPIBase(TwitterAPIBase):

    output = TwitterFeedOutput

    def get_options(self, argument):
        return None


class TwitterAPIHomeTimeLine(TwitterAPIBase):

    name = _('Home TimeLine')

    def _get_api(self):
        return self.account.api.home_timeline

class TwitterAPIListTimeLine(TwitterAPIBase):

    name = _('List TimeLine')
    has_argument = True

    def _get_api(self):
        return self.account.api.list_timeline

    def get_options(self, argument):
        list_name = argument.split('/')
        params = {'owner_screen_name': list_name[0], 'slug': list_name[1]}
        return params

class TwitterAPIMentions(TwitterAPIBase):

    name = _('Mentions')

    def _get_api(self):
        return self.account.api.mentions

class TwitterAPIDirectMessages(TwitterAPIBase):

    name = _('Direct Messages')
    has_popup_menu = False

    def _get_api(self):
        return self.account.api.direct_messages

class TwitterAPIUserStream(TwitterFeedAPIBase):

    name = _('User Stream')

    def _get_api(self):
        return self.account.api.userstream

class TwitterAPITrack(TwitterFeedAPIBase):

    name = _('Track')
    include_rt = False
    has_argument = True

    def _get_api(self):
        return self.account.api.track

    def get_options(self, argument):
        return [ x.strip() for x in argument.split(' ') ]


class TwitterSearchAPI(TwitterAPIBase):

    output= TwitterSearchOutput
    name = _('Search')
    include_rt = False
    has_argument = True

    def _get_api(self):
        return self.account.api.search

    def get_options(self, argument):
        return {'q': argument}
