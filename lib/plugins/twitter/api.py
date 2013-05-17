#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012, Yoshizumi Endo.
# Licence: GPL3

from output import TwitterRestOutput, TwitterSearchOutput, TwitterFeedOutput, TwitterRelatedResultOutput


class TwitterAPIDict(dict):

    def __init__(self):
        all_api = [
             TwitterAPIHomeTimeLine,
             TwitterAPIUserTimeLine,
             TwitterAPIListTimeLine,
             TwitterAPIMentions,
             TwitterAPIDirectMessages,
             TwitterSearchAPI,

             TwitterAPIUserStream,
             TwitterAPITrack,

             TwitterAPIRelatedResults,
             ]

        for api in all_api:
            self[api.name] = api

    def get_default(self):
        return TwitterAPIUserStream

class TwitterAPIBase(object):

    output = TwitterRestOutput
    include_rt = True
    has_argument = False
    has_popup_menu = True
    
    connections = 0
    rate_limit = 15

    def __init__(self, account):
        self.account = account
        self.api = self._get_api()
        self.__class__.connections += 1

    def exit(self):
        self.__class__.connections -= 1

    def get_options(self, argument):
        return {}

    def print_to_other_view(self, entry_dict):
        return None

class TwitterFeedAPIBase(TwitterAPIBase):

    output = TwitterFeedOutput

    def get_options(self, argument):
        return None


class TwitterAPIHomeTimeLine(TwitterAPIBase):

    name = _('Home TimeLine')

    def _get_api(self):
        return self.account.api.home_timeline

class TwitterAPIUserTimeLine(TwitterAPIBase):

    name = _('User TimeLine')
    has_argument = True
    rate_limit = 180

    def _get_api(self):
        return self.account.api.user_timeline

    def get_options(self, argument):
        return {'screen_name': argument}

class TwitterAPIListTimeLine(TwitterAPIBase):

    name = _('List TimeLine')
    has_argument = True
    rate_limit = 180

    def _get_api(self):
        return self.account.api.list_timeline

    def get_options(self, argument):
        list_name = argument.split('/')

        if len(list_name) == 2:
            params = {'owner_screen_name': list_name[0], 'slug': list_name[1]}
        else:
            print "Error: Invalid list name."
            params = {}

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

class TwitterAPIRelatedResults(TwitterAPIBase):

    name = _('Related Results')
    output = TwitterRelatedResultOutput
    has_argument = True

    def _get_api(self):
        return self.account.api.related_results

    def get_options(self, argument):
        args = argument.split('/')

        return {'from_user': args[0], 'to_user': args[1],
                'in_reply_to_status_id': args[2]} if len(args) >= 3 else {}
            
class TwitterAPIUserStream(TwitterFeedAPIBase):

    name = _('User Stream')

    def _get_api(self):
        return self.account.feedapi.user

    def print_to_other_view(self, entry_dict):
        is_own_tweet = entry_dict['user_name'] == self.account.user_name
        is_reply = entry_dict['status_body'].count('@')

        view_target = _('Mentions') if is_own_tweet and is_reply else None
        return view_target

class TwitterAPITrack(TwitterFeedAPIBase):

    name = _('Track')
    include_rt = False
    has_argument = True

    def _get_api(self):
        return self.account.feedapi.track

    def get_options(self, argument):
        return [ x.strip() for x in argument.split(' ') ]


class TwitterSearchAPI(TwitterAPIBase):

    output= TwitterSearchOutput
    name = _('Search')
    include_rt = False
    has_argument = True
    rate_limit = 180

    def _get_api(self):
        return self.account.api.search

    def get_options(self, argument):
        return {'q': argument}
