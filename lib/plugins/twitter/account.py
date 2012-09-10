from ...twittytwister import twitter, txml
from oauth import oauth

from gi.repository import GObject
from getauthtoken import CONSUMER
from ...utils.settings import SETTINGS_TWITTER
from ...utils.iconimage import WebIconImage


class TwitterIcon(WebIconImage):

    def __init__(self):
        self.icon_name = 'twitter.ico'
        self.icon_url = 'http://www.twitter.com/favicon.ico'

class AuthorizedTwitterAccount(GObject.GObject):

    __gsignals__ = {
        'update-credential': (GObject.SignalFlags.RUN_LAST, None, (object, )),
        }

    CONFIG = None

    def __init__(self, user_name, key, secret):
        super(AuthorizedTwitterAccount, self).__init__()

        token = self._get_token(user_name, key, secret)
        self.api = TwitterFeed(consumer=CONSUMER, token=token)
        #SETTINGS_TWITTER.connect("changed::access-secret", 
        #                         self._on_update_credential)

        self.icon = TwitterIcon()

        if not AuthorizedTwitterAccount.CONFIG:
            self.api.configuration().addCallback(self._on_get_configuration)

    def _on_get_configuration(self, data):
        AuthorizedTwitterAccount.CONFIG = data

    def _on_update_credential(self, account, unknown):
        token = self._get_token()
        self.api.update_token(token)
        self.emit("update-credential", None)

    def _get_token(self, user_name, key, secret):
        token = oauth.OAuthToken(key, secret) if key and secret else None
        self.user_name = user_name if token else None

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

    def update_with_media(self, status, image_file, params=None):
        with open(image_file, 'rb') as fh:
            image_binary = fh.read()

        fields = [('status', status), ('media[]', image_binary)]
        if params:
            fields += params.items()

        return self.__postMultipart(
            'https://upload.twitter.com/1/statuses/update_with_media.xml',
            fields=tuple(fields))

    def update_token(self, token):
        self.use_auth = True
        self.use_oauth = True
        self.consumer = CONSUMER
        self.token = token
        self.signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

class TwitterFeed(Twitter, twitter.TwitterFeed):

    def userstream(self, delegate, args=None):
        return self._rtfeed('https://userstream.twitter.com/2/user.json',
                            delegate, args)
