import webbrowser
import urllib
import cgi
import re

from oauth import oauth

from gi.repository import Gtk, GObject, WebKit

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

class TumblrWebKitScrolledWindow(Gtk.ScrolledWindow):

    def __init__(self):
        super(TumblrWebKitScrolledWindow, self).__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        uri, self.token = TumblrAuthorization().open_authorize_uri()

        w = WebKit.WebView.new()
        w.set_vexpand(True)
        w.load_uri(uri)
        w.connect("document-load-finished", self._get_document_cb)

        self.add(w)
        self.show_all()

    def _get_document_cb(self, w, e):
        url = w.get_property('uri')
        re_verifier = re.compile('.*oauth_verifier=(.*)&?.*')
        re_token = re.compile('.*oauth_token=(.*)&.*')
        login_url = 'https://www.tumblr.com/login'
        error_url = 'http://www.tumblr.com/error'

        if url.startswith(login_url):
            self.emit("login-started", None)
        elif re_token.search(url):
            verifier = re_verifier.sub("\\1", url)
            token = re_token.sub("\\1", url)
            print "OAUTH=",token, verifier

            result = TumblrAuthorization().get_access_token(verifier, self.token)

            self.emit("token-acquired", result)

        elif url.startswith(error_url):
            self.emit("error-occurred", None)

for signal in ["login-started", "token-acquired", "error-occurred"]:
    GObject.signal_new(signal, TumblrWebKitScrolledWindow,
                       GObject.SignalFlags.RUN_LAST, None,
                       (GObject.TYPE_PYOBJECT,))

if __name__ == '__main__':

    auth = TumblrAuthorization()
#    token = auth.open_authorize_uri()
#    pin = raw_input()
#    auth.get_access_token(pin, token)
