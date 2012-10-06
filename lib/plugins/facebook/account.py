import json
from oauth import oauth
import urllib

from gi.repository import GObject
from ...utils.settings import SETTINGS_TWITTER
from ...utils.iconimage import WebIconImage
from ...utils.urlgetautoproxy import urlget_with_autoproxy


class FacebookIcon(WebIconImage):

    def __init__(self):
        self.icon_name = 'facebook.png'
        self.icon_url = 'http://www.facebook.com/favicon.ico'

class AuthorizedFacebookAccount(GObject.GObject):

    def __init__(self, user_name, token, secret):
        super(AuthorizedFacebookAccount, self).__init__()
        self.api = Facebook(token=token)
        self.icon = FacebookIcon()

#    def _on_update_credential(self, account, unknown):
#        token = self._get_token()
#        self.api.update_token(token)
#        self.emit("update-credential", None)

class Facebook(object):

    def __init__(self, token):
        self.token = token

    def home_timeline(self, cb, params):
        url = 'https://graph.facebook.com/me/home'
        url += '?access_token=%s&locale=ja' % self.token 
        if params:
            url += '&'+self._urlencode(params)

        print url
        return urlget_with_autoproxy(str(url), cb=cb)

    def feed(self, username):
        pass

    def _urlencode(self, h):
        rv = []
        for k,v in h.iteritems():
            rv.append('%s=%s' %
                (urllib.quote(k.encode("utf-8")),
                urllib.quote(v.encode("utf-8"))))
        return '&'.join(rv)
