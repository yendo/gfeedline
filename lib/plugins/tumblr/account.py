import urllib

from oauth import oauth

from api import TumblrAPIDict
from gi.repository import GObject
from getauthtoken import CONSUMER
from ...utils.settings import SETTINGS_TWITTER
from ...utils.iconimage import WebIconImage
from ...constants import Column

from ...utils.urlgetautoproxy import UrlGetWithAutoProxy

class TumblrIcon(WebIconImage):

    def __init__(self):
        self.icon_name = 'twitter.gif'
        self.icon_url = 'http://assets.tumblr.com/images/favicon.gif'

class AuthorizedTumblrAccount(GObject.GObject):

    __gsignals__ = {
        'update-credential': (GObject.SignalFlags.RUN_LAST, None, (object, )),
        }

    CONFIG = None

    def __init__(self, user_name, key, secret, idnum):
        super(AuthorizedTumblrAccount, self).__init__()

        token = self._get_token(user_name, key, secret)
        self.api = Tumblr(consumer=CONSUMER, token=token)


        self.source = 'Tumblr'
        self.icon = TumblrIcon()
        self.api_dict = TumblrAPIDict()

#        self.api.user_info()
#        self.api.dashboard()

    def get_recent_api(self, label_list, feedliststore):
        recent = SETTINGS_TWITTER.get_int('recent-target')
        old_target = feedliststore[Column.TARGET].decode('utf-8') \
            if feedliststore else None

        num = label_list.index(old_target) if old_target in label_list \
            else recent if recent >= 0 else label_list.index(_("User Stream"))

        return num

    def set_recent_api(self, num):
        SETTINGS_TWITTER.set_int('recent-target', num)

#    def _on_get_configuration(self, data):
#        AuthorizedTumblrAccount.CONFIG = data

    def _on_update_credential(self, account, unknown):
        token = self._get_token()
        self.api.update_token(token)
        self.emit("update-credential", None)

    def _get_token(self, user_name, key, secret):
        token = oauth.OAuthToken(key, secret) if key and secret else None
        self.user_name = user_name if token else None

        return token

class Tumblr(object):

    def __init__(self, consumer, token):
        self.consumer = consumer
        self.token =token
        self.signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()

    def dashboard(self, cb, params=None):
        url = str('http://api.tumblr.com/v2/user/dashboard')

        if params:
            url += '?'+urllib.urlencode(params)
        print url
        header = self.make_oauth_header('GET', url, params)

        return self.urlget_with_autoproxy(url, cb=cb, header=header)

    def user_info(self):
        url = str('http://api.tumblr.com/v2/user/info')
        header = self.make_oauth_header('GET', url)
        self.urlget_with_autoproxy(url, cb=self._cb, header=header)


    def _cb(self, *args):
        print "!",args
        
    def make_oauth_header(self, method, url, parameters={}, headers={}):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
            token=self.token, http_method=method, http_url=url, parameters=parameters)
        oauth_request.sign_request(self.signature_method, self.consumer, self.token)

        headers.update(oauth_request.to_header())
        return headers

    def urlget_with_autoproxy(self, url, arg=None, cb=None, method='GET', header=None):

        client = UrlGetWithAutoProxy(url)
        content_type = {'Content-Type' : 'application/x-www-form-urlencoded'}

        d = client.getPage(url, method=method, headers=header)
        if cb:
            d.addCallback(cb)
        d.addErrback(cb)

        return d
