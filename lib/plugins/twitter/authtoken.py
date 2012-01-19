from twittytwister import twitter, txml
from oauth import oauth

from authorize import consumer

from ...utils.settings import SETTINGS_TWITTER


class Twitter(twitter.Twitter):

    def list_timeline(self, delegate, params={}, extra_args=None):
        return self.__get('/1/lists/statuses.xml',
                delegate, params, txml.Statuses, extra_args=extra_args)

class TwitterFeed2(twitter.TwitterFeed):

    def userstream(self, delegate, args=None):
        return self._rtfeed('https://userstream.twitter.com/2/user.json',
                            delegate, args)

TwitterOauth = None
TwitterFeedOauth = None

def set_auth():
    key = SETTINGS_TWITTER.get_string('access-token')
    secret = SETTINGS_TWITTER.get_string('access-secret')
    token = oauth.OAuthToken(key, secret) if key and secret else None

    global TwitterOauth, TwitterFeedOauth
    TwitterOauth = Twitter(consumer=consumer, token=token)
    TwitterFeedOauth = TwitterFeed2(consumer=consumer, token=token)

set_auth()
