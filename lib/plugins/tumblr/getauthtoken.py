import webbrowser
import urllib
import cgi
import re

from oauth import oauth

from gi.repository import Gtk, GObject, WebKit

from ..base.authwebkit import AuthWebKitScrolledWindow

consumer_key = 'Ygjp6HoG7BCGGTVAamZj6pDJK4M1phyHH0jX7cDB6983VX5EDg'
consumer_secret = 'ychftk5UOQKaYn9NHVPKLQiDS8SqPAJZqNK0AbDaIEd5RtohTI'
CONSUMER = oauth.OAuthConsumer(consumer_key, consumer_secret)
SIGNATURE_METHOD = oauth.OAuthSignatureMethod_HMAC_SHA1()


class TumblrAuthorization(object):

    def open_authorize_uri(self):

        request = oauth.OAuthRequest.from_consumer_and_token(
            CONSUMER, 
            callback='http://code.google.com/p/gfeedline/',
            http_url= 'http://www.tumblr.com/oauth/request_token' )
        request.sign_request(SIGNATURE_METHOD, CONSUMER, token=None)

        stream = urllib.urlopen(request.to_url())
        tokendata = stream.read()
        token = oauth.OAuthToken.from_string(tokendata)
        uri = ('http://www.tumblr.com/oauth/authorize'
               '?theme=android&oauth_token=' + token.key)

        #webbrowser.open(uri)
        return uri, token

    def get_access_token(self, pin, request_token):
        request = oauth.OAuthRequest.from_consumer_and_token(
            CONSUMER,
            parameters={'oauth_verifier': pin,
                        'oauth_token': request_token.key},
            http_url= 'http://www.tumblr.com/oauth/access_token' )
        request.sign_request(SIGNATURE_METHOD, CONSUMER, token=request_token)

        stream = urllib.urlopen(request.to_url())
        tokendata = stream.read()

        token = oauth.OAuthToken.from_string(tokendata)
        params = cgi.parse_qs(tokendata, keep_blank_values=False)

#        screen_name = params['screen_name'][0]
        screen_name = 'dummy'

        result = {'screen-name': screen_name,
                  'access-token': token.key,
                  'access-secret': token.secret}

        return result
