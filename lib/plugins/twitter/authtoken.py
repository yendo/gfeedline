from twittytwister import twitter, txml
#from ...twittytwister2 import twitter, txml
from oauth import oauth

from authorize import consumer
from ...utils.settings import SETTINGS_TWITTER

class Twitter(twitter.Twitter):

    def list_timeline(self, delegate, params={}, extra_args=None):
        return self.__get('/1/lists/statuses.xml',
                delegate, params, txml.Statuses, extra_args=extra_args)


    def update_token(self, token):
        self.use_auth = True
        self.use_oauth = True
        self.consumer = consumer
        self.token = token
        self.signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

class TwitterFeed(Twitter, twitter.TwitterFeed):

    def userstream(self, delegate, args=None):
        return self._rtfeed('https://userstream.twitter.com/2/user.json',
                            delegate, args)

class AuthorizedTwitterAPI(object):

    rest = None
    feed = None

    def __init__(self):
        key = SETTINGS_TWITTER.get_string('access-token')
        secret = SETTINGS_TWITTER.get_string('access-secret')
        token = oauth.OAuthToken(key, secret) if key and secret else None

        self.rest = Twitter(consumer=consumer, token=token)
        self.feed = TwitterFeed(consumer=consumer, token=token)

key = SETTINGS_TWITTER.get_string('access-token')
secret = SETTINGS_TWITTER.get_string('access-secret')
token = oauth.OAuthToken(key, secret) if key and secret else None

AuthedTwitterRestAPI = Twitter(consumer=consumer, token=token)
AuthedTwitterFeedAPI = TwitterFeed(consumer=consumer, token=token)


def set_auth():
    key = SETTINGS_TWITTER.get_string('access-token')
    secret = SETTINGS_TWITTER.get_string('access-secret')
    token = oauth.OAuthToken(key, secret) if key and secret else None

    AuthedTwitterRestAPI.update_token(token)
    AuthedTwitterFeedAPI.update_token(token)
