from twisted.internet import defer
from oauth import oauth
from ...twittytwister import twitter, tjson

from api import TwitterAPIDict
from getauthtoken import CONSUMER
from ...utils.settings import SETTINGS_TWITTER
from ...utils.iconimage import WebIconImage
from ..base.getauthtoken import AuthorizedAccount
from tweetentry import DictObj

class TwitterIcon(WebIconImage):

    def __init__(self):
        self.icon_name = 'twitter.ico'
        self.icon_url = 'http://www.twitter.com/favicon.ico'

class TwitterConfig(DictObj):

    def __init__(self):
        self.d = { "characters_reserved_per_media": 23,
                   "photo_size_limit": 3145728,
                   "short_url_length_https": 23,
                   "short_url_length": 22 }
        self.is_updated = False

    def update_config(self, api):
        if not self.is_updated:
            self.is_updated = True
            api.configuration().addCallback(self._on_get_config)

    def _on_get_config(self, data):
        self.d.update(data)

class AuthorizedTwitterAccount(AuthorizedAccount):

    SETTINGS = SETTINGS_TWITTER
    CONFIG = TwitterConfig()

    def __init__(self, user_name, key, secret, idnum):
        super(AuthorizedTwitterAccount, self).__init__()

        token = self._get_token(user_name, key, secret)
        self.api = Twitter(consumer=CONSUMER, token=token)
        self.feedapi = twitter.TwitterFeed(consumer=CONSUMER, token=token)
        #SETTINGS_TWITTER.connect("changed::access-secret", 
        #                         self._on_update_credential)

        self.source = 'Twitter'
        self.icon = TwitterIcon()
        self.api_dict = TwitterAPIDict()

        AuthorizedTwitterAccount.CONFIG.update_config(self.api)
        
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

    def update(self, status, source=None, params={}):
        params = params.copy()
        params['status'] = status
        if source:
            params['source'] = source
        return self.__post('/statuses/update.json', params)

    def retweet(self, status_id, delegate):
        return self.__post('/statuses/retweet/%s.json' % status_id)

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

        return self.__get_json('/search/tweets.json', delegate, params,
                               extra_args=extra_args)

    def show(self, status_id, delegate, params=None, extra_args=None):
        if params is None:
            params = {}
        params['id'] = str(status_id)

        return self.__get_json('/statuses/show.json', delegate, params,
            extra_args=extra_args)

    def related_results(self, delegate, delegate_for_replyto, 
                        params=None, extra_args=None):
        status_id = params.get('in_reply_to_status_id')
        from_user = params.get('from_user')
        to_user = params.get('to_user')

        query = '(from:%s to:%s) OR (from:%s to:%s)' % (
            from_user, to_user, to_user, from_user)
        defer = self.search(delegate, {'q': query, 'since_id': status_id})
        defer.pause()

        cb = lambda data: self._related_results_cb(
            data, delegate_for_replyto, defer)
        self.show(status_id, cb)

        return defer

    def _related_results_cb(self, data, delegate, defer):
        in_reply_to_status_id = data.get('in_reply_to_status_id')
        delegate(data)

        if in_reply_to_status_id:
            cb = lambda data: self._related_results_cb(data, delegate, defer)
            self.show(in_reply_to_status_id, cb)
        else:
            defer.unpause()

    def fav(self, status_id):
        return self.__post('/favorites/create.json', {'id': status_id})

    def unfav(self, status_id):
        return self.__post('/favorites/destroy.json', {'id': status_id})

    def update_with_media(self, status, image_file, params=None):
        with open(image_file, 'rb') as fh:
            image_binary = fh.read()

        fields = [('status', status), ('media[]', image_binary)]
        if params:
            fields += params.items()

        return self.__postMultipart('/statuses/update_with_media.json',
                                    fields=tuple(fields))

    def configuration(self):
        url = '/help/configuration.json'
        d = defer.Deferred()

        self.__downloadPage(url, tjson.Parser(lambda u: d.callback(u))) \
            .addErrback(lambda e: d.errback(e))

        return d

    def update_token(self, token):
        self.use_auth = True
        self.use_oauth = True
        self.consumer = CONSUMER
        self.token = token
        self.signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

    def __get_json(self, path, delegate, params, parser_factory=tjson.Parser, extra_args=None):
        parser = parser_factory(delegate)
        return self.__downloadPage(path, parser, params)
