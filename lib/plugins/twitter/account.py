from ...twittytwister import twitter, txml
from oauth import oauth

from gi.repository import GObject
from getauthtoken import consumer
from ...utils.settings import SETTINGS_TWITTER

class AuthorizedTwitterAccount(GObject.GObject):

    __gsignals__ = {
        'update-credential': (GObject.SignalFlags.RUN_LAST, None, (object, )),
        }

    def __init__(self):
        super(AuthorizedTwitterAccount, self).__init__()

        token = self._get_token()
        self.api = TwitterFeed(consumer=consumer, token=token)
        SETTINGS_TWITTER.connect("changed::access-secret", 
                                 self._on_update_credential)

    def _on_update_credential(self, account, unknown):
        token = self._get_token()
        self.api.update_token(token)
        self.emit("update-credential", None)

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

    def fav(self, status_id):
        return self.__post('/favorites/create/%s.xml' % status_id)

    def unfav(self, status_id):
        return self.__post('/favorites/destroy/%s.xml' % status_id)

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
