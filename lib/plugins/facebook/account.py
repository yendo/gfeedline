import json
import urllib
import locale
from oauth import oauth

from gi.repository import GObject

from ...utils.settings import SETTINGS_FACEBOOK
from ...utils.iconimage import WebIconImage
from ...utils.urlgetautoproxy import urlget_with_autoproxy, urlpost_with_autoproxy
from ...constants import Column
from api import FacebookAPIDict

class FacebookIcon(WebIconImage):

    def __init__(self):
        self.icon_name = 'facebook.png'
        self.icon_url = 'http://www.facebook.com/favicon.ico'

class AuthorizedFacebookAccount(GObject.GObject):

    def __init__(self, user_name, token, secret, idnum):
        super(AuthorizedFacebookAccount, self).__init__()

        self.api = Facebook(token=token)
        self.api_dict = FacebookAPIDict()
        self.idnum = idnum # type unicode
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
        lang = locale.getdefaultlocale()[0]
        self.access_params = {'access_token': token, 'locale': lang}

    def home(self, cb, params=None):
        url = 'https://graph.facebook.com/me/home?'
        return self._get_defer(url, params, cb)

    def feed(self, cb, params):
        user = params.pop('user') or 'me'
        url = 'https://graph.facebook.com/%s/feed?' % user
        return self._get_defer(url, params, cb)

    def like(self, url, is_unlike=False):
        method = 'DELETE' if is_unlike else 'POST'
        d = urlpost_with_autoproxy(str(url), self.access_params, 
                                   cb=self._like_cb, method=method)
        d.addErrback(self._like_cb)

    def _like_cb(self, *args):
        # print args
        pass

    def _get_defer(self, url, params, cb):
        if params is None:
            params = {}

        params.update(self.access_params)
        url += urllib.urlencode(params)
        print url
        return urlget_with_autoproxy(str(url), cb=cb)
