from oauth import oauth

from gi.repository import GObject
from getauthtoken import CONSUMER
from ...utils.settings import SETTINGS_TWITTER
from ...utils.iconimage import WebIconImage


class FacebookIcon(WebIconImage):

    def __init__(self):
        self.icon_name = 'twitter.ico'
        self.icon_url = 'http://www.twitter.com/favicon.ico'

class AuthorizedFacebookAccount(GObject.GObject):

    def __init__(self, user_name, key, secret):
        super(AuthorizedTwitterAccount, self).__init__()

        token = self._get_token(user_name, key, secret)
        self.api = TwitterFeed(consumer=CONSUMER, token=token)

        self.icon = FacebookIcon()

    def _on_get_configuration(self, data):
        AuthorizedTwitterAccount.CONFIG = data

    def _on_update_credential(self, account, unknown):
        token = self._get_token()
        self.api.update_token(token)
        self.emit("update-credential", None)

    def _get_token(self, user_name, key, secret):
        token = oauth.OAuthToken(key, secret) if key and secret else None
        self.user_name = user_name if token else None

        return token

