#!/usr/bin/python

from oauth import oauth
import webbrowser
import urllib
import cgi

consumer_key = 'zniRMF8u0aOuLPb1Q94QNg'
consumer_secret = 'iuYLw5KPRodf5crYj3caIPxqVF62hIm3ZRziUbtuM'
uri_prefix = 'http://twitter.com'
consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
SIGNATURE_METHOD = oauth.OAuthSignatureMethod_HMAC_SHA1()

class TwitterAuthorization(object):

    def open_authorize_uri(self):

        request = oauth.OAuthRequest.from_consumer_and_token(
            consumer, 
            callback='oob',
            http_url= 'http://twitter.com/oauth/request_token' )
        request.sign_request(SIGNATURE_METHOD, consumer, token=None)

        stream = urllib.urlopen(request.to_url())
        tokendata = stream.read()
        token = oauth.OAuthToken.from_string(tokendata)

        uri = 'http://twitter.com/oauth/authorize?mode=desktop&oauth_token=' + token.key

        webbrowser.open(uri)
        return token

    def get_access_token(self, pin, request_token):
        request = oauth.OAuthRequest.from_consumer_and_token(
            consumer,
            parameters={'oauth_verifier': pin,
                        'oauth_token': request_token.key},
            http_url= 'http://twitter.com/oauth/access_token',
            )
        request.sign_request(SIGNATURE_METHOD, consumer, token=request_token)

        stream = urllib.urlopen(request.to_url())
        tokendata = stream.read()

        token = oauth.OAuthToken.from_string(tokendata)
        params = cgi.parse_qs(tokendata, keep_blank_values=False)
        screen_name = params['screen_name'][0]

        #print "|", screen_name, token.key, token.secret
        result = {'screen-name': screen_name,
                  'access-token': token.key,
                  'access-secret': token.secret}

        return result

if __name__ == '__main__':

    auth = TwitterAuthToken()
    token = auth.open_authorize_uri()
    pin = raw_input()
    auth.get_access_token(pin, token)
