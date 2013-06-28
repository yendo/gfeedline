#
# gfeedline - A Social Networking Client
#
# Copyright (c) 2012-2013, Yoshizumi Endo.
# Licence: GPL3

from ...utils.settings import SETTINGS_TWITTER
from ..base.api import APIBase
from output import TwitterRestOutput, TwitterSearchOutput, TwitterFeedOutput, TwitterRelatedResultOutput, TwitterUserTimeLineOutput


class TwitterAPIDict(dict):

    def __init__(self):
        all_api = [
             TwitterAPIHomeTimeLine,
             TwitterAPIUserTimeLine,
             TwitterAPIListTimeLine,
             TwitterAPIMentions,
             TwitterAPIDirectMessages,
             TwitterAPIFavoritesList,
             TwitterSearchAPI,

             TwitterAPIUserStream,
             TwitterAPITrack,

             TwitterAPIRelatedResults,
             ]

#        if SETTINGS_TWITTER.get_boolean('hometimeline-api'):
#            all_api.append(TwitterAPIHomeTimeLine)

        for api in all_api:
            self[api.name] = api

    def get_default(self):
        return TwitterAPIUserStream

class TwitterAPIBase(APIBase):

    output = TwitterRestOutput
    tooltip_for_argument = ''
    
    connections = 0
    rate_limit = 15

    def __init__(self, account, options):
        super(TwitterAPIBase, self).__init__(account, options)
        self.__class__.connections += 1

    def exit(self):
        self.__class__.connections -= 1

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
    output = TwitterUserTimeLineOutput
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
    tooltip_for_argument = _('The format is "username/listname".  '
                             'ex) yendo0206/gfeedline')

    def _get_api(self):
        return self.account.api.list_timeline

    def get_options(self, argument):
        list_name = argument.split('/')

        if len(list_name) == 2:
            params = {'owner_screen_name': list_name[0], 'slug': list_name[1]}
        else:
            print "Error: Invalid list name."
            params = {}

        params['include_rts']= '1' if self.options.get('include_rts') else '0'

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

class TwitterAPIFavoritesList(TwitterAPIBase):

    name = _('Favorites')

    def _get_api(self):
        return self.account.api.fav_list

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
        is_event = entry_dict.get('event')

        has_other_view = (is_own_tweet and is_reply) or is_event 
        view_target = _('Mentions') if has_other_view else None
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
