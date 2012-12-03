import urllib

from oauth import oauth

from api import TumblrAPIDict
from getauthtoken import CONSUMER
from ..base.getauthtoken import AuthorizedAccount
from ...utils.settings import SETTINGS_TUMBLR
from ...utils.iconimage import WebIconImage
from ...utils.urlgetautoproxy import urlget_with_autoproxy

class TumblrIcon(WebIconImage):

    def __init__(self):
        self.icon_name = 'twitter.gif'
        self.icon_url = 'http://assets.tumblr.com/images/favicon.gif'

class AuthorizedTumblrAccount(AuthorizedAccount):

    SETTINGS = SETTINGS_TUMBLR

    def __init__(self, user_name, key, secret, idnum=None):
        super(AuthorizedTumblrAccount, self).__init__()

        token = self._get_token(user_name, key, secret)
        self.source = 'Tumblr'
        self.api = Tumblr(consumer=CONSUMER, token=token)
        self.api_dict = TumblrAPIDict()
        self.icon = TumblrIcon()

class Tumblr(object):

    def __init__(self, consumer, token):
        self.consumer = consumer
        self.token =token
        self.signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

    def dashboard(self, cb, params=None):
        url = str('http://api.tumblr.com/v2/user/dashboard')

        if params:
            url += '?'+urllib.urlencode(params)
        headers = self.make_oauth_header('GET', url, params)

        return urlget_with_autoproxy(url, cb=cb, headers=headers)

    def posts(self, cb, params):
        '''Get posts'''

        hostname = params.pop('hostname')
        hostname = hostname + '.tumblr.com'
        url = str('http://api.tumblr.com/v2/blog/%s/posts') % str(hostname)

        params.update({'api_key': self.consumer.key})
        url += '?'+urllib.urlencode(params)

        return urlget_with_autoproxy(url, cb=cb)

    def user_info(self, cb):
        url = str('http://api.tumblr.com/v2/user/info')
        headers = self.make_oauth_header('GET', url)
        urlget_with_autoproxy(url, cb=cb, headers=headers)

    def _cb(self, *args):
        print "!",args

    def make_oauth_header(self, method, url, parameters={}, headers={}):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
            self.consumer, token=self.token, 
            http_method=method, http_url=url, parameters=parameters)
        oauth_request.sign_request(self.signature_method, self.consumer, self.token)

        headers.update(oauth_request.to_header())
        return headers
