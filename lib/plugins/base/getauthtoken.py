import urllib
import cgi

from oauth import oauth

SIGNATURE_METHOD = oauth.OAuthSignatureMethod_HMAC_SHA1()


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
