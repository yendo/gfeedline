#
# gfeedline - Gnome Social Feed Reader
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

from ...utils.nullobject import Null
from output import TwitterOutput, TwitterSearchOutput, TwitterFeedOutput


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

        null = Null()
        for api in all_api:
            self[api(null).name] = api

class TwitterAPIBase(object):

    def __init__(self, authed=None):
        self.authed = authed
        self.include_rt = True

        self._get_output_class()
        self._setup()

    def create_obj(self, view, argument, options):
        obj = self.output(self, self.authed, view, argument, options)
        return obj

    def get_options(self, argument):
        return {}

    def _get_output_class(self):
        self.output= TwitterOutput

class TwitterFeedAPIBase(TwitterAPIBase):

    def _get_output_class(self):
        self.output = TwitterFeedOutput

    def get_options(self, argument):
        return None


class TwitterAPIHomeTimeLine(TwitterAPIBase):

    def _setup(self):
        self.api = self.authed.api.home_timeline
        self.name = 'Home TimeLine'

class TwitterAPIListTimeLine(TwitterAPIBase):

    def _setup(self):
        self.api = self.authed.api.list_timeline
        self.name = 'List TimeLine'

    def get_options(self, argument):
        list_name = argument.split('/')
        params = {'owner_screen_name': list_name[0], 'slug': list_name[1]}
        return params

class TwitterAPIMentions(TwitterAPIBase):

    def _setup(self):
        self.api = self.authed.api.mentions
        self.name = 'Mentions'

class TwitterAPIDirectMessages(TwitterAPIBase):

    def _setup(self):
        self.api = self.authed.api.direct_messages
        self.name = 'Direct Messages'


class TwitterAPIUserStream(TwitterFeedAPIBase):

    def _setup(self):
        self.api = self.authed.api.userstream
        self.name = 'User Stream'

class TwitterAPITrack(TwitterFeedAPIBase):

    def _setup(self):
        self.api = self.authed.api.track
        self.name = 'Track'
        self.include_rt = False

    def get_options(self, argument):
        return [ x.strip() for x in argument.split(',') ]


class TwitterSearchAPI(TwitterAPIBase):

    def _setup(self):
        self.api = self.authed.api.search
        self.name = 'Search'
        self.include_rt = False

    def _get_output_class(self):
        self.output= TwitterSearchOutput

    def get_options(self, argument):
        return {'q': argument}

