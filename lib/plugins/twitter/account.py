from ...twittytwister import twitter, txml
from oauth import oauth

from api import TwitterAPIDict
from getauthtoken import CONSUMER
from ...utils.settings import SETTINGS_TWITTER
from ...utils.iconimage import WebIconImage
from ..base.getauthtoken import AuthorizedAccount


class TwitterIcon(WebIconImage):

    def __init__(self):
        self.icon_name = 'twitter.ico'
        self.icon_url = 'http://www.twitter.com/favicon.ico'

class AuthorizedTwitterAccount(AuthorizedAccount):

    SETTINGS = SETTINGS_TWITTER
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
            # FIXME
            # self.api.configuration().addCallback(self._on_get_configuration)
            pass

    def _on_get_configuration(self, data):
        AuthorizedTwitterAccount.CONFIG = data

    def _on_update_credential(self, account, unknown):
        token = self._get_token()
        self.api.update_token(token)
        self.emit("update-credential", None)

class Twitter(twitter.Twitter):

    def home_timeline(self, delegate, params={}, extra_args=None):
        return self.__get_json('/statuses/home_timeline.json', delegate, params,
                               extra_args=extra_args)


    def mentions(self, delegate, params={}, extra_args=None):
        return self.__get_json('/statuses/mentions_timeline.json', delegate, params,
                               extra_args=extra_args)

    def direct_messages(self, delegate, params={}, extra_args=None):
        return self.__get_json('/direct_messages.json', delegate, params,
                               extra_args=extra_args)


    def list_timeline(self, delegate, params={}, extra_args=None):
        return self.__get_json('/lists/statuses.json', delegate, params,
            extra_args=extra_args)

    def user_timeline(self, delegate, params={}, extra_args=None):
        return self.__get_json('/statuses/user_timeline.json', delegate, params,
            extra_args=extra_args)

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
    pass
