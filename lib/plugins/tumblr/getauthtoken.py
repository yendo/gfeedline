from oauth import oauth

from ..base.getauthtoken import Authorization

consumer_key = 'Ygjp6HoG7BCGGTVAamZj6pDJK4M1phyHH0jX7cDB6983VX5EDg'
consumer_secret = 'ychftk5UOQKaYn9NHVPKLQiDS8SqPAJZqNK0AbDaIEd5RtohTI'
CONSUMER = oauth.OAuthConsumer(consumer_key, consumer_secret)


class TumblrAuthorization(Authorization):

    CALLBACK = 'http://code.google.com/p/gfeedline/'
    REQUEST_TOKEN_URL = 'http://www.tumblr.com/oauth/request_token'
    ACCESS_TOKEN_URL = 'http://www.tumblr.com/oauth/access_token'
    AUTHORIZE_URL = 'http://www.tumblr.com/oauth/authorize?theme=android&oauth_token='
    CONSUMER = CONSUMER
