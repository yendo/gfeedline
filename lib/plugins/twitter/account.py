from ...twittytwister import twitter, txml
from oauth import oauth

from getauthtoken import consumer
from ...utils.settings import SETTINGS_TWITTER

class AuthorizedTwitterAccount(object):

    def __init__(self):
        token = self._get_token()
        self.api = TwitterFeed(consumer=consumer, token=token)

    def update_credential(self):
        token = self._get_token()
        self.api.update_token(token)

    def _get_token(self):
        key = SETTINGS_TWITTER.get_string('access-token')
        secret = SETTINGS_TWITTER.get_string('access-secret')
        token = oauth.OAuthToken(key, secret) if key and secret else None
        return token

class Twitter(twitter.Twitter):

    def list_timeline(self, delegate, params={}, extra_args=None):
        return self.__get('/1/lists/statuses.xml',
                delegate, params, txml.Statuses, extra_args=extra_args)

    def search(self, delegate, params=None, extra_args=None):
        if params is None: 
            params = {}
        params['result_type'] = 'recent'
        return self.__doDownloadPage(self.search_url + '?' + self._urlencode(params),
            txml.Feed(delegate, extra_args), agent=self.agent)

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
