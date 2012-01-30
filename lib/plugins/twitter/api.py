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

    def __init__(self, account=None):
        self.account = account or Null()
        self.include_rt = True
        self.has_argument = False

        self._get_output_class()
        self._setup()

    def create_obj(self, view, argument, options):
        obj = self.output(self, self.account, view, argument, options)
        return obj

    def get_options(self, argument):
        return {}

    def _get_output_class(self):
        self.output= TwitterRestOutput

class TwitterFeedAPIBase(TwitterAPIBase):

    def _get_output_class(self):
        self.output = TwitterFeedOutput

    def get_options(self, argument):
        return None


class TwitterAPIHomeTimeLine(TwitterAPIBase):

    def _setup(self):
        self.api = self.account.api.home_timeline
        self.name = 'Home TimeLine'

class TwitterAPIListTimeLine(TwitterAPIBase):

    def _setup(self):
        self.api = self.account.api.list_timeline
        self.name = 'List TimeLine'
        self.has_argument = True

    def get_options(self, argument):
        list_name = argument.split('/')
        params = {'owner_screen_name': list_name[0], 'slug': list_name[1]}
        return params

class TwitterAPIMentions(TwitterAPIBase):

    def _setup(self):
        self.api = self.account.api.mentions
        self.name = 'Mentions'

class TwitterAPIDirectMessages(TwitterAPIBase):

    def _setup(self):
        self.api = self.account.api.direct_messages
        self.name = 'Direct Messages'


class TwitterAPIUserStream(TwitterFeedAPIBase):

    def _setup(self):
        self.api = self.account.api.userstream
        self.name = 'User Stream'

class TwitterAPITrack(TwitterFeedAPIBase):

    def _setup(self):
        self.api = self.account.api.track
        self.name = 'Track'
        self.include_rt = False
        self.has_argument = True

    def get_options(self, argument):
        return [ x.strip() for x in argument.split(' ') ]


class TwitterSearchAPI(TwitterAPIBase):

    def _setup(self):
        self.api = self.account.api.search
        self.name = 'Search'
        self.include_rt = False
        self.has_argument = True

    def _get_output_class(self):
        self.output= TwitterSearchOutput

    def get_options(self, argument):
        return {'q': argument}

