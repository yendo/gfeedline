import json
import urllib
from oauth import oauth

from gi.repository import GObject

from ...utils.settings import SETTINGS_FACEBOOK
from ...utils.iconimage import WebIconImage
from ...utils.urlgetautoproxy import urlget_with_autoproxy
from ...constants import Column
from api import FacebookAPIDict

class FacebookIcon(WebIconImage):

    def __init__(self):
        self.icon_name = 'facebook.png'
        self.icon_url = 'http://www.facebook.com/favicon.ico'

class AuthorizedFacebookAccount(GObject.GObject):

    def __init__(self, user_name, token, secret):
        super(AuthorizedFacebookAccount, self).__init__()

        self.api = Facebook(token=token)
        self.api_dict = FacebookAPIDict()
        self.icon = FacebookIcon()

    def get_recent_api(self, label_list, feedliststore):
        recent = SETTINGS_FACEBOOK.get_int('recent-target')
        old_target = feedliststore[Column.TARGET].decode('utf-8') \
            if feedliststore else None

        num = label_list.index(old_target) if old_target in label_list \
            else recent if recent >= 0 else label_list.index(_("News Feed"))

        return num

    def set_recent_api(self, num):
        SETTINGS_FACEBOOK.set_int('recent-target', num)

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
