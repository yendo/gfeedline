from ...twittytwister import twitter, txml
from oauth import oauth

from api import TwitterAPIDict
from gi.repository import GObject
from getauthtoken import CONSUMER
from ...utils.settings import SETTINGS_TWITTER
from ...utils.iconimage import WebIconImage
from ...constants import Column

class TwitterIcon(WebIconImage):

    def __init__(self):
        self.icon_name = 'twitter.ico'
        self.icon_url = 'http://www.twitter.com/favicon.ico'

class AuthorizedTwitterAccount(GObject.GObject):

    __gsignals__ = {
        'update-credential': (GObject.SignalFlags.RUN_LAST, None, (object, )),
        }

    CONFIG = None

    def __init__(self, user_name, key, secret, idnum):
        super(AuthorizedTwitterAccount, self).__init__()

        token = self._get_token(user_name, key, secret)
        self.api = TwitterFeed(consumer=CONSUMER, token=token)
        #SETTINGS_TWITTER.connect("changed::access-secret", 
        #                         self._on_update_credential)

        self.source = 'Twitter'
        self.icon = TwitterIcon()
        self.api_dict = TwitterAPIDict()

        if not AuthorizedTwitterAccount.CONFIG:
            self.api.configuration().addCallback(self._on_get_configuration)

    def get_recent_api(self, label_list, feedliststore):
        recent = SETTINGS_TWITTER.get_int('recent-target')
        old_target = feedliststore[Column.TARGET].decode('utf-8') \
            if feedliststore else None

        num = label_list.index(old_target) if old_target in label_list \
            else recent if recent >= 0 else label_list.index(_("User Stream"))

        return num

    def set_recent_api(self, num):
        SETTINGS_TWITTER.set_int('recent-target', num)

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
        return self.__get('/lists/statuses.xml',
                delegate, params, txml.Statuses, extra_args=extra_args)

    def user_timeline(self, delegate, params={}, extra_args=None):
        return self.__get('/statuses/user_timeline.xml', delegate, params,
                          txml.Statuses, extra_args=extra_args)

    def search(self, delegate, params=None, extra_args=None):
        if params is None:
            params = {}
        params['result_type'] = 'recent'

        return self.__doDownloadPage(self.search_url + '?' + self._urlencode(params),
            txml.Feed(delegate, extra_args), agent=self.agent)

    def related_results(self, delegate, params={}, extra_args=None):
        statusid = params['id']
        return self.__get_json('/related_results/show/%s.json' % statusid,
                delegate, params, extra_args=extra_args)

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
