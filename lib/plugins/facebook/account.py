import json
import urllib
import locale
from oauth import oauth

from ...utils.settings import SETTINGS_FACEBOOK
from ...utils.iconimage import WebIconImage
from ...utils.urlgetautoproxy import urlget_with_autoproxy, urlpost_with_autoproxy
from ...constants import Column
from api import FacebookAPIDict
from ..base.getauthtoken import AuthorizedAccount

from ...utils.notification import Notification
from ...utils.iconimage import IconImage

class FacebookIcon(WebIconImage):

    def __init__(self):
        self.icon_name = 'facebook.png'
        self.icon_url = 'http://www.facebook.com/favicon.ico'

class AuthorizedFacebookAccount(AuthorizedAccount):

    SETTINGS = SETTINGS_FACEBOOK

    def __init__(self, user_name, token, secret, idnum):
        super(AuthorizedFacebookAccount, self).__init__()

        self.source = 'Facebook'
        self.api = Facebook(token, self._error_cb)
        self.api_dict = FacebookAPIDict()
        self.idnum = idnum # type unicode
        self.user_name = user_name
        self.icon = FacebookIcon()

    def update_access_token(self, token):
        self.api.update_access_token(token)
        self.valid = True

    def _error_cb(self, error):
        """
        https://developers.facebook.com/docs/graph-api/using-graph-api/#errorsubcodes
        """

        d = json.loads(error.value.response)
        error_subcode = d["error"]["error_subcode"]
        
        error_msg = error.getErrorMessage()
        print "Error (Facebook): ", d["error"]["message"]
       
        if error_subcode == 463 or error_subcode == 467:

            self.valid = False
        
            icon_file = IconImage('gfeedline').get_icon_file()
            summary = _('Facebook connection error: ') + error_msg
            body = _("Authentication seems to fail.  "
                     "Facebook access token expires after 60 days.  "
                     "You have to re-do Facebook authentication on Preferences.")

            n = Notification('GFeedLine')
            n.notify(icon_file, summary, body)

class Facebook(object):

    def __init__(self, token, error_cb):
        self.update_access_token(token)
        self.error_cb = error_cb

    def update_access_token(self, token):
        lang = locale.getdefaultlocale()[0]
        self.access_params = {'access_token': token, 'locale': lang}

    def home(self, cb, params=None):
        url = 'https://graph.facebook.com/me/home?'
        return self._get_defer(url, params, cb)

    def feed(self, cb, params):
        user = params.pop('user') or 'me'
        url = 'https://graph.facebook.com/%s/feed?' % user
        return self._get_defer(url, params, cb)

    def like(self, post_id, is_unlike=False):
        url = 'https://graph.facebook.com/%s/likes' % post_id
        method = 'DELETE' if is_unlike else 'POST'
        d = urlpost_with_autoproxy(str(url), self.access_params, 
                                   cb=self._like_cb, method=method)
        d.addErrback(self._like_cb)

    def _like_cb(self, *args):
        # print args
        pass

    def update(self, status, params):
        params={'message': status.encode('utf-8'), 'privacy': params}
        params.update(self.access_params)

        url = 'https://graph.facebook.com/me/feed?'
        url += urllib.urlencode(params)
        # print url
        
        d = urlpost_with_autoproxy(str(url), params, cb=self._like_cb)
        d.addErrback(self._like_cb)

    def _get_defer(self, url, params, cb):
        if params is None:
            params = {}

        params.update(self.access_params)
        url += urllib.urlencode(params)
        # print url
 
        d = urlget_with_autoproxy(str(url), cb=cb)
        d.addErrback(self.error_cb)
        return d
