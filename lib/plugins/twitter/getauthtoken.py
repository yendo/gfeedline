from oauth import oauth
from ..base.getauthtoken import Authorization

consumer_key = 'zniRMF8u0aOuLPb1Q94QNg'
consumer_secret = 'iuYLw5KPRodf5crYj3caIPxqVF62hIm3ZRziUbtuM'
CONSUMER = oauth.OAuthConsumer(consumer_key, consumer_secret)


class TwitterAuthorization(Authorization):

    CALLBACK = 'oob'
    REQUEST_TOKEN_URL = 'https://twitter.com/oauth/request_token'
    ACCESS_TOKEN_URL = 'https://twitter.com/oauth/access_token'
    AUTHORIZE_URL = 'https://twitter.com/oauth/authorize?mode=desktop&oauth_token='
    CONSUMER = CONSUMER
