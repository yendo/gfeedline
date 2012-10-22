import urllib
import cgi

from oauth import oauth
from gi.repository import GObject


SIGNATURE_METHOD = oauth.OAuthSignatureMethod_HMAC_SHA1()

class AuthorizedAccount(GObject.GObject):

    SETTINGS = None

    def __init__(self):
        super(AuthorizedAccount, self).__init__()

    def get_recent_api(self, label_list, feedliststore):
        recent = self.SETTINGS.get_int('recent-target')
        old_target = feedliststore[Column.TARGET].decode('utf-8') \
            if feedliststore else None

        default_menuitem = self.api_dict.get_default()
        print default_menuitem
        num = label_list.index(old_target) if old_target in label_list \
            else recent if recent >= 0 else label_list.index(default_menuitem)

        return num

    def set_recent_api(self, num):
        self.SETTINGS.set_int('recent-target', num)

    def _get_token(self, user_name, key, secret):
        token = oauth.OAuthToken(key, secret) if key and secret else None
        self.user_name = user_name if token else None
        return token

class Authorization(object):

    CALLBACK = 'oob'
    REQUEST_TOKEN_URL = None
    ACCESS_TOKEN_URL = None
    AUTHORIZE_URL = None

    def open_authorize_uri(self):

        request = oauth.OAuthRequest.from_consumer_and_token(
            self.CONSUMER, 
            callback=self.CALLBACK,
            http_url=self.REQUEST_TOKEN_URL)
        request.sign_request(SIGNATURE_METHOD, self.CONSUMER, token=None)

        stream = urllib.urlopen(request.to_url())
        tokendata = stream.read()
        token = oauth.OAuthToken.from_string(tokendata)

        uri = (self.AUTHORIZE_URL + token.key)
        return uri, token

    def get_access_token(self, pin, request_token):
        request = oauth.OAuthRequest.from_consumer_and_token(
            self.CONSUMER,
            parameters={'oauth_verifier': pin,
                        'oauth_token': request_token.key},
            http_url=self.ACCESS_TOKEN_URL)
        request.sign_request(SIGNATURE_METHOD, self.CONSUMER, token=request_token)

        stream = urllib.urlopen(request.to_url())
        tokendata = stream.read()

        token = oauth.OAuthToken.from_string(tokendata)
        params = cgi.parse_qs(tokendata, keep_blank_values=False)

        return token, params
